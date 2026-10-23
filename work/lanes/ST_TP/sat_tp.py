import sys, json, random, time, itertools
from pycryptosat import Solver
import os
_L=json.load(open(os.environ['LAY'])); B=_L['b']; C=_L['c']
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
    # fault propagation: X fault at (cell q, time t), all copies
    def xor3(vs):
        y=nv(); s.add_xor_clause([y]+vs,False); return y
    def AND(a,b):
        z=nv(); s.add_clause([-z,a]); s.add_clause([-z,b]); s.add_clause([z,-a,-b]); return z
    def add_fault(t0,q):
        f={v:None for v in cells}   # None = const 0
        f[q]=True                     # const 1
        for t in range(t0,D):
            se=sel[t]; nf={}
            for v in cells:
                terms=[]
                for u in nb(v):
                    if (u,v) in se:
                        fu=f[u]
                        if fu is None: continue
                        if fu is True: terms.append(se[(u,v)])
                        else: terms.append(AND(se[(u,v)],fu))
                cur=f[v]
                if cur is None:
                    if not terms: nf[v]=None
                    elif len(terms)==1: nf[v]=terms[0]
                    else: y=nv(); s.add_xor_clause([y]+terms,False); nf[v]=y
                elif cur is True:
                    if not terms: nf[v]=True
                    else:
                        y=nv(); s.add_xor_clause([y]+terms,True); nf[v]=y   # y = 1 ^ terms
                else:
                    y=nv(); s.add_xor_clause([y,cur]+terms,False); nf[v]=y
            f=nf
        # final constraint on B,C
        def bits(blk,r):
            return [f[blk[i]] for i in r]
        def par(vs):
            cs=sum(1 for x in vs if x is True); vv=[x for x in vs if x not in (None,True)]
            y=nv()
            if vv: s.add_xor_clause([y]+vv,bool(cs%2))
            else: s.add_clause([y] if cs%2 else [-y])
            return y
        sB=[par(bits(B,r)) for r in ROWS]; sC=[par(bits(C,r)) for r in ROWS]
        pB=par([f[b] for b in B])
        d=[]
        for a,b in zip(sB,sC):
            y=nv(); s.add_xor_clause([y,a,b],False); d.append(y)
        nz=nv()
        s.add_clause([-nz]+sB)
        for a in sB: s.add_clause([nz,-a])
        s.add_clause(d+[-nz,pB]); s.add_clause(d+[nz,-pB])

    A={(j,i):nv() for j in range(K) for i in range(K)}
    for v in cells:
        for j in range(K):
            terms=[A[(j,i)] for i in range(K) if v in rows[i]]
            s.add_xor_clause([x[D][(v,j)]]+terms,False)
    if maxcx is not None:
        pass
    return s,sel,p,edges,cells,add_fault
import ft_tp as ft
def solve(D,helpers,seed,threads=1,pivfix=None):
    s,sel,p,edges,cells,add_fault=build(D,helpers,seed,threads,pivfix=pivfix)
    added=set(); t=time.time(); it=0
    while True:
        ok,m=s.solve()
        it+=1
        if not ok:
            print("D",D,"UNSAT",time.time()-t,"iters",it,flush=True); return None
        ops=[[list(e) for e in edges if m[se[e]]] for se in sel]
        piv=[v for j in range(6) for v in cells if m[p[(j,v)]]]
        bad=[(a,b) for a,b,_ in ft.faults({"ops":ops,"pivots":piv},cells) if (a,b) not in added]
        print("iter",it,"bad",len(bad),"added",len(added),time.time()-t,flush=True)
        if not bad: return ops,piv
        for a,b in bad: add_fault(a,b); added.add((a,b))
if __name__=="__main__":
    D=int(sys.argv[1]); hs=eval(sys.argv[2]); seed=int(sys.argv[3]); th=int(sys.argv[4]); tag=sys.argv[5]
    r=solve(D,hs,seed,th)
    if r:
        ops,piv=r
        print(sum(len(o) for o in ops)); json.dump({"ops":ops,"pivots":piv},open(f"sat_{tag}_{D}_{seed}.json","w"))
