from fast_templates import *
def run(a):
 m=cp_model.CpModel();v=lambda n,lo=0,hi=35:m.NewIntVar(lo,hi,n)
 E={k:[v(k+str(i))for i in range(6 if k=='c'else 7)]for k in'dabc'};m.AddAllDifferent(sum(E.values(),[]))
 for i in range(7):
  for k,j in [('d','a'),('d','b')]+([('b','c')]if i<6 else[]):m.AddAllowedAssignments([E[k][i],E[j][i]],ED)
 for i in range(5):m.Add(E['d'][i]<E['d'][i+1])
 m.AddAllowedAssignments([E['d'][0]],[(q,)for q in range(36)if q//6<=q%6 and q//6+q%6<=5])
 for k in'abc':
  pos=E[k];n=len(pos);dep=[m.NewConstant(0)]+[v(k+'depth'+str(i),1,n-1)for i in range(1,n)]
  for i in range(1,n):
   pp=[]
   for j in range(n):
    if j==i:continue
    z=m.NewBoolVar(k+f'p{i}_{j}');pp.append(z);m.AddAllowedAssignments([pos[i],pos[j]],ED).OnlyEnforceIf(z);m.Add(dep[i]>dep[j]).OnlyEnforceIf(z)
   m.AddBoolOr(pp)
 solver=cp_model.CpSolver();solver.parameters.num_search_workers=a.workers;solver.parameters.max_time_in_seconds=a.seconds;solver.parameters.random_seed=a.seed;m.ExportToFile(str(H/(a.name+'.pbtxt')));st=solver.Solve(m);r=dict(args=vars(a),status=solver.StatusName(st),stats=solver.ResponseStats(),model='stationary connected A7 B7 C6, arbitrary data, disjoint27 cells, D-A D-B matchings and B-C6 matching missing distinguished raw chain6; no encoder cap or prefix constraints')
 if st in(cp_model.OPTIMAL,cp_model.FEASIBLE):r['final']={k:[solver.Value(v)for v in vs]for k,vs in E.items()}
 (H/(a.name+'.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',default='c6_static_geometry');p.add_argument('--workers',type=int,default=4);p.add_argument('--seconds',type=float,default=180);p.add_argument('--seed',type=int,default=0);run(p.parse_args())
