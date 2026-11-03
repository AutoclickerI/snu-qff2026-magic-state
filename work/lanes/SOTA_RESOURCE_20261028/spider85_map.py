import json,collections,itertools,stim
from pathlib import Path
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028';roles=json.loads((R/'work/lanes/SOTA_20261028/tile_geometry_free2.json').read_text())['roles'];D,A,B,C=(roles[k] for k in 'DABC');allowed=set(range(36))-set(D+A);free=sorted(allowed-set(B+C));c=stim.Circuit((R/'work/lanes/SOTA_DETECT_20261028/spider_bc85.log').read_text());edges=collections.Counter()
for ins in c:
 if ins.name=='CX':
  x=[t.value for t in ins.targets_copy()]
  for a,b in zip(x[::2],x[1::2]):edges[tuple(sorted((a,b)))]+=1
def distances(a):
 d={a:0};Q=collections.deque([a])
 while Q:
  u=Q.popleft()
  for v in sorted(allowed-d.keys()):
   if abs(u//6-v//6)+abs(u%6-v%6)==1:d[v]=d[u]+1;Q.append(v)
 return d
dist={a:distances(a) for a in allowed};results=[]
for fs in itertools.permutations(free,4):
 mp=B+C+list(fs); lengths=[(a,b,count,dist[mp[a]].get(mp[b],100)) for (a,b),count in edges.items()];cost=sum(n*(1 if d==1 else 4*d-4) for a,b,n,d in lengths)
 results.append((cost,max(d for a,b,n,d in lengths),fs,lengths))
results.sort();out=[]
for cost,maxd,fs,lengths in results[:20]:out.append({'physical_cx_dirty_bridges':cost,'max_distance':maxd,'flags':fs,'distances':lengths})
(H/'spider85_map.json').write_text(json.dumps({'free_cells':free,'best':out},indent=2)+'\n');print(json.dumps(out[:3],indent=2))
