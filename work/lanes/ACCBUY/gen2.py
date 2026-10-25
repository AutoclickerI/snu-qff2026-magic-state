"""Phantom check screen on v36g with time-dependent code-qubit positions.
usage: gen2.py <hi> [width] -> builds ph2/<elem><kind>_h<hi> for all elements, kinds Z, X, XZ (latest ticks <= hi)."""
import sys, json, itertools, os
sys.path.insert(0, '.')
from qedit import load
import ph
BASE = '/home/jihoon/competitions/quantumn/work/lanes/MAIN/v36g'
c = load(BASE)
S = [{0, 2, 4, 6}, {1, 2, 5, 6}, {3, 4, 5, 6}]
elems = {}
for m in range(1, 8):
    s = set()
    for k in range(3):
        if m >> k & 1:
            s ^= S[k]
    elems['S' + ''.join(str(k + 1) for k in range(3) if m >> k & 1)] = sorted(s)
def pos(i, t):
    if i == 0: return 0 if t >= 13 else None
    if i == 1: return 20 if t >= 13 else None
    if i == 2: return 7 if t >= 13 else None
    if i == 3: return 4 if 13 <= t <= 32 else (10 if t >= 35 else None)
    if i == 4: return 8 if 13 <= t <= 29 else (3 if t >= 34 else None)
    if i == 5: return 15 if 13 <= t <= 30 else (16 if 33 <= t <= 34 else (22 if t >= 37 else None))
    if i == 6: return 3 if 13 <= t <= 29 else (9 if t == 35 else (15 if t == 37 else (21 if t >= 39 else None)))
busy = {t: c.qubits_at(t) for t in range(len(c.segs))}
TD = {0: 30, 7: 29, 3: 29, 8: 30, 22: 37, 10: 42, 20: 43}  # current T-dag ticks
TMOVE = {10: 35, 20: 37}
def idle(q, t, tm):
    if q is None or q in busy[t]: return False
    return not (q in tm and tm[q] == t)
hi = int(sys.argv[1]); W = int(sys.argv[2]) if len(sys.argv) > 2 else 7
os.makedirs('ph2', exist_ok=True)
for name, idx in elems.items():
    for kind in ('Z', 'X', 'XZ'):
        tm = {q: t for q, t in TMOVE.items() if kind != 'Z'}
        best = None
        if kind in ('Z', 'X'):
            for ts in itertools.permutations(range(hi - W + 1, hi + 1), 4):
                qs = [pos(i, t) for i, t in zip(idx, ts)]
                if all(idle(q, t, tm) for q, t in zip(qs, ts)):
                    key = (min(ts), sum(ts))
                    if best is None or key > best[0]:
                        best = (key, ts, qs)
            if best is None: continue
            _, ts, qs = best
            ch = dict(k=kind, a=36, r=min(ts) - 1, cx=[[t, q] for q, t in zip(qs, ts)], m=max(ts) + 1)
        else:
            s = hi - 5
            for f in itertools.combinations(idx, 2):
                sd = [i for i in idx if i not in f]
                pf = [pos(i, s + 2) for i in f]; ps = [pos(i, s + 3) for i in sd]
                if [pos(i, s + 5) for i in f] != pf or [pos(i, s + 4) for i in sd] != ps: continue
                if all(idle(q, s + 2, tm) and idle(q, s + 5, tm) for q in pf) and all(idle(q, s + 3, tm) and idle(q, s + 4, tm) for q in ps):
                    best = (pf, ps)
            if best is None: continue
            ch = dict(k='XZ', a1=36, a2=37, s=s, f=best[0], sd=best[1])
        used = {q for q in [pos(i, t) for i in idx for t in range(hi - W, hi + 1)] if q is not None}
        tml = [[q, t] for q, t in tm.items() if q in used and TD[q] > t] if kind != 'Z' else []
        spec = dict(base=BASE, tmoves=tml, checks=[ch])
        n = f'{name}{kind}_h{hi}'
        try:
            ph.build(spec, f'ph2/{n}')
            print(n, json.dumps(ch), tml)
        except Exception as e:
            print(n, 'FAIL', e)
