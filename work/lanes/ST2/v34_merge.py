"""Merge the validated A-decoder instrument onto earlier SEPBC schedules.
Preserve B/C verification and native prefix; explicitly repair readout collisions.
"""
import sys,json,re,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import v34_campaign as v
from ortools.sat.python import cp_model
a=v.a;C=a.C;d=a.d

def decoder(c,advance):
 c=C.clone(c);R=c['meta']['R'];us=c['u'];old=c['t'];changes=[]
 coupling={}
 for q,h in [(10,9),(21,15)]:
  i=max((i for i,u in enumerate(us)if u.lines==[f'cx q[{q}],q[{h}];']),key=lambda i:old[i]);coupling[q]=i
  if advance:
   old[i]=R-1
   for j,u in enumerate(us):
    if j!=i and q in u.qs and old[j]==R-1 and u.name=='TDG':old[j]=R-2
 for q,bit in [(8,16),(9,17)]:
  i=next(i for i,u in enumerate(us)if u.lines==[f'measure q[{q}] -> c[{bit}];']);old[i]=R+2
  if q==8:us[i]=C.Unit([f'h q[{q}];',f'measure q[{q}] -> c[{bit}];',f'h q[{q}];'])
 # Exact reviewer parity transport; existing terminal readout edges commute.
 for cb,tb in [(17,20),(16,17)]:
  for j,line in enumerate(c['tail']):
   if not line.startswith('// DETECTOR'):continue
   bs=set(a.bits(line))
   if tb in bs:bs^={cb}
   c['tail'][j]='// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs))
 assert all(16 not in a.bits(s)for s in c['tail'])
 c['tail'].append('// DETECTOR c[16]')
 us.extend([C.Unit(['cx q[9],q[15];']),C.Unit(['cx q[8],q[9];'])]);old.extend([R,R+1]);newids={len(us)-2,len(us)-1}
 # At ties decoder gates precede old final readout CXs; D couplings precede
 # decoder gates, even when the desired same-tick placement cannot fit.
 def priority(i):
  if i in coupling.values():return -2
  if i in newids:return -1
  return 0
 order=sorted(range(len(us)),key=lambda i:(old[i],priority(i),i));us=[us[i]for i in order];target=[old[i]for i in order];horizon=max(target)+2
 m=cp_model.CpModel();ts=[m.NewIntVar(0,horizon,f't{i}')for i in range(len(us))];last={};dev=[]
 for i,u in enumerate(us):
  for q in u.qs:
   if q in last:m.Add(ts[i]>ts[last[q]])
   last[q]=i
  # Only the A/readout cone and the two explicitly advanced D couplings move.
  if target[i]<R or not(set(u.qs)&{8,9,14,15}):m.Add(ts[i]==target[i])
  else:m.Add(ts[i]>=target[i])
  z=m.NewIntVar(0,horizon,f'd{i}');m.AddAbsEquality(z,ts[i]-target[i]);dev.append(z)
 depth=m.NewIntVar(0,horizon,'depth');m.AddMaxEquality(depth,ts);m.Minimize(1000*depth+sum(dev))
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=3;st=s.Solve(m)
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return None,dict(status=s.StatusName(st))
 c['u']=us;c['t']=[s.Value(t)for t in ts]
 return d.normalize(c),dict(family='SEPBC_A_decoder_merge',R=R,advance=advance,status=s.StatusName(st),depth=s.Value(depth)+1,budget_screen=True)

def candidates():
 for name in ['guard5_timing_0','guard5_timing_1','guards_0235','guard_joint_2','A44_timing_10']:
  st=a.H.parents[2]/'work/lanes/SEPBC/v31'/name
  if not st.with_suffix('.qasm').exists():continue
  c=d.normalize(C.read(st))
  for advance in [True,False]:
   x,r=decoder(c,advance)
   if x is not None:yield name+('_early'if advance else'_same'),x,dict(r,source=str(st))
   else:print(name,advance,r,flush=True)
if __name__=='__main__':a.batch(candidates(),'merges',4)
