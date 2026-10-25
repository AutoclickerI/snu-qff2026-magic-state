"""Which change shifts loss/acceptance: abtest.py <stem> -> loss, acceptance per variant (old butterfly FWHT in the
kernel and/or in the channel tables)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path('sparse').resolve()))
import numpy as np, sparse_walsh as sw
def butterfly(a):
    a = np.asarray(a, dtype=float).reshape(-1).copy(); n = a.size; h = 1
    while h < n:
        t = a.reshape(-1, 2 * h); l = t[:, :h].copy(); r = t[:, h:].copy()
        t[:, :h] = l + r; t[:, h:] = l - r; h *= 2
    return a
blas = sw.fwht
stem = Path(sys.argv[1]).resolve()
m, eng, groups, nd, ks, psi, where, _ = sw.prepare(stem, True)
for kern, table in (('blas', 'blas'), ('butterfly', 'blas'), ('blas', 'butterfly'), ('butterfly', 'butterfly')):
    sw.fwht = butterfly if table == 'butterfly' else blas
    compiled, elim = sw.compile_best(m, eng, groups, nd, ks)
    sw.fwht = butterfly if kern == 'butterfly' else blas
    sw._CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
    rows = [sw._row(k) for k in [None] + eng.keys]
    A = rows[0]['value']; O = sum(w * b * r['value'] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
    print(json.dumps(dict(kernel=kern, tables=table, loss=(A - O) / (2 * A), acceptance=A)), flush=True)
