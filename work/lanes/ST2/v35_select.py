"""Joint guard/echo/initialization knapsack; all complete choices repriced exactly."""
import sys,json,math,itertools,copy,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import v35_campaign as v,knapsack_select as k
from ortools.sat.python import cp_model

def rows():
 base=v.C.read(v.V/'base');out=[];seen=set()
 ledger=json.loads((v.V/'base.detector_prices.json').read_text())
 od=v.V/'detector_only';od.mkdir(exist_ok=True)
 for rr in ledger['detector_rows']:
  c=v.C.clone(base);c['tail'].pop(rr['row']);st=od/f'det_{rr["row"]:02}';v.d.save(c,st)
  r=dict(rr,stem=str(st.relative_to(v.H)),ok=True,description=dict(family='detector_only',row=rr['row'],detector=rr['detector']))
  st.with_suffix('.score.json').write_text(json.dumps(r,indent=2));out.append(r)
 for label in ('fasttrack','physical','additions'):
  for p in sorted((v.V/label).glob('*.score.json')):out.append(json.loads(p.read_text()))
 for r in out:
  if not r.get('ok')or 'loss'not in r:continue
  c=v.C.read(v.H/r['stem']);fp=v.d.digest(c)
  if fp in seen:continue
  seen.add(fp);r['delta_loss']=r['loss']-ledger['base_loss'];r['acceptance_recovered']=r['acceptance']-ledger['base_acceptance']
  yield r,c

def options():
 base=v.C.read(v.V/'base');opts=[]
 available=list(rows())
 for r,c in available:
  if r['description']['family']=='known_measurement':
   alts=[s for s,_ in available if s['description'].get('family')=='known_measurement' and s['description'].get('bit')==r['description']['bit'] and s['stem']!=r['stem']]
   if any(s['loss']<=r['loss']+1e-14 and s['acceptance']>=r['acceptance']-1e-10 and (s['loss']<r['loss']-1e-14 or s['acceptance']>r['acceptance']+1e-10 or s['description']['form']=='omit')for s in alts):continue
  if r['delta_loss']>3e-6 or (r['acceptance_recovered']<1e-7 and r['delta_loss']>=-1e-13):continue
  # Microscopic detector-only savings create thousands of nearly identical
  # integer optima. Keep their prices, but allocate with physical elements.
  if r['description']['family']=='detector_only' and r['acceptance_recovered']<1e-4:continue
  # Each optional check receives a distinct new record before patches combine.
  newbits=sorted({b for u in c['u']for b in v.a.bits(' '.join(u.lines))if b>=278});mapping={b:300+len(opts)*4+j for j,b in enumerate(newbits)}
  def rewrite(s):return re.sub(r'c\[(\d+)\]',lambda m:f'c[{mapping.get(int(m[1]),int(m[1]))}]',s)
  c['u']=[v.C.Unit([rewrite(s)for s in u.lines])for u in c['u']];c['tail']=[rewrite(s)for s in c['tail']]
  p=k.patches(base,c);opts.append((r,p))
 return base,opts

def incompatible(p,q):
 if k.conflict(p,q):return True
 def deleted_records(p):
  removed={b for _,ls in p['remove']for line in ls if '->'in line for b in v.a.bits(line)}
  added={b for _,ls in p['add']for line in ls if '->'in line for b in v.a.bits(line)}
  return removed-added
 if deleted_records(p)&{b for line in q['add_tail']for b in v.a.bits(line)}:return True
 if deleted_records(q)&{b for line in p['add_tail']for b in v.a.bits(line)}:return True
 # Two distinct optional instruments cannot occupy one native qubit slot.
 def slots(p):return {(t,z)for t,ls in p['add']for z in v.C.Unit(list(ls)).qs}
 return bool(slots(p)&slots(q))

def proposals(n=28):
 base,opts=options();a0=json.loads((v.V/'base.detector_prices.json').read_text())['base_acceptance'];l0=v.a.BASE_LOSS
 m=cp_model.CpModel();xs=[m.NewBoolVar(f'x{i}')for i in range(len(opts))]
 for i,(_,p)in enumerate(opts):
  for j,(_,q)in enumerate(opts[:i]):
   if incompatible(p,q):m.Add(xs[i]+xs[j]<=1)
 costs=[round(math.log(r['acceptance']/a0)*1e11)for r,p in opts];gains=[round(r['delta_loss']*1e16)for r,p in opts]
 m.Add(sum(x*c for x,c in zip(xs,costs))>=round(math.log(.5005/a0)*1e11));m.Minimize(sum(x*g for x,g in zip(xs,gains)))
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=20
 print('OPTIONS',len(opts),flush=True)
 for rank in range(n):
  st=s.Solve(m)
  if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):break
  ix=[i for i,x in enumerate(xs)if s.Value(x)]
  # Require distinct physical bundles, while retaining the exact best first.
  m.Add(sum(xs[i]if i in ix else 1-xs[i]for i in range(len(xs)))<=len(xs)-3)
  try:c=k.apply(base,[opts[i][1]for i in ix])
  except Exception as e:print('COMBINATION_REJECT',rank,repr(e),flush=True);continue
  yield f'choice_{rank:03}',c,dict(family='joint_knapsack',selected=[opts[i][0]['stem']for i in ix],predicted_loss=l0+sum(opts[i][0]['delta_loss']for i in ix),predicted_acceptance=a0*math.exp(sum(costs[i]for i in ix)/1e11),budget_screen=True)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=5);p.add_argument('--count',type=int,default=28);p.add_argument('--label',default='selected');args=p.parse_args()
 v.a.batch(proposals(args.count),args.label,args.workers)
