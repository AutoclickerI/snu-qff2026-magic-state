import os,sys,json,copy
from pathlib import Path
import numpy as np
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import run_legacy_suffix,synth
from qcirc import parse,save
from search_phase import singles
from qtools import price

def augment(stem,mode='all',limit=None):
    p=Path(stem);units,dets=parse(p.with_suffix('.qasm').read_text());meta=json.loads(p.with_suffix('.json').read_text())
    flagt=next(u['t'] for u in units if u['b']==500);cells=synth.CELLS;qi={q:i for i,q in enumerate(cells)}
    starts={q:min(u['t'] for u in units if q in u['q']) for q in cells}
    n=1<<len(cells);ix=np.arange(n,dtype=np.uint32);v=np.zeros(n,complex);v[0]=1
    bits={q:(ix>>i)&1 for q,i in qi.items()};new=[];record=600;possible=[]
    for t in range(flagt):
        now=[u for u in units if u['t']==t and set(u['q'])<=set(cells)]
        active={q for u in now for q in u['q']}
        for q in cells:
            if q in active or t<starts[q]:continue
            pz=float(np.sum(abs(v)**2*(1-2*bits[q].astype(float))))
            px=float(np.vdot(v,v[ix^(1<<qi[q])]).real)
            k='M' if pz>1-1e-10 else 'MX' if px>1-1e-10 else None
            if k and (mode=='all' or mode==k):possible.append(dict(t=t,k=k,q=(q,),b=record));record+=1
        for u in now:
            k=u['k'];qs=u['q']
            if k in ('R','RX'):
                q=qs[0]
                assert abs(v[bits[q]==1]).max()<1e-10
                if k=='RX':v=(v+v[ix^(1<<qi[q])])/np.sqrt(2)
            elif k=='CX':
                c,tar=qs;perm=ix^((bits[c])<<qi[tar]);v=v[perm]
            elif k in ('T','TDG'):v*=np.exp((1j if k=='T' else -1j)*np.pi/4*bits[qs[0]])
            else:raise ValueError(u)
    # Prefix checks replace idles and require no extra CX or depth.
    if limit is not None:possible=possible[:limit]
    units+=possible;dets += [[u['b']] for u in possible]
    meta.update(transient_checks=[dict(u,q=list(u['q'])) for u in possible],source='PREFIX20261027 synthesized phase network plus deterministic transient checks')
    out=synth.HERE/'cand'/(p.name+'_checks_'+mode+(str(limit) if limit else ''))
    save(out,units,dets,meta['data_qubits'],meta)
    return out,len(possible)

if __name__=='__main__':
    for s in sys.argv[1:]:
        for mode in ['M','MX','all']:
            p,n=augment(s,mode);c1,h=singles(p);r=price(p,1)
            ans=dict(stem=str(p),checks=n,c1=c1,harmful=h,loss=r['loss'],acceptance=r['acceptance'])
            print(json.dumps(ans),flush=True)
            p.with_suffix('.result.json').write_text(json.dumps(ans,indent=2))
