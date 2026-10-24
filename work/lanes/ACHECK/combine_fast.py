from common import *
from variants import retime
for qs in [(9,15),(2,9,15),(1,2,9,15)]:
 src='init_1' if 1 not in qs else 'base'
 text=(HERE/(src+'.qasm')).read_text();h,r,tail=S.qasm_ops(text);us=S.fold_units(r);old=native_times(text,us)
 qi=max(i for i,u in enumerate(us) if old[i]<45 and u.qs==(16,) and u.name=='RESET')
 us[qi]=unit(['measure q[16] -> c[96];']);tail.append('// DETECTOR c[96]')
 init={q:max(i for i,u in enumerate(us) if old[i]<45 and u.qs==(q,) and u.name in ('RX','RESET')) for q in qs}
 uu=[];tt=[]
 for i,(u,t) in enumerate(zip(us,old)):
  uu.append(u);tt.append(t)
  if i in init.values():
   q=u.qs[0];b=140+q;assert u.name=='RX'
   uu.append(unit([f'h q[{q}];',f'measure q[{q}] -> c[{b}];',f'h q[{q}];']));tt.append(t);tail.append(f'// DETECTOR c[{b}]')
 rr={i for i,t in enumerate(tt) if t>=45};ts,R=retime(uu,tt,rr)
 emit('verify_'+'_'.join(map(str,qs)),uu,ts,tail,dict(R=R,method='verified A pivots, M-init q16; optional q1 reuse',verified_sites=qs,source=src))
