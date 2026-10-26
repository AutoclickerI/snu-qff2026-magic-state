"""Check the certificate by a separate 256-bin integer convolution.

This uses all 2,187 assignments directly, without symmetry reduction or imports
from strengthened.py. A stronger rational enclosure is checked for the optimum.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
c = json.loads((HERE/'certificate.json').read_text())
den = c['probability_denominator']
w = c['probability_numerators_I_X_Y_Z']
assert all(sum(v) == den and min(v) >= 0 for v in w.values())
moment_den = den**7
assert moment_den == c['moment_denominator']
claimed = F(c['max_norm_squared'])
lower = F(1365785079053665, 10**20)
upper = lower+F(1, 10**20)
assert (1-2*upper)**2 < claimed <= (1-2*lower)**2

# Bits encode X syndrome 0..2, Z syndrome 3..5, X parity 6, Z parity 7.
increments = []
for position in range(1,8):
    x, z = position | 64, (position << 3) | 128
    increments.append((0, x, x ^ z, z))


def step(dist, site, label):
    out = [0]*256
    for state, n in enumerate(dist):
        if n:
            for k in range(4):
                out[state ^ increments[site][k]] += n*w[label][k]
    return out


# Cache common prefixes in a ternary tree; each leaf is still verified directly.
frontier = {'': [1]+[0]*255}
for site in range(7):
    frontier = {prefix+label: step(dist, site, label)
                for prefix,dist in frontier.items() for label in 'LXZ'}
assert len(frontier) == 2187
by_member = {}
for case in c['cases']:
    for member in case['members']:
        assert member not in by_member
        by_member[member] = case
assert set(by_member) == set(frontier)
observed = F(0)
maximizers = []
for labels, dist in frontier.items():
    assert sum(dist) == moment_den
    # Transform to signed syndrome distributions using a different accumulation.
    sign_z = [0]*8
    sign_xy = [[0]*8 for _ in range(8)]
    for state, n in enumerate(dist):
        sx, sz = state & 7, (state >> 3) & 7
        px, pz = (state >> 6) & 1, state >> 7
        sign_z[sz] += n*(-1)**pz
        sign_xy[sx][sz] += n*(-1)**(px ^ pz)
    # Apply the decoder signs by direct sum, independent of the optimized formula.
    vz = [sum(n*(-1)**(bool(z) ^ bool(z ^ sz)) for sz,n in enumerate(sign_z))
          for z in range(8)]
    vx_y = [sum(sign_xy[sx][sz]*(-1)**(bool(x) ^ bool(z) ^ bool(x ^ sx) ^ bool(z ^ sz))
                for sx,sz in product(range(8), repeat=2))
            for x,z in product(range(8), repeat=2)]
    norms = [F(vz[z]**2+vx_y[8*x+z]**2, 2*moment_den**2)
             for x,z in product(range(8), repeat=2)]
    maximum = max(norms)
    assert maximum == F(by_member[labels]['max_norm_squared'])
    assert maximum <= claimed
    if labels == by_member[labels]['representative']:
        expected = [[x,z,vz[z],vx_y[8*x+z]] for x,z in product(range(8), repeat=2)]
        assert expected == by_member[labels]['sectors_x_z_vx_numerator_vy_numerator']
    if maximum > observed:
        observed, maximizers = maximum, [labels]
    elif maximum == observed:
        maximizers.append(labels)
assert observed == claimed and maximizers == ['XXXXXXX']
out = {'all_assignments_checked_without_symmetry': len(frontier), 'sectors_each': 64,
       'total_sector_inequalities': 2187*64, 'maximizers': maximizers,
       'rational_lower_bound': str(lower), 'rational_upper_bound_on_relaxation_optimum': str(upper),
       'certificate_verified': True}
(HERE/'verification.json').write_text(json.dumps(out, indent=2)+'\n')
print(json.dumps(out, indent=2))
