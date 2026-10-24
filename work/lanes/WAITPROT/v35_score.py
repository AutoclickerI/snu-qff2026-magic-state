"""All-order prices using the unchanged MAIN sparse implementation."""
import os,sys,json,time,hashlib,contextlib,io,traceback
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;V=H/'v35';ROOT=H.parents[2]
sys.path[:0]=[str(V/'sparse'),str(ROOT/'work/lanes/EVAL')]
import sparse_walsh as sw,exact2,xtim
xtim.cache_dir=str(V/'.xtim_cache')
os.environ['XTIM_TWIRL_CACHE_DIR']=str(V/'.xtim_cache')
def score(job):
 p=V/job['stem'];start=time.monotonic();r=dict(job)
 try:
  text=p.with_suffix('.qasm').read_text();md=json.loads(p.with_suffix('.json').read_text())
  ev=exact2.Eval(text,md['data_qubits'])
  r.update(c1=float(ev.fp@ev.n_single),noiseless_correct=True)
  # The CLI writes beside its source; route that output into this lane.
  sw.__file__=str(V/'sparse'/'sparse_walsh.py')
  with contextlib.redirect_stdout(io.StringIO()):ao=sw.run(p,72,True,job.get('procs',1))
  r.update(ok=True,loss=ao['loss'],acceptance=ao['acceptance'],eligible=ao['acceptance']>=.5005,omission_bound=ao['conditional_loss_kernel_omission_bound'])
  assert job['sha256']==hashlib.sha256(text.encode()).hexdigest()
 except Exception as e:r.update(ok=False,error=repr(e),traceback=traceback.format_exc())
 r['seconds']=time.monotonic()-start;p.with_suffix('.score.json').write_text(json.dumps(r,indent=2)+'\n')
 return r
if __name__=='__main__':
 import concurrent.futures as cf
 manifest=sys.argv[1];workers=int(sys.argv[2]);jobs=json.loads((V/manifest).read_text());pending=[]
 for j in jobs:
  rc=V/(j['stem']+'.score.json')
  if rc.exists()and json.loads(rc.read_text()).get('sha256')==j['sha256']:continue
  pending.append(j)
 print('START',manifest,len(pending),workers,flush=True)
 with cf.ProcessPoolExecutor(workers)as pool:
  for r in pool.map(score,pending):print(json.dumps({k:v for k,v in r.items()if k not in('description','traceback')}),flush=True)
 print('COMPLETE',manifest,flush=True)
