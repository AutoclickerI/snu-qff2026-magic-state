import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import concurrent.futures,json,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
groups=json.loads((H/'lns_unique.json').read_text());jobs=[]
for qs in ([6],[5],[26],[17],[12],[11],[6,5,26,17,12,11]):
 jobs.append((H/'inputs/clean82.prep.json','mx_'+'_'.join(map(str,qs)),['--mx',','.join(map(str,qs))]))
# Distribute the priority screen across the entire network portfolio.
ix=sorted(set([i for i,g in enumerate(groups) if 's201' in g[0] or 's202' in g[0]][::3]+list(range(0,len(groups),80))))
for i in ix:jobs.append((ROOT/groups[i][0],f'priority_{i:04d}',['--mode','release_alap']))
def job(x):
 f,tag,extra=x
 with (H/'full'/f'{tag}.price.log').open('w') as log:
  p=subprocess.Popen([sys.executable,str(H/'price.py'),str(f),tag,*extra],stdout=log,stderr=subprocess.STDOUT,cwd=H);rc=p.wait()
 print(json.dumps(dict(tag=tag,exit_code=rc)),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(job,jobs))
