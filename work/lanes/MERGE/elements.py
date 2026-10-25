"""Removable elements of a plan (v36f family): cancelling CX pairs, helper check sessions (echoes, guards, extensions),
q6's unread guard, and acceptance trades on singleton checks. Each element is a list of edits; `strip(c, el)` applies them.

Edit kinds: ('rm', t, q, name)  remove the op at tick t on qubit q with unit name (CX: q is the pair (a, b));
            ('add', t, lines)   add an op group;  ('rmdet', bit) drop a singleton detector.
"""
from gadgets import *


def find(c, t, q, name):
    for o in c['ops']:
        if o['t'] != t:
            continue
        u = unit(o)
        if name == 'CX':
            if u.name == 'CX' and tuple(cx_qs(o)) == tuple(q):
                return o
        elif u.name == name and q in u.qs:
            return o
    raise KeyError((t, q, name))


def strip(c, edits):
    c = copy.deepcopy(c)
    for e in edits:
        if e[0] == 'rm':
            c['ops'].remove(find(c, e[1], e[2], e[3]))
        elif e[0] == 'add':
            c['ops'].append(dict(t=e[1], lines=list(e[2])))
        elif e[0] == 'rmdet':
            line = f'// DETECTOR c[{e[1]}]'
            if line not in c['tail']:
                raise ValueError(('not a singleton detector', e[1]))
            c['tail'].remove(line)
        elif e[0] == 'move':
            o = find(c, e[1], e[2], e[3]); o['t'] = e[4]
        else:
            raise ValueError(e)
    return fix(c)


def singles(c):
    return {int(BITRE.findall(l)[0]) for l in c['tail'] if l.startswith('// DETECTOR') and len(BITRE.findall(l)) == 1}


def cx_pairs(c):
    """CX (a->b) at t and t+1, consecutive on both qubits."""
    out = []
    for q in range(36):
        s = seq(c, q)
        for x, y in zip(s, s[1:]):
            if unit(x).name == 'CX' and unit(y).name == 'CX' and cx_qs(x) == cx_qs(y) and y['t'] == x['t'] + 1:
                a, b = cx_qs(x)
                if q != a:
                    continue
                sb = seq(c, b)
                ib = sb.index(x)
                if ib + 1 < len(sb) and sb[ib + 1] is y:
                    out.append(dict(a=a, b=b, t=x['t']))
    return out


def elements(c):
    S1 = singles(c)
    prs = cx_pairs(c)
    pair_ops = set()
    els = []
    for p in prs:
        pair_ops |= {(p['t'], (p['a'], p['b'])), (p['t'] + 1, (p['a'], p['b']))}
        els.append(dict(name=f"pair_{p['a']}_{p['b']}_{p['t']}", kind='pair',
                        edits=[('rm', p['t'], (p['a'], p['b']), 'CX'), ('rm', p['t'] + 1, (p['a'], p['b']), 'CX')]))
    for h in range(36):
        s = seq(c, h)
        for k, o in enumerate(s):
            u = unit(o)
            if u.name not in ('MEASURE', 'MX') or not bits_of(o) or bits_of(o)[0] not in S1:
                continue
            j = k - 1
            cxs, pcx = [], []
            while j >= 0 and unit(s[j]).name == 'CX':
                key = (s[j]['t'], tuple(cx_qs(s[j])))
                (pcx if key in pair_ops else cxs).append(s[j])
                j -= 1
            if not cxs:
                continue
            P = s[j] if j >= 0 else None
            N = s[k + 1] if k + 1 < len(s) else None
            b = bits_of(o)[0]
            pn = unit(P).name if P else None
            nn = unit(N).name if N else None
            rm_cx = [('rm', x['t'], tuple(cx_qs(x)), 'CX') for x in cxs]
            partners = collections.defaultdict(list)
            for x in cxs:
                a_, b_ = cx_qs(x)
                partners[b_ if a_ == h else a_].append(x)
            base = f"chk_h{h}_{'_'.join(map(str, sorted(partners)))}_{min(x['t'] for x in cxs)}_{o['t']}"
            # full removal
            if nn in (None, 'RESET', 'RX'):
                ed = rm_cx + [('rm', o['t'], h, u.name), ('rmdet', b)]
                if pn in ('RESET', 'RX') and not pcx:
                    ed.append(('rm', P['t'], h, pn))
                els.append(dict(name=base, kind='session', edits=ed))
            else:
                # the measurement initialises the next role: keep it as a plain idle check, or replace it by an init
                els.append(dict(name=base + '_keepM', kind='session', edits=list(rm_cx)))
                init = ['reset q[%d];' % h] + (['h q[%d];' % h] if u.name == 'MX' else [])
                ed = rm_cx + [('rm', o['t'], h, u.name), ('rmdet', b), ('add', o['t'], init)]
                if pn in ('RESET', 'RX') and not pcx:
                    ed.append(('rm', P['t'], h, pn))
                els.append(dict(name=base + '_init', kind='session', edits=ed))
            if len(partners) > 1:
                for d, xs in partners.items():
                    els.append(dict(name=f"{base}_only{d}", kind='partial',
                                    edits=[('rm', x['t'], tuple(cx_qs(x)), 'CX') for x in xs]))
    return els


def q6_elements(c):
    """q6's unread guard (v36f: R31, CX 6->7 at 32,37-41, 6->0 at 33-36, then CX 12->6 at 42 as B)."""
    s = [o for o in seq(c, 6) if 31 <= o['t'] <= 41]
    to7 = [o for o in s if unit(o).name == 'CX' and cx_qs(o) == [6, 7]]
    to0 = [o for o in s if unit(o).name == 'CX' and cx_qs(o) == [6, 0]]
    r = [o for o in s if unit(o).name == 'RESET']
    if not (to7 and to0 and r):
        return []
    e7 = [('rm', o['t'], (6, 7), 'CX') for o in to7]
    e0 = [('rm', o['t'], (6, 0), 'CX') for o in to0]
    return [dict(name='q6g_no7', kind='q6', edits=e7), dict(name='q6g_no0', kind='q6', edits=e0),
            dict(name='q6g_none', kind='q6', edits=e7 + e0 + [('move', r[0]['t'], 6, 'RESET', 41)])]


if __name__ == '__main__':
    c = read(C / sys.argv[1])
    for e in elements(c) + q6_elements(c):
        print(e['name'], e['edits'])
