"""Complete rank-four 14-T circuits on the v36c suffix.

The cultivation prefix (injection, double-cat check, blue XZ check, hops, guards, echoes: 115 CX) is removed.
The data |+_L> is prepared on the A cells with v36c's own 12-CX A encoder (4 |+> seeds), the 14 T-dagger
rotations are applied in place (7 single-qubit T-dagger + 7 even-parity rotations, one per nonzero syndrome),
an optional X-check follows, then every data qubit hops A_i -> D_i (A_i and D_i are adjacent by construction of
the round) and the v36c suffix (A, B/C resource, round, readout, unchanged times) runs.

Phase identity on the code space: sum over the 14 classes (s != 0, w in {0,1}) of -[class] = [Z_L] (mod 8).
"""
import sys, json, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from qcirc import parse, save, adjacent
from decompose import is_round

HERE = Path(__file__).resolve().parent
D = [0, 20, 7, 10, 3, 22, 21]
A = [1, 14, 8, 9, 2, 16, 15]


def suffix_units():
    units, dets = parse((HERE.parent / 'MAIN' / 'v36c.qasm').read_text())
    pre = set(json.loads((HERE / 'v36c_prefix_idx.json').read_text()))
    suf = [dict(u) for i, u in enumerate(units) if i not in pre]
    pbits = {units[i]['b'] for i in pre if units[i]['b'] is not None}
    sdets = [d for d in dets if not set(d) & pbits]
    return suf, sdets


# v36c A encoder, relative to its first step (36): prepares |+_L> on A (code order) from 4 |+> seeds.
ENC = [(0, 'RX', (8,)), (0, 'R', (2,)), (1, 'RX', (14,)), (1, 'CX', (8, 2)), (2, 'RX', (9,)), (2, 'CX', (2, 1)),
       (2, 'CX', (14, 8)), (3, 'RX', (16,)), (3, 'CX', (1, 2)), (3, 'CX', (9, 8)), (4, 'MX16', (16,)), (4, 'CX', (8, 2)),
       (4, 'CX', (9, 15)), (5, 'CX', (8, 9)), (5, 'CX', (16, 15)), (6, 'CX', (9, 8)), (6, 'CX', (15, 14)),
       (7, 'CX', (14, 8))]

# In-place 14-T-dagger network on A cells (code labels l = index+1: q1:1 q14:2 q8:3 q9:4 q2:5 q16:6 q15:7).
# Even-class holders: q2 {d0,d4} s4, q9 {d2,d3} s7, q15 {d1,d6} s5, q9 {d1,d2,d3,d6} s2, q15 {d5,d6} s1,
# q8 {d2,d4} s6, q9 {d3,d6} s3.  Single T-dagger on every data qubit when it holds its own value.
NET = [(0, 'CX', (1, 2)), (0, 'CX', (8, 9)), (0, 'CX', (14, 15)), (0, 'TDG', (16,)),
       (1, 'TDG', (2,)), (1, 'TDG', (9,)), (1, 'TDG', (15,)), (1, 'CX', (1, 7)),
       (2, 'CX', (1, 2)), (2, 'CX', (8, 9)), (2, 'CX', (14, 15)),
       (3, 'CX', (8, 7)), (3, 'CX', (16, 15)),
       (4, 'TDG', (7,)), (4, 'TDG', (15,)), (4, 'TDG', (1,)), (4, 'TDG', (9,)),
       (5, 'CX', (8, 7)), (5, 'CX', (16, 15)),
       (6, 'CX', (1, 7)), (6, 'CX', (2, 8)), (6, 'CX', (15, 9)),
       (7, 'TDG', (8,)), (7, 'TDG', (9,)), (7, 'TDG', (14,)), (7, 'TDG', (2,)),
       (8, 'CX', (2, 8)), (8, 'CX', (15, 9)),
       (9, 'TDG', (8,)), (9, 'TDG', (15,))]
NET_LEN = 10


def check_network():
    """Replay the network on coordinate rows: every T-dagger's axis, and the restored rows."""
    rows = {q: 1 << i for i, q in enumerate(A)}   # data i holds e_i (bit i)
    rows[7] = 0
    def lab(v):
        syn = 0
        for i in range(7):
            if v >> i & 1: syn ^= i + 1
        return (syn, bin(v).count('1') % 2)
    axes = []
    for t in range(NET_LEN):
        for (tt, k, qs) in NET:
            if tt != t: continue
            if k == 'CX':
                rows[qs[1]] ^= rows[qs[0]]
            else:
                axes.append(rows[qs[0]])
    assert all(rows[q] == 1 << i for i, q in enumerate(A)) and rows[7] == 0, rows
    classes = sorted(tuple(lab(v)) for v in axes)
    want = sorted((s, w) for s in range(1, 8) for w in (0, 1))
    assert classes == want, classes
    return axes


