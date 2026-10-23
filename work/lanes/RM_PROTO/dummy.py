import sys
sys.dont_write_bytecode=True
from variants import direct,finish
from alap import alap
from build import DATA

def dummy(parallel):
 c=direct(parallel);start=c.lines.index('// STAGE coherent_gauge_frame')
 c.lines=c.lines[:start];c.nm=15;c.dets=c.dets[:-1]
 A=list(range(16,23)) if parallel else list(range(20,27))
 B=list(range(23,30)) if parallel else list(range(27,34))
 c.stage('dummy_preparation')
 for q in A+B:c.reset(q)
 c.barrier(list(range(1,16))+A+B)
 c.stage('coherent_gauge_frame')
 for q in range(1,8):c.gate('cx',q,q+7)
 for a,b in zip(A,B):c.gate('cx',a,b)
 c.stage('final_step')
 rec={q:c.meas(q,'X') for q in range(8,16)}
 c.dets.append(list(rec.values()));c.frame=[rec[q] for q in range(8,15)]
 for a,b,d in zip(A,B,range(1,8)):
  c.meas(b,'Z',True);c.gate('cx',a,d)
 return c
if __name__=='__main__':
 for par in [False,True]:finish(alap(dummy(par)),'rm7_'+('parallel' if par else 'serial')+'_dummy_alap')
