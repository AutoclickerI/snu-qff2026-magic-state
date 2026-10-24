"""X2 split per fault (half each pair) for a syn/*.json resource or v36c."""
import sys, json
from collections import defaultdict
import mkcand, splice, proxy, lns
from qcirc import parse
def load(n):
    if n == 'v36c':
        u, d = parse(open('v36c.qasm').read()); return proxy.analyse(u, d)
    sol = json.load(open(n)); sol.setdefault('T0', 33)
    spec = mkcand.spec_from(sol, sol.get('policy', 'default'))
    u, d, nb = splice.build(lns.BASE[0], lns.BASE[1], spec)
    return proxy.analyse(u, d, flags=sorted({e[2] for e in spec['extra'] if e[2] not in mkcand.CELLS}), starts=mkcand.starts_of(spec))
s, faults, groups = load(sys.argv[1])
per = defaultdict(float); perq = defaultdict(float)
for df, fs in groups.items():
    if not df: continue
    for a in range(len(fs)):
        for b in range(a + 1, len(fs)):
            if proxy.dangerous(fs[a][1] ^ fs[b][1]):
                v = 0.5 * fs[a][0] * fs[b][0]
                for f in (fs[a], fs[b]):
                    per[(f[2][0], f[2][1], f[2][2])] += v / 2
                    for q in f[2][2]: perq[q] += v / 2 / len(f[2][2])
print('X2', s['X2'], 'RZ', s['RZ'], 'acc1', s['acc1'])
print('by qubit', {q: f'{v*1e6:.2f}' for q, v in sorted(perq.items(), key=lambda kv: -kv[1])[:16]})
for k, v in sorted(per.items(), key=lambda kv: -kv[1])[:int(sys.argv[2]) if len(sys.argv) > 2 else 12]:
    print(f'{v:.3e}', k)
