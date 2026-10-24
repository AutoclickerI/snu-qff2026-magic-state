"""Move the synchronized round, allowing every commuting CX reorder."""
from core import *
import argparse

def proposals(base):
 us=base['u'];old=base['t'];R=base['meta']['R'];per={}
 for i,u in enumerate(us):
  for q in u.qs:per.setdefault(q,[]).append(i)
 for nr in range(R-3,R+2):
  for ordermode in ['fixed','commuting']:
   for obj in ['near','late','early']:
    c=clone(base);m=cp_model.CpModel();tv=[m.new_int_var(0,nr+2,f't{i}')for i in range(len(us))]
    for seq in per.values():
     for pos,j in enumerate(seq):
      for i in seq[:pos]:
       if ordermode=='commuting'and commute(us[i],us[j]):m.add(tv[i]!=tv[j])
       else:m.add(tv[i]<tv[j])
    for i,t in enumerate(old):
     if t>=R:m.add(tv[i]==t+nr-R)
     else:m.add(tv[i]<nr)
    ds=[]
    for i,t in enumerate(old):
     d=m.new_int_var(0,100,f'd{i}');m.add_abs_equality(d,tv[i]-t);ds.append(d)
    if obj=='near':m.minimize(sum(ds))
    if obj=='late':m.minimize(sum(ds)-10*sum(tv))
    if obj=='early':m.minimize(sum(ds)+10*sum(tv))
    s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=5;s.parameters.cp_model_presolve=False
    st=s.solve(m)
    receipt=dict(family='timing',move='round_cpsat',R=nr,order=ordermode,objective=obj,status=s.status_name(st),source=base['source'],source_sha256=hashlib.sha256(textof(base).encode()).hexdigest())
    with (OUT/'round_solver.jsonl').open('a')as f:f.write(json.dumps(receipt)+'\n')
    if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):continue
    c['t']=[s.value(v)for v in tv];yield c,receipt
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--workers',type=int,default=4);ap.add_argument('--label',default='round_lns');a=ap.parse_args();batch(list(proposals(read(a.stem))),a.label,a.workers)
