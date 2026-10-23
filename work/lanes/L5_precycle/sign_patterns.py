"""Conjugate the transversal double-cat check by Steane Z stabilizer sign patterns."""
from search_v10 import *
from tprep.grid import SUPPORTS
raw,data,ops,times,npre=base()
physical=[0,20,7,4,3,15,8]
stabs=[{physical[i] for i in s} for s in SUPPORTS]
labels=[]
for mask in range(1,8):
    sign=set()
    for k,s in enumerate(stabs):
        if (mask>>k)&1:sign^=s
    changed=[(('g:tdg' if op[0]=='g:t' else 'g:t'),op[1],op[2]) if i>=85 and i<npre and op[0] in ('g:t','g:tdg') and op[1][0] in sign else op for i,op in enumerate(ops)]
    qasm=text_for(raw,changed,times)
    rep=tprep.check(qasm,data,shots=1000)
    label=f'cat_sign_{mask}'
    print(label,sorted(sign),str(rep),flush=True)
    if not rep.passed:continue
    save(label,raw,data,changed,times,npre,{'change':'Conjugate double-cat transversal T rotations by a Steane Z stabilizer','mask':mask,'flipped_qubits':sorted(sign)})
    labels.append(label)
(HERE/'sign_manifest.json').write_text(json.dumps(labels,indent=2)+'\n')
