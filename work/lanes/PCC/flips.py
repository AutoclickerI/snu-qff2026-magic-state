"""Enumerate init flips (R->RX, M->MX, and the reverse) in ticks 20..43 of a v36h-family circuit and report which give
|R_V> (B = |0_L>, C stabilized by X(V), Z(V-perp)) after B->C at tick 44.  Pairs for k=2."""
import sys, copy, itertools, json
import lin
stem = sys.argv[1]
ops, dets = lin.load(stem)
FLIP = {'R': 'RX', 'RX': 'R', 'M': 'MX', 'MX': 'M'}
cand = [i for i, o in enumerate(ops) if o.kind in FLIP and 20 <= o.time <= 43]
def run(idxs):
    o2 = [copy.copy(o) for o in ops]
    for i in idxs:
        o2[i].kind = FLIP[o2[i].kind]
    sim = lin.simulate(o2, 44)
    st = lin.cstate(sim)
    return st
res = {}
good1 = []
for i in cand:
    st = run([i])
    o = ops[i]
    pure = st['B0L'] and st['rX'] + st['rZ'] == 7
    xw = [m for m in st['X']]
    tag = f"{o.kind}->{FLIP[o.kind]} q{o.qs[0]} t{o.time} bit{o.bit}"
    if pure and st['rX'] >= 1:
        good1.append(i)
        print('K1', tag, 'X(V)=', [lin.fmt(m) for m in xw], 'inC2', all(m in lin.C2 for m in xw))
    elif st['rX'] or not st['B0L'] or st['rX'] + st['rZ'] != 7:
        print('  ', tag, 'B0L', st['B0L'], 'rX', st['rX'], 'rZ', st['rZ'])
print('k1 count', len(good1))
for i, j in itertools.combinations(good1, 2):
    st = run([i, j])
    if st['B0L'] and st['rX'] == 2 and st['rZ'] == 5:
        print('K2', [f"q{ops[k].qs[0]}t{ops[k].time}" for k in (i, j)], [lin.fmt(m) for m in st['X']])
