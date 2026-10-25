"""Apply menu specs (singles.py / loo_build.py) to any plan with legality re-checked on that plan.
A spec: {family: echo|pair|guard|trade|loo, ...}. apply_spec(c, spec) -> new plan or raises Invalid."""
from elements import *
import joint as J
import guards_pc as GP


class Invalid(Exception):
    pass


def apply_spec(c, s):
    f = s['family']
    if f in ('echo', 'pair'):
        g = s['g']
        if not J.valid(c, g):
            raise Invalid(f)
        c2 = J.apply(c, g)
    elif f == 'guard':
        g = s['g']
        st = status(c)
        h, sq = g['h'], g['seq']
        if not (all(st[h][t] in GP.FREE for t in range(sq[0][0] - 1, sq[-1][0] + 2)) and all(st[q][t] == 'live' for t, q in sq)):
            raise Invalid('guard')
        c2 = GP.apply(c, g)
    elif f == 'trade':
        if s['kind'] == 'prep_delay':
            r = s['edit']
            if not any(o['t'] == r['old'] and o['lines'] == r['lines'] for o in c['ops']):
                raise Invalid('prep')
            st = status(c)
            q = r['q']
            if any(o['t'] in range(r['old'] + 1, r['new'] + 1) for o in seq(c, q) if o['lines'] != r['lines']):
                raise Invalid('prep busy')
            c2 = delay_preps(c, [r])
        else:
            b = s['bit']
            if f'// DETECTOR c[{b}]' not in c['tail']:
                raise Invalid('check')
            c2 = remove_check(c, b, s['mode'])
    elif f == 'loo':
        try:
            c2 = strip(c, s['edits'])
        except (KeyError, ValueError) as e:
            raise Invalid(repr(e))
    else:
        raise ValueError(f)
    try:
        c2, _ = normalized(c2)
    except Exception as e:
        raise Invalid(repr(e)[:120])
    return c2
