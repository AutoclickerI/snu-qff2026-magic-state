import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,concurrent.futures,json,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=10);p.add_argument('--limit',type=int,default=10);p.add_argument('--mode',default='project');p.add_argument('--start',type=int,default=0);a=p.parse_args()
groups=json.loads((HERE/'lns_unique.json').read_text());jobs=[(str(HERE/'inputs/clean82.prep.json'),'replay82'),(str(HERE/'runs/cancel_1.prep.json'),'cancel_1'),(str(HERE/'runs/cancel_2.prep.json'),'cancel_2'),(str(HERE/'runs/cancel_3.prep.json'),'cancel_3')]
jobs +=[(str(ROOT/fs[0]),f'lns_{i:04d}') for i,fs in enumerate(groups[:a.limit]) if i>=a.start]
def job(x):
 prep,tag=x
 if a.mode!='project':tag+='_'+a.mode
 out=HERE/'full'/tag
 if out.with_suffix('.price.json').exists() and 'check' in json.loads(out.with_suffix('.price.json').read_text()):return dict(tag=tag,status='cached')
 t=time.time()
 with open(str(out)+'.price.log','w') as log:
  p=subprocess.Popen([sys.executable,str(HERE/'price.py'),prep,tag,'--mode',a.mode],stdout=log,stderr=subprocess.STDOUT,cwd=HERE)
  out.with_suffix('.process.json').write_text(json.dumps(dict(pid=p.pid,started=t,cmd=prep)));rc=p.wait()
 row=dict(tag=tag,exit_code=rc,elapsed=time.time()-t);out.with_suffix('.exit.json').write_text(json.dumps(row));print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:rows=list(ex.map(job,jobs))
(HERE/'prices_batch.receipt.json').write_text(json.dumps(rows,indent=2))
