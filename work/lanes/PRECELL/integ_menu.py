"""INTEG's echo and pair singles (gadgets.echoes / gadgets.pairs, INTEG's p2 selection rules) on a base stem,
restricted to gadgets that touch ticks >= TMIN; written to PRECELL/c/<prefix>__<gadget>, list in c/<prefix>.list.
usage: integ_menu.py <base stem> <prefix> [TMIN]"""
import sys
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/PRECELL')
from guards import *

base, prefix = sys.argv[1], sys.argv[2]
TMIN = int(sys.argv[3]) if len(sys.argv) > 3 else 0
c = read(base)
st = status(c)
names = []


def emit(cc, g):
    n = f'{prefix}__{gname_i(g)}'
    if n in names:
        return
    try:
        save_plan(cc, n, dict(gadget=g))
        names.append(n)
    except Exception as e:
        print(n, repr(e)[:160])


import gadgets as G
gname_i = G.gname
es = echoes(c, st)
by = collections.defaultdict(list)
for e in es:
    if e['t2'] + 1 >= TMIN:
        by[(e['q'], e['h'], e['axis'])].append(e)
for k, v in by.items():
    for e in v:
        if not any(f is not e and f['t1'] <= e['t1'] and f['t2'] >= e['t2'] for f in v):
            emit(add_echo(c, e), e)
ps = [p for p in pairs(c, st) if p['t'] + 1 >= TMIN and not (p['a'] in D and p['b'] in D)]
runs = collections.defaultdict(list)
for p in ps:
    runs[(p['a'], p['b'])].append(p)
for k, v in runs.items():
    v.sort(key=lambda p: p['t'])
    groups = [[v[0]]]
    for p in v[1:]:
        if p['t'] == groups[-1][-1]['t'] + 1 and p['sa'] == groups[-1][-1]['sa'] and p['sb'] == groups[-1][-1]['sb']:
            groups[-1].append(p)
        else:
            groups.append([p])
    for g in groups:
        p = g[len(g) // 2]
        emit(add_pair(c, p), p)
(P / (prefix + '.list')).write_text(' '.join(names))
print(len(names))
