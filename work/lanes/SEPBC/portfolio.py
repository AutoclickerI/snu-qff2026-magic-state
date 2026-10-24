"""Bounded process portfolio; waits on child exits and writes each receipt immediately."""
import os,sys,json,subprocess,concurrent.futures,time
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
PY=str(ROOT/'.venv/bin/python')
def run(job):
 name,cmd=job
 load=os.getloadavg()[0]
 if load>60:raise RuntimeError(f'Host load {load}: capacity unavailable before {name}')
 started=time.monotonic()
 with(H/(name+'.log')).open('w')as f:
  p=subprocess.run([PY,*cmd],cwd=ROOT,env=os.environ,stdout=f,stderr=subprocess.STDOUT)
 rec=dict(name=name,returncode=p.returncode,seconds=time.monotonic()-started,load_before=load)
 (H/(name+'.exit.json')).write_text(json.dumps(rec,indent=2))
 with(H/'REPORT.md').open('a')as f:
  f.write('\n- Process exit: '+json.dumps(rec)+'. See its receipt; timeout is not an impossibility proof.\n')
 print(json.dumps(rec),flush=True)
 return rec
if __name__=='__main__':
 jobs=[]
 for k,(d,c,seed)in enumerate([(14,78,0),(14,72,1),(14,64,2),(16,64,3),(12,78,4),(16,72,5),(18,64,6),(14,82,7)]):
  name=f'helper_d{d}_c{c}_s{seed}'
  jobs.append((name,[str(H/'helper_synth.py'),'--depth',str(d),'--cap',str(c),'--seed',str(seed),'--seconds','480','--helpers','18,24,30,31,32,33,34,35','--helper-x','--eager','--out',str(H/name)]))
 for seed in range(4):
  name=f'interleave_r45_k4_s{seed}'
  cmd=[str(H/'interleave.py'),'--out',name,'--round','45','--moves','4','--seconds','480','--workers','2','--seed',str(240+seed),'--solutions','1']
  if seed%2==0:cmd+=['--fixed-endpoints']
  if seed>=2:cmd+=['--automorphisms']
  jobs.append((name,cmd))
 with concurrent.futures.ThreadPoolExecutor(max_workers=12)as pool:
  for r in pool.map(run,jobs):pass
