"""CP-SAT layouts for the teleport round: chain d_i ~ o_i ~ b_i ~ c_i on the 6x6 grid.

Pairings may use any permutation of the Hamming code automorphism group (168): O_i ~ d_{s1(i)},
C_{j} ~ B_{i} with j = s3(i).  Per block: in place (final cells + helpers connected, prepared
from the cell release) or staged (stage cells + helpers connected, member i hops to a final cell
adjacent to its stage cell).  Release: free cells 0, pre-stage ancilla cells 33, data never.  Time-expanded: block X has start
s_X; in place its region (finals + helpers) is busy from s_X, helpers until s_X+P_X, finals to the
end; staged: stage cells + helpers busy [s_X, h_X+3), finals from h_X (h_X >= s_X+P_X-1: reset of
the destination overlaps the last prep step; CX at h+1, h+2).  Round start T >= end of every block.
Cells may be reused in time (helper/stage cell of X as final cell of Y when X's use ended).

    python layout5.py first last seconds workers out.json '((0,),(1,2))' '(7,16)'
"""
import itertools
import json
import sys

from ortools.sat.python import cp_model

K = 2
import os
WT = int(os.environ.get('WT', 1000))
WH = int(os.environ.get('WH', 2))
HB = int(os.environ.get('HB', 0))
WM = int(os.environ.get('WM', 40))
K = int(os.environ.get('K', 3))
R = C = 6
N = 36
D0 = [0, 20, 7, 4, 3, 15, 8]
ANC0 = [1, 2, 6, 9, 10, 13, 14, 19]
GEN = [0b1010101, 0b1100110, 0b1111000]   # X-stabilizer supports as bit masks (0,2,4,6 ...)
GEN = [sum(1 << i for i in s) for s in ([0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6])]


def span(gs):
    out = {0}
    for g in gs:
        out |= {x ^ g for x in out}
    return out


def automorphisms():
    sp = span(GEN)
    res = []
    for p in itertools.permutations(range(7)):
        def ap(x):
            return sum(1 << p[i] for i in range(7) if x >> i & 1)
        if all(ap(g) in sp for g in GEN):
            res.append(p)
    return res


AUT = automorphisms()
assert len(AUT) == 168


def nbrs(q):
    r, c = divmod(q, C)
    return [rr * C + cc for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)) if 0 <= rr < R and 0 <= cc < C]


EDGES = [(q, p) for q in range(N) for p in nbrs(q)]
SYMS = [lambda r, c: (r, c), lambda r, c: (c, r), lambda r, c: (r, 5 - c), lambda r, c: (5 - c, r),
        lambda r, c: (5 - r, c), lambda r, c: (c, 5 - r), lambda r, c: (5 - r, 5 - c), lambda r, c: (5 - c, 5 - r)]


def placements():
    seen, out = set(), []
    for si, f in enumerate(SYMS):
        pts = {q: f(*divmod(q, C)) for q in D0 + ANC0}
        rs = [p[0] for p in pts.values()]
        cs = [p[1] for p in pts.values()]
        for dr in range(-min(rs), R - max(rs)):
            for dc in range(-min(cs), C - max(cs)):
                m = {q: (p[0] + dr) * C + p[1] + dc for q, p in pts.items()}
                key = tuple(m[q] for q in D0)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"sym": si, "dr": dr, "dc": dc, "d": [m[q] for q in D0], "anc": [m[q] for q in ANC0]})
    return out


