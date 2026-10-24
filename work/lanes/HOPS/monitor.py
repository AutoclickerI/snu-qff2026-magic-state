from build import *
for name,early,late_t in [('watch9',False,False),('hop_early',True,False),('hop_early_t',True,True)]:
 h,u,ts,tail,meta=read();bit=47
 if early:
  for i in [112,118,116,132,117,121,133,144,154,134,145,153,161,167,168,176,184]:ts[i]-=1
  if late_t:
   for i,d in [(117,22),(132,21)]:u[i]=S.Unit([f'tdg q[{d}];'],[]);ts[i]=44
 for i in [154,193,223]:
  q=u[i].qs[0];u[i]=S.Unit([f'measure q[{q}] -> c[{bit}];'],[]);tail.append(f'// DETECTOR c[{bit}]');bit+=1
 for q,t in ([(9,37),(15,37)]if early else[(9,37)]):
  u.append(S.Unit([f'measure q[{q}] -> c[{bit}];'],[]));ts.append(t);tail.append(f'// DETECTOR c[{bit}]');bit+=1
 h=[re.sub(r'creg c\[\d+\]',f'creg c[{bit}]',s)for s in h]
 save(name,h,u,ts,tail,meta)
