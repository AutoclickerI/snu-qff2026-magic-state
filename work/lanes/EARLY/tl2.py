import sys
sys.path.insert(0, ".")
from timeline import timeline
import json
stem = sys.argv[1]
ops, end, gaps = timeline(stem)
data = json.load(open(stem + ".json"))["data_qubits"]
idle = {}
for i, q, t0, n in gaps:
    for t in range(t0, t0 + n):
        idle[(q, t)] = 1
qs = sorted({q for q, _ in ops})
t0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
for q in qs:
    ent = []
    for t in range(t0, end):
        s = ops.get((q, t))
        if s: ent.append(f"{t}:{s}")
        elif idle.get((q, t)): ent.append(f"{t}:.")
    tag = f"D{data.index(q)}" if q in data else ""
    print(f"q{q}{tag}", " ".join(ent))
