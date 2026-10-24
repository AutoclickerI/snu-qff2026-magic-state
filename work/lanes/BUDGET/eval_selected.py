import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import concurrent.futures,json,math,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/EVAL');import exact2

def one(p):
 p=Path(p); o=p.with_suffix('.third.json')
 if o.exists(): return p.stem,'cached'
 try:
  ev=exact2.Eval(p.read_text(),json.loads(p.with_suffix('.json').read_text())['data_qubits']);x=exact2.run(ev,1,third=True)
  z={'name':p.stem,'c1':x['loss1'],'second':x['loss'],'A1':x['A1'],'exp_minus_A1':math.exp(-x['A1']),'acc1':x['acc1'],'acc2':x['acc2']}
  if abs(x['loss1'])<1e-12:
   t=exact2.third_order(ev,1)[0]+x['t3bc'];z.update(third=t,total=x['loss']+t)
  else:z.update(third=None,total=None)
 except Exception as e:z={'name':p.stem,'error':repr(e)}
 o.write_text(json.dumps(z));return p.stem,z
if __name__=='__main__':
 paths=sys.argv[1:]; workers=int(os.getenv('WORKERS','4'));t=time.time()
 with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
  for x,z in pool.map(one,paths): print(x,z,flush=True)
 print('elapsed',time.time()-t)
