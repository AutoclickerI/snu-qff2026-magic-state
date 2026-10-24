"""Free endpoint/time search using ST1's reviewed native lifetime model read-only.
All callbacks/models/receipts are confined to ENDSTATE. Prefixes are extracted
from the named MAIN QASM, including the v29 fused moves.
"""
import os,sys,json,argparse,importlib.util,time,collections
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
import model_core as rd
from types import SimpleNamespace
from fast_templates import AUT,ED
rd.H=H;rd.AUT=AUT;rd.ED=ED
from ortools.sat.python import cp_model

def run(a):
 prefix=json.loads((H/(a.prefix+'.prefix.json')).read_text());templates={x['id']:x for x in json.loads((H/'templates.json').read_text())};tpl=templates[a.template]
 selected=[o for o in prefix['ops']if o['name']!='TDG'];rd.PD=prefix['data_qubits']
 rd.prefix=lambda:([SimpleNamespace(lines=o['lines'],name=o['name'],qs=o['qs'])for o in selected],prefix['detectors'][:])
 rd.encoder=lambda name,k:(tpl['plus'if k=='a'else'zero']['ops'],tpl['plus'if k=='a'else'zero']['pivots'])
 if a.abstract_depth:rd.encoder=lambda name,k:([],[])
 a.encoder=a.template;a.min_round=25;a.catalog=a.geometry;a.compact9=False;a.external_moves=0
 m,V,pre,dets,emb,enc,dec=rd.create(a)
 helpers={}
 if a.abstract_depth:
  for k in'abc':
   ps=[V['tokens'][f'{k}{i}']['pos'][0]for i in range(7)];start=V['tokens'][k+'0']['init']
   extra=bool(a.helpers and k in'bc')
   if extra:
    q=m.NewIntVar(0,35,k+'helper');ps.append(q);end=m.NewIntVar(0,a.max_round,k+'helper_end');m.Add(end==start+a.abstract_depth+2);helpers[k]=dict(cell=q,init=start,end=end)
    V['space_intervals'].append(m.NewFixedSizeIntervalVar(q,1,k+'helper_cell'));V['time_intervals'].append(m.NewFixedSizeIntervalVar(start,a.abstract_depth+2,k+'helper_life'))
   depth=[m.NewConstant(0)]+[m.NewIntVar(1,len(ps)-1,k+'tree'+str(i))for i in range(1,len(ps))]
   m.AddAllDifferent(ps)
   for i in range(7):
    tok=V['tokens'][f'{k}{i}'];m.Add(tok['init']==start);m.Add(tok['ts'][0]>=start+a.abstract_depth+1+extra)
   m.Add(V['R']>=start+a.abstract_depth+1+extra)
   for i in range(1,len(ps)):
    pp=[]
    for j in range(len(ps)):
     if i==j:continue
     z=m.NewBoolVar(k+f'parent{i}_{j}');pp.append(z);m.AddAllowedAssignments([ps[i],ps[j]],ED).OnlyEnforceIf(z);m.Add(depth[i]>depth[j]).OnlyEnforceIf(z)
    m.AddBoolOr(pp)
  if helpers:
   m.Add(helpers['b']['cell']==helpers['c']['cell'])
   m.AddNoOverlap2D(V['space_intervals'],V['time_intervals'])
 if a.stationary_a:
  for i in range(7):
   for z in V['tokens'][f'a{i}']['moves']:m.Add(z==0)
 if a.prep_before_moves:
  for job in V['jobs']:
   if job['k']!='d':
    for stage in job['stage']:m.Add(stage==0)
 if a.fixed_prefix:
  for t,o in zip(V['prefix_t'],selected):m.Add(t==o['asap'])
 if a.hint:
  old=json.loads(Path(a.hint).read_text());index={v.name:v for v in m.Proto().variables}
  # Hint by variable names from a saved model solution.
  for i,v in enumerate(m.Proto().variables):
   if v.name in old.get('variable_values',{}):m.AddHint(m.GetIntVarFromProtoIndex(i),old['variable_values'][v.name])
 if a.geometry:
  geo=json.loads(Path(a.geometry).read_text())
  if 'seed_paths'in geo and not a.hint:
   for key,tok in V['tokens'].items():
    path=geo['seed_paths'][key]
    for j,p in enumerate(tok['pos']):m.AddHint(p,path[min(j,len(path)-1)])
    for j,z in enumerate(tok['moves']):m.AddHint(z,int(j+1<len(path)and path[j]!=path[j+1]))
   for k,perm in V['permutations'].items():
    for i,p in enumerate(perm):m.AddHint(p,i)
   m.AddHint(V['embedding'],0)
 # Lexicographic optimization: first R alone, then exact idle-count proxy at fixed R.
 # A large dominating multiplier avoids rerunning an unproven first-stage optimum.
 exposure=[]
 for key,tok in V['tokens'].items():
  K=len(tok['moves']);total_life=V['R']-tok['init']+3*sum(tok['moves'])
  if key[0]!='d':
   # One reset per segment and each encoder CX incident on a wire consume one tick;
   # one teleport consumes source CX + source measurement + destination reset/CX.
   gates=sum(key[1:] in [str(i)for i in job['indices']]for job in V['jobs']if job['k']==key[0])
   exposure.append(total_life-1-gates-4*sum(tok['moves']))
  # requested secondary cost: number of measured teleports plus coherent hop CX.
  exposure.append((2 if key[0]=='d'else 1)*sum(tok['moves']))
 secondary=sum(exposure);m.Minimize(100000*V['R']+secondary)
 if a.feasible_at:
  m.Add(V['R']==a.feasible_at);m.ClearObjective()
 modelpath=H/(a.out+'.pbtxt');m.ExportToFile(str(modelpath))
 solver=cp_model.CpSolver();solver.parameters.num_workers=a.workers;solver.parameters.max_time_in_seconds=a.seconds;solver.parameters.cp_model_presolve=False;solver.parameters.random_seed=a.seed
 rows=[]
 class Save(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   x=rd.get(self,a,V,pre,dets,emb,enc);x.update(prefix_source=a.prefix,prefix_units=selected,prefix_detectors=dets,template=tpl['id'],secondary_objective=self.Value(secondary),helpers={k:{n:self.Value(v)for n,v in hp.items()}for k,hp in helpers.items()},variable_values={v.name:self.Value(m.GetIntVarFromProtoIndex(i))for i,v in enumerate(m.Proto().variables)})
   stem=H/(a.out+f'_w{len(rows):03d}');stem.with_suffix('.schedule.json').write_text(json.dumps(x,indent=1));row=dict(file=str(stem.with_suffix('.schedule.json')),R=x['R'],secondary=x['secondary_objective'],wall_seconds=self.WallTime(),bound=self.BestObjectiveBound());rows.append(row);print(json.dumps(row),flush=True)
   if a.first:self.StopSearch()
 callback=Save();st=solver.Solve(m,callback)
 out=dict(args=vars(a),status=solver.StatusName(st),stats=solver.ResponseStats(),solutions=rows,model=('connected-region placeholder preparation; exact synthesis and native rescheduling required'if a.abstract_depth else'fixed known encoder graph')+'; complete prefix per-wire dependencies; native state occupancy; coherent data hops; measured block teleports; per-wire move bounds; objective R then exposure',helper_pool='one shared physical cell'if helpers else'none',prefix_embedding_domain=48 if a.geometry else 6,prefix_extraction=prefix['sha256'])
 (H/(a.out+'.receipt.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--prefix',default='v29c');p.add_argument('--template',default='s34c15');p.add_argument('--moves',type=int,default=1);p.add_argument('--data-moves',type=int,default=5);p.add_argument('--max-round',type=int,default=55);p.add_argument('--embedding',type=int,default=-1);p.add_argument('--seconds',type=float,default=900);p.add_argument('--workers',type=int,default=4);p.add_argument('--seed',type=int,default=0);p.add_argument('--stationary-a',action='store_true');p.add_argument('--prep-before-moves',action='store_true');p.add_argument('--fixed-prefix',action='store_true');p.add_argument('--first',action='store_true');p.add_argument('--hint');p.add_argument('--geometry');p.add_argument('--feasible-at',type=int);p.add_argument('--abstract-depth',type=int,default=0);p.add_argument('--helpers',action='store_true');run(p.parse_args())
