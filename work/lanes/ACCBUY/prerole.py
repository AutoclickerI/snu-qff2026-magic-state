"""Pre-role guard menu: helpers sitting in |0> (after R, before first op that is not 'CX h->x') or |+> (after RX, before
first op that is not 'CX x->h') couple to an adjacent idle live qubit on an idle tick of the helper. Dead ticks before
an R/RX can be used by moving the R/RX earlier. Each candidate = one added CX (+ moved init).
usage: prerole.py <stem> <prefix>  -> c/<prefix>__<h>_<q>_<t>[_r<t0>] + c/<prefix>.list"""
import sys, json
from elements import *
stem, prefix = sys.argv[1], sys.argv[2]
base = read(stem)
st = status(base)
T = depth(base)
def windows(c, h):
    s = seq(c, h)
    out = []
    for i, o in enumerate(s):
        u = unit(o)
        if u.name not in ('RESET', 'RX'):
            continue
        kind = 'Z' if u.name == 'RESET' else 'X'
        # earliest dead tick before the init
        t0 = o['t']
        while t0 - 1 >= 0 and st[h][t0 - 1] in ('dead', 'pre') and not any(p['t'] == t0 - 1 for p in s):
            t0 -= 1
        # end: first op after init that is not a no-op coupling
        end = T
        for p in s[i + 1:]:
            v = unit(p)
            if v.name == 'CX':
                a, b = cx_qs(p)
                if (kind == 'Z' and a == h) or (kind == 'X' and b == h):
                    continue
            end = p['t']; break
        out.append(dict(kind=kind, init=o['t'], t0=t0, end=end, lines=o['lines']))
    return out
cands = []
for h in range(36):
    for w in windows(base, h):
        for t in range(w['t0'] + 1, w['end']):
            if any(p['t'] == t for p in seq(base, h)) and t > w['init']:
                continue  # helper busy at t (existing no-op coupling)
            if t <= w['init'] and t < w['t0'] + 1:
                continue
            for q in ADJ[h]:
                if st[q][t] != 'live':
                    continue
                cands.append(dict(h=h, q=q, t=t, w=w))
names = []
for cd in cands:
    h, q, t, w = cd['h'], cd['q'], cd['t'], cd['w']
    c = copy.deepcopy(base)
    rt = None
    if t <= w['init']:
        o = next(o for o in c['ops'] if o['t'] == w['init'] and o['lines'] == w['lines'])
        o['t'] = t - 1; rt = t - 1
    line = f'cx q[{h}],q[{q}];' if w['kind'] == 'Z' else f'cx q[{q}],q[{h}];'
    c = add_ops(c, [(t, [line])])
    n = f'{prefix}__{h}_{q}_{t}' + (f'_r{rt}' if rt is not None else '')
    try:
        save(c, n, desc=dict(prerole=dict(h=h, q=q, t=t, kind=w['kind'], rt=rt)))
        names.append(n)
    except Exception as e:
        print('skip', n, repr(e)[:100])
(C / (prefix + '.list')).write_text(' '.join(names))
print(len(names), 'candidates')
