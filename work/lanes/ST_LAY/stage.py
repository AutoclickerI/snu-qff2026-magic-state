"""Staging layout model. python stage.py tag seconds workers extra_cells(csv or '') seed
Round cells d,a,b,c distinct; staging s^X_i in {p^X_i} u nbrs(p^X_i), staging+helpers per block connected,
disjoint across blocks, inside allowed set S; staging/helper cells are not round cells except s_i = p_i."""
import sys, json
from ortools.sat.python import cp_model
from lay3 import nbrs, EDGES, PRE
R = C = 6; N = 36
F = [5,11,12,16,17,18] + list(range(21,36))
import os
MAXD = int(os.environ.get("MAXD", "3"))
ROLE = {"A": "a", "B": "b", "C": "c"}
def solve(allowed, seconds, workers, seed=0, pre=PRE, pen=None, maxM=None, maxh=8):
    pen = pen or {}
    m = cp_model.CpModel()
    roles = "dabc"
    x = {(k,i,q): m.NewBoolVar("") for k in roles for i in range(7) for q in range(N)}
    for k in roles:
        for i in range(7): m.AddExactlyOne(x[(k,i,q)] for q in range(N))
    for q in range(N): m.AddAtMostOne(x[(k,i,q)] for k in roles for i in range(7))
    for i in range(7):
        for k1,k2 in (("d","a"),("d","b"),("b","c")):
            for q in range(N):
                m.AddBoolOr([x[(k2,i,p)] for p in nbrs(q)]).OnlyEnforceIf(x[(k1,i,q)])
    st = {}; h = {}; mm = {}
    for X in "ABC":
        role = ROLE[X]
        h[X] = {q: m.NewBoolVar("") for q in allowed}
        for i in range(7):
            for q in allowed: st[(X,i,q)] = m.NewBoolVar("")
            m.AddExactlyOne(st[(X,i,q)] for q in allowed)
            for q in allowed:
                m.AddBoolOr([x[(role,i,p)] for p in [q]+nbrs(q)]).OnlyEnforceIf(st[(X,i,q)])
                mm[(X,i,q)] = m.NewBoolVar("")
                m.AddImplication(mm[(X,i,q)], st[(X,i,q)]); m.AddImplication(mm[(X,i,q)], x[(role,i,q)])
                m.AddBoolOr([st[(X,i,q)].Not(), x[(role,i,q)].Not(), mm[(X,i,q)]])
    for q in range(N):
        rnd = sum(x[(k,i,q)] for k in roles for i in range(7))
        if q in allowed:
            stg = sum(st[(X,i,q)] for X in "ABC" for i in range(7)) + sum(h[X][q] for X in "ABC")
            m.Add(stg <= 1)
            rabc = sum(x[(k,i,q)] for k in 'abc' for i in range(7))
            m.Add(rabc + stg <= 1 + sum(mm[(X,i,q)] for X in "ABC" for i in range(7)))
            m.Add(sum(x[('d',i,q)] for i in range(7)) + sum(mm[(X,i,q)] for X in 'ABC' for i in range(7)) <= 1)
    m.Add(sum(h[X][q] for X in "ABC" for q in allowed) <= maxh)
    # connectivity per block
    for X in "ABC":
        isb = {q: sum(st[(X,i,q)] for i in range(7)) for q in allowed}
        mem = {q: m.NewBoolVar("") for q in allowed}
        for q in allowed: m.Add(mem[q] == isb[q] + h[X][q])
        E = [(u,v) for u in allowed for v in nbrs(u) if v in allowed]
        f = {e: m.NewIntVar(0,7,"") for e in E}
        for (u,v),fe in f.items():
            m.Add(fe <= 7*mem[u]); m.Add(fe <= 7*mem[v])
        for q in allowed:
            m.Add(sum(f[(q,p)] for p in nbrs(q) if p in allowed) - sum(f[(p,q)] for p in nbrs(q) if p in allowed)
                  == 7*st[(X,0,q)] - isb[q])

    # data routes: shortest grid paths whose intermediate cells carry no block cell
    blk = {}
    for q in range(N):
        b = m.NewBoolVar("")
        terms = [x[(k,i,q)] for k in "abc" for i in range(7)]
        m.Add(b == sum(terms)); blk[q] = b
    import itertools
    def paths(a, bq):
        ra, ca = divmod(a, C); rb, cb = divmod(bq, C)
        dr = 1 if rb > ra else -1; dc = 1 if cb > ca else -1
        steps = ["r"] * abs(rb - ra) + ["c"] * abs(cb - ca)
        out = set()
        for perm in set(itertools.permutations(steps)):
            r, c = ra, ca; cells = []
            for t in perm:
                if t == "r": r += dr
                else: c += dc
                cells.append(r * C + c)
            out.add(tuple(cells[:-1]))
        return out
    for i, pc in enumerate(pre):
        for q in range(N):
            D = abs(q//C-pc//C) + abs(q%C-pc%C)
            if D > MAXD:
                m.Add(x[("d",i,q)] == 0); continue
            if D <= 1: continue
            oks = []
            for pth in paths(pc, q):
                o = m.NewBoolVar("")
                for c in pth: m.AddImplication(o, blk[c].Not())
                oks.append(o)
            m.AddBoolOr(oks).OnlyEnforceIf(x[("d",i,q)])
    for q in (pre if os.environ.get('NOPRE','1')=='1' else []):
        if q in allowed: m.Add(sum(st[(X,i,q)] for X in 'ABC' for i in range(7)) + sum(h[X][q] for X in 'ABC') == 0)
    # costs
    dist = [sum(x[("d",i,q)]*(abs(q//C-pc//C)+abs(q%C-pc%C)) for q in range(N)) for i,pc in enumerate(pre)]
    M = m.NewIntVar(0, 12, "")
    for dd in dist: m.Add(M >= dd)
    hop = [1 - mm[(X,i,q)] if False else None for X in "ABC" for i in range(7) for q in allowed][:0]
    nohop = sum(mm[(X,i,q)] for X in "ABC" for i in range(7) for q in allowed)
    nhop = 21 - nohop
    anyhop = m.NewBoolVar("")
    m.Add(nhop <= 21 * anyhop)
    m.Add(M >= anyhop)
    if maxM is not None: m.Add(M <= maxM)
    extra = sum(pen.get(q, 0) * (sum(st[(X,i,q)] for X in "ABC" for i in range(7)) + sum(h[X][q] for X in "ABC"))
                for q in allowed)
    m.Minimize(1000*M + 10*sum(dist) + 3*nhop + sum(h[X][q] for X in "ABC" for q in allowed) + extra)
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = seconds; s.parameters.num_workers = workers
    s.parameters.random_seed = seed
    r = s.Solve(m)
    if r not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return s.StatusName(r)
    g = lambda k: [next(q for q in range(N) if s.Value(x[(k,i,q)])) for i in range(7)]
    lay = {k: g(k) for k in roles}
    lay["stage"] = {ROLE[X]: [next(q for q in allowed if s.Value(st[(X,i,q)])) for i in range(7)] for X in "ABC"}
    lay["helpers"] = {ROLE[X]: [q for q in allowed if s.Value(h[X][q])] for X in "ABC"}
    return lay, s.ObjectiveValue(), s.StatusName(r), s.Value(M)
def show(l):
    g = [[" ."]*6 for _ in range(6)]
    for k in "dabc":
        for i,q in enumerate(l[k]): g[q//6][q%6] = f"{k}{i}"
    for k in "abc":
        for i,q in enumerate(l["stage"][k]):
            if g[q//6][q%6] == " .": g[q//6][q%6] = f"s{k}{i}"
        for q in l["helpers"][k]: g[q//6][q%6] = f"h{k}"
    return "\n".join(" ".join(f"{x:3}" for x in r) for r in g)
if __name__ == "__main__":
    tag = sys.argv[1]; secs = float(sys.argv[2]); wk = int(sys.argv[3])
    ex = [int(t) for t in sys.argv[4].split(",") if t]; seed = int(sys.argv[5])
    pw = float(sys.argv[6]) if len(sys.argv) > 6 else 30
    allowed = sorted(set(F) | set(ex))
    r = solve(allowed, secs, wk, seed, pen={q: pw for q in ex})
    if isinstance(r, str): print(tag, r)
    else:
        l, obj, stt, M = r; l["obj"] = obj; l["M"] = M; l["tag"] = tag
        json.dump(l, open(f"stage_{tag}.json", "w")); print(tag, stt, obj, M); print(show(l))
