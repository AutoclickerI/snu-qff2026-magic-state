"""CP-SAT synthesis of the correlated rank-3 B/C resource on v36c's 14-cell B/C path (plus optional helpers).

Layers t = 0..D-1 run at ticks T0+t; B->C stays at tick T0+D (= 44). Hard: target span {(g,g)}, per-cell
availability, at most 3 pivots, first-order clean (an X fault C cannot see leaves no B X error),
robust (an X fault C sees on one bit leaves no B X error, or exactly that bit's error).
Objective: Z exposure (loaded cell-ticks) + CX count weight.  Every solution is re-verified outside.
"""
import sys, json, argparse, time, itertools
from ortools.sat.python import cp_model
from qcirc import adjacent

B = [6, 26, 13, 11, 4, 23, 27]
C = [12, 25, 19, 17, 5, 29, 28]
ROWS = [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6]]
CELLS = B + C


def col(i):  # generator column of B/C index i (simplex code = Hamming parity-check columns)
    return sum(((i in row) << j) for j, row in enumerate(ROWS))


def endpoint_h(q):
    """11 bits: 4-bit B signature (3 syndrome + parity) of the B-part, 7-bit literal diff."""
    h = [0] * 11
    if q in B:
        i = B.index(q)
        for j, row in enumerate(ROWS):
            h[j] = int(i in row)
        h[3] = 1
        h[4 + i] = 1
    else:
        h[4 + C.index(q)] = 1
    return h


