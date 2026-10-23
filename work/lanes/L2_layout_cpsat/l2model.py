"""L2 layout variants on gmodel.GModel plus a CP-SAT generator of feasible (interleaved) final-round
schedules for any GModel layout. Validity: gmodel.feasible rules + the nine tile-pair parity
conditions (L1/cpsat.py) as CP-SAT constraints; Stim (GModel.cost) stays the oracle."""
import random
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/me_layout")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import gmodel as G  # noqa: E402
from ortools.sat.python import cp_model  # noqa: E402

D = {xy: i for i, xy in enumerate(G.DATA0)}
d0, d1, d2, d3, d4, d5, d6 = range(7)
assert G.DATA0[d1] == (2, 3) and G.DATA0[d3] == (4, 0) and G.DATA0[d5] == (3, 2) and G.DATA0[d4] == (3, 0)

# tile-1 options: (moves, extras, xmem)
T1 = {
    "v6": ({}, [(1, (1, 3), (1, 2))], {(1, d1): (1, 3)}),
    "A1": ({d1: [(1, 3)]}, [(1, (2, 3), (2, 2))], {(1, d1): (2, 3)}),
    "A2": ({d1: [(1, 3)]}, [], {}),
    # A1 + (3,3) hanging off the (2,3) extra takes d5's tile-1 X part
    "C1": ({d1: [(1, 3)]}, [(1, (2, 3), (2, 2)), (1, (3, 3), (2, 3))], {(1, d1): (2, 3), (1, d5): (3, 3)}),
    # (2,3) only relays (3,3); d1's X goes to (1,2)
    "C2": ({d1: [(1, 3)]}, [(1, (2, 3), (2, 2)), (1, (3, 3), (2, 3))], {(1, d5): (3, 3)}),
    # A1 + relay (0,2) -> (0,1) takes d2's tile-1 X part
    "A1h01": ({d1: [(1, 3)]}, [(1, (2, 3), (2, 2)), (1, (0, 2), (1, 2)), (1, (0, 1), (0, 2))],
              {(1, d1): (2, 3), (1, d2): (0, 1)}),
}
# tile-2 options; "m" = d3 hops (4,0)->(5,0)->(5,1)
T2 = {
    "e42": ({}, [(2, (4, 2), (4, 1))], {(2, d5): (4, 2)}),
    # relay (5,1) -> (5,0) takes d3's X part (no move)
    "h50": ({}, [(2, (5, 1), (4, 1)), (2, (5, 0), (5, 1))], {(2, d3): (5, 0)}),
    "h50_42": ({}, [(2, (5, 1), (4, 1)), (2, (5, 0), (5, 1)), (2, (4, 2), (4, 1))], {(2, d3): (5, 0), (2, d5): (4, 2)}),
    "none": ({}, [], {}),
    "m": ({d3: [(5, 0), (5, 1)]}, [], {}),
    "m40": ({d3: [(5, 0), (5, 1)]}, [(2, (4, 0), (4, 1))], {(2, d4): (4, 0)}),
    "m42": ({d3: [(5, 0), (5, 1)]}, [(2, (4, 2), (4, 1))], {(2, d5): (4, 2)}),
    "m40_42": ({d3: [(5, 0), (5, 1)]}, [(2, (4, 0), (4, 1)), (2, (4, 2), (4, 1))], {(2, d4): (4, 0), (2, d5): (4, 2)}),
    "m40_50": ({d3: [(5, 0), (5, 1)]}, [(2, (4, 0), (4, 1)), (2, (5, 0), (4, 0))], {(2, d4): (4, 0), (2, d3): (5, 0)}),
    "m42_52": ({d3: [(5, 0), (5, 1)]}, [(2, (4, 2), (4, 1)), (2, (5, 2), (4, 2))], {(2, d5): (4, 2), (2, d3): (5, 2)}),
    "m40_42_50": ({d3: [(5, 0), (5, 1)]}, [(2, (4, 0), (4, 1)), (2, (4, 2), (4, 1)), (2, (5, 0), (4, 0))],
                  {(2, d4): (4, 0), (2, d5): (4, 2), (2, d3): (5, 0)}),
    "m40_42_52": ({d3: [(5, 0), (5, 1)]}, [(2, (4, 0), (4, 1)), (2, (4, 2), (4, 1)), (2, (5, 2), (4, 2))],
                  {(2, d4): (4, 0), (2, d5): (4, 2), (2, d3): (5, 2)}),
}


