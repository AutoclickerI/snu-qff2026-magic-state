"""Real variants: q6 (B from tick 41) reassigned from q0's echo to a Z-guard on q7 / q0."""
import sys
sys.path.insert(0, '.')
from redit import *

BASE = '../MAIN/v36d'


def strip_q6():
    c = load(BASE)
    rm(c, 32, 'reset q[6]')
    rm(c, 33, 'cx q[6],q[0]')
    for t in (35, 36, 37, 38):
        rm(c, t, 'cx q[0],q[6]')
    rm(c, 39, 'cx q[6],q[0]')
    rm(c, 40, 'q[6]')
    rmdet(c, 273)
    return c


def zguard(c, h, seq, rtick, mtick, init_is_reset_at=None):
    """Z-guard: helper |0> as control, CX h->d at each (t, d); helper reset at rtick, measured at mtick."""
    add(c, rtick, [f'reset q[{h}];'])
    for t, d in seq:
        add(c, t, [f'cx q[{h}],q[{d}];'])
    b = newbit(c)
    add(c, mtick, [f'measure q[{h}] -> c[{b}];'])
    adddet(c, [b])
    return c


V = {}
c = strip_q6(); V['q6_none'] = c
# q6 Z-guard on q7 37-40, measured at 41 = B init (replaces R at 41)
c = strip_q6(); rm(c, 41, 'reset q[6]'); zguard(c, 6, [(t, 7) for t in (37, 38, 39, 40)], 36, 41); V['q6_g7'] = c
# q6 Z-guard on q0 33-36 then q7 37-40
c = strip_q6(); rm(c, 41, 'reset q[6]'); zguard(c, 6, [(t, 0) for t in (33, 34, 35, 36)] + [(t, 7) for t in (37, 38, 39, 40)], 32, 41); V['q6_g0g7'] = c
# q6 Z-guard on q0 33-35, q7 37-40 (q7 at 36 is the 1-7 pair)
c = strip_q6(); rm(c, 41, 'reset q[6]'); zguard(c, 6, [(t, 0) for t in (33, 34, 35, 36, 37, 38, 39, 40)], 32, 41); V['q6_g0only'] = c
# q6 Z-guard on q7 at 34 and 37-40, q0 at 33, 35, 36
c = strip_q6(); rm(c, 41, 'reset q[6]'); zguard(c, 6, [(33, 0), (34, 7), (35, 0), (36, 0)] + [(t, 7) for t in (37, 38, 39, 40)], 32, 41); V['q6_g0g7b'] = c
for k, c in V.items():
    save(c, BASE, 'c/' + k, dict(source='PRECELL build_q6 ' + k))
print(list(V))
