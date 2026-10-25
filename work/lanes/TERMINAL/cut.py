"""Cut sweep: all-orders loss of <stem> with every op before tick t0 made noiseless, for each t0 in argv[2:]."""
import sys, json, io, contextlib
from pathlib import Path
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/MAIN/sparse')
import sparse_walsh as sw, region
stem = Path(sys.argv[1])
m, *_ = sw.prepare(stem, True)
ops = sorted({(op.time, tuple(op.qs), op.kind) for op in m.labels})
T = max(t for t, _, _ in ops)
print(json.dumps(dict(last_tick=T, n_ops=len(ops))), flush=True)
dq = json.load(open(stem.with_suffix('.json')))['data_qubits']
print('ops at the last 6 ticks:')
for t in range(T - 5, T + 1):
    print(t, [(qs, k) for tt, qs, k in ops if tt == t])
for t0 in map(int, sys.argv[2:]):
    spec = dict(name=f'before {t0} perfect', units=[[t, list(qs)] for t, qs, _ in ops if t < t0])
    with contextlib.redirect_stdout(io.StringIO()):
        r = region.run(stem, spec, 8)
    print(json.dumps(dict(t0=t0, loss=r['loss'], acceptance=r['acceptance'])), flush=True)
