"""Lower bounds on 1-F from undetectable output 'tails', and v6's actual tail masses.

After a data qubit's last check CNOT nothing can detect its errors, and the judge's ideal lookup
correction miscorrects any weight-2 error. Two undetected errors on different data qubits give
X_L (cost 1/2), Y_L (1/2) or Z_L (1). Second-order loss = sum over qubit pairs of
m_a[P] m_b[Q] cost(P, Q), with m_q[P] the undetected probability of Pauli P on qubit q.

Minimal per-qubit masses under the judge's noise (p per gate/idle step, DEPOLARIZE2 = 15 Paulis
of p/15), for a qubit whose last two CNOTs are the two check types in consecutive steps s-1, s:
  * last CNOT's fault is undetected only if its ancilla part is invisible to the readout:
    direct single-basis readout -> ancilla Pauli in {I, readout basis} (2/15 per data Pauli);
    Bell-pair (superdense) readout -> ancilla Pauli I only (1/15).
  * the previous CNOT (other type) leaves its own type undetected the same way.
  * idle until the end: 1 step for direct readout (ancilla measured at s+1), 2 steps for Bell
    readout (unbell at s+1, measure at s+2), p/3 per Pauli per step.
  * or, instead of that idle step, a dummy CX(q -> data) from a |0> partner q that was itself checked
    by CX(q -> c) at step s (c read in Z): the data gets DEPOLARIZE2's marginal (4/15 per Pauli) plus
    q's undetectable X (4/15). This beats idling, so one idle step on every data qubit is not forced.
"""
import itertools


def cost(P, Q):
    fx = ("X" in P or "Y" in P) and ("X" in Q or "Y" in Q)   # X parts weight 2 -> X_L
    fz = ("Z" in P or "Y" in P) and ("Z" in Q or "Y" in Q)   # Z parts weight 2 -> Z_L
    if fx:
        return 0.5           # X_L or Y_L
    return 1.0 if fz else 0.0


def pair_loss(masses):
    """masses: list of dicts {X,Y,Z: prob}. Second-order loss over distinct-qubit pairs."""
    tot = 0.0
    for a, b in itertools.combinations(masses, 2):
        for P, pa in a.items():
            for Q, pb in b.items():
                tot += pa * pb * cost(P, Q)
    return tot


H = [[0, 0, 0, 1, 1, 1, 1], [0, 1, 1, 0, 0, 1, 1], [1, 0, 1, 0, 1, 0, 1]]


def exact_loss(masses):
    """All orders over 4^7 patterns of independent per-qubit channels, with the judge's lookup decoding."""
    def syn(v):
        return tuple(sum(h[i] * v[i] for i in range(7)) % 2 for h in H)
    fix = {syn([int(j == i) for j in range(7)]): i for i in range(7)}

    def logical(v):
        s = syn(v)
        w = list(v)
        if any(s):
            w[fix[s]] ^= 1
        return sum(w) % 2 == 1
    tot = 0.0
    for pat in itertools.product("IXYZ", repeat=7):
        pr = 1.0
        for P, m in zip(pat, masses):
            pr *= 1 - sum(m.values()) if P == "I" else m[P]
        if pr < 1e-13:
            continue
        fx = logical([P in "XY" for P in pat])
        fz = logical([P in "ZY" for P in pat])
        tot += pr * (0.5 if fx else (1.0 if fz else 0.0))
    return tot


def final_step(dummy, p=1e-3):
    """Undetectable noise of the final step alone: idle (p/3 per Pauli) or the dummy CX above."""
    return {"X": 8 * p / 15, "Y": 4 * p / 15, "Z": 4 * p / 15} if dummy else {P: p / 3 for P in "XYZ"}


def tail(kind, last, p=1e-3, dummy=False):
    """Minimal tail of one qubit. kind: 'direct' or 'bell'; last: type of the final check CNOT
    ('X' = X-check, catches Z-type errors; 'Z' = Z-check); dummy: final step as in final_step."""
    g = (2 if kind == "direct" else 1) / 15 * p
    end = final_step(dummy, p) if kind == "direct" else {P: 2 * p / 3 for P in "XYZ"}
    m = {P: g + end[P] for P in "XYZ"}             # last CNOT + final step: every Pauli undetected
    other = "X" if last == "X" else "Z"            # X-check last -> X-only errors also escape...
    m["X" if last == "X" else "Z"] += g            # ...from the previous (Z-check) CNOT
    return m


if __name__ == "__main__":
    for dummy in (False, True):
        print(f"final step only, dummy={dummy}: {exact_loss([final_step(dummy)] * 7):.4e} (exact)")
    best = min(pair_loss([tail("direct", o, dummy=True) for o in orient]) for orient in itertools.product("XZ", repeat=7))
    print(f"direct readout floor with dummy final steps: {best:.3e}")
    for kind in ("direct", "bell"):
        best = min((pair_loss([tail(kind, o) for o in orient]), orient)
                   for orient in itertools.product("XZ", repeat=7))
        print(f"{kind:6s} readout floor: {best[0]:.3e}   (last check type per qubit {''.join(best[1])})")
