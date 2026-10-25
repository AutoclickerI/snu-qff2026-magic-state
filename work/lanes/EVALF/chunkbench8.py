import sys, time, statistics, json
from pathlib import Path
sys.path.insert(0, str(Path('sparse').resolve()))
import numpy as np, sparse_walsh as sw
m, eng, groups, nd, ks, psi, where, _ = sw.prepare(Path(sys.argv[1]).resolve(), True)
compiled, elim = sw.compile_best(m, eng, groups, nd, ks)
keys = [None] + eng.keys
data = []
for key in keys[::12]:
    st, w, _ = sw.sparse_kernel(eng, ks, psi, where, key)
    data.append((st, sw.factors_for(compiled, st, 0 if key is None else sw.emask_for(key), elim['order'])))
def run(cc):
    for st, f in data:
        if cc:
            np.concatenate([sw.contract_selector([(s, a[lo:lo + cc] if len(a) > 1 else a) for s, a in f], elim['order'], min(cc, len(st) - lo))[0] for lo in range(0, len(st), cc)])
        else:
            sw.contract_selector(f, elim['order'], len(st))
def kern(kb):
    for key in keys[::12]:
        sw.sparse_kernel(eng, ks, psi, where, key)
def job(seed):
    res = {}
    for rep in range(4):
        for cc in (0, 256, 384):
            t = time.perf_counter(); run(cc); res.setdefault(f'cc{cc}', []).append(time.perf_counter() - t)
    return {k: statistics.median(v) / len(data) * 1e3 for k, v in res.items()}
import multiprocessing as mp
with mp.get_context('fork').Pool(8) as pool:
    out = pool.map(job, range(8))
print(json.dumps({k: round(statistics.mean(o[k] for o in out), 2) for k in out[0]}), 'ms/moment, mean over 8 concurrent workers')
