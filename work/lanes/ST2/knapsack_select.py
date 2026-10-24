"""Solve marginal acceptance knapsacks; reprice complete interacting circuits."""
import sys,json,math,collections,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a
from ortools.sat.python import cp_model

def patches(base,c):
 k=lambda u,t:(t,tuple(u.lines))
 bs={k(u,t)for u,t in zip(base['u'],base['t'])};cs={k(u,t)for u,t in zip(c['u'],c['t'])}
 return dict(remove=bs-cs,add=cs-bs,remove_tail=set(base['tail'])-set(c['tail']),add_tail=set(c['tail'])-set(base['tail']))
def apply(base,ps):
 c=a.C.clone(base)
 for p in ps:
  ks={(t,tuple(u.lines)):i for i,(u,t)in enumerate(zip(c['u'],c['t']))};assert all(k in ks for k in p['remove'])
  a.remove_units(c,{ks[k]for k in p['remove']});c['tail']=[s for s in c['tail']if s not in p['remove_tail']]
  for t,ls in sorted(p['add']):c['u'].append(a.C.Unit(list(ls)));c['t'].append(t)
  c['tail'].extend(sorted(p['add_tail']-set(c['tail'])))
 return a.d.normalize(c)
def conflict(p,q):
 return bool(p['remove']&q['remove'] or p['remove_tail']&q['remove_tail'] or p['add']&q['add'])

def proposals():
 base=a.d.normalize(a.C.read(a.OUT/'base'));rr=json.loads((a.OUT/'prices/results.json').read_text())['rows'];opts=[]
 for r in rr:
  if not r.get('ok') or abs(r.get('c1',0))>1e-12 or r['acceptance_recovered']<1e-6 or r['delta_loss']>2e-6:continue
  c=a.C.read(a.H/r['stem']);p=patches(base,c);opts.append((r,p))
 yield 'base',base,dict(family='base')
 for budget in [0,.0005,.001,.002,.004,.006,.008,.012,.016,.02,.03,.04]:
  m=cp_model.CpModel();xs=[m.NewBoolVar(f'x{i}')for i in range(len(opts))]
  for i,(_,p)in enumerate(opts):
   for j,(_,q)in enumerate(opts[:i]):
    if conflict(p,q):m.Add(xs[i]+xs[j]<=1)
  # Additive log-acceptance is a proposal model only. Every selected complete
  # circuit is re-evaluated with all interacting fault orders.
  cost=[round(math.log(r['acceptance']/a.BASE_ACC)*1e9)for r,p in opts]
  gain=[round((r['delta_loss']if abs(r['delta_loss'])>1e-13 else 0)*1e14)for r,p in opts]
  m.Add(sum(x*k for x,k in zip(xs,cost))>=round(math.log((a.BASE_ACC+budget)/a.BASE_ACC)*1e9));m.Minimize(sum(x*k for x,k in zip(xs,gain)))
  s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=3;st=s.Solve(m)
  if st not in(cp_model.FEASIBLE,cp_model.OPTIMAL):continue
  ix=[i for i,x in enumerate(xs)if s.Value(x)];c=apply(base,[opts[i][1]for i in ix]);desc=dict(family='marginal_knapsack',budget=budget,selected=[opts[i][0]['stem']for i in ix],predicted_loss=a.BASE_LOSS+sum(opts[i][0]['delta_loss']for i in ix),predicted_acceptance=a.BASE_ACC*math.exp(sum(cost[i]for i in ix)/1e9))
  yield f'budget_{int(budget*1e5):04}',c,desc
 # Explicit near-zero-cost removals make the acceptance/loss frontier reviewable.
 cheap=sorted(opts,key=lambda z:z[0]['delta_loss']/z[0]['acceptance_recovered']);picked=[]
 for r,p in cheap:
  if r['delta_loss']>2e-8 or any(conflict(p,q)for _,q in picked):continue
  picked.append((r,p));c=apply(base,[q for _,q in picked]);yield f'cheap_{len(picked):02}',c,dict(family='cheap_removal_stack',selected=[r['stem']for r,q in picked])
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=14);args=p.parse_args();a.batch(proposals(),'selected',args.workers)
