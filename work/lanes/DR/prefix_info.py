"""Layer structure of the v11 pre-stage (QASM lines 1..204): per cell its first and last layer, and
whether its last operation is a measurement; data qubits' last layer.

    python prefix_info.py
"""
import re

PREFIX = "/home/jihoon/competitions/quantumn/work/submissions/v11_A1i_alap45.qasm"
CUT = 204


def layers(path=PREFIX, cut=CUT):
    out, cur = [], []
    for line in open(path).read().split("\n")[:cut]:
        s = line.strip()
        if s.startswith(("OPENQASM", "include", "qreg", "creg")) or not s or s.startswith("//"):
            continue
        if s.startswith("barrier"):
            out.append(cur)
            cur = []
        else:
            cur.append(s)
    if cur:
        out.append(cur)
    return out


def usage(L):
    first, last, meas = {}, {}, {}
    for t, l in enumerate(L):
        for s in l:
            for q in map(int, re.findall(r"q\[(\d+)\]", s)):
                first.setdefault(q, t)
                last[q] = t
                meas[q] = s.startswith("measure")
    return first, last, meas


if __name__ == "__main__":
    L = layers()
    first, last, meas = usage(L)
    print("prefix layers", len(L))
    for q in sorted(first):
        print(f"cell {q:2d} ({q // 6},{q % 6}) first {first[q]:2d} last {last[q]:2d} {'measured' if meas[q] else ''}")
    unused = [q for q in range(36) if q not in first]
    print("never used", unused)
