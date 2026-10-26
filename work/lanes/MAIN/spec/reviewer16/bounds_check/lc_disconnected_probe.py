from lc_probe import graph,orbit,canon,measure
from itertools import combinations,product
from pathlib import Path
import json
base=graph(7,[(0,2),(0,4),(0,6),(1,2),(1,5),(1,6),(3,4),(3,5),(3,6)])
cc={canon(g) for g in orbit(base)};degtypes={x[0] for x in cc}
coords=[(r,c) for r in range(3) for c in range(4) if (r,c)!=(0,0)];n=len(coords)
edges=[(i,j) for i,j in combinations(range(n),2) if abs(coords[i][0]-coords[j][0])+abs(coords[i][1]-coords[j][1])==1];a=graph(n,edges)
hits=[]
for removed in combinations(range(n),n-7):
 kept=set(range(n))-set(removed);todo=set(kept);components=[]
 while todo:
  v=todo.pop();stack=[v];component={v}
  while stack:
   u=stack.pop();nb={w for w in todo if (a[u]>>w)&1};todo-=nb;component|=nb;stack+=list(nb)
  components.append(sorted(component))
 for bases in product('XYZ',repeat=n-7):
  b=a
  for v,basis in reversed(tuple(zip(removed,bases))):b=measure(b,v,basis)
  if tuple(sorted(x.bit_count() for x in b)) in degtypes and canon(b) in cc:
   hits.append({'coords':coords,'edges':edges,'removed':removed,'bases':bases,'graph_after':b,'output_components':components});break
hits.sort(key=lambda h:len(h['output_components']),reverse=True)
Path('bounds_check/lc_disconnected_hits.json').write_text(json.dumps(hits,indent=2))
print('hit output subsets',len(hits),'max_components',len(hits[0]['output_components']) if hits else 0)
if hits:
 print(json.dumps(hits[0],indent=2));Path('bounds_check/lc_hit.json').write_text(json.dumps(hits[0],indent=2))
