import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import concurrent.futures,json,time,math
from pathlib import Path
import sys;sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/EVAL');import exact2
ROOT=Path('/home/jihoon/competitions/quantumn/work/lanes/BUDGET/det_scan');OUT=ROOT/'eval';OUT.mkdir(exist_ok=True)
files=sorted(ROOT.glob('*.qasm'))
def one(p):
 o=OUT/(p.stem+'.json')
 if o.exists():return p.stem,'cached'
 try:
  ev=exact2.Eval(p.read_text(),[0,20,7,10,3,22,21]);x=exact2.run(ev,1,third=False)
  z={'name':p.stem,'c1':x['loss1'],'second':x['loss'],'A1':x['A1'],'exp_minus_A1':math.exp(-x['A1']),'acc1':x['acc1'],'acc2':x['acc2'],'detectors':ev.m.n_det}
 except Exception as e:z={'name':p.stem,'error':repr(e)}
 o.write_text(json.dumps(z));return p.stem,z
if __name__=='__main__':
 t=time.time();n=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=32) as pool:
  for k,z in pool.map(one,files):
   n+=1
   if n%20==0 or n==len(files):print(n,'/',len(files),k,z if isinstance(z,str) else {x:z.get(x) for x in ('second','c1')},flush=True)
 print('elapsed',time.time()-t)
