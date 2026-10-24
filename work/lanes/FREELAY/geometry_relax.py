"""Independent placement-only relaxation to identify time-model binding cuts."""
from co_design import *
def main(a):
 m=cp_model.CpModel();initial={};final={}
 for k in 'dabc':
  initial[k]=[m.NewIntVar(0,35,f'{k}i{i}') for i in range(7)]
  final[k]=[m.NewIntVar(0,35,f'{k}f{i}') for i in range(7)]
  m.AddAllDifferent(initial[k])
  n=2 if k=='d' else a.hops
  pairs=[(u,v) for u in range(36) for v in range(36) if abs(u//6-v//6)+abs(u%6-v%6)<=n]
  for i in range(7):m.AddAllowedAssignments([initial[k][i],final[k][i]],pairs)
  if k=='d':
   for i,q in enumerate(D0):m.Add(initial[k][i]==q)
  else:
   p=template(a.option if k=='a' else 'l5_11',k)
   for u,v in {tuple(sorted(e)) for L in p['ops'] for e in L}:m.AddAllowedAssignments([initial[k][u],initial[k][v]],EDGES)
 m.AddAllDifferent(sum(final.values(),[]))
 for i in range(7):
  for k,l in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([final[k][i],final[l][i]],EDGES)
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=90;s.parameters.cp_model_presolve=False
 st=s.Solve(m);out=dict(status=s.StatusName(st),stats=s.ResponseStats(),args=vars(a))
 if st in (cp_model.FEASIBLE,cp_model.OPTIMAL):out.update(initial={k:[s.Value(x) for x in v] for k,v in initial.items()},final={k:[s.Value(x) for x in v] for k,v in final.items()})
 (HERE/f'geometry_h{a.hops}_{a.option}.json').write_text(json.dumps(out,indent=1));print(out,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--hops',type=int,default=1);p.add_argument('--option',default='l5_11');main(p.parse_args())
