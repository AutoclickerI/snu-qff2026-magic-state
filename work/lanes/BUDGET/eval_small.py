import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import subprocess,concurrent.futures
from pathlib import Path
files=list(Path('work/lanes/BUDGET/timing').glob('*.qasm'))
def one(p):
 log=p.with_suffix('.exact.log')
 with log.open('w') as f:
  r=subprocess.run(['/home/jihoon/competitions/quantumn/.venv/bin/python','work/lanes/EVAL/exact2.py',str(p),'--procs','1','--third'],stdout=f,stderr=subprocess.STDOUT)
 return p.name,r.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=9) as ex:
 for x in ex.map(one,files):print(x,flush=True)
