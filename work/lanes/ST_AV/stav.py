"""Steane-type round with a D verifier block for A (grid-free exact proxy).

Step T-1: CX dd_i -> a_i (D = |+_L> control, A target), T: CX d_i->a_i and CX b_i->c_i,
T+1: measure A, C (Z), CX b_i->d_i, and MX D at T... (D read X at step T).  B read X at T+2.
"""
import json
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR")
import poc  # noqa: E402
import steane  # noqa: E402  (patches poc.proxy2.joint_loss to record the first-order part)

PIV = steane.PIV
ENC = steane.ENC
GENS = poc.GENS
PIN = [0.0]

# standard |+_L> encoder (H-dual): spec = (layers of (control,target), init kinds)
STD_PLUS = ([[(q, p) for p, q in layer] for layer in ENC], {i: ("R" if i in PIV else "RX") for i in range(7)})


def spec_from_json(path, cells):
    js = json.load(open(path))
    idx = {c: i for i, c in enumerate(cells)}
    layers = [[(idx[u], idx[v]) for u, v in l] for l in js["ops"]]
    piv = {idx[c] for c in js["pivots"]}
    return layers, {i: ("RX" if i in piv else "R") for i in range(7)}


A_CELLS = [1, 14, 8, 9, 2, 16, 15]
SPECS = {
    "std": STD_PLUS,
    "s7307": spec_from_json("/home/jihoon/competitions/quantumn/work/lanes/DR/prepA_L5_s7307.json", A_CELLS),
    "exact": spec_from_json("/home/jihoon/competitions/quantumn/work/lanes/EXENC/prepA_L5_exact.json", A_CELLS),
}


def plus_block(b, spec, last):
    """Build |+_L> with its last encoder layer at step `last`; qubits reset just before first use."""
    layers, init = spec
    Q = [b.fresh() for _ in range(7)]
    L = len(layers)
    first = {}
    for k, layer in enumerate(layers):
        for u, v in layer:
            first.setdefault(u, k)
            first.setdefault(v, k)
    for i in range(7):
        b.op(last - L + first.get(i, L) , init[i], [Q[i]])      # step before its first layer
    for k, layer in enumerate(layers):
        for u, v in layer:
            b.op(last - L + 1 + k, "cx", (Q[u], Q[v]))
    return Q


def zero_block(b, enc, t0):
    Q = [b.fresh() for _ in range(7)]
    for i in range(7):
        b.op(t0, "RX" if i in PIV else "R", [Q[i]])
    for k, layer in enumerate(enc):
        for p, q in layer:
            b.op(t0 + 1 + k, "cx", (Q[p], Q[q]))
    return Q


def build(spec_a="std", spec_d=None, base=20, gap=0):
    """spec_d None: no verifier block."""
    sa = SPECS[spec_a]
    b = poc.Builder()
    for d in range(7):
        b.op(base - 1, "id", [d])
    tv = base - 1 - gap          # D->A coupling step
    A = plus_block(b, sa, tv - 1 if spec_d else base - 1)
    cat = {}
    if spec_d:
        D = plus_block(b, SPECS[spec_d], tv - 1)
        for i in range(7):
            b.op(tv, "cx", (D[i], A[i]))
            b.op(tv + 1, "MX", [D[i]], ("D", i))
        for S in GENS:
            cat[("D", S)] = [("D", i) for i in sorted(S)]
        cat[("D", frozenset(range(7)))] = [("D", i) for i in range(7)]
    B = zero_block(b, ENC, base - 6)
    C = zero_block(b, ENC, base - 4)
    for i in range(7):
        b.op(base, "cx", (i, A[i]))
        b.op(base, "cx", (B[i], C[i]))
        b.op(base + 1, "M", [A[i]], ("A", i))
        b.op(base + 1, "M", [C[i]], ("C", i))
        b.op(base + 1, "cx", (B[i], i))
        b.op(base + 2, "MX", [B[i]], ("B", i))
    for S in GENS:
        cat[("Z", S)] = [("A", i) for i in sorted(S)]
        cat[("X", S)] = [("B", i) for i in sorted(S)]
        cat[("C", S)] = [("C", i) for i in sorted(S)]
    cat[("C", frozenset(range(7)))] = [("C", i) for i in range(7)]
    return b, cat, []


_orig = poc.apply_noise


def _noise(s, p, model):
    t = _orig(s, p, model)
    if PIN[0]:
        t = f"DEPOLARIZE1({PIN[0]}) " + " ".join(map(str, range(7))) + "\n" + t
    return t


poc.apply_noise = _noise


def score(spec_a, spec_d, pin, gap=0):
    PIN[0] = pin
    steane.FIRST.clear()
    r, c = poc.proxy(builder=lambda s: build(spec_a, spec_d, gap=gap))
    return r, steane.FIRST[0], c.n, c.n_2q()


if __name__ == "__main__":
    import itertools
    for sa in ["std", "s7307", "exact"]:
        for pin in [0, 5e-3, 1e-2, 2e-2]:
            for sd in [None, "std", "exact"]:
                if sd and sd == "exact" and sa == "std":
                    pass
                try:
                    r, f, n, cx = score(sa, sd, pin)
                    print(f"A={sa} D={sd} pin={pin}: {r:.4e} first={f:.1e} qubits {n} cx {cx}", flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"A={sa} D={sd} pin={pin}: error {e!r}", flush=True)
