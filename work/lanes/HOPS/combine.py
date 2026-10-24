from build import *
for mode in ['advance','advance_watch','advance_watch9','advance_watch_all']:
 h,u,ts,tail,meta=read();drop={134};bit=47
 for src,dst in [(15,22),(8,21)]:
  ix=next(i for i,x in enumerate(u)if x.lines==[f'tdg q[{src}];']);u[ix]=S.Unit([f'tdg q[{dst}];'],[]);ts[ix]=44
 u[118]=S.Unit(['h q[9];','measure q[9] -> c[9];','h q[9];'],[])
 u[145]=S.Unit(['cx q[9],q[8];'],[]);u[153]=S.Unit(['cx q[8],q[9];'],[])
 for i in [121,133,144,154,145,153,161,167,168,176,184]:ts[i]-=1
 if 'watch' in mode:
  for i in [154,223]:
   q=u[i].qs[0];u[i]=S.Unit([f'measure q[{q}] -> c[{bit}];'],[]);tail.append(f'// DETECTOR c[{bit}]');bit+=1
 if mode in ['advance_watch9','advance_watch_all']:
  for q,t in ([(9,37)]if mode=='advance_watch9'else[(9,37),(15,37)]):
   u.append(S.Unit([f'measure q[{q}] -> c[{bit}];'],[]));ts.append(t);tail.append(f'// DETECTOR c[{bit}]');bit+=1
 h=[re.sub(r'creg c\[\d+\]',f'creg c[{bit}]',s)for s in h]
 pre=set(meta['prefix_unit_indices']);meta['prefix_unit_indices']=[j for j,i in enumerate(i for i in range(len(u))if i not in drop)if i in pre]
 save(mode,h,[x for i,x in enumerate(u)if i not in drop],[t for i,t in enumerate(ts)if i not in drop],tail,meta)
