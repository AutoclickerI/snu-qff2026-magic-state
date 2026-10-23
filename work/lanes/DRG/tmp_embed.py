import sys,json,collections
from ortools.sat.python import cp_model
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR'); import poc
s={int(k):[(t,typ,frozenset(S)) for t,typ,S in v] for k,v in json.load(open('/home/jihoon/competitions/quantumn/work/lanes/DR/sched_zfirst.json')).items()}
b,_,_=poc.build_hybrid(s,z_mode='pair'); n=b.next_q
edges=sorted(set(tuple(sorted(qs)) for t,k,kind,qs,tag in b.ops if kind=='cx'))
print(n,len(edges),collections.Counter(sum(1 for e in edges if v in e) for v in range(n)))
col={}; ok=True
for v in range(n):
 if v not in col:
  col[v]=0; st=[v]
  while st:
   a=st.pop()
   for x,y in edges:
    if x==a:z=y
    elif y==a:z=x
    else:continue
    if z in col and col[z]==col[a]: ok=False
    elif z not in col:col[z]=1-col[a]; st.append(z)
print('bip',ok,collections.Counter(col.values()))
N=6; cells=list(range(36)); adjpairs=[(a,b) for a in cells for b in cells if abs(a//6-b//6)+abs(a%6-b%6)==1]
m=cp_model.CpModel(); x={(v,c):m.NewBoolVar(f'x{v}_{c}') for v in range(n) for c in cells}
for v in range(n):m.Add(sum(x[v,c] for c in cells)==1)
for c in cells:m.Add(sum(x[v,c] for v in range(n))<=1)
p=[m.NewIntVar(0,35,f'p{v}') for v in range(n)]
for v in range(n):m.Add(p[v]==sum(c*x[v,c] for c in cells))
allowed=[list(z) for z in adjpairs]
for a,bv in edges:m.AddAllowedAssignments([p[a],p[bv]],allowed)
vmax=max(range(n),key=lambda v:sum(v in e for e in edges)); print('vmax',vmax); m.Add(p[vmax]==14)
solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=300; solver.parameters.num_search_workers=8; solver.parameters.log_search_progress=True
res=solver.Solve(m); print('res',solver.StatusName(res),solver.ObjectiveValue(),solver.BestObjectiveBound())
if res in (cp_model.OPTIMAL,cp_model.FEASIBLE):
 a=[solver.Value(p[v]) for v in range(n)]; print('map',a); print('coords',[(c//6,c%6) for c in a]); print('bad',[(u,v) for u,v in edges if (abs(a[u]//6-a[v]//6)+abs(a[u]%6-a[v]%6)!=1)])
