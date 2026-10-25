"""Independent 128x128 decoder/channel calculation; no exact-code imports.

Constructs the decoded fidelity observable directly from the judge's stabilizers.
Constructs terminal channels by conjugating two-qubit Kraus Paulis through CX,
then compares every eigenvalue with the rational certificate's 64 blocks.
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import json
import numpy as np

HERE = Path(__file__).resolve().parent
p, q = 0.001, 0.0002
paulis = [np.eye(2, dtype=complex), np.array([[0,1],[1,0]], dtype=complex),
          np.array([[0,-1j],[1j,0]], dtype=complex), np.diag([1,-1]).astype(complex)]
eye = np.eye(128, dtype=complex)
supports = ({0,2,4,6}, {1,2,5,6}, {3,4,5,6})


def tensor(label, support):
    result = np.ones((1,1), dtype=complex)
    for k in reversed(range(7)):
        result = np.kron(result, paulis[label if k in support else 0])
    return result


def any_syndrome_sign(axis):
    zero = eye.copy()
    for support in supports:
        zero = zero @ ((eye+tensor(axis, support))/2)
    return 2*zero-eye


def marginal_channels():
    # Tensor order = data, helper. Generate CX matrices from their truth tables.
    channels = {}
    probs = [1-q, q/3, q/3, q/3]
    for label, control in [('X', 1), ('Z', 0)]:
        cx = np.zeros((4,4), dtype=complex)
        for data, helper in product(range(2), repeat=2):
            d, h = (data ^ helper, helper) if control == 1 else (data, helper ^ data)
            cx[2*d+h, 2*data+helper] = 1
        eigen = []
        for axis in range(4):
            obs = np.kron(paulis[axis], paulis[0])
            noisy = np.zeros((4,4), dtype=complex)
            for a, b, c, d in product(range(4), repeat=4):
                propagated = cx @ np.kron(paulis[a], paulis[b]) @ cx.conj().T
                error = np.kron(paulis[c], paulis[d]) @ propagated
                probability = probs[a]*probs[b]*(1-p if c == d == 0 else p/15)
                noisy += probability*(error.conj().T @ obs @ error)
            value = np.trace(obs @ noisy).real/4
            assert np.max(np.abs(noisy-value*obs)) < 2e-14
            eigen.append(value)
        # Inverse one-qubit Pauli transfer transform.
        a, x, y, z = eigen
        channels[label] = np.array([a+x+y+z, a+x-y-z, a-x+y-z, a-x-y+z])/4
    # Independent sequential one-qubit channels for the idle/local case.
    base = np.array([1., 0, 0, 0])
    # I,X,Y,Z have bit labels 0,1,3,2; implement composition by matrices.
    for strength in (q, p):
        new = np.zeros(4)
        for i, j in product(range(4), repeat=2):
            matrix = paulis[i] @ paulis[j]
            overlaps = [abs(np.trace(k.conj().T @ matrix))/2 for k in paulis]
            new[int(np.argmax(overlaps))] += base[i]*([1-strength]+[strength/3]*3)[j]
        base = new
    channels['L'] = base
    return channels


sx, sz = any_syndrome_sign(1), any_syndrome_sign(3)
# check.py uses X^7 and physical Y^7 with target (+1,-1)/sqrt(2).
H = (eye+(sx @ tensor(1, set(range(7)))-sx @ sz @ tensor(2, set(range(7))))/np.sqrt(2))/2
assert np.max(np.abs(H-H.conj().T)) < 1e-14
assert np.max(np.abs(H @ H-H)) < 1e-14
local = {(k,a): tensor(a,{k}) for k in range(7) for a in range(1,4)}
channels = marginal_channels()
certificate = json.loads((HERE/'certificate.json').read_text())
den = certificate['probability_denominator']
channel_error = max(np.max(np.abs(channels[k]-np.array(v, dtype=float)/den))
                    for k,v in certificate['probability_numerators_I_X_Y_Z'].items())
assert channel_error < 5e-14


def apply_channel(observable, site, weights):
    result = weights[0]*observable
    for a in range(1,4):
        P = local[site,a]
        result = result+weights[a]*(P @ observable @ P)
    return result


rows = []
maximum_spectrum_error = 0.
for case in certificate['cases']:
    obs = H.copy()
    for k, label in enumerate(case['representative']):
        obs = apply_channel(obs, k, channels[label])
    spectrum = np.linalg.eigvalsh(obs)
    reference = []
    for _, _, nx, ny in case['sectors_x_z_vx_numerator_vy_numerator']:
        vx = float(Fraction(nx, certificate['moment_denominator']))
        vy = float(Fraction(ny, certificate['moment_denominator']))
        r = np.sqrt((vx*vx+vy*vy)/2)
        reference += [(1-r)/2, (1+r)/2]
    error = float(np.max(np.abs(spectrum-np.sort(reference))))
    maximum_spectrum_error = max(maximum_spectrum_error, error)
    rows.append({'type': case['representative'], 'loss': float(1-spectrum[-1]),
                 'spectrum_error': error})
assert maximum_spectrum_error < 5e-13
out = {'method': 'Direct 128x128 decoder and independently propagated 4x4 CX noise',
       'cases': len(rows), 'eigenvalues_checked': 128*len(rows),
       'max_channel_probability_error': float(channel_error),
       'max_all_eigenvalues_error': maximum_spectrum_error,
       'minimum_loss': min(r['loss'] for r in rows),
       'minimizing_structure': min(rows, key=lambda r: r['loss'])['type'], 'rows': rows}
(HERE/'matrix_check.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k != 'rows'}, indent=2))
