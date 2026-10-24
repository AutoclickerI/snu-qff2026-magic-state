"""Joint compact preparation geometry and prefix exit; full scheduling follows each SAT witness."""
from common import *
from graph_embeddings import embeddings
import redesign as rd,argparse
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--disjoint-ab',action='store_true');p.add_argument('--encoder',default='s34c15,s13c8,s13c8');p.add_argument('--moves',type=int,default=2);p.add_argument('--data-moves',type=int,default=3);p.add_argument('--prefix-variant',default='cats13');p.add_argument('--external',default='ab');p.add_argument('--workers',type=int,default=2);p.add_argument('--seconds',type=float,default=180);p.add_argument('--seed',type=int,default=0);a=p.parse_args()
pre,det=rd.prefix(a.prefix_variant);cells=sorted({q for u in pre for q in u.qs});embs=[e for e in rd.mappings(cells)if e['sym']==0];enc={k:rd.encoder(a.encoder,k)for k in'abc'}
m=cp_model.CpModel();v=lambda n:m.NewIntVar(0,35,n);em=m.NewIntVar(0,len(embs)-1,'embed');mp=[v('pref'+str(q))for q in cells];m.AddAllowedAssignments([em]+mp,[[i]+e['cells']for i,e in enumerate(embs)])
P={k:[v(k+'p'+str(i))for i in range(7)]for k in'abc'};E={k:[v(k+'e'+str(i))for i in range(7)]for k in'dabc'};G={};dist=[]
for k in'abc':
 native=[v(k+'native'+str(i))for i in range(7)];m.AddAllowedAssignments(native,embeddings(tuple(tuple(e)for e in enc[k][0])));G[k]=[m.NewIntVar(0,6,k+'perm'+str(i))for i in range(7)];m.AddAllowedAssignments(G[k],rd.AUT)
 for i in range(7):
  m.AddElement(G[k][i],native,P[k][i]);d=m.NewIntVar(0,a.moves,k+'distance'+str(i));m.AddAllowedAssignments([P[k][i],E[k][i],d],[(q,t,abs(q//6-t//6)+abs(q%6-t%6))for q in range(36)for t in range(36)if abs(q//6-t//6)+abs(q%6-t%6)<=a.moves]);dist.append(d)
 if k in a.external:
  for q in P[k]:
   for r in mp:m.Add(q!=r)
if a.disjoint_ab:m.AddAllDifferent(P['a']+P['b'])
for i in range(7):
 for k,j in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([E[k][i],E[j][i]],rd.ED)
 d=m.NewIntVar(0,a.data_moves,'dd'+str(i));m.AddAllowedAssignments([mp[cells.index(rd.PD[i])],E['d'][i],d],[(q,t,abs(q//6-t//6)+abs(q%6-t%6))for q in range(36)for t in range(36)if abs(q//6-t//6)+abs(q%6-t%6)<=a.data_moves]);dist.extend([d,d])
m.AddAllDifferent(sum(E.values(),[]));m.Minimize(sum(dist));s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=False;s.parameters.random_seed=a.seed
rows=[]
class Save(cp_model.CpSolverSolutionCallback):
 def on_solution_callback(self):
  initial={k:[self.Value(q)for q in qs]for k,qs in P.items()};final={k:[self.Value(q)for q in qs]for k,qs in E.items()};blocks={}
  for k in'abc':
   perm=[self.Value(q)for q in G[k]];inv={j:i for i,j in enumerate(perm)};ops,piv=enc[k];blocks[k]=dict(ops=[[initial[k][inv[u]],initial[k][inv[v]]]for u,v in ops],pivots=[initial[k][inv[u]]for u in piv])
  name=a.out+f'_w{len(rows)}';x=dict(initial=initial,final=final,blocks=blocks,args=vars(a),prefix_embedding=embs[self.Value(em)],objective=self.ObjectiveValue(),scope='geometric relaxation only; no timing, collision-free paths or noise claim');(H/(name+'.json')).write_text(json.dumps(x,indent=2));rows.append(name);print(json.dumps(dict(name=name,objective=x['objective'])),flush=True)
st=s.Solve(m,Save());receipt=dict(status=s.StatusName(st),stats=s.ResponseStats(),witnesses=rows,args=vars(a));(H/(a.out+'.receipt.json')).write_text(json.dumps(receipt,indent=2));append_result(a.out,receipt,'Geometric relaxation for joint native compact preparations and nearby prefix exits. Full circuits must be assembled and scored before ranking.');print(json.dumps(receipt),flush=True)
