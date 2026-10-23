"""Grid-free prototype of a direct-readout final round with verified 4-member cats.

Data d0..d6 on qubits 0..6 start in an ideal code state (MPP), as in gmodel.proxy. Each check is a
4-member cat: X-checks use GHZ_Z (members control CX onto data, read MX), Z-checks use GHZ_X (data
control CX onto members, read M). Each cat is verified with one parity ancilla before use, and each
member is read out right after its coupling. The exact second-order T-state loss comes from
proxy2.joint_loss on the judge's noise; `first` must be 0 (no single fault fails).

    python poc.py
"""
import sys

import stim

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import proxy2  # noqa: E402
from qcirc import Circ, allow_any_coupling  # noqa: E402
from tprep.noise import STANDARD, apply_noise  # noqa: E402
from tprep.qasm import to_stim  # noqa: E402

allow_any_coupling()
GENS = [frozenset(s) for s in ({0, 2, 4, 6}, {1, 2, 5, 6}, {3, 4, 5, 6})]


def gens_of(S):
    """Indices of the standard generators whose product is S."""
    for k in range(1, 8):
        idx = [i for i in range(3) if k >> i & 1]
        acc = frozenset()
        for i in idx:
            acc = acc ^ GENS[i]
        if acc == S:
            return idx
    raise ValueError(S)


# Relaxed-floor schedule (relaxed.py, common start): (data, step, type, support)
SCHED = {
    0: [(0, "Z", {0, 1, 3, 6}), (1, "Z", {0, 1, 4, 5}), (2, "Z", {0, 2, 3, 5}), (3, "X", {0, 2, 4, 6})],
    1: [(1, "Z", {0, 1, 4, 5}), (2, "Z", {0, 1, 3, 6}), (3, "X", {1, 2, 5, 6})],
    2: [(1, "X", {0, 2, 4, 6}), (2, "Z", {0, 2, 3, 5}), (3, "X", {1, 2, 5, 6})],
    3: [(1, "Z", {0, 1, 3, 6}), (2, "Z", {0, 2, 3, 5}), (3, "X", {3, 4, 5, 6})],
    4: [(1, "X", {3, 4, 5, 6}), (2, "X", {0, 2, 4, 6}), (3, "Z", {0, 1, 4, 5})],
    5: [(0, "Z", {0, 2, 3, 5}), (1, "X", {1, 2, 5, 6}), (2, "Z", {0, 1, 4, 5}), (3, "X", {3, 4, 5, 6})],
    6: [(0, "X", {1, 2, 5, 6}), (1, "X", {3, 4, 5, 6}), (2, "X", {0, 2, 4, 6}), (3, "Z", {0, 1, 3, 6})],
}


class Builder:
    def __init__(self):
        self.ops = []          # (step, order, kind, qubits, tag)
        self.next_q = 7
        self.k = 0

    def op(self, t, kind, qs, tag=None):
        self.ops.append((t, self.k, kind, tuple(qs), tag))
        self.k += 1

    def fresh(self):
        q = self.next_q
        self.next_q += 1
        return q


