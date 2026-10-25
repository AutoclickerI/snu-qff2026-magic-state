"""Compose gadgets onto a base plan with validity re-checked against the composed plan."""
from gadgets import *


def valid(c, g, st=None):
    st = st or status(c)
    if g['kind'] in ('pair', 'pairR'):
        a, b, t = g['a'], g['b'], g['t']
        for q in (a, b):
            s = st[q][t:t + 2]
            if 'busy' in s or 'pre' in s or len(set(s)) > 1:
                return False
        return 'live' in st[a][t:t + 2] + st[b][t:t + 2]
    if g['kind'] == 'echo':
        q, h, t1, t2 = g['q'], g['h'], g['t1'], g['t2']
        if any(st[h][t] not in ('dead', 'pre', 'prem') for t in range(t1 - 1, t2 + 2)):
            return False
        nxt = [o for o in seq(c, h) if o['t'] > t2 + 1]
        if nxt and unit(nxt[0]).name not in ('RESET', 'RX', 'MX') and nxt[0]['t'] - 1 <= t2 + 1:
            return False
        if st[q][t1] != 'live' or st[q][t2] != 'live':
            return False
        for t in range(t1 + 1, t2):
            if st[q][t] in ('dead', 'pre'):
                return False
            if st[q][t] == 'busy' and not commutes(c, q, t, g['axis']):
                return False
        return True
    if g['kind'] == 'move':
        return True
    if g['kind'] == 'pguard':
        return st[16][38] == 'dead' and st[g['d']][39] == 'live' and any(o['t'] == 39 and unit(o).name == 'RX' for o in seq(c, 16))
    raise ValueError(g)


def apply(c, g):
    if g['kind'] == 'pair':
        return add_pair(c, g)
    if g['kind'] == 'pairR':
        return add_pair(c, g, orient=1)
    if g['kind'] == 'echo':
        h = g['h']
        c = echo(c, g['q'], h, g['axis'], g['t1'] - 1, g['t1'], g['t2'], g['t2'] + 1)
        nxt = [o for o in seq(c, h) if o['t'] > g['t2'] + 1]
        if nxt and unit(nxt[0]).name not in ('RESET', 'RX', 'MX'):
            assert nxt[0]['t'] - 1 > g['t2'] + 1, g
            c = add_ops(c, [(nxt[0]['t'] - 1, [f'reset q[{h}];'])])
        return c
    if g['kind'] == 'pguard':
        c = copy.deepcopy(c)
        o = next(o for o in c['ops'] if o['t'] == 39 and 16 in unit(o).qs and unit(o).name == 'RX')
        o['t'] = 38
        return add_ops(c, [(39, [f"cx q[{g['d']}],q[16];"])])
    if g['kind'] == 'move':
        c = copy.deepcopy(c)
        o = next(o for o in c['ops'] if o['t'] == g['t0'] and g['q'] in unit(o).qs)
        o['t'] = g['t1']
        return fix(c)
    raise ValueError(g)


def compose(c, gs):
    used = []
    for g in gs:
        if valid(c, g):
            c2 = apply(c, g)
            try:
                normalized(c2)
            except Exception:
                continue
            c = c2
            used.append(g)
    return c, used
