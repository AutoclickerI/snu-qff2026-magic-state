import numpy as np, time
rng = np.random.default_rng(1)
n = 1145; U = list(range(9))
sa = (0, 1, 2, 4, 6, 7); sb = (1, 3, 5, 7, 8)
A = rng.random((n,) + (2,) * len(sa)); B = rng.random((n,) + (2,) * len(sb))
def bshape(s): return (n,) + tuple(2 if u in s else 1 for u in U)
def t(f, r=20):
    f(); t0 = time.perf_counter()
    for _ in range(r): x = f()
    return (time.perf_counter() - t0) / r * 1e3, x
ms, ref = t(lambda: A.reshape(bshape(sa)) * B.reshape(bshape(sb)))
print('broadcast mul', ms)
# 2D layout: column bit j <-> scope[j]; union assignment u bit k <-> U[k]
A2 = np.ascontiguousarray(A.reshape(n, -1, order='F')); B2 = np.ascontiguousarray(B.reshape(n, -1, order='F'))
u = np.arange(1 << len(U))
def idx(s): return sum(((u >> U.index(q)) & 1) << j for j, q in enumerate(s))
ia, ib = idx(sa), idx(sb)
ms, out2 = t(lambda: np.take(A2, ia, axis=1) * np.take(B2, ib, axis=1))
print('take mul', ms, np.abs(out2 - ref.reshape(n, -1, order='F')).max())
ms, _ = t(lambda: A2[:, ia] * B2[:, ib]); print('fancy mul', ms)
def tm():
    o = np.take(A2, ia, axis=1); o *= np.take(B2, ib, axis=1); return o
ms, _ = t(tm); print('take inplace', ms)
# sum over variable at bit p
full = out2
for p in (0, 4, 8):
    ms, s1 = t(lambda: full.reshape(n, -1, 2, 1 << p).sum(axis=2))
    def ph():
        o = full.reshape(n, -1, 2, 1 << p); r = o[:, :, 0] + o[:, :, 1]; r *= 0.5; return r
    ms2, s2 = t(ph)
    T = ref  # tensor layout mean over axis
    ax = 1 + p
    ms3, s3 = t(lambda: ref.mean(axis=ax))
    print('sum bit', p, 'reshape-sum', round(ms, 3), 'pair-add', round(ms2, 3), 'tensor mean', round(ms3, 3))