def build(name, s0, xcheck=False, watches=True):
    suf, sdets = suffix_units()
    units = [u for u in suf]
    dets = list(sdets)
    bit = [300]
    def nb():
        bit[0] += 1; return bit[0] - 1
    stage = []
    for (dt, k, qs) in ENC:
        if k == 'MX16':
            b = nb(); stage.append(dict(k='MX', q=qs, t=s0 + dt, b=b)); dets.append([b])
        else:
            stage.append(dict(k=k, q=qs, t=s0 + dt, b=None))
    n0 = s0 + 8
    for (dt, k, qs) in NET:
        stage.append(dict(k=k, q=qs, t=n0 + dt, b=None))
    h0 = n0 + NET_LEN
    if xcheck:
        # DIAGNOSTIC ONLY (not grid-legal): ideal-placement X-stabilizer check right after the network, ancillas on
        # the unused cells 24, 30, 32; it is priced noiseless by region.py to bound any real X-check.
        anc = {24: (15, 1, 8, 2), 30: (14, 15, 16, 8), 32: (9, 2, 15, 16)}
        for a in anc:
            stage.append(dict(k='RX', q=(a,), t=h0, b=None))
        for layer in range(4):
            for a, qs in anc.items():
                stage.append(dict(k='CX', q=(a, qs[layer]), t=h0 + 1 + layer, b=None))
        for a in anc:
            b = nb(); stage.append(dict(k='MX', q=(a,), t=h0 + 5, b=b)); dets.append([b]); stage[-1]['xc'] = 1
        for u in stage[-18:]:
            u['xc'] = 1
        h0 = h0 + 6
    # hop A_i -> D_i: CX a->d, CX d->a (data now on D, A_i back to |0>)
    for a, d in zip(A, D):
        assert adjacent(a, d)
        stage.append(dict(k='CX', q=(a, d), t=h0, b=None))
        stage.append(dict(k='CX', q=(d, a), t=h0 + 1, b=None))
    units += stage
    # watches on vacated A cells: measure |0> where the suffix lets it, keep the record as a detector
    busy = {}
    for u in suf:
        for q in u['q']:
            busy.setdefault(q, []).append(u['t'])
    if watches:
        for a in A:
            first = min(busy[a])
            if first > h0 + 2:
                b = nb(); units.append(dict(k='M', q=(a,), t=h0 + 2, b=b)); dets.append([b])
    # sanity: no qubit has two units in one step, stage ends before the suffix uses each cell
    occ = {}
    for u in units:
        for q in u['q']:
            assert (q, u['t']) not in occ, ('clash', q, u['t'], u, occ[(q, u['t'])])
            occ[(q, u['t'])] = u
    for u in stage:
        for q in u['q']:
            if q in busy:
                assert u['t'] < min(busy[q]), ('stage after suffix start', q, u)
    meta = dict(source='T14 build_t14.py', family='rank-4 14-T (f14 all-TDG)', stage_start=s0,
                network_start=n0, hop=h0, xcheck=xcheck, R=44)
    roles = []
    for u in units:
        if u in stage or (u['k'] == 'M' and u['b'] is not None and u['b'] >= 300):
            r = 'enc' if u['t'] < n0 else 'net' if u['t'] < n0 + NET_LEN else 'hop'
            if u.get('xc'):
                r = 'xcheck'
            if u['k'] == 'TDG':
                r = 'tdg'
            roles.append(dict(t=u['t'], q=list(u['q']), k=u['k'], role=r))
    (HERE / (name + '.stage.json')).write_text(json.dumps(roles))
    for u in units:
        u.pop('xc', None)
    return save(HERE / name, units, dets, D, meta, nbits=bit[0])


if __name__ == '__main__':
    check_network()
    p = argparse.ArgumentParser(); p.add_argument('name'); p.add_argument('--s0', type=int, default=15)
    p.add_argument('--no-watch', action='store_true'); p.add_argument('--xcheck', action='store_true')
    a = p.parse_args()
    print(build(a.name, a.s0, xcheck=a.xcheck, watches=not a.no_watch))
