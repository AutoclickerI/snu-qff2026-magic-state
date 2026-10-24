"""v35a physical detector prices; preserve native schedules and lane-local output."""
import sys,os,json,copy,re,itertools
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import acceptance as a
C=a.C;d=a.d;H=a.H;V=H/'v35';V.mkdir(exist_ok=True)
a.OUT=V;a.BASE_LOSS=4.393527676042e-5;a.BASE_ACC=.501236939
_old=d.normalize
def normalize(c):
 c=_old(c);c['meta']={k:c['meta'][k]for k in ('data_qubits','cx','native_depth','round_range')};c['meta']['R']=max(c['meta']['round_range']);c['meta']['source']='MAIN/v35a acceptance knapsack';return c
d.normalize=normalize
GUARDS=[(0,6,'Z',34,40,273),(20,19,'X',13,32,274),(7,13,'X',19,24,275),(10,11,'X',18,29,276),(4,5,'X',17,33,277)]
# Explicit indices permit a reset to precede its first guard edge by several ticks.
def drop_guard(c,g):
 q,h,axis,init,end,bit=g;x=C.clone(c)
 inds={i for i,(u,t)in enumerate(zip(x['u'],x['t']))if init<=t<=end and h in u.qs and (len(u.qs)==1 or q in u.qs)}
 assert len(inds)==4,(g,[(x['t'][i],x['u'][i].lines)for i in inds])
 a.remove_units(x,inds);a.strip_bits(x,[bit]);return d.normalize(x)

def physical():
 c=C.read(V/'base')
 for g in GUARDS:yield f'guard_{g[-1]}_off',drop_guard(c,g),dict(family='guard_remove',guard=g)
 # All known-zero measurements; omit and reset are different instruments.
 singles={a.bits(s)[0]for s in c['tail']if len(a.bits(s))==1}
 for i,(u,t)in enumerate(zip(c['u'],c['t'])):
  bs=a.bits(' '.join(u.lines))
  if u.name not in ('MX','MEASURE')or len(bs)!=1 or bs[0]not in singles or 273<=bs[0]<=277:continue
  b=bs[0];q=u.qs[0]
  if t>=44:
   # Detector-only prices cover terminal A flag and redundant syndrome checks.
   continue
  # Initial omit and reset forms are retained, including useful v34 cheap removals.
  for form in ('reset','omit'):
   x=C.clone(c);a.strip_bits(x,[b])
   if form=='omit':a.remove_units(x,{i})
   else:x['u'][i]=C.Unit([f'reset q[{q}];']+([f'h q[{q}];']if u.name=='MX'else[]))
   yield f'meas_{b}_{form}',x,dict(family='known_measurement',bit=b,q=q,time=t,form=form)
 for hs,name in [({1},'blue_Z'),({2},'blue_X'),({1,2},'blue_XZ')]:
  x=C.clone(c);inds={i for i,(u,t)in enumerate(zip(x['u'],x['t']))if 28<=t<=37 and set(u.qs)&hs}
  a.remove_units(x,inds);a.strip_bits(x,[64]if hs=={1}else[67]if hs=={2}else[64,67])
  yield name+'_off',x,dict(family='blue_physical',helpers=sorted(hs))
 # All four repeated terminal Z records are independently measurable guards.
 for bit,src,h in [(265,23,18),(266,22,31),(267,26,35),(268,27,34)]:
  x=C.clone(c);inds={i for i,(u,t)in enumerate(zip(x['u'],x['t']))if t>=44 and h in u.qs}
  assert len(inds)==3;a.remove_units(x,inds)
  x['tail']=[s for s in x['tail']if bit not in a.bits(s)]
  yield f'terminal_copy_{bit}_off',x,dict(family='terminal_redundancy',bit=bit,source_bit=src)

