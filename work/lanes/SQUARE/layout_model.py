"""CP-SAT end-state layout + timing search on v36c's kept prefix (cultivation + blue check).

Data start cells/ready ticks and cell releases come from the kept prefix (see PREFIX below).
Variables: one coherent-hop path per data qubit (<= MAXH hops, source-zero check after each hop), final roles
A_i, B_i, C_i, connectivity of A and of B u C, the A flag path (a weight-3 X_L support of A forming a grid path).
Timing (proxy): hop j into x at t >= rel(x)+1, two CX ticks, source M at t+2 (cell free at t+3);
A cell ready window: R >= rel(c) + A_LEN; B u C cell: R >= rel(c) + BC_LEN (LATE cells may use BC_LATE);
data: R >= arrival (flag data: R-1 >= arrival).
Objective: R, then hops.

usage: layout.py [A_LEN] [BC_LEN] [BC_LATE] [NLATE] [MAXH] [nsol]
"""
import sys, json, itertools
from ortools.sat.python import cp_model

N = 6
def nb(q):
    r, c = divmod(q, N)
    return [q2 for q2, ok in ((q - N, r > 0), (q + N, r < N - 1), (q - 1, c > 0), (q + 1, c < N - 1)) if ok]

# Kept prefix (v36c through the blue check, blue Z readout moved to 35, q14 echo closed at 32/MX33).
START = {0: 0, 1: 20, 2: 7, 3: 4, 4: 3, 5: 15, 6: 8}           # code label -> start cell
READY = {0: 33, 1: 33, 2: 34, 3: 33, 4: 34, 5: 31, 6: 33}       # first free tick of the data
REL = {1: 36, 2: 36, 5: 34, 6: 31, 9: 32, 10: 30, 11: 30, 13: 33, 14: 34, 19: 33, 21: 32}  # first free tick
for q in range(36):
    REL.setdefault(q, 0)
for i, s in START.items():
    REL[s] = 99  # data cells: handled through paths
PIN = {}  # optional {'A'|'B'|'C': [cell per label], 'paths': {i: path}} pinned roles
KEEP_A = False
KEEP_R3 = False
CROSS = False  # allow sequential reuse of a cell by two data paths (time-disjoint)
SEPARATE_CONNECTED = True
A_CONNECTED = False
COMPACT = False
XL3 = [(1, 3, 5), (0, 3, 4), (0, 1, 2), (2, 3, 6), (1, 4, 6), (0, 5, 6), (2, 4, 5)]


def paths_from(s, maxh):
    out = [[s]]
    frontier = [[s]]
    for _ in range(maxh):
        nf = []
        for p in frontier:
            for q in nb(p[-1]):
                if q in p or (q in START.values() and not CROSS):
                    continue
                nf.append(p + [q])
        out += nf
        frontier = nf
    return out


def hop_times(i, p):
    """Return (arrival tick, per-cell busy-until tick (first free tick after the data left))."""
    t = READY[i]
    busy = {}
    for a, b in zip(p, p[1:]):
        t = max(t, REL[b] + 1 if REL[b] < 99 else 0)
        busy[a] = t + 3  # CX at t, t+1; source check M at t+2
        t += 2
    return t, busy


def occupancy(i, p):
    """cell -> [first tick held, first tick free) for path p of data i (final cell held forever)."""
    t = READY[i]
    occ = {p[0]: [0, None]}
    for a, b in zip(p, p[1:]):
        t = max(t, REL[b] + 1 if REL[b] < 99 else 0)
        occ[a][1] = t + 3
        occ[b] = [t, None]
        t += 2
    occ[p[-1]][1] = 10 ** 6
    return occ


def disjoint(x, y):
    return x[1] <= y[0] or y[1] <= x[0]


