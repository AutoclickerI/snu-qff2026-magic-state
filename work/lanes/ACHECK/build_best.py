"""Reproduce the delivered circuit from the preserved v19 base, byte for byte."""
from common import *
from variants import retime
h,us,tail,old,meta,init,ai=base()
prev=max(j for j,u in enumerate(us[:init[1]]) if 1 in u.qs);assert us[prev].name=='MX'
us[prev]=unit(us[prev].lines+['h q[1];'])
uu=[u for i,u in enumerate(us) if i!=init[1]];tt=[t for i,t in enumerate(old) if i!=init[1]]
tt,R=retime(uu,tt,{i for i,t in enumerate(tt) if t>=45})
stage=emit('_replay_init1',uu,tt,tail,dict(R=R))
text=stage.with_suffix('.qasm').read_text();h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);old=native_times(text,us)
qi=max(i for i,u in enumerate(us) if old[i]<45 and u.qs==(16,) and u.name=='RESET')
us[qi]=unit(['measure q[16] -> c[96];']);tail.append('// DETECTOR c[96]')
init={q:max(i for i,u in enumerate(us) if old[i]<45 and u.qs==(q,) and u.name=='RX') for q in (2,9,15)}
uu=[];tt=[]
for i,(u,t) in enumerate(zip(us,old)):
 uu.append(u);tt.append(t)
 if i in init.values():
  q=u.qs[0];b=140+q
  uu.append(unit([f'h q[{q}];',f'measure q[{q}] -> c[{b}];',f'h q[{q}];']));tt.append(t);tail.append(f'// DETECTOR c[{b}]')
tt,R=retime(uu,tt,{i for i,t in enumerate(tt) if t>=45})
p=emit('replay',uu,tt,tail,dict(R=R,method='reproduction of verify_2_9_15'))
assert p.with_suffix('.qasm').read_bytes()==(HERE/'best.qasm').read_bytes(),'reproduction differs from delivery'
print('byte-identical to best.qasm',flush=True)
