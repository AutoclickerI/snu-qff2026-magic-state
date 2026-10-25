"""Helper guards as seeds: flip a helper's init (R->RX) and its closing measurement (M->MX) together; report |R_V>."""
import sys, copy, itertools
import lin
stem = sys.argv[1]
ops, dets = lin.load(stem)
FLIP = {'R': 'RX', 'RX': 'R', 'M': 'MX', 'MX': 'M'}
# helper windows: (qubit, init time, meas time) with only control-CX onto B/C inside
wins = []
for q in sorted({q for o in ops for q in o.qs}):
    if q in lin.B or q in lin.C:
        continue
    seq = [(i, o) for i, o in enumerate(ops) if q in o.qs and 28 <= o.time <= 44]
    cur = None
    for i, o in seq:
        if o.kind in ('R', 'RX', 'M', 'MX'):
            if cur is not None and o.kind in ('M', 'MX'):
                cxs = cur[2]
                if cxs and all(ops[j].qs[0] == q and (ops[j].qs[1] in lin.B or ops[j].qs[1] in lin.C) for j in cxs):
                    wins.append((q, cur[0], i, [(ops[j].time, ops[j].qs[1]) for j in cxs]))
                cur = None
            if o.kind in ('R', 'RX'):
                cur = (i, o, [])
        elif o.kind == 'CX' and cur is not None:
            cur[2].append(i)
for w in wins:
    print('window', w[0], 'init t', ops[w[1]].time, 'meas t', ops[w[2]].time, 'cx', w[3])
def run(ws):
    o2 = [copy.copy(o) for o in ops]
    for w in ws:
        for i in (w[1], w[2]):
            o2[i].kind = FLIP[o2[i].kind]
    return lin.cstate(lin.simulate(o2, 44))
for r in range(1, len(wins) + 1):
    for ws in itertools.combinations(wins, r):
        st = run(ws)
        tag = [w[0] for w in ws]
        ok = st['B0L'] and st['rX'] + st['rZ'] == 7
        print(tag, 'B0L', st['B0L'], 'rX', st['rX'], 'rZ', st['rZ'], 'X(V)', [lin.fmt(m) for m in st['X']],
              'inC2' if all(m in lin.C2 for m in st['X']) else 'notC2', 'PURE' if ok else '')
