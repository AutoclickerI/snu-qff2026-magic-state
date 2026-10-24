"""Necessary placement relaxation for alternative exact encoder templates."""
from co_design import *

def solve(a):
 m=cp_model.CpModel();initial={};final={}
 for k in 'dabc':
  initial[k]=[m.NewIntVar(0,35,f'{k}i{i}') for i in range(7)];final[k]=[m.NewIntVar(0,35,f'{k}f{i}') for i in range(7)];m.AddAllDifferent(initial[k]);n=a.dhops if k=='d' else a.bhops
  pairs=[(u,v) for u in range(36) for v in range(36) if abs(u//6-v//6)+abs(u%6-v%6)<=n]
  for i in range(7):m.AddAllowedAssignments([initial[k][i],final[k][i]],pairs)
  if k=='d':
   for i,q in enumerate(D0):m.Add(initial[k][i]==q)
  else:
   p=template(a.option if k=='a' else a.bc_option,k)
   for u,v in {tuple(sorted(e)) for L in p['ops'] for e in L}:m.AddAllowedAssignments([initial[k][u],initial[k][v]],EDGES)
 m.AddAllDifferent(sum(final.values(),[]))
 for i in range(7):
  for k,l in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([final[k][i],final[l][i]],EDGES)
 s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=False
 st=s.Solve(m);out=dict(status=s.StatusName(st),result='TIMEOUT' if st==cp_model.UNKNOWN else s.StatusName(st),stats=s.ResponseStats(),args=vars(a))
 if st in (cp_model.FEASIBLE,cp_model.OPTIMAL):out.update(initial={k:[s.Value(x) for x in v] for k,v in initial.items()},final={k:[s.Value(x) for x in v] for k,v in final.items()})
 (HERE/a.out).with_suffix('.json').write_text(json.dumps(out,indent=1));print(out,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--option',default='l3_10');p.add_argument('--bc-option',default='l3_10');p.add_argument('--dhops',type=int,default=2);p.add_argument('--bhops',type=int,default=1);p.add_argument('--seconds',type=float,default=120);p.add_argument('--workers',type=int,default=2);solve(p.parse_args())
