"""Finite expanded screens: arbitrary init masks, prep timing and BC check order."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,random,itertools,hashlib,concurrent.futures,time
from pathlib import Path
from evaluate import H,BASE,price,score,judge,record
from build import build,source,S,native_times,B,C

def save_screen(tag,kind,text,md,witness,threshold=BASE):
 try:
  row=score(text,md);keep=row.get('total',1)<threshold and row.get('exp_minus_A1',0)>=.504
  if keep:row['check']=judge(text,md);keep=row['check']['passed'] and row['check']['acceptance']>=.505
  row.update(R=md['R'],CX=md['CX'],change=witness);record(tag,kind,row,witness,text if keep else None,md);return row
 except (ValueError,AssertionError) as e:
  row=dict(status='INVALID',error=str(e));record(tag,kind,row,witness);return row

def init_job(job):
 tag,d,opt=job;return price(d,opt,tag,'init')
def init_scan(workers,seed):
 d=json.loads((H/'inputs/fb_s401_0035.prep.json').read_text());piv=set(d['pivots']);mz0={23,25,27,28,29};cells=sorted(B+C);rng=random.Random(seed)
 # Include the complete one/two/three-bit neighborhood plus wide arbitrary masks.
 mask0=sum(1<<i for i,q in enumerate(cells) if q in piv|mz0);masks={mask0,0,(1<<14)-1}
 for k in (1,2,3):
  for ix in itertools.combinations(range(14),k):masks.add(mask0^sum(1<<i for i in ix))
 masks|={rng.randrange(1<<14) for _ in range(1000)}
 jobs=[]
 for mask in sorted(masks):
  pick={q for i,q in enumerate(cells) if mask>>i&1};opt=dict(timing='alap',mx=sorted(pick&piv),mz=sorted(pick-piv));jobs.append((f'init_m{mask:04x}',d,opt))
 with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:list(ex.map(init_job,jobs))
 (H/'runs/init.receipt.json').write_text(json.dumps(dict(status='COMPLETE',masks=len(masks),seed=seed)))

def order_scan():
 d=json.loads((H/'inputs/fb_s401_0035.prep.json').read_text());jobs=[]
 for delta in range(-4,4):
  for early in (False,True):
   for mode in ('alap','asap'):
    tag=f'order_d{delta}_e{int(early)}_{mode}';r=price(d,dict(timing=mode,check_delta=delta,read_early=early),tag,'order')
 for deadline in range(39,45):price(d,dict(timing='deadline',deadline=deadline),f'finish_{deadline}','timing')
 for seed in range(20):price(d,dict(timing='random',timing_seed=seed),f'spread_{seed}','timing')
 (H/'runs/order.receipt.json').write_text(json.dumps(dict(status='COMPLETE')))

def timing_job(job):
 tag,text,md,change=job;return save_screen(tag,'timing',text,md,change)
def timing_scan(stem,workers,rounds,radius):
 p=Path(stem);p=p if p.is_absolute() else H/p;text=p.with_suffix('.qasm').read_text();md=json.loads(p.with_suffix('.json').read_text());best=score(text,md)['total'];seen=set();count=0;improve=0;prefix=p.name
 for rnd in range(rounds):
  h,r,tail=S.qasm_ops(text);us=S.fold_units(r);ts=native_times(text,us);pred,succ=S.build_dag(us);R=md['R']
  init={q:max(i for i,u in enumerate(us) if u.qs==(q,) and ts[i]<R and u.name in ('RX','RESET','MEASURE','MX')) for q in B+C}
  ids=[i for i,u in enumerate(us) if ts[i]<R and set(u.qs)<=set(B+C) and all(i>=init[q] for q in u.qs)]
  jobs=[];texts={}
  for i in ids:
   lo=max((ts[j]+1 for j in pred[i]),default=0);hi=min((ts[j]-1 for j in succ[i]),default=R-1)
   for t in range(max(lo,ts[i]-radius),min(hi,ts[i]+radius)+1):
    if t==ts[i]:continue
    nt=ts.copy();nt[i]=t;new=S.emit(h,us,nt,tail);sig=hashlib.sha256(new.encode()).hexdigest()[:12]
    if sig in seen:continue
    seen.add(sig);tag=f'time_{prefix}_{sig}';change=dict(source=str(p),round=rnd,unit=i,lines=us[i].lines,old=ts[i],new=t)
    nmd=dict(md,timing_change=change);jobs.append((tag,new,nmd,change));texts[tag]=(new,nmd)
  print(json.dumps(dict(event='timing_round',round=rnd,candidates=len(jobs),baseline=best)),flush=True);oldbest=best
  with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
   for r in ex.map(timing_job,jobs):
    count+=1
    if r.get('total',1)<best-1e-12 and r.get('check',{}).get('passed') and r['check']['acceptance']>=.505:
     best=r['total'];text,md=texts[r['tag']];improve+=1
  if best>=oldbest-1e-12:break
 rec=dict(status='COMPLETE',rounds=rnd+1,prices=count,improvements=improve,best=best)
 (H/'runs'/f'timing_{prefix}.receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('kind',choices=['init','order','timing']);p.add_argument('--workers',type=int,default=4);p.add_argument('--seed',type=int,default=701);p.add_argument('--stem',default='inputs/replay');p.add_argument('--rounds',type=int,default=12);p.add_argument('--radius',type=int,default=8);a=p.parse_args()
 if a.kind=='init':init_scan(a.workers,a.seed)
 elif a.kind=='order':order_scan()
 else:timing_scan(a.stem,a.workers,a.rounds,a.radius)
