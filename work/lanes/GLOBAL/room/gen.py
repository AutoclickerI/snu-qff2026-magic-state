"""Room prize on v36h: phantom late checks (ancillas 38/39), off-grid flag-gap helpers (36/37), and both."""
import sys, json, itertools
A = '/home/jihoon/competitions/quantumn/work/lanes/ACCBUY'
sys.path.insert(0, A); sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/R43')
from qedit import load
import ph, gapfill
BASE = '/home/jihoon/competitions/quantumn/work/lanes/MAIN/v36h'
c = load(BASE)
tdg = {}
for t, seg in enumerate(c.segs):
    for g in seg:
        for ln in g:
            if ln.startswith('tdg'):
                tdg[int(ln.split('[')[1].split(']')[0])] = t
print('tdg ticks', tdg)
TM = {}
for q in (10, 20, 22):
    t = tdg[q]
    while t - 1 > 30 and q not in c.qubits_at(t - 1): t -= 1
    TM[q] = t
print('earliest tdg', TM)
tdg_orig = dict(tdg); tdg.update(TM)
D = [0, 20, 7, 10, 3, 22, 21]
S = [{0, 2, 4, 6}, {1, 2, 5, 6}, {3, 4, 5, 6}]
busy = {t: c.qubits_at(t) for t in range(len(c.segs))}
def idle(q, t):
    return q not in busy[t] or (q in TM and t == tdg_orig[q])
out = {}
for m in range(1, 8):
    idx = set()
    for k in range(3):
        if m >> k & 1: idx ^= S[k]
    name = 'S' + ''.join(str(k + 1) for k in range(3) if m >> k & 1)
    qs = [D[i] for i in sorted(idx)]
    for kind in ('Z', 'X'):
        best = None
        for ts in itertools.permutations(range(30, 44), 4):
            if kind == 'X' and any(t <= tdg.get(q, -1) for q, t in zip(qs, ts)):
                continue
            if all(idle(q, t) for q, t in zip(qs, ts)):
                key = (min(ts), sum(ts))
                if best is None or key > best[0]: best = (key, ts)
        if best:
            ts = best[1]
            out[f'{name}{kind}'] = dict(base=BASE, tmoves=[[q, TM[q]] for q in qs if q in TM and kind == 'X' and TM[q] != tdg_orig[q]], checks=[dict(k=kind, a=38, r=min(ts) - 1, cx=[[t, q] for q, t in zip(qs, ts)], m=max(ts) + 1)])
    best = None
    for s in range(28, 44 - 4):
        for f in itertools.combinations(qs, 2):
            sd = [q for q in qs if q not in f]
            if any(s + 2 <= tdg.get(q, -1) for q in qs): continue
            if all(idle(q, s + 2) and idle(q, s + 5) for q in f) and all(idle(q, s + 3) and idle(q, s + 4) for q in sd):
                best = (s, f, sd)
    if best:
        s, f, sd = best
        out[f'{name}XZ'] = dict(base=BASE, tmoves=[[q, TM[q]] for q in qs if q in TM and TM[q] != tdg_orig[q]], checks=[dict(k='XZ', a1=38, a2=39, s=s, f=list(f), sd=sd)])
json.dump(out, open('specs.json', 'w'), indent=0)
for n, sp in out.items():
    try:
        ph.build(sp, n)
        txt = open(n + '.qasm').read().replace('qreg q[38];', 'qreg q[40];'); open(n + '.qasm', 'w').write(txt)
        gapfill.build({"base": n, "fill": [[36, 10, 43, 44, 45], [37, 21, 43, 44, 45]], "kind": "plus"}, n + '_gap')
        print(n, json.dumps(sp['checks']))
    except Exception as e:
        print(n, 'FAIL', e)
gapfill.build({"base": BASE, "fill": [[36, 10, 43, 44, 45], [37, 21, 43, 44, 45]], "kind": "plus"}, 'gap_only')
