"""Long exact-loss SAT repair. A win never stops a seed's budget."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,random,time,math,hashlib
from pathlib import Path
from synth import Model,verify
from evaluate import price,H,BASE,database

def trace(d):return repr((sorted(d['pivots']),[(q,[tuple(e) for l in d['ops'] for e in l if q in e]) for q in sorted(d['cells'])]))
def main():
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int,required=True);p.add_argument('--depth',type=int,default=14);p.add_argument('--cap',type=int,default=98);p.add_argument('--seconds',type=float,default=7200);p.add_argument('--prefix',default='fb');a=p.parse_args();rng=random.Random(a.seed)
 base=json.loads((H/'inputs/fb_s401_0035.prep.json').read_text());initial=json.loads(json.dumps(base))
 hint=H/'runs'/f'fb_s{a.seed}.best.json'
 prior=json.loads(hint.read_text()) if hint.exists() else None
 if prior:base=prior['prep']
 if len(base['ops'])<a.depth:base['ops'].insert(a.seed%15,[])
 m=Model(a.depth,a.cap,a.seed)
 for t in range(a.depth+1):
  for q in m.cells:m.cut((t,(q,)))
 for t,ss in enumerate(m.sel):
  for e in ss:m.cut((t+1,e))
 m.warm(base);best=prior['total'] if prior else BASE;current=best;seen=set();start=time.monotonic();it=0;n=0;solver_secs=0.;bestprep=base;optbest=dict(timing='alap');last_progress=0
 while time.monotonic()-start<a.seconds:
  width=rng.choice([2,3,3,4,5,6,7,8]);lo=rng.randrange(a.depth+1-width);free=set(range(lo,lo+width)) if it%2 else set(rng.sample(range(a.depth),width));ass=[]
  for t,ss in enumerate(m.sel):
   if t in free:continue
   active={tuple(e) for e in base['ops'][t]};ass.extend(z if e in active else -z for e,z in ss.items())
  m.s.conf_budget(3000 if it%5 else 30000);tt=time.monotonic();ok=m.s.solve_limited(assumptions=ass);solver_secs+=time.monotonic()-tt;it+=1
  if ok is not True:continue
  d=m.candidate();v=verify(d);assert v['stim_target_pass'] and v['clean_pass']
  mv={z for z in m.s.get_model() if z>0};m.add([-z if z in mv else z for ss in m.sel for z in ss.values()]);tr=trace(d)
  if tr in seen:continue
  seen.add(tr);n+=1;tag=f'{a.prefix}_d{a.depth}_c{a.cap}_s{a.seed}_{n:05d}'
  opt=dict(timing='alap')
  # Separate chains retain a pure all-MX search; mixed chains co-optimize init/timing.
  if a.seed%3==0 and n%3:
   opt['mx']=[q for q in d['pivots'] if rng.random()<.9]
   opt['mz']=[q for q in d['cells'] if q not in d['pivots'] and rng.random()<.8]
  if a.seed%4==0 and n%5==0:opt.update(timing='random',timing_seed=rng.randrange(2**30))
  row=price(d,opt,tag,'feedback',threshold=min(best,BASE))
  if row.get('error')=='SCHEDULE_INFEASIBLE':
   opt['retime_window']=2;tag+='_rt';row=price(d,opt,tag,'feedback_retime',threshold=min(best,BASE))
  val=row.get('total',1);eligible=row.get('exp_minus_A1',0)>.505 and row.get('status')=='SCREENED'
  if eligible and val<best-1e-12 and row.get('check',{}).get('passed'):
   best=val;bestprep=d;optbest=opt;print(json.dumps(dict(event='best',tag=tag,total=best,seconds=time.monotonic()-start)),flush=True)
   (H/'runs'/f'{a.prefix}_s{a.seed}.best.json').write_text(json.dumps(dict(tag=tag,total=best,prep=d,options=opt),indent=2))
  temp=1e-7 if a.seed%2 else 0
  if eligible and (val<current or (temp and rng.random()<math.exp(min(0,(current-val)/temp)))):base=d;current=val
  if n%20==0:base=bestprep;current=best
  m.warm(base)
 rec=dict(vars(a),status='BUDGET_FINISHED',iterations=it,priced=n,seconds=time.monotonic()-start,solver_seconds=solver_secs,best=best)
 (H/'runs'/f'{a.prefix}_s{a.seed}.receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
if __name__=='__main__':main()
