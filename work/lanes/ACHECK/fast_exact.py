"""Exact identity-projector pruning; no approximation or change to fault sums.

The dense rotation span represents many detector projectors as scalar I.
A flipped such detector has exactly zero acceptance for every rotation sign.
Skip its table construction, preserving the original engine everywhere else.
"""
from common import *
import engine,numpy as np,runpy
_ntable=engine.Engine.ntable;_batch=engine.Engine.batch_n
def mask(self):
 if not hasattr(self,'_identity_mask'):
  self._identity_mask=sum(1<<i for i,(x,z,c) in enumerate(self.projs) if x==0 and z==0 and abs(c-(-1)**int(self.v[i]))<1e-15)
 return self._identity_mask
def ntable(self,s,d):
 if d&mask(self):return 0.0,None
 return _ntable(self,s,d)
def batch_n(self,S,D):
 D=np.asarray(D,dtype=np.int64);S=np.asarray(S,dtype=np.int64)
 live=(D&mask(self))==0
 if live.all():return _batch(self,S,D)
 aa=np.zeros(len(D));nn=np.zeros((len(D),1024))
 if live.any():aa[live],nn[live]=_batch(self,S[live],D[live])
 return aa,nn
engine.Engine.ntable=ntable;engine.Engine.batch_n=batch_n
if __name__=='__main__':runpy.run_path(str(ROOT/'work/lanes/EVAL/exact2.py'),run_name='__main__')
