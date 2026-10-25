"""Compare original and analytical factors on the pinned current evaluator."""
from pathlib import Path
import os,sys,json,time,hashlib
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path(__file__).resolve().parents[3]
SP=ROOT/'quantumn_review11/work/lanes/MAIN/sparse'
sys.path.insert(0,str(SP))
import sparse_walsh as sw
import numpy as np
from channel_algebra import compile_character_channels,character_factors

def main():
    stem=ROOT/'quantumn_review11/work/lanes/MAIN/v36g'
    start=time.perf_counter()
    m,eng,groups,nd,ks,psi,where,dense=sw.prepare(stem,True)
    prep=time.perf_counter()-start
    start=time.perf_counter();compiled,elim=sw.compile_best(m,eng,groups,nd,ks)
    planning=time.perf_counter()-start
    compressed,counts=compile_character_channels(compiled,merge=True)
    unmerged,unmerged_counts=compile_character_channels(compiled,merge=False)
    rows=[];timings={'original_factor':0.,'analytic_factor':0.,'merged_factor':0.,'original_contract':0.,'merged_contract':0.,'kernel':0.}
    max_factor_diff=0.
    for index,key in enumerate([None]+eng.keys):
        start=time.perf_counter();states,weights,bound=sw.sparse_kernel(eng,ks,psi,where,key);timings['kernel']+=time.perf_counter()-start
        mask=0 if key is None else sw.emask_for(key)
        start=time.perf_counter();original=sw.factors_for(compiled,states,mask);timings['original_factor']+=time.perf_counter()-start
        start=time.perf_counter();analytic=character_factors(unmerged,states,mask,sw.factors_for);timings['analytic_factor']+=time.perf_counter()-start
        # Identity drops change list length, so compare an independent contraction below.
        start=time.perf_counter();merged=character_factors(compressed,states,mask,sw.factors_for);timings['merged_factor']+=time.perf_counter()-start
        start=time.perf_counter();v0,p0=sw.contract_selector(original,elim['order'],len(states));timings['original_contract']+=time.perf_counter()-start
        start=time.perf_counter();v1,p1=sw.contract_selector(merged,elim['order'],len(states));timings['merged_contract']+=time.perf_counter()-start
        max_factor_diff=max(max_factor_diff,float(np.max(np.abs(v0-v1))))
        scale=1<<len(ks)
        a=float(weights@v0/scale);b=float(weights@v1/scale)
        rows.append(dict(key=key,original=a,analytic_merged=b,absolute_difference=abs(a-b),kernel_omission_bound=bound,selector_max_difference=float(np.max(np.abs(v0-v1)))))
        if index%12==0:print(json.dumps({'completed_moments':index+1,'max_diff':max(r['absolute_difference'] for r in rows)}),flush=True)
    def loss(field):
        A=rows[0][field];O=sum(w*b*r[field] for w,b,r in zip(eng.W,eng.beta,rows[1:]));return {'acceptance':A,'loss':(A-O)/(2*A)}
    out={'source_commit':'0ff9423a8e69c13998ab1baf7bf09c8e97558a60','qasm_sha256':hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),'evaluator_sha256':hashlib.sha256((SP/'sparse_walsh.py').read_bytes()).hexdigest(),'stem':str(stem),'counts':counts,'unmerged_counts':unmerged_counts,'prepare_seconds':prep,'planning_seconds':planning,'timings_seconds':timings,'elimination':elim,'original':loss('original'),'analytic_merged':loss('analytic_merged'),'max_moment_difference':max(r['absolute_difference'] for r in rows),'max_selector_difference':max_factor_diff,'rows':rows,'passed':all(r['absolute_difference']<1e-12 for r in rows),'scope':'Single-process accumulated component timings on one host; not a universal speedup or physical improvement.'}
    Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('rows','elimination')},indent=2),flush=True)

if __name__=='__main__':main()
