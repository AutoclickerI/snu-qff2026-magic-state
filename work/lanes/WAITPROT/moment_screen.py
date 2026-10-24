import os,sys,json,concurrent.futures
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
sys.path[:0]=[str(ROOT/'work/lanes/EVAL'),str(ROOT/'work/lanes/FRESH')]
import exact2,moments

def one(stem):
 try:
  md=json.loads((H/(stem+'.json')).read_text());ev=exact2.Eval((H/(stem+'.qasm')).read_text(),md['data_qubits']);r=moments.evaluate(ev)
 except Exception as e:r=dict(error=repr(e))
 r['stem']=stem;(H/(stem+'.screen.json')).write_text(json.dumps(r));return r
if __name__=='__main__':
 rows=json.loads((H/sys.argv[1]).read_text());stems=[r['stem'] if isinstance(r,dict) else r for r in rows]
 with concurrent.futures.ProcessPoolExecutor(max_workers=6) as ex:
  for r in ex.map(one,stems):print(json.dumps(r),flush=True)
