from round35 import *
from ortools.sat.python import cp_model
import itertools
A=[1,14,8,9,2,16,15];OUT=HERE/'r36';deadline=int(sys.argv[1]) if len(sys.argv)>1 else 43
edges=[(a,b) for a in range(7) for b in range(7) if abs(A[a]//6-A[b]//6)+abs(A[a]%6-A[b]%6)==1]
GL=[]
for a,b,c in itertools.product(range(1,8),repeat=3):
 vals=[a,b,a^b,c,a^c,b^c,a^b^c]
 if len(set(vals))==7:GL.append([v>>j&1 for v in vals for j in range(3)])
rows=[]
for third in [8,1,9,15,16]:
 piv=[2,14,third];release={1:38,14:38,8:36,9:38,2:38,16:38,15:40};release[third]+=1
 m=cp_model.CpModel();ts=range(36,deadline);state={(q,t,j):m.NewBoolVar(f's{q}_{t}_{j}') for q in range(7) for t in range(36,deadline+1) for j in range(3)}
 for q in range(7):
  v=(1<<piv.index(A[q])) if A[q] in piv else 0
  for j in range(3):m.Add(state[q,36,j]==(v>>j&1))
 gate={(a,b,t):m.NewBoolVar(f'g{a}_{b}_{t}') for a,b in edges for t in ts}
 for t in ts:
  for q in range(7):
   m.Add(sum(gate[a,b,t] for a,b in edges if q in (a,b))<=1)
   incoming=[gate[a,b,t] for a,b in edges if b==q];none=m.NewBoolVar(f'none{q}_{t}');m.Add(sum(incoming)==0).OnlyEnforceIf(none);m.Add(sum(incoming)==1).OnlyEnforceIf(none.Not())
   for j in range(3):m.Add(state[q,t+1,j]==state[q,t,j]).OnlyEnforceIf(none)
  for a,b in edges:
   g=gate[a,b,t]
   if t<max(release[A[a]],release[A[b]]):m.Add(g==0)
   for j in range(3):m.AddAllowedAssignments([state[a,t,j],state[b,t,j],state[b,t+1,j]],[(0,0,0),(0,1,1),(1,0,1),(1,1,0)]).OnlyEnforceIf(g)
 m.AddAllowedAssignments([state[q,deadline,j] for q in range(7) for j in range(3)],GL)
 m.Minimize(sum(gate.values()));sol=cp_model.CpSolver();sol.parameters.num_workers=7;sol.parameters.max_time_in_seconds=180
 sol.parameters.log_search_progress=True
 st=sol.Solve(m);r=dict(third=third,deadline=deadline,status=sol.StatusName(st),bound=sol.BestObjectiveBound(),seconds=sol.WallTime(),release=release)
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):r.update(CX=int(sol.ObjectiveValue()),pivots=piv,ops=[[A[a],A[b],t] for t in ts for a,b in edges if sol.Value(gate[a,b,t])])
 rows.append(r);(OUT/f'dual_sat_{deadline}.json').write_text(json.dumps(rows,indent=2));print('RESULT',json.dumps(r),flush=True)
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):break
