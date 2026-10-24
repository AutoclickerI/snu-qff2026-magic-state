"""Compose exact physical deltas, then fully reprice; no assumed gain additivity."""
from funding import *
def delta(source):
 a=base();b=json.loads((V/(source+'.plan.json')).read_text());aa=collections.Counter((o['t'],tuple(o['lines']))for o in a['ops']);bb=collections.Counter((o['t'],tuple(o['lines']))for o in b['ops'])
 return dict(remove=[dict(t=t,lines=list(ls))for t,ls in(aa-bb).elements()],add=[dict(t=t,lines=list(ls))for t,ls in(bb-aa).elements()],detector_remove=sorted(set(a['tail'])-set(b['tail'])),detector_add=sorted(set(b['tail'])-set(a['tail'])))
def compose(c,source):
 d=delta(source);c=copy.deepcopy(c);basebits={int(x)for o in base()['ops']for x in re.findall(r'c\[(\d+)\]',' '.join(o['lines']))};newbits=sorted({int(x)for o in d['add']for x in re.findall(r'-> c\[(\d+)\]',' '.join(o['lines']))}-basebits);mp={x:bit(c)+i for i,x in enumerate(newbits)};remap=lambda l:re.sub(r'c\[(\d+)\]',lambda m:f'c[{mp.get(int(m[1]),int(m[1]))}]',l)
 for r in d['remove']:
  found=[o for o in c['ops']if o['t']==r['t']and o['lines']==r['lines']]
  if found:c['ops'].remove(found[0])
  else:
   # Repeated pure removal is idempotent; replacing an already changed
   # operation requires a new explicit recipe, not a silent fallback.
   bits=set(map(int,re.findall(r'c\[(\d+)\]',' '.join(r['lines']))));qs=set(unit(r).qs)
   assert not any(qs&set(unit(o).qs)and o['t']==r['t']for o in d['add']),('conflicting replacement',source,r)
 for line in d['detector_remove']:
  if line in c['tail']:c['tail'].remove(line)
 for r in d['add']:
  lines=[remap(l)for l in r['lines']]
  if any(o['t']==r['t']and o['lines']==lines for o in c['ops']):continue
  c['ops'].append(dict(t=r['t'],lines=lines,tag='integration',id=10000+len(c['ops'])))
 for line in d['detector_add']:
  line=remap(line)
  if line not in c['tail']:c['tail'].append(line)
 c['meta']['composed']=c['meta'].get('composed',[])+[source];return fix(c)
def eval_plan(c):
 c,txt=normalized(c);ev=exact2.Eval(txt,c['meta']['data_qubits']);r=wide_moments.evaluate(ev);return c,r
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--seed',default='fund_full');p.add_argument('--width',type=int,default=12);p.add_argument('--rounds',type=int,default=5);a=p.parse_args();seed=json.loads((V/(a.seed+'.plan.json')).read_text());br=json.loads((V/'base.screen.json').read_text());wr=json.loads((V/'wait_builds.json').read_text());choices=[]
 for r in wr:
  if'screen'not in r:continue
  z=r['screen']
  if z.get('invalid_cubic'):continue
  # Proposal heuristic only: retain single-screen gains and budget suppliers.
  # Nonadditivity means discarded singles are not globally refuted; the
  # later integration sweep reevaluates all menu entries on the winner.
  if z['total']<br['total']-1e-10 or(z['exp_minus_A1']>br['exp_minus_A1']+.0005 and z['total']<br['total']+3e-7):choices.append(r['stem'])
 choices+=['c_exchange_0','st2_15','st2_both']
 seed,z=eval_plan(seed);beam=[dict(c=seed,r=z,chosen=[])];history=[];seen=set()
 for k in range(a.rounds):
  trials=[]
  for parent in beam:
   for name in choices:
    if name in parent['chosen']:continue
    chosen=tuple(sorted(parent['chosen']+[name]))
    if chosen in seen:continue
    seen.add(chosen)
    try:c,r=eval_plan(compose(parent['c'],name))
    except Exception:continue
    if r['exp_minus_A1']<.4999:continue
    trials.append(dict(c=c,r=r,chosen=list(chosen)))
  if not trials:break
  # Keep a loss/acceptance Pareto set plus the best loss candidates.
  trials.sort(key=lambda x:x['r']['total']);front=[];maxacc=-1
  for t in trials:
   if t['r']['exp_minus_A1']>maxacc:front.append(t);maxacc=t['r']['exp_minus_A1']
  selected=trials[:max(1,a.width//2)]+front[:max(1,a.width//2)];unique={tuple(x['chosen']):x for x in selected};beam=list(unique.values())[:a.width]
  for j,t in enumerate(beam):
   n=f'knap_{k}_{j}';st,r=write(t['c'],n,dict(family='acceptance_knapsack',seed=a.seed,chosen=t['chosen'],beam_width=a.width));history.append(dict(stem=n,round=k,chosen=t['chosen'],screen=r))
  (V/'knapsack_builds.json').write_text(json.dumps(history,indent=2));print('round',k,'valid trials',len(trials),'best',trials[0]['r']['total'],flush=True)
