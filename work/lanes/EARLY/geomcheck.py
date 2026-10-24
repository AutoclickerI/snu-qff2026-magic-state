"""Pure 6x6 geometry: is there an end state (D, A_i~D_i, B_i~D_i, C_i~B_i, A connected, B u C connected)
with k spare cells adjacent to data? modes: pair (2 adjacent spares touching 4 distinct data, 2+2 or 3+1),
plus (1 spare with 4 data neighbours), single (1 spare adjacent to >= 1 data), count (max # data with a spare nbr)."""
import sys, itertools
from ortools.sat.python import cp_model
N = 6
def nb(q):
    r, c = divmod(q, N)
    return [q2 for q2, ok in ((q - N, r > 0), (q + N, r < N - 1), (q - 1, c > 0), (q + 1, c < N - 1)) if ok]
cells = range(36)
def model(mode, noconn=False):
    m = cp_model.CpModel()
    role = {(r, i, c): m.NewBoolVar(f"{r}{i}_{c}") for r in "DABC" for i in range(7) for c in cells}
    for r in "DABC":
        for i in range(7):
            m.AddExactlyOne(role[r, i, c] for c in cells)
    occ = {c: m.NewBoolVar(f"occ{c}") for c in cells}
    for c in cells:
        m.Add(occ[c] == sum(role[r, i, c] for r in "DABC" for i in range(7)))
    isD = {c: m.NewBoolVar(f"isD{c}") for c in cells}
    for c in cells:
        m.Add(isD[c] == sum(role["D", i, c] for i in range(7)))
        for i in range(7):
            for r in "AB":
                m.AddBoolOr([role[r, i, c].Not()] + [role["D", i, d] for d in nb(c)])
            m.AddBoolOr([role["C", i, c].Not()] + [role["B", i, d] for d in nb(c)])
    def connected(xs, size, name):
        root = {c: m.NewBoolVar(f"{name}r{c}") for c in cells}
        m.AddExactlyOne(root.values())
        for c in cells:
            m.AddImplication(root[c], xs[c])
        f = {}
        for u in cells:
            for v in nb(u):
                f[u, v] = m.NewIntVar(0, size, f"{name}f{u}_{v}")
                m.Add(f[u, v] <= size * xs[u]); m.Add(f[u, v] <= size * xs[v])
        for c in cells:
            m.Add(sum(f[u, c] for u in nb(c)) - sum(f[c, v] for v in nb(c)) == xs[c] - size * root[c])
    isA = {c: m.NewBoolVar(f"isA{c}") for c in cells}
    isBC = {c: m.NewBoolVar(f"isBC{c}") for c in cells}
    for c in cells:
        m.Add(isA[c] == sum(role["A", i, c] for i in range(7)))
        m.Add(isBC[c] == sum(role[r, i, c] for r in "BC" for i in range(7)))
    if not noconn:
        connected(isA, 7, "A"); connected(isBC, 14, "BC")
    # spare-adjacent data count
    sp = {}
    for c in cells:
        sp[c] = m.NewBoolVar(f"sp{c}")  # data at c with a spare neighbour
        m.AddImplication(sp[c], isD[c])
        m.AddBoolOr([sp[c].Not()] + [occ[x].Not() for x in nb(c)])
    if mode == "count":
        m.Maximize(sum(sp.values()))
    elif mode == "plus":
        v = {x: m.NewBoolVar(f"plus{x}") for x in cells if len(nb(x)) == 4}
        m.AddExactlyOne(v.values())
        for x, vv in v.items():
            m.AddImplication(vv, occ[x].Not())
            for y in nb(x):
                m.AddImplication(vv, isD[y])
    elif mode == "pair":
        opts = []
        for a1 in cells:
            for a2 in nb(a1):
                v = m.NewBoolVar(f"pair{a1}_{a2}")
                opts.append(v)
                m.AddImplication(v, occ[a1].Not()); m.AddImplication(v, occ[a2].Not())
                # a1 touches >= 2 data, a2 touches >= 2 data, total distinct >= 4
                d1 = [isD[y] for y in nb(a1) if y != a2]
                d2 = [isD[y] for y in nb(a2) if y != a1]
                m.Add(sum(d1) >= 1).OnlyEnforceIf(v)
                m.Add(sum(d2) >= 1).OnlyEnforceIf(v)
                m.Add(sum(set(d1) | set(d2)) >= 4).OnlyEnforceIf(v)
        m.AddExactlyOne(opts)
    s = cp_model.CpSolver(); s.parameters.num_workers = 16; s.parameters.max_time_in_seconds = 600
    st = s.Solve(m)
    out = s.StatusName(st)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        g = [["  ."] * 6 for _ in range(6)]
        for (r, i, c), v in role.items():
            if s.Value(v):
                g[c // 6][c % 6] = f" {r}{i}"
        out += f" obj={s.ObjectiveValue() if mode == 'count' else ''}\n" + "\n".join("".join(row) for row in g)
    return out
for mode in sys.argv[1:]:
    print(mode, model(mode.replace('-noconn', ''), mode.endswith('-noconn')), flush=True)
