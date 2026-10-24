import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import concurrent.futures,json,sys,time,math
from pathlib import Path
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/EVAL')
import exact2
ROOT=Path('/home/jihoon/competitions/quantumn/work/lanes/BUDGET/reenc_scan'); OUT=ROOT/'eval'; OUT.mkdir(exist_ok=True)
files=sorted(ROOT.glob('r*.qasm'))
def one(p):
 out=OUT/(p.stem+'.json')
 if out.exists(): return p.stem,'cached'
 try:
  ev=exact2.Eval(p.read_text(),[0,20,7,10,3,22,21]);x=exact2.run(ev,1,third=False)
  z={'id':int(p.stem[1:]),'c1':x['loss1'],'second':x['loss'],'A1':x['A1'],'exp_minus_A1':math.exp(-x['A1']),'acc1':x['acc1'],'acc2':x['acc2'],'cx':sum(1 for l in p.read_text().splitlines() if l.startswith('cx '))}
  out.write_text(json.dumps(z));return p.stem,z
 except Exception as e:
  z={'id':int(p.stem[1:]),'error':repr(e)};out.write_text(json.dumps(z));return p.stem,z
if __name__=='__main__':
 t=time.time(); n=0
 with concurrent.futures.ProcessPoolExecutor(max_workers=32) as pool:
  for k,z in pool.map(one,files):
   n+=1
   if n%25==0 or n==len(files):print(n,'/',len(files),k,z if isinstance(z,str) else {x:z.get(x) for x in ('second','c1')},flush=True)
 print('elapsed',time.time()-t)
