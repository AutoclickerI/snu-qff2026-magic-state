"""Generalized final round: data qubits may first move (2-CNOT hops onto fresh |0> qubits), then a
superdense round with one Bell pair per plaquette (both members take Z-part CNOTs) plus X-only
extra cat members. Evaluated exactly to second order (Stim DEM, judge noise via tprep's own QASM
conversion, so grid adjacency is enforced) and annealed like gen2_cycle.
"""
import random
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")

import stim  # noqa: E402

import cultiv_port as cp  # noqa: E402
import proxy2  # noqa: E402
from qcirc import Circ  # noqa: E402
from tprep.noise import STANDARD, apply_noise  # noqa: E402
from tprep.qasm import to_stim  # noqa: E402

P = cp.phys
DATA0 = [cp.DATA_XY[i] for i in range(7)]                     # positions after the T-check
PLAQ = [[DATA0.index(xy) for xy in ds] for _, ds in proxy2.TILES]   # data indices per plaquette
BELL = [(m, (m[0] + 1, m[1])) for m, _ in proxy2.TILES]


def adj(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


class GModel:
    def __init__(self, moves=(), extras=(), xmem=None):
        """moves: {d: [xy1, xy2, ...]} hop path; extras: [(t, c, parent)]; xmem: {(t, d): member}
        for X-part CNOTs that go to an extra (default: the Bell member next to the data)."""
        self.moves = dict(moves)
        self.pos = list(DATA0)
        for d, path in self.moves.items():
            self.pos[d] = path[-1]
        self.extras = list(extras)
        self.xmem = dict(xmem or {})
        self.zmem = {}
        for t, ds in enumerate(PLAQ):
            for d in ds:
                ms = [m for m in BELL[t] if adj(m, self.pos[d])]
                assert ms, f"data {d} not next to a Bell member of tile {t}"
                self.zmem[(t, d)] = ms[0]
                self.xmem.setdefault((t, d), ms[0])
        for (t, d), m in self.xmem.items():
            assert adj(m, self.pos[d]), (t, d, m)
        self.keys = [(t, d, typ) for t, ds in enumerate(PLAQ) for d in ds for typ in "XZ"]
        self.keys += [(t, "U", "") for t in range(3)] + [(t, "A", c) for t, c, _ in self.extras]
        self.keys += [("M", d, k) for d, path in self.moves.items() for k in range(2 * len(path))]

    def qubits_of(self, key, orient):
        a, b, c = key
        if a == "M":                     # hop k//2 of data b; even k: CX src->dst, odd: dst->src
            path = [DATA0[b]] + self.moves[b]
            src, dst = path[c // 2], path[c // 2 + 1]
            return (src, dst) if c % 2 == 0 else (dst, src)
        if b == "U":
            return self.readers(a, orient)       # CX from the X-read member to the Z-read one
        if b == "A":
            parent = next(p for t, cc, p in self.extras if cc == c)
            return (parent, c)
        m = self.xmem[(a, b)] if c == "X" else self.zmem[(a, b)]
        return (m, self.pos[b]) if c == "X" else (self.pos[b], m)

    def readers(self, t, orient):
        a, b = BELL[t]
        return (a, b) if orient[t] == 0 else (b, a)

    def feasible(self, assign, orient):
        used = set()
        for k, L in assign.items():
            for q in self.qubits_of(k, orient):
                if (L, q) in used:
                    return False
                used.add((L, q))
        for d, path in self.moves.items():
            ms = [assign[("M", d, k)] for k in range(2 * len(path))]
            if ms != sorted(ms) or len(set(ms)) != len(ms):
                return False
            for k, L in assign.items():
                if k[0] != "M" and k[1] == d and L <= ms[-1]:
                    return False
        extra_set = {c for _, c, _ in self.extras}
        for t in range(3):
            u = assign[(t, "U", "")]
            ax, az = self.readers(t, orient)
            for k, L in assign.items():
                if k[0] != t or L < u:
                    continue
                if k[1] == "A":
                    if self.qubits_of(k, orient)[0] == az:
                        return False
                    continue
                if k[1] == "U":
                    continue
                q = self.xmem[(t, k[1])] if k[2] == "X" else self.zmem[(t, k[1])]
                if q in extra_set:
                    continue
                if (q == ax and k[2] != "X") or (q == az and k[2] != "Z"):
                    return False
        for t, c, parent in self.extras:
            la = assign[(t, "A", c)]
            for (tt, d), m in self.xmem.items():
                if m == c and assign[(tt, d, "X")] <= la:
                    return False
            if parent in extra_set:
                tp = next(tt for tt, cc, _ in self.extras if cc == parent)
                if assign[(tp, "A", parent)] >= la:
                    return False
            # an extra sitting on a vacated data site may only join after the move left it in |0>
            for d, path in self.moves.items():
                srcs = [DATA0[d]] + path[:-1]
                if c in srcs and la <= max(assign[("M", d, k)] for k in range(2 * len(path))):
                    return False
        return True

    def emit(self, c, assign, orient):
        lmax = max(assign.values())
        bell = [q for pair in BELL for q in pair]
        ex = [cc for _, cc, _ in self.extras]
        dests = [q for path in self.moves.values() for q in path]
        involved = sorted({P(q) for q in bell + ex + dests + DATA0 + self.pos})
        c.barrier(*involved)
        c.rx(*[P(a) for a, _ in BELL]); c.reset(*[P(b) for _, b in BELL])
        fresh = [P(q) for q in ex + dests if q not in DATA0]
        if fresh:
            c.reset(*fresh)
        c.barrier(*involved)
        bl = getattr(self, "bell_layer", {})
        for t, (a, b) in enumerate(BELL):
            if bl.get(t, 1) == 1:
                c.cx(P(a), P(b))
        lastq = {}
        for k, L in assign.items():
            for q in self.qubits_of(k, orient):
                lastq[q] = max(lastq.get(q, 0), L)
        readers = {}
        for t in range(3):
            ax, az = self.readers(t, orient)
            readers[ax], readers[az] = (t, "X"), (t, "Z")
        for t, cc, _ in self.extras:
            readers[cc] = (t, "X")
        self.checks = {}
        for L in range(2, lmax + 2):  # bell layers >= 2 handled inside
            c.barrier(*involved)
            for q, (t, B) in readers.items():
                if lastq.get(q, 1) == L - 1:
                    bit = c.mx(P(q)) if B == "X" else c.measure(P(q))
                    self.checks.setdefault((t, B), []).append(bit)
            for t, (a, b) in enumerate(BELL):
                if bl.get(t, 1) == L:
                    c.cx(P(a), P(b))
            for k, LL in sorted(assign.items(), key=lambda kv: str(kv[0])):
                if LL == L:
                    a, b = self.qubits_of(k, orient)
                    c.cx(P(a), P(b))
        for _, bits in sorted(self.checks.items()):
            c.detector(*bits)

    def proxy(self, assign, orient):
        c = Circ()
        c.g("id", *[P(q) for q in DATA0])
        self.emit(c, assign, orient)
        bit_check = {b: (t if B == "X" else 3 + t) for (t, B), bits in self.checks.items() for b in bits}
        c.detectors = []
        c = c.rescheduled(lazy_init=True)
        s, err = to_stim(c.text())
        if err:
            raise ValueError("; ".join(err))
        noisy = apply_noise(s, 1e-3, STANDARD)
        bits = [b for kind, qs, b in c.sops if kind in ("M", "MX")]
        cx, cz = (self._full(noisy, bits, bit_check, L) for L in "XZ")
        return proxy2.joint_loss(cx, cz)

    def _full(self, noisy, bits, bit_check, logical):
        sup0 = [sorted(P(DATA0[d]) for d in ds) for ds in PLAQ]
        sup1 = [sorted(P(self.pos[d]) for d in ds) for ds in PLAQ]
        d0 = sorted(P(q) for q in DATA0)
        d1 = sorted(P(q) for q in self.pos)
        lines = [proxy2._mpp(B, s) for B in "XZ" for s in sup0] + [proxy2._mpp(logical, d0)]
        lines += [l for l in noisy.splitlines() if not l.startswith(("DETECTOR", "OBSERVABLE"))]
        lines += [proxy2._mpp(B, s) for B in "XZ" for s in sup1] + [proxy2._mpp(logical, d1)]
        nm = len(bits)
        n = 7 + nm + 7
        rec = lambda i: f"rec[{i - n}]"
        pos = {b: j for j, b in enumerate(bits)}
        per = {}
        for b, k in bit_check.items():
            per.setdefault(k, []).append(pos[b])
        for k, js in sorted(per.items()):
            lines.append("DETECTOR " + " ".join(rec(7 + j) for j in js) + f" {rec(k)}")
        for k in range(6):
            lines.append(f"OBSERVABLE_INCLUDE({k}) {rec(7 + nm + k)} {rec(k)}")
        lines.append(f"OBSERVABLE_INCLUDE(6) {rec(7 + nm + 6)} {rec(6)}")
        return stim.Circuit("\n".join(lines))

    def cost(self, assign, orient):
        if not self.feasible(assign, orient):
            return None
        try:
            return self.proxy(assign, orient)
        except (ValueError, AssertionError):
            return None

    def full_circuit(self, assign, orient, lazy=True):
        c = Circ()
        cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_init_unitary", cp.UP + "_injection_stage.py"), s_to="Tswap")
        cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_double_cat_check", cp.UP + "_cultivation_stage.py"), s_to="Tswap")
        self.emit(c, assign, orient)
        c = c.rescheduled(lazy_init=True) if lazy else c
        return c, [P(q) for q in self.pos]


def random_start(model, lmax, rng, tries=200000):
    for _ in range(tries):
        a, used = {}, set()
        ok = True
        keys = list(model.keys)
        # moves first, in order, at the earliest layers
        mk = sorted([k for k in keys if k[0] == "M"], key=lambda k: (k[1], k[2]))
        L0 = {}
        for k in mk:
            L = max(2, L0.get(k[1], 1) + 1)
            a[k] = L
            L0[k[1]] = L
        rest = [k for k in keys if k[0] != "M"]
        rng.shuffle(rest)
        for k in rest:
            a[k] = rng.randint(2, lmax)
        o = [rng.randint(0, 1) for _ in range(3)]
        if model.cost(a, o) is not None:
            return a, o
    raise RuntimeError("no feasible start")


def anneal(model, a0, o0, seed, steps, lmax, T0=4e-6, T1=2e-7):
    rng = random.Random(seed)
    assign, orient = dict(a0), list(o0)
    cur = model.cost(assign, orient)
    best = (cur, dict(assign), list(orient))
    for s in range(steps):
        T = T0 * (T1 / T0) ** (s / steps)
        a2, o2 = dict(assign), list(orient)
        r = rng.random()
        if r < 0.08:
            o2[rng.randrange(3)] ^= 1
        elif r < 0.4:
            a2[rng.choice(model.keys)] = rng.randint(2, lmax)
        elif r < 0.6:
            k1, k2 = rng.sample(model.keys, 2)
            a2[k1], a2[k2] = a2[k2], a2[k1]
        else:
            k = rng.choice(model.keys)
            old, L = a2[k], rng.randint(2, lmax)
            qs = set(model.qubits_of(k, o2))
            for k2, L2 in list(a2.items()):
                if k2 != k and L2 == L and qs & set(model.qubits_of(k2, o2)):
                    a2[k2] = old
            a2[k] = L
        c2 = model.cost(a2, o2)
        if c2 is None:
            continue
        if c2 < cur or rng.random() < pow(2.718281828, -(c2 - cur) / T):
            assign, orient, cur = a2, o2, c2
            if cur < best[0]:
                best = (cur, dict(assign), list(orient))
    return best
