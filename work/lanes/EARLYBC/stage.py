from core import *
from ortools.sat.python import cp_model
import argparse,time
FREE=sorted(set(range(36))-(set(D0)|{1,2,6,9,10,13,14,19}))
AE=[(1,2),(2,8),(8,9),(8,14),(14,15),(15,16)]
def solve(args):
 m=cp_model.CpModel();init={q:m.NewIntVar(0,35,f'i{q}') for q in A+B+C};final={q:m.NewIntVar(0,35,f'f{q}') for q in A+B+C+D};m.AddAllDifferent(list(init.values()));m.AddAllDifferent(list(final.values()))
 adj=[(u,v) for u in range(36) for v in nb(u)]
 for q in init:m.AddAllowedAssignments([init[q]],[(x,) for x in (sorted(set(range(36))-set(D0)) if args.late_a and q in A else (FREE+[13,19] if args.released else FREE))])
 for u,v in AE+list(zip(BCCHAIN,BCCHAIN[1:])):m.AddAllowedAssignments([init[u],init[v]],adj)
 for u,v in list(zip(D,A))+list(zip(D,B))+list(zip(B,C))+[(17,16),(19,25)]:m.AddAllowedAssignments([final[u],final[v]],adj)
 ds=[]
 for q in init:
  d=m.NewIntVar(0,args.bhops,f'd{q}');m.AddAllowedAssignments([init[q],final[q],d],[(u,v,abs(u//6-v//6)+abs(u%6-v%6)) for u in range(36) for v in range(36) if abs(u//6-v//6)+abs(u%6-v%6)<=args.bhops]);ds.append(d)
 dd=[]
 for i,q in enumerate(D):
  d=m.NewIntVar(0,args.dhops,f'dd{q}');m.AddAllowedAssignments([final[q],d],[(v,abs(D0[i]//6-v//6)+abs(D0[i]%6-v%6)) for v in range(36) if abs(D0[i]//6-v//6)+abs(D0[i]%6-v%6)<=args.dhops]);dd.append(d)
 m.Minimize(sum(ds)+3*sum(dd));s=cp_model.CpSolver();s.parameters.max_time_in_seconds=args.seconds;s.parameters.num_workers=args.workers;s.parameters.cp_model_presolve=False;s.parameters.random_seed=args.seed
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   out=dict(status='FEASIBLE',init={q:self.Value(x) for q,x in init.items()},final={q:self.Value(x) for q,x in final.items()},cost=self.ObjectiveValue(),args=vars(args),wall=self.WallTime())
   (HERE/f'stage_{args.seed}_{int(self.ObjectiveValue())}.json').write_text(json.dumps(out,indent=2));print('solution',self.ObjectiveValue(),self.WallTime(),flush=True)
 st=s.Solve(m,CB());print('status',s.StatusName(st),s.ResponseStats(),flush=True)
 (HERE/f'stage_{args.seed}.receipt.json').write_text(json.dumps(dict(status=s.StatusName(st),stats=s.ResponseStats(),args=vars(args)),indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--late-a',action='store_true');p.add_argument('--released',action='store_true');p.add_argument('--seed',type=int,default=0);p.add_argument('--seconds',type=int,default=180);p.add_argument('--workers',type=int,default=4);p.add_argument('--bhops',type=int,default=3);p.add_argument('--dhops',type=int,default=2);solve(p.parse_args())
