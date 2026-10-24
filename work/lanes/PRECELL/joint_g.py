"""Compose guards (guards.py specs) on a base stem and save complete circuits: joint_g.py <base> <name> <guard name>..."""
import sys, json
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/PRECELL')
from guards import *

base, name = sys.argv[1], sys.argv[2]
c = read(base)
used = []
for gn in sys.argv[3:]:
    g = json.loads((P / (gn + '.json')).read_text())['guard']
    st = status(c)
    h, seq = g['h'], g['seq']
    ok = all(st[h][t] in FREE for t in range(seq[0][0] - 1, seq[-1][0] + 2)) and all(st[q][t] == 'live' for t, q in seq)
    if not ok:
        print('skip', gn); continue
    c = apply(c, g)
    used.append(g)
save_plan(c, name, dict(guards=used))
print(name, len(used))
