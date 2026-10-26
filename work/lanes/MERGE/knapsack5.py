"""Compatible buyer knapsack proposes circuits; all decisions use whole-circuit exact prices."""
from pass5 import *
from wide5 import buyer,frontier
from ortools.sat.python import cp_model

def run():
 hist=json.loads((R/'wide_history.json').read_text());cur=hist[-1]['price'];assert sha(cur['stem'])=='d797a23dd127e1479fa2388b1c07f3c851e59ce06dc2fba95acedca26b1eaf6e'
 E.configure(R/('basis_'+cur['sha256']+'.json'),12);base=M.read(cur['stem']);es=json.loads((R/'wide_r3_menu.json').read_text())
 flip=M.mk(fam='rev',a=25,b=24,t=37);es[flip['id']]=flip
 f=next(r for r in json.loads((R/'global_pilot_outcome.json').read_text())if r['pilot']=='current')
 allrows=[json.loads(l)for l in (R/'wide_r3_singles.jsonl').read_text().splitlines()]
 candidates=sorted([r for r in allrows if buyer(r,cur)],key=lambda r:r['loss']);buyers=[];seen=set();rejected=[]
 for r in candidates:
  if r['sha256']in seen:continue
  seen.add(r['sha256']);i=r['edits'][0]
  try:apply(base,[flip,es[i]])
  except Exception as ex:rejected.append(dict(id=i,invalid=repr(ex)));continue
  buyers.append(r)
 ids=[r['edits'][0]for r in buyers];conflicts=[]
 for i,j in itertools.combinations(range(len(ids)),2):
  try:apply(base,[flip,es[ids[i]],es[ids[j]]])
  except Exception as ex:conflicts.append(dict(i=i,j=j,invalid=repr(ex)))
 aa=[round((r['acceptance']-cur['acceptance'])*1e9)for r in buyers];ll=[round((r['loss']-cur['loss'])*1e14)for r in buyers]
 # The linear model is only a proposal heuristic; a small headroom covers typical cross terms.
 need=round((FLOOR+0.0001-f['acceptance'])*1e9);tasks=set();models=[]
 for cap in range(1,len(ids)+1):
  model=cp_model.CpModel();xs=[model.new_bool_var('x'+str(i))for i in range(len(ids))]
  model.add(sum(xs)<=cap);model.add(sum(a*x for a,x in zip(aa,xs))>=need)
  for pair in conflicts:model.add(xs[pair['i']]+xs[pair['j']]<=1)
  model.minimize(sum(l*x for l,x in zip(ll,xs)));solver=cp_model.CpSolver();solver.parameters.num_search_workers=1
  for k in range(2):
   status=solver.solve(model)
   if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):models.append(dict(cap=cap,rank=k,status=solver.status_name(status)));break
   assignment=[solver.value(x)for x in xs];chosen=[ids[i]for i,x in enumerate(assignment)if x];task=tuple(sorted([flip['id']]+chosen));tasks.add(task)
   models.append(dict(cap=cap,rank=k,status=solver.status_name(status),edits=task,linear_loss=f['loss']+sum(v*l for v,l in zip(assignment,ll))/1e14,linear_acceptance=f['acceptance']+sum(v*a for v,a in zip(assignment,aa))/1e9))
   model.add_forbidden_assignments(xs,[assignment])
 p=R/'global_knapsack_menu.json';dump(p,es);dump(R/'global_knapsack_model.json',dict(base=cur,flip=f,buyers=buyers,rejected=rejected,conflicts=conflicts,models=models,acceptance_margin=.0001,policy='two best compatible linear proposals per cardinality; exact full prices decide'))
 tasks=sorted(tasks,key=lambda x:(len(x),x));dump(R/'global_knapsack_tasks.json',tasks);out=R/'global_knapsack.jsonl';done={tuple(r['edits']):r for r in map(json.loads,out.read_text().splitlines())}if out.exists()else{}
 init(cur['stem'],p,cur['loss']);rows=[]
 print(json.dumps(dict(event='global_knapsack_proposals',buyers=len(buyers),conflicts=len(conflicts),proposals=len(tasks))),flush=True)
 with out.open('a')as stream:
  for k,task in enumerate(tasks,1):
   if task in done:r=done[task]
   else:r=job(task);r['stage']='global_knapsack';stream.write(json.dumps(r)+'\n');stream.flush()
   rows.append(r)
   if feasible(r)and r['loss']<TAU-3e-8:publish(r)
   print(json.dumps(dict(event='global_knapsack_price',done=k,total=len(tasks),loss=r.get('loss'),A=r.get('acceptance'),error=r.get('error',r.get('invalid')))),flush=True)
 best=choose(rows,cur);dump(R/'global_knapsack_outcome.json',dict(base=cur,price=best,gain=cur['loss']-best['loss'],pareto=frontier(rows+[cur]),proposals=len(tasks)))
 print(json.dumps(dict(event='global_knapsack_complete',loss=best['loss'],A=best['acceptance'],gain=cur['loss']-best['loss'])),flush=True)
if __name__=='__main__':run()
