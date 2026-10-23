import sys,json,collections
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR'); import poc
s={int(k):[(t,typ,frozenset(S)) for t,typ,S in v] for k,v in json.load(open('/home/jihoon/competitions/quantumn/work/lanes/DR/sched_zfirst.json')).items()}
for name,fn in [('pair',lambda:poc.build_hybrid(s,z_mode='pair')),('cat1',lambda:poc.build_hybrid(s,z_mode='cat1')),('clean',lambda:poc.build_clean(s,clean_z=True))]:
 b,_,_=fn(); E=set(tuple(qs) for t,k,kind,qs,tag in b.ops if kind=='cx'); adj={v:set() for e in E for v in e}
 for a,c in E:adj[a].add(c);adj[c].add(a)
 col={}; bad=None
 for v in adj:
  if v in col:continue
  col[v]=0; st=[v]
  while st and bad is None:
   a=st.pop()
   for z in adj[a]:
    if z in col:
     if col[z]==col[a]:bad=(a,z);break
    else:col[z]=1-col[a];st.append(z)
 print(name,b.next_q,len(E),'bip',bad is None,'bad',bad)
 if bad:
  # find odd cycle via bfs
  from collections import deque
  par={bad[0]:None};q=deque([bad[0]])
  while q:
   a=q.popleft()
   if a==bad[1]:break
   for z in adj[a]:
    if z not in par:par[z]=a;q.append(z)
  path=[]; x=bad[1]
  while x is not None:path.append(x);x=par[x]
  print(path)
