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


def tail(kind, last, p=1e-3):
    """Minimal tail of one qubit. kind: 'direct' or 'bell'; last: type of the final check CNOT
    ('X' = X-check, catches Z-type errors; 'Z' = Z-check)."""
    g = (2 if kind == "direct" else 1) / 15 * p
    idle = (1 if kind == "direct" else 2) * p / 3
    m = {P: g + idle for P in "XYZ"}               # last CNOT + idle: every Pauli undetected
    other = "X" if last == "X" else "Z"            # X-check last -> X-only errors also escape...
    m["X" if last == "X" else "Z"] += g            # ...from the previous (Z-check) CNOT
    return m


if __name__ == "__main__":
    for kind in ("direct", "bell"):
        best = min((pair_loss([tail(kind, o) for o in orient]), orient)
                   for orient in itertools.product("XZ", repeat=7))
        print(f"{kind:6s} readout floor: {best[0]:.3e}   (last check type per qubit {''.join(best[1])})")
