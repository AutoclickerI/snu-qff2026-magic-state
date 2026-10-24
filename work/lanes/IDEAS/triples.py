"""Exact third-order weight-3 fault sets of a circuit, aggregated by (region, kind) of the three faults."""
import os, sys, json
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'EVAL'))
import exact2
from collections import defaultdict
ROLES = dict(D=[0, 20, 7, 10, 3, 22, 21], A=[1, 14, 8, 9, 2, 16, 15], B=[6, 26, 13, 11, 4, 23, 27], C=[12, 25, 19, 17, 5, 29, 28])
def role(q):
    for r, qs in ROLES.items():
        if q in qs: return r
    return 'H'
qasm = sys.argv[1]; procs = int(sys.argv[2])
text = open(qasm).read()
data = json.load(open(qasm.rsplit('.', 1)[0] + '.json'))['data_qubits']
ev = exact2.Eval(text, data)
r = exact2.run(ev, procs, third=True)
T3a, big3 = exact2.third_order(ev, procs)
print('loss2', r['loss'], 'T3a', T3a, 't3bc', r['t3bc'], 'loss3', T3a + r['t3bc'])
def cls(i):
    lab = ev.fault_label(i)
    f = ev.m.faults[i]
    ch = ev.m.chans[f['chan']]
    return lab
agg = defaultdict(float)
rows = []
for val, i, j, k in big3:
    labs = [ev.fault_label(x) for x in (i, j, k)]
    rows.append((val, labs))
rows.sort(key=lambda x: -x[0])
tot = sum(v for v, _ in rows)
print('captured', tot, 'of T3a', T3a)
json.dump([(v, l) for v, l in rows[:5000]], open(sys.argv[3], 'w'))
for v, l in rows[:80]:
    print(f'{v:.2e}', ' | '.join(l))
