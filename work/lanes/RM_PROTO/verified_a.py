import sys,copy
sys.dont_write_bytecode=True
from variants import direct,finish,ENC
from subsets import subset
from alap import alap
from build import DATA
from tprep.grid import SUPPORTS

def final4(c):
 c.stage('verified_A_final_round')
 A=list(range(8,15));B=list(range(16,23));C=list(range(24,31));D=[15,23,31,32,33,34,35]
 for block,dual in [(A,True),(B,False),(C,False),(D,True)]:
  for i,q in enumerate(block):c.reset(q,'X' if (i not in [0,1,3])==dual else 'Z')
  for layer in ENC:
   for p,q in layer:c.gate('cx',*((block[q],block[p]) if dual else (block[p],block[q])))
 c.barrier(A+B+C+D+[i+1 for i in DATA])
 for d,a in zip(D,A):c.gate('cx',d,a)
 rd=[c.meas(d,'X') for d in D]
 for d,a in zip([q+1 for q in DATA],A):c.gate('cx',d,a)
 for b,cc in zip(B,C):c.gate('cx',b,cc)
 # B→C one step before B→data, synchronized with A→data round.
 # Enforce A after its verification and B→C at that same layer.
 ra=[c.meas(a) for a in A];rc=[c.meas(cc) for cc in C]
 for b,d in zip(B,[q+1 for q in DATA]):c.gate('cx',b,d)
 rb=[c.meas(b,'X') for b in B]
 for rec in [ra,rb,rc,rd]:
  for g in SUPPORTS:c.dets.append([rec[i] for i in sorted(g)])
 c.dets.extend([rc,rd]);return c
if __name__=='__main__':
 for keep in [[],['TA'],['TB'],['TA','TB'],['TA','TB','PA','PB'],['TA','PA'],['TA','PB'],['PA'],['PA','PB']]:
  name='va_'+'_'.join(keep);finish(alap(final4(subset(keep))),name)
