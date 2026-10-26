"""Exact arithmetic for the independently audited last-two-tick lower bound.

This is a mathematical channel certificate, not a quantum-circuit simulation.
The physical reduction is stated separately in penultimate_bound_proof.md.
Only Python's standard library is used. No files outside this directory are read.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
from math import lcm
from pathlib import Path
import json
import time

P = F(1, 1000)
Q = 2 * P / 5
R = 4 * P / 15
BITS = ((0, 0), (1, 0), (1, 1), (0, 1))
BIT_INDEX = {v: i for i, v in enumerate(BITS)}


def dep(p):
    return (1-p, p/3, p/3, p/3)


def compose(a, b):
    out = [F(0)] * 4
    for i, (xi, zi) in enumerate(BITS):
        for j, (xj, zj) in enumerate(BITS):
            out[BIT_INDEX[xi ^ xj, zi ^ zj]] += a[i] * b[j]
    return tuple(out)


def flip(r, axis):
    out = [1-r, F(0), F(0), F(0)]
    out[axis] = r
    return tuple(out)


def label(column, pauli):
    x, z = BITS[pauli]
    return (column if x else 0) | ((column if z else 0) << 3) | (x << 6) | (z << 7)


def conv(dist, terms):
    out = [0] * 256
    for state, mass in enumerate(dist):
        if mass:
            for error, weight in terms:
                out[state ^ error] += mass * weight
    return out


def moments(dist):
    """All 64 incoming sectors; never assume the input is in the code space."""
    dz = [0] * 8
    dxy = [[0] * 8 for _ in range(8)]
    total = sum(dist)
    for state, mass in enumerate(dist):
        sx, sz = state & 7, (state >> 3) & 7
        px, pz = (state >> 6) & 1, (state >> 7) & 1
        dz[sz] += (-mass if pz else mass)
        dxy[sx][sz] += (-mass if px ^ pz else mass)
    tz = sum(dz)
    rows = list(map(sum, dxy))
    cols = [sum(dxy[x][z] for x in range(8)) for z in range(8)]
    txy = sum(rows)
    result = []
    for x, z in product(range(8), repeat=2):
        vx = (-1 if z else 1) * (2*dz[z] - tz)
        vy = (-1 if bool(x) ^ bool(z) else 1) * (
            4*dxy[x][z] - 2*rows[x] - 2*cols[z] + txy)
        result.append((x, z, vx, vy))
    return total, result


def decimal_loss(norm_squared):
    with localcontext() as ctx:
        ctx.prec = 75
        n = Decimal(norm_squared.numerator) / Decimal(norm_squared.denominator)
        return str((1 - n.sqrt()) / 2)


def permutations():
    perms = set()
    for a, b, c in product(range(1, 8), repeat=3):
        images = tuple((a if k & 1 else 0) ^ (b if k & 2 else 0) ^
                       (c if k & 4 else 0) for k in range(1, 8))
        if len(set(images)) == 7 and 0 not in images:
            perms.add(tuple(i-1 for i in images))
    assert len(perms) == 168
    generators = (0b1010101, 0b1100110, 0b1111000)
    span = {0}
    for row in generators:
        span |= {v ^ row for v in tuple(span)}
    for perm in perms:
        assert {sum(((row >> k) & 1) << perm[k] for k in range(7))
                for row in span} == span
    return sorted(perms)


def orbits(alphabet):
    todo = {''.join(v) for v in product(alphabet, repeat=7)}
    perms = permutations()
    result = []
    while todo:
        rep = min(todo)
        members = {''.join(rep[p[k]] for k in range(7)) for p in perms}
        assert members <= todo
        todo -= members
        result.append((rep, sorted(members)))
    assert sum(len(m) for _, m in result) == len(alphabet) ** 7
    return result


def mapped_d2(name, mapping):
    den = 15000
    terms = [(mapping(a, b), int((1-P if a == b == 0 else P/15)*den))
             for a, b in product(range(4), repeat=2)]
    d = [0] * 256
    d[0] = 1
    d = conv(d, terms)
    total, sectors = moments(d)
    assert total == den
    norm = max(F(vx*vx + vy*vy, 2*total*total) for _, _, vx, vy in sectors)
    return {'name': name, 'terms_error_weight': terms, 'denominator': den,
            'minimum_loss': decimal_loss(norm), 'max_norm_squared': str(norm),
            'sectors_x_z_vx_vy': sectors,
            'maximizing_sectors': [s[:2] for s in sectors
                if F(s[2]**2 + s[3]**2, 2*total*total) == norm]}


def main():
    start = time.monotonic()
    q0 = (2*P/5)/(1-8*P/15)
    assert q0 >= Q and 2*Q/3 == R
    # All required scalar residual channels are CPTP at the specified p.
    assert 0 <= (P-2*Q/3)/(1-4*Q/3) <= 1  # output preparation
    assert 0 <= (P-R)/(1-2*R) <= 1         # helper preparation, anticommuting basis
    assert 0 <= (q0-Q)/(1-4*Q/3) <= 1      # measured partner factor
    binary_residual = ((1-5*R+5*R*R)/(1-2*R)**2,
                       R*R/(1-2*R)**2, R*R/(1-2*R)**2,
                       R*(1-3*R)/(1-2*R)**2)
    assert min(binary_residual) >= 0 and sum(binary_residual) == 1
    binary_product = ((1-R)**2, R*(1-R), R*(1-R), R*R)
    recovered = [sum(binary_product[a] * binary_residual[a ^ b] for a in range(4))
                 for b in range(4)]
    assert recovered == [1-3*R, R, R, R]

    channels = {
        'L': compose(dep(P), dep(Q)),
        'X': compose(compose(dep(4*P/5), dep(Q)), flip(R, 1)),
        'Z': compose(compose(dep(4*P/5), dep(Q)), flip(R, 3)),
        'P': compose(dep(4*P/5), dep(4*P/5)),
    }
    den = lcm(*(v.denominator for channel in channels.values() for v in channel))
    weights = {key: [int(v*den) for v in channel] for key, channel in channels.items()}
    total_expected = den ** 7
    max_numerator = -1
    cases = []
    for rep, members in orbits('LXPZ'):
        dist = [0] * 256
        dist[0] = 1
        for column, key in enumerate(rep, 1):
            dist = conv(dist, [(label(column, a), weights[key][a]) for a in range(4)])
        total, sectors = moments(dist)
        assert total == total_expected
        numerators = [vx*vx + vy*vy for _, _, vx, vy in sectors]
        maximum = max(numerators)
        max_numerator = max(max_numerator, maximum)
        cases.append({'representative': rep, 'members': members,
                      'orbit_size': len(members),
                      'sectors_x_z_vx_vy': sectors,
                      'maximizing_sectors': [s[:2] for s, n in zip(sectors, numerators)
                                             if n == maximum],
                      'maximum_numerator': maximum})
    norm = F(max_numerator, 2*total_expected**2)
    rounded_bound = F(2189, 10**8)
    assert norm <= (1-2*rounded_bound)**2
    winners = [c for c in cases if c['maximum_numerator'] == max_numerator]
    assert [c['representative'] for c in winners] == ['XXXXXXX']
    assert winners[0]['maximizing_sectors'] == [(0, 0)]
    assert sum(c['orbit_size'] for c in winners) == 1
    assert all(c['maximizing_sectors'] == [(0, 0)] for c in cases)

    li = lambda i, a: label(i, a)
    excluded = [
        mapped_d2('output_output', lambda a, b: li(1,a) ^ li(2,b)),
        mapped_d2('output_other_helper_X', lambda a, b: li(1,a) ^ (li(2,1) if BITS[b][0] else 0)),
        mapped_d2('output_other_helper_Z', lambda a, b: li(1,a) ^ (li(2,3) if BITS[b][1] else 0)),
        mapped_d2('helper_helper_XX', lambda a, b: (li(1,1) if BITS[a][0] else 0) ^ (li(2,1) if BITS[b][0] else 0)),
        mapped_d2('helper_helper_ZZ', lambda a, b: (li(1,3) if BITS[a][1] else 0) ^ (li(2,3) if BITS[b][1] else 0)),
    ]
    for ex in excluded:
        assert F(ex['max_norm_squared']) <= (1-2*F(133,10**6))**2
        assert F(ex['max_norm_squared']) < norm
    opposite = mapped_d2('helper_helper_XZ', lambda a, b: (li(1,1) if BITS[a][0] else 0) ^ (li(2,3) if BITS[b][1] else 0))
    assert opposite['minimum_loss'] == '0'

    summary = {
        'status': 'New independently audited bound under the inspected STANDARD contract; not official endorsement or an attainability claim',
        'p': str(P), 'q': str(Q), 'r': str(R), 'q0': str(q0),
        'channels_probability_denominator': den,
        'channels_probability_numerators_I_X_Y_Z': weights,
        'binary_residual_00_10_01_11': list(map(str, binary_residual)),
        'moment_denominator': total_expected,
        'assignments': 4**7, 'sectors_per_assignment': 64,
        'sector_inequalities': 4**7*64,
        'symmetry_group_order': 168, 'orbit_count': len(cases),
        'minimum_loss': decimal_loss(norm), 'max_norm_squared': str(norm),
        'certified_rounded_down_lower_bound': str(rounded_bound),
        'unique_minimizing_assignment': 'XXXXXXX', 'unique_best_sector': [0,0],
        'excluded_channels': [{k:v for k,v in e.items() if k not in ('sectors_x_z_vx_vy', 'terms_error_weight')}
                              for e in excluded],
        'seconds': time.monotonic()-start,
    }
    here = Path(__file__).resolve().parent
    (here/'penultimate_bound_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    certificate = dict(summary, cases=cases, excluded_channel_certificates=excluded,
                       opposite_axis_channel_certificate=opposite)
    (here/'penultimate_bound_certificate.json').write_text(json.dumps(certificate, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
