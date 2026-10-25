"""q4 guard on q3/q10 before q4's B role (v36g)."""
import sys
from elements import *
base = read('/home/jihoon/competitions/quantumn/work/lanes/MAIN/v36g')
def variant(name, tgt_seq, rd=False, rm_pairs=('pair_4_5_38',), rt=36):
    c = copy.deepcopy(base)
    els = {e['name']: e for e in elements(c)}
    for p in rm_pairs:
        c = strip(c, els[p]['edits'])
    # move reset q4 37 -> rt
    o = next(o for o in c['ops'] if o['t'] == 37 and o['lines'] == ['reset q[4];'])
    o['t'] = rt
    items = [(t, [f'cx q[4],q[{q}];']) for t, q in tgt_seq]
    if rd:
        m = bit(c)
        tm = tgt_seq[-1][0] + 1
        items.append((tm, [f'measure q[4] -> c[{m}];']))
        c['tail'].append(f'// DETECTOR c[{m}]')
    c = add_ops(c, items)
    st = save(c, name)
    print(name, st)
variant('g4_3_37_39', [(37, 3), (38, 3), (39, 3)])
variant('g4_3_37_38r', [(37, 3), (38, 3)], rd=True)
variant('g4_10_37_38', [(37, 10), (38, 10)], rm_pairs=('pair_4_5_38',))
variant('g4_m_37_39', [(37, 3), (38, 10), (39, 3)])
variant('g4_3_37_39_p41', [(37, 3), (38, 3), (39, 3)], rm_pairs=('pair_4_5_38', 'pair_4_5_41'))
