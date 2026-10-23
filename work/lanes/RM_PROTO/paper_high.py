import sys,os
sys.dont_write_bytecode=True
from paper_eval import *
from scipy.stats import beta
import functools
m=make_model();engines=[];look=[]
for basis in 'XY':
 e,fs=make_ed(m,basis);engines.append(e)
 ar=np.zeros((150,15,3),dtype=np.int64);ns=np.zeros(150,dtype=np.int64)
 for ch,w,s,d,z in fs:
  ar[ch,ns[ch]]=[s,d,z];ns[ch]+=1
 look.append(ar)

@functools.lru_cache(None)
def metric(b,s,d):
 if d&32767:return 0.,0.
 e=engines[b];a=e.phi(s)
 for k,pm in enumerate(e.projs):
  sg=1-2*(int(e.v[k])^((d>>k)&1));a=(a+sg*e.apply(a,pm))/2
 A=float(np.vdot(a,a).real)
 E=e.expect(a,e.Qs[('XY'[b],0,0)])*(-1 if b else 1)
 return A,E

rng=np.random.default_rng(20261024);out={'samples_per_order':1000000,'seed':20261024,'strata':{}}
for w in [4,5,6]:
 total=1000000;positive=0;loss_sum=0.;acc_sum=0.
 for start in range(0,total,100000):
  ch=np.sort(rng.integers(150,size=(100000,w)),axis=1)
  bad=np.any(np.diff(ch,axis=1)==0,axis=1)
  while bad.any():
   ch[bad]=np.sort(rng.integers(150,size=(bad.sum(),w)),axis=1);bad=np.any(np.diff(ch,axis=1)==0,axis=1)
  ix=(rng.random(ch.shape)*ns[ch]).astype(int)
  sig=[np.bitwise_xor.reduce(ar[ch,ix],axis=1) for ar in look]
  src=(sig[0][:,1]&32767)==0
  S=np.column_stack([sig[0][src],sig[1][src]])
  uniq,cts=np.unique(S,axis=0,return_counts=True)
  for (sx,dx,zx,sy,dy,zy),ct in zip(uniq,cts):
   ax,ex=metric(0,int(sx),int(dx));ay,ey=metric(1,int(sy),int(dy))
   loss=(ax+ay)/4-(((-1)**int(zx))*ex+((-1)**int(zy))*ey)/(2*np.sqrt(2))
   positive+=int(ct)*int(loss>1e-10);loss_sum+=ct*loss;acc_sum+=ct*(ax+ay)/2
 p=1e-3;mass=math.comb(150,w)*p**w*(1-p)**(150-w)
 upper=float(beta.ppf(1-1e-3/3,positive+1,total-positive))
 out['strata'][w]={'samples':total,'positive_events':positive,'mean_loss':loss_sum/total,'mean_acceptance':acc_sum/total,'mass':mass,'loss_upper':mass*upper,'loss_estimate':mass*loss_sum/total}
 print(w,out['strata'][w],flush=True)
 (BASE/'paper_high.json').write_text(json.dumps(out,indent=2)+'\n')
p=1e-3;orders=json.loads((BASE/'paper_orders.json').read_text());tail=1-sum(math.comb(150,w)*p**w*(1-p)**(150-w) for w in range(7));q3=orders['coefficient_cubic']*p**3*(1-p)**147
out['tail_w7plus']=tail;out['joint_confidence']=.999;out['upper_infidelity']=(q3+sum(v['loss_upper'] for v in out['strata'].values())+tail)/(1-p)**150
out['estimated_infidelity']=(q3+sum(v['loss_estimate'] for v in out['strata'].values()))/(orders['acceptance_through_fault3']+sum(v['mass']*v['mean_acceptance'] for v in out['strata'].values()))
(BASE/'paper_high.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
