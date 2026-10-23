"""Test removing double-cat leaf flags or its central readout; official gates remain mandatory."""
from search_v10 import *
raw,data,ops,times,npre=base();labels=[]
for mask in range(1,5):
    template=copy.deepcopy(raw)
    if mask<4:
        qs={q for b,q in enumerate((1,2)) if (mask>>b)&1}
        deleted={i for i,op in enumerate(ops[:npre]) if i>=85 and any(q in op[1] for q in qs)}
        bits={op[2] for i,op in enumerate(ops) if i in deleted and op[2] is not None}
        source={'change':'Remove double-cat leaf flags','ancillas':sorted(qs)}
    else:
        deleted={110};bits={7}
        source={'change':'Remove central cat readout, retain its reset; omit detectors containing that readout'}
    # Preserve the remaining components of mixed detectors, e.g. c10 XOR c7 -> c10.
    template.detectors=[dd for d in raw.detectors if (dd:=[b for b in d if b not in bits])]
    pre=[op for i,op in enumerate(ops[:npre]) if i not in deleted]
    no=pre+ops[npre:];np=len(pre);pt=greedy(pre,4,True,True)
    ts=pt+[t-min(times[npre:])+max(pt)+1 for t in times[npre:]]
    qasm=text_for(template,no,ts);r=tprep.check(qasm,data,shots=1000)
    label=f'prune_cat_{mask}';print(label,str(r),flush=True)
    if not r.passed:continue
    m=save(label,template,data,no,ts,np,source);m['template_detectors']=template.detectors
    (HERE/(label+'.json')).write_text(json.dumps(m,indent=2)+'\n');labels.append(label)
(HERE/'prune_manifest.json').write_text(json.dumps(labels,indent=2)+'\n')
