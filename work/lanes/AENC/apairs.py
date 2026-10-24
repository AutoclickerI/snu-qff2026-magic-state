"""A-region idle pairs: CX(a->b) at t and t+1 (identity) between an idle A cell and an idle neighbour, on a base stem.

usage: apairs.py <base stem> <out tag> <procs>   (prices every single pair, then greedy combinations)
"""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/T14')
import qcirc, allorders

A = [1, 14, 8, 9, 2, 16, 15]


def busy_map(units):
    b = set()
    for u in units:
        for q in u['q']:
            b.add((q, u['t']))
    return b


def add_pairs(base, pairs, stem):
    units, dets = qcirc.parse(Path(base).with_suffix('.qasm').read_text())
    data = json.loads(Path(base).with_suffix('.json').read_text())['data_qubits']
    busy = busy_map(units)
    nb = max(u['b'] for u in units if u['b'] is not None) + 1
    for c, g, t in pairs:
        for tt in (t, t + 1):
            assert (c, tt) not in busy and (g, tt) not in busy, ('busy', c, g, tt)
            busy.add((c, tt)); busy.add((g, tt))
            units.append(dict(k='CX', q=(c, g), t=tt, b=None))
    units.sort(key=lambda u: u['t'])
    qcirc.save(stem, units, dets, data, meta=dict(source=f'{base} + A idle pairs', pairs=pairs, R=44), nbits=nb)
    return stem


def idle_window(units, q, lo, hi):
    """ticks in [lo, hi] where q has no op but is live (has ops before and after)."""
    ts = sorted(u['t'] for u in units if q in u['q'])
    return [t for t in range(lo, hi + 1) if t not in ts and ts and ts[0] < t < ts[-1]]


def candidates(base):
    units, _ = qcirc.parse(Path(base).with_suffix('.qasm').read_text())
    nbr = lambda q: [p for p in (q - 6, q + 6, q - 1 if q % 6 else -1, q + 1 if q % 6 != 5 else -1) if 0 <= p < 36]
    out = []
    for a in A:
        ia = set(idle_window(units, a, 36, 43))
        for b in nbr(a):
            ib = set(idle_window(units, b, 36, 43))
            for t in range(36, 43):
                if {t, t + 1} <= ia and {t, t + 1} <= ib:
                    for p in ((b, a, t), (a, b, t)):
                        if p not in out: out.append(p)
    return out


if __name__ == '__main__':
    base, tag, procs = sys.argv[1], sys.argv[2], int(sys.argv[3])
    (HERE / 'pairs').mkdir(exist_ok=True)
    b0 = allorders.run(base, procs)
    print(json.dumps(dict(base=b0)), flush=True)
    res = []
    for i, p in enumerate(candidates(base)):
        stem = add_pairs(base, [p], HERE / 'pairs' / f'{tag}_{i}')
        r = allorders.run(stem, procs)
        r.update(pairs=[p], dloss=r['loss'] - b0['loss'], dacc=r['acceptance'] - b0['acceptance'])
        res.append(r)
        print(json.dumps(r), flush=True)
    good = sorted([r for r in res if r['dloss'] < 0], key=lambda r: r['dloss'])
    # greedy combination of disjoint improving pairs
    chosen, best = [], b0
    for r in good:
        p = r['pairs'][0]
        if any({p[0], p[1]} & {q[0], q[1]} and abs(p[2] - q[2]) < 2 for q in chosen):
            continue
        trial = chosen + [p]
        try:
            stem = add_pairs(base, trial, HERE / 'pairs' / f'{tag}_combo{len(trial)}')
        except AssertionError:
            continue
        rr = allorders.run(stem, procs)
        print(json.dumps(dict(combo=trial, loss=rr['loss'], acceptance=rr['acceptance'])), flush=True)
        if rr['loss'] < best['loss'] and rr['acceptance'] >= 0.5002:
            chosen, best = trial, rr
    print(json.dumps(dict(final=chosen, loss=best['loss'], acceptance=best['acceptance'])), flush=True)
