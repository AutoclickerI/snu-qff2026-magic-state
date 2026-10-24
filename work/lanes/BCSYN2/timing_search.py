"""Exact third-order search of B+C operation timing, all other times held."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,concurrent.futures,json,math,time,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path.insert(0,str(H));import schedule as S
from util import native_times
from moments import evaluate,exact2
from synth import B,C

def score(job):
 tag,text,md,change=job;out=H/'full'/tag;out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(md,indent=2))
 ev=exact2.Eval(text,md['data_qubits']);r=evaluate(ev);r.update(tag=tag,change=change,R=md['R'],CX=md['CX'],verification=md['verification'],prep_cx=md['verification']['cx'])
 out.with_suffix('.timing.json').write_text(json.dumps(r,indent=2));return r

def main():
 p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--workers',type=int,default=3);p.add_argument('--rounds',type=int,default=3);p.add_argument('--radius',type=int,default=2);a=p.parse_args();base=Path(a.stem);base=base if base.is_absolute() else H/'full'/base
 text=base.with_suffix('.qasm').read_text();md=json.loads(base.with_suffix('.json').read_text());seen=set();best=evaluate(exact2.Eval(text,md['data_qubits']))['total'];rows=[]
 for rnd in range(a.rounds):
  h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us);pred,succ=S.build_dag(us);jobs=[];byhash={}
  init={q:max(i for i,u in enumerate(us) if u.qs==(q,) and ts[i]<md['R'] and u.name in ('RESET','RX','MEASURE','MX')) for q in B+C}
  ids=[i for i,u in enumerate(us) if set(u.qs)<=set(B+C) and ts[i]<md['R'] and all(i>=init[q] for q in u.qs)]
  for i in ids:
   lo=max((ts[j]+1 for j in pred[i]),default=0);hi=min((ts[j]-1 for j in succ[i]),default=md['R']-1)
   for tt in range(max(lo,ts[i]-a.radius),min(hi,ts[i]+a.radius)+1):
    if tt==ts[i]:continue
    nt=ts.copy();nt[i]=tt;new=S.emit(h,us,nt,tail);sig=hashlib.sha256(new.encode()).hexdigest()[:14]
    if sig in seen:continue
    seen.add(sig);tag=f'time_{sig}';jobs.append((tag,new,md,dict(unit=i,lines=us[i].lines,old=ts[i],new=tt,round=rnd)));byhash[tag]=new
  print(json.dumps(dict(event='round_start',round=rnd,candidates=len(jobs),baseline=best)),flush=True)
  with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as ex:
   for r in ex.map(score,jobs):
    rows.append(r)
    if r['total']<best-1e-12:
     best=r['total'];text=byhash[r['tag']];(H/'timing_best.json').write_text(json.dumps(r,indent=2));print(json.dumps(dict(event='best',**r)),flush=True)
  if not jobs:break
 (H/'timing_results.json').write_text(json.dumps(rows,indent=2));print('FINISHED',best,flush=True)
if __name__=='__main__':main()
