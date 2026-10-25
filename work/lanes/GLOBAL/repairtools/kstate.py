"""Known-state guard slots: at tick t, helper h idle with a known +1 Z (|0>) or X (|+>) single-qubit stabilizer (T->I
surrogate, state after tick t-1 and h untouched at t), neighbour q live and idle at t. Adds CX h->q (Z) or CX q->h (X),
a noiseless identity. usage: kstate.py <base stem> <prefix> [tmin]"""
import sys, re
import stim
from elements import *
from qedit import load
stem, prefix = sys.argv[1], sys.argv[2]
tmin = int(sys.argv[3]) if len(sys.argv) > 3 else 1
base = read(stem)
st = status(base)
T = depth(base)
Tq = set()
for o in base['ops']:
    if unit(o).name in ('T', 'TDG'):
        Tq |= set(unit(o).qs)
qc = load(stem)
QRE = re.compile(r'q\[(\d+)\]')
sim = stim.TableauSimulator(); sim.set_num_qubits(36)
known = {}
for t in range(len(qc.segs)):
    # state before tick t (after t-1)
    for h in range(36):
        for P in 'ZX':
            p = stim.PauliString(36); p[h] = P
            if sim.peek_observable_expectation(p) == 1:
                known[(h, t)] = P
    for g in qc.segs[t]:
        for ln in g:
            s = ln.strip(); n = s.split()[0]; qs = [int(x) for x in QRE.findall(s)]
            if n == 'reset': sim.reset(*qs)
            elif n == 'h': sim.h(*qs)
            elif n == 'cx': sim.cnot(*qs)
            elif n == 'measure': sim.measure(qs[0])
names = []
for (h, t), P in sorted(known.items(), key=lambda x: (x[0][1], x[0][0])):
    if t < tmin or t >= T - 1 or st[h][t] != 'live':
        continue
    if P == 'X' and h in Tq:
        continue
    for q in ADJ[h]:
        if st[q][t] != 'live':
            continue
        line = f'cx q[{h}],q[{q}];' if P == 'Z' else f'cx q[{q}],q[{h}];'
        c = add_ops(base, [(t, [line])])
        n = f'{prefix}__{h}{P}_{q}_{t}'
        try:
            save(c, n, desc=dict(kslot=dict(h=h, q=q, t=t, P=P)))
            names.append(n)
        except Exception as e:
            pass
(C / (prefix + '.list')).write_text(' '.join(names))
print(len(names), 'candidates')
