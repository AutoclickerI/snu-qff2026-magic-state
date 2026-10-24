"""List idle runs (start step, length) per qubit under the judge schedule: gaps.py <stem> [q ...]."""
import sys, json
sys.path.insert(0, "/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem")
from tprep.qasm import convert
from tprep.noise import schedule
stem = sys.argv[1]
qs = [int(x) for x in sys.argv[2:]]
stim, labels, errors = convert(open(stem + ".qasm").read())
prog, steps, gaps = schedule(stim)
runs = {}
for i, q, t0, n in gaps:
    runs.setdefault(q, []).append((t0, n))
for q in sorted(runs):
    if qs and q not in qs:
        continue
    print(q, sorted(runs[q]))
