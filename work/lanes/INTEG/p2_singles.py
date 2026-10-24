"""Phase 2: single gadgets on a funded base; writes c/<base>__<gadget> and a name list."""
from gadgets import *

base = sys.argv[1]
out = sys.argv[2]
c = load_plan(base)
st = status(c)
names = []


def emit(cc, g):
    n = f'{base}__{gname(g)}'
    try:
        save(cc, n, dict(kind='single', base=base, gadget=g))
        names.append(n)
    except Exception as e:
        print(n, repr(e)[:200])


es = echoes(c, st)
by = collections.defaultdict(list)
for e in es:
    by[(e['q'], e['h'], e['axis'])].append(e)
for k, v in by.items():
    for e in v:
        if not any(f is not e and f['t1'] <= e['t1'] and f['t2'] >= e['t2'] for f in v):
            emit(add_echo(c, e), e)
ps = pairs(c, st)
runs = collections.defaultdict(list)
for p in ps:
    if p['a'] in D and p['b'] in D:
        continue
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
(H / out).write_text(' '.join(names))
print(len(names))
