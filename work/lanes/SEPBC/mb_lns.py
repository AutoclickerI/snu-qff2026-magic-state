"""Incremental native-MX/reset neighbourhoods of a clean BC witness."""
import mb_synth as S
from portfolio import H
import argparse,time,json,random
def main():
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=0);p.add_argument('--seconds',type=float,default=600);p.add_argument('--cap',type=int,default=81);a=p.parse_args();rng=random.Random(a.seed)
 d=json.loads((H/'inputs/seed82.prep.json').read_text());m=S.Model(14,a.cap,a.seed,[18,24,30,31,32,33,34,35],True,max_measurements=10)
 for t in range(15):
  for q in m.cells:m.cut((t,(q,)))
 m.warm(d);start=time.monotonic();attempts=0;count=0
 while time.monotonic()-start<a.seconds:
  width=rng.choice([4,5,6,7,8]);lo=rng.randrange(15-width);hi=lo+width;ass=[]
  for t,ss in enumerate(m.sel):
   if not lo<=t<hi:
    act=set(map(tuple,d['ops'][t]));ass.extend(z if e in act else -z for e,z in ss.items());ass.extend(-z for z in m.ms[t].values())
  m.s.conf_budget(12000);st=m.s.solve_limited(assumptions=ass);attempts+=1
  if st is True:
   dd=m.candidate();v=S.verify(dd);assert v['stim_target_pass'],v
   bad=S.ft.faults(dd,m.cells,'clean')
   if bad:
    for f in bad:m.cut(f[0])
    continue
   name=f'mblns_s{a.seed}_{count:03d}';dd['verification']=v;(H/(name+'.prep.json')).write_text(json.dumps(dd,indent=2));count+=1
   print(json.dumps(dict(name=name,lo=lo,hi=hi,cx=v['cx'],measurements=sum(map(len,dd['measures'])),elapsed=time.monotonic()-start)),flush=True)
   # Continue from each accepted reduction, retaining learned clauses.
   d=dd;m.warm(d);m.card([z for ss in m.sel for z in ss.values()],v['cx']-1)
  if st is False and lo==0 and hi==14:break
 r=dict(args=vars(a),attempts=attempts,witnesses=count,seconds=time.monotonic()-start)
 (H/f'mblns_s{a.seed}.receipt.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if __name__=='__main__':main()
