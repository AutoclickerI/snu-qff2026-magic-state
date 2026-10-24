import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import subprocess,concurrent.futures,json,time
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
jobs=[('policy',v) for v in range(9,16)]+[('endpoint',v) for v in range(1,8)]+[('c6',v) for v in range(7)]
def run(job):
 load=os.getloadavg()[0]
 cpu=sum(float(v) for v in subprocess.check_output(["ps","-u",str(os.getuid()),"-o","pcpu="],text=True).split())/100
 if load>=64 or cpu>=47:return dict(job=job,status="CAPACITY",load=load,user_cpu=cpu)
 kind,v=job;seed=701+jobs.index(job);tag=f'{kind}_{v}_s{seed}';cmd=[str(ROOT/'.venv/bin/python'),str(H/'search.py'),kind,str(v),'--seed',str(seed),'--seconds','900','--cap','96']
 with (H/'runs'/f'{tag}.log').open('w') as f:
  p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,cwd=ROOT);print(json.dumps(dict(event='start',tag=tag,pid=p.pid)),flush=True);rc=p.wait()
 print(json.dumps(dict(event='exit',tag=tag,rc=rc)),flush=True);return dict(tag=tag,rc=rc)
with concurrent.futures.ThreadPoolExecutor(max_workers=18) as ex:rows=list(ex.map(run,jobs))
(H/'portfolio.receipt.json').write_text(json.dumps(rows,indent=2))
