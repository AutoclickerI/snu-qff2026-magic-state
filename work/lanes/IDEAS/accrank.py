import sys, json
from pathlib import Path
from collections import defaultdict
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sparse_walsh as sw, chan
stem = Path(sys.argv[1]); adj = json.loads(Path(sys.argv[2]).read_text())
m, eng, groups, nd, ks, psi, where, _ = sw.prepare(stem, True)
meta = chan.classify(m)
A0 = adj['acceptance']
rows = [(r['perfect_channel_acceptance'] - A0, r['hypothetical_loss_reduction'], meta[r['channel']]) for r in adj['channel_ablations']]
agg = defaultdict(lambda: [0., 0., 0])
for da, dl, d in rows:
    reg = 'pre' if d['t0'] < 31 else 'post'
    k = (reg, d['kind'], ''.join(chan.role(q) for q in d['qs']))
    agg[k][0] += da; agg[k][1] += dl; agg[k][2] += 1
print('sum dacc', sum(r[0] for r in rows))
for k, v in sorted(agg.items(), key=lambda kv: -kv[1][0])[:30]:
    print(f'dacc {v[0]:.4f}  dloss {v[1]:.2e}  n {v[2]}', k)
print()
for da, dl, d in sorted(rows, key=lambda x: -x[0])[:40]:
    print(f"dacc {da:.5f} dloss {dl:+.2e} {d['kind']:6s} q{d['qs']} {''.join(chan.role(q) for q in d['qs'])} t{d['t0']}+{d['n']} L{d['line']} {d['op']}")
