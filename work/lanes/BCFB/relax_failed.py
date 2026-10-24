"""Price previously infeasible clean feedback witnesses at R46/R47.
Uniform sampling over distinct prep/options representatives, not CX ranking.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,zlib,sqlite3,random,hashlib,concurrent.futures,argparse
from evaluate import H,price

def job(x):
 tag,w=x;opt=dict(w['options'],round_shift=1,retime_window=4);r=price(w['prep'],opt,'late1_'+tag,'late_feedback')
 if r.get('error')=='SCHEDULE_INFEASIBLE':
  opt['round_shift']=2;r=price(w['prep'],opt,'late2_'+tag,'late_feedback')
 return r

def main():
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=4);p.add_argument('--limit',type=int,default=1500);a=p.parse_args();seen=set();jobs=[]
 with sqlite3.connect(H/'search.sqlite',timeout=120) as db:
  for tag,kind,row,blob in db.execute('select tag,kind,row,witness from prices where value is null'):
   if kind not in ('feedback','feedback_retime'):continue
   r=json.loads(row)
   if r.get('error')!='SCHEDULE_INFEASIBLE':continue
   w=json.loads(zlib.decompress(blob));d=w['prep'];opt=dict(w['options']);opt.pop('retime_window',None)
   sig=repr((sorted(d['pivots']),[(q,[tuple(e) for l in d['ops'] for e in l if q in e]) for q in sorted(d['cells'])],sorted(opt.items())))
   if sig in seen:continue
   seen.add(sig);jobs.append((tag,w))
 random.Random(9917).shuffle(jobs);available=len(jobs);jobs=jobs[:a.limit]
 print(json.dumps(dict(event='START',representatives_available=available,selected=len(jobs),selection_seed=9917)),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as ex:rs=list(ex.map(job,jobs))
 out=dict(status='COMPLETE',representatives_available=available,selected=len(jobs),prices=len(rs),best=min((r.get('total',1) for r in rs),default=None));(H/'runs/late_feedback.receipt.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':main()
