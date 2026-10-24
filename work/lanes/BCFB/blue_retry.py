import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['BCFB_BLUE_DB']='neighbors.sqlite'
import sqlite3,json,zlib,hashlib,time
from blue_evaluate import price,H
rows=[];seen=set();start=time.monotonic()
with sqlite3.connect(H/'snapshot.sqlite') as db:
 jobs=[]
 for tag,raw,blob in db.execute('select tag,row,witness from prices where value is null'):
  r=json.loads(raw)
  if r.get('error')!='SCHEDULE_INFEASIBLE':continue
  w=json.loads(zlib.decompress(blob));opt=w['options'];opt['retime_window']=4;k=json.dumps(w,sort_keys=True)
  if k in seen:continue
  seen.add(k);jobs.append((tag,w))
for tag,w in jobs:
 base=json.loads((H/'finalists'/w['options']['context']).with_suffix('.screen.json').read_text())['total'];rows.append(price(w['prep'],w['options'],'wide_'+tag,'blue_window4_retry',threshold=base))
rec=dict(status='COMPLETE',source='snapshot.sqlite',prices=len(rows),seconds=time.monotonic()-start,best=min((r.get('total',1) for r in rows),default=None));(H/'retry_receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
