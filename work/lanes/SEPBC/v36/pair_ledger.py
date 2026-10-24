from regions import *
from model import Basis
ev=exact2.Eval((V/'base.qasm').read_text(),c['meta']['data_qubits']);ownership=[];mixed=[]
for j,ch in enumerate(ev.m.chans):
 lab=ev.chan_label(j)
 if ch['gap']:
  q,first,n=ch['gap'];parts=collections.Counter(region([q],tt,True)for tt in range(first,first+n));weights={k:v/n for k,v in parts.items()}
  if len(parts)>1:mixed.append(dict(channel=j,gap=ch['gap'],regions=dict(parts)))
 else:weights={region(lab['qubits'],int(lab['steps'])):1.}
 ownership.append(weights)
bas=Basis();indices=[];constraints=[]
for i,(x,z,coef)in enumerate(ev.e.projs):
 co=bas.express(x|(z<<ev.e.r))
 if co is None:bas.add(x|(z<<ev.e.r));indices.append(i)
 else:
  rel=1<<i
  for j,bi in enumerate(indices):
   if co>>j&1:rel^=1<<bi
  constraints.append(rel)
old=ev.e.ntable;ev.e.ntable=lambda s,d:(0.,None)if any((int(d)&h).bit_count()%2 for h in constraints)else old(s,d)
r=exact2.run(ev,2,keep_thr=0);pairs=collections.Counter();examples={}
for value,i,j,n,acc in r['big']:
 for a,wa in ownership[int(ev.fch[i])].items():
  for b,wb in ownership[int(ev.fch[j])].items():
   key=' x '.join(sorted([a,b]));val=value*wa*wb;pairs[key]+=val
   if val>examples.get(key,[0])[0]:examples[key]=[val,ev.fault_label(i),ev.fault_label(j)]
assert abs(sum(pairs.values())-r['loss2'])<1e-15
out=dict(second=r['loss2'],pair_classes=dict(pairs.most_common()),examples=examples,mixed_idle_gaps=mixed,attribution='Unchanged exact2 physical pair contraction. Boundary-crossing compressed idle-channel contributions, if any, are allocated by physical tick count; all-orders removal masks instead recompose exact idle probabilities.')
(V/'ledger/pairs.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
