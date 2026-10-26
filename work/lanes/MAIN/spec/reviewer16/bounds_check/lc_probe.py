from collections import deque
from itertools import combinations, permutations, product
import json,time

def graph(n, edges):
    a=[0]*n
    for u,v in edges: a[u]|=1<<v;a[v]|=1<<u
    return tuple(a)

def lc(a,v):
    b=list(a); ns=[u for u in range(len(a)) if a[v]>>u&1]
    for u,w in combinations(ns,2): b[u]^=1<<w;b[w]^=1<<u
    return tuple(b)

def orbit(a):
    seen={a};todo=deque([a])
    while todo:
        g=todo.popleft()
        for v in range(len(g)):
            h=lc(g,v)
            if h not in seen: seen.add(h);todo.append(h)
    return seen

def canon(a):
    deg=[g.bit_count() for g in a]
    groups=[[i for i in range(len(a)) if deg[i]==d] for d in sorted(set(deg))]
    best=None
    for parts in product(*(permutations(g) for g in groups)):
        p=sum(parts,()); val=0
        for i,j in combinations(range(len(a)),2): val=(val<<1)|(a[p[i]]>>p[j]&1)
        if best is None or val<best:best=val
    return tuple(sorted(deg)),best

def delete(a,v):
    kept=[u for u in range(len(a)) if u!=v]
    return tuple(sum(((a[u]>>w)&1)<<j for j,w in enumerate(kept)) for u in kept)

def measure(a,v,basis):
    if basis=='Y':a=lc(a,v)
    if basis=='X':
        if not a[v]:return delete(a,v)
        u=(a[v]&-a[v]).bit_length()-1
        a=lc(lc(lc(a,u),v),u)
    return delete(a,v)

if __name__=='__main__':
    st=time.time()
    base=graph(7,[(0,2),(0,4),(0,6),(1,2),(1,5),(1,6),(3,4),(3,5),(3,6)])
    oo=orbit(base)
    cc={canon(a) for a in oo}
    print('orbit',len(oo),'isoclasses',len(cc),'minedges',min(sum(x.bit_count() for x in g)//2 for g in oo),'time',time.time()-st,flush=True)
    json.dump({'orbit':[list(x) for x in oo],'canonical':list(cc)},open('bounds_check/lc_orbit.json','w'))
    grid_edges=[(i,j) for i,j in combinations(range(9),2) if abs(i//3-j//3)+abs(i%3-j%3)==1]
    grid=graph(9,grid_edges)
    hits=[]
    for v,w in combinations(range(9),2):
        for bv,bw in product('XYZ',repeat=2):
            end=measure(measure(grid,w,bw),v,bv)
            if canon(end) in cc:hits.append((v,w,bv,bw))
    print('3x3 full grid measured 2',len(hits),hits[:10],flush=True)
    degtypes={x[0] for x in cc}
    from pathlib import Path
    for coords in [[(r,c) for r in range(2) for c in range(5)],[(r,c) for r in range(3) for c in range(4) if (r,c) not in [(0,0),(0,3)]],[(r,c) for r in range(3) for c in range(4) if (r,c)!=(0,0)]]:
        n=len(coords); edges=[(i,j) for i,j in combinations(range(n),2) if abs(coords[i][0]-coords[j][0])+abs(coords[i][1]-coords[j][1])==1]; a=graph(n,edges)
        hit=None;count=0
        for removed in combinations(range(n),n-7):
            for bases in product('XYZ',repeat=n-7):
                b=a
                for v,basis in reversed(tuple(zip(removed,bases))): b=measure(b,v,basis)
                count+=1
                if tuple(sorted(x.bit_count() for x in b)) in degtypes and canon(b) in cc:
                    hit={'coords':coords,'edges':edges,'removed':removed,'bases':bases,'graph_after':b,'count':count};break
            if hit:break
        print('grid',n,'hit',hit,'count',count,flush=True)
        if hit: Path('bounds_check/lc_hit.json').write_text(json.dumps(hit,indent=2));break
