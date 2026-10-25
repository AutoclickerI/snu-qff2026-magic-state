import sys, time, statistics, json
from pathlib import Path
sys.path.insert(0, str(Path('sparse').resolve()))
import numpy as np, sparse_walsh as sw
m, eng, groups, nd, ks, psi, where, _ = sw.prepare(Path(sys.argv[1]).resolve(), True)
compiled, elim = sw.compile_best(m, eng, groups, nd, ks)
keys = ([None] + eng.keys)[::6]
def blocked(key, kb):
    mj, wj, c = (0, 0, 1) if key is None else eng.Qs[key]
    group = np.zeros((eng.N, len(where)), dtype=np.complex128)
    for v, idx in enumerate(where): group[idx, v] = 1
    M = group * (c * eng.sgn(wj))[:, None]; perm = eng.idx.astype(int) ^ mj
    g = np.empty((len(psi), len(where)))
    for lo in range(0, len(psi), kb):
        blk = psi[lo:lo + kb]
        mix = np.take(blk, perm, axis=1); np.conjugate(mix, out=mix); mix *= blk
        g[lo:lo + kb] = (mix @ M).real
    return sw.fwht(g)
def job(seed):
    res = {}
    for rep in range(4):
        for kb in (0, 1024, 4096):
            t = time.perf_counter()
            for key in keys:
                if kb: blocked(key, kb)
                else: sw.sparse_kernel(eng, ks, psi, where, key)
            res.setdefault(f'kb{kb}', []).append(time.perf_counter() - t)
        t = time.perf_counter()
        for key in keys:
            st, w, _ = sw.sparse_kernel(eng, ks, psi, where, key); sw.factors_for(compiled, st, 0 if key is None else sw.emask_for(key), elim['order'])
        res.setdefault('kernel+factors', []).append(time.perf_counter() - t)
    return {k: statistics.median(v) / len(keys) * 1e3 for k, v in res.items()}
import multiprocessing as mp
with mp.get_context('fork').Pool(int(sys.argv[2])) as pool:
    out = pool.map(job, range(int(sys.argv[2])))
print(json.dumps({k: round(statistics.mean(o[k] for o in out), 2) for k in out[0]}), 'ms/moment, mean over', sys.argv[2], 'concurrent workers')
