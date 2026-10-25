"""Exact prices with time-accurate noise counterfactuals and single-fault audit."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,hashlib,contextlib,time
from pathlib import Path
from dataclasses import replace
H=Path(__file__).resolve().parent
TAU=3.7423214600721095e-5

def price(name,procs=3):
    assert 1 <= procs <= 3, 'hippo lane limit: three workers plus parent'
    stem=H/'builds'/name
    meta=json.loads(stem.with_suffix('.json').read_text())
    text=stem.with_suffix('.qasm').read_text()
    evdir=H/('sparseframe' if '// FRAME' in text else 'sparse')
    sys.path.insert(0,str(evdir))
    import sparse_walsh as sw
    fa=sw.fa
    from judge_subset.noise import STANDARD
    original=fa.noise_blocks
    start=meta.get('noise_start')
    scale=meta.get('noise_scale',1)
    units={ (t,tuple(qs)) for t,qs in meta.get('noisy_units',[]) }
    resource={int(q):t for q,t in meta.get('perfect_resource',{}).items()}
    wait=meta.get('perfect_data_wait')
    rend=meta.get('round_start',9999)
    if start is not None or scale!=1 or units or resource or wait:
        def selected(text,p,first_order=False):
            p*=scale
            prog,blocks=original(text,p,noise=replace(STANDARD,idle=0),first_order=first_order)
            _,steps,gaps=fa.schedule(text)
            for i,ins in enumerate(prog):
                assert len(steps[i])==1
                t=steps[i][0][1]
                hit_resource=resource and t<rend and all(q in resource and t>=resource[q] for q in ins.qubits)
                if (start is not None and t<start) or (units and (t,tuple(ins.qubits)) not in units) or hit_resource:blocks[i]=[ins.text]
            for i,q,t,n in gaps:
                count=sum((start is None or j>=start) and not(q in resource and resource[q]<=j<rend)
                          and not(wait and q in meta['data_qubits'] and wait[0]<=j<wait[1]) for j in range(t,t+n))
                if count:
                    pr=count*p if first_order else .75*(1-(1-4*p/3)**count)
                    blocks[i].append(f'DEPOLARIZE1({pr}) {q}')
            return prog,blocks
        fa.noise_blocks=selected
    with (H/'logs'/f'{name}.log').open('w') as f,contextlib.redirect_stdout(f):
        r=sw.run(stem,72,True,procs)
    # Use the same saved circuit, selected channels, and exact ideal kernel.
    m,e,groups,*_=sw.prepare(stem,True)
    singles=[]; cache={}; n1=0.
    for fs in groups.values():
        for f in fs:
            key=(f['s'],f['d'])
            if key not in cache:cache[key]=e.ntable(*key)
            a,n=cache[key]; loss=0. if n is None else float(n[f['e']])
            n1+=f['p']*loss
            if loss>1e-9 and f['p']>0:singles.append(dict(probability=f['p'],conditional_n=loss,label=f['label']))
    sha=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest()
    receipt=dict(stem=f'builds/{name}',sha256=sha,loss=r['loss'],acceptance=r['acceptance'],J_tau=r['acceptance']*(r['loss']-TAU),
        single_fault_loss=n1,harmful_single_faults=singles,metadata=meta,host=os.uname().nodename,
        evaluator={k:v for k,v in r.items() if k!='results'},
        evaluator_hashes={str(p.relative_to(H)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__)]+sorted(evdir.rglob('*.py'))+[evdir/'basis_warm.json']})
    (H/'logs'/f'{name}.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('metadata','evaluator','evaluator_hashes','harmful_single_faults')}),flush=True)
    fa.noise_blocks=original

if __name__=='__main__':price(sys.argv[1],int(sys.argv[2]) if len(sys.argv)>2 else 3)