def build(sched=SCHED, verify=True, base=8):
    b = Builder()
    checks = {}
    for d, lst in sched.items():
        for t, typ, S in lst:
            checks.setdefault((typ, frozenset(S)), []).append((t, d))
    for d in range(7):
        b.op(base - 1, "id", [d])
    cat_bits = {}      # check -> list of tags of member measurements
    ver_tags = []
    for (typ, S), cpl in checks.items():
        cpl.sort()
        e = base + cpl[0][0]
        m = [b.fresh() for _ in range(4)]
        v = b.fresh() if verify else None
        # GHZ_Z tree for X-checks; its H-conjugate (reversed CX, swapped bases) for Z-checks
        root_init, leaf_init = ("RX", "R") if typ == "X" else ("R", "RX")
        rev = typ == "Z"
        t0 = e - (6 if verify else 3)
        b.op(t0, root_init, [m[0]])
        for q in m[1:]:
            b.op(t0, leaf_init, [q])
        for t, (c, x) in ((t0 + 1, (m[0], m[1])), (t0 + 2, (m[0], m[2])), (t0 + 2, (m[1], m[3]))):
            b.op(t, "cx", (x, c) if rev else (c, x))
        if verify:
            b.op(t0 + 2, "R" if typ == "X" else "RX", [v])
            for t, q in ((t0 + 3, m[0]), (t0 + 4, m[1])):
                b.op(t, "cx", (v, q) if rev else (q, v))
            tag = ("ver", typ, S)
            b.op(t0 + 5, "M" if typ == "X" else "MX", [v], tag)
            ver_tags.append(tag)
        tags = []
        for (t, d), q in zip(cpl, m):
            b.op(base + t, "cx", (q, d) if typ == "X" else (d, q))
            tag = ("cat", typ, S, q)
            b.op(base + t + 1, "MX" if typ == "X" else "M", [q], tag)
            tags.append(tag)
        cat_bits[(typ, S)] = tags
    return b, cat_bits, ver_tags


def emit(b):
    c = Circ(b.next_q)
    bit = {}
    used = sorted({q for _, _, kind, qs, _ in b.ops for q in qs})
    by_t = {}
    for t, k, kind, qs, tag in b.ops:
        by_t.setdefault(t, []).append((k, kind, qs, tag))
    T = sorted(by_t)
    # lazy init: resets are written in their own step already
    for i, t in enumerate(T):
        for k, kind, qs, tag in sorted(by_t[t]):
            if kind == "cx":
                c.cx(*qs)
            elif kind == "R":
                c.reset(qs[0])
            elif kind == "RX":
                c.rx(qs[0])
            elif kind == "M":
                bit[tag] = c.measure(qs[0])
            elif kind == "MX":
                bit[tag] = c.mx(qs[0])
            else:
                c.g(kind, *qs)
        if i + 1 < len(T):
            if T[i + 1] != t + 1:
                raise ValueError("gap in schedule")
            c.barrier(*used)
    return c, bit


def proxy(sched=SCHED, verify=True, builder=None):
    b, cat_bits, ver_tags = builder(sched) if builder else build(sched, verify)
    c, bit = emit(b)
    s, err = to_stim(c.text(), n_qubits=c.n)
    assert not err, err
    noisy = apply_noise(s, 1e-3, STANDARD)
    meas_order = [tag for kind, qs, tg in c.sops if kind in ("M", "MX") for tag in [tg]]
    nm = c.nbits
    stab = [("X", g) for g in GENS] + [("Z", g) for g in GENS]

    def full(logical):
        data = list(range(7))
        lines = [proxy2._mpp(B, sorted(g)) for B, g in stab] + [proxy2._mpp(logical, data)]
        lines += [l for l in noisy.splitlines() if not l.startswith(("DETECTOR", "OBSERVABLE"))]
        lines += [proxy2._mpp(B, sorted(g)) for B, g in stab] + [proxy2._mpp(logical, data)]
        n = 7 + nm + 7
        rec = lambda i: f"rec[{i - n}]"
        for (typ, S), tags in cat_bits.items():
            # typ "C": an ancilla-only parity (no data stabilizer term)
            init = [(0 if typ == "X" else 3) + i for i in gens_of(S)] if typ in ("X", "Z") else []
            lines.append("DETECTOR " + " ".join(rec(7 + bit[t]) for t in tags) + " " + " ".join(rec(k) for k in init))
        for t in ver_tags:
            lines.append(f"DETECTOR {rec(7 + bit[t])}")
        for k in range(6):
            lines.append(f"OBSERVABLE_INCLUDE({k}) {rec(7 + nm + k)} {rec(k)}")
        lines.append(f"OBSERVABLE_INCLUDE(6) {rec(7 + nm + 6)} {rec(6)}")
        return stim.Circuit("\n".join(lines))

    cx, cz = full("X"), full("Z")
    for circ in (cx, cz):   # noiseless determinism of every detector and observable
        circ.without_noise().detector_error_model()
    return proxy2.joint_loss(cx, cz), c


