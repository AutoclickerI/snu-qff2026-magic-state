"""Dense exact evaluation of (s, d) fault classes on the small rotation subspace."""
import math

import numpy as np

from model import Basis, Model

SQ2 = math.sqrt(2.0)


class Engine:
    def __init__(self, model: Model):
        m = self.m = model
        B = self.B = Basis()
        for r in m.rots:
            B.add(r[0])
        self.rank_rot = len(B.vecs)
        # make sure every x-part we will touch lies in the span (exact, otherwise extend)
        for x, z, c in m.proj_m + [(q[0], q[1], q[2]) for q in m.Q.values()]:
            B.add(x)
        self.r = len(B.vecs)
        N = self.N = 1 << self.r
        self.idx = np.arange(N, dtype=np.uint64)
        self.rot = []
        for (x, z, coef, theta, _ins) in m.rots:
            self.rot.append((B.express(x), self._w(z), coef, theta))
        self.projs = [(B.express(x), self._w(z), c) for x, z, c in m.proj_m]
        self.sign_cache = {}
        self.Qs = {k: (B.express(v[0]), self._w(v[1]), v[2]) for k, v in m.Q.items()}
        # decode weights W[T][(a,b)]
        W = {"X": {}, "Y": {}}
        syn = np.arange(64)
        sx = (syn & 7) != 0
        sz = ((syn >> 3) & 7) != 0
        sgn = {"X": np.where(sx, -1.0, 1.0), "Y": np.where(sx ^ sz, -1.0, 1.0)}
        for T in "XY":
            for a in range(8):
                for b in range(8):
                    ch = np.array([(-1) ** (bin((s & 7) & a).count("1") + bin(((s >> 3) & 7) & b).count("1")) for s in range(64)])
                    W[T][(a, b)] = float((sgn[T] * ch).sum() / 64)
        self.keys = [k for k in m.Q if abs(W[k[0]][(k[1], k[2])]) > 1e-15]
        self.W = np.array([W[k[0]][(k[1], k[2])] for k in self.keys])
        self.beta = np.array([(1 / SQ2) * (-1) ** m.cz if k[0] == "X" else -(1 / SQ2) * (-1) ** m.cxz for k in self.keys])
        # sign table over e (10 bits): bit mask of each Q key
        # e bits: 0..5 stabs, 6 X7, 7 Z7, 8 parZ, 9 parXZ
        masks_ = []
        for (T, a, b) in self.keys:
            msk = a | (b << 3)
            if T == "X":
                msk |= (1 << 6) | (1 << 8)
            else:
                msk |= (1 << 6) | (1 << 7) | (1 << 9)
            masks_.append(msk)
        e = np.arange(1024)
        par = np.zeros((1024, len(self.keys)))
        for k, msk in enumerate(masks_):
            par[:, k] = 1 - 2 * (np.bitwise_count(e & msk).astype(np.int64) & 1)
        self.SG = par * (self.W * self.beta)[None, :]      # (1024, nq)
        # detector reference values: from the noiseless state
        self.v = list(m.proj_v)
        self._ref()

    def _w(self, z):
        w = 0
        for i, b in enumerate(self.B.vecs):
            w |= ((b & z).bit_count() & 1) << i
        return w

    def sgn(self, w):
        s = self.sign_cache.get(w)
        if s is None:
            s = 1.0 - 2.0 * (np.bitwise_count(self.idx & np.uint64(w)) & 1).astype(np.float64)
            self.sign_cache[w] = s
        return s

    def phi(self, s):
        a = np.zeros(self.N, dtype=complex)
        a[0] = 1.0
        for j, (mj, wj, coef, theta) in enumerate(self.rot):
            th = -theta if (s >> j) & 1 else theta
            sg = self.sgn(wj)
            sn = 1j * math.sin(th) * coef
            a = math.cos(th) * a + sn * (sg * a)[self.idx ^ np.uint64(mj)]
        return a

    def apply(self, a, pm):
        mj, wj, coef = pm
        return coef * (self.sgn(wj) * a)[self.idx ^ np.uint64(mj)]

    def expect(self, a, pm):
        mj, wj, coef = pm
        return float((np.conj(a[self.idx ^ np.uint64(mj)]) * coef * self.sgn(wj) * a).sum().real)

    def _ref(self):
        a = self.phi(0)
        # postselect conditions first
        for k in range(self.m.n_post):
            sg = (-1) ** self.v[k]
            a = (a + sg * self.apply(a, self.projs[k])) / 2
        A0 = float(np.vdot(a, a).real)
        for k in range(self.m.n_post, len(self.projs)):
            val = self.expect(a, self.projs[k]) / A0
            assert abs(abs(val) - 1) < 1e-9, f"detector {k} not deterministic: {val}"
            self.v[k] = 0 if val > 0 else 1
        self.A0 = A0
        self.v = np.array(self.v)

    def table(self, s, d):
        """(A/A0, E vector of <acc|Q|acc>/A0 over self.keys) for flipped rotations s and detector flips d,
        or None if the acceptance vanishes."""
        a = self.phi(s)
        for k, pm in enumerate(self.projs):
            sg = 1 - 2 * (int(self.v[k]) ^ ((d >> k) & 1))
            a = (a + sg * self.apply(a, pm)) / 2
            if k % 4 == 3 and float(np.vdot(a, a).real) < 1e-22:
                return None
        A = float(np.vdot(a, a).real)
        if A < 1e-18:
            return None
        E = np.array([self.expect(a, self.Qs[k]) for k in self.keys])
        return A / self.A0, E / self.A0

    def ntable(self, s, d):
        """(a, n over all 1024 e) : n = a - 0.5 * sum_q beta W sgn(e) E, in units of 1/A0."""
        t = self.table(s, d)
        if t is None:
            return 0.0, None
        A, E = t
        n = 0.5 * (A - self.SG @ E)
        return A, n


