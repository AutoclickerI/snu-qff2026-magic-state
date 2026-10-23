"""CP-SAT layout with the D verifier: roles d,a,b,c,e(=D), 35 cells, no helpers.
d_i~a_i, d_i~b_i, b_i~c_i, a_i~e_i. Connectivity regions per mode:
  own: A, D, B+C each connected;  joint: A+D, B+C connected;  mode all: every block (A, D, B, C) alone.
python layout.py <mode> <seconds> <workers> <out.json>
"""
import json
import sys

from ortools.sat.python import cp_model

R = C = 6
N = 36
PRE = [0, 20, 7, 4, 3, 15, 8]


def nbrs(q):
    r, c = divmod(q, C)
    return [rr * C + cc for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)) if 0 <= rr < R and 0 <= cc < C]


EDGES = [(q, p) for q in range(N) for p in nbrs(q)]
REGIONS = {"hel": [("a",), ("e",), ("b", "c")], "ae": [("a", "e")], "none": [], "bc": [("b", "c")], "own": [("a",), ("e",), ("b", "c")], "joint": [("a", "e"), ("b", "c")],
           "all": [("a",), ("e",), ("b",), ("c",)]}


def solve(mode, seconds, workers):
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
    helpers = []
    for reg in REGIONS[mode]:
        n_abs = 7 * len(reg)
        isr = [m.NewBoolVar("") for _ in range(N)]
        own = [sum(x[(k, i, q)] for k in reg for i in range(7)) for q in range(N)]
        for q in range(N):
            m.Add(isr[q] == own[q])
        if mode == "hel" and reg in (("a",), ("e",)):
            # helper cells of A: B/C cells; of D: A/B/C cells (used earlier, released before they are prepared)
            later = ("b", "c") if reg == ("a",) else ("a", "b", "c")
            mem = [m.NewBoolVar("") for _ in range(N)]
            hq = [m.NewBoolVar("") for _ in range(N)]
            for q in range(N):
                m.Add(mem[q] == own[q] + hq[q])
                m.Add(hq[q] <= sum(x[(k, i, q)] for k in later for i in range(7)))
            helpers += hq
            isr_members = mem
        else:
            isr_members = isr
        ab, isr = isr, isr_members
        root = [x[(reg[0], 0, q)] for q in range(N)]
        f = {e: m.NewIntVar(0, n_abs, "") for e in EDGES}
        for (u, v), fe in f.items():
            m.Add(fe <= n_abs * isr[u])
            m.Add(fe <= n_abs * isr[v])
        for q in range(N):
            out = sum(f[(q, p)] for p in nbrs(q))
            inn = sum(f[(p, q)] for p in nbrs(q))
            m.Add(out - inn == n_abs * root[q] - ab[q])
    m.Minimize(sum(helpers) + sum(x[("d", i, q)] * (abs(q // C - pc // C) + abs(q % C - pc % C))
                   for i, pc in enumerate(PRE) for q in range(N)))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_workers = workers
    st = s.Solve(m)
    name = s.StatusName(st)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": name}
    lay = {k: [next(q for q in range(N) if s.Value(x[(k, i, q)])) for i in range(7)] for k in roles}
    lay["status"], lay["obj"] = name, s.ObjectiveValue()
    return lay


if __name__ == "__main__":
    mode, secs, w, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    lay = solve(mode, secs, w)
    json.dump(lay, open(out, "w"))
    print(lay, flush=True)
    if "d" in lay:
        g = [["  ."] * C for _ in range(R)]
        for k in "dabce":
            for i, q in enumerate(lay[k]):
                g[q // C][q % C] = f" {k}{i}"
        print("\n".join("".join(r) for r in g))
