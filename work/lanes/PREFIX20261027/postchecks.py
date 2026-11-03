import os,sys,json,itertools
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import run_legacy_suffix,synth
from search_phase import singles
from qtools import price
H=synth.HERE
p=H/'cand/network_f24_s0_first0.json'
rec=json.loads(p.read_text())['synthesis']
checks=[[dict(mask=x,basis=b)] for b in ['X','Z'] for x in [2,6,1]]+[[dict(mask=x,basis='X') for x in seq] for seq in [(2,6),(6,2),(2,6,1),(6,2,1)]]
out=[]
for ch in checks:
    name='post_'+'_'.join(x['basis']+str(x['mask']) for x in ch)
    r=dict(rec,postchecks=ch);s=synth.build(r,name)
    try:
        c1,n=singles(s);ans=dict(name=name,c1=c1,harmful=n)
        if c1<2e-5:
            p=price(s,1);ans.update(loss=p['loss'],acceptance=p['acceptance'])
        print(json.dumps(ans),flush=True);out.append(ans);(H/'postcheck_results.json').write_text(json.dumps(out,indent=2))
    except Exception as ex:print('ERROR',name,repr(ex),flush=True)
