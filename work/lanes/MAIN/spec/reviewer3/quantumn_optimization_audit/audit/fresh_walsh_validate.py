"""Finite three-channel brute-force validation of the exact contraction."""
from itertools import product
from functools import lru_cache
from fresh_exact_walsh import *

m,eng,groups,nd,ks,psi,where,elim=prepare()
ca=next(c for c,ch in enumerate(m.chans) if ch['name']=='DEPOLARIZE2' and ch['qs']==[1,2] and m.steps[ch['ins']][0][1]==44)
cb=next(c for c,ch in enumerate(m.chans) if ch['name']=='DEPOLARIZE1' and ch['qs']==[10] and ch['p']>.01)
cc=next(f['chan'] for f in m.faults if f['s']!=0 and m.chans[f['chan']]['name']=='DEPOLARIZE2')
chosen=[ca,cb,cc]
events=[]
for c in chosen:
    events.append([dict(p=1-m.chans[c]['p'],s=0,d=0,e=0)]+groups[c])
@lru_cache(None)
def tab(s,d):return eng.ntable(s,d)
ea=en=0.
for trip in product(*events):
    p=math.prod(f['p'] for f in trip);s=d=e=0
    for f in trip:s^=f['s'];d^=f['d'];e^=f['e']
    a,n=tab(s,d);ea+=p*a;en+=p*(0 if n is None else n[e])
results=[];cache={}
for key in [None]+eng.keys:
    qpm=None if key is None else eng.Qs[key]
    if qpm not in cache:cache[qpm]=kernel(eng,ks,psi,where,key)
    emask=0 if key is None else emask_for(key)
    factors=[channel_factor(m,groups[c],nd,emask) for c in chosen]+[cache[qpm]]
    results.append(contract(factors,elim['order']))
A=results[0];obs=sum(w*b*v for w,b,v in zip(eng.W,eng.beta,results[1:]));N=(A-obs)/2
out=dict(channels=chosen,event_count=math.prod(map(len,events)),contraction_acceptance=A,enumeration_acceptance=ea,contraction_N=N,enumeration_N=en,contraction_loss=N/A,enumeration_loss=en/ea,abs_A_difference=abs(A-ea),abs_N_difference=abs(N-en))
assert abs(A-ea)<1e-12 and abs(N-en)<1e-12
(ROOT/'audit/fresh_walsh_validation_result.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
