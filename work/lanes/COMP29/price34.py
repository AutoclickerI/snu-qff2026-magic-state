"""Unmodified sparse evaluator, relocated only to keep its output in COMP29."""
import os,sys,json,time,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.path.insert(0,str(H/'sparse34'))
import sparse_walsh as w
name=sys.argv[1];procs=int(sys.argv[2]) if len(sys.argv)>2 else 1
start=time.monotonic();p=H/name
try:
    r=w.run(p,72,True,procs)
    r.update(source_sha256=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest(),validated=True)
except Exception as e:
    r=dict(error=repr(e),seconds=time.monotonic()-start)
    p.with_suffix('.allorders.json').write_text(json.dumps(r,indent=2)+'\n')
    raise
p.with_suffix('.allorders.json').write_text(json.dumps(r,indent=2)+'\n')
