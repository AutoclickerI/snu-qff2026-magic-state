import os,sys,json,subprocess,concurrent.futures,time,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.chdir(ROOT)
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
manifest=H/sys.argv[1];workers=int(sys.argv[2]);procs=int(sys.argv[3]);rows=json.loads(manifest.read_text())
def one(row):
 stem=row['stem'] if isinstance(row,dict) else row
 qp=H/(stem+'.qasm');dest=H/(stem+'.ref.log');rc=H/(stem+'.ref.exit.json');t=time.monotonic()
 sha=hashlib.sha256(qp.read_bytes()).hexdigest()
 if rc.exists():
  prior=json.loads(rc.read_text())
  if prior.get('returncode')==0 and prior.get('sha256')==sha:return dict(stem=stem,cached=True)
 with dest.open('w') as f:
  p=subprocess.run([str(ROOT/'.venv/bin/python'),'-u',str(H/'reference.py'),str(qp),'--third','--procs',str(procs),'--top','10','--json',str(H/(stem+'.ref.sensitivity.json'))],stdout=f,stderr=subprocess.STDOUT)
 out=dict(stem=stem,returncode=p.returncode,seconds=time.monotonic()-t,sha256=sha);rc.write_text(json.dumps(out));return out
with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
 for out in ex.map(one,rows):print(json.dumps(out),flush=True)
