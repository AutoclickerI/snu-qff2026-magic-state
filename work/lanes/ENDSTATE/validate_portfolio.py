import os,sys,json,subprocess,concurrent.futures,time
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2];PY=ROOT/'.venv/bin/python'
names=sys.argv[1:] or ['abstract_opt11','abstract_opt10','abstract_opt08','legacy_opt48','legacy_opt46']
def job(name):
 out=[]
 for mode in ['speed','check','exact','split']:
  cmd=[str(PY),str(H/'evaluate.py'),mode,str(H/name),'--procs','1'];start=time.monotonic()
  with(H/(name+'.'+mode+'.log')).open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
  row=dict(name=name,mode=mode,exit_code=r.returncode,seconds=time.monotonic()-start);out.append(row);print(json.dumps(row),flush=True)
 return out
with concurrent.futures.ThreadPoolExecutor(max_workers=5)as pool:rows=list(pool.map(job,names))
(H/'validation_batch.json').write_text(json.dumps(rows,indent=2))
