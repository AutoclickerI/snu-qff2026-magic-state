from common import *
from ortools.sat.python import cp_model
for mask in [1<<i for i in range(7)]+[127]:
 h,us,tail,old,meta,init,ai=base()
 ac={i:next(j for j,u in enumerate(us) if old[j]==45 and u.lines==[f'cx q[{D[i]}],q[{A[i]}];']) for i in range(7)}
 # Fix B/C and the readout at v19 timing; put A checks before their TDG
 # wherever the cells and native per-wire dependencies permit it.
 m=cp_model.CpModel();tv=[m.NewIntVar(0,47,f't{i}') for i in range(len(us))]
 for j,t in enumerate(old):
  if j not in ai and j not in ac.values():m.Add(tv[j]==t)
 per={}
 for j,u in enumerate(us):
  for q in u.qs:per.setdefault(q,[]).append(j)
 for i,j in ac.items():
  if not (mask>>i&1):m.Add(tv[j]==45)
  # A CX commutes with the final T_DAG on its control data wire.
  if mask>>i&1:
   seq=per[D[i]];k=seq.index(j)
   if k and us[seq[k-1]].name=='TDG':seq[k-1],seq[k]=seq[k],seq[k-1]
 for seq in per.values():
  for i,j in zip(seq,seq[1:]):m.Add(tv[j]>tv[i])
 m.Minimize(1000*sum(tv[j] for i,j in ac.items() if mask>>i&1)-sum(tv[j] for j in ai))
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=10;st=s.Solve(m)
 if st not in (cp_model.FEASIBLE,cp_model.OPTIMAL):continue
 ts=[s.Value(v) for v in tv]
 if ts==old:continue
 emit(f'early_{mask:03}',us,ts,tail,dict(R=45,method='A coupling before final T_DAG where possible',A_coupling_steps=[ts[ac[i]] for i in range(7)]))
