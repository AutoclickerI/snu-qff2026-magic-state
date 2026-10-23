import sys,itertools,re
sys.dont_write_bytecode=True
from subsets import subset
from verified_a import final4
from variants import finish
from alap import alap
from build import Circuit

S=[{9,8,10,15},{9,8,14,13},{9,10,14,11}]
def reduced(inds):
 c=subset(['TA','PA']);start=c.lines.index('// STAGE TA');end=next(i for i in range(start+1,len(c.lines)) if c.lines[i].startswith('// STAGE'))
 g=Circuit();g.stage('reduced_TA')
 for q in ([16,17] if len(inds)==2 else [16]):g.reset(q)
 g.reset(19,'X')
 if len(inds)==2:
  a,b=sorted(S[inds[0]]&S[inds[1]]);u1,u2=sorted(S[inds[0]]-S[inds[1]]);v1,v2=sorted(S[inds[1]]-S[inds[0]])
  pairs=[(a,16),(19,16),(b,16),(16,17),(u1,16),(u2,16),(v1,17),(v2,17),(19,16),(19,17)]
 else:
  a,b,d,e=sorted(S[inds[0]]);pairs=[(a,16),(19,16),(b,16),(d,16),(19,16),(e,16)]
 for a,b in pairs:g.gate('cx',a,b)
 g.lines.append('measure q[15] -> c[1];')
 if len(inds)==2:g.lines.append('measure q[16] -> c[2];')
 g.gate('h',19);g.lines.append('measure q[18] -> c[4];')
 c.lines[start:end]=g.lines;c.dets=[d for d in c.dets if d!=[3] and not(len(inds)==1 and d==[2])]
 return c
if __name__=='__main__':
 for n in [1,2]:
  for ids in itertools.combinations(range(3),n):finish(alap(final4(reduced(ids))),'va_ta'+''.join(map(str,ids))+'_PA')
