"""Joint native-path encoder labelling and C4 checker-route lower bounds.
All 30 Steane label classes (840 distinct four-check bases) are included.
"""
from common import *
import redesign as rd,itertools,collections
CHECKS=[[0,1,2],[0,3,4],[0,5,6],[1,3,5]];NB={q:{p for u,p in rd.ED if u==q}for q in range(36)}
def rowkey(rows):
 rr=list(rows)
 for i in range(3):
  j=min(range(i,3),key=lambda j:(rr[j]&-rr[j]).bit_length());rr[i],rr[j]=rr[j],rr[i];b=rr[i]&-rr[i]
  for j in range(3):
   if j!=i and rr[j]&b:rr[j]^=rr[i]
 return sum(r<<(7*i)for i,r in enumerate(rr))
ref=[5,0,1,2,3,4,6];tpl=json.loads((H/'inputs/path_encoder_classes.json').read_text());lookup={rowkey([sum(1<<t['label_to_shape'][i]for i in r)for r in rd.ROWS]):t for t in tpl};perms={}
for p in itertools.permutations(range(7)):
 triples=tuple(tuple(sorted(p[i]for i in r))for r in CHECKS);family=tuple(sorted(triples))
 if family in perms:continue
 t=lookup[rowkey([sum(1<<ref[p[i]]for i in r)for r in rd.ROWS])];perms[family]=(p,triples,t)
assert len(perms)==840,len(perms)
paths=[]
def dfs(path):
 if len(path)==7:paths.append(path);return
 if len(path)>1 and len(NB[path[-1]])<4:return
 for q in NB[path[-1]]-set(path):
  if len(NB[q])>=3 and not(NB[q]&set(path[:-1])):dfs(path+[q])
for q in range(36):
 if len(NB[q])>=3:dfs([q])
best={12:None,14:None};rows={12:[],14:[]};hist={12:collections.Counter(),14:collections.Counter()}
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
 details={}
 for triple in itertools.combinations(range(7),3):
  win=None
  for order in itertools.permutations(triple):
   for cs in itertools.product(*(sorted(NB[path[i]]-occupied)for i in order)):
    u,v,w=cs
    if v not in dist[u]or w not in dist[v]:continue
    price=dist[u][v]+dist[v][w]
    if win is None or price<win[0]:win=(price,order,cs,routes[u,v]+routes[v,w][1:])
  details[triple]=win
 for p,triples,t in perms.values():
  vals=[99 if details[z]is None else details[z][0]for z in triples];key=(max(vals),sum(vals),t['cx'],t['depth'])
  for limit in[12,14]:
   if t['cx']>limit:continue
   hist[limit][key[0]]+=1
   if best[limit]is not None and key>=best[limit]:continue
   best[limit]=key;inv={q:i for i,q in enumerate(p)};l2s=t['label_to_shape'];conv=lambda i:inv[ref.index(l2s[i])];zero=dict(ops=[[conv(u),conv(v)]for u,v in t['zero']['ops']],pivots=[conv(i)for i in t['zero']['pivots']]);check_routes=[]
   for z in triples:
    detail=details[z];check_routes.append(None if detail is None else[detail[0],[inv[i]for i in detail[1]],list(detail[2]),detail[3]])
   out=dict(bound_max_moves=key[0],bound_sum_moves_at_minmax=key[1],encoder_cx=t['cx'],encoder_depth=t['depth'],encoder_source=t['id'],encoder_zero=zero,native_b=[path[p[i]]for i in range(7)],permutation=list(range(7)),logical_b=[path[p[i]]for i in range(7)],check_routes=check_routes,scope='All path embeddings and all Steane code label classes under the stated CX cap; checker paths avoid B but omit A/D/other-checker occupancy. Not a bound for early B-cell reuse.')
   rows[limit].append(out);dest=H/f'path_code_cx{limit}_best.json';tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(out,indent=2));tmp.replace(dest);print(json.dumps(dict(limit=limit,**out)),flush=True)
summary=dict(path_embeddings=len(paths),check_bases=len(perms),best={k:rows[k][-1]for k in rows},histogram={k:dict(v)for k,v in hist.items()});(H/'path_code_catalog.json').write_text(json.dumps(summary,indent=2));append_result('path_code_catalog',dict(path_embeddings=len(paths),check_bases=len(perms),best=best,histogram=summary['histogram']),summary['best'][14]['scope'])
