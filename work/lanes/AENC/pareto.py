"""Exact (class-table) Pareto front of loss vs acceptance over all asearch encoders and init variants (v36c exterior)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import Table
from rank import variants
import enc
T = Table(sys.argv[1])
recs = [json.loads(l) for l in open(sys.argv[2])]
res = []
for i, r in enumerate(recs):
    for s in variants(r):
        L, A = T.exact(s)
        res.append((L, A, i, r['cx'], s))
L0, A0 = T.exact(enc.V36C)
res.sort(key=lambda x: (-x[1], x[0]))
front, best = [], 1e9
for x in res:
    if x[0] < best - 1e-15:
        front.append(x); best = x[0]
print(f'v36c {L0:.6e} {A0:.5f}')
for L, A, i, cx, s in sorted(front, key=lambda x: x[0]):
    print(f'{L:.6e} acc {A:.5f}  dL {L - L0:+.3e} dA {A - A0:+.5f}  rate {(L - L0) / (A - A0) if A != A0 else 0:+.2e}  #{i} cx {cx} init {s["init"]} checks {s["checks"]}')
