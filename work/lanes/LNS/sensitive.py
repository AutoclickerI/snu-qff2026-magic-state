"""CP-SAT large timing neighborhoods using exact pair-loss derivatives."""
from core import *
import random,argparse

def proposals(base):
 ev=exact2.Eval(textof(base),D);sy=setup_syndromes(ev);pairs=[(a,b)for a in range(len(sy))for b in range(a,len(sy))if sy[a]==sy[b]]
 exact2.G.update(ev=ev,third=True,SA=float(ev.fp@ev.a_single),Pch=np.bincount(ev.fch,weights=ev.fp),pairs=pairs)
 p2,aa,sens,big,bc=exact2._pair_chunk((0,len(pairs),1e-15));n=len(base['u']);grad=np.zeros(n)
 byq={}
 for i,u in enumerate(base['u']):
  for q in u.qs:byq.setdefault(q,[]).append(i)
 for ch,v in zip(ev.m.chans,sens):
  if ch['gap']is None:continue
  q,first,length=ch['gap'];seq=byq[q];left=[i for i in seq if base['t'][i]<first];right=[i for i in seq if base['t'][i]>first+length-1]
  if not left or not right:continue
  a,b=left[-1],right[0];w=v/ch['prob']*.001*(1-4*.001/3)**length;grad[a]-=w;grad[b]+=w
 pred,succ=S.build_dag(base['u']);rng=random.Random(774)
 # Frozen or relaxed horizons, all units in the neighborhood, plus smaller
 # random subsets. Third-order exact screening decides every kept schedule.
 for radius in [1,2,4,8]:
  for mode in ['all','A','BC','pre','hop']:
   for penalty in [0,.03,.1,.3]:
    c=clone(base);m=cp_model.CpModel();tv=[];movable=[]
    for i,(u,t)in enumerate(zip(c['u'],c['t'])):
     active=mode=='all'or(mode=='A'and set(u.qs)<=set(A))or(mode=='BC'and set(u.qs)<=set(B+C))or(mode=='pre'and t<30)or(mode=='hop'and 28<=t<45 and bool(set(u.qs)&set(D)))
     lo=max(0,t-radius)if active else t;hi=t+radius if active else t;tv.append(m.new_int_var(lo,hi,f't{i}'));movable.append(active)
    for i in range(n):
     for j in pred[i]:m.add(tv[i]>tv[j])
    end=m.new_int_var(0,max(c['t'])+radius,'end');m.add_max_equality(end,tv);m.add(end<=max(c['t'])+1)
    terms=[]
    for i,t in enumerate(c['t']):
     dev=m.new_int_var(0,radius,f'd{i}');m.add_abs_equality(dev,tv[i]-t)
     terms.append(int(round(grad[i]*1e12))*tv[i]+int(penalty*1e5)*dev)
    m.minimize(sum(terms));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=3
    st=s.solve(m)
    if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):continue
    c['t']=[s.value(t)for t in tv]
    yield c,dict(family='timing',move='sensitivity_lns',radius=radius,region=mode,penalty=penalty,pair_linear_delta=float(grad@(np.array(c['t'])-base['t'])),changed=sum(a!=b for a,b in zip(c['t'],base['t'])))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--label',default='sensitive');a=ap.parse_args();batch(list(proposals(read(a.stem))),a.label,a.workers)
