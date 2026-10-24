import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse, concurrent.futures, json, subprocess, time
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--host',required=True);p.add_argument('--seeds',type=int,default=4);p.add_argument('--offset',type=int,default=0);p.add_argument('--seconds',type=float,default=7205);a=p.parse_args()
 jobs=[]
 hints=['tom_ep_d14_c78_s0.endpoint.json','tom_ep_d14_c74_s1.endpoint.json','tom_ep_d14_c70_s2.endpoint.json','tom_ep_d14_c62_s6.endpoint.json']
 for depth,cap in ((14,78),(14,74),(14,70),(13,82),(13,78)):
  for k in range(a.seeds):
   seed=a.offset+k
   tag=f'{a.host}_d{depth}_c{cap}_s{seed}'
   out=HERE/'runs'/tag
   cmd=[sys.executable,str(HERE/'synth.py'),'--depth',str(depth),'--cap',str(cap),'--seed',str(seed),'--seconds',str(a.seconds),'--hint',str(HERE/'inputs'/hints[k%4]),'--out',str(out)]
   if k%2==0:cmd+=['--eager']
   jobs.append((tag,out,cmd))
 def run(job):
  tag,out,cmd=job;start=time.time()
  with open(str(out)+'.log','w') as log:
   proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
   Path(str(out)+'.process.json').write_text(json.dumps(dict(pid=proc.pid,host=a.host,start=start,cmd=cmd)))
   code=proc.wait()
  rec=dict(tag=tag,pid=proc.pid,exit_code=code,wall_seconds=time.time()-start)
  Path(str(out)+'.exit.json').write_text(json.dumps(rec));print(json.dumps(rec),flush=True);return rec
 with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as pool:rs=list(pool.map(run,jobs))
 (HERE/f'{a.host}_portfolio.json').write_text(json.dumps(rs,indent=2))
if __name__=='__main__':main()
