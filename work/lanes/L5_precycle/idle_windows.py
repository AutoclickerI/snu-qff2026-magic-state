"""Diagnostic only: official sampler with selected idle channels removed."""
from search_v10 import *
import tprep.noise as tn
from tprep.qasm import to_stim

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=16);args=p.parse_args()
    text=(HERE/'v10_reference.qasm').read_text();data=json.loads((HERE/'v10_reference.json').read_text())['data_qubits']
    orig=tn.schedule
    cases=[('remove_injection_idle',0,11,None),('remove_first_check_idle',11,21,None),('remove_double_cat_idle',21,33,None),
           ('remove_pre_data_idle',0,33,{0,20,7,4,3,15,8}),('remove_pre_ancilla_idle',0,33,set(range(36))-{0,20,7,4,3,15,8})]
    results=[]
    for name,lo,hi,qs in cases:
        def schedule(t):
            prog,steps,gaps=orig(t);keep=[]
            for i,q,first,n in gaps:
                if qs is not None and q not in qs:keep.append((i,q,first,n));continue
                a,b=max(first,lo),min(first+n,hi)
                if b<=a:keep.append((i,q,first,n));continue
                if first<a:keep.append((i,q,first,a-first))
                if b<first+n:keep.append((i,q,b,first+n-b))
            return prog,steps,keep
        tn.schedule=schedule
        rows=[]
        try:
            for seed in SEEDS:
                r=fast_check.check(text,data,shots=10**8,seed=seed,procs=args.procs)
                rows.append({'seed':seed,'score':r.score,'acceptance':r.acceptance,'passed':r.passed})
        finally:tn.schedule=orig
        row={'case':name,'diagnostic_modified_noise':True,'seeds':rows,'mean':statistics.mean(r['score'] for r in rows)}
        results.append(row);print(json.dumps(row),flush=True)
        (HERE/'idle_windows.json').write_text(json.dumps(results,indent=2)+'\n')
