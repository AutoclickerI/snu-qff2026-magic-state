"""Exact vacancy routing of two separate blocks in synchronous move batches."""
from construct_route import *

def main(a):
 if a.geometry:
  geo=json.loads(Path(a.geometry).read_text());FIND.update(geo['final']);cost=geo['block_distance'];b=geo['initial']['b'];c=geo['initial']['c']
 else:
  cs=candidates(a.automorphisms);cost,b,c=cs[a.placement]
 initial={f'{k}{i}':q for k,arr in [('b',b),('c',c)] for i,q in enumerate(arr)}
 goals={f'{k}{i}':q for k in 'bc' for i,q in enumerate(FIND[k])};keys=sorted(initial);N=len(keys);T=a.steps;available=sorted(set(range(36))-set(FIND['d']))
 m=cp_model.CpModel();positions=[[m.NewIntVarFromDomain(cp_model.Domain.FromValues(available),f'p{i}_{t}') for t in range(T+1)] for i in range(N)];moves=[]
 for i,key in enumerate(keys):
  m.Add(positions[i][0]==initial[key]);m.Add(positions[i][-1]==goals[key])
  for t in range(T):
   z=m.NewBoolVar(f'm{i}_{t}');moves.append(z)
   m.AddAllowedAssignments([positions[i][t],positions[i][t+1],z],[(u,v,1) for u,v in EDGES if u in available and v in available]+[(q,q,0) for q in available])
 for t in range(T+1):m.AddAllDifferent([positions[i][t] for i in range(N)])
 for t in range(T):
  for i in range(N):
   for j in range(N):
    if i!=j:m.Add(positions[i][t]!=positions[j][t+1])
 if a.hint:
  hh=json.loads(Path(a.hint).read_text())['macro_positions']
  for i,key in enumerate(keys):
   for t in range(T+1):m.AddHint(positions[i][t],hh[key][t])
 if a.cap is not None:m.Add(sum(moves)<=a.cap)
 m.Minimize(sum(moves));s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=False;s.parameters.random_seed=a.seed
 s.parameters.stop_after_first_solution=a.first
 out=HERE/a.out
 def result(cb):
  ms=[]
  for t in range(T):
   for i,key in enumerate(keys):
    u,v=cb.Value(positions[i][t]),cb.Value(positions[i][t+1])
    if u!=v:ms.append((key,u,v))
  return dict(initial=initial,final=FIND,moves=ms,macro_positions={key:[cb.Value(x) for x in positions[i]] for i,key in enumerate(keys)},static_distance=cost,args=vars(a))
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   x=result(self);out.with_suffix('.route.json').write_text(json.dumps(x,indent=1));print('incumbent',len(x['moves']),self.WallTime(),flush=True)
 st=s.Solve(m,CB());receipt=dict(status=s.StatusName(st),result='TIMEOUT' if st==cp_model.UNKNOWN else s.StatusName(st),stats=s.ResponseStats(),args=vars(a));out.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=1));print(receipt,flush=True)
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):
  x=result(s);out.with_suffix('.route.json').write_text(json.dumps(x,indent=1));build(x['initial'],x['moves'],out,a.workers,a.automorphisms or bool(a.geometry))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--placement',type=int,default=0);p.add_argument('--steps',type=int,default=30);p.add_argument('--workers',type=int,default=8);p.add_argument('--seconds',type=float,default=600);p.add_argument('--seed',type=int,default=0);p.add_argument('--automorphisms',action='store_true');p.add_argument('--first',action='store_true');p.add_argument('--hint');p.add_argument('--cap',type=int);p.add_argument('--geometry');main(p.parse_args())
