"""Hierarchical endpoint geometry only; no monolithic circuit scheduling."""
import os,sys,json,argparse,time,collections
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent;PARENT=H.parent
NB={q:[p for p in range(36)if abs(q//6-p//6)+abs(q%6-p%6)==1]for q in range(36)}
ED=[(q,p)for q in NB for p in NB[q]]

def run(a):
 prefix=json.loads((PARENT/(a.prefix+'.prefix.json')).read_text());em=prefix['embeddings'][a.embedding];mp={int(q):v for q,v in em['mapping'].items()};data=[mp[q]for q in prefix['data_qubits']];release={mp[q]:v for q,v in ((int(q),v)for q,v in prefix['release_asap'].items())};poutputs=set(data)
 free=[q for q in range(36)if q not in poutputs and (q not in mp.values()or release.get(q,1000)<=a.release)]
 m=cp_model.CpModel();v=lambda n,lo=0,hi=35:m.NewIntVar(lo,hi,n);E={k:[v(k+str(i))for i in range(7)]for k in'dabc'};m.AddAllDifferent(sum(E.values(),[]))
 for i in range(7):
  for k,j in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([E[k][i],E[j][i]],ED)
 for q in E['b']+E['c']:m.AddAllowedAssignments([q],[(q,)for q in free])
 def connected(ps,label):
  dep=[m.NewConstant(0)]+[v(label+'dep'+str(i),1,len(ps)-1)for i in range(1,len(ps))]
  for i in range(1,len(ps)):
   parents=[]
   for j in range(len(ps)):
    if j==i:continue
    z=m.NewBoolVar(label+f'parent{i}_{j}');parents.append(z);m.AddAllowedAssignments([ps[i],ps[j]],ED).OnlyEnforceIf(z);m.Add(dep[i]>dep[j]).OnlyEnforceIf(z)
   m.AddBoolOr(parents)
 connected(E['b']+E['c'],'bc');connected(E['a'],'a')
 # Distances refer to fixed code labels; no arbitrary relabelling after selection.
 distances=[];ready=[]
 for i,q in enumerate(data):
  d=v('dist'+str(i),0,a.data_hops);m.AddAllowedAssignments([E['d'][i],d],[(p,abs(q//6-p//6)+abs(q%6-p%6))for p in range(36)if abs(q//6-p//6)+abs(q%6-p%6)<=a.data_hops]);distances.append(d);ready.append(prefix['last_data_asap'][str(prefix['data_qubits'][i])]+1+2*d)
 r=v('data_ready',0,70);m.AddMaxEquality(r,ready)
 # Pure geometric lower bound. Real paths and preparation synthesis come next.
 score=1000*r+sum(distances);m.Minimize(score)
 solver=cp_model.CpSolver();solver.parameters.num_workers=a.workers;solver.parameters.cp_model_presolve=False;solver.parameters.max_time_in_seconds=a.seconds;solver.parameters.random_seed=a.seed
 rows=[];seen=set()
 class Save(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   end={k:[self.Value(z)for z in vs]for k,vs in E.items()};key=tuple(sum((end[k]for k in'dabc'),[]))
   if key in seen:return
   seen.add(key);row=dict(args=vars(a),prefix=a.prefix,embedding=a.embedding,mapping=mp,initial_data=data,final=end,region=sorted(end['b']+end['c']),resource_available_from=max([release.get(q,0)for q in end['b']+end['c']]),data_distances=[self.Value(d)for d in distances],data_ready_lb=self.Value(r),score=self.ObjectiveValue(),scope='geometry/lower-bound screen only; no gate synthesis or collision-free routing yet')
   row['R_lower_bounds']={str(d):max(row['data_ready_lb'],row['resource_available_from']+d+1)for d in[9,10,11]};name=a.out+f'_g{len(rows):03d}';(H/(name+'.region.json')).write_text(json.dumps(row,indent=2));rows.append(dict(name=name,Rlb=row['R_lower_bounds'],distance=sum(row['data_distances']),available=row['resource_available_from']));print(json.dumps(rows[-1]),flush=True)
   if a.first:self.StopSearch()
 m.ExportToFile(str(H/(a.out+'.pbtxt')));st=solver.Solve(m,Save());rec=dict(args=vars(a),status=solver.StatusName(st),free_cells=free,stats=solver.ResponseStats(),regions=rows);(H/(a.out+'.receipt.json')).write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--prefix',default='v29c');p.add_argument('--embedding',type=int,default=0);p.add_argument('--release',type=int,default=0);p.add_argument('--data-hops',type=int,default=6);p.add_argument('--seconds',type=float,default=180);p.add_argument('--workers',type=int,default=4);p.add_argument('--seed',type=int,default=0);p.add_argument('--first',action='store_true');run(p.parse_args())
