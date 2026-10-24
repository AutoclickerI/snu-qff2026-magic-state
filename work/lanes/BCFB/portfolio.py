import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,concurrent.futures,json,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=8);p.add_argument('--offset',type=int,default=501);p.add_argument('--seconds',type=int,default=7200);p.add_argument('--prefix',default='fb');a=p.parse_args()
print(json.dumps(dict(event='capacity',nproc=os.cpu_count(),load=os.getloadavg(),workers=a.workers)),flush=True)
def job(k):
 seed=a.offset+k;depth=14+(k%2);cap=[82,105,98,90][k%4];tag=f'{a.prefix}_s{seed}';cmd=[sys.executable,str(H/'feedback.py'),'--seed',str(seed),'--depth',str(depth),'--cap',str(cap),'--seconds',str(a.seconds),'--prefix',a.prefix]
 with (H/'runs'/f'{tag}.log').open('w') as log:
  pr=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);(H/'runs'/f'{tag}.process.json').write_text(json.dumps(dict(pid=pr.pid,cmd=cmd,start=time.time())))
  rc=pr.wait()
 (H/'runs'/f'{tag}.exit.json').write_text(json.dumps(dict(exit_code=rc)));print(tag,rc,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:list(ex.map(job,range(a.workers)))
