import os,sys,json,itertools,time,argparse
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent
NB={q:[p for p in range(36) if abs(q//6-p//6)+abs(q%6-p%6)==1] for q in range(36)}
ED=[(q,p) for q in NB for p in NB[q]]
AUT=[[((a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0))-1 for i in range(1,8)]for a in range(1,8)for b in range(1,8)for c in range(1,8)if len({a,b,c,a^b,a^c,b^c,a^b^c})==7]
def embeddings(edges):
 adj={i:set()for i in range(7)}
 for u,v in edges:adj[u].add(v);adj[v].add(u)
 out=[]
 def rec(mp):
  if len(mp)==7:out.append([mp[i]for i in range(7)]);return
  u=max((i for i in adj if i not in mp),key=lambda i:(len(adj[i]&mp.keys()),len(adj[i]),-i))
  vs=set(range(36))-set(mp.values())
  for n in adj[u]&mp.keys():vs&=set(NB[mp[n]])
  for v in sorted(vs):rec(mp|{u:v})
 rec({});return out

def run(a):
 source=Path('work/lanes/ST1/inputs/prep_l3_10.json' if a.template=='l3' else 'work/lanes/DR/prepA_L5_s7307.json')
 prep=json.loads(source.read_text());cells=prep.get('cells',[1,14,8,9,2,16,15]);edges=sorted({tuple(sorted((cells.index(u),cells.index(v))))for l in prep['ops']for u,v in l})
 emb=embeddings(edges);print('embeddings',len(emb),flush=True)
 m=cp_model.CpModel();V=lambda n:m.NewIntVar(0,35,n)
 P={k:[V(k+'p'+str(i))for i in range(7)]for k in 'abc'};E={k:[V(k+'e'+str(i))for i in range(7)]for k in 'dabc'}
 for k in 'abc':
  native=[V(k+'native'+str(i))for i in range(7)];m.AddAllowedAssignments(native,emb)
  perm=[m.NewIntVar(0,6,k+'perm'+str(i))for i in range(7)]
  m.AddAllowedAssignments(perm,AUT if k!='a' else [list(range(7))])
  for i in range(7):m.AddElement(perm[i],native,P[k][i])
  for i in range(7):m.AddAllowedAssignments([P[k][i],E[k][i]],[(q,p)for q in range(36)for p in range(36)if abs(q//6-p//6)+abs(q%6-p%6)<=a.moves])
 m.AddAllDifferent(sum(E.values(),[]))
 for i in range(7):
  for k,j in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([E[k][i],E[j][i]],ED)
 # D4 fundamental triangle for labelled d0.
 m.AddAllowedAssignments([E['d'][0]],[(q,)for q in range(36)if q//6<=q%6 and q//6+q%6<=5])
 if a.order:
  for idx,k in enumerate(a.order):
   forbidden=E['d']+sum((E[j]for j in a.order[:idx]),[])
   for p in P[k]:
    for q in forbidden:m.Add(p!=q)
   # For one hop, ordering into vacancies; each source stays occupied until measurement.
   ranks=[m.NewIntVar(0,6,k+'rank'+str(i))for i in range(7)]
   for i in range(7):
    for j in range(7):
     if i==j:continue
     z=m.NewBoolVar(k+f'dep{i}_{j}');m.Add(E[k][i]==P[k][j]).OnlyEnforceIf(z);m.Add(E[k][i]!=P[k][j]).OnlyEnforceIf(z.Not());m.Add(ranks[i]>ranks[j]).OnlyEnforceIf(z)
 m.ExportToFile(str(H/(a.name+'.pbtxt')))
 s=cp_model.CpSolver();s.parameters.num_search_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=False;s.parameters.random_seed=a.seed
 st=s.Solve(m);rec=dict(args=vars(a),status=s.StatusName(st),stats=s.ResponseStats(),model='template; sequential complete-block preparation; stationary final data; one-hop vacancy-order constraint' if a.order else 'geometric relaxation, no lifetimes')
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):rec.update(initial={k:[s.Value(v)for v in vs]for k,vs in P.items()},final={k:[s.Value(v)for v in vs]for k,vs in E.items()})
 (H/(a.name+'.json')).write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--template',default='l3');p.add_argument('--order',default='');p.add_argument('--moves',type=int,default=1);p.add_argument('--seconds',type=float,default=180);p.add_argument('--workers',type=int,default=2);p.add_argument('--seed',type=int,default=0);run(p.parse_args())
