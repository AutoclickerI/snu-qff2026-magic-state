"""Phantom late-check screen on v36g: every weight-4 Z/X stabilizer element and blue-style XZ, latest feasible ticks."""
import sys, json, itertools
sys.path.insert(0, '.')
from qedit import load
import ph
BASE = '/home/jihoon/competitions/quantumn/work/lanes/MAIN/v36g'
c = load(BASE)
D = [0, 20, 7, 10, 3, 22, 21]
S = [{0, 2, 4, 6}, {1, 2, 5, 6}, {3, 4, 5, 6}]
elems = {}
for m in range(1, 8):
    s = set()
    for k in range(3):
        if m >> k & 1:
            s ^= S[k]
    elems['S' + ''.join(str(k + 1) for k in range(3) if m >> k & 1)] = sorted(s)
busy = {t: c.qubits_at(t) for t in range(len(c.segs))}
TMOVE = {10: 35, 20: 37}  # T-dag earlier for X checks (q22 at 37 already)
def idle(q, t):
    return q not in busy[t] and not (q in TMOVE and t == TMOVE[q])
specs = {}
hi = int(sys.argv[1]) if len(sys.argv) > 1 else 43
for name, idx in elems.items():
    qs = [D[i] for i in idx]
    for kind in ('Z', 'X'):
        lo = 38 if kind == 'X' else 34
        best = None
        for ts in itertools.permutations(range(lo, hi + 1), 4):
            if all(idle(q, t) for q, t in zip(qs, ts)):
                key = (min(ts), sum(ts))
                if best is None or key > best[0]:
                    best = (key, ts)
        if best is None:
            continue
        ts = best[1]
        a = 36
        ch = dict(k=kind, a=a, r=min(ts) - 1, cx=[[t, q] for q, t in zip(qs, ts)], m=max(ts) + 1)
        tm = [[q, TMOVE[q]] for q in qs if q in TMOVE] if kind == 'X' else []
        specs[f'{name}{kind}_h{hi}'] = dict(base=BASE, tmoves=tm, checks=[ch])
    # blue style XZ
    best = None
    for s in range(32, hi - 4):
        for f in itertools.combinations(qs, 2):
            sd = [q for q in qs if q not in f]
            if all(idle(q, s + 2) and idle(q, s + 5) for q in f) and all(idle(q, s + 3) and idle(q, s + 4) for q in sd):
                best = (s, f, sd)
    if best:
        s, f, sd = best
        tm = [[q, TMOVE[q]] for q in qs if q in TMOVE]
        if all(not (q in TMOVE and TMOVE[q] >= s + 2) for q in qs):
            specs[f'{name}XZ_h{hi}'] = dict(base=BASE, tmoves=tm, checks=[dict(k='XZ', a1=36, a2=37, s=s, f=list(f), sd=sd)])
for n, sp in specs.items():
    ph.build(sp, f'ph/{n}')
    print(n, json.dumps(sp['checks']), sp['tmoves'])
