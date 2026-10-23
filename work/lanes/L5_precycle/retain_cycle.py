"""Retain postselected X readouts used for final-cycle |+> ancillas."""
from search_v10 import *
raw,data,ops,times,npre=base()
choices=[(1,134),(13,84),(9,132)]
labels=[]
for mask in range(1,8):
    keep={q:mi for b,(q,mi) in enumerate(choices) if (mask>>b)&1}
    removed={i for i,op in enumerate(ops) if i>=npre and op[0]=='RX' and op[1][0] in keep}
    new=[];ts=[]
    for i,(op,t) in enumerate(zip(ops,times)):
        if i in removed:continue
        if i in keep.values():op=('MX_KEEP',op[1],op[2])
        new.append(op);ts.append(t)
    for seed in (4,5):
        tt=pack_pre(new,ts,npre,seed,False)
        label=f'retain_cycle_m{mask}_s{seed}'
        qasm=text_for(raw,new,tt)
        start=time.monotonic();r=tprep.check(qasm,data,shots=10000)
        print(label,time.monotonic()-start,str(r),flush=True)
        if not r.passed:continue
        save(label,raw,data,new,tt,npre,{'change':'Retain postselected MX state instead of resetting final-cycle X ancillas','ancillas':sorted(keep),'priority_seed':seed})
        labels.append(label)
(HERE/'retain_manifest.json').write_text(json.dumps(labels,indent=2)+'\n')
