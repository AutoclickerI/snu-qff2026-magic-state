"""Pre-/post-role guard slots on a base plan.
Slot = helper h in a known product state at tick t (no op on h at t), coupling with no noiseless effect:
  Z-kind (|0>): CX h->q ; X-kind (|+>): CX q->h ; q adjacent, live and idle at t.
Windows: (a) after R/RX init until the first op that is not a no-op coupling; (b) dead ticks before an R/RX (init moved
earlier to t-1, only if no op on h in between); (c) after a deterministic singleton-detector M/MX until the next op
that is R/RX (the qubit is reused, so ticks between are charged).
usage: prerole2.py <base stem> <prefix>"""
import sys, json
from elements import *
stem, prefix = sys.argv[1], sys.argv[2]
base = read(stem)
st = status(base)
T = depth(base)
S1 = singles(base)
def slots(c, h):
    s = seq(c, h)
    out = []
    busy = {o['t'] for o in s}
    for i, o in enumerate(s):
        u = unit(o)
        if u.name in ('RESET', 'RX'):
            kind = 'Z' if u.name == 'RESET' else 'X'
            end = T
            for p in s[i + 1:]:
                v = unit(p)
                if v.name == 'CX':
                    a, b = cx_qs(p)
                    if (kind == 'Z' and a == h) or (kind == 'X' and b == h):
                        continue
                end = p['t']; break
            for t in range(o['t'] + 1, end):
                if t not in busy:
                    out.append(dict(t=t, kind=kind, move=None))
            # dead before
            prev = s[i - 1]['t'] if i > 0 else -1
            for t in range(prev + 2, o['t'] + 1):
                if all(st[h][x] in ('dead', 'pre') for x in range(t - 1, o['t'])):
                    out.append(dict(t=t, kind=kind, move=(o['t'], t - 1, o['lines'])))
        if u.name in ('MEASURE', 'MX') and bits_of(o) and bits_of(o)[0] in S1 and i + 1 < len(s):
            nx = s[i + 1]
            if unit(nx).name in ('RESET', 'RX'):
                kind = 'Z' if u.name == 'MEASURE' else 'X'
                for t in range(o['t'] + 1, nx['t']):
                    out.append(dict(t=t, kind=kind, move=None, post=True))
    return out
names = []
for h in range(36):
    for sl in slots(base, h):
        t = sl['t']
        for q in ADJ[h]:
            if t >= T - 1 or st[q][t] != 'live':
                continue
            c = copy.deepcopy(base)
            if sl['move']:
                t_old, t_new, lines = sl['move']
                o = next(o for o in c['ops'] if o['t'] == t_old and o['lines'] == lines)
                o['t'] = t_new
            line = f'cx q[{h}],q[{q}];' if sl['kind'] == 'Z' else f'cx q[{q}],q[{h}];'
            c = add_ops(c, [(t, [line])])
            n = f"{prefix}__{h}_{q}_{t}" + (f"_m{sl['move'][1]}" if sl['move'] else '') + ('_p' if sl.get('post') else '')
            if n in names:
                continue
            try:
                save(c, n, desc=dict(slot=dict(h=h, q=q, t=t, kind=sl['kind'], move=sl['move'], post=sl.get('post', False))))
                names.append(n)
            except Exception as e:
                pass
(C / (prefix + '.list')).write_text(' '.join(names))
print(len(names), 'candidates')
