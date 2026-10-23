"""Use native h-measure-h to retain the postselected X eigenstate without a reset."""
from search_v10 import *

raw,data,ops,times,npre=base()
assert ops[110]==('MX',(8,),7) and ops[111]==('RX',(8,),None)
pre=ops[:110]+[('MX_KEEP',(8,),7)]+ops[112:npre]
newops=pre+ops[npre:];np=len(pre)
labels=[];seen=set()
for seed in (4,0,1,2,3,5,6,7):
    pt=greedy(pre,seed,True,True)
    ct=[t-min(times[npre:])+max(pt)+1 for t in times[npre:]]
    ts=pt+ct
    for boundary in (False,True):
        ts1=pack_pre(newops,ts,np,seed,False) if boundary else ts
        label=f'nreset_s{seed}_b{int(boundary)}'
        qasm=text_for(raw,newops,ts1);h=hashlib.sha256(qasm.encode()).hexdigest()
        if h in seen:continue
        seen.add(h)
        rep=tprep.check(qasm,data,shots=1000,seed=0)
        print(label,'depth',max(ts1)-min(ts1)+1,str(rep),flush=True)
        if not rep.passed:continue
        save(label,raw,data,newops,ts1,np,{'change':'Remove reset after central postselected X readout; h-measure-h natively retains X eigenstate','priority_seed':seed,'boundary_overlap':boundary})
        labels.append(label)
(HERE/'nreset_manifest.json').write_text(json.dumps(labels,indent=2)+'\n')
