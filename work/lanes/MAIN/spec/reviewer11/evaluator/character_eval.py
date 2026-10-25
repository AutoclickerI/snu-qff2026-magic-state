#!/usr/bin/env python3
"""Portable evaluator wrapper using exact uniform-Pauli character factors."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
import time
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ.setdefault(name,'1')
import numpy as np
from channel_algebra import compile_character_channels,character_factors

CTX={}

def row(key):
    sw=CTX['sw'];eng=CTX['eng'];ks=CTX['ks'];start=time.perf_counter()
    states,weights,bound=sw.sparse_kernel(eng,ks,CTX['psi'],CTX['where'],key)
    mask=0 if key is None else sw.emask_for(key)
    factors=character_factors(CTX['channels'],states,mask,sw.factors_for)
    vals,peak=sw.contract_selector(factors,CTX['elim']['order'],len(states))
    return dict(key=key,value=float(weights@vals/(1<<len(ks))),
                kernel_nonzero=len(states),peak_bucket_elements=peak,
                absolute_kernel_omission_bound=bound,seconds=time.perf_counter()-start)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evaluator-dir',type=Path,required=True)
    ap.add_argument('--stem',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--processes',type=int,default=4)
    ap.add_argument('--basis-trials',type=int,default=None,
                    help='Override trials per saved basis; zero evaluates only saved bases. Omit for upstream default.')
    ap.add_argument('--profile-factor-construction',action='store_true')
    args=ap.parse_args()
    directory=args.evaluator_dir.resolve();stem=args.stem.resolve()
    if stem.suffix in ('.qasm','.json'):stem=stem.with_suffix('')
    sys.path.insert(0,str(directory));import sparse_walsh as sw
    assert Path(sw.__file__).resolve().parent==directory
    if args.basis_trials is not None:
        assert args.basis_trials>=0
        upstream_search=sw.search_basis
        def bounded_search(*a,**kw):
            kw['trials']=args.basis_trials
            return upstream_search(*a,**kw)
        sw.search_basis=bounded_search
    start=time.perf_counter();m,eng,groups,nd,ks,psi,where,dense=sw.prepare(stem,True)
    prepared=time.perf_counter();compiled,elim=sw.compile_best(m,eng,groups,nd,ks)
    planned=time.perf_counter();channels,counts=compile_character_channels(compiled,merge=True)
    compressed=time.perf_counter()
    CTX.update(sw=sw,eng=eng,ks=ks,psi=psi,where=where,channels=channels,elim=elim)
    profile=[]
    if args.profile_factor_construction:
        states,weights,bound=sw.sparse_kernel(eng,ks,psi,where,None)
        # ABBA on the acceptance moment; compare CPU and elapsed time. This
        # is a factor-construction microbenchmark, not total evaluation speed.
        for mode in ('original','analytic','analytic','original'):
            wall=time.perf_counter();cpu=time.process_time()
            for _ in range(4):
                factors=(sw.factors_for(compiled,states,0) if mode=='original'
                         else character_factors(channels,states,0,sw.factors_for))
            profile.append(dict(mode=mode,repetitions=4,wall_seconds=time.perf_counter()-wall,
                                cpu_seconds=time.process_time()-cpu))
    eval_start=time.perf_counter();keys=[None]+eng.keys
    if args.processes==1:
        rows=[row(k) for k in keys]
    else:
        import multiprocessing as mp
        with mp.get_context('fork').Pool(args.processes) as pool:
            rows=list(pool.imap(row,keys))
    finished=time.perf_counter()
    A=rows[0]['value'];O=sum(w*b*r['value'] for w,b,r in zip(eng.W,eng.beta,rows[1:]))
    eA=rows[0]['absolute_kernel_omission_bound']
    eO=sum(abs(w*b)*r['absolute_kernel_omission_bound'] for w,b,r in zip(eng.W,eng.beta,rows[1:]))
    semantic_paths=['sparse_walsh.py','frontend.py','fastfill.py','basis_warm.json']
    semantic_paths += [str(p.relative_to(directory)) for p in sorted((directory/'judge_subset').glob('*.py'))]
    semantic_hashes={name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in semantic_paths}
    extension_dir=Path(__file__).resolve().parent
    extension_hashes={name:hashlib.sha256((extension_dir/name).read_bytes()).hexdigest()
                      for name in ['channel_algebra.py','character_eval.py']}
    input_meta=json.loads(stem.with_suffix('.json').read_text())
    provenance=dict(input_json_sha256=hashlib.sha256(stem.with_suffix('.json').read_bytes()).hexdigest(),
                    data_qubits=input_meta['data_qubits'],evaluator_files_sha256=semantic_hashes,
                    extension_files_sha256=extension_hashes,algorithm_version=2,
                    numpy_version=np.__version__,python_version=sys.version,
                    basis_trials_per_warm_start=args.basis_trials)
    provenance['semantic_context_sha256']=hashlib.sha256(json.dumps(provenance,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    out=dict(method='Exact uniform-Pauli character factors with full-signature coalescing',
        source=str(stem),qasm_sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),
        evaluator_sha256=hashlib.sha256((directory/'sparse_walsh.py').read_bytes()).hexdigest(),
        provenance=provenance,
        acceptance=A,loss=(A-O)/(2*A),numerator=(A-O)/2,
        conditional_loss_kernel_omission_bound=eO/(2*(A-eA))+abs(O)*eA/(2*A*(A-eA)),
        omission_bound_note='Sparse-cutoff error only, excludes floating-point roundoff.',
        counts=counts,conditioned_width=elim['width'],conditioned_work_entries=elim['work_entries'],
        processes=args.processes,seconds=finished-start,prepare_seconds=prepared-start,
        basis_trials_per_warm_start=args.basis_trials,
        planning_seconds=planned-prepared,character_compile_seconds=compressed-planned,
        contraction_seconds=finished-eval_start,factor_profile=profile,results=rows)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2))

if __name__=='__main__':main()
