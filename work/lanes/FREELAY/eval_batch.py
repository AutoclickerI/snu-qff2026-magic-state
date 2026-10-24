"""Bounded parallel evaluator; workers are reallocated only on process exit."""
import os,sys,subprocess,concurrent.futures,json
from pathlib import Path
H=Path(__file__).resolve().parent;os.chdir(H)
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def run(p):
 print('capacity',os.cpu_count(),'loadavg',Path('/proc/loadavg').read_text().strip(),flush=True)
 if os.getloadavg()[0]>=os.cpu_count():raise RuntimeError('host capacity')
 with p.with_suffix('.eval.log').open('w') as f:
  subprocess.run([sys.executable,'evaluate.py',p.stem,'8'],stdout=f,stderr=subprocess.STDOUT,check=True)
 return p.stem
ps=sorted(H.glob(sys.argv[1] if len(sys.argv)>1 else 'joint_cal*.qasm'))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for name in pool.map(run,ps):print('finished',name,flush=True)
