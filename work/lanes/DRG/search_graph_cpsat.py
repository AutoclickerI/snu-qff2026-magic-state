import sys,json,collections
from ortools.sat.python import cp_model
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR');import poc
s={int(k):[(t,typ,frozenset(S)) for t,typ,S in v] for k,v in json.load(open('/home/jihoon/competitions/quantumn/work/lanes/DR/sched_zfirst.json')).items()}
for name,bfn in [('pair',lambda s:poc.build_hybrid(s,z_mode='pair')),('cat1',lambda s:poc.build_hybrid(s,z_mode='cat1')),('clean',lambda s:poc.build_clean(s,clean_z=True))]:
 b,_,_=bfn(s); n=b.next_q; E=list(set(tuple(qs) for t,k,kind,qs,tag in b.ops if kind=='cx')); print(name,n,len(E))
 m=cp_model.CpModel();p=[m.NewIntVar(0,35,f'p{v}') for v in range(n)]
 # all qubits distinct only if same global physical simulation; reuse allowed when nonoverlap. Compute op interval per qubit.
 ints=[]
 for q in range(n):
  tt=[t for t,k,kind,qs,tag in b.ops if q in qs];ints.append((min(tt),max(tt)))
 for a in range(n):
  for c in range(a):
   if not (ints[a][1]<ints[c][0] or ints[c][1]<ints[a][0]):m.Add(p[a]!=p[c])
 allowed=[[a,z] for a in range(36) for z in range(36) if abs(a//6-z//6)+abs(a%6-z%6)==1]
 for a,c in E:m.AddAllowedAssignments([p[a],p[c]],allowed)
 sol=cp_model.CpSolver();sol.parameters.max_time_in_seconds=30;sol.parameters.num_search_workers=8
 rr=sol.Solve(m);print('status',sol.StatusName(rr),flush=True)
 if rr in (cp_model.FEASIBLE,cp_model.OPTIMAL):print([sol.Value(z) for z in p])
