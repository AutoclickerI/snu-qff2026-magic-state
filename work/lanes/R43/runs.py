"""Idle runs per qubit under the judge schedule. usage: runs.py <stem> [qubits...]"""
import sys, json
sys.path.insert(0, "/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem")
from tprep.qasm import convert
from tprep.noise import schedule

def runs(stem):
    stim, _, err = convert(open(stem + ".qasm").read())
    assert not err, err
    prog, steps, gaps = schedule(stim)
    out = {}
    for i, q, t0, n in gaps:
        out.setdefault(q, []).append((t0, n))
    return out

if __name__ == "__main__":
    stem = sys.argv[1]
    r = runs(stem)
    data = json.load(open(stem + ".json"))["data_qubits"]
    qs = [int(x) for x in sys.argv[2:]] or data
    for q in qs:
        print(q, sorted(r.get(q, [])))
