"""Enumerate protection gadgets on a plan: CX pairs on idle neighbours and echoed parity checks."""
from lib import *

ADJ = {q: [p for p in range(36) if abs(p // 6 - q // 6) + abs(p % 6 - q % 6) == 1] for q in range(36)}


def cx_qs(o):
    return [int(x) for x in re.findall(r'q\[(\d+)\]', o['lines'][0])]


def status(c):
    """st[q][t] in busy/live/dead/pre for t in 0..depth-1."""
    T = depth(c)
    st = {}
    for q in range(36):
        s = seq(c, q)
        row = []
        for t in range(T):
            if any(o['t'] == t for o in s):
                row.append('busy'); continue
            prev = [o for o in s if o['t'] < t]
            nxt = [o for o in s if o['t'] > t]
            pn = unit(prev[-1]).name if prev else None
            nn = unit(nxt[0]).name if nxt else None
            if nn in ('RESET', 'RX'):
                row.append('dead')
            elif not prev and not nxt:
                row.append('dead')
            elif not nxt:
                row.append('dead' if pn in ('MEASURE', 'MX') else 'live')
            elif not prev:
                row.append({'MX': 'dead', 'MEASURE': 'prem'}.get(nn, 'pre'))
            else:
                row.append('live')
        st[q] = row
    return st


def ops_at(c, q, t):
    return [o for o in c['ops'] if o['t'] == t and q in unit(o).qs]


def commutes(c, q, t, axis):
    """Ops on q at tick t keep the q parity of `axis` (Z: control/diag, X: target)."""
    for o in ops_at(c, q, t):
        u = unit(o)
        if u.name == 'CX':
            a, b = cx_qs(o)
            if axis == 'Z' and a != q:
                return False
            if axis == 'X' and b != q:
                return False
        elif u.name in ('T', 'TDG'):
            if axis != 'Z':
                return False
        else:
            return False
    return True


def pairs(c, st=None, need=('live',), other=('live', 'dead', 'prem')):
    st = st or status(c)
    T = depth(c)
    out = []
    for a in range(36):
        for b in ADJ[a]:
            if b < a:
                continue
            for t in range(T - 1):
                sa, sb = st[a][t:t + 2], st[b][t:t + 2]
                if 'busy' in sa or 'busy' in sb or 'pre' in sa or 'pre' in sb or len(set(sa)) > 1 or len(set(sb)) > 1:
                    continue
                if not (set(sa) <= set(need) | set(other) and set(sb) <= set(need) | set(other)):
                    continue
                if not (set(sa) & set(need) or set(sb) & set(need)):
                    continue
                out.append(dict(kind='pair', a=a, b=b, t=t, sa=sa, sb=sb))
    return out


def add_pair(c, g, orient=0):
    a, b = (g['a'], g['b']) if orient == 0 else (g['b'], g['a'])
    return add_ops(c, [(g['t'], [f'cx q[{a}],q[{b}];']), (g['t'] + 1, [f'cx q[{a}],q[{b}];'])])


def first_use(c, q):
    s = seq(c, q)
    return s[0]['t'] if s else None


def echoes(c, st=None, protect=None, minlen=1, fresh=True):
    """Echo with helper h: h dead on [t1-1, t2+1] (or pre-use, then a reset is added at its first use - 1),
    q free at t1, t2, commuting ops between."""
    st = st or status(c)
    T = depth(c)
    out = []
    ok = ('dead', 'pre', 'prem') if fresh else ('dead',)
    for q in (protect if protect is not None else range(36)):
        for h in ADJ[q]:
            fu = first_use(c, h)
            for axis in ('Z', 'X'):
                for t1 in range(1, T - 2):
                    if st[q][t1] != 'live' or st[h][t1 - 1] not in ok or st[h][t1] not in ok:
                        continue
                    for t2 in range(t1 + 1 + minlen, T - 1):
                        if st[h][t2] not in ok or st[h][t2 + 1] not in ok:
                            break
                        if not commutes(c, q, t2 - 1, axis):
                            break
                        if any(st[q][t] in ('dead', 'pre', 'prem') for t in range(t1, t2 + 1)):
                            break
                        if st[q][t2] != 'live':
                            continue
                        pre = st[h][t2 + 1] in ('pre', 'prem')
                        if pre and not (fu is not None and fu - 1 > t2 + 1):
                            continue
                        out.append(dict(kind='echo', q=q, h=h, axis=axis, t1=t1, t2=t2, rst=(fu - 1) if pre else None))
    return out


def add_echo(c, g):
    c = echo(c, g['q'], g['h'], g['axis'], g['t1'] - 1, g['t1'], g['t2'], g['t2'] + 1)
    if g.get('rst') is not None:
        c = add_ops(c, [(g['rst'], [f"reset q[{g['h']}];"])])
    return c


def gname(g):
    if g['kind'] == 'pguard':
        return f"pguard16_{g['d']}"
    if g['kind'] == 'pairR':
        return f"pairR_{g['a']}_{g['b']}_{g['t']}"
    if g['kind'] == 'pair':
        return f"pair_{g['a']}_{g['b']}_{g['t']}"
    return f"echo{g['axis']}_{g['q']}_h{g['h']}_{g['t1']}_{g['t2']}"


if __name__ == '__main__':
    c = read(C / sys.argv[1])
    st = status(c)
    for q in range(36):
        print(f'q{q:2d}', ''.join({'busy': '#', 'live': '.', 'dead': ' ', 'pre': '-', 'prem': 'm'}[x] for x in st[q]))
    ps = pairs(c, st)
    print(len(ps), 'pairs')
    es = echoes(c, st)
    print(len(es), 'echoes')
