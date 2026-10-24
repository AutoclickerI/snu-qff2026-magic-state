"""In-memory bulk prices; durable receipts and finalist-only circuit artifacts."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,time,hashlib,sqlite3,zlib,traceback
H=Path(__file__).resolve().parent;ROOT=H.parents[2];sys.path[:0]=[str(H),str(ROOT/'work/lanes/EVAL')]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
from moments_batch import evaluate,exact2
from build import build
BASE=6.92210398227877e-5

def score(text,md):
 ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single)
 if abs(c1)>=1e-12:return dict(c1=c1,status='INVALID_C1')
 return dict(evaluate(ev),status='SCREENED')
def judge(text,md):
 import tprep
 ck=tprep.check(text,md['data_qubits'],shots=10**6,seed=0)
 return dict(passed=bool(ck.passed),format_ok=bool(ck.format_ok),class_ok=bool(ck.class_ok),correct_ok=bool(ck.correct_ok),acceptance_ok=bool(ck.acceptance_ok),acceptance=float(ck.acceptance),score=float(ck.score),n_2q=int(ck.n_2q),format_errors=ck.format_errors,correctness_errors=ck.correctness_errors)

def database():
 db=sqlite3.connect(H/'search.sqlite',timeout=120)
 db.execute('pragma journal_mode=WAL');db.execute('create table if not exists prices(tag text primary key, kind text, value real, row text, witness blob)');return db

def record(tag,kind,row,witness,text=None,md=None):
 row.update(tag=tag,kind=kind)
 with database() as db:db.execute('insert or replace into prices values(?,?,?,?,?)',(tag,kind,row.get('total'),json.dumps(row),zlib.compress(json.dumps(witness).encode())))
 if text is not None:
  out=H/'finalists'/tag;out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(md,indent=2));out.with_suffix('.screen.json').write_text(json.dumps(row,indent=2))
 print(json.dumps(row),flush=True)

def price(d,opt,tag,kind,threshold=BASE):
 start=time.monotonic();w=dict(prep=d,options=opt)
 try:
  text,md=build(d,opt);row=score(text,md);row.update(CX=md['CX'],R=md['R'],depth=md['native_depth'],options=opt)
  keep=row.get('total',1)<threshold and row.get('exp_minus_A1',0)>.504
  if keep:row['check']=judge(text,md);keep=row['check']['passed'] and row['check']['acceptance']>=.505
  row['seconds']=time.monotonic()-start;record(tag,kind,row,w,text if keep else None,md)
  return row
 except (ValueError,AssertionError) as e:
  row=dict(status='INVALID',error=str(e),seconds=time.monotonic()-start);record(tag,kind,row,w);return row

if __name__=='__main__':
 from build import source
 rows=[]
 for name in ['v23h_c2c9','replay']:
  f=H/'inputs'/name;text=f.with_suffix('.qasm').read_text();md=json.loads(f.with_suffix('.json').read_text());r=score(text,md);r['check']=judge(text,md);r['tag']=name;rows.append(r);print(json.dumps(r),flush=True)
 assert abs(rows[0]['total']-rows[1]['total'])<1e-15,(rows[0],rows[1])
 (H/'replay_validation.json').write_text(json.dumps(rows,indent=2))
