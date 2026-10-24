"""Sparse A-to-C readout recoding: all single edges and transversal subsets."""
import json
from build import *
def build(name,pairs):
    c=Circuit(); c.prep(A,True,32);c.prep(B,False,32);c.prep(C,False,32)
    for i in range(7): c.cx(33,D[i],A[i]);c.cx(33,B[i],C[i]);c.cx(34,B[i],D[i])
    for i,j in pairs: c.cx(34,A[i],C[j])
    liveA={i for i,_ in pairs};liveC={j for _,j in pairs}
    ab=[c.read(35 if i in liveA else 34,q) for i,q in enumerate(A)]
    cb=[c.read(35 if i in liveC else 34,q) for i,q in enumerate(C)]
    bb=[c.read(35,q,'X') for q in B]
    for bs in (ab,bb):
        for S in GENS:c.dets.append(' '.join(f'c[{bs[i]}]' for i in S))
    for S in GENS+[list(range(7))]:
        bs=[cb[i] for i in S]+[ab[i] for i,j in pairs if j in S]
        c.dets.append(' '.join(f'c[{b}]' for b in bs))
    return c.save(name,dict(readout_pairs=pairs))
if __name__=='__main__':
    rows=[]
    for i in range(7):
        for j in range(7):rows.append(build(f'ac{i}{j}',[(i,j)]))
    for mask in range(1,128): rows.append(build(f'acmask{mask:03d}',[(i,i) for i in range(7) if mask>>i&1]))
    (HERE/'readout_manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
