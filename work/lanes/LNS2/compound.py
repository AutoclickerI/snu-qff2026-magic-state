"""Combine independently measured improving moves, then recheck their interaction."""
from moves import *
import argparse,itertools

def key(u):return tuple(u.lines[:2]if u.name=='MX'else u.lines)
def locate(c,orig,i):
 k=key(orig['u'][i]);occ=sum(key(u)==k for u in orig['u'][:i]);found=[j for j,u in enumerate(c['u'])if key(u)==k]
 if len(found)<=occ:raise ValueError('operation replaced by another compound edit')
 return found[occ]
def apply(c,orig,d):
 c=clone(c);mv=d['move']
 if mv=='single':
  i=locate(c,orig,d['unit']);c['t'][i]+=d['new']-d['old'];c=retime(c)
 elif mv=='swap':
  i,j=[locate(c,orig,k)for k in d['units']];c['u'][i],c['u'][j]=c['u'][j],c['u'][i];c=retime(c)
 elif mv in ('reset_to_measure','check_rx','watch_before_reset'):
  i=locate(c,orig,d['unit']);q=c['u'][i].qs[0];b=bit(c);t=c['t'][i]
  if mv=='reset_to_measure':c['u'][i]=Unit([f'measure q[{q}] -> c[{b}];'])
  elif mv=='check_rx':c['u'].insert(i+1,Unit([f'h q[{q}];',f'measure q[{q}] -> c[{b}];',f'h q[{q}];']));c['t'].insert(i+1,t+1)
  else:
   lines=[f'measure q[{q}] -> c[{b}];']
   if d['axis']=='X':lines=[f'h q[{q}];']+lines
   c['u'].insert(i,Unit(lines));c['t'].insert(i,t-1)
  adddet(c,b);c=retime(c)
 elif mv=='add_edge':c=next(x for x,dd in readout_moves(c)if dd['move']=='add_edge'and dd['edge']==d['edge'])
 else:raise ValueError(mv)
 if c is None:raise ValueError('retime infeasible')
 return normalize(c)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('trace');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--label',default='compound');ap.add_argument('--target');a=ap.parse_args()
 rows=[json.loads(l)for l in Path(a.trace).read_text().splitlines()];orig=read(rows[0]['desc']['source']);base=read(a.target)if a.target else orig;parent=base['meta']['lns_result']['total']
 good=sorted([r for r in rows if 'total'in r and r['total']<r['desc'].get('parent_total',0)-1e-10 and r['desc']['move']in('single','swap','reset_to_measure','check_rx','watch_before_reset','add_edge')and r['exp_minus_A1']>.51],key=lambda x:x['total'])
 selected=[];seen=set()
 for r in good:
  d=r['desc'];k=(d['move'],d.get('unit'),str(d.get('units')),str(d.get('edge')))
  if k in seen:continue
  seen.add(k);selected.append(d)
  if len(selected)>=14:break
 subsets=[tuple(range(n))for n in range(2,len(selected)+1)]+list(itertools.combinations(range(min(10,len(selected))),2));cands=[]
 for sub in subsets:
  c=clone(base)
  try:
   for j in sub:c=apply(c,orig,selected[j])
  except (ValueError,AssertionError,StopIteration):continue
  cands.append((c,dict(family='triple',move='combine_verified',moves=[selected[j]for j in sub],parent_total=parent,local_track=bool(a.target))))
 batch(cands,a.label,a.workers)
