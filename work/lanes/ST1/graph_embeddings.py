"""All injective nearest-neighbour embeddings of a fixed seven-wire CX graph."""
import functools
@functools.lru_cache(None)
def embeddings(edges):
 adj=[set()for _ in range(7)]
 for a,b in edges:adj[a].add(b);adj[b].add(a)
 grid=[{p for p in range(36)if abs(q//6-p//6)+abs(q%6-p%6)==1}for q in range(36)]
 order=[]
 while len(order)<7:order.append(max((i for i in range(7)if i not in order),key=lambda i:(len(adj[i]&set(order)),len(adj[i]))))
 path=[-1]*7;rows=[]
 def rec(j,used):
  if j==7:rows.append(tuple(path));return
  v=order[j];ns=[n for n in adj[v]if path[n]>=0];cand=set(range(36))if not ns else set.intersection(*(grid[path[n]]for n in ns))
  for p in cand-used:path[v]=p;rec(j+1,used|{p});path[v]=-1
 rec(0,set());return rows
