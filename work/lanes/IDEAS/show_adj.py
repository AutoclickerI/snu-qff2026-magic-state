import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'MAIN' / 'sparse'))
import sparse_walsh as sw, chan
stem = Path(sys.argv[1]); adj = json.loads(Path(sys.argv[2]).read_text())
m, eng, groups, nd, ks, psi, where, _ = sw.prepare(stem, True)
meta = chan.classify(m)
print('base loss', adj['loss'], 'acc', adj['acceptance'])
rows = adj['channel_ablations']
for r in sorted(rows, key=lambda r: -r['hypothetical_loss_reduction'])[:int(sys.argv[3]) if len(sys.argv) > 3 else 60]:
    d = meta[r['channel']]
    print(f"{r['hypothetical_loss_reduction']:.3e} {100*r['hypothetical_loss_reduction']/adj['loss']:5.2f}%  dacc {r['perfect_channel_acceptance']-adj['acceptance']:+.5f}  {d['kind']:6s} q{d['qs']} {''.join(chan.role(q) for q in d['qs'])} t{d['t0']}+{d['n']} L{d['line']} {d['op']}")
