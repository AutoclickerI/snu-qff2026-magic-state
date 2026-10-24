import os,sys,json,itertools,time
sys.dont_write_bytecode=True
from pathlib import Path
from ortools.sat.python import cp_model
HERE=Path(__file__).resolve().parent
from generate import PAR,REVIEW
EDGES=[(u,v) for u in range(36) for v in range(36) if abs(u//6-v//6)+abs(u%6-v%6)==1]

def place(kind,fixed=None):
 m=cp_model.CpModel();N=25 if kind=='review_full' else 11
 p=[m.NewIntVar(0,35,f'p{i}') for i in range(N)];m.AddAllDifferent(p)
 graph=set((u,v) for l in REVIEW for u,v in l) if kind.startswith('review') else set((i,7+j) for j,row in enumerate(PAR) for i in row)
 for u,v in graph:m.AddAllowedAssignments([p[u],p[v]],EDGES)
 if fixed:
  for i,q in enumerate(fixed):m.Add(p[i]==q)
 if kind=='review_full':
  for i in range(7):
   m.AddAllowedAssignments([p[i],p[11+i]],EDGES)
   m.AddAllowedAssignments([p[11+i],p[18+i]],EDGES)
  # A connectivity by single-commodity flow.
  a=p[18:25]; adj={}
  for i in range(7):
   for j in range(i+1,7):
    b=m.NewBoolVar(f'a{i}_{j}');m.AddAllowedAssignments([a[i],a[j]],EDGES).OnlyEnforceIf(b);adj[i,j]=b
  flows={}
  for i in range(7):
   for j in range(7):
    if i!=j:
     f=m.NewIntVar(0,6,f'f{i}_{j}');m.Add(f<=6*adj[min(i,j),max(i,j)]);flows[i,j]=f
  for i in range(7):m.Add(sum(flows[i,j]-flows[j,i] for j in range(7) if j!=i)==(6 if i==0 else -1))
  ds=[0,20,7,4,3,15,8];cost=[]
  for i,q in enumerate(ds):
   c=m.NewIntVar(0,10,f'd{i}');m.AddElement(p[11+i],[abs(q//6-x//6)+abs(q%6-x%6) for x in range(36)],c);cost.append(c)
  m.Minimize(sum(cost))
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=120
 t=time.time();st=s.Solve(m);out=dict(kind=kind,status=s.StatusName(st),seconds=time.time()-t,bound=s.BestObjectiveBound())
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):
  v=[s.Value(x) for x in p];out.update(B=v[:7],F=v[7:11]);
  if N>11:out.update(d=v[11:18],a=v[18:25],distance=s.ObjectiveValue())
 (HERE/f'placement_{kind}.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)

if __name__=='__main__':
 assert os.getloadavg()[0]<os.cpu_count()-2
 place('direct4')
 place('review_full',[8,9,22,26,16,13,19,14,15,21,20])
