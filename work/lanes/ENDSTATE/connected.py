from fast_templates import *
def run(a):
 m=cp_model.CpModel();v=lambda n,lo=0,hi=35:m.NewIntVar(lo,hi,n)
 P={k:[v(k+'p'+str(i))for i in range(7)]for k in 'abc'};E={k:[v(k+'e'+str(i))for i in range(7)]for k in 'dabc'}
 order={k:v(k+'order',0,2)for k in 'abc'};m.AddAllDifferent(list(order.values()))
 for k in 'abc':
  m.AddAllDifferent(P[k]);depth=[m.NewConstant(0)]+[v(k+'depth'+str(i),1,6)for i in range(1,7)]
  for i in range(1,7):
   pars=[]
   for j in range(7):
    if j==i:continue
    z=m.NewBoolVar(k+f'parent{i}_{j}');pars.append(z);m.AddAllowedAssignments([P[k][i],P[k][j]],ED).OnlyEnforceIf(z);m.Add(depth[i]>depth[j]).OnlyEnforceIf(z)
   m.AddBoolOr(pars)
  for i in range(7):m.AddAllowedAssignments([P[k][i],E[k][i]],[(q,p)for q in range(36)for p in range(36)if abs(q//6-p//6)+abs(q%6-p%6)<=a.moves])
  if a.stationary_a and k=='a':
   for i in range(7):m.Add(P[k][i]==E[k][i])
 m.AddAllDifferent(sum(E.values(),[]))
 for i in range(7):
  for k,j in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([E[k][i],E[j][i]],ED)
 for i in range(6):m.Add(E['d'][i]<E['d'][i+1])
 m.AddAllowedAssignments([E['d'][0]],[(q,)for q in range(36)if q//6<=q%6 and q//6+q%6<=5])
 if not a.relax:
  assert a.moves==1
  for k in 'abc':
   for p in P[k]:
    for q in E['d']:m.Add(p!=q)
   for j in 'abc':
    if j==k:continue
    z=m.NewBoolVar(j+'before'+k);m.Add(order[j]<order[k]).OnlyEnforceIf(z);m.Add(order[j]>order[k]).OnlyEnforceIf(z.Not())
    for p in P[k]:
     for q in E[j]:m.Add(p!=q).OnlyEnforceIf(z)
   rr=[v(k+'vacancy'+str(i),0,6)for i in range(7)]
   for i in range(7):
    for j in range(7):
     if i==j:continue
     z=m.NewBoolVar(k+f'dep{i}_{j}');m.Add(E[k][i]==P[k][j]).OnlyEnforceIf(z);m.Add(E[k][i]!=P[k][j]).OnlyEnforceIf(z.Not());m.Add(rr[i]>rr[j]).OnlyEnforceIf(z)
 s=cp_model.CpSolver();s.parameters.num_search_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=not a.no_presolve;s.parameters.random_seed=a.seed
 m.ExportToFile(str(H/(a.name+'.pbtxt')))
 st=s.Solve(m);rec=dict(args=vars(a),status=s.StatusName(st),stats=s.ResponseStats(),model='unlabelled connected-prep geometry; arbitrary CX cost; no occupancy'if a.relax else 'unlabelled connected preps; stationary final data; sequential block order and vacancy moves; CX cap not yet checked')
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):rec.update(initial={k:[s.Value(v)for v in vs]for k,vs in P.items()},final={k:[s.Value(v)for v in vs]for k,vs in E.items()},order=sorted('abc',key=lambda k:s.Value(order[k])))
 (H/(a.name+'.json')).write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--moves',type=int,default=1);p.add_argument('--seconds',type=float,default=600);p.add_argument('--workers',type=int,default=4);p.add_argument('--seed',type=int,default=0);p.add_argument('--relax',action='store_true');p.add_argument('--no-presolve',action='store_true');p.add_argument('--stationary-a',action='store_true');run(p.parse_args())
