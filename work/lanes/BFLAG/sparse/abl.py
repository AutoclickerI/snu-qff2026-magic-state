"""All-orders loss/acceptance with chosen noise made ideal (optimistic bounds).

Usage as a library:
    ctx = Ctx(stem)                    # prepares model, caches noise-independent kernels
    res = ctx.many({name: keep_fn})    # keep_fn(meta, fault) -> weight multiplier in [0,1]
meta: chan.classify() entry (kind, qs, t0, n, line, op, p); fault: frontend fault dict (pauli, qs, p, ...).
Removing a fault component lowers that channel's total probability (no renormalisation).
"""
import sys, json, time, os
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE))
import sparse_walsh as sw, chan

_G = {}


def compile_filtered(m, groups, nd, ks, meta, keep):
    """Weighted faults (weight 0 drops a fault) as sw.compile_channels entries; a channel's no-fault weight is
    1 - (sum of its kept fault probabilities)."""
    kept = {}
    for cid, fs in groups.items():
        ws = [keep(meta[cid], f) for f in fs]
        if any(ws):
            kept[cid] = [dict(f, p=f['p'] * w) for f, w in zip(fs, ws) if w]
    saved = {cid: m.chans[cid]['p'] for cid in kept}
    for cid, fs in kept.items():
        m.chans[cid]['p'] = sum(f['p'] for f in fs)
    try:
        return sw.compile_channels(m, kept, nd, ks)
    finally:
        for cid, p in saved.items():
            m.chans[cid]['p'] = p


def _job(arg):
    name, k = arg
    compiled, elim = _G['comp'][name]
    states, weights, emask = _G['kern'][k]
    factors = sw.factors_for(compiled, states, emask, elim['order'])
    vec, _ = sw.contract_selector(factors, elim['order'], len(states))
    return name, k, float(np.dot(weights, vec) / (1 << len(_G['ks'])))


class Ctx:
    def __init__(self, stem, procs=None):
        self.stem = Path(stem)
        m, eng, groups, nd, ks, psi, where, _ = sw.prepare(self.stem, True)
        self.m, self.eng, self.groups, self.nd, self.ks = m, eng, groups, nd, ks
        self.meta = chan.classify(m)
        self.keys = [None] + eng.keys[:72]
        kern = []
        for key in self.keys:
            states, weights, _ = sw.sparse_kernel(eng, ks, psi, where, key)
            kern.append((states, weights, 0 if key is None else sw.emask_for(key)))
        self.kern = kern
        self.procs = procs or int(os.environ.get('ABL_PROCS', '12'))

    def many(self, specs):
        comp = {}
        for name, keep in specs.items():
            c = compile_filtered(self.m, self.groups, self.nd, self.ks, self.meta, keep)
            comp[name] = (c, sw.minfill([set(e[0]) for e in c]))
        _G.update(comp=comp, kern=self.kern, ks=self.ks)
        jobs = [(n, k) for n in specs for k in range(len(self.keys))]
        import multiprocessing as mp
        with mp.get_context('fork').Pool(self.procs) as pool:
            res = pool.map(_job, jobs, chunksize=1)
        vals = {n: [0.] * len(self.keys) for n in specs}
        for n, k, v in res:
            vals[n][k] = v
        out = {}
        eng = self.eng
        for n, rows in vals.items():
            A = rows[0]
            obs = sum(w * b * r for w, b, r in zip(eng.W, eng.beta, rows[1:]))
            out[n] = dict(loss=(A - obs) / (2 * A), acceptance=A)
        return out


ALL = lambda md, f: 1.0


def drop(pred):
    """keep_fn that removes whole channels where pred(meta) is true."""
    return lambda md, f: 0.0 if pred(md) else 1.0


if __name__ == '__main__':
    t = time.time()
    ctx = Ctx(sys.argv[1])
    print(json.dumps(ctx.many({'base': ALL})), time.time() - t)
