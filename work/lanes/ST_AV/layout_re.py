"""Layout where D reuses the cells of block C (or B): roles d,a,b,c on 28 cells (+ up to 8 free cells).
D = cells of `ein` (c or b). Preparation order: a, e(D), then X, Y of {b, c}; D is measured before its
cells are re-prepared as c (or b). Each block is connected through its own cells plus helpers: cells of
blocks prepared later (not live) or free cells. Constraints: d_i~a_i, d_i~b_i, b_i~c_i, a_i~(ein)_i.
Objective: data moves + W_AD*helpers(a,e) + W_BC*helpers(b,c) + W_B*(block cells on pre-stage busy cells).
python layout_re.py <ein: c|b> <order after a,e: bc|cb> <seconds> <workers> <out.json>
"""
import json
import sys

from ortools.sat.python import cp_model

R = C = 6
N = 36
PRE = [0, 20, 7, 4, 3, 15, 8]
BUSY = {0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 13, 14, 15, 19, 20}
import os
WM = int(os.environ.get("WM", 1))
W_AD, W_BC, W_BUSY = 1, 3, int(os.environ.get("WB", 1))


def nbrs(q):
    r, c = divmod(q, C)
    return [rr * C + cc for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)) if 0 <= rr < R and 0 <= cc < C]


EDGES = [(q, p) for q in range(N) for p in nbrs(q)]


def solve(ein, rest, seconds, workers):
    m = cp_model.CpModel()
    roles = "dabc"
    x = {(k, i, q): m.NewBoolVar("") for k in roles for i in range(7) for q in range(N)}
    for k in roles:
        for i in range(7):
            m.AddExactlyOne(x[(k, i, q)] for q in range(N))
    for q in range(N):
        m.AddAtMostOne([x[(k, i, q)] for k in roles for i in range(7)])
    for i in range(7):
        for k1, k2 in (("d", "a"), ("d", "b"), ("b", "c"), ("a", ein)):
            for q in range(N):
                m.AddBoolOr([x[(k2, i, p)] for p in nbrs(q)]).OnlyEnforceIf(x[(k1, i, q)])
    occ = lambda ks, q: sum(x[(k, i, q)] for k in ks for i in range(7))
    free = lambda q: 1 - occ(roles, q)
    other = "b" if ein == "c" else "c"
    # (block name, own cell role, helper cell roles, weight)
    stages = [("a", "a", ["b", "c"], W_AD),
              ("e", ein, [other], W_AD),
              (rest[0], rest[0], [rest[1]] if rest[1] == ein else [], W_BC),
              (rest[1], rest[1], [], W_BC)]
    # the second of b/c: its cells' helper from the first? first (rest[0]) may use cells of rest[1]
    stages[2] = (rest[0], rest[0], [rest[1]], W_BC)
    helpers, hel, cost = [], {}, []
    for name, role, hroles, w in stages:
        h = [m.NewBoolVar("") for _ in range(N)]
        for q in range(N):
            m.Add(h[q] <= occ(hroles, q) + free(q))
            m.Add(h[q] + occ(role, q) <= 1)
        helpers += h
        cost.append(w * sum(h))
        hel[name] = h
        mem = [m.NewBoolVar("") for _ in range(N)]
        for q in range(N):
            m.Add(mem[q] == occ(role, q) + h[q])
        root = [x[(role, 0, q)] for q in range(N)]
        f = {e: m.NewIntVar(0, 7, "") for e in EDGES}
        for (u, v), fe in f.items():
            m.Add(fe <= 7 * mem[u])
            m.Add(fe <= 7 * mem[v])
        for q in range(N):
            out = sum(f[(q, p)] for p in nbrs(q))
            inn = sum(f[(p, q)] for p in nbrs(q))
            m.Add(out - inn == 7 * root[q] - occ(role, q))
    busy_use = sum(occ("abc", q) for q in BUSY)
    m.Minimize(sum(cost) + W_BUSY * busy_use + WM * sum(x[("d", i, q)] * (abs(q // C - pc // C) + abs(q % C - pc % C))
                                                   for i, pc in enumerate(PRE) for q in range(N)))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_workers = workers
    st = s.Solve(m)
    name = s.StatusName(st)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": name, "ein": ein, "rest": rest}
    lay = {k: [next(q for q in range(N) if s.Value(x[(k, i, q)])) for i in range(7)] for k in roles}
    lay["e"] = lay[ein]
    lay["helpers"] = {k: [q for q in range(N) if s.Value(hel[k][q])] for k in hel}
    lay["status"], lay["obj"], lay["ein"], lay["rest"] = name, s.ObjectiveValue(), ein, rest
    lay["bound"] = s.BestObjectiveBound()
    return lay


if __name__ == "__main__":
    ein, rest, secs, w, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    lay = solve(ein, rest, secs, w)
    json.dump(lay, open(out, "w"))
    print(lay, flush=True)
    if "d" in lay:
        g = [["  ."] * C for _ in range(R)]
        for k in "dabc":
            for i, q in enumerate(lay[k]):
                g[q // C][q % C] = f" {k}{i}"
        for k, hs in lay["helpers"].items():
            for q in hs:
                if g[q // C][q % C] == "  .":
                    g[q // C][q % C] = f" h{k}"
        print("\n".join("".join(r) for r in g))
