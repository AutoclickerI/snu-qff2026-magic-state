"""Resource-level exact Pauli propagation for the B/C side of a spliced circuit.

Faults on B/C cells (and readout helpers) from their prep init to their readout, each propagated through
the B/C units; signature = (flipped B/C detectors, X pattern delivered to the data by B->D).
Reports: c1 (undetected dangerous singles), leak (undetected weight-1 data X), X2 (second-order
pairs with equal signature and dangerous combined data X, cost 1/2), RZ (rate of faults whose only
effect is a B-syndrome flip: masks waiting-data Z pairs at third order), acc1 (first-order rejection).
"""
import sys, json
from collections import defaultdict
from qcirc import parse
B = [6, 26, 13, 11, 4, 23, 27]
C = [12, 25, 19, 17, 5, 29, 28]
D = [0, 20, 7, 10, 3, 22, 21]
ROWS = [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6]]
BC = set(B + C)
P = 1e-3
P2 = [a + b for a in 'IXYZ' for b in 'IXYZ'][1:]


def sig(e):
    return sum((sum(i in e for i in row) % 2) << j for j, row in enumerate(ROWS)) | ((len(e) % 2) << 3)


def dangerous(s):
    return bool(s & 8) == (not bool(s & 7))


def analyse(units, dets, prep_t0=29, flags=(), starts=None):
    """starts: {qubit: tick of its resource init}; default from splice.extract (earliest prep init per cell).
    A cell without an init op (reuse of a known state) starts at its last measurement before the resource."""
    LIVE = BC | set(flags)
    if starts is None:
        import splice
        spec = splice.extract(units)
        starts = {}
        for q, (k, t) in spec['inits'].items():
            starts[int(q)] = t
        for t, k, q in spec['extra']:
            starts[q] = min(starts.get(q, 99), t)
    life = {}
    for q in LIVE:
        cand = [i for i, u in enumerate(units) if u['q'] == (q,) and u['k'] in ('R', 'RX', 'M', 'MX') and u['t'] <= starts.get(q, -1)]
        if q in starts and cand:
            life[q] = max(cand, key=lambda i: units[i]['t'])
        elif q not in starts:
            # reused state: last measurement before the cell's first resource CX
            fc = min([u['t'] for u in units if u['k'] == 'CX' and q in u['q'] and all(x in LIVE for x in u['q']) and 33 <= u['t'] < 44] or [99])
            cand = [i for i, u in enumerate(units) if u['q'] == (q,) and u['k'] in ('M', 'MX') and u['t'] < fc]
            if cand:
                life[q] = max(cand, key=lambda i: units[i]['t'])
    start = {q: units[i]['t'] for q, i in life.items()}
    helpers = set()
    for u in units:
        if u['k'] == 'CX' and u['t'] >= 44 and any(q in BC for q in u['q']):
            for q in u['q']:
                if q not in BC and q not in D:
                    helpers.add(q)
    t_min = min(start.values())
    sel = []
    for i, u in enumerate(units):
        if u['t'] < t_min:
            continue
        qs = u['q']
        ok = False
        for q in qs:
            if q in LIVE and u['t'] >= start[q]:
                ok = True
            if q in helpers and u['t'] >= 44:
                ok = True
        if ok and all((q not in LIVE) or u['t'] >= start[q] for q in qs):
            sel.append(i)
    sel.sort(key=lambda i: (units[i]['t'], i))
    U = [units[i] for i in sel]
    bit_det = defaultdict(list)
    for j, d in enumerate(dets):
        for b in d:
            bit_det[b].append(j)
    # end of life per qubit: its last measurement in window
    endt = {}
    busy = defaultdict(set)
    for u in U:
        for q in u['q']:
            busy[q].add(u['t'])
            if u['k'] in ('M', 'MX'):
                endt[q] = u['t']
    tracked = set(BC) | helpers | set(flags)

    # explicit simple propagator (records as a set)
    def run(t_after, x, z):
        x, z = set(x), set(z)
        recs = set()
        data = set()
        for u in U:
            if u['t'] <= t_after:
                continue
            k, qs = u['k'], u['q']
            if k == 'CX':
                a, b = qs
                if a in x:
                    if b in D:
                        data ^= {D.index(b)}
                    else:
                        x ^= {b}
                if b in z and a not in D:
                    z ^= {a}
            elif k in ('M', 'MX'):
                q = qs[0]
                hit = (q in x) if k == 'M' else (q in z)
                if hit:
                    recs ^= {u['b']}
                # the measured state keeps the error of the measured basis; the other one is irrelevant
                if k == 'M':
                    z.discard(q)
                else:
                    x.discard(q)
            elif k in ('R', 'RX'):
                x.discard(qs[0]); z.discard(qs[0])
        dflip = set()
        for b in recs:
            for j in bit_det.get(b, []):
                dflip ^= {j}
        # data X delivered only through B->D
        return frozenset(dflip), frozenset(data)

    faults = []
    for u in U:
        k, qs, t = u['k'], u['q'], u['t']
        q0 = qs[0]
        if k in ('R', 'RX', 'M', 'MX') and q0 in LIVE and t == start.get(q0):
            if k == 'R':
                faults.append((P, ('init', t, qs, 'X'), run(t, [q0], [])))
            elif k == 'RX':
                faults.append((P, ('init', t, qs, 'Z'), run(t, [], [q0])))
            else:
                for pa in 'XYZ':
                    faults.append((P / 3, ('init', t, qs, pa), run(t, [q0] if pa in 'XY' else [], [q0] if pa in 'YZ' else [])))
        elif k == 'CX':
            if not all(q in tracked for q in qs if q not in D):
                continue
            for pa in P2:
                x = [q for q, c in zip(qs, pa) if c in 'XY' and q not in D]
                z = [q for q, c in zip(qs, pa) if c in 'ZY' and q not in D]
                if qs[1] in D:
                    # B->D: X on the data side lands directly on data
                    dx = pa[1] in 'XY'
                    sigd = run(t, x, z)
                    data = set(sigd[1]) ^ ({D.index(qs[1])} if dx else set())
                    faults.append((P / 15, ('cx', t, qs, pa), (sigd[0], frozenset(data))))
                    continue
                faults.append((P / 15, ('cx', t, qs, pa), run(t, x, z)))
        elif k in ('M', 'MX') and (q0 in tracked) and (t >= 44 or t > start.get(q0, 99)):
            faults.append((P, ('meas', t, qs, 'flip'), (frozenset(bit_det.get(u['b'], [])), frozenset())))
    # idles: tracked qubit between start and end, ticks without an op
    for q in tracked:
        s = start.get(q, min(u['t'] for u in U if q in u['q']))
        e = endt.get(q, 46)
        for t in range(s + 1, e):
            if t not in busy[q]:
                for pa in 'XYZ':
                    faults.append((P / 3, ('idle', t, (q,), pa), run(t, [q] if pa in 'XY' else [], [q] if pa in 'YZ' else [])))
    # summaries
    c1 = leak = RZ = acc1 = 0.0
    bdet = set()
    for j, d in enumerate(dets):
        bset = {u['b'] for u in U if u['k'] == 'MX' and u['q'][0] in B and u['t'] >= 45}
        if set(d) & bset:
            bdet.add(j)
    groups = defaultdict(list)
    for p, tag, (df, data) in faults:
        s = sig(data)
        if not df:
            if dangerous(s):
                c1 += p
            elif s:
                leak += p
        else:
            acc1 += p
            if df <= bdet and not s:
                RZ += p
        groups[df].append((p, s, tag))
    X2 = X2leak = 0.0
    for df, fs in groups.items():
        # aggregate by sig
        agg = defaultdict(float)
        for p, s, tag in fs:
            agg[s] += p
        items = list(agg.items())
        for a in range(len(items)):
            for b in range(a + 1, len(items)):
                if dangerous(items[a][0] ^ items[b][0]):
                    if df:
                        X2 += 0.5 * items[a][1] * items[b][1]
                    else:
                        X2leak += 0.5 * items[a][1] * items[b][1]
    return dict(c1=c1, leak=leak, X2=X2, X2leak=X2leak, RZ=RZ, acc1=acc1, nf=len(faults)), faults, groups


def pair_detail(groups, top=20):
    rows = []
    for df, fs in groups.items():
        for a in range(len(fs)):
            for b in range(a + 1, len(fs)):
                if dangerous(fs[a][1] ^ fs[b][1]):
                    rows.append((0.5 * fs[a][0] * fs[b][0], fs[a][2], fs[b][2]))
    rows.sort(key=lambda r: -r[0])
    return rows[:top]


if __name__ == '__main__':
    units, dets = parse(open(sys.argv[1] + '.qasm').read())
    s, faults, groups = analyse(units, dets)
    print(json.dumps(s))
    for r in pair_detail(groups, 30):
        print(f'{r[0]:.3e}', r[1], r[2])
