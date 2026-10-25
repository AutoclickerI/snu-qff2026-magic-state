"""Replacement moves: on each leave-one-out base that frees a helper (echo/guard sessions), enumerate the echoes, pairs and
guards that use that helper, legality re-derived on the reduced base. -> c/<loo base>__R_<gadget>, list in swap.list"""
from gadgets import *
import gadgets as G
import guards_pc as GP

FREED = {'echoX_15_h21_4_11': 21, 'echoX_15_h21_14_17+g22': 21, 'echoZ_6_h12_19_24': 12, 'echoX_13_h12_28_30+ext': 12,
         'echoX_15_h16_21_28+ext': 16, 'echoX_21_h22_21_30': 22, 'echoX_19_h25_19_30': 25, 'echoX_0_h6_7_10': 6,
         'g32_26': 32, 'g33_27': 33, 'g24_25': 24, 'g18_12': 18, 'g22_21': 22, 'q6g_none': 6, 'q13guard_7': 13}
names = []
for el, h in FREED.items():
    bn = f'i2_v36f__L_{el}'
    c = load_plan(bn)
    st = status(c)
    cands = []
    by = collections.defaultdict(list)
    for e in echoes(c, st):
        if e['h'] == h:
            by[(e['q'], e['axis'])].append(e)
    for v in by.values():
        for e in v:
            if not any(f is not e and f['t1'] <= e['t1'] and f['t2'] >= e['t2'] for f in v):
                cands.append((G.gname(e) + ('r' if e.get('rst') is not None else ''), lambda c, e=e: add_echo(c, e)))
    for g in GP.menu(c):
        if g['h'] == h:
            cands.append((GP.gname(g), lambda c, g=g: GP.apply(c, g)))
    runs = collections.defaultdict(list)
    for p in pairs(c, st):
        if h in (p['a'], p['b']) and not (p['a'] in D and p['b'] in D):
            runs[(p['a'], p['b'])].append(p)
    for v in runs.values():
        v.sort(key=lambda p: p['t'])
        groups = [[v[0]]]
        for p in v[1:]:
            if p['t'] == groups[-1][-1]['t'] + 1 and p['sa'] == groups[-1][-1]['sa'] and p['sb'] == groups[-1][-1]['sb']:
                groups[-1].append(p)
            else:
                groups.append([p])
        for g in groups:
            p = g[len(g) // 2]
            cands.append((G.gname(p), lambda c, p=p: add_pair(c, p)))
    seen = set()
    for k, f in cands:
        if k in seen:
            continue
        seen.add(k)
        n = f'{bn}__R_{k}'
        try:
            save(f(c), n, dict(kind='swap', base=bn))
            names.append(n)
        except Exception as e:
            print('fail', n, repr(e)[:120])
(H / 'swap.list').write_text(' '.join(names))
print(len(names))
