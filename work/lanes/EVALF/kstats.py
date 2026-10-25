import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import numpy as np, sparse_walsh as sw
m, eng, groups, nd, ks, psi, where, dense = sw.prepare(Path(sys.argv[2]).resolve(), True)
compiled, elim = sw.compile_best(m, eng, groups, nd, ks)
n = 1146
def rank(vs):
    piv = {}
    for v in vs:
        while v:
            h = v.bit_length() - 1
            if h not in piv: piv[h] = v; break
            v ^= piv[h]
    return len(piv)
items = [(frozenset(e[0]), frozenset(km for km, _, _ in e[2] if km), 'in') for e in compiled]
rows = []; tot_state = tot_kappa = 0
for v in elim['order']:
    bucket = [it for it in items if v in it[0]]; items = [it for it in items if v not in it[0]]
    if not bucket: continue
    U = frozenset().union(*(b[0] for b in bucket)); K = frozenset().union(*(b[1] for b in bucket))
    R = rank(K); Kin = frozenset().union(*(b[1] for b in bucket if b[2] == 'in'))
    k = len(bucket); full = sum(1 for b in bucket if b[1])
    cs = k * (n if K else 1) * 2 ** len(U); ck = k * min(n, 2 ** R) * 2 ** len(U)
    tot_state += cs; tot_kappa += ck
    rows.append((cs, len(U), k, full, len(K), R, len(Kin), rank(Kin)))
    items.append((U - {v}, K, 'msg'))
rows.sort(reverse=True)
print('state-mode cost', tot_state, 'kappa-mode cost (rank-based)', tot_kappa)
print('(cost,|U|,#f,#full,|K|,rankK,|Kin|,rankKin)')
for r in rows[:15]: print(r)
