import sys,copy
sys.dont_write_bytecode=True
from variants import direct,final_round,finish
from alap import alap

def late_verify():
 c=direct(True)
 start=c.lines.index('// STAGE logical_X_verifier');end=c.lines.index('// STAGE TA')
 block=c.lines[start:end];c.lines=c.lines[:start]+c.lines[end:]
 # Add conventional two-CX flag around the inner five data interactions.
 out=['// STAGE late_logical_X_verifier','reset q[30];'];k=0
 for line in block[1:]:
  if line.startswith('cx '):
   k+=1
   if k==7:out.append('cx q[29],q[30];')
  out.append(line)
  if line.startswith('cx ') and k==1:out.append('cx q[29],q[30];')
 out.append(f'measure q[30] -> c[{c.nm}];');c.dets.append([c.nm]);c.nm+=1
 where=c.lines.index('// STAGE transversal_T');c.lines[where:where]=out
 return c
if __name__=='__main__':
 c=late_verify();finish(c,'rm7_lateverify');finish(alap(copy.deepcopy(c)),'rm7_lateverify_alap')
 finish(alap(final_round(c)),'rm7_lateverify_steane_alap')
