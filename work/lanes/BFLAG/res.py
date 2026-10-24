"""B/C resource of a layered circuit: X-span evolution and single-fault (e_B, literal diff) table."""
import sys, json
from collections import defaultdict
from qcirc import parse
B = [6, 26, 13, 11, 4, 23, 27]
C = [12, 25, 19, 17, 5, 29, 28]
ROWS = [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6]]
BC = set(B + C)
def sig(e):  # 4-bit sig of a B-index set
    return sum((sum(i in e for i in row) % 2) << j for j, row in enumerate(ROWS)) | ((len(e) % 2) << 3)
def dangerous(s):
    return bool(s & 8) == (not bool(s & 7))
def resource(units, t0=32, tchk=44):
    """prep units: inits on BC cells at t>=t0 (last init before tchk) and CX among BC with t<tchk."""
    init = {}
    for i, u in enumerate(units):
        if u['t'] < tchk and len(u['q']) == 1 and u['q'][0] in BC and u['k'] in ('R', 'RX', 'M', 'MX') and u['t'] >= t0:
            init[u['q'][0]] = i
    cx = [u for u in units if u['k'] == 'CX' and set(u['q']) <= BC and u['t'] < tchk and all(u['t'] > units[init[q]]['t'] for q in u['q'])]
    return init, sorted(cx, key=lambda u: u['t'])
def propagate(cx, t, qs):
    """X on qubits qs right after tick t (faults of ops at tick t), pushed through CX at ticks > t."""
    e = set(qs)
    for u in cx:
        if u['t'] > t and u['q'][0] in e:
            e ^= {u['q'][1]}
    return e
def table(units, p=1e-3, tchk=44):
    init, cx = resource(units, tchk=tchk)
    busy = defaultdict(set)
    for i in init.values():
        busy[units[i]['q'][0]].add(units[i]['t'])
    for u in cx:
        for q in u['q']:
            busy[q].add(u['t'])
    faults = []  # (prob, tag, e)
    for q, i in init.items():
        u = units[i]
        if u['k'] in ('R',):
            faults.append((p, f'init R q{q}@{u["t"]}', propagate(cx, u['t'], [q])))
        elif u['k'] == 'M':
            faults.append((2 * p / 3, f'init M q{q}@{u["t"]}', propagate(cx, u['t'], [q])))
        # RX/MX: X error on |+> harmless
        # idle ticks from init to tchk-1
        for t in range(u['t'] + 1, tchk):
            if t not in busy[q]:
                faults.append((2 * p / 3, f'idle q{q}@{t}', propagate(cx, t, [q])))
    for u in cx:
        a, b = u['q']
        for qs in ([a], [b], [a, b]):
            faults.append((4 * p / 15, f'cx{a}-{b}@{u["t"]} X{qs}', propagate(cx, u['t'], qs)))
    out = []
    for pr, tag, e in faults:
        eb = {i for i, q in enumerate(B) if q in e}
        ec = {i for i, q in enumerate(C) if q in e}
        diff = eb ^ ec
        out.append(dict(p=pr, tag=tag, eb=eb, diff=frozenset(diff), dang=dangerous(sig(eb)), s=sig(eb)))
    return out, init, cx
if __name__ == '__main__':
    units, dets = parse(open(sys.argv[1] + '.qasm').read())
    out, init, cx = table(units)
    print('inits', {q: (units[i]['k'], units[i]['t']) for q, i in init.items()}, 'cx', len(cx))
    # span evolution
    vec = {q: 0 for q in BC}
    piv = [q for q, i in init.items() if units[i]['k'] in ('RX', 'MX')]
    for j, q in enumerate(piv):
        vec[q] = 1 << j
    for u in cx:
        vec[u['q'][1]] ^= vec[u['q'][0]]
    print('pivots', piv, 'B', [vec[q] for q in B], 'C', [vec[q] for q in C])
    bad1 = [f for f in out if f['dang'] and len(f['diff']) == 0]
    print('first-order undetected dangerous', len(bad1))
    rob = [f for f in out if f['dang'] and len(f['diff']) == 1]
    print('robust violations (dangerous, |diff|=1):')
    for f in sorted(rob, key=lambda f: -f['p']):
        print(f"  {f['p']:.2e} {f['tag']} eb={sorted(f['eb'])} diff={sorted(f['diff'])}")
    # internal pair collisions
    by = defaultdict(list)
    for f in out:
        if f['diff']:
            by[f['diff']].append(f)
    tot = 0; rows = []
    for dkey, fs in by.items():
        for i in range(len(fs)):
            for j in range(i + 1, len(fs)):
                if dangerous(sig(fs[i]['eb'] ^ fs[j]['eb'])):
                    v = fs[i]['p'] * fs[j]['p'] * 0.5
                    tot += v; rows.append((v, fs[i]['tag'], fs[j]['tag'], sorted(dkey)))
    print('internal colliding pairs total (X-part, 1/2 cost)', tot, len(rows))
    for r in sorted(rows, reverse=True)[:25]:
        print(f'  {r[0]:.2e} {r[1]} + {r[2]} diff={r[3]}')
    rw = defaultdict(float)
    for f in rob:
        rw[min(f['diff'])] += f['p']
    print('robust-violation prob by C index:', dict(rw))