# Z-only extras (zmodel.ZModel): (moves, extras, zmem, zext)
Z1 = {
    "v6z": ({}, [(1, (1, 3), (1, 2))], {(1, d1): (1, 3)}, {(1, 3)}),
    "A1z": ({d1: [(1, 3)]}, [(1, (2, 3), (2, 2))], {(1, d1): (2, 3)}, {(2, 3)}),  # mirrored hop leaves (2,3) in |+>
}
Z2 = {"z42": ({}, [(2, (4, 2), (4, 1))], {(2, d5): (4, 2)}, {(4, 2)})}


def variant(name):
    a, b = name.split("+")
    if a in Z1 or b in Z2:
        import zmodel
        mv, ex, xm, zm, zx = {}, [], {}, {}, set()
        for tok, X, Z in ((a, T1, Z1), (b, T2, Z2)):
            if tok in Z:
                m_, e_, z_, s_ = Z[tok]
                mv.update(m_); ex += e_; zm.update(z_); zx |= s_
            else:
                m_, e_, x_ = X[tok]
                mv.update(m_); ex += e_; xm.update(x_)
        zh = {d for d, path in mv.items() if any(c in zx for c in [G.DATA0[d]] + path[:-1])}
        return zmodel.ZModel(moves=mv, extras=ex, xmem=xm, zmem=zm, zext=zx, zhops=zh)
    m1, e1, x1 = T1[a]
    m2, e2, x2 = T2[b]
    return G.GModel(moves={**m1, **m2}, extras=e1 + e2, xmem={**x1, **x2})


