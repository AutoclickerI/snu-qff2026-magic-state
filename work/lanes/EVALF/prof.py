"""Stage profile of a sparse_walsh evaluator directory: prof.py <evaluator_dir> <stem> <procs>.
Prints one JSON line: prepare / compile_best / pool wall, and per-row kernel / factor / contraction sums."""
import json, sys, time
from pathlib import Path
d, stem, procs = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), int(sys.argv[3])
sys.path.insert(0, str(d))
t0 = time.perf_counter()
import numpy as np
import sparse_walsh as sw
t_import = time.perf_counter() - t0
CTX = {}

def row(key):
    eng, ks, psi, where, compiled, elim = (CTX[k] for k in ('eng', 'ks', 'psi', 'where', 'compiled', 'elim'))
    a = time.perf_counter()
    states, weights, _ = sw.sparse_kernel(eng, ks, psi, where, key)
    b = time.perf_counter()
    factors = sw.factors_for(compiled, states, 0 if key is None else sw.emask_for(key), elim["order"])
    c = time.perf_counter()
    vec, _ = sw.contract_selector(factors, elim['order'], len(states))
    value = float(np.dot(weights, vec) / (1 << len(ks)))
    e = time.perf_counter()
    return value, b - a, c - b, e - c, len(states)

t1 = time.perf_counter()
m, eng, groups, nd, ks, psi, where, dense = sw.prepare(stem, True)
t2 = time.perf_counter()
compiled, elim = sw.compile_best(m, eng, groups, nd, ks)
t3 = time.perf_counter()
CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
keys = [None] + eng.keys
if procs > 1:
    import multiprocessing as mp
    with mp.get_context('fork').Pool(procs) as pool:
        rows = list(pool.imap(row, keys))
else:
    rows = [row(k) for k in keys]
t4 = time.perf_counter()
A = rows[0][0]
obs = sum(w * b * r[0] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
print(json.dumps(dict(dir=d.name, stem=stem.name, procs=procs, import_s=t_import, prepare_s=t2 - t1, compile_best_s=t3 - t2,
                      pool_wall_s=t4 - t3, total_s=t4 - t0, kernel_sum_s=sum(r[1] for r in rows),
                      factor_sum_s=sum(r[2] for r in rows), contract_sum_s=sum(r[3] for r in rows),
                      kernel_nonzero_max=max(r[4] for r in rows), channels=len(compiled), width=elim['width'],
                      work=elim['work_entries'], loss=(A - obs) / (2 * A), acceptance=A)), flush=True)
