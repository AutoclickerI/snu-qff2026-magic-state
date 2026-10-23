"""Grid-free exact proxy: current Steane-type round vs teleport-output round.

current: CX d->a (A=|+_L>, read Z) at T, CX b->d at T+1, MX B at T+2; C checks B (CX b->c at T, Z at T+1).
teleport: O=|+_L> CX o->d at T; at T+1 measure D in Z and CX b->o; MX B at T+2; output = O.
    python tp.py
"""
import json
import sys

import stim

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import steane  # noqa: E402,F401  (patches joint_loss to record first order)
import poc  # noqa: E402
import proxy2  # noqa: E402
from steane import ENC, PIV  # noqa: E402
from tprep.noise import STANDARD, apply_noise  # noqa: E402
from tprep.qasm import to_stim  # noqa: E402

GENS = poc.GENS


def json_enc(path, cells):
    """(layers of (p,q) in code indices, pivot code indices) of an L5-style json prep."""
    d = json.load(open(path))
    ix = {c: i for i, c in enumerate(cells)}
    return [[(ix[u], ix[v]) for u, v in l] for l in d["ops"]], {ix[p] for p in d["pivots"]}


def lazy_enc(b, Q, layers, pivots, end):
    """|+_L>-type encoder in the json convention (pivot RX, others R, cx u->v); last layer at step end."""
    L = len(layers)
    first = {}
    for k, l in enumerate(layers):
        for u, v in l:
            first.setdefault(u, k)
            first.setdefault(v, k)
    for i in range(7):
        k = first.get(i, 0)
        b.op(end - L + k, "RX" if i in pivots else "R", [Q[i]])
    for k, l in enumerate(layers):
        for u, v in l:
            b.op(end - L + 1 + k, "cx", (Q[u], Q[v]))


def build_round(tp, enc_o=None, enc_b=ENC, enc_c=ENC, base=8, t_b=2):
    """enc_o: None (standard dual encoder, ends at base-1) or (layers, pivots) json style."""
    b = poc.Builder()
    for d in range(7):
        b.op(base - 1, "id", [d])
    A = [b.fresh() for _ in range(7)]
    B = [b.fresh() for _ in range(7)]
    C = [b.fresh() for _ in range(7)]
    if enc_o is None:
        t_a = base - 1 - len(ENC)
        for i in range(7):
            b.op(t_a, "R" if i in PIV else "RX", [A[i]])
        for k, layer in enumerate(ENC):
            for p, q in layer:
                b.op(t_a + 1 + k, "cx", (A[q], A[p]))
    else:
        lazy_enc(b, A, enc_o[0], enc_o[1], base - 1)
    for i in range(7):
        b.op(t_b, "RX" if i in PIV else "R", [B[i]])
    for k, layer in enumerate(enc_b):
        for p, q in layer:
            b.op(t_b + 1 + k, "cx", (B[p], B[q]))
    t0 = base - 1 - len(enc_c)
    for i in range(7):
        b.op(t0, "RX" if i in PIV else "R", [C[i]])
    for k, layer in enumerate(enc_c):
        for p, q in layer:
            b.op(t0 + 1 + k, "cx", (C[p], C[q]))
    for i in range(7):
        b.op(base, "cx", (B[i], C[i]))
        b.op(base + 1, "M", [C[i]], ("C", i))
    for i in range(7):
        if tp:
            b.op(base, "cx", (A[i], i))
            b.op(base + 1, "M", [i], ("D", i))
            b.op(base + 1, "cx", (B[i], A[i]))
        else:
            b.op(base, "cx", (i, A[i]))
            b.op(base + 1, "M", [A[i]], ("A", i))
            b.op(base + 1, "cx", (B[i], i))
        b.op(base + 2, "MX", [B[i]], ("B", i))
    cat = {}
    k = "D" if tp else "A"
    for S in GENS:
        cat[("Z", S)] = [(k, i) for i in sorted(S)]
        cat[("X", S)] = [("B", i) for i in sorted(S)]
        cat[("C", S)] = [("C", i) for i in sorted(S)]
    cat[("C", frozenset(range(7)))] = [("C", i) for i in range(7)]
    return b, cat, [], (A if tp else list(range(7)))


def proxy(tp, **kw):
    b, cat, ver, out = build_round(tp, **kw)
    c, bit = emit_(b)
    s, err = to_stim(c.text(), n_qubits=c.n)
    assert not err, err
    noisy = apply_noise(s, 1e-3, STANDARD)
    nm = c.nbits
    stab = [("X", g) for g in GENS] + [("Z", g) for g in GENS]

    def full(logical):
        lines = [proxy2._mpp(B_, sorted(g)) for B_, g in stab] + [proxy2._mpp(logical, list(range(7)))]
        lines += [l for l in noisy.splitlines() if not l.startswith(("DETECTOR", "OBSERVABLE"))]
        lines += [proxy2._mpp(B_, [out[i] for i in sorted(g)]) for B_, g in stab] + [proxy2._mpp(logical, out)]
        n = 7 + nm + 7
        rec = lambda i: f"rec[{i - n}]"
        for (typ, S), tags in cat.items():
            init = [(0 if typ == "X" else 3) + i for i in poc.gens_of(S)] if typ in ("X", "Z") else []
            lines.append("DETECTOR " + " ".join(rec(7 + bit[t]) for t in tags) + " " + " ".join(rec(k) for k in init))
        for k in range(6):
            if tp and k >= 3:   # Z stabs of O ignore D; X stabs of O copy D's
                lines.append(f"OBSERVABLE_INCLUDE({k}) {rec(7 + nm + k)}")
            else:
                lines.append(f"OBSERVABLE_INCLUDE({k}) {rec(7 + nm + k)} {rec(k)}")
        extra = " ".join(rec(7 + bit[("D", i)]) for i in range(7)) if (tp and logical == "Z") else ""
        lines.append(f"OBSERVABLE_INCLUDE(6) {rec(7 + nm + 6)} {rec(6)} {extra}")
        return stim.Circuit("\n".join(lines))
    cx_, cz_ = full("X"), full("Z")
    for circ in (cx_, cz_):
        circ.without_noise().detector_error_model()
    steane.FIRST.clear()
    r = proxy2.joint_loss(cx_, cz_)
    return r, steane.FIRST[-1], c


def emit_(b):
    return poc.emit(b)


if __name__ == "__main__":
    A7307 = json_enc("/home/jihoon/competitions/quantumn/work/lanes/DR/prepA_L5_s7307.json", [1, 14, 8, 9, 2, 16, 15])
    EXACT = json_enc("/home/jihoon/competitions/quantumn/work/lanes/EXENC/prepA_L5_exact.json", [1, 14, 8, 9, 2, 16, 15])
    for name, enc in (("standard", None), ("L5 s7307", A7307), ("L5 exact", EXACT)):
        for tp in (False, True):
            try:
                r, f, c = proxy(tp, enc_o=enc)
                print(f"{name:10s} {'teleport' if tp else 'current ':8s}  loss {r:.4e}  first {f:.2e}  qubits {c.n} cx {c.n_2q()}", flush=True)
            except Exception as e:  # noqa: BLE001
                import traceback; traceback.print_exc()
                print(name, tp, "error", e)
