"""CP-SAT synthesis of a nearest-neighbour CNOT circuit that prepares a CSS block state.

State: sum over x in V of |x> on the block cells, V spanned by `rows` (lists of code positions),
helpers end in |0>. Start: k pivot cells in |+> (chosen by the solver), all else |0>. CX(u->v) maps
x_v ^= x_u. Layers: each cell in at most one CX per layer; only edges between `avail` cells.
Minimizes the CX count, then the depth.

    from synth import synth
    ops, pivots = synth(cells, rows, avail, depth)   # ops: list of layers of (control, target)
"""
from ortools.sat.python import cp_model

COLS = 6


def nbrs(q):
    r, c = divmod(q, COLS)
    return [rr * COLS + cc for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
            if 0 <= rr < 6 and 0 <= cc < COLS]


def synth(cells, rows, avail, depth, seconds=60, workers=8, max_cx=None):
    """cells[i]: cell of code position i; rows: generator supports (code positions); avail: cells usable."""
    return synth_cells([{cells[i] for i in r} for r in rows], avail, depth, seconds, workers, max_cx)


def synth_cells(rows, avail, depth, seconds=60, workers=8, max_cx=None, hint=None, seed=None):
    """rows: generator supports as sets of cells (several blocks at once: concatenate their rows)."""
    avail = sorted(set(avail).union(*rows))
    k = len(rows)
    target = {v: [1 if v in r else 0 for r in rows] for v in avail}
    edges = [(u, v) for u in avail for v in nbrs(u) if v in avail]
    m = cp_model.CpModel()
    one = m.NewBoolVar("one")
    m.Add(one == 1)
    piv = {(j, v): m.NewBoolVar("") for j in range(k) for v in avail}
    for j in range(k):
        m.AddExactlyOne(piv[(j, v)] for v in avail)
    for v in avail:
        m.AddAtMostOne(piv[(j, v)] for j in range(k))
    col = [{(v, j): piv[(j, v)] for v in avail for j in range(k)}]
    sel = []
    for t in range(depth):
        s = {e: m.NewBoolVar("") for e in edges}
        sel.append(s)
        for v in avail:
            m.AddAtMostOne([s[e] for e in edges if v in e])
        nxt = {}
        for v in avail:
            ins = [(u, v) for u in nbrs(v) if (u, v) in s]
            for j in range(k):
                w = []
                for e in ins:
                    z = m.NewBoolVar("")
                    m.AddMultiplicationEquality(z, [s[e], col[t][(e[0], j)]])
                    w.append(z)
                b = m.NewBoolVar("")
                if w:
                    m.AddBoolXOr([b, col[t][(v, j)], *w, one])     # b = col ^ (incoming control bit)
                else:
                    m.Add(b == col[t][(v, j)])
                nxt[(v, j)] = b
        col.append(nxt)
    # final basis = A * rows (A invertible follows from rank preservation)
    A = {(j, i): m.NewBoolVar("") for j in range(k) for i in range(k)}
    for v in avail:
        for j in range(k):
            terms = [A[(j, i)] for i in range(k) if target[v][i]]
            if terms:
                m.AddBoolXOr([col[depth][(v, j)], *terms, one])
            else:
                m.Add(col[depth][(v, j)] == 0)
    n_cx = sum(s[e] for s in sel for e in edges)
    used = [m.NewBoolVar("") for _ in range(depth)]
    for t in range(depth):
        for e in edges:
            m.AddImplication(sel[t][e], used[t])
        if t:
            m.AddImplication(used[t], used[t - 1])
    if max_cx is not None:
        m.Add(n_cx <= max_cx)
    tie = 0
    if seed is not None:
        import random
        rng = random.Random(seed)
        tie = sum(rng.randint(0, 3) * s[e] for s in sel for e in edges)
    m.Minimize(n_cx * 1000 + 10 * sum(used) + tie)
    sol = cp_model.CpSolver()
    sol.parameters.max_time_in_seconds = seconds
    sol.parameters.num_workers = workers
    st = sol.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    ops = [[e for e in edges if sol.Value(sel[t][e])] for t in range(depth)]
    ops = [l for l in ops if l]
    pivots = [next(v for v in avail if sol.Value(piv[(j, v)])) for j in range(k)]
    return ops, pivots, sol.StatusName(st)


