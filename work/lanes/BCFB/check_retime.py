import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,sqlite3,zlib,concurrent.futures
from init_checks import job,H
jobs=[]
with sqlite3.connect(H/'search.sqlite',timeout=120) as db:
 for tag,row,w in db.execute('select tag,row,witness from prices where kind="init_checks" and value is null'):
  r=json.loads(row);w=json.loads(zlib.decompress(w))
  if r.get('error')=='SCHEDULE_INFEASIBLE' and not w.get('retime_window'):jobs.append((w['source'],w['checked'],2))
with concurrent.futures.ProcessPoolExecutor(max_workers=4) as ex:rows=list(ex.map(job,jobs))
out=dict(status='COMPLETE',prices=len(rows),best=min((r.get('total',1) for r in rows),default=None));(H/'runs/check_retime.receipt.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