class Gen:
    """CP-SAT over layers 2..lmax for every key of a GModel, plus orientation booleans."""

    def __init__(self, m, lmax, fix_orient=None, parity=None):
        if parity is None:
            parity = not getattr(m, "zext", None)
        self.m, self.lmax = m, lmax
        c = self.c = cp_model.CpModel()
        self.v = {k: c.new_int_var(2, lmax, str(k)) for k in m.keys}
        self.o = [c.new_bool_var(f"o{t}") for t in range(3)]
        if fix_orient is not None:
            for t in range(3):
                c.add(self.o[t] == fix_orient[t])
        perq = {}
        for k in m.keys:
            for q in m.qubits_of(k, [0, 0, 0]):
                perq.setdefault(q, []).append(k)
        for ks in perq.values():
            if len(ks) > 1:
                c.add_all_different([self.v[k] for k in ks])
        extra_set = {cc for _, cc, _ in m.extras}
        zext = getattr(m, "zext", set())
        # moves: strictly ordered, every other op of the moved data after them
        for d, path in m.moves.items():
            ms = [self.v[("M", d, k)] for k in range(2 * len(path))]
            for x, y in zip(ms, ms[1:]):
                c.add(x < y)
            for k in m.keys:
                if k[0] != "M" and k[1] == d:
                    c.add(self.v[k] > ms[-1])
        # after U: X-reader only takes X parts, Z-reader only Z parts; no attachment from the Z-reader
        for t in range(3):
            u = self.v[(t, "U", "")]
            b0, b1 = G.BELL[t]
            for k in m.keys:
                if k[0] != t or k[1] == "U":
                    continue
                if k[1] == "A":
                    par = next(p for _, cc, p in m.extras if cc == k[2])
                    z = k[2] in zext   # X extra: no attach from az after U; Z extra: none onto ax
                    if par == b0:      # az == b0 iff orient 1; ax == b0 iff orient 0
                        c.add(self.v[k] < u).only_enforce_if(~self.o[t] if z else self.o[t])
                    elif par == b1:
                        c.add(self.v[k] < u).only_enforce_if(self.o[t] if z else ~self.o[t])
                    continue
                q = m.xmem[(t, k[1])] if k[2] == "X" else m.zmem[(t, k[1])]
                if q in extra_set:
                    continue
                # ax = b0 iff orient 0
                if q == b0:
                    if k[2] == "Z":
                        c.add(self.v[k] < u).only_enforce_if(~self.o[t])
                    else:
                        c.add(self.v[k] < u).only_enforce_if(self.o[t])
                elif q == b1:
                    if k[2] == "Z":
                        c.add(self.v[k] < u).only_enforce_if(self.o[t])
                    else:
                        c.add(self.v[k] < u).only_enforce_if(~self.o[t])
        for t, cc, parent in m.extras:
            la = self.v[(t, "A", cc)]
            mm_, typ_ = (m.zmem, "Z") if cc in zext else (m.xmem, "X")
            for (tt, d), mem in mm_.items():
                if mem == cc:
                    c.add(self.v[(tt, d, typ_)] > la)
            if parent in extra_set:
                tp = next(tt for tt, c2, _ in m.extras if c2 == parent)
                c.add(self.v[(tp, "A", parent)] < la)
            for d, path in m.moves.items():
                srcs = [G.DATA0[d]] + path[:-1]
                if cc in srcs:
                    c.add(la > self.v[("M", d, 2 * len(path) - 1)])
        # tile-pair parity (L1/cpsat.py)
        for ta in (range(3) if parity else []):
            for tb in range(3):
                terms = []
                for d in set(G.PLAQ[ta]) & set(G.PLAQ[tb]):
                    b = c.new_bool_var(f"par{ta}{tb}{d}")
                    c.add(self.v[(ta, d, "X")] < self.v[(tb, d, "Z")]).only_enforce_if(b)
                    c.add(self.v[(ta, d, "X")] >= self.v[(tb, d, "Z")]).only_enforce_if(~b)
                    terms.append(b)
                c.add(sum(terms) == 2 * c.new_int_var(0, len(terms) // 2, f"ev{ta}{tb}"))
        # surrogate objective: total data tail to the last CX layer, plus depth
        self.end = c.new_int_var(2, lmax, "end")
        c.add_max_equality(self.end, list(self.v.values()))
        tails = []
        for d in range(7):
            ks = [self.v[k] for k in m.keys if k[0] != "M" and k[1] == d]
            last = c.new_int_var(2, lmax, f"last{d}")
            c.add_max_equality(last, ks)
            tails.append(self.end - last)
        self.tail = sum(tails)

    def install_propagation(self, only=None):
        """Backward CSS Pauli propagation (as L1/validity.py, generalized to moves and extras):
        each final data stabilizer / logical and each check readout pulls back to its intended
        data operator times prepared-ancilla stabilizers. X parts exact, Z parts up to Z stabilizers."""
        m, c = self.m, self.c
        on = {}
        for k, v in self.v.items():
            for L in range(2, self.lmax + 1):
                b = c.new_bool_var(f"on{k}{L}")
                c.add(v == L).only_enforce_if(b)
                c.add(v != L).only_enforce_if(~b)
                on[k, L] = b

        def conj(bs, name):
            b = c.new_bool_var(name)
            c.add_bool_and(bs).only_enforce_if(b)
            c.add_bool_or([~x for x in bs]).only_enforce_if(~b)
            return b

        arcs = {L: [] for L in range(2, self.lmax + 1)}
        for L in arcs:
            for k in m.keys:
                if k[1] == "U":
                    b0, b1 = G.BELL[k[0]]
                    arcs[L].append((b0, b1, conj([on[k, L], ~self.o[k[0]]], f"u{k}{L}a")))
                    arcs[L].append((b1, b0, conj([on[k, L], self.o[k[0]]], f"u{k}{L}b")))
                else:
                    ctl, tg = m.qubits_of(k, [0, 0, 0])
                    arcs[L].append((ctl, tg, on[k, L]))
        allq = sorted({q for k in m.keys for q in m.qubits_of(k, [0, 0, 0])} | {q for p in G.BELL for q in p} | set(G.DATA0))
        data0 = set(G.DATA0)
        extra_set = {cc for _, cc, _ in m.extras}
        zext = getattr(m, "zext", set())
        zd = {q for d in getattr(m, "zhops", set()) for q in m.moves[d]}
        dests = {q for path in m.moves.values() for q in path} - zd
        permX = ({b0 for b0, _ in G.BELL} | zext | zd) - data0
        permZ = ({b1 for _, b1 in G.BELL} | (extra_set - zext) | dests) - data0
        specs = []
        for B in "XZ":
            for t, ds in enumerate(G.PLAQ):
                specs.append((B, f"s{t}", {m.pos[d] for d in ds}, {G.DATA0[d] for d in ds}, None))
            specs.append((B, "L", set(m.pos), set(data0), None))
            for t, ds in enumerate(G.PLAQ):
                specs.append((B, f"c{t}", None, {G.DATA0[d] for d in ds}, t))
        zrows = None
        dlist = sorted(data0)
        for B, name, start, target, ct in [s_ for s_ in specs if only is None or s_[0] + s_[1] in only]:
            lab = B + name
            vec = {q: c.new_bool_var(f"{lab}_e{q}") for q in allq}
            if ct is None:
                for q, b in vec.items():
                    c.add(b == int(q in start))
            else:
                b0, b1 = G.BELL[ct]
                ex = {cc for t, cc, _ in m.extras if t == ct and (cc in zext) == (B == "Z")}
                for q, b in vec.items():
                    if q == b0:   # ax = b0 iff orient 0; az = b0 iff orient 1
                        c.add(b == (1 - self.o[ct]) if B == "X" else b == self.o[ct])
                    elif q == b1:
                        c.add(b == self.o[ct] if B == "X" else b == (1 - self.o[ct]))
                    else:
                        c.add(b == int(q in ex))
            for L in range(self.lmax, 1, -1):
                tog = {q: [] for q in allq}
                for ctl, tg, b in arcs[L]:
                    src, dst = (ctl, tg) if B == "X" else (tg, ctl)
                    tog[dst].append(conj([b, vec[src]], f"{lab}{L}{ctl}{tg}"))
                prev = {}
                for q in allq:
                    if not tog[q]:
                        prev[q] = vec[q]
                        continue
                    t_ = c.new_bool_var(f"{lab}{L}t{q}")
                    c.add(t_ == sum(tog[q]))
                    prev[q] = c.new_bool_var(f"{lab}{L}p{q}")
                    c.add_bool_xor([vec[q], t_, ~prev[q]])
                vec = prev
            for b0, b1 in G.BELL:   # Bell CX(b0, b1) at layer 1
                src, dst = (b0, b1) if B == "X" else (b1, b0)
                nv = c.new_bool_var(f"{lab}bell{dst}")
                c.add_bool_xor([vec[src], vec[dst], ~nv])
                vec[dst] = nv
            perm = permX if B == "X" else permZ
            for q, b in vec.items():
                if q in data0:
                    if B == "X":
                        c.add(b == int(q in target))
                elif q not in perm:
                    c.add(b == 0)
            if B == "Z":
                rows = []
                for mask in range(8):
                    sup = set(target)
                    for t, ds in enumerate(G.PLAQ):
                        if mask >> t & 1:
                            sup ^= {G.DATA0[d] for d in ds}
                    rows.append([int(q in sup) for q in dlist])
                c.add_allowed_assignments([vec[q] for q in dlist], rows)

    def solutions(self, n, seconds, seed, wt_end=2, rand_obj=0.0):
        rng = random.Random(seed)
        obj = self.tail + wt_end * self.end
        if rand_obj:
            obj = obj * 10 + sum(rng.randint(0, int(rand_obj)) * v for v in self.v.values())
        self.c.minimize(obj)
        out = []

        class CB(cp_model.CpSolverSolutionCallback):
            def __init__(s):
                super().__init__()

            def on_solution_callback(s):
                a = {k: s.value(v) for k, v in self.v.items()}
                o = [int(s.value(b)) for b in self.o]
                out.append((a, o))
                if len(out) >= n:
                    s.stop_search()

        s = cp_model.CpSolver()
        s.parameters.num_search_workers = 1
        s.parameters.max_time_in_seconds = seconds
        s.parameters.random_seed = seed
        s.solve(self.c, CB())
        return out


def starts(m, lmax, nwant, seed, tries=6, per=40, seconds=20):
    """Feasible schedules that pass Stim; returns sorted [(cost, a, o)]."""
    found = {}
    for i in range(tries):
        g = Gen(m, lmax)
        g.install_propagation()
        sols = g.solutions(per, seconds, seed * 100 + i, rand_obj=(0 if i == 0 else 3))
        for a, o in sols:
            key = (tuple(sorted(a.items(), key=str)), tuple(o))
            if key in found:
                continue
            found[key] = m.cost(a, o)
        ok = [(cst, k) for k, cst in found.items() if cst is not None]
        if len(ok) >= nwant:
            break
    ok = sorted([(cst, dict(k[0]), list(k[1])) for k, cst in found.items() if cst is not None], key=lambda r: r[0])
    return ok, len(found)

def repair(m, base_a, base_o, lmax, seconds=20, seed=0, keep=8):
    """Feasible schedules for layout m closest (Hamming over shared keys + orientation) to a base
    schedule; Stim-validated, sorted by proxy."""
    g = Gen(m, lmax)
    g.install_propagation()
    diffs = []
    for k, v in g.v.items():
        if k in base_a and 2 <= base_a[k] <= lmax:
            b = g.c.new_bool_var(f"df{k}")
            g.c.add(v == base_a[k]).only_enforce_if(~b)
            diffs.append(b)
            g.c.add_hint(v, base_a[k])
    for t in range(3):
        diffs.append(g.o[t] if base_o[t] == 0 else ~g.o[t])
    g.c.minimize(sum(diffs) * 4 + g.tail)
    out = []

    class CB(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(s):
            out.append(({k: s.value(v) for k, v in g.v.items()}, [int(s.value(b)) for b in g.o]))

    s = cp_model.CpSolver()
    s.parameters.num_search_workers = 1
    s.parameters.max_time_in_seconds = seconds
    s.parameters.random_seed = seed
    s.solve(g.c, CB())
    res = []
    for a, o in out[-keep:]:
        cst = m.cost(a, o)
        if cst is not None:
            res.append((cst, a, o))
    return sorted(res, key=lambda r: r[0]), len(out)


def bases(limit=8):
    """Distinct incumbent schedules from me_layout and this lane (gmodel format), best first."""
    import glob
    import json
    from l2alap import load_assign
    seen, out = set(), []
    files = glob.glob("/home/jihoon/competitions/quantumn/work/lanes/me_layout/res_*.json")
    files += glob.glob("/home/jihoon/competitions/quantumn/work/lanes/L2_layout_cpsat/res_*.json")
    rows = []
    for f in files:
        for r in json.load(open(f)):
            if r[0] is not None:
                rows.append((r[0], r[1], r[2], r[4], f))
    rows.sort(key=lambda r: r[0])
    for cst, a, o, name, f in rows:
        key = round(cst, 11)
        if key in seen:
            continue
        seen.add(key)
        out.append((cst, load_assign(a), list(o), name, f))
    return out