if __name__ == "__main__":
    for ver in (False, True):
        r, c = proxy(verify=ver)
        print(f"verify={ver}: {r}  qubits {c.n}  cx {c.n_2q()}")


def build_clean(sched, base=14, clean_z=False):
    """X-check cats: chain GHZ_Z, every member verified (Z-parity with a chain neighbour) in the step
    right before its coupling; verifier pairs cover every chain cut. Z-check cats: plain tree GHZ_X
    (optionally verified as in build). Ops are placed as late as possible."""
    b = Builder()
    busy = {}

    def free(q, t):
        return t not in busy.setdefault(q, set())

    def place(t_max, kind, qs, tag=None):
        t = t_max
        while not all(free(q, t) for q in qs):
            t -= 1
        for q in qs:
            busy[q].add(t)
        b.op(t, kind, qs, tag)
        return t

    def put(t, kind, qs, tag=None):
        for q in qs:
            assert free(q, t), (t, kind, qs)
            busy.setdefault(q, set()).add(t)
        b.op(t, kind, qs, tag)

    checks = {}
    for d, lst in sched.items():
        for t, typ, S in lst:
            checks.setdefault((typ, frozenset(S)), []).append((base + t, d))
    for d in range(7):
        put(base - 1, "id", [d])
    for (typ, S), cpl in checks.items():
        for t, d in cpl:
            busy.setdefault(d, set()).add(t)
    cat_bits, ver_tags = {}, []
    order = sorted(checks.items(), key=lambda kv: -min(t for t, _ in kv[1]))
    for (typ, S), cpl in order:
        cpl.sort()
        m = [b.fresh() for _ in range(4)]
        tags = []
        for (t, d), q in zip(cpl, m):
            b.op(t, "cx", (q, d) if typ == "X" else (d, q))
            busy.setdefault(q, set()).add(t)
            tag = ("cat", typ, S, q)
            put(t + 1, "MX" if typ == "X" else "M", [q], tag)
            tags.append(tag)
        cat_bits[(typ, S)] = tags
        if typ == "X" or clean_z:
            rv = typ == "Z"            # Z-checks: H-conjugate (reversed CX, swapped bases)
            cxo = (lambda c, t: (t, c)) if rv else (lambda c, t: (c, t))
            w = [b.fresh() for _ in range(4)]
            partner = {0: 1, 1: 2, 2: 3, 3: 2}
            vt = {}
            for i in range(4):          # own verification right before coupling
                t = cpl[i][0] - 1
                put(t, "cx", cxo(m[i], w[i]))
                vt[i] = [t]
            for i in range(4):          # partner's CX on w[i], before the partner's own check
                j = partner[i]
                t = place(min(vt[j]) - 1, "cx", cxo(m[j], w[i]))
                vt[i].append(t)
                vt[j].append(t)
            for i in range(4):
                tag = ("ver", typ, S, i)
                put(max(vt[i]) + 1, "MX" if rv else "M", [w[i]], tag)
                ver_tags.append(tag)
                put(min(vt[i]) - 1, "RX" if rv else "R", [w[i]])
            t_end = min(min(v) for v in vt.values()) - 1
            t3 = place(t_end, "cx", cxo(m[2], m[3]))
            t2 = place(t3 - 1, "cx", cxo(m[1], m[2]))
            t1 = place(t2 - 1, "cx", cxo(m[0], m[1]))
            put(t1 - 1, "R" if rv else "RX", [m[0]])
            for k, tk in ((1, t1), (2, t2), (3, t3)):
                put(tk - 1, "RX" if rv else "R", [m[k]])
        else:
            e = cpl[0][0]
            t2 = place(e - 1, "cx", (m[2], m[0]))
            t2b = place(e - 1, "cx", (m[3], m[1]))
            t1 = place(min(t2, t2b) - 1, "cx", (m[1], m[0]))
            put(t1 - 1, "R", [m[0]])
            put(t1 - 1, "RX", [m[1]])
            put(t2 - 1, "RX", [m[2]])
            put(t2b - 1, "RX", [m[3]])
    lo = min(t for t, *_ in b.ops)
    b.ops = [(t - lo, k, kind, qs, tag) for t, k, kind, qs, tag in b.ops]
    return b, cat_bits, ver_tags


