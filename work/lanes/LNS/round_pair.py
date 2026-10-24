"""Diversified commuting orders at a prescribed native round, exact-priced."""
from core import *
import argparse,random,concurrent.futures

def pair_gradient(base):
 ev=exact2.Eval(textof(base),D);sy=setup_syndromes(ev);pairs=[(a,b)for a in range(len(sy))for b in range(a,len(sy))if sy[a]==sy[b]]
 exact2.G.update(ev=ev,third=True,SA=float(ev.fp@ev.a_single),Pch=np.bincount(ev.fch,weights=ev.fp),pairs=pairs)
 _,_,sens,_,_=exact2._pair_chunk((0,len(pairs),1));grad=np.zeros(len(base['u']));byq={}
 for i,u in enumerate(base['u']):
  for q in u.qs:byq.setdefault(q,[]).append(i)
 for ch,v in zip(ev.m.chans,sens):
  if ch['gap']is None:continue
  q,first,n=ch['gap'];left=[i for i in byq[q]if base['t'][i]<first];right=[i for i in byq[q]if base['t'][i]>=first+n]
  if not left or not right:continue
  w=v/ch['prob']*.001*(1-4*.001/3)**n;grad[left[-1]]-=w;grad[right[0]]+=w
 (OUT/'round43_pair.gradient.json').write_text(json.dumps(dict(source=base['source'],gradient=grad.tolist()),indent=2));return grad.tolist()

def one(job):
 stem,R,seed,scale,grad=job;orig=read(stem);us=orig['u'];old=orig['t'];rng=random.Random(seed);m=cp_model.CpModel();tv=[m.new_int_var(0,R+2,f't{i}')for i in range(len(us))];per={}
 for i,u in enumerate(us):
  for q in u.qs:per.setdefault(q,[]).append(i)
 for seq in per.values():
  for pos,j in enumerate(seq):
   for i in seq[:pos]:
    if commute(us[i],us[j]):m.add(tv[i]!=tv[j])
    else:m.add(tv[i]<tv[j])
 for i,t in enumerate(old):
  if t>=orig['meta']['R']:m.add(tv[i]==t+R-orig['meta']['R'])
  else:m.add(tv[i]<R)
 ds=[];terms=[]
 for i,t in enumerate(old):
  d=m.new_int_var(0,100,f'd{i}');m.add_abs_equality(d,tv[i]-t);ds.append(d);w=rng.randint(1,9);terms.append(w*100*d+rng.randint(-scale,scale)*tv[i])
 pair_scale=[1e9,1e10,1e11,3e11][seed%4];terms.extend(int(round(g*pair_scale))*v for g,v in zip(grad,tv));m.minimize(sum(terms));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=15;s.parameters.cp_model_presolve=False;s.parameters.random_seed=seed
 st=s.solve(m);desc=dict(family='commute',move='R43_pair_sensitivity_LNS',pair_scale=pair_scale,R=R,seed=seed,random_scale=scale,solver=s.status_name(st),source=stem,parent_total=orig['meta']['lns_result']['total'],local_track=True)
 if st not in(cp_model.FEASIBLE,cp_model.OPTIMAL):return dict(desc=desc,solver_status=s.status_name(st)),None,None
 orig['t']=[s.value(x)for x in tv]
 try:orig=normalize(orig)
 except Exception as e:return dict(desc=desc,error='build: '+str(e)),None,None
 txt=textof(orig);r=worker((txt,orig['meta'],desc));return r,txt,orig['meta']
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--workers',type=int,default=12);ap.add_argument('--trials',type=int,default=48);a=ap.parse_args();label='round43_pair';best=1.;grad=pair_gradient(read(a.stem));jobs=[(a.stem,43,25000+i,[1,10,50,200][i%4],grad)for i in range(a.trials)]
 with concurrent.futures.ProcessPoolExecutor(a.workers)as pool,(OUT/(label+'.jsonl')).open('a')as f:
  for r,txt,md in pool.map(one,jobs):
   if r.get('exp_minus_A1',0)>=.505 and r.get('total',1)<best-1e-12:
    best=r['total'];r['stem']=label+'_'+r['sha256'][:10];save(r['stem'],txt,md,r)
   f.write(json.dumps(r)+'\n');f.flush();report();print(json.dumps(r),flush=True)