def add_echo(c,q,h,axis,init,first,last,end,move=None):
 x=C.clone(c)
 if move:
  bit,t=move;i=next(i for i,u in enumerate(x['u'])if bit in a.bits(' '.join(u.lines)));x['t'][i]=t
 assert not any(h in u.qs and init<=t<=end for u,t in zip(x['u'],x['t']))
 assert not any(q in u.qs and t in (first,last)for u,t in zip(x['u'],x['t']))
 bit=C.bit(x);edge=f'cx q[{q}],q[{h}];'if axis=='X'else f'cx q[{h}],q[{q}];'
 ini=[f'reset q[{h}];']+([f'h q[{h}];']if axis=='Z'else[])
 meas=[f'measure q[{h}] -> c[{bit}];'];meas=([f'h q[{h}];']+meas+[f'h q[{h}];'])if axis=='Z'else meas
 for t,ls in [(init,ini),(first,[edge]),(last,[edge]),(end,meas)]:x['u'].append(C.Unit(ls));x['t'].append(t)
 x['tail'].append(f'// DETECTOR c[{bit}]');return d.normalize(x)

def additions():
 c=C.read(V/'base')
 # Five v34 echoes are already present as the five guards. Reprice the three
 # absent checks with the longest compatible lifetimes on this schedule.
 for args in [(20,26,'Z',19,20,30,31,None),(10,16,'X',20,21,22,23,None),(10,16,'X',20,21,27,28,(43,30)),(15,21,'X',19,20,29,30,None)]:
  q,h,ax,ini,first,last,end,mv=args
  yield f'echo_{q}_{h}_{ax}_{first}_{last}',add_echo(c,*args[:-1],move=mv),dict(family='ported_echo',args=args)
 # q16 watch was removed by this branch; recover its exact parity at t30.
 x=C.clone(c);b=C.bit(x);x['u'].append(C.Unit([f'measure q[16] -> c[{b}];']));x['t'].append(30);x['tail'].append(f'// DETECTOR c[43] c[{b}]')
 yield 'watch16_t30',x,dict(family='watch_add',q=16,time=30,old_bit=43)
 # Known outcomes after a guard can prepare the next resource without reset.
 for q,t in [(13,25),(19,33),(6,41)]:
  i=next(i for i,(u,tt)in enumerate(zip(c['u'],c['t']))if tt==t and u.qs==(q,)and u.name=='RESET')
  x=C.clone(c);b=C.bit(x);x['u'][i]=C.Unit([f'measure q[{q}] -> c[{b}];']);x['tail'].append(f'// DETECTOR c[{b}]')
  yield f'mz_{q}_{t}',x,dict(family='measured_Z_init',q=q,time=t)
  if q!=6:
   x=C.clone(c);a.remove_units(x,{i});yield f'reuse_{q}_{t}',x,dict(family='reuse_guard_outcome',q=q,time=t)
 # Frame-corrected X resource preps.
 for b in (256,260,262):
  x=C.clone(c);i=next(i for i,u in enumerate(x['u'])if b in a.bits(' '.join(u.lines)));q=x['u'][i].qs[0]
  x['u'][i]=C.Unit([f'reset q[{q}];',f'h q[{q}];']);a.strip_bits(x,[b]);yield f'resource_{b}_reset',x,dict(family='resource_MX_to_RX',bit=b,q=q)

def init():
 import shutil
 for ext in ('.qasm','.json'):shutil.copyfile(H.parent/'MAIN'/('v35a'+ext),str(V/'base')+ext)
 d.save(C.read(V/'base'),V/'base')

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--workers',type=int,default=5);args=p.parse_args()
 if args.mode=='init':init()
 elif args.mode=='physical':
  fast={'meas_42_omit','meas_39_omit','meas_40_omit','meas_41_omit','meas_43_reset','meas_45_reset','meas_46_reset','meas_185_reset','meas_186_reset','meas_187_reset','meas_188_reset','meas_182_reset','meas_181_reset','meas_183_reset','meas_184_reset'}
  a.batch((x for x in physical()if x[0]not in fast and not x[0].startswith('guard_')),'physical',args.workers)
 elif args.mode=='additions':a.batch(additions(),'additions',args.workers)