def build(D, avail, cap=None, w_cx=1, w_z=1, robust=True, fix=None, forbid=(), pivot_ok=None, max_layer_end=None, soft=None, helpers=(), flags_only=False, force_pivots=(), robust_cells=None, midmeas=False, w_meas=10, hard_cells=()):
    """soft: None (robust hard) or (w_idle, w_cx_src): robust violations allowed at that cost per source."""
    m = cp_model.CpModel()
    CELLS = B + C + list(helpers)
    NH = len(helpers)
    NS = 11 + NH + (1 if midmeas else 0)   # last bit: parity of mid-preparation Z measurements flipped
    E = [(u, v) for u in CELLS for v in CELLS if adjacent(u, v)]
    sel = [{e: m.NewBoolVar(f's{t}_{e[0]}_{e[1]}') for e in E} for t in range(D)]
    for t in range(D):
        for e in E:
            if t < avail[e[0]] or t < avail[e[1]]:
                m.Add(sel[t][e] == 0)
            if any(q in (18, 31, 34, 35) for q in e) and t >= D - 1:
                m.Add(sel[t][e] == 0)  # those helpers are reset at 44 for C readout copies
            if flags_only and e[0] in helpers:
                m.Add(sel[t][e] == 0)
        for q in CELLS:
            m.AddAtMostOne([sel[t][e] for e in E if q in e])
    used = [{q: m.NewBoolVar(f'u{t}_{q}') for q in CELLS} for t in range(D)]
    for t in range(D):
        for q in CELLS:
            inc = [sel[t][e] for e in E if q in e]
            m.AddMaxEquality(used[t][q], inc)
    meas = None
    if midmeas:
        meas = [{q: m.NewBoolVar(f'm{t}_{q}') for q in CELLS} for t in range(D)]
        for t in range(D):
            for q in CELLS:
                m.AddImplication(meas[t][q], used[t][q].Not())
                if t == 0:
                    m.Add(meas[t][q] == 0)
    nx = 3
    x = [{q: [m.NewBoolVar(f'x{t}_{q}_{b}') for b in range(nx)] for q in CELLS} for t in range(D + 1)]
    h = [{q: [m.NewBoolVar(f'h{t}_{q}_{b}') for b in range(NS)] for q in CELLS} for t in range(D + 1)]
    for q in CELLS:
        if q in helpers:
            v = 0
            hv = [0] * NS
            hv[11 + list(helpers).index(q)] = 1
        else:
            i = (B + C).index(q) % 7
            v = col(i)
            hv = endpoint_h(q) + [0] * (NS - 11)
        for b in range(nx):
            m.Add(x[D][q][b] == ((v >> b) & 1))
        for b in range(NS):
            m.Add(h[D][q][b] == hv[b])

    def xor_eq(z, a, c, lit):  # z = a ^ c if lit
        m.AddBoolXOr([z, a, c, True]).OnlyEnforceIf(lit) if False else None
        k = m.NewIntVar(0, 1, '')
        m.Add(z + a + c == 2 * k).OnlyEnforceIf(lit)
        m.Add(k == 0).OnlyEnforceIf(lit.Not())  # no free auxiliaries (enumeration)

    for t in range(D):
        for q in CELLS:
            ins = [e for e in E if e[1] == q]
            outs = [e for e in E if e[0] == q]
            tin = m.NewBoolVar(''); m.AddMaxEquality(tin, [sel[t][e] for e in ins])
            cout = m.NewBoolVar(''); m.AddMaxEquality(cout, [sel[t][e] for e in outs])
            for b in range(nx):
                m.Add(x[t][q][b] == x[t + 1][q][b]).OnlyEnforceIf(tin.Not())
                for e in ins:
                    xor_eq(x[t][q][b], x[t + 1][q][b], x[t + 1][e[0]][b], sel[t][e])
            for b in range(NS):
                if midmeas and b == NS - 1:
                    # not a control: the flag bit flips if q is measured at this layer
                    kk = m.NewIntVar(0, 1, '')
                    m.Add(h[t][q][b] + h[t + 1][q][b] + meas[t][q] == 2 * kk).OnlyEnforceIf(cout.Not())
                    m.Add(kk == 0).OnlyEnforceIf(cout)
                else:
                    m.Add(h[t][q][b] == h[t + 1][q][b]).OnlyEnforceIf(cout.Not())
                for e in outs:
                    xor_eq(h[t][q][b], h[t + 1][q][b], h[t + 1][e[1]][b], sel[t][e])
    # pivots: nonzero start vectors, <= 3
    nz = [{q: m.NewBoolVar(f'nz{t}_{q}') for q in CELLS} for t in range(D + 1)]
    for t in range(D + 1):
        for q in CELLS:
            m.AddMaxEquality(nz[t][q], x[t][q])
    m.Add(sum(nz[0][q] for q in CELLS) <= 3)
    for q in helpers:
        m.Add(nz[0][q] == 0)
    for q in force_pivots:
        m.Add(nz[0][q] == 1)
    if pivot_ok is not None:
        for q in CELLS:
            if q not in pivot_ok:
                m.Add(nz[0][q] == 0)
    # alive: used at some layer <= t
    alive = [{q: m.NewBoolVar(f'a{t}_{q}') for q in CELLS} for t in range(D + 1)]
    for q in CELLS:
        for t in range(D + 1):
            m.AddMaxEquality(alive[t][q], [used[s][q] for s in range(min(t + 1, D))])

    viols = []

    nmeas = 0
    if midmeas:
        for t in range(D):
            for q in CELLS:
                for b in range(nx):
                    m.Add(x[t][q][b] == 0).OnlyEnforceIf(meas[t][q])
                m.AddImplication(meas[t][q], alive[t][q])
        nmeas = sum(meas[t][q] for t in range(D) for q in CELLS)

    def constrain(sig, lit, w=0, cells=None):
        """sig: 11 literals (bools) of a fault source; lit: enforcement (source exists)."""
        dif = sig[4:]   # literal C diff bits and flag bits: all are detectors
        s = sig[:4]
        esc = []
        rob = robust and (robust_cells is None or cells is None or set(cells) <= set(robust_cells))
        if soft is not None and w and not (cells is not None and hard_cells and set(cells) <= set(hard_cells)):
            v = m.NewBoolVar('viol')
            viols.append((w, v))
            esc = [v]
        # F1: diff == 0 -> s == 0
        for b in range(4):
            m.AddBoolOr(dif + [s[b].Not(), lit.Not()])
        if rob:
            for i in range(7):
                cond = [d.Not() if j == i else d for j, d in enumerate(dif)]  # (dif == e_i) fails if any is true; literals whose truth breaks diff==e_i
                ci = col(i)
                for k in range(3):
                    if (ci >> k) & 1:
                        # s_k == s_par
                        m.AddBoolOr(cond + esc + [lit.Not(), s[k].Not(), s[3]])
                        m.AddBoolOr(cond + esc + [lit.Not(), s[k], s[3].Not()])
                    else:
                        m.AddBoolOr(cond + esc + [lit.Not(), s[k].Not()])

    for t in range(D + 1):
        for q in CELLS:
            if soft is None or t == 0:
                constrain(h[t][q], alive[t][q], 0 if soft is None else soft[0], cells=[q])
            else:
                # idle at layer t-1 -> X or Y (2p/3); used -> single-qubit X part of a CX (4p/15)
                ai = m.NewBoolVar(''); m.AddBoolAnd([alive[t][q], used[t - 1][q].Not()]).OnlyEnforceIf(ai)
                m.AddBoolOr([alive[t][q].Not(), used[t - 1][q], ai])
                au = m.NewBoolVar(''); m.AddBoolAnd([alive[t][q], used[t - 1][q]]).OnlyEnforceIf(au)
                m.AddBoolOr([alive[t][q].Not(), used[t - 1][q].Not(), au])
                constrain(h[t][q], ai, soft[0], cells=[q])
                constrain(h[t][q], au, soft[1], cells=[q])
    for t in range(D):
        for e in E:
            u, v = e
            if u > v:
                continue
            both = m.NewBoolVar('')
            m.AddMaxEquality(both, [sel[t][(u, v)], sel[t][(v, u)]])
            sig = []
            for b in range(NS):
                z = m.NewBoolVar('')
                xor_eq(z, h[t + 1][u][b], h[t + 1][v][b], both)
                m.Add(z == 0).OnlyEnforceIf(both.Not())
                sig.append(z)
            constrain(sig, both, 0 if soft is None else soft[1], cells=[u, v])
    ncx = sum(sel[t][e] for t in range(D) for e in E)
    if cap is not None:
        m.Add(ncx <= cap)
    for t, e in forbid:
        m.Add(sel[t][e] == 0)
    zexp = sum(nz[t + 1][q] for t in range(D) for q in CELLS)
    vcost = sum(w * v for w, v in viols) if viols else 0
    m.Minimize(w_z * zexp + w_cx * ncx + vcost + w_meas * nmeas)
    m._meas = meas
    m._viols = viols
    m._cells = CELLS
    return m, sel, x, nz, E, ncx, zexp


