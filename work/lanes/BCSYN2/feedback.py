"""Assumption-based SAT repair ranked by exact in-situ 1-F after each witness."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,random,time,hashlib
from pathlib import Path
from synth import Model,verify
from price import price
H=Path(__file__).resolve().parent

def trace(d):return repr((sorted(d['pivots']),[(q,[tuple(e) for l in d['ops'] for e in l if q in e]) for q in d['cells']]))
def main():
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int,required=True);p.add_argument('--seconds',type=float,default=7205);a=p.parse_args();rng=random.Random(a.seed)
 base=json.loads((H/'runs/lns_c81_s201_w0111.prep.json').read_text());m=Model(14,82,a.seed)
 for t in range(15):
  for q in m.cells:m.cut((t,(q,)))
 for t,ss in enumerate(m.sel):
  for e in ss:m.cut((t+1,e))
 m.warm(base);best=7.189718838871983e-5;seen={trace(base):'p2134_mx'};start=time.monotonic();it=0;rows=[];n=0
 while time.monotonic()-start<a.seconds:
  width=rng.choice([2,3,3,4,5,6]);lo=rng.randrange(15-width);free=set(range(lo,lo+width)) if it%2 else set(rng.sample(range(14),width));ass=[]
  for t,ss in enumerate(m.sel):
   if t in free:continue
   active={tuple(e) for e in base['ops'][t]};ass.extend(z if e in active else -z for e,z in ss.items())
  m.s.conf_budget(3000);ok=m.s.solve_limited(assumptions=ass);it+=1
  if ok is not True:continue
  d=m.candidate();v=verify(d);assert v['stim_target_pass'] and v['clean_pass']
  mv={z for z in m.s.get_model() if z>0};m.add([-z if z in mv else z for ss in m.sel for z in ss.values()]);tr=trace(d)
  if tr in seen:continue
  n+=1;tag=f'fb_s{a.seed}_{n:04d}';prep=H/'runs'/f'{tag}.prep.json';prep.write_text(json.dumps(d,indent=2));seen[tr]=tag
  row=price(prep,tag,mode='release_alap',mx=d['pivots']);rows.append(row)
  if row.get('check',{}).get('passed') and row.get('total',1)<best-1e-12:
   best=row['total'];base=d;print(json.dumps(dict(event='best',tag=tag,total=best,seconds=time.monotonic()-start)),flush=True)
   (H/f'feedback_s{a.seed}_best.json').write_text(json.dumps(dict(tag=tag,total=best,prep=str(prep)),indent=2))
  m.warm(base)
 (H/f'feedback_s{a.seed}_receipt.json').write_text(json.dumps(dict(status='BUDGET_FINISHED',iterations=it,priced=n,seconds=time.monotonic()-start,best=best),indent=2))
if __name__=='__main__':main()
