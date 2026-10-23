"""Layouts for the Steane-type round whose block preparations can run in parallel.

Roles per cell: data d_i, blocks a_i, b_i, c_i (d_i~a_i, d_i~b_i, b_i~c_i), helper cells hA (connect
block A) and hBC (connect B and C, prepared together as |0_L>|0_L>). Region A = A + hA and region
BC = B + C + hBC must each be connected; they are disjoint by construction. Objective: data moves
from `prefer` (Manhattan) + w_h * helpers.

    python steane_layout2.py [w_h] [seconds]
"""
import sys

from ortools.sat.python import cp_model

R = C = 6
N = R * C
PRE = [0, 20, 7, 4, 3, 15, 8]


def nbrs(q):
    r, c = divmod(q, C)
    return [rr * C + cc for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)) if 0 <= rr < R and 0 <= cc < C]


EDGES = [(q, p) for q in range(N) for p in nbrs(q)]


def solve(prefer=PRE, w_h=2, seconds=120, workers=16, extra=None):
    m = cp_model.CpModel()
    roles = "dabc"
    x = {(k, i, q): m.NewBoolVar("") for k in roles for i in range(7) for q in range(N)}
    hA = [m.NewBoolVar("") for _ in range(N)]
    hB = [m.NewBoolVar("") for _ in range(N)]
    for k in roles:
        for i in range(7):
            m.AddExactlyOne(x[(k, i, q)] for q in range(N))
    for q in range(N):
        m.AddAtMostOne([x[(k, i, q)] for k in roles for i in range(7)] + [hA[q], hB[q]])
    for i in range(7):
        for k1, k2 in (("d", "a"), ("d", "b"), ("b", "c")):
            for q in range(N):
                m.AddBoolOr([x[(k2, i, p)] for p in nbrs(q)]).OnlyEnforceIf(x[(k1, i, q)])

    inA = [m.NewBoolVar("") for _ in range(N)]
    isA = [m.NewBoolVar("") for _ in range(N)]
    inBC = [m.NewBoolVar("") for _ in range(N)]
    isBC = [m.NewBoolVar("") for _ in range(N)]
    for q in range(N):
        m.Add(isA[q] == sum(x[("a", i, q)] for i in range(7)))
        m.Add(inA[q] == isA[q] + hA[q])
        m.Add(isBC[q] == sum(x[(k, i, q)] for k in "bc" for i in range(7)))
        m.Add(inBC[q] == isBC[q] + hB[q])
    rootA = [x[("a", 0, q)] for q in range(N)]
    rootB = [x[("c", 0, q)] for q in range(N)]
    for members, absorb, root, n_abs in ((inA, isA, rootA, 7), (inBC, isBC, rootB, 14)):
        f = {e: m.NewIntVar(0, n_abs, "") for e in EDGES}
        for (u, v), fe in f.items():
            m.Add(fe <= n_abs * members[u])
            m.Add(fe <= n_abs * members[v])
        for q in range(N):
            out = sum(f[(q, p)] for p in nbrs(q))
            inn = sum(f[(p, q)] for p in nbrs(q))
            m.Add(out - inn == n_abs * root[q] - absorb[q])
    cost = []
    for i, pc in enumerate(prefer):
        cost.append(sum(x[("d", i, q)] * (abs(q // C - pc // C) + abs(q % C - pc % C)) for q in range(N)))
    obj = sum(cost) + w_h * (sum(hA) + sum(hB))
    if extra:
        obj = obj + extra(m, x, hA, hB)
    m.Minimize(obj)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_workers = workers
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    lay = {k: [next(q for q in range(N) if s.Value(x[(k, i, q)])) for i in range(7)] for k in roles}
    lay["hA"] = [q for q in range(N) if s.Value(hA[q])]
    lay["hBC"] = [q for q in range(N) if s.Value(hB[q])]
    return lay, s.ObjectiveValue(), s.StatusName(st)


def show(lay):
    g = [["  ." for _ in range(C)] for _ in range(R)]
    for k in "dabc":
        for i, q in enumerate(lay[k]):
            g[q // C][q % C] = f" {k}{i}"
    for q in lay.get("hA", []):
        g[q // C][q % C] = " hA"
    for q in lay.get("hBC", []):
        g[q // C][q % C] = " hB"
    return "\n".join("".join(row) for row in g)


if __name__ == "__main__":
    w = float(sys.argv[1]) if len(sys.argv) > 1 else 2
    secs = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    r = solve(w_h=w, seconds=secs)
    if not r:
        print("infeasible")
    else:
        lay, obj, st = r
        print(st, obj)
        print(lay)
        print(show(lay))
