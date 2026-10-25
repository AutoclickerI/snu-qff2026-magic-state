"""Independent dense-matrix check of the judge's terminal decoded fidelity.

This does not use the syndrome-distribution code in terminal_bound.py.
It constructs the actual 128-dimensional observable from the six stabilizers
and the signs used by upstream tprep/check.py, then diagonalizes it.
Requires NumPy; rational certification is in subthreshold_bound/terminal_bound.py.
"""
import json
from itertools import combinations, product
from pathlib import Path

import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)
I = np.eye(128, dtype=complex)
SUPPORTS = [{0, 2, 4, 6}, {1, 2, 5, 6}, {3, 4, 5, 6}]


def tensor_on(op, support):
    result = np.array([[1]], dtype=complex)
    for q in range(6, -1, -1):
        result = np.kron(result, op if q in support else I2)
    return result


def syndrome_sign(op):
    # +1 iff all three stabilizers have outcome 0; otherwise -1.
    projector = I.copy()
    for support in SUPPORTS:
        projector = projector @ ((I + tensor_on(op, support)) / 2)
    return 2 * projector - I


SX, SZ = syndrome_sign(X), syndrome_sign(Z)
logical_x = tensor_on(X, set(range(7)))
physical_y7 = tensor_on(Y, set(range(7)))
decoded_x = SX @ logical_x
decoded_y = -SX @ SZ @ physical_y7  # logical Y = -Y^7
H = (I + (decoded_x + decoded_y) / np.sqrt(2)) / 2
assert np.max(np.abs(H.conj().T - H)) < 1e-14
assert np.max(np.abs(H @ H - H)) < 1e-14
assert abs(np.trace(H).real - 64) < 1e-12
local_paulis = {
    (q, a): tensor_on(op, {q})
    for q in range(7) for a, op in enumerate([I2, X, Y, Z])
}


def dep1_adjoint(observable, q, site):
    out = (1 - q) * observable
    for a in range(1, 4):
        P = local_paulis[site, a]
        out = out + q / 3 * (P @ observable @ P)
    return out


def dep2_adjoint(observable, p, pair):
    out = (1 - p) * observable
    for a, b in product(range(4), repeat=2):
        if a == b == 0:
            continue
        P = local_paulis[pair[0], a] @ local_paulis[pair[1], b]
        out = out + p / 15 * (P @ observable @ P)
    return out


p = 0.001
out = {"method": "128x128 observable built directly from judge stabilizers and signs", "p": p}
out["local_channels"] = {}
for name, q in [
    ("last_CX_only", 4 * p / 5),
    ("last_idle_only", p),
    ("two_tick_extracted", p - 16 * p * p / 75),
]:
    noisy_H = H.copy()
    for site in range(7):
        noisy_H = dep1_adjoint(noisy_H, q, site)
    eigenvalues = np.linalg.eigvalsh(noisy_H)
    out["local_channels"][name] = {
        "q": q,
        "minimum_loss_over_all_128_dimensional_states": float(1 - eigenvalues[-1]),
    }

pair_losses = []
for pair in combinations(range(7), 2):
    eigenvalues = np.linalg.eigvalsh(dep2_adjoint(H, p, pair))
    pair_losses.append(float(1 - eigenvalues[-1]))
out["final_data_data_CX"] = {
    "pairs_checked": len(pair_losses),
    "minimum_loss_across_pairs": min(pair_losses),
    "maximum_loss_across_pairs": max(pair_losses),
}

reference = 0.00001162029638920668820439987200204524
computed = out["local_channels"]["two_tick_extracted"]["minimum_loss_over_all_128_dimensional_states"]
assert abs(computed - reference) < 5e-14
assert min(pair_losses) > 0.0003333
out["agreement_with_rational_result_absolute_error"] = abs(computed - reference)
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
