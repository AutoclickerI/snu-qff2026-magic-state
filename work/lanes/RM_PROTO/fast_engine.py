"""Exact short circuit of projectors that are ±identity on the entire rotation span."""
from engine import Engine
_original=Engine.table

def table(self,s,d):
 mask=getattr(self,'identity_projector_mask',None)
 if mask is None:
  mask=0
  for k,(x,z,coef) in enumerate(self.projs):
   if x==0 and z==0:
    assert abs(coef.real-(-1)**int(self.v[k]))<1e-12
    mask|=1<<k
  self.identity_projector_mask=mask
 if d&mask:return None
 return _original(self,s,d)
Engine.table=table
