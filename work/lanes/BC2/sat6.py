import sys, json, random, time, itertools
from pycryptosat import Solver
B=[6,26,13,11,4,23,27]; C=[12,25,19,17,5,29,28]
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def nb(q):
    r,c=divmod(q,6)
    return [rr*6+cc for rr,cc in((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<6 and 0<=cc<6]
def build(D,helpers,seed,threads=1,maxcx=None,pivfix=None,rule="base"):
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
    cache = {}
    def propagate_source(src):
        t0, qs = src
        if src in cache: return cache[src]
        f={v:(True if v in qs else None) for v in cells}
        for t in range(t0,D):
            se=sel[t]; nf={}
            for v in cells:
                terms=[]
                for u in nb(v):
                    if (u,v) in se:
                        fu=f[u]
                        if fu is None: continue
                        terms.append(se[(u,v)] if fu is True else AND(se[(u,v)],fu))
                cur=f[v]
                if cur is not None and cur is not True: terms.append(cur)
                if not terms: nf[v]=cur if cur is True else None
                else:
                    y=nv(); s.add_xor_clause([y]+terms,cur is True); nf[v]=y
            f=nf
        cache[src]=f
        return f
    def par(vs):
        cs=sum(x is True for x in vs)
        vv=[x for x in vs if x is not None and x is not True]
        y=nv(); s.add_xor_clause([y]+vv,bool(cs%2)); return y
    def add_fault(sources):
        fs=[propagate_source(src) for src in sources]
        f={v:par([f[v] for f in fs]) for v in cells}
        guard=[]
        for t,qs in sources:
            if len(qs)==2: guard.append(-sel[t-1][qs])
        sb=[par([f[B[i]] for i in r]) for r in ROWS]+[par([f[q] for q in B])]
        sc=[par([f[C[i]] for i in r]) for r in ROWS]+[par([f[q] for q in C])]
        ds=[par([a,b]) for a,b in zip(sb,sc)]
        def neq(bits,val):
            return [-v if val>>i&1 else v for i,v in enumerate(bits)]
        use='robust' if rule=='pairs' and len(sources)==1 else rule
        if rule=='allpairs': use='both' if len(sources)==1 else 'base'
        if use in ('clean','clean_literal','both'):
            for v in ([f[q] for q in B] if use=='clean_literal' else sb):
                s.add_clause(guard+ds+[-v])
        if use not in ('clean','clean_literal'):
            diffs=[0]+(sorted(ft.READ_FLIPS) if use in ('robust','both') else [])
            for diff in diffs:
                for bval in range(16):
                    if ft.dangerous(bval): s.add_clause(guard+neq(ds,diff)+neq(sb,bval))

    A={(j,i):nv() for j in range(K) for i in range(K)}
    for v in cells:
        for j in range(K):
            terms=[A[(j,i)] for i in range(K) if v in rows[i]]
            s.add_xor_clause([x[D][(v,j)]]+terms,False)
    # CNOTs preserve the six input columns' independence. State this implied
    # fact explicitly so the SAT solver need not rediscover it through D layers.
    Ai={(i,j):nv() for i in range(K) for j in range(K)}
    for j in range(K):
        for l in range(K):
            terms=[AND(Ai[(j,i)],A[(i,l)]) for i in range(K)]
            s.add_xor_clause(terms,j==l)
    if maxcx is not None:
        xs=[v for se in sel for v in se.values()]; K=maxcx
        # sequential counter: at most K of xs
        prev=[nv() for _ in range(K)]
        s.add_clause([-xs[0],prev[0]]); 
        for j in range(1,K): s.add_clause([-prev[j]])
        for i in range(1,len(xs)):
            cur=[nv() for _ in range(K)]
            s.add_clause([-xs[i],cur[0]]); s.add_clause([-prev[0],cur[0]])
            for j in range(1,K):
                s.add_clause([-xs[i],-prev[j-1],cur[j]]); s.add_clause([-prev[j],cur[j]])
            s.add_clause([-xs[i],-prev[K-1]])
            prev=cur
    return s,sel,p,edges,cells,add_fault
import ft
def solve(D,helpers,seed,threads=1,pivfix=None,K=None,rule="base",seconds=180,initial=None,free_layers=None,fix_pivots=False):
    started=time.monotonic()
    s,sel,p,edges,cells,add_fault=build(D,helpers,seed,threads,maxcx=K,pivfix=pivfix,rule=rule)
    added=set(); it=0
    if initial is not None:
        if fix_pivots:
            for v in cells:
                if v in initial['pivots']: s.add_clause([p[(j,v)] for j in range(6)])
                else:
                    for j in range(6): s.add_clause([-p[(j,v)]])
        for t,layer in enumerate(initial['ops']):
            if free_layers is None or t in free_layers: continue
            active={tuple(e) for e in layer}
            for e,var in sel[t].items(): s.add_clause([var if e in active else -var])
        for fault in ft.faults(initial,cells,rule,limit=96):
            add_fault(fault); added.add(fault)
    while True:
        remaining=seconds-(time.monotonic()-started)
        if remaining<=0: return 'TIMEOUT',None,time.monotonic()-started,it,len(added)
        ok,m=s.solve(time_limit=remaining)
        it+=1
        if ok is not True:
            return ('UNSAT' if ok is False else 'TIMEOUT'),None,time.monotonic()-started,it,len(added)
        ops=[[list(e) for e in edges if m[se[e]]] for se in sel]
        piv=[v for j in range(6) for v in cells if m[p[(j,v)]]]
        d={'ops':ops,'pivots':piv}
        bad=[f for f in ft.faults(d,cells,rule,limit=128) if f not in added]
        print('iter',it,'bad',len(bad),'added',len(added),'seconds',time.monotonic()-started,flush=True)
        if not bad:
            assert not ft.faults(d,cells,rule)
            return 'SAT',d,time.monotonic()-started,it,len(added)
        for f in bad: add_fault(f); added.add(f)

if __name__=='__main__':
    import argparse
    from pathlib import Path
    ap=argparse.ArgumentParser()
    ap.add_argument('--depth',type=int,required=True)
    ap.add_argument('--cap',type=int,required=True)
    ap.add_argument('--seed',type=int,default=1)
    ap.add_argument('--rule',choices=['base','clean_literal','clean','robust','pairs','both','allpairs'],required=True)
    ap.add_argument('--helpers',default='18,24,30,31,32,33,34,35')
    ap.add_argument('--seconds',type=float,default=180)
    ap.add_argument('--initial')
    ap.add_argument('--free')
    ap.add_argument('--fix-pivots',action='store_true')
    ap.add_argument('--out',required=True)
    a=ap.parse_args()
    init=json.load(open(a.initial)) if a.initial else None
    free=[int(x) for x in a.free.split(',')] if a.free else None
    hs=[int(x) for x in a.helpers.split(',') if x]
    status,d,elapsed,iters,nfaults=solve(a.depth,hs,a.seed,K=a.cap,rule=a.rule,seconds=a.seconds,initial=init,free_layers=free,fix_pivots=a.fix_pivots)
    receipt=dict(vars(a),status=status,elapsed=elapsed,iters=iters,constraints=nfaults)
    if d:
        receipt['cx']=sum(map(len,d['ops']))
        Path(a.out+'.prep.json').write_text(json.dumps(d))
    Path(a.out+'.receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt),flush=True)
