from common import *
from guards import apply
from ortools.sat.python import cp_model
import math,itertools

def compatible(base,actions):
 try:
  for a,b in itertools.combinations(actions,2):
   if a['type']=='echo'and b['type']=='echo'and a['h']==b['h']:
    lo_a=a.get('prior_time',a['init']) if a.get('reuse') else a['init']
    lo_b=b.get('prior_time',b['init']) if b.get('reuse') else b['init']
    if max(lo_a,lo_b)<=min(a['measure'],b['measure']):return False
  p=apply(base,actions);slots=[(o['t'],q)for o in p['ops']for q in o['qs']]
  return len(slots)==len(set(slots))
 except AssertionError:return False

def run(base_name='control_R38'):
 base=load(H/base_name);ref=json.loads((H/(base_name+'.allorders.json')).read_text());actions=json.loads((H/(base_name+'.actions.json')).read_text());rows=[]
 for a in actions:
  f=H/(base_name+'_'+a['id']+'.price.json')
  if not f.exists():continue
  r=json.loads(f.read_text())
  if r.get('ok')and r['loss']<ref['loss']-1e-10:
   rows.append(dict(action=a,gain=ref['loss']-r['loss'],cost=-math.log(r['acceptance']/ref['acceptance']),price=r))
 conflicts=[(i,j)for i in range(len(rows))for j in range(i)if not compatible(base,[rows[i]['action'],rows[j]['action']])];out=[];seen=set()
 for frac in (.2,.4,.6,.8,1.,1.1):
  m=cp_model.CpModel();x=[m.NewBoolVar(f'x{i}')for i in range(len(rows))]
  for i,j in conflicts:m.Add(x[i]+x[j]<=1)
  cap=-math.log(.5005/ref['acceptance'])*frac;m.Add(sum(round(r['cost']*1e9)*v for r,v in zip(rows,x))<=round(cap*1e9));m.Maximize(sum(round(r['gain']*1e13)*v for r,v in zip(rows,x)))
  s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.cp_model_presolve=False;s.parameters.max_time_in_seconds=15;st=s.Solve(m)
  if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):continue
  inds=tuple(i for i,v in enumerate(x)if s.Value(v))
  if inds in seen:continue
  seen.add(inds);aa=[rows[i]['action']for i in inds];assert compatible(base,aa);p=apply(base,aa);p['meta']['knapsack_proposal']=dict(fraction=frac,status=s.StatusName(st),linear_gain=sum(rows[i]['gain']for i in inds),linear_log_acceptance_cost=sum(rows[i]['cost']for i in inds),actual_evaluation_required=True)
  name=base_name+f'_pack{len(out):02d}';save(p,name);out.append(name)
 (H/(base_name+'.positive_marginals.json')).write_text(json.dumps(rows,indent=2));(H/(base_name+'.knapsack_queue.json')).write_text(json.dumps(out));print(base_name,'positive',len(rows),'conflicts',len(conflicts),'proposals',out,flush=True)
if __name__=='__main__':run(*sys.argv[1:])
