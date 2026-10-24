from common import *
from variants import retime
for qs in [(9,),(15,),(9,15),(1,2,9,15)]:
 h,us,tail,old,meta,init,ai=base();uu=[];tt=[]
 for i,(u,t) in enumerate(zip(us,old)):
  uu.append(u);tt.append(t)
  if i in init.values() and u.qs[0] in qs:
   q=u.qs[0];assert u.name=='RX';b=100+q
   uu.append(unit([f'h q[{q}];',f'measure q[{q}] -> c[{b}];',f'h q[{q}];']));tt.append(t)
   tail.append(f'// DETECTOR c[{b}]')
 rr={i for i,t in enumerate(tt) if t>=45};ts,R=retime(uu,tt,rr)
 emit('pivot_'+'_'.join(map(str,qs)),uu,ts,tail,dict(R=R,method='RX then MX postselection on A pivots',sites=qs))
