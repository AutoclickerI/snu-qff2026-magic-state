from fast_templates import *
def run(a):
 m=cp_model.CpModel();v=lambda n,lo=0,hi=35:m.NewIntVar(lo,hi,n)
 E={k:[v(k+str(i))for i in range(7)]for k in'dabc'};helpers={k:v(k+'helper')for k in'bc'}
 order={k:v(k+'order',0,2)for k in'abc'};m.AddAllDifferent(list(order.values()))
 m.AddAllDifferent(sum(E.values(),[]))
 for i in range(7):
  for k,j in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([E[k][i],E[j][i]],ED)
 for i in range(6):m.Add(E['d'][i]<E['d'][i+1])
 m.AddAllowedAssignments([E['d'][0]],[(q,)for q in range(36)if q//6<=q%6 and q//6+q%6<=5])
 for k in'abc':
  pos=E[k]+([helpers[k]]if k in'bc'else[]);n=len(pos)
  use=m.NewBoolVar(k+'usehelper')if k in'bc'else None
  if k in'bc':
   for q in E['d']+E[k]:m.Add(helpers[k]!=q)
   for other in'abc':
    if other==k:continue
    earlier=m.NewBoolVar(other+'before'+k);m.Add(order[other]<order[k]).OnlyEnforceIf(earlier);m.Add(order[other]>order[k]).OnlyEnforceIf(earlier.Not())
    for q in E[other]:m.Add(helpers[k]!=q).OnlyEnforceIf(earlier)
  depth=[m.NewConstant(0)]+[v(k+'depth'+str(i),1,n-1)for i in range(1,n)]
  for i in range(1,n):
   pars=[]
   for j in range(n):
    if i==j:continue
    z=m.NewBoolVar(k+f'parent{i}_{j}');pars.append(z);m.AddAllowedAssignments([pos[i],pos[j]],ED).OnlyEnforceIf(z);m.Add(depth[i]>depth[j]).OnlyEnforceIf(z)
    if k in'bc'and(i==7 or j==7):m.Add(z<=use)
   if i==7:m.AddBoolOr(pars).OnlyEnforceIf(use)
   else:m.AddBoolOr(pars)
 s=cp_model.CpSolver();s.parameters.num_search_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.random_seed=a.seed
 m.ExportToFile(str(H/(a.name+'.pbtxt')));st=s.Solve(m);r=dict(args=vars(a),status=s.StatusName(st),stats=s.ResponseStats(),model='all blocks stationary; A connected7; B and C each connected with zero or one helper; helper may borrow a later-prepared block cell; arbitrary sequential block order; data stationary; no CX bound')
 if st in(cp_model.OPTIMAL,cp_model.FEASIBLE):r.update(final={k:[s.Value(v)for v in vs]for k,vs in E.items()},helpers={k:s.Value(v)for k,v in helpers.items()},order=sorted('abc',key=lambda k:s.Value(order[k])))
 (H/(a.name+'.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=180);p.add_argument('--workers',type=int,default=2);p.add_argument('--seed',type=int,default=0);run(p.parse_args())
