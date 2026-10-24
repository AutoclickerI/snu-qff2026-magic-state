import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import concurrent.futures,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
jobs=[]
for base,f in [('base',H/'inputs/clean82.prep.json'),('p1497',H/'runs/lns_c81_s201_w0013.prep.json'),('p2134',H/'runs/lns_c81_s201_w0111.prep.json')]:
 piv=json.loads(f.read_text())['pivots']
 jobs.append((f,base+'_mx',['--mx',','.join(map(str,piv)),'--mode','release_alap']))
 for qs in ([6],[19],[6,19]):
  for mx in (False,True):
   extra=['--reuse',','.join(map(str,qs)),'--mode','project']
   if mx:extra+=['--mx',','.join(str(q) for q in piv if q not in qs)]
   jobs.append((f,base+'_reuse'+'_'.join(map(str,qs))+('_mx' if mx else ''),extra))
def job(x):
 f,tag,extra=x
 with (H/'full'/f'{tag}.price.log').open('w') as log:
  p=subprocess.Popen([sys.executable,str(H/'price.py'),str(f),tag,*extra],stdout=log,stderr=subprocess.STDOUT,cwd=H);rc=p.wait()
 print(json.dumps(dict(tag=tag,exit_code=rc)),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(job,jobs))
