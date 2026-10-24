from common import *
from ortools.sat.python import cp_model
import itertools

def retime(units,old,round_ids,mode='alap',early=False):
 m=cp_model.CpModel();ts=[m.NewIntVar(0,90,f't{i}') for i in range(len(units))];R=m.NewIntVar(40,80,'R')
 per={}
 for i,u in enumerate(units):
  for q in u.qs:per.setdefault(q,[]).append(i)
  if i in round_ids:m.Add(ts[i]==R+old[i]-45)
  else:m.Add(ts[i]<R)
 for seq in per.values():
  for i,j in zip(seq,seq[1:]):m.Add(ts[j]>ts[i])
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=20
 m.Minimize(R);st=s.Solve(m);assert st in (cp_model.FEASIBLE,cp_model.OPTIMAL)
 m.Add(R==s.Value(R));m.Maximize(sum(ts));st=s.Solve(m);assert st in (cp_model.FEASIBLE,cp_model.OPTIMAL)
 return [s.Value(t) for t in ts],s.Value(R)

def init_variants():
 for qs in [(1,2,16),(1,2,9,15,16),(8,),(1,2,8,16)]:
  h,us,tail,ts,meta,init,ai=base();drop=set()
  for q in qs:
   i=init[q]
   if q in (1,2):
    prev=max(j for j,u in enumerate(us[:i]) if q in u.qs);assert us[prev].name=='MX'
    us[prev]=unit(us[prev].lines+[f'h q[{q}];']);drop.add(i)
   elif q==16:
    bit=80+q;us[i]=unit([f'measure q[{q}] -> c[{bit}];']);tail.append(f'// DETECTOR c[{bit}]')
   else:us[i]=unit([f'h q[{q}];'])
  # S.Unit's upstream constructor assumes every h has a second line. A
  # standalone H is handled below in the local constructor shim.
  uu=[u for i,u in enumerate(us) if i not in drop];tt=[t for i,t in enumerate(ts) if i not in drop]
  rr={i for i,t in enumerate(tt) if t>=45};tt,R=retime(uu,tt,rr)
  emit('reuse_'+'_'.join(map(str,qs)),uu,tt,tail,dict(R=R,method='known-state init/reuse',sites=qs))

def encoder_variants():
 sources=[ROOT/'work/lanes/FLAG/prepA_L5_flag_candidates.json',ROOT/'work/lanes/EXENC/prepA_L5_exact_top.json']
 candidates=[]
 for src in sources:candidates+=json.loads(src.read_text())
 for src in sorted((ROOT/'work/lanes/SCHED/encoders').glob('enc_[0-9][0-9][0-9].json')):candidates.append(json.loads(src.read_text())['encoder'])
 candidates.append(json.loads((ROOT/'work/lanes/FREELAY/inputs/prepA_L5_s7307.json').read_text()))
 # Keep all distinct candidate paths; source table already carries Pareto
 # witnesses. Reorder disjoint gates identically to avoid duplicate builds.
 seen=set();kept=[]
 for c in candidates:
  edges=[tuple(e) for L in c['ops'] for e in L]
  key=(tuple(sorted(c['pivots'])),tuple(tuple(e for e in edges if q in e) for q in A))
  if key not in seen:seen.add(key);kept.append(c)
 (HERE/'encoder_candidates.json').write_text(json.dumps(kept))
 for k,c in enumerate(kept):
  h,us,tail,ts,meta,init,ai=base()
  # Take all existing prefix/hop/BC operations before new A. This preserves
  # dependencies on releases while leaving CP-SAT to interleave them.
  before=[i for i,t in enumerate(ts) if t<45 and i not in ai];after=[i for i,t in enumerate(ts) if t>=45]
  au=[unit([f'reset q[{q}];']+([f'h q[{q}];'] if q in c['pivots'] else [])) for q in A]
  au += [unit([f'cx q[{u}],q[{v}];']) for L in c['ops'] for u,v in L]
  uu=[us[i] for i in before]+au+[us[i] for i in after];tt=[ts[i] for i in before]+[40]*len(au)+[ts[i] for i in after]
  rr=set(range(len(before)+len(au),len(uu)));tt,R=retime(uu,tt,rr)
  emit(f'enc_{k:03}',uu,tt,tail,dict(R=R,method='in situ A encoder',encoder=c,encoder_index=k))
 print('encoders',len(kept),flush=True)

if __name__=='__main__':
 if sys.argv[1]=='init':init_variants()
 elif sys.argv[1]=='enc':encoder_variants()
