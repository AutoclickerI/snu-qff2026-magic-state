"""Unweighted A-CX Pauli classes after ideal propagation; explanatory, not ranking."""
from a30_common import *
import collections

def counts(text,md):
 h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us)
 _,_,_,baseu,baset,_,init,owned,_=source();release={q:max(baset[j] for j in range(init[q]) if q in baseu[j].qs) for q in A}
 gates=[edge(u) for u,t in zip(us,ts) if u.name=='CX' and t<48 and set(u.qs)<=set(A) and all(t>release[q] for q in u.qs)];result=collections.Counter();detail=[]
 def sig(x):return sum(1<<k for k,row in enumerate(ROWS) if sum(q in x for q in [A[i] for i in row])%2)
 for i,(a,b) in enumerate(gates):
  for pa in range(4):
   for pb in range(4):
    if pa==pb==0:continue
    x={q for q,p in [(a,pa),(b,pb)] if p&1};z={q for q,p in [(a,pa),(b,pb)] if p&2}
    for c,t in gates[i+1:]:
     if c in x:x.symmetric_difference_update({t})
     if t in z:z.symmetric_difference_update({c})
    if sig(x):key='A_X_detected'
    elif sig(z) and len(z)%2==0:key=f'danger_pairs_data_{DATA[sig(z)-1]}'
    elif sig(z)==0 and len(z)%2:key='undetected_logical_Z'
    else:key='other'
    result[key]+=1
    if key.startswith('danger'):detail.append(dict(gate=[a,b],index=i,paulis=[pa,pb],X=sorted(x),Z=sorted(z),syndrome=sig(z),data_partner=DATA[sig(z)-1]))
 return dict(counts=dict(result),dangerous_events=detail,units='each CX Pauli event has p/15 before exterior conditioning')
p=D/'finalists/a30_fastpick_feedback_neighbors_05085';base_text,base_md,*_=source();out=dict(base=counts(base_text,base_md),candidate=counts(p.with_suffix('.qasm').read_text(),json.loads(p.with_suffix('.json').read_text())),scope='Encoder CX events only. Exact exterior and normalization are not included; these counts do not rank circuits.')
(D/'fault_class_mechanism.json').write_text(json.dumps(out,indent=2));print({k:v['counts'] for k,v in out.items() if isinstance(v,dict)})
