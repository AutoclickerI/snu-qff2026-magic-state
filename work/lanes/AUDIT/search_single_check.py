import sys
sys.path.insert(0, '/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
import tprep
import random

qc = QuantumCircuit(7)
qc.h(0); qc.t(0); qc.h(1)
qc.cx(0,4); qc.cx(4,0); qc.cx(0,4); qc.cx(1,0)
qc.h(2); qc.cx(1,5); qc.cx(5,1); qc.cx(1,5); qc.cx(2,1)
qc.cx(4,5); qc.cx(5,2); qc.cx(2,4)
qc.h(3); qc.cx(5,6); qc.cx(4,3); qc.cx(3,5); qc.cx(5,4)
qc.cx(4,6); qc.cx(6,3); qc.cx(3,6); qc.cx(6,3)
cm = CouplingMap.from_grid(6, 6)

def neigh(q):
    r, c = divmod(q, 6)
    return {x for x in (q-1, q+1, q-6, q+6)
            if 0 <= x < 36 and abs(x//6-r) + abs(x%6-c) == 1}

def common(data, support):
    out = set(range(36)) - set(data)
    for i in support:
        out &= neigh(data[i])
    return out

supports = [{0,2,4,6}, {1,2,5,6}, {3,4,5,6}]
out = []
for seed in range(500):
    init = random.Random(seed).sample(range(36), 7)
    r = transpile(qc, coupling_map=cm, basis_gates=['h','t','cx'],
                  optimization_level=3, seed_transpiler=seed,
                  initial_layout=init)
    data = list(r.layout.final_index_layout()[:7])
    for si, support in enumerate(supports):
        centers = common(data, support)
        if not centers:
            continue
        anc = next(iter(centers))
        lines = tprep.submission_text(r).splitlines()
        qi = next(i for i, x in enumerate(lines) if x.startswith('qreg'))
        lines.insert(qi+1, 'creg c[1];')
        lines += [f'reset q[{anc}];', f'h q[{anc}];']
        lines += [f'cx q[{anc}],q[{data[i]}];' for i in sorted(support)]
        lines += [f'h q[{anc}];', 'measure q[%d] -> c[0];' % anc, '// DETECTOR c[0]']
        text = '\n'.join(lines) + '\n'
        rep = tprep.check(text, data, p=1e-3, shots=50000, seed=0)
        if rep.passed:
            row = (rep.score, rep.acceptance, r.count_ops().get('cx', 0), seed,
                   data, si, anc, text)
            out.append(row)
            print(row[:7], flush=True)
out.sort(key=lambda x: x[0])
print('BEST', [x[:7] for x in out[:20]])
if out:
    open('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/single_check_best.qasm','w').write(out[0][7])
