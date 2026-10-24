"""Whole-circuit exact-priced endpoint neighbourhood of a verified new C4 design."""
from common import *
import c4_design as C,argparse,gzip
from types import SimpleNamespace
p=argparse.ArgumentParser();p.add_argument('--source',default='work/lanes/ST1/c4_path_earlyA_fixed_w26.solver.json');p.add_argument('--out',required=True);p.add_argument('--changed-b',type=int,default=1);p.add_argument('--freeze-a-initial',action='store_true');p.add_argument('--check-moves',type=int,default=4);p.add_argument('--seconds',type=float,default=600);p.add_argument('--workers',type=int,default=8);p.add_argument('--seed',type=int,default=0);opt=p.parse_args();old=json.loads(Path(opt.source).read_text());args=dict(old['args']);args.update(out=opt.out,world_fixed=True,sync_round=False,b_catalog=None,b_endpoints=False,b_moves=2,external_b=False,stationary_b=False,free_prefix=False,early_a=True,final_window=-1,tail_objective=True,fixed_prefix=True,presolve=True,recycle_readouts=True,data_auto=True,moves=2,check_moves=opt.check_moves,move_budget=90,max_round=70,workers=opt.workers,seconds=opt.seconds,seed=opt.seed);a=SimpleNamespace(**args);m,v,enc=C.create(a);m.Add(v['em']==old['embedding']);changed=[]
for i in range(7):
 tok=v['T']['b'+str(i)];orig=old['tokens']['b'+str(i)];m.Add(tok['pos'][0]==orig['pos'][0]);z=m.NewBoolVar('changed_b'+str(i));m.Add(tok['pos'][-1]!=orig['pos'][-1]).OnlyEnforceIf(z);m.Add(tok['pos'][-1]==orig['pos'][-1]).OnlyEnforceIf(z.Not());changed.append(z)
 if opt.freeze_a_initial:m.Add(v['T']['a'+str(i)]['pos'][0]==old['tokens']['a'+str(i)]['pos'][0])
m.Add(sum(changed)<=opt.changed_b);hint={}
def h(var,val):hint[var.Index()]=int(val)
h(v['R'],old['R']);h(v['em'],old['embedding'])
for q,z in v['mp'].items():h(z,old['mapping'][str(q)])
for z,t in zip(v['pt'],old['prefix_t']):h(z,t)
for vs,zs in zip(v['pl'],old['prefix_locs']):
 for z,t in zip(vs,zs):h(z,t)
for k,tok in v['T'].items():
 for n,z in tok.items():
  if isinstance(z,list):
   vals=old['tokens'][k][n]
   for j,q in enumerate(z):
    value=vals[j]if j<len(vals)else 0 if n=='moves'else vals[-1]
    if n=='ts'and j>=len(vals):value=vals[-1]+(2 if k[0]=='d'else 1)*old['tokens'][k]['moves'][-1]
    h(q,value)
  else:h(z,old['tokens'][k][n])
for key,oldkey in [('P','permutations'),('E','endpoints')]:
 for k,vs in v[key].items():
  for z,t in zip(vs,old[oldkey][k]):h(z,t)
for key,oldkey in [('endb','endb'),('endc','endc'),('enda','enda'),('dp','data_permutation')]:
 for z,t in zip(v[key],old[oldkey]):h(z,t)
for j,o in zip(v['jobs'],old['jobs']):
 assert j['k']==o['k']and j['indices']==o['indices']
 h(j['t'],o['t'])
 for k in('loc','stage'):
  for z,t in zip(j[k],o[k]):h(z,t)
for j,o in zip(v['checks'],old['checks']):
 for k in('t','stage','loc'):h(j[k],o[k])
for z in changed:h(z,0)
for i,t in hint.items():m.AddHint(m.GetIntVarFromProtoIndex(i),t)
assert not m.Validate(),m.Validate();ctl=cp_model.CpSolver();ctl.parameters.num_workers=1;ctl.parameters.max_time_in_seconds=15;ctl.parameters.fix_variables_to_their_hinted_value=True;st=ctl.Solve(m);control=dict(status=ctl.StatusName(st),stats=ctl.ResponseStats());print('CONTROL',json.dumps(control),flush=True);assert st in(cp_model.OPTIMAL,cp_model.FEASIBLE),control
control_stem=C.build(C.extract(ctl,a,v,enc),opt.out+'_control');source_qasm=Path(str(opt.source).removesuffix('.solver.json')+'.qasm');assert control_stem.with_suffix('.qasm').read_bytes()==source_qasm.read_bytes(),'control emission changed'
append_result(opt.out+':control',dict(passed=True,sha256=hashlib.sha256(source_qasm.read_bytes()).hexdigest()),'Fixed-hint model control reproduces the verified source QASM byte-for-byte before structural search.')
path=H/(opt.out+'.model.pbtxt');m.ExportToFile(str(path))
with gzip.open(path.with_suffix('.pbtxt.gz'),'wb')as z:z.write(path.read_bytes())
path.unlink();s=cp_model.CpSolver();s.parameters.num_workers=opt.workers;s.parameters.max_time_in_seconds=opt.seconds;s.parameters.cp_model_presolve=True;s.parameters.random_seed=opt.seed;count=0
class CB(cp_model.CpSolverSolutionCallback):
 def on_solution_callback(self):
  global count
  x=C.extract(self,a,v,enc);name=opt.out+f'_w{count}';count+=1;(H/(name+'.solver.json')).write_text(json.dumps(x,indent=1));row=dict(name=name,R=x['R'],changed_b=[i for i,z in enumerate(changed)if self.Value(z)],objective=self.ObjectiveValue())
  try:stem=C.build(x,name);row.update(score(stem))
  except Exception as e:row['error']=repr(e)
  with gzip.open(H/(opt.out+'.witnesses.jsonl.gz'),'at')as z:z.write(json.dumps(dict(result=row,plan=x))+'\n')
  append_result(name,row,'C4 whole-circuit endpoint neighbourhood; native B initial path and prefix embedding fixed to a verified control, B endpoints/checker routes/A-data contacts jointly resynthesized.');print(json.dumps(row),flush=True)
  if row.get('total',1)<6.505e-5 and row.get('exp_minus_A1',0)>=.5002:self.StopSearch()
st=s.Solve(m,CB());r=dict(status=s.StatusName(st),stats=s.ResponseStats(),witnesses=count,control=control,args=vars(opt));(H/(opt.out+'.receipt.json')).write_text(json.dumps(r,indent=2));append_result(opt.out,r,'Completed exact-priced C4 endpoint neighbourhood; UNKNOWN/interrupted searches are not global bounds.');print(json.dumps(r),flush=True)
