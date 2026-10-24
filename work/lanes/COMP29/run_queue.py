"""Finite queue: completion is subprocess exit, never output-file polling."""
import os,sys,json,subprocess,time,concurrent.futures,math
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
mode=sys.argv[1];workers=int(sys.argv[2]);queue=json.loads((H/sys.argv[3]).read_text())
def job(name):
    start=time.monotonic()
    if mode=='exact':args=[str(H/'exact_job.py'),name,'1']
    elif mode=='gate':args=[str(H/'gate.py'),name]
    elif mode=='allorders':args=[str(H/'allorders_general.py'),str(H/name),'--procs','1']
    elif mode=='mc':args=[str(H/'mc3.py'),str(H/name),'--procs','1']
    else:raise ValueError(mode)
    with (H/(name+'.'+mode+'.log')).open('w') as f:
        p=subprocess.run([str(ROOT/'.venv/bin/python'),*args],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
    r=dict(stem=name,mode=mode,exit_code=p.returncode,seconds=time.monotonic()-start)
    print(json.dumps(r),flush=True);return r
with concurrent.futures.ThreadPoolExecutor(workers) as pool:
    futures={pool.submit(job,name):name for name in queue}
    with (H/(mode+'_'+Path(sys.argv[3]).stem+'.completed.jsonl')).open('a') as f:
        for fut in concurrent.futures.as_completed(futures):
            f.write(json.dumps(fut.result())+'\n');f.flush()