def check(cells, rows, avail, ops, pivots):
    """Simulate the linear map: span of final basis restricted to cells == span(rows), helpers zero."""
    avail = sorted(set(avail) | set(cells))
    vecs = [{p} for p in pivots]
    for layer in ops:
        for u, v in layer:
            for x in vecs:
                if u in x:
                    x ^= {v}
    for x in vecs:
        if any(q not in cells for q in x):
            return False

    def rank(vs):
        vs = [set(v) for v in vs]
        r = 0
        cols = sorted({q for v in vs for q in v})
        for c in cols:
            piv = next((i for i in range(r, len(vs)) if c in vs[i]), None)
            if piv is None:
                continue
            vs[r], vs[piv] = vs[piv], vs[r]
            for i in range(len(vs)):
                if i != r and c in vs[i]:
                    vs[i] ^= vs[r]
            r += 1
        return r
    want = [{cells[i] for i in r} for r in rows]
    return rank(vecs) == len(rows) and rank(vecs + want) == len(rows)


def _path(src, dst, ok, cost):
    """Cheapest grid path src..dst through cells in ok (Dijkstra; cost(cell) for entering a cell)."""
    import heapq
    dist, prev, pq = {src: 0}, {}, [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == dst:
            break
        if d > dist[u]:
            continue
        for v in nbrs(u):
            if v not in ok:
                continue
            nd = d + (0 if v == dst else cost(v))
            if nd < dist.get(v, 1e9):
                dist[v], prev[v] = nd, u
                heapq.heappush(pq, (nd, v))
    if dst not in dist:
        return None
    p = [dst]
    while p[-1] != src:
        p.append(prev[p[-1]])
    return p[::-1]


def greedy(rows, avail, order=None, rng=None):
    """Fast constructive synthesis (not minimal): rows as cell sets; returns (ops, pivots) with ops a
    flat CX list and pivots[j] the |+> cell of row j (all prepared at the start). Rows are processed
    in `order`; a pivot must lie in no row processed before its own. Each row's pivot value is XORed
    into its other cells along cheapest paths: a zero intermediate costs 2 CX per hop (chain +
    uncompute), a busy one 4 (long-range CX gadget)."""
    import random
    rng = rng or random.Random(0)
    avail = set(avail).union(*rows)
    order = order or list(range(len(rows)))
    pivots, seen = {}, set()
    for j in order:
        cand = [q for q in rows[j] if q not in seen and q not in pivots.values()]
        if not cand:
            raise ValueError(f"row {j} has no pivot outside earlier rows")
        pivots[j] = rng.choice(cand)
        seen |= rows[j]
    val = {q: set() for q in avail}            # current value of each cell: set of row labels
    for j, p in pivots.items():
        val[p] = {j}
    ops = []

    def cx(u, v):
        ops.append((u, v))
        val[v] = val[v] ^ val[u]
    for j in order:
        R, p = rows[j], pivots[j]
        assert val[p] == {j}
        exact = {p}                            # cells holding exactly a_j
        todo = set(R) - {p}
        while todo:
            best = None
            for t in todo:
                for s in exact:
                    path = _path(s, t, avail, lambda v: 1 if not val[v] else 3)
                    if path and (best is None or len(path) < len(best)):
                        best = path
            path, t = best, best[-1]
            mid = path[1:-1]
            m = len(path) - 1
            if not mid:
                cx(path[0], t)
            elif all(not val[v] for v in mid):
                for i in range(m):
                    cx(path[i], path[i + 1])
                for i in range(m - 2, -1, -1):
                    cx(path[i], path[i + 1])
            else:
                # long-range CX v0 -> vm through busy cells: 4(m-1) CX (ladders up, down, up, down)
                for i in range(m):
                    cx(path[i], path[i + 1])
                for i in range(m - 2, -1, -1):
                    cx(path[i], path[i + 1])
                for i in range(1, m):
                    cx(path[i], path[i + 1])
                for i in range(m - 2, 0, -1):
                    cx(path[i], path[i + 1])
            if val[t] == {j}:
                exact.add(t)
            todo.discard(t)
    want = {q: {j for j, r in enumerate(rows) if q in r} for q in avail}
    assert val == want, "greedy synthesis left a wrong state"
    return ops, [pivots[j] for j in range(len(rows))]


def layers(ops, busy0=None):
    """ASAP layering of a CX list keeping each qubit's order."""
    ready, out = dict(busy0 or {}), []
    for u, v in ops:
        t = max(ready.get(u, 0), ready.get(v, 0))
        while len(out) <= t:
            out.append([])
        out[t].append((u, v))
        ready[u] = ready[v] = t + 1
    return out


HAM_POS = [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6]]