def solve(pl, seconds, workers, groups=((0,), (1, 2)), P=(7, 16), Tmax=70, log=False):
    """groups: tuple of block-index tuples (0=O, 1=B, 2=C) prepared jointly; P: prep steps per group."""
    d, anc = pl["d"], pl["anc"]
    rel = [0] * N
    for q in anc:
        rel[q] = 33
    m = cp_model.CpModel()
    B = lambda: m.NewBoolVar("")
    blocks = range(3)
    G = range(len(groups))
    grp = {k: g for g in G for k in groups[g]}
    F = {(k, i, q): B() for k in blocks for i in range(7) for q in range(N)}
    Mx = {(k, i, q): B() for k in blocks for i in range(7) for q in range(N)}
    H = {(g, q): B() for g in G for q in range(N)}
    st = [B() for _ in G]
    for k in blocks:
        for i in range(7):
            m.AddExactlyOne(F[(k, i, q)] for q in range(N))
            m.Add(sum(Mx[(k, i, q)] for q in range(N)) == st[grp[k]])
    isD0 = [1 if q in d else 0 for q in range(N)]
    Dfin = {}
    mv = 0
    T0 = m.NewIntVar(33, Tmax, "T0")
    for j in range(7):
        r0_, c0_ = divmod(d[j], C)
        for q in [d[j]] + [p for p in range(N) if p not in d and 0 < abs(p // C - r0_) + abs(p % C - c0_) <= K]:
            Dfin[(j, q)] = B()
            dist = abs(q // C - r0_) + abs(q % C - c0_)
            if dist:
                m.Add(T0 >= 33 + 3 * dist).OnlyEnforceIf(Dfin[(j, q)])
                mv += dist * Dfin[(j, q)]
        m.AddExactlyOne(Dfin[(j, q)] for q in range(N) if (j, q) in Dfin)
    isD_b = [None] * N
    isD = [isD0[q] if isD0[q] else sum(Dfin[(j, q)] for j in range(7) if (j, q) in Dfin) for q in range(N)]
    for q in range(N):
        if not isD0[q]:
            m.Add(isD[q] <= 1)
            isD_b[q] = B()
            m.Add(isD_b[q] == isD[q])
    for g, v in enumerate(os.environ.get('FORCE', '').split(',')):
        if v in '01' and v:
            m.Add(st[g] == int(v))
    fsum = lambda ks, q: sum(F[(k, i, q)] for k in ks for i in range(7))
    msum = lambda ks, q: sum(Mx[(k, i, q)] for k in ks for i in range(7))
    for q in range(N):
        m.Add(fsum(blocks, q) + isD[q] <= 1)
        for g in G:
            m.Add(msum(groups[g], q) + H[(g, q)] + fsum(groups[g], q) + isD[q] <= 1)
            m.Add(msum(groups[g], q) + H[(g, q)] + isD[q] <= 1)
    for k in blocks:
        for i in range(7):
            for q in range(N):
                m.AddBoolOr([Mx[(k, i, p)] for p in nbrs(q)] + [st[grp[k]].Not()]).OnlyEnforceIf(F[(k, i, q)])
    s1 = [B() for _ in AUT]
    s3 = [B() for _ in AUT]
    m.AddExactlyOne(s1)
    m.AddExactlyOne(s3)
    p1 = {(i, j): B() for i in range(7) for j in range(7)}
    p3 = {(i, j): B() for i in range(7) for j in range(7)}
    for i in range(7):
        for j in range(7):
            m.Add(p1[(i, j)] == sum(s1[n] for n, s in enumerate(AUT) if s[i] == j))
            m.Add(p3[(i, j)] == sum(s3[n] for n, s in enumerate(AUT) if s[i] == j))
            for q in range(N):
                m.AddBoolOr([Dfin[(j, p)] for p in nbrs(q) if (j, p) in Dfin] + [p1[(i, j)].Not()]).OnlyEnforceIf(F[(0, i, q)])
    for i in range(7):
        for q in range(N):
            m.AddBoolOr([F[(0, i, p)] for p in nbrs(q)]).OnlyEnforceIf(F[(1, i, q)])
    for i in range(7):
        for j in range(7):
            for q in range(N):
                m.AddBoolOr([F[(1, i, p)] for p in nbrs(q)] + [p3[(i, j)].Not()]).OnlyEnforceIf(F[(2, j, q)])
    ncol = sum(1 for q in d if (q // C + q % C) % 2 == 1)
    for k in blocks:
        n1 = sum(F[(k, i, q)] for i in range(7) for q in range(N) if (q // C + q % C) % 2 == 1)
        m.Add(n1 == (7 - ncol if k != 1 else ncol))
    for g in G:
        ks = groups[g]
        hb = HB if 1 in ks else 0
        n = 7 * len(ks) + hb
        if hb:
            m.Add(sum(H[(g, q)] for q in range(N)) == hb)
        rg = [B() for _ in range(N)]
        r0 = [B() for _ in range(N)]
        for q in range(N):
            m.Add(rg[q] == fsum(ks, q) + H[(g, q)]).OnlyEnforceIf(st[g].Not())
            m.Add(rg[q] == msum(ks, q) + H[(g, q)]).OnlyEnforceIf(st[g])
            m.Add(r0[q] == F[(ks[0], 0, q)]).OnlyEnforceIf(st[g].Not())
            m.Add(r0[q] == Mx[(ks[0], 0, q)]).OnlyEnforceIf(st[g])
        absorb = [rg[q] - H[(g, q)] for q in range(N)] if not hb else list(rg)
        f = {e: m.NewIntVar(0, n, "") for e in EDGES}
        for (u, v), fe in f.items():
            m.Add(fe <= n * rg[u])
            m.Add(fe <= n * rg[v])
        for q in range(N):
            out = sum(f[(q, p)] for p in nbrs(q))
            inn = sum(f[(p, q)] for p in nbrs(q))
            m.Add(out - inn == n * r0[q] - absorb[q])
    T = m.NewIntVar(33, Tmax, "T")
    m.Add(T >= T0)
    s_ = [m.NewIntVar(0, Tmax, "") for _ in G]
    h_ = [m.NewIntVar(0, Tmax, "") for _ in G]
    fs = [m.NewIntVar(0, Tmax, "") for _ in G]
    te = [m.NewIntVar(0, Tmax + 3, "") for _ in G]
    idle = []
    for g in G:
        m.Add(fs[g] == s_[g]).OnlyEnforceIf(st[g].Not())
        m.Add(te[g] == s_[g] + P[g]).OnlyEnforceIf(st[g].Not())
        m.Add(T >= s_[g] + P[g]).OnlyEnforceIf(st[g].Not())
        m.Add(fs[g] == h_[g]).OnlyEnforceIf(st[g])
        m.Add(h_[g] >= s_[g] + P[g] - 1).OnlyEnforceIf(st[g])
        m.Add(te[g] == h_[g] + 3).OnlyEnforceIf(st[g])
        m.Add(T >= h_[g] + 3).OnlyEnforceIf(st[g])
        m.Add(h_[g] == s_[g]).OnlyEnforceIf(st[g].Not())
        iv = m.NewIntVar(0, Tmax, "")
        m.Add(iv == T - s_[g] - P[g]).OnlyEnforceIf(st[g].Not())
        m.Add(iv == T - s_[g] - P[g] - 2).OnlyEnforceIf(st[g])
        idle.append(iv)
    tmp = {(g, q): B() for g in G for q in range(N)}
    fin = {(g, q): B() for g in G for q in range(N)}
    for g in G:
        for q in range(N):
            m.Add(fin[(g, q)] == fsum(groups[g], q))
            m.Add(tmp[(g, q)] == H[(g, q)] + msum(groups[g], q))
            if rel[q]:
                m.Add(s_[g] >= rel[q]).OnlyEnforceIf(tmp[(g, q)])
                m.Add(fs[g] >= rel[q]).OnlyEnforceIf(fin[(g, q)])
    for q in range(N):
        if not isD0[q]:
            for x in G:
                m.Add(te[x] <= 33).OnlyEnforceIf([tmp[(x, q)], isD_b[q]])
    order = {(x, y): B() for x in G for y in G if x < y}
    for x in G:
        for y in G:
            if x == y:
                continue
            for q in range(N):
                m.Add(te[x] <= fs[y]).OnlyEnforceIf([tmp[(x, q)], fin[(y, q)]])
                if x < y:
                    m.Add(te[x] <= s_[y]).OnlyEnforceIf([tmp[(x, q)], tmp[(y, q)], order[(x, y)]])
                    m.Add(te[y] <= s_[x]).OnlyEnforceIf([tmp[(x, q)], tmp[(y, q)], order[(x, y)].Not()])
    nh = sum(H[(g, q)] for g in G for q in range(N))
    m.Minimize(WT * T + WM * mv + sum(28 * len(groups[g]) * st[g] for g in G) + 7 * sum(idle) + WH * nh)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_workers = workers
    s.parameters.log_search_progress = log
    status = s.Solve(m)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": s.StatusName(status)}
    g_ = s.Value
    res = {"status": s.StatusName(status), "T": g_(T), "s": [g_(x) for x in s_], "h": [g_(x) for x in h_],
           "obj": s.ObjectiveValue(), "bound": s.BestObjectiveBound(), "staged": [g_(x) for x in st],
           "groups": [list(x) for x in groups], "d0": d, "anc": anc,
           "d": [next(q for q in range(N) if (j, q) in Dfin and g_(Dfin[(j, q)])) for j in range(7)]}
    for k, nm in enumerate("obc"):
        res[nm] = [next(q for q in range(N) if g_(F[(k, i, q)])) for i in range(7)]
        res[nm + "_stage"] = [next(q for q in range(N) if g_(Mx[(k, i, q)])) for i in range(7)] if g_(st[grp[k]]) else None
        res[nm + "_help"] = [q for q in range(N) if g_(H[(grp[k], q)])]
    res["s1"] = [AUT[n] for n in range(len(AUT)) if g_(s1[n])][0]
    res["s3"] = [AUT[n] for n in range(len(AUT)) if g_(s3[n])][0]
    return res


def show(res):
    grid = [["  ." for _ in range(C)] for _ in range(R)]
    for q in res["anc"]:
        grid[q // C][q % C] = "  x"
    for q in res["d"]:
        grid[q // C][q % C] = "  D"
    for nm in "obc":
        for i, q in enumerate(res[nm]):
            grid[q // C][q % C] = f" {nm}{i}"
        for i, q in enumerate(res[nm + "_stage"] or []):
            grid[q // C][q % C] = f" {nm.upper()}{i}"
        for q in res[nm + "_help"]:
            grid[q // C][q % C] = f"  h{nm}"
    return "\n".join("".join(r) for r in grid)


if __name__ == "__main__":
    a, b, secs, w, out = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    groups = eval(sys.argv[6])
    P = eval(sys.argv[7])
    pls = placements()
    results = []
    for idx in range(a, min(b, len(pls))):
        r = solve(pls[idx], secs, w, groups, P)
        r["idx"] = idx
        r["pl"] = {k: pls[idx][k] for k in ("sym", "dr", "dc")}
        results.append(r)
        print(idx, r["pl"], r["status"], r.get("T"), r.get("staged"), r.get("obj"), r.get("bound"), flush=True)
        if "o" in r:
            print(show(r), flush=True)
        json.dump(results, open(out, "w"))
