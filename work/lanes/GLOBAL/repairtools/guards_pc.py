"""Multi-tick guard menu on a base stem (INTEG plan machinery, output in PRECELL/c).

Guard: helper h free (dead/pre/prem) on [a-1, b+1]; R h at a-1, CX h->q at every tick in [a, b] where q is idle
(live, no op), M h at b+1 as a singleton detector. h is a |0> control, so the guard never acts noiselessly; a helper X
fault spreads X onto q and persists to the M (detected); Z faults on h are inert. Each guarded tick leaves q an
undetected D1(2p/5) instead of D1(p).
usage: guards.py <base stem> <prefix>   -> c/<prefix>__g<h>_<q>_<a>_<b> (+ multi-target g<h>_m_<a>_<b>), list in c/<prefix>.list
"""
import sys, json, copy

from gadgets import *  # read, status, add_ops, normalized, bit, ADJ, D

P = C
FREE = ('dead', 'pre', 'prem')


def windows(st, h):
    """maximal runs of free ticks of h"""
    out, cur = [], None
    for t, s in enumerate(st[h]):
        if s in FREE:
            cur = [t, t] if cur is None else [cur[0], t]
        else:
            if cur:
                out.append(tuple(cur))
            cur = None
    if cur:
        out.append(tuple(cur))
    return out


def menu(c):
    st = status(c)
    T = len(st[0])
    gs = []
    for h in range(36):
        for lo, hi in windows(st, h):
            # CX ticks must lie in [lo+1, hi-1] (R at >= lo, M at <= hi); the circuit's last tick is excluded
            nb = [q for q in ADJ[h] if any(st[q][t] == 'live' for t in range(lo + 1, min(hi, T - 1)))]
            per = {}
            for q in nb:
                ts = [t for t in range(lo + 1, min(hi, T - 1)) if st[q][t] == 'live']
                if ts:
                    per[q] = ts
                    gs.append(dict(h=h, seq=[(t, q) for t in ts]))
                    runs = [[ts[0]]]
                    for t in ts[1:]:
                        if t == runs[-1][-1] + 1:
                            runs[-1].append(t)
                        else:
                            runs.append([t])
                    if len(runs) > 1:
                        for r in runs:
                            gs.append(dict(h=h, seq=[(t, q) for t in r]))
            if len(per) > 1:
                # multi-target: each tick to a data qubit if one is idle, else to the first idle neighbour
                ticks = sorted({t for ts in per.values() for t in ts})
                seq = []
                for t in ticks:
                    qs = [q for q in per if t in per[q]]
                    qs.sort(key=lambda q: (q not in D, q))
                    seq.append((t, qs[0]))
                gs.append(dict(h=h, seq=seq))
    return gs


def apply(c, g):
    h, seq = g['h'], g['seq']
    a, b = seq[0][0], seq[-1][0]
    m = bit(c)
    items = [(a - 1, [f'reset q[{h}];'])] + [(t, [f'cx q[{h}],q[{q}];']) for t, q in seq] + \
            [(b + 1, [f'measure q[{h}] -> c[{m}];'])]
    c = add_ops(c, items)
    c['tail'].append(f'// DETECTOR c[{m}]')
    return c


def gname(g):
    qs = sorted({q for _, q in g['seq']})
    tag = str(qs[0]) if len(qs) == 1 else 'm'
    return f"g{g['h']}_{tag}_{g['seq'][0][0]}_{g['seq'][-1][0]}"


def save_plan(c, name, meta):
    c, txt = normalized(c)
    (P / (name + '.qasm')).write_text(txt)
    m = dict(c['meta']); m.update(meta)
    for k in ('allorders', 'allorders_acceptance', 'all_orders_loss', 'all_orders_acceptance', 'judge_1e6', 'speed',
              'official_1e8_seed0_hippo'):
        m.pop(k, None)
    (P / (name + '.json')).write_text(json.dumps(m, indent=1))
    (P / (name + '.plan.json')).write_text(json.dumps(c))


if __name__ == '__main__':
    base, prefix = sys.argv[1], sys.argv[2]
    c = read(base)
    names = []
    for g in menu(c):
        n = f'{prefix}__{gname(g)}'
        if n in names:
            continue
        try:
            save_plan(apply(c, g), n, dict(guard=g))
            names.append(n)
        except Exception as e:
            print(n, repr(e)[:160])
    (P / (prefix + '.list')).write_text(' '.join(names))
    print(len(names))
