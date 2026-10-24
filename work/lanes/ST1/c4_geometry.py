"""C4 endpoint/checker-route generator; every result still needs full scheduling/scoring."""
from common import *
import redesign as rd,itertools,collections,argparse
from graph_embeddings import embeddings
CHECKS=[[0,1,2],[0,3,4],[0,5,6],[1,3,5]]
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--b-catalog',default='work/lanes/ST1/c4_path_best.json');p.add_argument('--encoder-a',default='l3_10');p.add_argument('--a-moves',type=int,default=2);p.add_argument('--check-moves',type=int,default=5);p.add_argument('--seconds',type=float,default=120);p.add_argument('--workers',type=int,default=4);p.add_argument('--seed',type=int,default=0);a=p.parse_args();bcat=json.loads(Path(a.b_catalog).read_text());B=bcat['logical_b'];m=cp_model.CpModel();v=lambda n:m.NewIntVar(0,35,n)
D=[v('d'+str(i))for i in range(7)];A=[v('a'+str(i))for i in range(7)];AI=[v('ai'+str(i))for i in range(7)];AP=[m.NewIntVar(0,6,'ap'+str(i))for i in range(7)];m.AddAllowedAssignments(AP,rd.AUT);enc=rd.encoder(a.encoder_a,'a');m.AddAllowedAssignments(AI,embeddings(tuple(tuple(e)for e in enc[0])));move=[]
for i in range(7):
 m.AddAllowedAssignments([D[i],m.NewConstant(B[i])],rd.ED);m.AddAllowedAssignments([D[i],A[i]],rd.ED);src=v('source'+str(i));m.AddElement(AP[i],AI,src);d=m.NewIntVar(0,a.a_moves,'ad'+str(i));m.AddAllowedAssignments([src,A[i],d],[(q,t,abs(q//6-t//6)+abs(q%6-t%6))for q in range(36)for t in range(36)if abs(q//6-t//6)+abs(q%6-t%6)<=a.a_moves]);move.append(d)
m.AddAllDifferent([m.NewConstant(q)for q in B]+D+A)
# A is read before the parity checker routes; checker cells may therefore reuse A.
C=[];J=[]
for j,row in enumerate(CHECKS):
 ps=[v('c'+str(j)+'_'+str(k))for k in range(a.check_moves+1)];zs=[]
 for k in range(a.check_moves):
  z=m.NewBoolVar('z'+str(j)+'_'+str(k));m.AddAllowedAssignments([ps[k],ps[k+1],z],[(u,v,1)for u,v in rd.ED]+[(q,q,0)for q in range(36)])
  if k:m.Add(z<=zs[-1])
  zs.append(z);move.append(z)
 for q in ps:
  for r in B:m.Add(q!=r)
  for d in D:m.Add(q!=d)
 for i in row:
  st=m.NewIntVar(0,a.check_moves,'stage'+str(j)+'_'+str(i));q=v('contact'+str(j)+'_'+str(i));m.AddElement(st,ps,q);m.AddAllowedAssignments([q,m.NewConstant(B[i])],rd.ED);J.append((j,i,st,q))
 C.append((ps,zs))
m.Minimize(sum(move));s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=True;s.parameters.random_seed=a.seed;rows=[]
class CB(cp_model.CpSolverSolutionCallback):
 def on_solution_callback(self):
  out=dict(b_catalog=bcat,data=[self.Value(q)for q in D],a_final=[self.Value(q)for q in A],a_initial=[self.Value(q)for q in AI],a_permutation=[self.Value(q)for q in AP],checker_paths=[[self.Value(q)for q in ps[:1+sum(self.Value(z)for z in zs)]]for ps,zs in C],checks=[dict(j=j,i=i,stage=self.Value(st),cell=self.Value(q))for j,i,st,q in J],objective=self.ObjectiveValue(),args=vars(a),scope='Geometric necessary/sufficient checker routes with B/D held and A already read; A-preparation/movement lifetimes and prefix not scheduled.')
  name=a.out+f'_w{len(rows)}';(H/(name+'.json')).write_text(json.dumps(out,indent=2));rows.append(name);print(json.dumps(dict(name=name,objective=out['objective'])),flush=True)
st=s.Solve(m,CB());r=dict(status=s.StatusName(st),stats=s.ResponseStats(),witnesses=rows,args=vars(a));(H/(a.out+'.receipt.json')).write_text(json.dumps(r,indent=2));append_result(a.out,r,'C4 geometric generator only; complete native circuits are required before ranking.');print(json.dumps(r),flush=True)