def build_hybrid(sched, base=14, z_mode="pair"):
    """X-checks: chain GHZ_Z cats, 3 verifiers (pairs 01, 12, 23), each member's last pre-coupling op is
    a verification CX. Z-checks: one Bell pair (Phi+), each member couples two data in time order
    (members take couplings 1,3 and 2,4), read M; no verification (their Z hooks meet later X-checks)."""
    b = Builder()
    busy = {}

    def free(q, t):
        return t not in busy.setdefault(q, set())

    def place(t_max, kind, qs, tag=None):
        t = t_max
        while not all(free(q, t) for q in qs):
            t -= 1
        for q in qs:
            busy[q].add(t)
        b.op(t, kind, qs, tag)
        return t

    def put(t, kind, qs, tag=None):
        for q in qs:
            assert free(q, t), (t, kind, qs)
            busy.setdefault(q, set()).add(t)
        b.op(t, kind, qs, tag)

    checks = {}
    for d, lst in sched.items():
        for t, typ, S in lst:
            checks.setdefault((typ, frozenset(S)), []).append((base + t, d))
    for d in range(7):
        put(base - 1, "id", [d])
    for (typ, S), cpl in checks.items():
        for t, d in cpl:
            busy.setdefault(d, set()).add(t)
    cat_bits, ver_tags = {}, []
    for (typ, S), cpl in sorted(checks.items(), key=lambda kv: -min(t for t, _ in kv[1])):
        cpl.sort()
        if typ == "X":
            import copy
            import itertools as it
            base_q = b.next_q
            for perm in it.permutations(range(4)):
                snap = (copy.deepcopy(busy), list(b.ops), b.k, b.next_q, list(ver_tags))
                try:
                    cp_ = [cpl[i] for i in perm]          # chain order of the couplings
                    b.next_q = base_q
                    m = [b.fresh() for _ in range(4)]
                    tags = []
                    for (t, d), q in zip(cp_, m):
                        b.op(t, "cx", (q, d))
                        busy.setdefault(q, set()).add(t)
                        tag = ("cat", typ, S, q)
                        put(t + 1, "MX", [q], tag)
                        tags.append(tag)
                    w = [b.fresh() for _ in range(3)]       # w[k] checks Z_{m_k} Z_{m_k+1}
                    last = {0: 0, 1: 1, 2: 2, 3: 2}
                    if cp_[2][0] == cp_[3][0]:
                        last = {0: 0, 1: 0, 2: 1, 3: 2}
                    vt = {k: [] for k in range(3)}
                    mt = {i: [] for i in range(4)}
                    for i in range(4):
                        t = cp_[i][0] - 1
                        put(t, "cx", (m[i], w[last[i]]))
                        vt[last[i]].append(t)
                        mt[i].append(t)
                    for k in range(3):
                        for i in (k, k + 1):
                            if last[i] != k:
                                t = place(min(mt[i]) - 1, "cx", (m[i], w[k]))
                                vt[k].append(t)
                                mt[i].append(t)
                    for k in range(3):
                        tag = ("ver", typ, S, k)
                        put(max(vt[k]) + 1, "M", [w[k]], tag)
                        ver_tags.append(tag)
                        put(min(vt[k]) - 1, "R", [w[k]])
                    t_end = min(min(v) for v in mt.values()) - 1
                    t3 = place(t_end, "cx", (m[2], m[3]))
                    t2 = place(t3 - 1, "cx", (m[1], m[2]))
                    t1 = place(t2 - 1, "cx", (m[0], m[1]))
                    put(t1 - 1, "RX", [m[0]])
                    for k, tk in ((1, t1), (2, t2), (3, t3)):
                        put(tk - 1, "R", [m[k]])
                    cat_bits[(typ, S)] = tags
                    break
                except AssertionError:
                    busy.clear(); busy.update(snap[0])
                    b.ops[:] = snap[1]; b.k = snap[2]; b.next_q = snap[3]
                    ver_tags[:] = snap[4]
            else:
                raise RuntimeError("no conflict-free chain for " + str((typ, sorted(S))))
        elif z_mode == "pair":
            a, c2 = b.fresh(), b.fresh()
            grp = {a: [cpl[0], cpl[2]], c2: [cpl[1], cpl[3]]}
            tags = []
            for q, lst in grp.items():
                for t, d in lst:
                    b.op(t, "cx", (d, q))
                    busy.setdefault(q, set()).add(t)
                tag = ("cat", typ, S, q)
                put(lst[-1][0] + 1, "M", [q], tag)
                tags.append(tag)
            cat_bits[(typ, S)] = tags
            e = min(t for t, _ in cpl)
            t1 = place(e - 1, "cx", (c2, a))
            put(t1 - 1, "R", [a])
            put(t1 - 1, "RX", [c2])
        else:   # "cat1": GHZ_X tree, one member per data, one verifier X_m0 X_m1 against prep correlations
            m = [b.fresh() for _ in range(4)]
            v = b.fresh()
            tags = []
            for (t, d), q in zip(cpl, m):
                b.op(t, "cx", (d, q))
                busy.setdefault(q, set()).add(t)
                tag = ("cat", typ, S, q)
                put(t + 1, "M", [q], tag)
                tags.append(tag)
            cat_bits[(typ, S)] = tags
            e = min(t for t, _ in cpl)
            tv1 = place(min(t for t, _ in cpl[:2]) - 1, "cx", (v, m[1]))
            tv0 = place(min(tv1, cpl[0][0]) - 1, "cx", (v, m[0]))
            tag = ("ver", typ, S)
            put(max(tv0, tv1) + 1 if free(v, max(tv0, tv1) + 1) else place(cpl[-1][0] + 2, "MX", [v], tag) or None, "MX", [v], tag) if free(v, max(tv0, tv1) + 1) else None
            ver_tags.append(tag)
            t_pre = min(tv0, tv1, e) - 1
            t2 = place(t_pre, "cx", (m[2], m[0]))
            t2b = place(t_pre, "cx", (m[3], m[1]))
            t1 = place(min(t2, t2b) - 1, "cx", (m[1], m[0]))
            put(min(tv0, tv1) - 1, "RX", [v]) if free(v, min(tv0, tv1) - 1) else None
            put(t1 - 1, "R", [m[0]])
            put(t1 - 1, "RX", [m[1]])
            put(t2 - 1, "RX", [m[2]])
            put(t2b - 1, "RX", [m[3]])
    lo = min(t for t, *_ in b.ops)
    b.ops = [(t - lo, k, kind, qs, tag) for t, k, kind, qs, tag in b.ops]
    return b, cat_bits, ver_tags


def concurrency(b):
    span = {}
    for t, k, kind, qs, tag in b.ops:
        for q in qs:
            lo, hi = span.get(q, (t, t))
            span[q] = (min(lo, t), max(hi, t))
    T = max(hi for lo, hi in span.values()) + 1
    return max(sum(1 for q, (lo, hi) in span.items() if q >= 7 and lo <= t <= hi) for t in range(T))
