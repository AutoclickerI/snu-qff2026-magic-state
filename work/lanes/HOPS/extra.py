from build import *
for mask in range(1,16):
 h,u,ts,tail,meta=read();bit=47;original_ts=list(ts)
 for j,q,step in [(3,16,41),(2,15,38),(1,8,38),(0,15,33)]:
  if not mask>>j&1:continue
  ix=next(i for i,(x,t)in enumerate(zip(u,original_ts))if t==step and x.lines[0]==f'reset q[{q}];')
  if u[ix].name=='RX':
   # Monitor the vacated |0> one step before the existing |+> reset.
   u.append(S.Unit([f'measure q[{q}] -> c[{bit}];'],[]));ts.append(step)
   # Shift the RX and all later gates globally by one where needed.
   ts=[t+1 if t>=step and i!=len(ts)-1 else t for i,t in enumerate(ts)]
  else:u[ix]=S.Unit([f'measure q[{q}] -> c[{bit}];'],[])
  tail.append(f'// DETECTOR c[{bit}]');bit+=1
 h=[re.sub(r'creg c\[\d+\]',f'creg c[{bit}]',s)for s in h]
 save(f'watch_{mask}',h,u,ts,tail,dict(meta,watch_mask=mask))
