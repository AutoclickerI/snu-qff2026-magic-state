import os,sys,subprocess,concurrent.futures,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def run(p):
 ev=HERE/'exact.py'
 t=time.time()
 with p.with_suffix('.exact.log').open('w') as f:r=subprocess.run([str(ROOT/'.venv/bin/python'),str(ev),str(p),*(['--grid-free'] if p.parent.name=='gf' else []),'--third','--procs','4','--top','10'],stdout=f,stderr=subprocess.STDOUT)
 print(p.name,r.returncode,round(time.time()-t,1),flush=True)
 return r.returncode
paths=[Path(a) for a in sys.argv[1:]] or sorted((HERE/'gf').glob('*.qasm'))
assert os.getloadavg()[0] + 4*min(4,len(paths)) <= os.cpu_count(), (os.getloadavg(),os.cpu_count())
with concurrent.futures.ThreadPoolExecutor(4) as ex:list(ex.map(run,paths))
