from common import *
from variants import retime
for qs in [(9,15),(9,15,8),(9,15,14),(9,15,8,14)]:
 text=(HERE/'reuse_1_2_16.qasm').read_text();h,r,tail=S.qasm_ops(text);us=S.fold_units(r);old=native_times(text,us)
 init={q:max(i for i,u in enumerate(us) if old[i]<45 and u.qs==(q,) and u.name in ('RX','RESET')) for q in qs}
 uu=[];tt=[]
 for i,(u,t) in enumerate(zip(us,old)):
  uu.append(u);tt.append(t)
  if i in init.values():
   q=u.qs[0];b=140+q
   ls=([f'h q[{q}];'] if u.name=='RX' else [])+[f'measure q[{q}] -> c[{b}];']+([f'h q[{q}];'] if u.name=='RX' else [])
   uu.append(unit(ls));tt.append(t);tail.append(f'// DETECTOR c[{b}]')
 rr={i for i,t in enumerate(tt) if t>=45};ts,R=retime(uu,tt,rr)
 emit('combo_'+'_'.join(map(str,qs)),uu,ts,tail,dict(R=R,method='MX reuse q1/q2, M-init q16, verified initialization',verified_sites=qs))
