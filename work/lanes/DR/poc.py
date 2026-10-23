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


def proxy(sched=SCHED, verify=True):
    b, cat_bits, ver_tags = build(sched, verify)
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
            init = [(0 if typ == "X" else 3) + i for i in gens_of(S)]
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
