import os,sys,json,subprocess,concurrent.futures,time
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;PY=H.parents[3]/'.venv/bin/python'
tasks=[(89,9,63,1),(89,10,70,2),(117,11,77,3),(564,11,77,4),(2,11,77,5),(1162,11,77,6)]
def job(t):
 row,d,c,s=t;name=f'r{row}_d{d}_s{s}';cmd=[str(PY),str(H/'synth_resource.py'),'--row',str(row),'--depth',str(d),'--cap',str(c),'--seed',str(s),'--out',name,'--seconds','600','--eager'];start=time.monotonic()
 with(H/(name+'.log')).open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 print(json.dumps(dict(name=name,returncode=r.returncode,seconds=time.monotonic()-start)),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:list(pool.map(job,tasks))
