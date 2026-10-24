"""Reprice diagnosed native-fold failures and schedule conflicts after exact retiming."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,zlib,concurrent.futures,sqlite3
from evaluate import H,price

def job(x):
 tag,kind,w=x;opt=w['options'];d=w['prep'];return price(d,opt,tag,kind)
def main():
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=4);p.add_argument('--limit',type=int,default=1200);p.add_argument('--kind',default='fold');a=p.parse_args();jobs=[];seen=set()
 with sqlite3.connect(H/'search.sqlite',timeout=120) as db:rr=list(db.execute('select tag,kind,row,witness from prices where value is null'))
 for tag,kind,row,w in rr:
  r=json.loads(row);w=json.loads(zlib.decompress(w))
  if 'prep' not in w or tag.startswith('retry'):continue
  if a.kind=='fold' and r.get('error')=='native fold changed':pass
  elif a.kind=='retime' and r.get('error')=='SCHEDULE_INFEASIBLE':w['options']['retime_window']=2
  else:continue
  sig=json.dumps(w,sort_keys=True)
  if sig in seen:continue
  seen.add(sig);jobs.append((f'retry_{a.kind}_{tag}',f'retry_{a.kind}',w))
  if len(jobs)>=a.limit:break
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as e:list(e.map(job,jobs))
 (H/'runs'/f'retry_{a.kind}.receipt.json').write_text(json.dumps(dict(status='COMPLETE',prices=len(jobs))))
if __name__=='__main__':main()
