"""Greedy CX-pair fill of idle resource cells (CX.CX = I; DEPOLARIZE2 x2 replaces four waiting DEPOLARIZE1),
scored by the proxy J = X2 + KZ*RZ + KA*acc1 on a base.  usage: pairfill.py <syn.json> <out.json> [base] [KZ KA]"""
import sys, json, os
os.environ.setdefault('BFLAG_BASE', sys.argv[3] if len(sys.argv) > 3 else 'v36c')
import lns3
from qcirc import adjacent

CELLS = lns3.S.CELLS


def live_idle(state):
    T0, ops = state['T0'], state['ops']
    first, busy = {}, set()
    for t, layer in enumerate(ops):
        for a, b in layer:
            for q in (a, b):
                first[q] = min(first.get(q, 99), t)
                busy.add((t, q))
    return first, busy


def candidates(state):
    first, busy = live_idle(state)
    D = len(state['ops'])
    qs = sorted(first)
    out = []
    for t in range(D - 1):
        for a in qs:
            for b in qs:
                if a >= b or not adjacent(a, b):
                    continue
                if t < max(first[a], first[b]):
                    continue
                if any((tt, q) in busy for tt in (t, t + 1) for q in (a, b)):
                    continue
                for e in ((a, b), (b, a)):
                    out.append((t, e))
    return out


def add(state, t, e):
    st = json.loads(json.dumps(state))
    st['ops'][t].append(list(e)); st['ops'][t + 1].append(list(e))
    st['pivots'] = {int(q): v for q, v in st['pivots'].items()}
    return st


if __name__ == '__main__':
    a = sys.argv
    KZ = float(a[4]) if len(a) > 4 else 1.1e-4
    KA = float(a[5]) if len(a) > 5 else 3e-5
    st = json.load(open(a[1]))
    st['pivots'] = {int(q): (v if isinstance(v, int) else sum(b << k for k, b in enumerate(v))) for q, v in st['pivots'].items()}
    J, s = lns3.score(st, KZ, KA)
    print(json.dumps(dict(start=J, X2=s['X2'], RZ=s['RZ'], acc1=s['acc1'])), flush=True)
    added = []
    while True:
        best = None
        for t, e in candidates(st):
            j, ss = lns3.score(add(st, t, e), KZ, KA)
            if j is not None and (best is None or j < best[0]):
                best = (j, t, e, ss)
        if best is None or best[0] >= J - 1e-12:
            break
        J, t, e, s = best
        st = add(st, t, e); added.append([st['T0'] + t, list(e)])
        print(json.dumps(dict(J=J, add=added[-1], X2=s['X2'], RZ=s['RZ'], acc1=s['acc1'])), flush=True)
    o = dict(st); o['pivots'] = {str(q): v for q, v in st['pivots'].items()}; o['J'] = J; o['proxy'] = s; o['pairs'] = added
    open(a[2], 'w').write(json.dumps(o))