def solve(A_LEN=5, BC_LEN=12, BC_LATE=6, NLATE=4, MAXH=3, nsol=5, fixR=None, flag=True, check=0, maxR=None, slide=0, xcheck=0, helper=0,
          spareW=None, spareWt=None, near=None, need=(), prio='weight'):
    m = cp_model.CpModel()
    cells = range(36)
    P = {i: paths_from(START[i], MAXH) for i in START}
    pv = {(i, k): m.NewBoolVar(f"p{i}_{k}") for i in P for k in range(len(P[i]))}
    for i in P:
        m.AddExactlyOne(pv[i, k] for k in range(len(P[i])))
    role = {}
    for c in cells:
        for r in "ABC":
            for i in range(7):
                role[r, i, c] = m.NewBoolVar(f"{r}{i}_{c}")
    final = {(i, c): m.NewBoolVar(f"D{i}_{c}") for i in range(7) for c in cells}
    for i in P:
        for c in cells:
            m.Add(final[i, c] == sum(pv[i, k] for k in range(len(P[i])) if P[i][k][-1] == c))
    for r in "ABC":
        for i in range(7):
            m.AddExactlyOne(role[r, i, c] for c in cells)
    for c in cells:
        m.Add(sum(role[r, i, c] for r in "ABC" for i in range(7)) + sum(final[i, c] for i in range(7)) <= 1)
    # paths may not cross each other (any shared cell)
    for c in cells:
        users = [pv[i, k] for i in P for k in range(len(P[i])) if c in P[i][k]]
        if len(users) > 1:
            # at most one data path touches c
            pass
    occ = {(i, k): occupancy(i, P[i][k]) for i in P for k in range(len(P[i]))}
    for i, j in itertools.combinations(range(7), 2):
        for k1, p1 in enumerate(P[i]):
            s1 = set(p1)
            for k2, p2 in enumerate(P[j]):
                sh = s1 & set(p2)
                if sh and not (CROSS and all(disjoint(occ[i, k1][c], occ[j, k2][c]) for c in sh)):
                    m.AddBoolOr([pv[i, k1].Not(), pv[j, k2].Not()])
    # adjacency
    for i in range(7):
        for c in cells:
            for r in "AB":
                # role r_i at c requires D_i final at a neighbour of c
                m.AddBoolOr([role[r, i, c].Not()] + [final[i, d] for d in nb(c)])
            m.AddBoolOr([role["C", i, c].Not()] + [role["B", i, d] for d in nb(c)])
            m.AddBoolOr([role["C", i, c].Not()] + [role["A", i, d] for d in nb(c)])
    flips = []
    if KEEP_A:
        for i,j in [(0,4),(4,2),(2,3),(2,1),(3,6),(1,6),(6,5)]:
            for c in cells:
                m.AddBoolOr([role['A',i,c].Not()]+[role['A',j,d] for d in nb(c)])
    if KEEP_R3:
        flips=[m.NewBoolVar(f'flip{i}') for i in range(7)]
        prep={}
        for i in range(7):
            for c in cells:
                for r,other in [('B','C'),('C','B')]:
                    z=m.NewBoolVar(f'prep{r}{i}_{c}');prep[r,i,c]=z
                    m.Add(z==role[r,i,c]).OnlyEnforceIf(flips[i].Not())
                    m.Add(z==role[other,i,c]).OnlyEnforceIf(flips[i])
        path=[('B',0),('C',0),('B',2),('C',2),('C',1),('B',1),('B',6),('C',6),('C',5),('B',5),('C',3),('B',3),('C',4),('B',4)]
        for (r,i),(s,j) in zip(path,path[1:]):
            for c in cells:m.AddBoolOr([prep[r,i,c].Not()]+[prep[s,j,d] for d in nb(c)])
    for r in "ABC":
        for i, c in enumerate(PIN.get(r, [])):
            m.Add(role[r, i, c] == 1)
    for i, path in PIN.get("paths", {}).items():
        m.Add(pv[i, P[i].index(path)] == 1)
    R = m.NewIntVar(30, 60, "R")
    # timing
    for i in P:
        for k, p in enumerate(P[i]):
            arr, busy = hop_times(i, p)
            # data arrival
            m.Add(R >= arr).OnlyEnforceIf(pv[i, k])
            for c, bt in busy.items():
                for j in range(7):
                    m.Add(R >= bt + 2).OnlyEnforceIf([pv[i, k], role["A", j, c]])
                for r in "BC":
                    for j in range(7):
                        m.Add(R >= bt + BC_LATE).OnlyEnforceIf([pv[i, k], role[r, j, c]])
    late = {c: m.NewBoolVar(f"late{c}") for c in cells}
    m.Add(sum(late.values()) <= NLATE)
    sl = {i: m.NewBoolVar(f"slide{i}") for i in range(7)}
    if not slide:
        for i in range(7):
            m.Add(sl[i] == 0)
    else:
        m.Add(sum(sl.values()) <= slide)
    prep = {(i, c): m.NewBoolVar(f"prep{i}_{c}") for i in range(7) for c in cells}
    stay = {(i, c): m.NewBoolVar(f"stay{i}_{c}") for i in range(7) for c in cells}
    for i in range(7):
        m.Add(sum(prep[i, c] for c in cells) == sl[i])
        for c in cells:
            m.AddBoolAnd([role["A", i, c], sl[i].Not()]).OnlyEnforceIf(stay[i, c])
            m.AddBoolOr([role["A", i, c].Not(), sl[i], stay[i, c]])
            # prep cell adjacent to the final A cell
            m.AddBoolOr([prep[i, c].Not()] + [role["A", i, d] for d in nb(c)])
            m.Add(sum(role[r, j, c] for r in "ABC" for j in range(7)) + sum(final[j, c] for j in range(7)) == 0).OnlyEnforceIf(prep[i, c])
            if REL[c] < 99:
                m.Add(R - 2 - A_LEN >= REL[c]).OnlyEnforceIf(prep[i, c])
                m.Add(R - 3 >= REL[c]).OnlyEnforceIf([role["A", i, c], sl[i]])
                m.Add(R >= REL[c] + A_LEN).OnlyEnforceIf(stay[i, c])
    for c in cells:
        m.Add(sum(prep[i, c] for i in range(7)) <= 1)
    for i in P:
        for k, p in enumerate(P[i]):
            arr, busy = hop_times(i, p)
            for c, bt in busy.items():
                for j in range(7):
                    m.Add(R >= bt + A_LEN).OnlyEnforceIf([pv[i, k], stay[j, c]])
    for i in P:
        for k, p in enumerate(P[i]):
            arr, busy = hop_times(i, p)
            for c, bt in busy.items():
                for j in range(7):
                    m.Add(R - 2 - A_LEN >= bt).OnlyEnforceIf([pv[i, k], prep[j, c]])
                    m.Add(R - 3 >= bt).OnlyEnforceIf([pv[i, k], role["A", j, c], sl[j]])
    for c in cells:
        if REL[c] >= 99:
            continue
        for j in range(7):
            for r in "BC":
                m.Add(R >= REL[c] + BC_LEN).OnlyEnforceIf([role[r, j, c], late[c].Not()])
                m.Add(R >= REL[c] + BC_LATE).OnlyEnforceIf([role[r, j, c], late[c]])
    # B/C cells crossed by a data path count as late joiners
    for i in P:
        for k, p in enumerate(P[i]):
            for c in p[:-1]:
                for r in "BC":
                    for j in range(7):
                        m.AddImplication(role[r, j, c], late[c]).OnlyEnforceIf(pv[i, k])
    # connectivity by single-commodity flow
    def connected(xs, size, name):
        root = {c: m.NewBoolVar(f"{name}root{c}") for c in cells}
        m.AddExactlyOne(root.values())
        for c in cells:
            m.AddImplication(root[c], xs[c])
        f = {}
        for u in cells:
            for v in nb(u):
                f[u, v] = m.NewIntVar(0, size, f"{name}f{u}_{v}")
                m.Add(f[u, v] <= size * xs[u])
                m.Add(f[u, v] <= size * xs[v])
        for c in cells:
            inflow = sum(f[u, c] for u in nb(c))
            outflow = sum(f[c, v] for v in nb(c))
            m.Add(inflow - outflow == xs[c] - size * root[c])
    isA = {c: m.NewBoolVar(f"isA{c}") for c in cells}
    isBC = {c: m.NewBoolVar(f"isBC{c}") for c in cells}
    for c in cells:
        m.Add(isA[c] == sum(stay[i, c] + prep[i, c] for i in range(7)))
        m.Add(isBC[c] == sum(role[r, i, c] for r in "BC" for i in range(7)))
    if SEPARATE_CONNECTED:
        connected(isA, 7, "A")
        connected(isBC, 14, "BC")
    else:
        free = {c:m.NewBoolVar(f'free{c}') for c in cells}
        for c in cells:m.Add(free[c]+sum(final[i,c] for i in range(7))==1)
        connected(free,29,'ancilla')
        if A_CONNECTED:
            connected(isA,7,'aloneA')
            rest={c:m.NewBoolVar(f'rest{c}') for c in cells}
            for c in cells:m.Add(rest[c]+isA[c]==free[c])
            connected(rest,22,'restBC')
    # flag: some weight-3 X_L triple of A labels forms a grid path, its two end... (two of its data couple at R-1)
    flagdata = {i: m.NewBoolVar(f"fd{i}") for i in range(7)}
    if flag:
        fl = []
        early = {i: [] for i in range(7)}
        for tri in XL3:
            for mid in tri:
                for ends in itertools.permutations([x for x in tri if x != mid]):
                    v = m.NewBoolVar(f"flag{tri}{mid}{ends}")
                    fl.append((v, tri, mid, ends))
                    # mid adjacent to both ends
                    for c in cells:
                        for e in ends:
                            m.AddBoolOr([v.Not(), role["A", mid, c].Not()] + [role["A", e, d] for d in nb(c)])
                    # decoder: CX mid->end2 at R, CX end1->mid at R+1, MX end1 at R+2: mid and end2 couple at R-1
                    for x in (mid, ends[1]):
                        early[x].append(v)
        m.AddExactlyOne(f[0] for f in fl)
        for i in range(7):
            m.Add(flagdata[i] == sum(early[i]))
        for i in P:
            for k, p in enumerate(P[i]):
                arr, _ = hop_times(i, p)
                m.Add(R - 1 >= arr).OnlyEnforceIf([pv[i, k], flagdata[i]])
    if fixR is not None:
        m.Add(R == fixR)
    hel = []
    if helper:
        # a spare (non-role) cell adjacent to a flag data's final cell, free at R (CX D->helper at R, MX at R+1)
        for i in range(7):
            for c in cells:
                for x in nb(c):
                    v = m.NewBoolVar(f"hel{i}_{c}_{x}")
                    hel.append((v, i, c, x))
                    m.AddImplication(v, final[i, c])
                    m.AddImplication(v, flagdata[i])
                    m.Add(sum(role[r, j, x] for r in "ABC" for j in range(7)) + sum(final[j, x] for j in range(7)) == 0).OnlyEnforceIf(v)
                    if REL[x] < 99:
                        m.Add(R - 1 >= REL[x]).OnlyEnforceIf(v)
        m.Add(sum(h[0] for h in hel) >= helper)
    if maxR is not None:
        m.Add(R <= maxR)
    xch = []
    for n in range(xcheck):
        # late X-type plaquette check on one free centre x whose 4 neighbours are the plaquette's data
        opts = []
        for P_ in [(0,2,4,6),(1,2,5,6),(3,4,5,6),(0,1,4,5),(0,2,3,5),(1,2,3,4),(0,1,3,6)]:
            for x in cells:
                if len(nb(x)) < 4:
                    continue
                v = m.NewBoolVar(f"xchk{n}_{P_}_{x}")
                opts.append((v, P_, x))
                m.Add(sum(role[r, i, x] for r in "ABC" for i in range(7)) + sum(final[i, x] for i in range(7)) == 0).OnlyEnforceIf(v)
                if REL[x] < 99:
                    m.Add(R - 6 >= REL[x]).OnlyEnforceIf(v)
                for d in P_:
                    m.AddBoolOr([v.Not()] + [final[d, y] for y in nb(x)])
                    for k, p in enumerate(P[d]):
                        arr, busy = hop_times(d, p)
                        m.Add(R - 5 >= arr).OnlyEnforceIf([v, pv[d, k]])
                        if x in busy:
                            m.Add(R - 6 >= busy[x]).OnlyEnforceIf([v, pv[d, k]])
        m.AddExactlyOne(o[0] for o in opts)
        xch.append(opts)
    PLAQ = [(0,2,4,6),(1,2,5,6),(3,4,5,6),(0,1,4,5),(0,2,3,5),(1,2,3,4),(0,1,3,6)]
    chk = []
    for n in range(check):
        # late XZ plaquette check: ancillas a1,a2 adjacent, free (not a role) and released by R-8;
        # a1 adjacent to two plaquette data, a2 to the other two; plaquette data arrive by R-6.
        opts = []
        for P_ in PLAQ:
            splits = [(pair, tuple(x for x in P_ if x not in pair)) for pair in itertools.combinations(P_, 2)]
            splits = [s_ for s_ in splits if s_[0] < s_[1]]
            splits += [(tri, tuple(x for x in P_ if x not in tri)) for tri in itertools.combinations(P_, 3)]
            for pair, other in splits:
                for a1 in cells:
                    for a2 in nb(a1):
                        v = m.NewBoolVar(f"chk{n}_{P_}_{pair}_{a1}_{a2}")
                        opts.append((v, P_, pair, other, a1, a2))
                        for anc, ds in ((a1, pair), (a2, other)):
                            m.Add(sum(role[r, i, anc] for r in "ABC" for i in range(7)) + sum(final[i, anc] for i in range(7)) == 0).OnlyEnforceIf(v)
                            if REL[anc] < 99:
                                m.Add(R - 8 >= REL[anc]).OnlyEnforceIf(v)
                            for d in ds:
                                m.AddBoolOr([v.Not()] + [final[d, x] for x in nb(anc)])
                        for d in P_:
                            for k, p in enumerate(P[d]):
                                arr, busy = hop_times(d, p)
                                m.Add(R - 6 >= arr).OnlyEnforceIf([v, pv[d, k]])
                                for anc in (a1, a2):
                                    if anc in busy:
                                        m.Add(R - 8 >= busy[anc]).OnlyEnforceIf([v, pv[d, k]])
        m.AddExactlyOne(o[0] for o in opts)
        chk.append(opts)
    hops = sum(pv[i, k] * (len(P[i][k]) - 1) for i in P for k in range(len(P[i])))
    spare = []
    if spareW is not None:
        # data i has a spare neighbour x: x holds no role/final/prep, x is free from R-spareW on (prefix release and
        # every chosen hop path's busy time); objective: weighted count of data with a spare neighbour.
        fd = {i: m.NewBoolVar(f"sparedata{i}") for i in range(7)}
        for i in range(7):
            opts = []
            for x in cells:
                v = m.NewBoolVar(f"spare{i}_{x}")
                opts.append(v)
                spare.append((v, i, x))
                m.AddBoolOr([v.Not()] + [final[i, c] for c in nb(x)])
                m.Add(sum(role[r, j, x] for r in "ABC" for j in range(7)) + sum(final[j, x] for j in range(7))
                      + sum(prep[j, x] for j in range(7)) == 0).OnlyEnforceIf(v)
                if REL[x] < 99:
                    m.Add(R - spareW >= REL[x]).OnlyEnforceIf(v)
                for j in P:
                    for k, p_ in enumerate(P[j]):
                        bt = hop_times(j, p_)[1].get(x)
                        if bt is not None:
                            m.Add(R - spareW >= bt).OnlyEnforceIf([v, pv[j, k]])
            m.Add(fd[i] <= sum(opts))
        same = 0
        if near:
            same = sum(role[r, i, c] for r in "ABC" for i, c in enumerate(near[r]))
        for i in need:
            m.Add(fd[i] == 1)
        wsum = sum(int(round(spareWt[i] * 100)) * fd[i] for i in range(7))
        if prio == 'near':  # fewest moved roles first (smallest rebuild), then freed weight, then hops
            m.Maximize(same * 100000 + wsum * 10 - hops)
        else:
            m.Maximize(wsum * 1000 + same * 10 - hops)
    elif near:
        same = sum(role[r, i, c] for r in "ABC" for i, c in enumerate(near[r]))
        samep = sum(pv[i, k] for i in P for k in range(len(P[i])) if 'paths' in near and P[i][k] == near['paths'][i])
        m.Maximize(same * 1000 + samep * 1000 - hops * 10 - R * 100000)
    else:
        if COMPACT:
            enc=[(0,2),(1,5),(3,6),(0,4),(1,6),(3,5),(0,6),(1,2),(3,4)]
            coord={}
            for r in 'ABC':
                for i in range(7):
                    for axis in (0,1):
                        v=m.NewIntVar(0,5,'');coord[r,i,axis]=v
                        m.Add(v==sum(role[r,i,c]*(c//6 if axis==0 else c%6) for c in cells))
            dist=[]
            for r in 'ABC':
                for i,j in enc:
                    for axis in (0,1):
                        v=m.NewIntVar(0,5,'');m.AddAbsEquality(v,coord[r,i,axis]-coord[r,j,axis]);dist.append(v)
            m.Minimize(R*100+20*sum(dist)+10*hops)
        else:m.Minimize(R * 100 + hops)
    s = cp_model.CpSolver()
    s.parameters.num_workers = int(__import__('os').environ.get('WORKERS', 16))
    s.parameters.max_time_in_seconds = 180
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return dict(status=s.StatusName(st))
    out = dict(status=s.StatusName(st), R=s.Value(R), hops=s.Value(hops))
    out["bc_pair_flips"] = [i for i in range(7) if flips and s.Value(flips[i])]
    out["paths"] = {i: P[i][k] for i in P for k in range(len(P[i])) if s.Value(pv[i, k])}
    for r in "ABC":
        out[r] = [next(c for c in cells if s.Value(role[r, i, c])) for i in range(7)]
    out["D"] = [out["paths"][i][-1] for i in range(7)]
    out["late"] = [c for c in cells if s.Value(late[c])]
    out["slide"] = {i: next(c for c in cells if s.Value(prep[i, c])) for i in range(7) if s.Value(sl[i])}
    out["flagdata"] = [i for i in range(7) if s.Value(flagdata[i])]
    out["flag"] = [dict(tri=f[1], mid=f[2], end1=f[3][0], end2=f[3][1]) for f in fl if s.Value(f[0])] if flag else []
    out["arrival"] = {i: hop_times(i, out["paths"][i])[0] for i in range(7)}
    out["helpers"] = [dict(data=h[1], cell=h[2], helper=h[3]) for h in hel if s.Value(h[0])]
    out["xchecks"] = [[dict(P=o[1], x=o[2]) for o in opts if s.Value(o[0])] for opts in xch]
    out["spare"] = [dict(data=v_[1], cell=v_[2]) for v_ in spare if s.Value(v_[0])]
    out["checks"] = [[dict(P=o[1], pair=o[2], other=o[3], a1=o[4], a2=o[5]) for o in opts if s.Value(o[0])] for opts in chk]
    return out


def draw(o):
    g = [["  ."] * 6 for _ in range(6)]
    for i, c in enumerate(o["D"]):
        g[c // 6][c % 6] = f" D{i}"
    for r in "ABC":
        for i, c in enumerate(o[r]):
            g[c // 6][c % 6] = f" {r}{i}"
    for i, c in o.get("slide", {}).items():
        g[c // 6][c % 6] = f" a{i}"
    for h in o.get("helpers", []):
        g[h["helper"] // 6][h["helper"] % 6] = "  h"
    for ch in o.get("xchecks", []):
        for x in ch:
            g[x["x"] // 6][x["x"] % 6] = "  X"
    for sp in o.get("spare", []):
        g[sp["cell"] // 6][sp["cell"] % 6] = "  s"
    for ch in o.get("checks", []):
        for x in ch:
            g[x["a1"] // 6][x["a1"] % 6] = " k1"
            g[x["a2"] // 6][x["a2"] % 6] = " k2"
    return "\n".join("".join(row) for row in g)


if __name__ == "__main__":
    flag = '--noflag' not in sys.argv
    a = [int(x) for x in sys.argv[1:] if not x.startswith('--')]
    keys = ["A_LEN", "BC_LEN", "BC_LATE", "NLATE", "MAXH", "check", "slide", "xcheck", "helper"]
    kw = dict(zip(keys, a))
    o = solve(flag=flag, **kw)
    print(json.dumps(o))
    if "D" in o:
        print(draw(o))
