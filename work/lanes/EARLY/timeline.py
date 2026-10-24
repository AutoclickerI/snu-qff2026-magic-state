"""Per-qubit native timeline of a QASM candidate under the judge's schedule.

usage: timeline.py <stem> [--gaps]
Prints, for each used qubit, the op at every native step (judge schedule: ASAP in written order,
barriers hold, h folded into MX/RX). Legend: R/RX resets, M/MX measures, Cxx>yy control, <xx target,
T/t T/Tdg, '.' idle (charged), ' ' not yet live / dead.
"""
import sys, json
sys.path.insert(0, "/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem")
from tprep.qasm import convert
from tprep.noise import schedule


def timeline(stem):
    text = open(stem + ".qasm").read()
    stim, labels, errors = convert(text)
    assert not errors, errors
    prog, steps, gaps = schedule(stim)
    ops = {}  # (q, t) -> label
    for ins, groups in zip(prog, steps):
        for group, t in groups:
            if ins.name == "CX":
                c, x = group
                ops[(c, t)] = f"{x}<" if False else f"C{x}"
                ops[(x, t)] = f"X{c}"
            elif ins.name in ("DETECTOR",):
                pass
            else:
                for q in group:
                    ops[(q, t)] = {"R": "R", "RX": "RX", "M": "M", "MX": "MX", "H": "H", "T": "T",
                                   "T_DAG": "t", "S": "S", "I": "I", "X": "x", "Z": "z"}.get(ins.name, ins.name)
    end = max(t for (_, t) in ops) + 1
    return ops, end, gaps


def main():
    stem = sys.argv[1]
    ops, end, gaps = timeline(stem)
    meta = json.load(open(stem + ".json"))
    data = meta["data_qubits"]
    qs = sorted({q for q, _ in ops})
    idle = {}
    for i, q, t0, n in gaps:
        for t in range(t0, t0 + n):
            idle[(q, t)] = True
    print("step " + "".join(f"{t:>4}" for t in range(end)))
    for q in qs:
        row = []
        for t in range(end):
            s = ops.get((q, t))
            if s is None:
                s = "." if idle.get((q, t)) else ""
            row.append(f"{s:>4}")
        tag = f"D{data.index(q)}" if q in data else "  "
        print(f"q{q:<2}{tag:>2}" + "".join(row))
    print("end", end)


if __name__ == "__main__":
    main()
