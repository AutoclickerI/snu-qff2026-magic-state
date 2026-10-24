import sys,json,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a

def proposals():
 c=a.d.normalize(a.C.read(a.OUT/'base'))
 # Random-X resource initialization is frame-corrected by B detector parities.
 # A reset version replaces that record by zero in every such parity.
 for chosen in [(256,),(260,),(262,),(256,260),(256,262),(260,262),(256,260,262)]:
  x=a.C.clone(c)
  for b in chosen:
   i=next(i for i,u in enumerate(x['u'])if b in a.bits(' '.join(u.lines)));q=x['u'][i].qs[0];assert x['u'][i].name=='MX'
   x['u'][i]=a.C.Unit([f'reset q[{q}];',f'h q[{q}];']);a.strip_bits(x,[b])
  yield 'resource_reset_'+'_'.join(map(str,chosen)),x,dict(family='resource_MX_to_RX',bits=chosen)
 # New measured-Z preparation checks in all late resource reset slots.
 for qs in [(11,),(5,),(12,),(19,),(6,),(4,),(13,),(5,12),(11,5,12)]:
  x=a.C.clone(c);recs=[]
  for q in qs:
   inds=[i for i,(u,t)in enumerate(zip(x['u'],x['t']))if u.name=='RESET'and u.qs==(q,)and 30<=t<c['meta']['R']]
   assert inds,(q,qs);i=inds[-1];b=a.C.bit(x);x['u'][i]=a.C.Unit([f'measure q[{q}] -> c[{b}];']);x['tail'].append(f'// DETECTOR c[{b}]');recs.append(dict(q=q,time=x['t'][i],bit=b))
  yield 'mz_'+'_'.join(map(str,qs)),x,dict(family='measured_Z_init',checks=recs)
 # Sequential reuse of an echo helper's known readout: omit a later reset
 # only when the immediately preceding native event is matching-basis M.
 for i,(u,t)in enumerate(zip(c['u'],c['t'])):
  if u.name not in ('RESET','RX')or t<18:continue
  q=u.qs[0];prev=[j for j in range(i)if q in c['u'][j].qs]
  if not prev or c['u'][prev[-1]].name!=('MEASURE'if u.name=='RESET'else'MX'):continue
  b=a.bits(' '.join(c['u'][prev[-1]].lines))[0]
  if not any(s==f'// DETECTOR c[{b}]'for s in c['tail']):continue
  x=a.C.clone(c);a.remove_units(x,{i})
  yield f'reuse_{q}_{t}',x,dict(family='shared_helper_known_reuse',q=q,time=t,known_record=b)
if __name__=='__main__':a.batch(proposals(),'additional',14)
