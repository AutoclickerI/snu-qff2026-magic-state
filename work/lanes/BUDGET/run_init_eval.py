import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import concurrent.futures,json,sys,time
from pathlib import Path
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/EVAL')
import exact2
ROOT=Path('/home/jihoon/competitions/quantumn/work/lanes/BUDGET/init_scan')
manifest=json.loads((ROOT/'manifest.json').read_text())
kind=sys.argv[1] if len(sys.argv)>1 else 'train'
ms=manifest[kind]
outdir=ROOT/'eval';outdir.mkdir(exist_ok=True)

def one(mask):
 out=outdir/f'{mask:03x}.json'
 if out.exists(): return mask,'cached'
 p=ROOT/f'v17a_i{mask:03x}.qasm'
 try:
  ev=exact2.Eval(p.read_text(),[0,20,7,10,3,22,21])
  x=exact2.run(ev,1,third=False)
  z=dict(mask=mask,c1=x['loss1'],second=x['loss'],A1=x['A1'],exp_minus_A1=float(__import__('math').exp(-x['A1'])),acc1=x['acc1'],acc2=x['acc2'],channels=ev.m.n_chans if hasattr(ev.m,'n_chans') else len(ev.m.chans))
  z['third']=None; z['total']=None
  out.write_text(json.dumps(z))
  return mask,z
 except Exception as e:
  z={'mask':mask,'error':repr(e)};out.write_text(json.dumps(z));return mask,z

if __name__=='__main__':
 t=time.time(); done=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=32) as pool:
  for mask,res in pool.map(one,ms):
   done+=1
   if done%10==0 or done==len(ms): print(done,'/',len(ms),mask,res if isinstance(res,str) else {k:res.get(k) for k in ('second','total','c1')},flush=True)
 print('elapsed',time.time()-t)
