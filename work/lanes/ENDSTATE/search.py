import os,sys,json,itertools,argparse,time
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent
LIB=json.loads((H/'library_input.json').read_text());ENC=json.loads((H/'library_encoders.json').read_text())
ED=[(u,v)for u in range(36)for v in range(36)if abs(u//6-v//6)+abs(u%6-v%6)==1]

def run(a):
 m=cp_model.CpModel();v=lambda n,lo=0,hi=35:m.NewIntVar(lo,hi,n)
 costs=[(s,c,r['cx'])for s,x in enumerate(ENC)for c,r in enumerate(x)if 0<=r['cx']<=a.cap];shapes={s for s,c,n in costs};emb=[r for r in LIB['embeddings']if r[0]in shapes]
 print(dict(cost_classes=len(costs),shapes=len(shapes),embeddings=len(emb)),flush=True)
 P={k:[v(k+'p'+str(i))for i in range(7)]for k in 'abc'};E={k:[v(k+'e'+str(i))for i in range(7)]for k in 'dabc'}
 meta={};rank={k:v(k+'rank',0,2)for k in 'abc'};m.AddAllDifferent(list(rank.values()))
 for k in 'abc':
  native=[v(k+'native'+str(i))for i in range(7)];sid=v(k+'shape',0,len(ENC)-1);cid=v(k+'class',0,29);cx=v(k+'cx',0,a.cap)
  m.AddAllowedAssignments([sid,*native],emb);m.AddAllowedAssignments([sid,cid,cx],costs)
  perm=[v(k+'perm'+str(i),0,6)for i in range(7)]
  if k=='a':
   reps={}
   for r in LIB['permutations']:reps.setdefault(r[0],r)
   m.AddAllowedAssignments([cid,*perm],list(reps.values()))
  else:m.AddAllowedAssignments([cid,*perm],LIB['permutations'])
  for i in range(7):m.AddElement(perm[i],native,P[k][i])
  for i in range(7):m.AddAllowedAssignments([P[k][i],E[k][i]],[(q,p)for q in range(36)for p in range(36)if abs(q//6-p//6)+abs(q%6-p%6)<=a.moves])
  meta[k]=dict(native=native,shape=sid,code_class=cid,perm=perm,cx=cx,rank=rank[k])
 m.AddAllDifferent(sum(E.values(),[]))
 for i in range(7):
  for k,j in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([E[k][i],E[j][i]],ED)
 m.AddAllowedAssignments([E['d'][0]],[(q,)for q in range(36)if q//6<=q%6 and q//6+q%6<=5])
 if not a.relax:
  assert a.moves==1
  for k in 'abc':
   for p in P[k]:
    for q in E['d']:m.Add(p!=q)
   for j in 'abc':
    if j==k:continue
    earlier=m.NewBoolVar(j+'before'+k);m.Add(rank[j]<rank[k]).OnlyEnforceIf(earlier);m.Add(rank[j]>rank[k]).OnlyEnforceIf(earlier.Not())
    for p in P[k]:
     for q in E[j]:m.Add(p!=q).OnlyEnforceIf(earlier)
   rr=[v(k+'vacancy'+str(i),0,6)for i in range(7)]
   for i in range(7):
    for j in range(7):
     if i==j:continue
     z=m.NewBoolVar(k+f'dep{i}_{j}');m.Add(E[k][i]==P[k][j]).OnlyEnforceIf(z);m.Add(E[k][i]!=P[k][j]).OnlyEnforceIf(z.Not());m.Add(rr[i]>rr[j]).OnlyEnforceIf(z)
 if a.hint:
  d=json.loads(Path(a.hint).read_text())
  for k in P:
   for x,y in zip(P[k],d['initial'][k]):m.AddHint(x,y)
  for k in E:
   for x,y in zip(E[k],d['final'][k]):m.AddHint(x,y)
 m.ExportToFile(str(H/(a.name+'.pbtxt')))
 s=cp_model.CpSolver();s.parameters.num_search_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=False;s.parameters.random_seed=a.seed
 st=s.Solve(m);rec=dict(args=vars(a),status=s.StatusName(st),stats=s.ResponseStats(),model='geometric relaxation (no occupancy)'if a.relax else 'all connected seven-cell unitary encoders; sequential block preparation; stationary final data; one-hop vacancy ordering; free block order; global code automorphism quotient')
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):
  rec.update(initial={k:[s.Value(v)for v in vs]for k,vs in P.items()},final={k:[s.Value(v)for v in vs]for k,vs in E.items()},blocks={k:{n:[s.Value(v)for v in x]if isinstance(x,list)else s.Value(x)for n,x in r.items()}for k,r in meta.items()})
 (H/(a.name+'.json')).write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--cap',type=int,default=12);p.add_argument('--moves',type=int,default=1);p.add_argument('--seconds',type=float,default=600);p.add_argument('--workers',type=int,default=8);p.add_argument('--seed',type=int,default=0);p.add_argument('--relax',action='store_true');p.add_argument('--hint');run(p.parse_args())
