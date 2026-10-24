"""Exhaustive small-graph embeddings and the prefix's D4 symmetry classes."""
from co_design import *

def embeddings(edges):
 adj={i:set() for i in range(7)};nb={i:set() for i in range(36)}
 for u,v in edges:adj[u].add(v);adj[v].add(u)
 for u,v in EDGES:nb[u].add(v)
 out=[]
 def rec(mp):
  if len(mp)==7:out.append([mp[i] for i in range(7)]);return
  u=max((u for u in adj if u not in mp),key=lambda u:(len(adj[u]&mp.keys()),len(adj[u]),-u))
  vs=set(range(36))-set(mp.values())
  for n in adj[u]&mp.keys():vs&=nb[mp[n]]
  for v in sorted(vs):rec(dict(mp,**{})|{u:v})
 rec({});return out

def global_d4(q,k):
 r,c=divmod(q,6)
 rr,cc=[(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
 return 6*rr+cc

def main():
 out={}; reps={(r,c):transform(0,r,c) for r in range(3) for c in range(2)};classes=[]
 for k in range(8):
  hh,ww=(4,5) if k<4 else (5,4)
  for r in range(7-hh):
   for c in range(7-ww):
    mp=transform(k,r,c);found=[]
    for (rr,cc),rp in reps.items():
     for g in range(8):
      if all(global_d4(rp[q],g)==mp[q] for q in P0):found.append([rr,cc,g])
    assert len(found)==1,found
    classes.append(dict(sym=k,row=r,col=c,representative=found[0][:2],global_symmetry=found[0][2]))
 standard=[(0,2),(1,6),(3,5),(0,4),(1,2),(3,6),(0,6),(1,5),(3,4)]
 for option in ['standard9','l5_11','l5_12']:
  edges=standard if option=='standard9' else [e for L in template(option,'a')['ops'] for e in L]
  edges=sorted({tuple(sorted(e)) for e in edges});e=embeddings(edges)
  out[option]=dict(edges=edges,embeddings=len(e),status='INFEASIBLE' if not e else 'EXHAUSTIVE_EMBEDDINGS',binding='encoder CX graph has no injective nearest-neighbor embedding' if not e else None)
  if e:(HERE/(option+'.embeddings.json')).write_text(json.dumps(e))
 (HERE/'geometry.json').write_text(json.dumps(dict(options=out,prefix_embeddings=classes),indent=1));print(out,flush=True)

if __name__=='__main__':main()
