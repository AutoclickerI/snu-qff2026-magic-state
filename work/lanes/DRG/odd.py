import sys,json,collections
sys.path.insert(0,'/home/jihoon/competitions/quantumn/ work/lanes/DRG'.replace(' ','') )
import poc_grid as p
s={int(k):[(t,typ,frozenset(S)) for t,typ,S in v] for k,v in json.load(open('/home/jihoon/competitions/quantumn/work/lanes/DR/sched_zfirst.json')).items()}
b,_,_=p.build_clean(s,clean_z=True);E=set(tuple(qs) for t,k,kind,qs,tag in b.ops if kind=='cx');adj={}
for a,c in E:adj.setdefault(a,set()).add(c);adj.setdefault(c,set()).add(a)
col={};par={};bad=None
for v in adj:
 if v in col:continue
 col[v]=0;par[v]=None;st=[v]
 while st and bad is None:
  a=st.pop()
  for z in adj[a]:
   if z in col:
    if col[z]==col[a]:bad=(a,z);break
   else:col[z]=1-col[a];par[z]=a;st.append(z)
print('bad',bad)
from collections import deque
q=deque([bad[0]]);pp={bad[0]:None}
while q:
 a=q.popleft()
 for z in adj[a]:
  if {a,z}==set(bad):continue
  if z not in pp:pp[z]=a;q.append(z)
x=bad[1];path=[]
while x is not None:path.append(x);x=pp[x]
print(path)
for x in path:print(x,[op for op in b.ops if x in op[3]])
