import sys, json, random, time, itertools
from pycryptosat import Solver
B=[6,26,13,11,4,23,27]; C=[12,25,19,17,5,29,28]
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def nb(q):
    r,c=divmod(q,6)
    return [rr*6+cc for rr,cc in((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<6 and 0<=cc<6]
def build(D,helpers,seed,threads=1,maxcx=None,pivfix=None):
    cells=B+C+helpers; S=set(cells)
    rows=[{B[i] for i in r} for r in ROWS]+[{C[i] for i in r} for r in ROWS]
    K=6
    rng=random.Random(seed)
    if seed: rng.shuffle(cells)
    edges=[(u,v) for u in cells for v in nb(u) if v in S]
    if seed: rng.shuffle(edges)
    s=Solver(threads=threads); s.set_seed(seed) if hasattr(s,'set_seed') else None
    n=[0]
    def nv():
        n[0]+=1; return n[0]
    p={(j,v):nv() for j in range(K) for v in cells}
    for j in range(K):
        s.add_clause([p[(j,v)] for v in cells])
        for a,b in itertools.combinations(cells,2): s.add_clause([-p[(j,a)],-p[(j,b)]])
    for v in cells:
        for a,b in itertools.combinations(range(K),2): s.add_clause([-p[(a,v)],-p[(b,v)]])
    for j in range(K-1):
        for a in range(len(cells)):
            for b in range(a+1):
                s.add_clause([-p[(j,cells[a])],-p[(j+1,cells[b])]])
    if pivfix:
        for j,v in enumerate(pivfix):
            if v is not None: s.add_clause([p[(j,v)]])
    x=[{(v,j):p[(j,v)] for v in cells for j in range(K)}]
    sel=[]
    for t in range(D):
        se={e:nv() for e in edges}; sel.append(se)
        for v in cells:
            inc=[se[e] for e in edges if v in e]
            for a,b in itertools.combinations(inc,2): s.add_clause([-a,-b])
        nx={}
        for v in cells:
            ins=[(u,v) for u in nb(v) if (u,v) in se]
            for j in range(K):
                zs=[]
                for e in ins:
                    z=nv(); a=se[e]; b=x[t][(e[0],j)]
                    s.add_clause([-z,a]); s.add_clause([-z,b]); s.add_clause([z,-a,-b]); zs.append(z)
                y=nv(); s.add_xor_clause([y,x[t][(v,j)]]+zs,False); nx[(v,j)]=y
        x.append(nx)
    A={(j,i):nv() for j in range(K) for i in range(K)}
    for v in cells:
        for j in range(K):
            terms=[A[(j,i)] for i in range(K) if v in rows[i]]
            s.add_xor_clause([x[D][(v,j)]]+terms,False)
    if maxcx is not None:
        pass
    return s,sel,p,edges,cells
def solve(D,helpers,seed,threads=1,pivfix=None):
    s,sel,p,edges,cells=build(D,helpers,seed,threads,pivfix=pivfix)
    t=time.time()
    ok,m=s.solve()
    print("D",D,"ok",ok,time.time()-t,flush=True)
    if not ok: return None
    ops=[[list(e) for e in edges if m[se[e]]] for se in sel]
    piv=[v for j in range(6) for v in cells if m[p[(j,v)]]]
    return ops,piv
if __name__=="__main__":
    D=int(sys.argv[1]); hs=eval(sys.argv[2]); seed=int(sys.argv[3]); th=int(sys.argv[4])
    r=solve(D,hs,seed,th)
    if r:
        ops,piv=r
        print(sum(len(o) for o in ops)); json.dump({"ops":ops,"pivots":piv},open(f"sat2_{D}_{seed}.json","w"))
