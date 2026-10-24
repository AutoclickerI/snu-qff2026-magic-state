"""Leave-one-out variants of a joint: loo.py JOINT BASE -> c/JOINT__loo_<k> (all gadgets but k)."""
from joint import *

jn, base = sys.argv[1], sys.argv[2]
gs = json.loads((C / jn).with_suffix('.json').read_text())['integ']['gadgets']
c0 = load_plan(base)
names = []
for k, g in enumerate(gs):
    c, used = compose(c0, [x for i, x in enumerate(gs) if i != k])
    if len(used) != len(gs) - 1:
        print('skip', k, gname(g), len(used))
        continue
    n = f'{jn}__loo{k}'
    save(c, n, dict(kind='loo', joint=jn, base=base, dropped=g, gadgets=used))
    names.append(n)
(H / f'loo_{jn}.txt').write_text(' '.join(names))
print(len(names))
