import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,time,sqlite3,zlib
from pathlib import Path
from evaluate import score
from build import build,H as OLDH
H=OLDH/'blue'
def database():
 db=sqlite3.connect(H/os.environ.get('BCFB_BLUE_DB','search.sqlite'),timeout=120);db.execute('pragma journal_mode=WAL');db.execute('create table if not exists prices(tag text primary key, kind text, value real, row text, witness blob)');return db
def price(d,opt,tag,kind,threshold):
 start=time.monotonic();w=dict(prep=d,options=opt)
 try:
  text,md=build(d,opt);row=score(text,md);row.update(CX=md['CX'],R=md['R'],depth=md['native_depth'],options=md['options'],context=opt['context'])
  if row.get('total',1)<threshold and row.get('exp_minus_A1',0)>=.4995:
   out=H/'finalists'/tag;out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(md,indent=2));row['retained_screen']=True
 except (ValueError,AssertionError) as e:row=dict(status='INVALID',error=str(e))
 row.update(tag=tag,kind=kind,seconds=time.monotonic()-start)
 with database() as db:db.execute('insert or replace into prices values(?,?,?,?,?)',(tag,kind,row.get('total'),json.dumps(row),zlib.compress(json.dumps(w).encode())))
 if row.get('retained_screen'):(H/'finalists'/tag).with_suffix('.screen.json').write_text(json.dumps(row,indent=2))
 print(json.dumps(row),flush=True);return row
