import sys,itertools,json,time
from pathlib import Path
from topology import DATA,W4,TRIPLES,E,adj,HERE
sets={s:i for i,s in enumerate(W4)};basis=set(TRIPLES)
opts=[[q]+[v for v in range(36) if v not in DATA and adj(q,v)] for q in DATA]
routes=0;withz=0;afterz=set();afterx=set();available=set();found=[]
t0=time.time()
for pos in itertools.product(*opts):
 if len(set(pos))<7:continue
 routes+=1
 free=set(range(36))-set(pos); edges=[e for e in E if set(e)<=free]
 direct={e:frozenset(i for i,q in enumerate(pos) if any(adj(q,r) for r in e)) for e in edges}
 zopts={k:[e for e in edges if W4[k]<=direct[e]] for k in range(7)}
 zts=[zt for zt in TRIPLES if all(zopts[k] for k in zt)]
 if not zts:continue
 withz+=1
 reach={e:frozenset(i for i,q in enumerate(pos) if i in direct[e] or any(adj(q,c) and any(adj(c,r) for r in e) for c in free-set(e))) for e in edges}
 for zt in zts:
  for xt in TRIPLES:afterz.add((xt,zt))
  for es in itertools.product(*(zopts[k] for k in zt)):
   if len(set(sum((list(e) for e in es),[])))!=6:continue
   xopts=[[k for k in range(7) if W4[k]<=reach[e]] for e in es]
   for xs in itertools.product(*xopts):
    xt=tuple(sorted(xs))
    if xt not in basis:continue
    afterx.add((xt,zt));occupied=set(pos)|set(sum((list(e) for e in es),[]))
    # Every required X leaf must be placeable without sharing another cat.
    needs=[]
    for tile,(x,e) in enumerate(zip(xs,es)):
     for i in W4[x]-direct[e]:
      cs=[(c,r) for c in range(36) if c not in occupied for r in e if adj(pos[i],c) and adj(c,r)]
      needs.append((tile,i,cs))
    ways=[]
    for ls in itertools.product(*(cs for _,_,cs in needs)):
     if len(set(c for c,r in ls))<len(ls):continue
     # Destinations and Bell cells may not obstruct required source->destination hops.
     # A vacated source may be used after its own hop, a valid temporal dependency.
     ways.append([dict(tile=t,data=i,cell=c,parent=r) for (t,i,_),(c,r) in zip(needs,ls)])
    if not ways:continue
    available.add((xt,zt))
    for leaves in ways:
     found.append(dict(pos=pos,xs=xs,zs=zt,bells=es,leaves=leaves,moves=sum(a!=b for a,b in zip(pos,DATA))))
print('DONE',routes,withz,len(afterz),len(afterx),len(available),len(found),time.time()-t0,flush=True)
found.sort(key=lambda r:(r['moves'],len(r['leaves'])))
r=dict(total_pairs=784,routes=routes,layouts_with_Z_basis=withz,pairs_after_Z_adjacency=len(afterz),pairs_after_X_adjacency=len(afterx),pairs_after_ancilla=len(available),physical_placements=len(found),pairs=[list(p) for p in sorted(available)],layouts=found)
(HERE/'relocations.json').write_text(json.dumps(r,indent=2))
