"""Complete fresh-prefix designs with the audited 9-CX B/two-check package."""
from common import *
import c4_design as C,argparse,gzip
from types import SimpleNamespace
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--prefix-variant',default='cats13');p.add_argument('--free-prefix',action='store_true');p.add_argument('--fixed-prefix',action='store_true');p.add_argument('--encoder-a',default='s34c15');p.add_argument('--moves',type=int,default=3);p.add_argument('--data-moves',type=int,default=5);p.add_argument('--max-round',type=int,default=55);p.add_argument('--placement',type=int,default=-1);p.add_argument('--seconds',type=float,default=600);p.add_argument('--workers',type=int,default=8);p.add_argument('--seed',type=int,default=0);opt=p.parse_args();package=json.loads((H/'two_check_package.json').read_text());C.CHECKS=package['check_rows'];a=SimpleNamespace(out=opt.out,prefix_variant=opt.prefix_variant,free_prefix=opt.free_prefix,fixed_prefix=opt.fixed_prefix,encoder=opt.encoder_a+',stwo9',stationary_prep=True,stationary_a=False,stationary_b=False,recycle_readouts=True,data_auto=True,b_catalog=None,world_fixed=True,b_endpoints=False,b_moves=1,external_b=False,sync_round=True,early_a=False,final_window=-1,tail_objective=False,presolve=True,moves=opt.moves,data_moves=opt.data_moves,check_moves=1,move_budget=90,max_round=opt.max_round,workers=opt.workers,seconds=opt.seconds,seed=opt.seed)
m,v,enc=C.create(a);cells=sorted(set(package['initial_b']+package['final_b']+package['checker_cells']));embs=[e for e in C.rd.mappings(cells)if e['sym']==0];pid=m.NewIntVar(0,len(embs)-1,'package_placement');rows=[]
for j,e in enumerate(embs):
 mp=dict(zip(cells,e['cells']));rows.append([j]+[mp[q]for q in package['initial_b']]+[mp[q]for q in package['final_b']]+[mp[q]for q in package['checker_cells']])
m.AddAllowedAssignments([pid]+[v['T']['b'+str(i)]['pos'][0]for i in range(7)]+[v['T']['b'+str(i)]['pos'][-1]for i in range(7)]+[v['T']['c'+str(i)]['pos'][0]for i in range(2)],rows)
if opt.placement>=0:m.Add(pid==opt.placement)
for i in range(7):m.Add(v['P']['b'][i]==i)
for i in range(2):
 for z in v['T']['c'+str(i)]['moves']:m.Add(z==0)
assert not m.Validate(),m.Validate();path=H/(opt.out+'.model.pbtxt');m.ExportToFile(str(path))
with gzip.open(path.with_suffix('.pbtxt.gz'),'wb')as z:z.write(path.read_bytes())
path.unlink();s=cp_model.CpSolver();s.parameters.num_workers=opt.workers;s.parameters.max_time_in_seconds=opt.seconds;s.parameters.cp_model_presolve=True;s.parameters.random_seed=opt.seed;count=0
class CB(cp_model.CpSolverSolutionCallback):
 def on_solution_callback(self):
  global count
  x=C.extract(self,a,v,enc);x['package_placement']=self.Value(pid);name=opt.out+f'_w{count}';count+=1;(H/(name+'.solver.json')).write_text(json.dumps(x,indent=1));row=dict(name=name,R=x['R'],placement=x['package_placement'],objective=self.ObjectiveValue())
  try:stem=C.build(x,name);row.update(score(stem))
  except Exception as e:row['error']=repr(e)
  with gzip.open(H/(opt.out+'.witnesses.jsonl.gz'),'at')as z:z.write(json.dumps(dict(result=row,plan=x))+'\n')
  append_result(name,row,'Complete synchronous A/B round with 9-CX B preparation, two native one-CX transfers, and two four-body Z parity checks; full exact first-order/cubic screening.');print(json.dumps(row),flush=True)
  if row.get('total',1)<6.505e-5 and row.get('exp_minus_A1',0)>=.5002:self.StopSearch()
st=s.Solve(m,CB());r=dict(status=s.StatusName(st),stats=s.ResponseStats(),witnesses=count,args=vars(opt),placements=len(embs));(H/(opt.out+'.receipt.json')).write_text(json.dumps(r,indent=2));append_result(opt.out,r,'Two-check verifier spacetime search; unchanged complete-circuit gates apply, UNKNOWN is not infeasibility.');print(json.dumps(r),flush=True)
