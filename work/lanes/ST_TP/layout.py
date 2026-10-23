"""CP-SAT layouts for the teleport round: chain d_i ~ o_i ~ b_i ~ c_i on the 6x6 grid.

Pairings may use any permutation of the Hamming code automorphism group (168): O_i ~ d_{s1(i)},
C_{j} ~ B_{i} with j = s3(i).  Per block: in place (final cells + helpers connected, prepared
from the cell release) or staged (stage cells + helpers connected, member i hops to a final cell
adjacent to its stage cell).  Release: free cells 0, pre-stage ancilla cells 33, data never.
T = round start: >= 33; an in-place block touching a late cell: 33 + P; a staged block with a
late final cell: 36 (reset 33, two CX).

    python layout.py <first placement> <last placement> <seconds> <workers> <out.json> [PO PB PC]
"""
import itertools
import json
import sys

from ortools.sat.python import cp_model

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


def solve(pl, seconds, workers, P=(7, 5, 5), Tmax=60, log=False):
    d, anc = pl["d"], pl["anc"]
    rel = [0] * N
    for q in anc:
        rel[q] = 33
    m = cp_model.CpModel()
    B = lambda: m.NewBoolVar("")
    blocks = range(3)           # O, B, C
    F = {(k, i, q): B() for k in blocks for i in range(7) for q in range(N)}      # final cells
    Mx = {(k, i, q): B() for k in blocks for i in range(7) for q in range(N)}     # stage cells (if staged)
    H = {(k, q): B() for k in blocks for q in range(N)}
    st = [B() for _ in blocks]
    for k in blocks:
        for i in range(7):
            m.AddExactlyOne(F[(k, i, q)] for q in range(N))
            m.Add(sum(Mx[(k, i, q)] for q in range(N)) == st[k])
    isD = [1 if q in d else 0 for q in range(N)]
    for q in range(N):
        m.Add(sum(F[(k, i, q)] + Mx[(k, i, q)] for k in blocks for i in range(7)) + sum(H[(k, q)] for k in blocks) + isD[q] <= 1)
    for k in blocks:     # staged: stage cell adjacent to its final cell
        for i in range(7):
            for q in range(N):
                m.AddBoolOr([Mx[(k, i, p)] for p in nbrs(q)] + [st[k].Not()]).OnlyEnforceIf(F[(k, i, q)])
    # pairings
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
    for i in range(7):
        for j in range(7):
            nb = nbrs(d[j])
            m.Add(sum(F[(0, i, q)] for q in nb) == 1).OnlyEnforceIf(p1[(i, j)])
    for i in range(7):    # B_i ~ O_i
        for q in range(N):
            m.AddBoolOr([F[(0, i, p)] for p in nbrs(q)]).OnlyEnforceIf(F[(1, i, q)])
    for i in range(7):    # C_j ~ B_i if p3[i][j]
        for j in range(7):
            for q in range(N):
                m.AddBoolOr([F[(1, i, p)] for p in nbrs(q)] + [p3[(i, j)].Not()]).OnlyEnforceIf(F[(2, j, q)])
    # regions and connectivity
    hops = 0
    late_ip, late_st = [], []
    for k in blocks:
        rg = [B() for _ in range(N)]
        r0 = [B() for _ in range(N)]
        for q in range(N):
            fin = sum(F[(k, i, q)] for i in range(7))
            stg = sum(Mx[(k, i, q)] for i in range(7))
            m.Add(rg[q] == fin + H[(k, q)]).OnlyEnforceIf(st[k].Not())
            m.Add(rg[q] == stg + H[(k, q)]).OnlyEnforceIf(st[k])
            m.Add(r0[q] == F[(k, 0, q)]).OnlyEnforceIf(st[k].Not())
            m.Add(r0[q] == Mx[(k, 0, q)]).OnlyEnforceIf(st[k])
        absorb = [rg[q] - H[(k, q)] for q in range(N)]
        f = {e: m.NewIntVar(0, 7, "") for e in EDGES}
        for (u, v), fe in f.items():
            m.Add(fe <= 7 * rg[u])
            m.Add(fe <= 7 * rg[v])
        for q in range(N):
            out = sum(f[(q, p)] for p in nbrs(q))
            inn = sum(f[(p, q)] for p in nbrs(q))
            m.Add(out - inn == 7 * r0[q] - absorb[q])
        lt = [q for q in range(N) if rel[q]]
        a = B()    # in place with a late region cell
        b = B()    # staged with a late final cell
        m.AddBoolOr([rg[q] for q in lt] + [a.Not()]).OnlyEnforceIf(st[k].Not()) if lt else None
        m.Add(a >= 0)
        # a >= any late region cell when in place
        for q in lt:
            m.Add(a >= rg[q]).OnlyEnforceIf(st[k].Not())
            m.Add(rg[q] == 0).OnlyEnforceIf(st[k])           # stage region uses only free cells
            m.Add(b >= sum(F[(k, i, q)] for i in range(7))).OnlyEnforceIf(st[k])
        late_ip.append(a)
        late_st.append(b)
        # colour counts (checkerboard): O: 3 on colour 1 / 4 on colour 0; B: 3/4 swapped; C like O
        col = [(q // C + q % C) % 2 for q in range(N)]
        n1 = sum(F[(k, i, q)] for i in range(7) for q in range(N) if col[q] == 1)
        m.Add(n1 == (3 if k != 1 else 4)) if False else None
    ncol = sum(1 for q in d if (q // C + q % C) % 2 == 1)
    for k in blocks:
        n1 = sum(F[(k, i, q)] for i in range(7) for q in range(N) if (q // C + q % C) % 2 == 1)
        m.Add(n1 == (7 - ncol if k != 1 else ncol))
    T = m.NewIntVar(33, Tmax, "T")
    for k in blocks:
        m.Add(T >= 33 + P[k]).OnlyEnforceIf(late_ip[k])
        m.Add(T >= 36).OnlyEnforceIf(late_st[k])
    nh = sum(H[(k, q)] for k in blocks for q in range(N))
    m.Minimize(10000 * T + 7 * 20 * sum(st) + nh)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_workers = workers
    s.parameters.log_search_progress = log
    status = s.Solve(m)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": s.StatusName(status)}
    g = lambda var: s.Value(var)
    res = {"status": s.StatusName(status), "T": g(T), "obj": s.ObjectiveValue(), "bound": s.BestObjectiveBound(),
           "staged": [g(x) for x in st], "d": d, "anc": anc}
    for k, nm in enumerate("obc"):
        res[nm] = [next(q for q in range(N) if g(F[(k, i, q)])) for i in range(7)]
        res[nm + "_stage"] = [next(q for q in range(N) if g(Mx[(k, i, q)])) for i in range(7)] if g(st[k]) else None
        res[nm + "_help"] = [q for q in range(N) if g(H[(k, q)])]
    res["s1"] = [AUT[n] for n in range(len(AUT)) if g(s1[n])][0]
    res["s3"] = [AUT[n] for n in range(len(AUT)) if g(s3[n])][0]
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
    P = tuple(int(x) for x in sys.argv[6:9]) if len(sys.argv) > 8 else (7, 5, 5)
    pls = placements()
    print(len(pls), "placements", flush=True)
    results = []
    for idx in range(a, min(b, len(pls))):
        r = solve(pls[idx], secs, w, P)
        r["idx"] = idx
        r["pl"] = {k: pls[idx][k] for k in ("sym", "dr", "dc")}
        results.append(r)
        print(idx, r["pl"], r["status"], r.get("T"), r.get("staged"), r.get("obj"), r.get("bound"), flush=True)
        if "o" in r:
            print(show(r), flush=True)
        json.dump(results, open(out, "w"))
