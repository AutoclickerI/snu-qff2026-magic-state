"""Matched early-verification and correlated-codeword resource prices."""
import os,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/ARCH'))
import build as arch
arch.HERE=H
from build import Circuit,A,B,C,D,GENS,gf33

def build(gap=0,correlated=False,R=33):
 c=Circuit();c.prep(A,True,R-1);v=R-gap
 if correlated:
  # Bell seeds at the three encoder pivots. All other B/C sites start zero.
  for q in B+C:c.add(v-5,f'reset q[{q}];','prep')
  for i in (0,1,3):
   c.add(v-5,f'h q[{B[i]}];','prep');c.cx(v-4,B[i],C[i],'prep')
  for k,layer in enumerate(gf33.LAYERS0):
   for a,b in layer:
    for blk in (B,C):c.cx(v-3+k,blk[a],blk[b],'prep')
 else:c.prep(B,False,v-1);c.prep(C,False,v-1)
 for i in range(7):c.cx(R,D[i],A[i]);c.cx(v,B[i],C[i]);c.cx(R+1,B[i],D[i])
 c.readblock(R+1,A,'Z');cb=c.readblock(v+1,C,'Z',True);c.readblock(R+2,B,'X')
 if correlated:
  c.dets += [f'c[{b}]' for b in cb]
 name=f'gf_{"correlated" if correlated else "separate"}_R{R}_gap{gap}'
 c.save(name,dict(gap=gap,correlated=correlated,R=R))
 return H/name

if __name__=='__main__':
 for gap in (0,1,2,4):build(gap)
 for R in (33,39,42,45):build(0,True,R)
