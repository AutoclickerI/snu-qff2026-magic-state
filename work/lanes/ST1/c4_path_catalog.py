"""Exact geometric lower bounds for a stationary path B and four moving parity targets."""
from common import *
import redesign as rd,itertools,collections
CHECKS=[[0,1,2],[0,3,4],[0,5,6],[1,3,5]];NB={q:{p for u,p in rd.ED if u==q}for q in range(36)}
logical_path=[1,0,2,3,4,5,6];paths=[]
def dfs(path):
 if len(path)==7:
  paths.append(path)
  return
 if len(path)>1 and len(NB[path[-1]])<4:return
 for q in NB[path[-1]]-set(path):
  if len(NB[q])>=3 and not(NB[q]&set(path[:-1])):dfs(path+[q])
for q in range(36):
 if len(NB[q])>=3:dfs([q])
seen=set();rows=[];hist=collections.Counter();best=None
for path in paths:
 occupied=set(path);dist={};routes={}
 for q in set(range(36))-occupied:
  d={q:0};prev={};todo=collections.deque([q])
  while todo:
   u=todo.popleft()
   for v in NB[u]-occupied:
    if v not in d:d[v]=d[u]+1;prev[v]=u;todo.append(v)
  dist[q]=d
  for t in d:
   arr=[t]
   while arr[-1]!=q:arr.append(prev[arr[-1]])
   routes[q,t]=arr[::-1]
 loc=[None]*7
 for i,q in zip(logical_path,path):loc[i]=q
 costs={};details={}
 for triple in itertools.combinations(range(7),3):
  win=None
  for order in itertools.permutations(triple):
   for cells in itertools.product(*(sorted(NB[loc[i]]-occupied)for i in order)):
    u,v,w=cells
    if v not in dist[u]or w not in dist[v]:continue
    price=dist[u][v]+dist[v][w]
    if win is None or price<win[0]:win=(price,order,cells,routes[u,v]+routes[v,w][1:])
  costs[triple]=99 if win is None else win[0];details[triple]=win
 for perm in rd.AUT:
  triples=[tuple(sorted(perm[i]for i in r))for r in CHECKS];vals=[costs[t]for t in triples];key=(max(vals),sum(vals));hist[key[0]]+=1
  if best is None or key<best:
   best=key;row=dict(bound_max_moves=key[0],bound_sum_moves=key[1],native_b=loc,permutation=perm,logical_b=[loc[i]for i in perm],check_routes=[details[t]for t in triples],scope='Shortest checker paths avoid stationary B but ignore A/D/other checkers and timing; lower bound only. Native B path encoder fixed to schain11; all code automorphisms included.');rows.append(row);print(json.dumps(row),flush=True)
(H/'c4_path_catalog.json').write_text(json.dumps(dict(path_embeddings=len(paths),best=rows[-1],improvements=rows,histogram=dict(hist)),indent=2));append_result('c4_stationary_path_checker_bound',dict(path_embeddings=len(paths),best=best,histogram=dict(hist)),rows[-1]['scope'])