class BatchMixin:
    pass


def _phi_all(self, svals):
    out = []
    for s in svals:
        v = self.phi_cache.get(s)
        if v is None:
            v = self.phi(int(s))
            self.phi_cache[s] = v
        out.append(v)
    return np.array(out)


def batch_tables(self, S, D):
    """Vectorized table(): returns (A/A0 (K,), E/A0 (K, nq))."""
    if not hasattr(self, "phi_cache"):
        self.phi_cache = {}
        self.idx_i = self.idx.astype(np.int64)
    S = np.asarray(S, dtype=np.int64)
    D = np.asarray(D, dtype=np.int64)
    acc = _phi_all(self, S)
    for k, (mj, wj, coef) in enumerate(self.projs):
        sg = (1 - 2 * (int(self.v[k]) ^ ((D >> k) & 1))).astype(np.float64)
        perm = self.idx_i ^ mj
        acc = (acc + sg[:, None] * coef * (self.sgn(wj)[None, :] * acc)[:, perm]) / 2
    A = (np.abs(acc) ** 2).sum(axis=1)
    E = np.zeros((len(S), len(self.keys)))
    live = A > 1e-18
    if live.any():
        a = acc[live]
        for q, key in enumerate(self.keys):
            mj, wj, coef = self.Qs[key]
            perm = self.idx_i ^ mj
            E[live, q] = (np.conj(a[:, perm]) * coef * self.sgn(wj)[None, :] * a).sum(axis=1).real
    return A / self.A0, E / self.A0


def batch_n(self, S, D):
    """(a (K,), n (K,1024)) with n = 0.5 (a - SG E)."""
    A, E = batch_tables(self, S, D)
    n = 0.5 * (A[:, None] - E @ self.SG.T)
    n[A <= 1e-18] = 0.0
    return A, n


Engine.batch_tables = batch_tables
Engine.batch_n = batch_n
