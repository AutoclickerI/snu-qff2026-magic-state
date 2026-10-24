#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Reverse-endpoint B+C synthesis with the BC2 clean/FT CEGAR predicate.

The target rows are the six B/C stabilizer generators.  CNOT layers are
propagated backwards from this target; at the input endpoint at most six
nonzero rows are required, which is exactly a product of six |+> inputs and
|0> elsewhere (CNOTs preserve rank).  Candidate circuits are then checked by
the same single-fault predicate as BC2, and every counterexample is added to
the CryptoMiniSat model before the next solve.
"""
import argparse, itertools, json, os, random, time
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[k] = '1'
from pathlib import Path
from pycryptosat import Solver
import ft

B = [6, 26, 13, 11, 4, 23, 27]
C = [12, 25, 19, 17, 5, 29, 28]
ROWS = [[0,2,4,6], [1,2,5,6], [3,4,5,6]]

def nb(q):
    r,c = divmod(q, 6)
    return [rr*6+cc for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1))
            if 0 <= rr < 6 and 0 <= cc < 6]

def target_rows(cells):
    x = {q: 0 for q in cells}
    for j, block in enumerate((B,C)):
        for k,row in enumerate(ROWS):
            for i in row:
                x[block[i]] |= 1 << (3*j+k)
    return x

def build(depth, cells, seed, threads=1, maxcx=None, rule='base', basis=False):
    cells = list(dict.fromkeys(cells)); S = set(cells)
    rng = random.Random(seed)
    edges = [(u,v) for u in cells for v in nb(u) if v in S]
    rng.shuffle(edges)
    K = 6; s = Solver(threads=threads)
    if hasattr(s, 'set_seed'):
        s.set_seed(seed)
    def nv():
        nv.n += 1; return nv.n
    nv.n = 0
    sel = []
    for t in range(depth):
        se = {e:nv() for e in edges}; sel.append(se)
        for q in cells:
            inc = [se[e] for e in edges if q in e]
            for a,b in itertools.combinations(inc,2):
                s.add_clause([-a,-b])
    # x[t][q,b] is the coefficient of target generator b on physical row q.
    x = [{(q,b):nv() for q in cells for b in range(K)} for _ in range(depth+1)]
    # The six target generators may be changed by any invertible basis
    # transformation.  This is essential: a sparse product endpoint can be
    # reached by a different generator basis even though the stabilizer space
    # is unchanged.  Encode x[D] = target_rows * A and A*Ai = I over GF(2).
    tar = target_rows(cells)
    if basis:
        A = {(i,j):nv() for i in range(K) for j in range(K)}
        Ai = {(i,j):nv() for i in range(K) for j in range(K)}
        def and_var(a,b):
            z=nv(); s.add_clause([-z,a]); s.add_clause([-z,b]); s.add_clause([z,-a,-b]); return z
        for i in range(K):
            for l in range(K):
                terms=[and_var(Ai[(i,j)],A[(j,l)]) for j in range(K)]
                s.add_xor_clause(terms, i == l)
        for q in cells:
            for b in range(K):
                terms=[A[(i,b)] for i in range(K) if (tar[q] >> i) & 1]
                if terms: s.add_xor_clause([x[depth][q,b], *terms], False)
                else: s.add_clause([-x[depth][q,b]])
    else:
        for q in cells:
            for b in range(K):
                s.add_clause([x[depth][q,b] if (tar[q] >> b) & 1 else -x[depth][q,b]])
    # Reverse each forward CNOT layer: row[v] ^= row[u].
    for t in range(depth-1, -1, -1):
        for v in cells:
            incoming = [(u,w) for (u,w) in edges if w == v]
            for b in range(K):
                zs = []
                for u,w in incoming:
                    z = nv(); a = sel[t][(u,w)]; y = x[t+1][(u,b)]
                    s.add_clause([-z,a]); s.add_clause([-z,y]); s.add_clause([z,-a,-y])
                    zs.append(z)
                if zs:
                    s.add_xor_clause([x[t][(v,b)], x[t+1][(v,b)], *zs], False)
                else:
                    s.add_xor_clause([x[t][(v,b)], x[t+1][(v,b)]], False)
    # At most six nonzero input rows.  Rank is six by invertibility of CNOTs,
    # so these rows are automatically an independent six-pivot |+> input.
    nz = {}
    for q in cells:
        z = nv(); nz[q] = z
        bits = [x[0][q,b] for b in range(K)]
        for y in bits: s.add_clause([-y,z])
        s.add_clause([-z, *bits])
    for qs in itertools.combinations(cells, 7):
        s.add_clause([-nz[q] for q in qs])
    if maxcx is not None:
        xs = [v for se in sel for v in se.values()]
        # Sequential counter encoding, copied in spirit from BC2/sat6.py.
        if maxcx < len(xs):
            prev = [nv() for _ in range(maxcx)]
            s.add_clause([-xs[0], prev[0]])
            for j in range(1,maxcx): s.add_clause([-prev[j]])
            for i in range(1,len(xs)):
                cur = [nv() for _ in range(maxcx)]
                s.add_clause([-xs[i], cur[0]]); s.add_clause([-prev[0],cur[0]])
                for j in range(1,maxcx):
                    s.add_clause([-xs[i],-prev[j-1],cur[j]])
                    s.add_clause([-prev[j],cur[j]])
                s.add_clause([-xs[i],-prev[maxcx-1]])
                prev = cur
    cache = {}
    def AND(a,b):
        z=nv(); s.add_clause([-z,a]); s.add_clause([-z,b]); s.add_clause([z,-a,-b]); return z
    def propagate_source(src):
        if src in cache: return cache[src]
        t0, qs = src
        f = {v:(True if v in qs else None) for v in cells}
        for t in range(t0, depth):
            nf = {}
            for v in cells:
                terms=[]
                for u in nb(v):
                    if (u,v) in sel[t]:
                        fu=f[u]
                        if fu is None: continue
                        terms.append(sel[t][(u,v)] if fu is True else AND(sel[t][(u,v)],fu))
                cur=f[v]
                if cur is not None and cur is not True: terms.append(cur)
                if not terms: nf[v] = cur if cur is True else None
                else:
                    y=nv(); s.add_xor_clause([y,*terms],cur is True); nf[v]=y
            f=nf
        cache[src]=f; return f
    def par(vs):
        cs=sum(v is True for v in vs); vv=[v for v in vs if v is not None and v is not True]
        if not vv: return bool(cs & 1)
        y=nv(); s.add_xor_clause([y,*vv],bool(cs & 1)); return y
    def add_fault(sources):
        fs=[propagate_source(src) for src in sources]
        f={v:par([g[v] for g in fs]) for v in cells}; guard=[]
        for t,qs in sources:
            if len(qs)==2: guard.append(-sel[t-1][qs])
        sb=[par([f[B[i]] for i in r]) for r in ROWS]+[par([f[q] for q in B])]
        sc=[par([f[C[i]] for i in r]) for r in ROWS]+[par([f[q] for q in C])]
        ds=[par([a,b]) for a,b in zip(sb,sc)]
        use = 'robust' if rule == 'pairs' and len(sources)==1 else rule
        if rule == 'allpairs': use = 'both' if len(sources)==1 else 'base'
        if use in ('clean','clean_literal','both'):
            vals = [f[q] for q in B] if use == 'clean_literal' else sb
            for v in vals: s.add_clause(guard + ds + [-v])
        if use not in ('clean','clean_literal'):
            diffs=[0] + sorted(ft.READ_FLIPS) if use in ('robust','both') else [0]
            for diff in diffs:
                for bval in range(16):
                    if ft.dangerous(bval):
                        neqds=[-v if (diff>>i)&1 else v for i,v in enumerate(ds)]
                        neqsb=[-v if (bval>>i)&1 else v for i,v in enumerate(sb)]
                        s.add_clause(guard + neqds + neqsb)
    return s,sel,nz,cells,add_fault

def solve(depth, cells, seed, threads=1, cap=None, rule='base', seconds=180, basis=False):
    started=time.monotonic(); s,sel,nz,cells,add_fault=build(depth,cells,seed,threads,cap,rule,basis)
    added=set(); it=0
    while True:
        rem=seconds-(time.monotonic()-started)
        if rem <= 0: return 'TIMEOUT',None,time.monotonic()-started,it,len(added)
        ok,m=s.solve(time_limit=rem); it+=1
        if ok is not True:
            return ('UNSAT' if ok is False else 'TIMEOUT'),None,time.monotonic()-started,it,len(added)
        ops=[[list(e) for e,v in se.items() if m[v]] for se in sel]
        piv=[q for q in cells if m[nz[q]]]
        d={'ops':ops,'pivots':piv}
        bad=[] if rule == 'none' else [f for f in ft.faults(d,cells,rule,limit=256) if f not in added]
        print(json.dumps({'seed':seed,'iter':it,'bad':len(bad),'added':len(added),'seconds':time.monotonic()-started}),flush=True)
        if not bad:
            return 'SAT',d,time.monotonic()-started,it,len(added)
        for f in bad:
            add_fault(f); added.add(f)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--depth',type=int,required=True); ap.add_argument('--cap',type=int,required=True)
    ap.add_argument('--seed',type=int,default=0); ap.add_argument('--threads',type=int,default=1); ap.add_argument('--seconds',type=float,default=300)
    ap.add_argument('--rule',choices=['none','base','clean_literal','clean','robust','pairs','both','allpairs'],default='both')
    ap.add_argument('--basis',action='store_true')
    ap.add_argument('--helpers',default=''); ap.add_argument('--out',required=True)
    a=ap.parse_args(); helpers=[int(x) for x in a.helpers.split(',') if x]
    cells=list(dict.fromkeys(B+C+helpers)); status,d,elapsed,iters,nfaults=solve(a.depth,cells,a.seed,a.threads,a.cap,a.rule,a.seconds,a.basis)
    rec=dict(vars(a),cells=cells,status=status,elapsed=elapsed,iters=iters,constraints=nfaults)
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.with_suffix('.receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
    if d:
        d.update({'depth':a.depth,'cx':sum(map(len,d['ops'])),'cells':cells,'rule':a.rule,'seed':a.seed})
        out.with_suffix('.prep.json').write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(rec),flush=True)

if __name__ == '__main__': main()
