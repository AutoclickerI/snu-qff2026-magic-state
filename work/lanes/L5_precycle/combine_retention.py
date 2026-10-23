"""Combine measured boundary scheduling gains with retaining X-readout states."""
from lns import read_state
from search_v10 import *
labels=[]
for pidx,parent in enumerate(('joint1_0026','bell0_delay_v10_reference')):
    raw,data,ops,times,np,meta=read_state(parent)
    candidates=[];last={}
    for i,(k,qs,b) in enumerate(ops):
        if k=='RX' and qs[0] in last:
            j=last[qs[0]]
            if ops[j][0]=='MX' and ops[j][2] in (6,9,11):candidates.append((qs[0],j,i))
        for q in qs:last[q]=i
    assert len(candidates)==3,candidates
    candidates.sort()
    for mask in range(1,8):
        replace={j:i for b,(q,j,i) in enumerate(candidates) if (mask>>b)&1}
        deleted=set(replace.values());out=[];ts=[]
        for i,op in enumerate(ops):
            if i in deleted:continue
            if i in replace:op=('MX_KEEP',op[1],op[2]);t=times[replace[i]]
            else:t=times[i]
            out.append(op);ts.append(t)
        label=f'combined_p{pidx}_m{mask}'
        newnp=np-sum(i<np for i in deleted)
        qasm=text_for(raw,out,ts);r=tprep.check(qasm,data,shots=1000)
        print(label,str(r),flush=True)
        if not r.passed:continue
        save(label,raw,data,out,ts,newnp,{'change':'Combine late cycle preparation and retained postselected X readouts','parent':parent,'retained_ancillas':[q for b,(q,j,i) in enumerate(candidates) if (mask>>b)&1]})
        labels.append(label)
(HERE/'combined_manifest.json').write_text(json.dumps(labels,indent=2)+'\n')
