"""Spend confirmed surplus on the useful original preparation checks."""
import sys,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import v35_campaign as v
base=v.C.read(v.V/'base');c=v.C.read(v.V/'refined/omit_16_22')
def restore(c,bits):
 x=v.C.clone(c)
 for b in bits:
  i=next(i for i,u in enumerate(base['u'])if b in v.a.bits(' '.join(u.lines)));u=base['u'][i];t=base['t'][i];q=u.qs[0]
  inds=[j for j,(uu,tt)in enumerate(zip(x['u'],x['t']))if tt==t and uu.qs==(q,)]
  assert len(inds)<=1
  if inds:x['u'][inds[0]]=v.C.Unit(u.lines)
  else:x['u'].append(v.C.Unit(u.lines));x['t'].append(t)
  for tail in base['tail']:
   if b in v.a.bits(tail)and tail not in x['tail']:x['tail'].append(tail)
 return v.d.normalize(x)
def proposals():
 for bits in [(181,182),(181,182,188),(181,182,188,39),(181,182,188,45),(181,182,188,39,45),(181,182,188,40),(181,182,188,41),(181,182,188,39,41),(181,182,188,40,41)]:
  yield 'restore_'+'_'.join(map(str,bits)),restore(c,bits),dict(family='conditional_restore_preparation',parent='refined/omit_16_22',bits=bits,budget_screen=True)
if __name__=='__main__':v.a.batch(proposals(),'tightened',9)
