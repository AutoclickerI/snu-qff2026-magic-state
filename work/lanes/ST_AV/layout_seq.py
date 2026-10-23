"""Sequential-prep layout: blocks d,a,b,c,e(=D) on 35 of 36 cells; the blocks are prepared in a given
order, each connected through its own cells plus helper cells (cells of later-prepared blocks or the
one free cell). Objective: data moves (Manhattan from PRE) + W*helpers.
python layout_seq.py <order e.g. eabc> <seconds> <workers> <out.json>
"""
import json
import sys

from ortools.sat.python import cp_model

R = C = 6
N = 36
PRE = [0, 20, 7, 4, 3, 15, 8]
W = 2


def nbrs(q):
    r, c = divmod(q, C)
    return [rr * C + cc for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)) if 0 <= rr < R and 0 <= cc < C]


EDGES = [(q, p) for q in range(N) for p in nbrs(q)]


def solve(order, seconds, workers):
    m = cp_model.CpModel()
    roles = "dabce"
    x = {(k, i, q): m.NewBoolVar("") for k in roles for i in range(7) for q in range(N)}
    for k in roles:
        for i in range(7):
            m.AddExactlyOne(x[(k, i, q)] for q in range(N))
    for q in range(N):
        m.AddAtMostOne([x[(k, i, q)] for k in roles for i in range(7)])
    for i in range(7):
        for k1, k2 in (("d", "a"), ("d", "b"), ("b", "c"), ("a", "e")):
            for q in range(N):
                m.AddBoolOr([x[(k2, i, p)] for p in nbrs(q)]).OnlyEnforceIf(x[(k1, i, q)])
    occ = lambda ks, q: sum(x[(k, i, q)] for k in ks for i in range(7))
    helpers = []
    hel = {}
    for pos, k in enumerate(order):
        later = order[pos + 1:]
        h = [m.NewBoolVar("") for _ in range(N)]
        for q in range(N):
            # helper: a cell of a later block, or the free cell (not occupied by anything)
            m.Add(h[q] <= occ(later, q) + (1 - occ(roles, q)))
            m.Add(h[q] + occ(k, q) <= 1)
        helpers += h
        hel[k] = h
        mem = [m.NewBoolVar("") for _ in range(N)]
        for q in range(N):
            m.Add(mem[q] == occ(k, q) + h[q])
        root = [x[(k, 0, q)] for q in range(N)]
        f = {e: m.NewIntVar(0, 7, "") for e in EDGES}
        for (u, v), fe in f.items():
            m.Add(fe <= 7 * mem[u])
            m.Add(fe <= 7 * mem[v])
        for q in range(N):
            out = sum(f[(q, p)] for p in nbrs(q))
            inn = sum(f[(p, q)] for p in nbrs(q))
            m.Add(out - inn == 7 * root[q] - occ(k, q))
    m.Minimize(W * sum(helpers) + sum(x[("d", i, q)] * (abs(q // C - pc // C) + abs(q % C - pc % C))
                                      for i, pc in enumerate(PRE) for q in range(N)))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_workers = workers
    st = s.Solve(m)
    name = s.StatusName(st)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": name, "order": order}
    lay = {k: [next(q for q in range(N) if s.Value(x[(k, i, q)])) for i in range(7)] for k in roles}
    lay["helpers"] = {k: [q for q in range(N) if s.Value(hel[k][q])] for k in order}
    lay["status"], lay["obj"], lay["order"] = name, s.ObjectiveValue(), order
    lay["bound"] = s.BestObjectiveBound()
    return lay


if __name__ == "__main__":
    order, secs, w, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    lay = solve(order, secs, w)
    json.dump(lay, open(out, "w"))
    print({k: v for k, v in lay.items()}, flush=True)
