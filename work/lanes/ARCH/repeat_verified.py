"""Verified late partial Z round, and a complete second Steane round."""
import json
from build import *
def first(c):
    c.prep(A,True,32);c.prep(B,False,32);c.prep(C,False,32)
    for i in range(7):c.cx(33,D[i],A[i]);c.cx(33,B[i],C[i]);c.cx(34,B[i],D[i])
    c.readblock(34,A,'Z');c.readblock(34,C,'Z',True);c.readblock(35,B,'X')
def make(which):
    c=Circuit();first(c)
    if which=='repeatZ_verified':
        c.prep(A,True,38);c.prep(C,True,38)
        for i in range(7):c.cx(39,C[i],A[i]);c.cx(40,D[i],A[i])
        c.readblock(40,C,'X',True);c.readblock(41,A,'Z')
    else:
        P=[1,2,6,9,10,13,14]
        c.prep(P,True,38);c.prep(A,False,38);c.prep(C,False,38)
        for i in range(7):c.cx(39,D[i],P[i]);c.cx(39,A[i],C[i]);c.cx(40,A[i],D[i])
        c.readblock(40,P,'Z');c.readblock(40,C,'Z',True);c.readblock(41,A,'X')
    return c.save(which)
if __name__=='__main__':
    rows=[make('repeatZ_verified'),make('double_full')]
    (HERE/'repeat_manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
