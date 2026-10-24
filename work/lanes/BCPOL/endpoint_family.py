"""Rank-four and rank-three C endpoints, with all independent C parities."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from synth import *
from build import build
from moments_batch import exact2,evaluate
import argparse,json,random,time,copy,lzma,math
p=argparse.ArgumentParser();p.add_argument('rank',type=int,choices=[3,4]);p.add_argument('value',type=int);p.add_argument('--seconds',type=float,default=900);a=p.parse_args();seed=1100+10*a.rank+a.value;rng=random.Random(seed);tag=f'rank{a.rank}_{a.value}';start=time.monotonic()
parents=[]
for plane in [1,2,3,4,5]:
 path=H/f'runs/endpoint_{plane}_s{707+plane}.best.json'
 if path.exists() and (a.rank==3 or not (plane&a.value).bit_count()%2):parents.append(json.loads(path.read_text()))
parent=min(parents,key=lambda d:d['row']['total']);base=copy.deepcopy(parent['prep']);base.update(kind='endpoint',value=a.value,endpoint_rank=a.rank,extra_check=True);D=16;base['ops']=(base['ops']+[[]]*D)[:D]
m=Model(D,110,seed,'endpoint',a.value,extra_check=True,endpoint_rank=a.rank)
for t in range(D+1):
 for q in m.cells:m.cut((t,(q,)))
for t,ss in enumerate(m.sel):
 for e in ss:m.cut((t+1,e))
m.warm(base);seen=set();count=priced=it=0;best=1.;current=1.;bestprep=base;solver_seconds=0.
with lzma.open(H/'runs'/f'{tag}.jsonl.xz','wt') as witness:
 while time.monotonic()-start<a.seconds:
  width=rng.choice([3,4,5,6,8,12,16] if not count else [2,3,4,5,6,8]);lo=rng.randrange(D+1-width);free=set(range(lo,lo+width)) if it%2 else set(rng.sample(range(D),width));ass=[]
  for t,ss in enumerate(m.sel):
   if t not in free:
    active={tuple(e) for e in base['ops'][t]};ass.extend(z if e in active else -z for e,z in ss.items())
  m.s.conf_budget(5000);tt=time.monotonic();ok=m.s.solve_limited(assumptions=ass);solver_seconds+=time.monotonic()-tt;it+=1
  if ok is not True:continue
  d=m.candidate();v=verify(d);assert v['stim_target_pass'] and v['policy_pass'];mv={z for z in m.s.get_model() if z>0};m.add([-z if z in mv else z for ss in m.sel for z in ss.values()]);tr=trace(d)
  if tr in seen:continue
  seen.add(tr);count+=1;ntag=f'{tag}_{count:05d}'
  try:
   opt=dict(base='v25k',timing='alap',endpoint_parity=True,mx=[q for q in d['pivots'] if q!=19]);text,md=build(d,opt);ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single)
   if abs(c1)>=1e-12:row=dict(status='INVALID_C1',c1=c1)
   else:
    row=evaluate(ev);priced+=1;val=row['total'];row.update(tag=ntag,verification=v,delta_loss=val-6.505010287762392e-5,delta_A1=-math.log(row['exp_minus_A1']/.5106215532040006))
    if row['exp_minus_A1']>=.5002 and val<best:
     import tprep
     t0=time.monotonic();ck=tprep.check(text,md['data_qubits'],shots=10**6,seed=0);sec=time.monotonic()-t0;row['judge']=dict(passed=bool(ck.passed),acceptance=float(ck.acceptance),seconds=sec)
     if ck.passed and sec<20*3.0/2.3:
      best=val;bestprep=d;out=H/'finalists'/ntag;out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(md,indent=2));out.with_suffix('.screen.json').write_text(json.dumps(row,indent=2));(H/'runs'/f'{tag}.best.json').write_text(json.dumps(dict(tag=ntag,prep=d,row=row),indent=2));print(json.dumps(dict(event='best',**row)),flush=True)
    if val<current or rng.random()<math.exp(min(0,(current-val)/3e-7)):base=d;current=val
    if count%30==0 and best<1:base=bestprep;current=best
  except (ValueError,AssertionError) as e:row=dict(tag=ntag,status='INVALID',error=str(e))
  witness.write(json.dumps(dict(prep=d,row=row))+'\n');witness.flush();m.warm(base)
rec=dict(rank=a.rank,value=a.value,status='BUDGET_FINISHED',iterations=it,witnesses=count,priced=priced,best=best,solver_seconds=solver_seconds,seconds=time.monotonic()-start)
(H/'runs'/f'{tag}.receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
