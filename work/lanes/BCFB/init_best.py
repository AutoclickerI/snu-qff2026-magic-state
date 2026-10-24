"""Re-optimize every BC init choice around a newly synthesized prep."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,itertools,random,concurrent.futures,sqlite3,zlib
from evaluate import H,price
from build import B,C,source

def job(j):
 d,opt,tag,threshold=j;return price(d,opt,tag,'init_best',threshold=threshold)
def main():
 p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--workers',type=int,default=4);p.add_argument('--radius',type=int,default=2);p.add_argument('--all',action='store_true');p.add_argument('--bar');p.add_argument('--resume',action='store_true');a=p.parse_args();f=H/'finalists'/a.stem;md=json.loads(f.with_suffix('.json').read_text());d=md['prep'];piv=set(d['pivots']);cells=sorted(B+C);mz={23,25,27,28,29}-piv;pick=piv|mz;mask0=sum(1<<i for i,q in enumerate(cells) if q in pick);masks={mask0,0,16383}
 for k in range(1,a.radius+1):
  for ix in itertools.combinations(range(14),k):masks.add(mask0^sum(1<<i for i in ix))
 if a.all:masks=set(range(1<<14))
 bar=H/'finalists'/a.bar if a.bar else f
 threshold=json.loads(bar.with_suffix('.screen.json').read_text())['total']-1e-12
 jobs=[];cached={};resumed=[]
 if a.resume:
  with sqlite3.connect(H/'search.sqlite',timeout=120) as db:
   for tag,row,witness in db.execute('select tag,row,witness from prices where kind=? and tag like ?',('init_best',f'ib_{a.stem}_%')):cached[tag]=(json.loads(row),json.loads(zlib.decompress(witness)))
 for m in masks:
  mm={q for i,q in enumerate(cells) if m>>i&1};opt=dict(mx=sorted(mm&piv),mz=sorted(mm-piv),timing='alap',retime_window=2);tag=f'ib_{a.stem}_{m:04x}'
  if tag in cached:
   row,w=cached[tag];assert w['prep']==d and w['options']==opt,(tag,'cache witness mismatch')
   if row.get('status')=='SCREENED' or row.get('error')=='SCHEDULE_INFEASIBLE':resumed.append(row);continue
  jobs.append((d,opt,tag,threshold))
 print(json.dumps(dict(event='COVERAGE',masks=len(masks),resumed=len(resumed),to_compute=len(jobs))),flush=True)
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as ex:rs=list(ex.map(job,jobs))
 assert len(rs)+len(resumed)==len(masks)
 out=dict(status='COMPLETE',prices=len(rs)+len(resumed),computed_this_run=len(rs),resumed=len(resumed),best=min((r.get('total',1) for r in rs+resumed),default=1));(H/'runs'/f'initbest_{a.stem}{"_all" if a.all else ""}.receipt.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':main()
