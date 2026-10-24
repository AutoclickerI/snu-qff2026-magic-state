"""All-orders evaluation of the exterior with an A-region class distribution, and the 128-class table.

usage:
  evalx.py validate <stem> <procs>          v36c's own encoder through enc.py -> must reproduce the full all-orders loss
  evalx.py table <stem> <procs> <out.json>  A_c, O_c (unnormalised acceptance / observable) for every class c
"""
import sys, json, time, math, os
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bmodel
from bmodel import sw, fa, rep
import enc

_G = {}


def _row(job):
    tag, k = job
    compiled, elim = _G['comp'][tag]
    states, weights, emask = _G['kern'][k]
    factors = sw.factors_for(compiled, states, emask)
    vec, _ = sw.contract_selector(factors, elim['order'], len(states))
    return tag, k, float(np.dot(weights, vec) / (1 << len(_G['ks'])))


class Ev:
    def __init__(self, stem, procs=16, **kw):
        t = time.time()
        self.ext = ext = bmodel.Exterior(stem, **kw)
        m, eng = ext.m, ext.eng
        self.m, self.eng = m, eng
        nd, nr = len(ext.dets), len(m.rots)
        self.nd = nd
        active = [i for i, p in enumerate(eng.projs) if p[:2] != (0, 0)]
        assert all(p[0] == 0 for p in eng.projs)
        assert all(v == 0 for v in eng.v)
        ks = tuple(active + list(range(nd, nd + nr)))
        states = np.arange(1 << nr, dtype=np.uint32)
        psi = np.zeros((len(states), eng.N), dtype=np.complex128)
        psi[:, 0] = 1
        for j, (mj, wj, coef, theta) in enumerate(eng.rot):
            signs = 1 - 2 * ((states >> j) & 1).astype(np.int8)
            psi = np.cos(theta) * psi + (1j * math.sin(theta) * coef) * signs[:, None] * (psi * eng.sgn(wj)[None, :])[:, eng.idx.astype(int) ^ mj]
        dvals = np.zeros(eng.N, dtype=np.int32)
        for j, i in enumerate(active):
            dvals |= (np.bitwise_count(np.arange(eng.N) & eng.projs[i][1]) % 2) << j
        where = [np.flatnonzero(dvals == v) for v in range(1 << len(active))]
        self.ks = ks
        self.keys = [None] + eng.keys
        self.kern = []
        for key in self.keys:
            st, w, _ = sw.sparse_kernel(eng, ks, psi, where, key)
            self.kern.append((st, w, 0 if key is None else sw.emask_for(key)))
        self.rest = ext.rest_groups()
        self.procs = procs
        self.prep_seconds = time.time() - t

    def _groups_with(self, terms, p0):
        """rest + one extra channel: terms = [(d, s, e, prob)], p0 = no-fault weight."""
        g = dict(self.rest)
        cid = len(self.m.chans)
        self.m.chans.append(dict(name='AREGION', p=1 - p0, qs=[], ins=-1, jl=-1))
        g[cid] = [dict(d=d, s=s, e=e, p=pr, chan=cid) for d, s, e, pr in terms]
        if not g[cid]:
            g[cid] = [dict(d=0, s=0, e=0, p=0.0, chan=cid)]
        return g

    def compile(self, terms, p0):
        g = self._groups_with(terms, p0)
        out = sw.compile_best(self.m, self.eng, g, self.nd, self.ks)
        self.m.chans.pop()
        return out

    def run_many(self, comps):
        """comps: {tag: (terms, p0)} -> {tag: (A, obs)}."""
        cc = {tag: self.compile(t, p0) for tag, (t, p0) in comps.items()}
        _G.update(comp=cc, kern=self.kern, ks=self.ks)
        jobs = [(tag, k) for tag in comps for k in range(len(self.keys))]
        import multiprocessing as mp
        with mp.get_context('fork').Pool(self.procs) as pool:
            res = pool.map(_row, jobs, chunksize=1)
        vals = {tag: [0.] * len(self.keys) for tag in comps}
        for tag, k, v in res:
            vals[tag][k] = v
        eng = self.eng
        out = {}
        for tag, rows in vals.items():
            Aacc = rows[0]
            obs = sum(w * b * r for w, b, r in zip(eng.W, eng.beta, rows[1:]))
            out[tag] = (Aacc, obs)
        return out

    def dist_terms(self, Pt):
        terms = []
        for c in range(1, 128):
            if Pt[c] != 0:
                d, s, e = self.ext.sig_of(*rep(c))
                terms.append((d, s, e, float(Pt[c])))
        return terms, float(Pt[0])


def loss_of(A, obs):
    return (A - obs) / (2 * A)


if __name__ == '__main__':
    mode, stem, procs = sys.argv[1], sys.argv[2], int(sys.argv[3])
    kw = {}
    if os.environ.get('AENC_EXT') == 'drop15':      # v36c without M57: q15 released by its hop CX at 38, reset in region
        rel = dict(bmodel.REL); rel[15] = 38
        kw = dict(rel=rel, mreuse={1: 64}, check_rows=tuple(json.loads(os.environ.get('AENC_CHECKROWS', '[]'))))
    ev = Ev(stem, procs, **kw)
    print(json.dumps(dict(prep_seconds=ev.prep_seconds, region_channels=len(ev.ext.region),
                          compensated_faults=ev.ext.nflip)), flush=True)
    if mode == 'validate':
        Pt = enc.ptilde(enc.V36C)
        t = time.time()
        r = ev.run_many({'v36c_enc': ev.dist_terms(Pt), 'perfect': ([], 1.0)})
        for tag, (Aacc, obs) in r.items():
            print(json.dumps(dict(tag=tag, loss=loss_of(Aacc, obs), acceptance=Aacc, seconds=time.time() - t)), flush=True)
    elif mode == 'table':
        out = sys.argv[4]
        comps = {}
        for c in range(128):
            if c == 0:
                comps[0] = ([], 1.0)
            else:
                d, s, e = ev.ext.sig_of(*rep(c))
                comps[c] = ([(d, s, e, 1.0)], 0.0)
        t = time.time()
        r = ev.run_many(comps)
        tab = {str(c): dict(A=r[c][0], O=r[c][1]) for c in range(128)}
        Path(out).write_text(json.dumps(dict(stem=stem, table=tab, seconds=time.time() - t), indent=1))
        print('done', time.time() - t)
