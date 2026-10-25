"""For each data qubit idle tick, show neighbours' status and known single-qubit state (surrogate)."""
import sys, re
import stim
from elements import *
from qedit import load
stem = sys.argv[1]; lo = int(sys.argv[2])
base = read(stem); st = status(base); T = depth(base)
qc = load(stem)
QRE = re.compile(r'q\[(\d+)\]')
sim = stim.TableauSimulator(); sim.set_num_qubits(36)
known = {}
for t in range(len(qc.segs)):
    for h in range(36):
        for P in 'ZX':
            p = stim.PauliString(36); p[h] = P
            v = sim.peek_observable_expectation(p)
            if v: known[(h, t)] = P + ('+' if v > 0 else '-')
    for g in qc.segs[t]:
        for ln in g:
            s = ln.strip(); n = s.split()[0]; qs = [int(x) for x in QRE.findall(s)]
            if n == 'reset': sim.reset(*qs)
            elif n == 'h': sim.h(*qs)
            elif n == 'cx': sim.cnot(*qs)
            elif n == 'measure': sim.measure(qs[0])
for d in [0, 20, 7, 10, 3, 22, 21]:
    for t in range(lo, T - 1):
        if st[d][t] != 'live': continue
        nb = []
        for h in ADJ[d]:
            ops = ops_at(base, h, t)
            o = ' '.join(ops[0]['lines'])[:12] if ops else st[h][t]
            nb.append(f"{h}:{o}:{known.get((h, t), '')}")
        print(f'q{d} t{t}', ' | '.join(nb))
