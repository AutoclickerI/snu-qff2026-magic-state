import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sparse_walsh as sw, chan
stem = Path(sys.argv[1]); adj = json.loads(Path(sys.argv[2]).read_text()); sens = json.loads(Path(sys.argv[3]).read_text())
m, eng, groups, nd, ks, psi, where, _ = sw.prepare(stem, True)
meta = chan.classify(m)
S = {r['channel']: r['loss_attribution'] for r in sens['locations']}
rows = []
for r in adj['channel_ablations']:
    c = r['channel']; d = meta[c]
    ex = r['hypothetical_loss_reduction'] - S[c]   # all-orders removal minus full second-order attribution
    rows.append((ex, c, d, r))
tot = sum(x[0] for x in rows)
print('sum of excess (overlapping)', tot)
from collections import defaultdict
agg = defaultdict(float)
for ex, c, d, r in rows:
    agg[(d['kind'], ''.join(chan.role(q) for q in d['qs']))] += ex
for k, v in sorted(agg.items(), key=lambda kv: -kv[1])[:25]:
    print(f'{v:.3e}', k)
print()
for ex, c, d, r in sorted(rows, key=lambda x: -x[0])[:int(sys.argv[4]) if len(sys.argv) > 4 else 50]:
    print(f"{ex:.3e} 2nd {S[c]:.3e} all {r['hypothetical_loss_reduction']:.3e} {d['kind']:6s} q{d['qs']} {''.join(chan.role(q) for q in d['qs'])} t{d['t0']}+{d['n']} L{d['line']} {d['op']}")