def z_class(zset, cells):
    """Class of a Z error on a |+_L> block: 0 if equivalent to weight <= 1 (benign: B catches it, and it
    cannot combine with one data Z error into Z_L), 1 if equivalent to Z_L x (weight <= 1)."""
    e = [1 if q in zset else 0 for q in cells]
    syn = sum(1 << k for k, S in enumerate(HAM_POS) if sum(e[i] for i in S) % 2)
    w = sum(e)
    # minimal representative: syndrome s -> weight-1 at code position s-1; logical bit = parity mismatch
    w_min = 0 if syn == 0 else 1
    return (w - w_min) % 2 if True else 0


def x_syndrome(xset, cells):
    e = [1 if q in xset else 0 for q in cells]
    return sum(1 << k for k, S in enumerate(HAM_POS) if sum(e[i] for i in S) % 2)


def dangerous_z(layers_, pivots, cells, avail, p=1e-3, idle_after=0):
    """Total probability of single faults (judge noise: CX depolarizing p/15 per pair, reset flips p,
    idle p/3 per Pauli per step) in a block prep that leave a Z error of class 1 on the block while
    its X part stays invisible to the block's own Z readout (otherwise the shot is rejected)."""
    avail = sorted(set(avail) | set(cells) | {q for l in layers_ for e in l for q in e})
    first = {}
    for t, l in enumerate(layers_):
        for u, v in l:
            first.setdefault(u, t)
            first.setdefault(v, t)
    for q in cells:
        first.setdefault(q, 0)

    def propagate(z, x, t0):
        """Z/X sets just after layer t0-1 -> at the end. CX(u->v): X_u -> X_u X_v, Z_v -> Z_u Z_v."""
        z, x = set(z), set(x)
        for l in layers_[t0:]:
            for u, v in l:
                if u in x:
                    x ^= {v}
                if v in z:
                    z ^= {u}
        return z, x
    tot = 0.0
    T = len(layers_)
    for t, l in enumerate(layers_):
        busy = set()
        for u, v in l:
            busy |= {u, v}
            for pu in "IXYZ":
                for pv in "IXYZ":
                    if pu == pv == "I":
                        continue
                    z = {q for q, P in ((u, pu), (v, pv)) if P in "YZ"}
                    x = {q for q, P in ((u, pu), (v, pv)) if P in "XY"}
                    zz, xx = propagate(z, x, t + 1)
                    if z_class(zz & set(cells), cells) and not x_syndrome(xx & set(cells), cells):
                        tot += p / 15
        # idle on started, unfinished qubits in this layer
        for q in avail:
            if q in busy or first.get(q, T) >= t:
                continue
            last = max((tt for tt, ll in enumerate(layers_) for e in ll if q in e), default=-1)
            if q not in cells and t > last:
                continue
            for P in "XYZ":
                z = {q} if P in "YZ" else set()
                x = {q} if P in "XY" else set()
                zz, xx = propagate(z, x, t)
                if z_class(zz & set(cells), cells) and not x_syndrome(xx & set(cells), cells):
                    tot += p / 3
    # reset flips: pivots (RX) get Z with prob p right after their reset
    for q in pivots:
        zz, _ = propagate({q}, set(), first[q])
        if z_class(zz & set(cells), cells):
            tot += p
    return tot
