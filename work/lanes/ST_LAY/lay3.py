"""Three-region layout model. python lay3.py idx w_h seconds workers  (idx = prefix map index)"""
import sys, json, itertools
from ortools.sat.python import cp_model
R = C = 6; N = 36; SEED = 0
PRE = [0, 20, 7, 4, 3, 15, 8]
def nbrs(q):
    r, c = divmod(q, C)
    return [rr*C+cc for rr, cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<R and 0<=cc<C]
EDGES = [(q,p) for q in range(N) for p in nbrs(q)]
def maps():
    """(name, PRE') for 8 symmetries x translations keeping footprint rows0-3 cols0-4 on chip."""
    out = {}
    for s in range(8):
        def f(r, c, s=s):
            if s & 1: r, c = c, r
            if s & 2: r = -r
            if s & 4: c = -c
            return r, c
        corners = [f(r, c) for r in (0, 3) for c in (0, 4)]
        rmin = min(r for r, _ in corners); cmin = min(c for _, c in corners)
        rmax = max(r for r, _ in corners); cmax = max(c for _, c in corners)
        for dr in range(-rmin, 6 - rmax):
            for dc in range(-cmin, 6 - cmax):
                pre = []
                for q in PRE:
                    r, c = f(*divmod(q, C)); pre.append((r+dr)*C + c+dc)
                out.setdefault(tuple(pre), (s, dr, dc))
    return [(v, list(k)) for k, v in out.items()]
def solve(prefer, w_h=1, seconds=120, workers=4, maxh=8, extra=None, blocks=("A","B","C")):
    m = cp_model.CpModel(); roles = "dabc"
    x = {(k,i,q): m.NewBoolVar("") for k in roles for i in range(7) for q in range(N)}
    h = {k: [m.NewBoolVar("") for _ in range(N)] for k in "ABC"}
    for k in roles:
        for i in range(7): m.AddExactlyOne(x[(k,i,q)] for q in range(N))
    for q in range(N):
        m.AddAtMostOne([x[(k,i,q)] for k in roles for i in range(7)] + [h[k][q] for k in "ABC"])
    for i in range(7):
        for k1,k2 in (("d","a"),("d","b"),("b","c")):
            for q in range(N):
                m.AddBoolOr([x[(k2,i,p)] for p in nbrs(q)]).OnlyEnforceIf(x[(k1,i,q)])
    m.Add(sum(sum(v) for v in h.values()) <= maxh)
    for blk, role in [t for t in (("A","a"),("B","b"),("C","c")) if t[0] in blocks]:
        isb = [sum(x[(role,i,q)] for i in range(7)) for q in range(N)]
        mem = [m.NewBoolVar("") for _ in range(N)]
        for q in range(N): m.Add(mem[q] == isb[q] + h[blk][q])
        f = {e: m.NewIntVar(0,7,"") for e in EDGES}
        for (u,v),fe in f.items():
            m.Add(fe <= 7*mem[u]); m.Add(fe <= 7*mem[v])
        for q in range(N):
            m.Add(sum(f[(q,p)] for p in nbrs(q)) - sum(f[(p,q)] for p in nbrs(q)) == 7*x[(role,0,q)] - isb[q])
    if extra: extra(m, x)
    cost = [sum(x[("d",i,q)]*(abs(q//C-pc//C)+abs(q%C-pc%C)) for q in range(N)) for i,pc in enumerate(prefer)]
    m.Minimize(sum(cost) + w_h*sum(sum(v) for v in h.values()))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = seconds; s.parameters.num_workers = workers; s.parameters.random_seed = SEED; s.parameters.log_search_progress = False
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return s.StatusName(st)
    lay = {k:[next(q for q in range(N) if s.Value(x[(k,i,q)])) for i in range(7)] for k in roles}
    for k in "ABC": lay["h"+k] = [q for q in range(N) if s.Value(h[k][q])]
    return lay, s.ObjectiveValue(), s.StatusName(st)
if __name__ == "__main__":
    ms = maps(); idx = int(sys.argv[1]); w = float(sys.argv[2]); secs = int(sys.argv[3]); wk = int(sys.argv[4])
    if idx < 0: print(len(ms)); sys.exit()
    name, pre = ms[idx]
    r = solve(pre, w, secs, wk)
    json.dump({"map": name, "pre": pre, "res": r}, open(f"lay_{idx}_{w}.json","w"))
