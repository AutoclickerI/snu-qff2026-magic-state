"""Single-qubit (and pair) stabilizers of the T->I surrogate state after each tick, for live qubits."""
import sys, re
import stim
sys.path.insert(0, '.')
from qedit import load
from gadgets import read, status
c = load(sys.argv[1]); t0, t1 = int(sys.argv[2]), int(sys.argv[3])
st = status(read(sys.argv[1]))
QRE = re.compile(r'q\[(\d+)\]')
sim = stim.TableauSimulator(); sim.set_num_qubits(36)
for t in range(len(c.segs)):
    for g in c.segs[t]:
        for ln in g:
            s = ln.strip(); n = s.split()[0]; qs = [int(x) for x in QRE.findall(s)]
            if n == 'reset': sim.reset(*qs)
            elif n == 'h': sim.h(*qs)
            elif n == 'cx': sim.cnot(*qs)
            elif n == 'measure': sim.measure(qs[0])
    if t < t0 or t > t1: continue
    out = []
    for q in range(36):
        if t + 1 >= len(st[q]) or st[q][t + 1] in ('dead', 'pre', 'prem'): continue
        for P in 'XZY':
            p = stim.PauliString(36); p[q] = P
            v = sim.peek_observable_expectation(p)
            if v != 0:
                out.append(f'{P}{q}{"+" if v > 0 else "-"}')
    print(t, ' '.join(out))
