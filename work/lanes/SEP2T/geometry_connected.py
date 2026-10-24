"""Connected seven-cell encoders with one-step block relocation into holes.

Initial block cells are distinct from final data. Every moved block destination
is empty initially, so all block moves can run simultaneously without swaps.
Data are routed before preparation; their routing is validated by the builder.
"""
from co_design import *

def main(a):
 m=cp_model.CpModel(); initial={}; final={}; member={}; moves=[]; distances=[]
 for k in 'dabc':
  final[k]=[m.NewIntVar(0,35,f'{k}f{i}') for i in range(7)]
  if k=='d':
   for i,q in enumerate(D0):
    d=m.NewIntVar(0,a.dhops,f'ddist{i}')
    m.AddAllowedAssignments([final[k][i],d],[(v,abs(v//6-q//6)+abs(v%6-q%6)) for v in range(36) if abs(v//6-q//6)+abs(v%6-q%6)<=a.dhops]);distances.append(d)
   initial[k]=final[k]
   continue
  initial[k]=[m.NewIntVar(0,35,f'{k}i{i}') for i in range(7)]
  for i in range(7):
   z=m.NewBoolVar(f'{k}move{i}');moves.append(z)
   m.AddAllowedAssignments([initial[k][i],final[k][i],z],[(u,v,1) for u,v in EDGES]+[(q,q,0) for q in range(36)])
  x={}
  for i in range(7):
   for q in range(36):
    x[i,q]=m.NewBoolVar(f'{k}x{i}_{q}');m.Add(initial[k][i]==q).OnlyEnforceIf(x[i,q]);m.Add(initial[k][i]!=q).OnlyEnforceIf(x[i,q].Not())
  mem={q:sum(x[i,q] for i in range(7)) for q in range(36)};member[k]=mem
  flow={(u,v):m.NewIntVar(0,6,f'{k}flow{u}_{v}') for u,v in EDGES}
  for (u,v),f in flow.items():m.Add(f<=6*mem[u]);m.Add(f<=6*mem[v])
  for q in range(36):m.Add(sum(flow[u,v] for u,v in EDGES if u==q)-sum(flow[u,v] for u,v in EDGES if v==q)==7*x[0,q]-mem[q])
 m.AddAllDifferent(sum(initial.values(),[]));m.AddAllDifferent(sum(final.values(),[]))
 if not a.chains:
  for k in 'abc':
   for i in range(7):
    for l in 'abc':
     for j in range(7):
      if (k,i)!=(l,j):m.Add(final[k][i]!=initial[l][j])
 for i in range(7):
  for k,l in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([final[k][i],final[l][i]],EDGES)
 m.Minimize(5*sum(distances)+sum(moves))
 s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=False;s.parameters.random_seed=a.seed
 out=HERE/a.out
 def result(cb,status):return dict(status=status,method='connected_1hop',initial={k:[cb.Value(v) for v in vs] for k,vs in initial.items()},final={k:[cb.Value(v) for v in vs] for k,vs in final.items()},cost=cb.ObjectiveValue(),args=vars(a))
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   x=result(self,'FEASIBLE');out.with_suffix('.json').write_text(json.dumps(x,indent=1));print('incumbent',x,flush=True)
 st=s.Solve(m,CB());receipt=dict(status=s.StatusName(st),result='TIMEOUT' if st==cp_model.UNKNOWN else s.StatusName(st),stats=s.ResponseStats(),args=vars(a))
 out.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=1))
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):out.with_suffix('.json').write_text(json.dumps(result(s,s.StatusName(st)),indent=1))
 print(receipt,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--dhops',type=int,default=3);p.add_argument('--workers',type=int,default=2);p.add_argument('--seconds',type=float,default=120);p.add_argument('--seed',type=int,default=0);p.add_argument('--chains',action='store_true');main(p.parse_args())