def solve(D, avail, seconds=60, workers=8, seed=0, **kw):
    kw.setdefault('helpers', ())
    m, sel, x, nz, E, ncx, zexp = build(D, avail, **kw)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_search_workers = workers
    s.parameters.random_seed = seed
    s.parameters.cp_model_presolve = False
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return dict(status=s.StatusName(st))
    ops = [[list(e) for e in E if s.Value(sel[t][e])] for t in range(D)]
    piv = {q: [s.Value(b) for b in x[0][q]] for q in m._cells if s.Value(nz[0][q])}
    nv = sum(s.Value(v) for w, v in m._viols)
    mids = [[t, q] for t in range(D) for q in m._cells if m._meas is not None and s.Value(m._meas[t][q])]
    return dict(status=s.StatusName(st), ops=ops, pivots=piv, cx=s.Value(ncx), zexp=s.Value(zexp), nviol=nv, mids=mids,
                obj=s.ObjectiveValue(), bound=s.BestObjectiveBound(), seconds=s.WallTime())


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--D', type=int, default=11)
    ap.add_argument('--T0', type=int, default=33)
    ap.add_argument('--seconds', type=float, default=60)
    ap.add_argument('--workers', type=int, default=8)
    ap.add_argument('--cap', type=int, default=None)
    ap.add_argument('--wz', type=int, default=1)
    ap.add_argument('--wcx', type=int, default=1)
    ap.add_argument('--norobust', action='store_true')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--soft', default=None, help='w_idle,w_cx violation costs')
    ap.add_argument('--reuse', action='store_true', help='q4/q6 as |+> pivots after their literal MX, q19 at 33')
    ap.add_argument('--flags_only', action='store_true')
    ap.add_argument('--force_pivots', default='')
    ap.add_argument('--robust_cells', default='')
    ap.add_argument('--midmeas', action='store_true')
    ap.add_argument('--hard_cells', default='')
    ap.add_argument('--wmeas', type=int, default=10)
    ap.add_argument('--helpers', default='', help='comma list of flag/routing helper cells, e.g. 18,24,31,32,33,34,35')
    ap.add_argument('--out', default=None)
    ap.add_argument('--base', default='v36c', help='v36c | v36d (cell availability of the base)')
    a = ap.parse_args()
    # earliest CX tick per cell in v36c's surroundings
    first_tick = {4: 37, 5: 35, 6: 42, 11: 31, 13: 34, 19: 34}
    if a.base == 'v36d':
        first_tick.update({11: 33, 12: 33, 25: 34})  # INTEG pair on q11 until 31, echo helpers q12 (MX@31), q25 (R@32)
    if a.reuse:
        first_tick.update({4: 36, 6: 41})
    helpers = [int(q) for q in a.helpers.split(',') if q]
    avail = {q: max(0, first_tick.get(q, 0) - a.T0) for q in CELLS + helpers}
    soft = tuple(map(int, a.soft.split(','))) if a.soft else None
    r = solve(a.D, avail, a.seconds, a.workers, a.seed, cap=a.cap, w_z=a.wz, w_cx=a.wcx, robust=not a.norobust, soft=soft, helpers=helpers, flags_only=a.flags_only, force_pivots=[int(q) for q in a.force_pivots.split(',') if q], robust_cells=[int(q) for q in a.robust_cells.split(',') if q] or None, midmeas=a.midmeas, w_meas=a.wmeas, hard_cells=[int(q) for q in a.hard_cells.split(',') if q])
    r.update(D=a.D, T0=a.T0, avail=avail, policy='reuse' if a.reuse else 'default')
    print(json.dumps({k: v for k, v in r.items() if k != 'ops'}))
    if a.out and 'ops' in r:
        json.dump(r, open(a.out, 'w'), indent=1)
