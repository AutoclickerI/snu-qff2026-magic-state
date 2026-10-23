"""Grid-free Steane-type final round: each data qubit couples once to a |+_L> block (CX data->a,
block read in Z: Z-stabilizer parities catch data X errors) and once to a |0_L> block (CX b->data,
block read in X: X-stabilizer parities catch data Z errors). Each data qubit does two CNOTs.

Block A's Z errors land on the data before block B checks them, so A needs no verification. Block
B's X errors land on the data after the last X check, so B's encoder is verified by Z-type parity
ancillas (`ver`: list of supports, each read by one ancilla) before coupling.

Scored with poc.proxy (exact second-order loss on the judge's noise; v11 round = 1.098e-4).

    python steane.py
"""
import itertools
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR")
import poc  # noqa: E402

GENS = poc.GENS
PIV = {0: [2, 4, 6], 1: [2, 5, 6], 3: [4, 5, 6]}       # pivot -> targets (pivot only in its generator)
ENC = [[(0, 2), (1, 5), (3, 6)], [(0, 4), (1, 6), (3, 5)], [(0, 6), (1, 2), (3, 4)]]
W3 = [frozenset(c) for c in itertools.combinations(range(7), 3)
      if all(len(set(c) & g) % 2 == 0 for g in GENS)]   # weight-3 logical supports


def build_steane(enc_a=ENC, enc_b=ENC, ver=(), t_b=2, t_a=4, base=8, gap=0, vblock=False, enc_c=ENC, t_c0=None):
    """t_b, t_a: init steps of blocks B and A. A couples at base, B at base + 1 + gap."""
    b = poc.Builder()
    for d in range(7):
        b.op(base - 1, "id", [d])
    A = [b.fresh() for _ in range(7)]
    B = [b.fresh() for _ in range(7)]
    # block A = H-dual of the |0_L> encoder: pivots |0>, others |+>, CX target -> pivot
    for i in range(7):
        b.op(t_a, "R" if i in PIV else "RX", [A[i]])
    for k, layer in enumerate(enc_a):
        for p, q in layer:
            b.op(t_a + 1 + k, "cx", (A[q], A[p]))
    # block B = |0_L>: pivots |+>, others |0>, CX pivot -> target
    for i in range(7):
        b.op(t_b, "RX" if i in PIV else "R", [B[i]])
    for k, layer in enumerate(enc_b):
        for p, q in layer:
            b.op(t_b + 1 + k, "cx", (B[p], B[q]))
    ver_tags = []
    t_enc = t_b + len(enc_b)                # last encoder step of B
    busy = {}
    for t, _, kind, qs, _ in b.ops:
        for q in qs:
            busy.setdefault(q, set()).add(t)
    t_c = base + gap                        # verification CNOTs end before B couples
    for j, S in enumerate(ver):
        v = b.fresh()
        steps, t = [], t_c
        for q in sorted(S, reverse=True):
            while t in busy.get(B[q], set()) or t in steps:
                t -= 1
            if t <= t_enc:
                raise ValueError("verification overlaps the encoder; start B earlier")
            steps.append(t)
            busy.setdefault(B[q], set()).add(t)
        b.op(min(steps) - 1, "R", [v])
        for t, q in zip(steps, sorted(S, reverse=True)):
            b.op(t, "cx", (B[q], v))
        tag = ("ver", j)
        b.op(max(steps) + 1, "M", [v], tag)
        ver_tags.append(tag)
    cat_bits = {}
    if vblock:
        # block C = |0_L>, unverified: CX b->c copies B's X errors (X_L class included) onto C, read in Z
        C = [b.fresh() for _ in range(7)]
        t0 = base + gap - 1 - len(enc_c) if t_c0 is None else t_c0
        for i in range(7):
            b.op(t0, "RX" if i in PIV else "R", [C[i]])
        for k, layer in enumerate(enc_c):
            for p, q in layer:
                b.op(t0 + 1 + k, "cx", (C[p], C[q]))
        for i in range(7):
            b.op(base + gap, "cx", (B[i], C[i]))
            b.op(base + gap + 1, "M", [C[i]], ("C", i))
        for k, S in enumerate(GENS):
            cat_bits[("C", S)] = [("C", i) for i in sorted(S)]
        cat_bits[("C", frozenset(range(7)))] = [("C", i) for i in range(7)]
    for i in range(7):
        b.op(base, "cx", (i, A[i]))
        b.op(base + 1, "M", [A[i]], ("A", i))
        b.op(base + 1 + gap, "cx", (B[i], i))
        b.op(base + 2 + gap, "MX", [B[i]], ("B", i))
    for S in GENS:
        cat_bits[("Z", S)] = [("A", i) for i in sorted(S)]
        cat_bits[("X", S)] = [("B", i) for i in sorted(S)]
    return b, cat_bits, ver_tags


KEEP = None      # optional predicate on the qubits of a noise channel (noise isolation)
_apply = poc.apply_noise


def _noise(s, p, model):
    out = []
    for line in _apply(s, p, model).splitlines():
        name = line.split("(")[0]
        if KEEP is not None and name in ("DEPOLARIZE1", "DEPOLARIZE2", "X_ERROR", "Z_ERROR"):
            qs = [int(x) for x in line.split(")")[1].split()]
            k = 2 if name == "DEPOLARIZE2" else 1
            qs = [g for g in (tuple(qs[i:i + k]) for i in range(0, len(qs), k)) if KEEP(g)]
            if not qs:
                continue
            line = line.split(")")[0] + ") " + " ".join(str(q) for g in qs for q in g)
        out.append(line)
    return "\n".join(out)


poc.apply_noise = _noise


def score(**kw):
    r, c = poc.proxy(builder=lambda s: build_steane(**kw))
    return r, c


if __name__ == "__main__":
    for ver in [(), *[(S,) for S in W3]]:
        try:
            r, c = score(ver=ver)
            print(f"ver {[sorted(S) for S in ver]}: {r:.4e}  qubits {c.n}  cx {c.n_2q()}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"ver {[sorted(S) for S in ver]}: error {e}", flush=True)


FIRST = []
_jl = poc.proxy2.joint_loss


def _joint(cx, cz):
    """joint_loss, also recording its first-order part (must be 0 for a fault-tolerant round)."""
    A, B = poc.proxy2._mechanisms(cx), poc.proxy2._mechanisms(cz)
    keys = {k for k in set(A) | set(B) if not k[0]}
    f = 0.0
    for k in keys:
        stab = k[1]
        for p, fl in A.get(k, []):
            f += p * ((fl ^ (1 if stab & 0b000111 else 0)) and 1)
        for p, fl in B.get(k, []):
            f += p * 0.5 * ((fl ^ (1 if stab & 0b111000 else 0)) and 1)
    FIRST.append(f)
    return _jl(cx, cz)


poc.proxy2.joint_loss = _joint
