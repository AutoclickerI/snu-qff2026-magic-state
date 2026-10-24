#!/usr/bin/env python
"""Apply ACHECK's zero-CX block-A edits to another base, keeping its schedule as close as possible.

    port_acheck.py <base stem> <out stem> [edits]   (edits: comma list of q1,q16,c2,c9,c15; default all)

Edits (ACHECK verify_2_9_15): reuse q1's postselected MX state instead of its re-initialisation, measure-init q16,
and an MX check right after the RX initialisation of q2, q9 and q15 (each with its own detector). Every operation
keeps its native step where possible: a CP-SAT re-timer minimises the total step change with the round fixed.
"""
import json
import sys
from pathlib import Path

ACHECK = Path(__file__).resolve().parents[1] / "ACHECK"
sys.path.insert(0, str(ACHECK))
import common as C  # noqa: E402
from ortools.sat.python import cp_model  # noqa: E402

A = [1, 14, 8, 9, 2, 16, 15]


def retime_keep(units, old, R):
    m = cp_model.CpModel()
    ts = [m.NewIntVar(0, 90, f"t{i}") for i in range(len(units))]
    per = {}
    for i, u in enumerate(units):
        for q in u.qs:
            per.setdefault(q, []).append(i)
        if old[i] >= R:
            m.Add(ts[i] == old[i])
        else:
            m.Add(ts[i] < R)
    for seq in per.values():
        for i, j in zip(seq, seq[1:]):
            m.Add(ts[j] > ts[i])
    dev = []
    for i, t in enumerate(ts):
        d = m.NewIntVar(0, 90, f"d{i}")
        m.AddAbsEquality(d, t - old[i])
        dev.append(d)
    m.Minimize(sum(dev))
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    s.parameters.max_time_in_seconds = 60
    st = s.Solve(m)
    assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), "re-timing infeasible"
    return [s.Value(t) for t in ts], int(s.ObjectiveValue())


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    edits = set((sys.argv[3] if len(sys.argv) > 3 else "q1,q16,c2,c9,c15").split(","))
    text = src.with_suffix(".qasm").read_text()
    meta = json.loads(src.with_suffix(".json").read_text())
    R = meta["R"]
    h, raw, tail = C.S.qasm_ops(text)
    us = C.S.fold_units(raw)
    old = C.native_times(text, us)
    used = {int(b) for line in text.splitlines() for b in __import__("re").findall(r"c\[(\d+)\]", line)}
    init = {}
    for q in A:
        cand = [i for i, u in enumerate(us) if old[i] < R and u.qs == (q,) and u.name in ("RESET", "RX")]
        if cand:
            init[q] = max(cand)
    if "q16" in edits and us[init[16]].name != "RESET" if 16 in init else "q16" in edits:
        print("q16 has no reset to replace; skipping that edit")
        edits.discard("q16")
    if "q1" in edits:
        prev = max(j for j, u in enumerate(us[:init[1]]) if 1 in u.qs)
        assert us[prev].name == "MX", us[prev].name
        us[prev] = C.unit(us[prev].lines + ["h q[1];"])
    for e in edits:
        if e.startswith("c"):
            assert us[init[int(e[1:])]].name == "RX", (e, us[init[int(e[1:])]].name)
    bits = iter(b for b in range(256) if b not in used)
    uu, tt = [], []
    for i, (u, t) in enumerate(zip(us, old)):
        if "q1" in edits and i == init[1]:
            continue
        if "q16" in edits and i == init[16]:
            b = next(bits)
            u = C.unit([f"measure q[16] -> c[{b}];"])
            tail.append(f"// DETECTOR c[{b}]")
        uu.append(u)
        tt.append(t)
        if i in [init[int(e[1:])] for e in edits if e.startswith("c")]:
            q, b = u.qs[0], next(bits)
            uu.append(C.unit([f"h q[{q}];", f"measure q[{q}] -> c[{b}];", f"h q[{q}];"]))
            tt.append(t + 1)
            tail.append(f"// DETECTOR c[{b}]")
    ts, moved = retime_keep(uu, tt, R)
    C.HERE = out.parent
    p = C.emit(out.name, uu, ts, tail, dict(R=R, source=str(src), method="ACHECK verify_2_9_15 edits", edits=sorted(edits), steps_moved=moved))
    print(p, "R", R, "steps moved", moved)


if __name__ == "__main__":
    main()
