import os,sys,json,time
sys.dont_write_bytecode=True
from pathlib import Path
from ortools.sat.python import cp_model
HERE=Path(__file__).resolve().parent
D0=[0,20,7,4,3,15,8]
NB={q:[u for u in range(36) if abs(q//6-u//6)+abs(q%6-u%6)==1] for q in range(36)}
def run():
 m=cp_model.CpModel();p={k:[m.NewIntVar(0,35,k+str(i)) for i in range(n)] for k,n in [('d',7),('a',7),('b',7),('f',4)]}
 m.AddAllDifferent(sum(p.values(),[]));edges=[(q,u) for q in range(36) for u in NB[q]]
 rows=[[0,1,2],[0,3,4],[0,5,6],[1,3,5]]
 for j,row in enumerate(rows):
  for i in row:m.AddAllowedAssignments([p['b'][i],p['f'][j]],edges)
 for i in range(7):
  m.AddAllowedAssignments([p['d'][i],p['a'][i]],edges);m.AddAllowedAssignments([p['d'][i],p['b'][i]],edges)
 mem={};eq={}
 for k,ps in p.items():
  for q in range(36):
   zz=[]
   for i,v in enumerate(ps):
    z=m.NewBoolVar('');m.Add(v==q).OnlyEnforceIf(z);m.Add(v!=q).OnlyEnforceIf(z.Not());eq[k,i,q]=z;zz.append(z)
   b=m.NewBoolVar('');m.Add(b==sum(zz));mem[k,q]=b
 h={q:m.NewBoolVar(f'h{q}') for q in range(36)}
 for q in range(36):m.Add(h[q]+sum(mem[k,q] for k in p)<=1)
 m.Add(sum(h.values())<=3)
 def connect(kind,root,mask,size):
  flows={(q,u):m.NewIntVar(0,11,'') for q,u in edges}
  for (q,u),v in flows.items():m.Add(v<=11*mask[q]);m.Add(v<=11*mask[u])
  for q in range(36):
   r=m.NewIntVar(0,11,'');m.AddMultiplicationEquality(r,[size,eq[root,0,q]])
   m.Add(sum(flows[q,u]-flows[u,q] for u in NB[q])==r-mask[q])
 connect('bf','b',{q:mem['b',q]+mem['f',q] for q in range(36)},11)
 size=m.NewIntVar(7,10,'size');m.Add(size==7+sum(h.values()))
 connect('a','a',{q:mem['a',q]+h[q] for q in range(36)},size)
 costs=[]
 for i,q in enumerate(D0):
  d=m.NewIntVar(0,4,'');m.AddElement(p['d'][i],[abs(q//6-u//6)+abs(q%6-u%6) for u in range(36)],d);costs.append(d)
 for i in []:pass
 m.Minimize(100*sum(costs)+sum(h.values()))
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=180
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   out={k:[self.Value(v) for v in ps] for k,ps in p.items()};out.update(hA=[q for q,v in h.items() if self.Value(v)],distance=sum(self.Value(v) for v in costs),objective=self.ObjectiveValue(),bound=self.BestObjectiveBound())
   (HERE/'layout_direct.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
 st=s.Solve(m,CB());print(s.StatusName(st),s.ResponseStats(),flush=True)
if __name__=='__main__':
 assert os.getloadavg()[0]<os.cpu_count()-2
 run()
