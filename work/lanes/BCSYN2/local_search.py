"""Incremental assumption-based LNS around clean82, with full clean cuts."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,itertools,json,random,time
from pathlib import Path
from synth import Model, verify
HERE=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=0);p.add_argument('--seconds',type=float,default=7200);p.add_argument('--cap',type=int,default=81);p.add_argument('--out',required=True);a=p.parse_args()
 initial=json.loads((HERE/'inputs/clean82.prep.json').read_text());m=Model(14,a.cap,a.seed)
 for t in range(15):
  for q in m.cells:m.cut((t,(q,)))
 for t,ss in enumerate(m.sel):
  for e in ss:m.cut((t+1,e))
 m.warm(initial);rng=random.Random(a.seed);start=time.monotonic();it=0;seen=set();base=initial
 while time.monotonic()-start<a.seconds:
  # Include every small window, plus larger disjoint layers to enable relocation.
  width=2+(it//14)%7
  if it%2:
   lo=rng.randrange(15-width);free=set(range(lo,lo+width))
  else:free=set(rng.sample(range(14),width))
  ass=[]
  for t,ss in enumerate(m.sel):
   if t in free:continue
   act={tuple(e) for e in base['ops'][t]}
   ass.extend(z if e in act else -z for e,z in ss.items())
  m.s.conf_budget(10000);st=time.monotonic();ok=m.s.solve_limited(assumptions=ass);it+=1
  if ok:
   d=m.candidate();v=verify(d);assert v['stim_target_pass'] and v['clean_pass'],v
   sig=tuple(tuple(sorted(tuple(e) for e in l)) for l in d['ops'])
   if sig not in seen:
    seen.add(sig);tag=f'{a.out}_w{len(seen):04d}';d['verification']=v;Path(tag+'.prep.json').write_text(json.dumps(d,indent=2))
    print(json.dumps(dict(iteration=it,seconds=time.monotonic()-start,free=sorted(free),cx=v['cx'],witness=tag)),flush=True)
   # Block the full selected gate network. Unlike cap minimization, this also
   # explores equal-CX networks with different fault correlations.
   mv={z for z in m.s.get_model() if z>0}
   m.add([-z if z in mv else z for ss in m.sel for z in ss.values()])
   if a.cap==82 and rng.random()<0.5:base=d
   m.warm(base)
  if it%100==0:print(json.dumps(dict(event='progress',iterations=it,elapsed=time.monotonic()-start,witnesses=len(seen))),flush=True)
 Path(a.out+'.receipt.json').write_text(json.dumps(dict(vars(a),status='COMPLETE',iterations=it,wall_seconds=time.monotonic()-start,witnesses=len(seen)),indent=2))
if __name__=='__main__':main()
