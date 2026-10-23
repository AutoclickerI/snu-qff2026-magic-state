"""Exhaust legal CX/readout shifts at the check-to-cycle boundary of a selected candidate."""
from lns import read_state
from search_v10 import *
parent=sys.argv[1]
raw,data,ops,times,np,meta=read_state(parent)
pred,succ=dag(ops,True)
seen={hashlib.sha256(text_for(raw,ops,times).encode()).hexdigest()};labels=[]
for i in sorted(range(np),key=lambda i:-i):
    if times[i]<27 or ops[i][0] not in ('cx','M','MX','MX_KEEP'):continue
    lo=max([times[j]+1 for j in pred[i]]+[min(times)])
    hi=min([times[j]-1 for j in succ[i]]+[max(times)])
    occupied={(q,t) for j,(op,t) in enumerate(zip(ops,times)) if j!=i for q in op[1]}
    for t in range(max(lo,times[i]-3),min(hi,times[i]+3)+1):
        if t==times[i] or any((q,t) in occupied for q in ops[i][1]):continue
        ts=list(times);ts[i]=t;qasm=text_for(raw,ops,ts);h=hashlib.sha256(qasm.encode()).hexdigest()
        if h in seen:continue
        seen.add(h)
        label=f'grid_{len(labels):03d}'
        save(label,raw,data,ops,ts,np,{'change':'Exhaustive legal boundary CX/readout shift','parent':parent,'op':i,'gate':ops[i],'from':times[i],'to':t})
        labels.append(label)
(HERE/'grid_manifest.json').write_text(json.dumps(labels,indent=2)+'\n')
print(json.dumps({'parent':parent,'candidates':len(labels)}),flush=True)
