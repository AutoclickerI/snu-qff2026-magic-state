"""Exact terminal-channel certificate; stdlib only, no reviewer imports.

Run with the repository .venv/bin/python -I on hippo, with BLAS threads set to 1.
Pauli ordering is I,X,Y,Z. L=local/idle, X=helper control, Z=helper target.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
from math import lcm, prod
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
P = F(1, 1000)
Q = P / 5
CERTIFIED = F(13657, 10**9)
BITS = [(0, 0), (1, 0), (1, 1), (0, 1)]
INDEX = {b: k for k, b in enumerate(BITS)}


def dep(q):
    return [1-q, q/3, q/3, q/3]


def compose(a, b):
    out = [F(0)] * 4
    for i, (xi, zi) in enumerate(BITS):
        for j, (xj, zj) in enumerate(BITS):
            out[INDEX[xi ^ xj, zi ^ zj]] += a[i] * b[j]
    return out


def final_cx_marginal(helper_control):
    """Explicitly propagate both independent Q errors, then all 16 D2 errors."""
    out = [F(0)] * 4
    for d, h, e, f in product(range(4), repeat=4):
        xd, zd = BITS[d]
        xh, zh = BITS[h]
        if helper_control:
            xd ^= xh
        else:
            zd ^= zh
        xe, ze = BITS[e]
        weight = dep(Q)[d] * dep(Q)[h] * (1-P if e == f == 0 else P/15)
        out[INDEX[xd ^ xe, zd ^ ze]] += weight
    assert sum(out) == 1
    return out


def local_channels():
    a, lam = 1-4*Q/3, 1-16*P/15
    r = [(1+6*lam/a+9*lam/a**2)/16,
         (1+2*lam/a-3*lam/a**2)/16,
         (1-2*lam/a+lam/a**2)/16]
    assert min(r) >= 0 and r[0]+6*r[1]+9*r[2] == 1
    # Explicit convolution also checks the simultaneous two-operand extraction.
    residual = [r[0] if i == j == 0 else r[1] if i == 0 or j == 0 else r[2]
                for i, j in product(range(4), repeat=2)]
    recovered = [F(0)] * 16
    for i, j, k, m in product(range(4), repeat=4):
        x, z = BITS[i][0] ^ BITS[k][0], BITS[i][1] ^ BITS[k][1]
        y, w = BITS[j][0] ^ BITS[m][0], BITS[j][1] ^ BITS[m][1]
        recovered[4*INDEX[x,z]+INDEX[y,w]] += dep(Q)[i]*dep(Q)[j]*residual[4*k+m]
    assert recovered == [1-P]+[P/15]*15
    reset = (P-2*Q/3)/(1-4*Q/3)
    assert 0 <= reset <= 1 and (1-4*Q/3)*(1-2*reset) == 1-2*P
    channels = {'L': compose(dep(P), dep(Q)),
                'X': final_cx_marginal(True), 'Z': final_cx_marginal(False)}
    qe = Q+4*P/5-4*Q*(4*P/5)/3
    for label, axis in [('X', 1), ('Z', 3)]:
        flip = [1-2*Q/3, F(0), F(0), F(0)]
        flip[axis] = 2*Q/3
        assert channels[label] == compose(dep(qe), flip)
    return channels, {'D2_residual_II_weight1_weight2': list(map(str, r)),
                      'reset_residual': str(reset), 'qeff': str(qe)}


def automorphisms():
    perms = set()
    for a, b, c in product(range(1, 8), repeat=3):
        images = tuple((a if x & 1 else 0) ^ (b if x & 2 else 0) ^
                       (c if x & 4 else 0) for x in range(1, 8))
        if len(set(images)) == 7 and 0 not in images:
            perms.add(tuple(x-1 for x in images))
    assert len(perms) == 168
    # Confirm preservation of the actual three-generator stabilizer row space.
    rows = (0b1010101, 0b1100110, 0b1111000)
    span = {0}
    for row in rows:
        span |= {x ^ row for x in tuple(span)}
    for perm in perms:
        assert {sum(((r >> k) & 1) << perm[k] for k in range(7)) for r in span} == span
    return sorted(perms)


def orbits():
    perms = automorphisms()
    todo = {''.join(x) for x in product('LXZ', repeat=7)}
    result = []
    while todo:
        representative = min(todo)
        orbit = {''.join(representative[p[k]] for k in range(7)) for p in perms}
        assert orbit <= todo
        todo -= orbit
        result.append((representative, sorted(orbit)))
    assert len(result) == 60 and sum(len(o) for _, o in result) == 2187
    return result


def patterns():
    result = []
    for pp in product(range(4), repeat=7):
        sx = sz = px = pz = 0
        for i, k in enumerate(pp, start=1):
            x, z = BITS[k]
            if x:
                sx ^= i
                px ^= 1
            if z:
                sz ^= i
                pz ^= 1
        result.append((pp, sx, sz, 1-2*pz, 1-2*(px ^ pz)))
    return result


PATTERNS = None


def moments(weights):
    """Integer signed mass; 4^7 errors, followed by all 64 input sectors."""
    dz = [0]*8
    dxy = [[0]*8 for _ in range(8)]
    total = 0
    for pp, sx, sz, sign_z, sign_xy in PATTERNS:
        n = prod(weights[j][k] for j, k in enumerate(pp))
        total += n
        dz[sz] += sign_z*n
        dxy[sx][sz] += sign_xy*n
    tz = sum(dz)
    rows = list(map(sum, dxy))
    cols = [sum(dxy[x][z] for x in range(8)) for z in range(8)]
    txy = sum(rows)
    out = []
    for x, z in product(range(8), repeat=2):
        vx = (-1 if z else 1)*(2*dz[z]-tz)
        vy = (-1 if bool(x) ^ bool(z) else 1)*(4*dxy[x][z]-2*rows[x]-2*cols[z]+txy)
        out.append([x, z, vx, vy])
    return total, out


def decimal_loss(norm):
    with localcontext() as ctx:
        ctx.prec = 70
        return str((1-(Decimal(norm.numerator)/Decimal(norm.denominator)).sqrt())/2)


def isotropic(q):
    den = lcm(*(r.denominator for r in dep(q)))
    weights = [int(r*den) for r in dep(q)]
    total, rows = moments([weights]*7)
    assert total == den**7
    norm = max(F(x*x+y*y, 2*total**2) for _, _, x, y in rows)
    return {'q': str(q), 'minimum_loss': decimal_loss(norm), 'max_norm_squared': str(norm)}


def main():
    global PATTERNS
    PATTERNS = patterns()
    channels, factors = local_channels()
    den = lcm(*(p.denominator for pp in channels.values() for p in pp))
    weights = {k: [int(p*den) for p in pp] for k, pp in channels.items()}
    certificate = {'p': str(P), 'q': str(Q), 'factors': factors,
                   'types': {'L': 'idle or one-qubit unitary', 'X': 'CX helper -> output',
                             'Z': 'CX output -> helper'},
                   'probability_denominator': den,
                   'probability_numerators_I_X_Y_Z': weights,
                   'moment_denominator': den**7,
                   'certified_lower_bound': str(CERTIFIED), 'cases': []}
    best = F(0)
    for representative, orbit in orbits():
        total, sectors = moments([weights[k] for k in representative])
        assert total == den**7
        norms = [F(vx*vx+vy*vy, 2*total**2) for _, _, vx, vy in sectors]
        assert all(n <= (1-2*CERTIFIED)**2 for n in norms)
        maximum = max(norms)
        row = {'representative': representative, 'orbit_size': len(orbit), 'members': orbit,
               'sectors_x_z_vx_numerator_vy_numerator': sectors,
               'max_norm_squared': str(maximum), 'minimum_loss': decimal_loss(maximum),
               'maximizing_sectors': [s[:2] for s, n in zip(sectors, norms) if n == maximum]}
        certificate['cases'].append(row)
        if maximum > best:
            best = maximum
    certificate['max_norm_squared'] = str(best)
    certificate['minimum_loss'] = decimal_loss(best)
    winners = [r for r in certificate['cases'] if F(r['max_norm_squared']) == best]
    certificate['minimizing_structures'] = [r['representative'] for r in winners]
    certificate['minimizing_assignments'] = sum(r['orbit_size'] for r in winners)
    comparisons = {'old_universal': isotropic(P-16*P*P/75),
                   'measured_partner_conservative': isotropic(P+2*P/5-4*P*(2*P/5)/3)}
    qm = (2*P/5)/(1-8*P/15)
    comparisons['measured_partner_exact_factor'] = isotropic(P+qm-4*P*qm/3)
    for name, q in comparisons.items():
        with localcontext() as ctx:
            ctx.prec = 60
            q['gap_from_strengthened'] = str(Decimal(q['minimum_loss'])-Decimal(certificate['minimum_loss']))
            q['ratio_to_strengthened'] = str(Decimal(q['minimum_loss'])/Decimal(certificate['minimum_loss']))
    certificate['comparisons'] = comparisons
    (HERE/'certificate.json').write_text(json.dumps(certificate, indent=2)+'\n')
    summary = {k: v for k, v in certificate.items() if k != 'cases'}
    summary['cases'] = len(certificate['cases'])
    summary['homogeneous_types'] = {r['representative']: r['minimum_loss'] for r in certificate['cases']
                                  if len(set(r['representative'])) == 1}
    summary['ten_best_cases'] = [{k: r[k] for k in ('representative', 'orbit_size', 'minimum_loss',
                                                  'maximizing_sectors')}
                               for r in sorted(certificate['cases'], key=lambda x: Decimal(x['minimum_loss']))[:10]]
    (HERE/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
