import os,sys,json,time,hashlib
from pathlib import Path
from multiprocessing import get_context
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H))
import ev37 as E
TAU=3.742321460072e-5
def job(rec):
 st=H/rec['stem'];s=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()
 cache=H/'res'/f'{s}.json'
 r=json.loads(cache.read_text()) if cache.exists() else None
 if r is None or r.get('evaluator_hash')!=E.EVH or r.get('data_qubits')!=E.D:
  r=dict(E.price_stem(st),sha256=s,data_qubits=E.D,evaluator_hash=E.EVH)
  if 'loss' in r:r['J_tau']=r['acceptance']*(r['loss']-TAU)
  cache.write_text(json.dumps(r,indent=2)+'\n')
 return dict(r,stem=str(st),what_moved=rec['why'])
if __name__=='__main__':
 tasks=json.loads(Path(sys.argv[1]).read_text());workers=int(sys.argv[2]);out=Path(sys.argv[3])
 with out.open('a') as f:
  if workers==1:
   for t in tasks:
    r=job(t);f.write(json.dumps(r)+'\n');f.flush();print(json.dumps(r),flush=True)
  else:
   with get_context('fork').Pool(workers) as pool:
    for r in pool.imap_unordered(job,tasks,chunksize=1):
     f.write(json.dumps(r)+'\n');f.flush();print(json.dumps(r),flush=True)
