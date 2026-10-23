"""Merge the Steane-type round into the tail of the v11 pre-stage on the judge's own time steps.

The pre-stage keeps the step of every statement in the judge's ASAP schedule. Data moves and block
preparations are scheduled as late as possible before the round start R (so blocks idle little),
each cell only after the pre-stage has released it; R is the smallest feasible start. The circuit
is written one time step per barrier-separated layer, so the judge reproduces these steps.

    python merge.py <layout name | layout.json> <preps.json | a=f.json,bc=g.json | - (preps in layout.json)> <out stem> [order, e.g. a,bc]
"""
import json
import os
import re
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import tprep.noise as tn  # noqa: E402
import tprep.qasm as tq  # noqa: E402
from steane_full import GENS, LAYOUTS, MOVES, PRE_DETECTORS, PREFIX, CUT  # noqa: E402

QRE = re.compile(r"q\[(\d+)\]")


def prefix_steps():
    """[(statement, step)] for the pre-stage statements, and the header lines."""
    raw = open(PREFIX).read().split("\n")[:CUT]
    head = [l for l in raw if l.startswith(("OPENQASM", "include", "qreg"))]
    text = "\n".join(raw) + "\n"
    stim, labels, errors = tq.convert(text)
    assert not errors, errors
    prog, steps, gaps = tn.schedule(stim)
    # stim instruction j -> its QASM statement number k (1-based over statements)
    k_step = {}
    lines = [l for l in stim.splitlines() if l.strip()]
    for j, (ins, st) in enumerate(zip(prog, steps)):
        lab = labels[ins.line_no - 1]
        m = re.match(r"instruction (\d+) ", lab)
        if m and st:
            k_step[int(m.group(1))] = st[0][1]
    stmts, k = [], 0
    for line in raw:
        s = line.split("//")[0].strip()
        if not s or s.startswith(("OPENQASM", "include", "qreg", "creg")):
            continue
        k += 1
        if s.startswith("barrier"):
            continue
        stmts.append([s, k_step.get(k)])
    # statements the judge folds away (h before a native MX, h after a reset) take their partner's step
    for i, (s, st) in enumerate(stmts):
        if st is None:
            q = QRE.findall(s)[0]
            nxt = next((t for t in stmts[i + 1:] if QRE.findall(t[0])[:1] == [q] and t[1] is not None), None)
            prv = next((t for t in reversed(stmts[:i]) if QRE.findall(t[0])[:1] == [q] and t[1] is not None), None)
            if s.startswith("h") and prv and prv[0].startswith("reset"):
                stmts[i][1] = prv[1]
            elif nxt:
                stmts[i][1] = nxt[1]
            else:
                stmts[i][1] = prv[1]
    return head, stmts


def suffix_jobs(preps, order, lay, moves):
    """Suffix operations as a list of (statements, qubits) units in dependency order per qubit; each
    unit runs in one time step. Returns units and the index range of the round."""
    units = []
    for path in moves:
        for s, d in zip(path, path[1:]):
            units.append(([f"reset q[{d}];"], [d]))
            units.append(([f"cx q[{s}],q[{d}];"], [s, d]))
            units.append(([f"cx q[{d}],q[{s}];"], [s, d]))
    for k in order:
        if k not in preps:
            continue
        ops, piv = preps[k]["ops"], preps[k]["pivots"]
        cells = lay["b"] + lay["c"] if k == "bc" else lay[k]
        first = {}
        for t, l in enumerate(ops):
            for u, v in l:
                first.setdefault(u, t)
                first.setdefault(v, t)
        for q in cells:
            first.setdefault(q, 0)
        for q in sorted(first, key=first.get):
            units.append(([f"reset q[{q}];"] + ([f"h q[{q}];"] if q in piv else []), [q]))
        for l in ops:
            for u, v in l:
                units.append(([f"cx q[{u}],q[{v}];"], [u, v]))
    return units


def build(preps, order, lay, moves):
    head, stmts = prefix_steps()
    release = {}                                   # cell -> first step it is free after the pre-stage
    for s, st in stmts:
        for q in map(int, QRE.findall(s)):
            release[q] = max(release.get(q, 0), st + 1)
    units = suffix_jobs(preps, order, lay, moves)
    # per-qubit order of units; ALAP: latest step for each unit given the round at R
    a, b, c, d = lay["a"], lay["b"], lay["c"], lay["d"]
    round_q = set(a) | set(b) | set(c) | set(d)

    def alap(R):
        latest = {q: R for q in round_q}           # every round qubit is busy from step R
        when = [None] * len(units)
        for i in range(len(units) - 1, -1, -1):
            sts, qs = units[i]
            t = min(latest.get(q, R) for q in qs) - 1
            when[i] = t
            for q in qs:
                latest[q] = t
        ok = all(when[i] >= max(release.get(q, 0) for q in units[i][1]) for i in range(len(units)))
        return ok, when
    R = max(release.values())
    while not alap(R)[0]:
        R += 1
    _, when = alap(R)
    by_step = {}
    for s, st in stmts:
        by_step.setdefault(st, []).append(s)
    for (sts, qs), t in zip(units, when):
        by_step.setdefault(t, []).extend(sts)
    n = 14
    bits = {}
    r0, r1, r2 = [], [], []
    for i in range(7):
        r0 += [f"cx q[{d[i]}],q[{a[i]}];", f"cx q[{b[i]}],q[{c[i]}];"]
    for k, cells in (("a", a), ("c", c)):
        for i in range(7):
            bits[(k, i)] = n
            r1.append(f"measure q[{cells[i]}] -> c[{n}];")
            n += 1
    for i in range(7):
        r1.append(f"cx q[{b[i]}],q[{d[i]}];")
    for i in range(7):
        bits[("b", i)] = n
        r2 += [f"h q[{b[i]}];", f"measure q[{b[i]}] -> c[{n}];"]
        n += 1
    by_step.setdefault(R, []).extend(r0)
    by_step.setdefault(R + 1, []).extend(r1)
    by_step.setdefault(R + 2, []).extend(r2)
    used = sorted({int(x) for v in by_step.values() for s in v for x in QRE.findall(s)})
    bar = "barrier " + ",".join(f"q[{q}]" for q in used) + ";"
    out = head + [f"creg c[{n}];"]
    for t in range(min(by_step), R + 3):
        if t == R:
            out.append("// region round")
        out += by_step.get(t, []) + [bar]
    out = out[:-1]
    dets = list(PRE_DETECTORS)
    for k in "abc":
        for S in GENS:
            dets.append(" ".join(f"c[{bits[(k, i)]}]" for i in S))
    dets.append(" ".join(f"c[{bits[('c', i)]}]" for i in range(7)))
    out += [f"// DETECTOR {x}" for x in dets]
    return "\n".join(out) + "\n", list(d), R, max(release.values())


if __name__ == "__main__":
    # layout: a name in steane_full.LAYOUTS, or a json {"d","a","b","c","moves","preps"?}
    name, src = sys.argv[1], sys.argv[2]
    order = sys.argv[4].split(",") if len(sys.argv) > 4 else ["a", "b", "c"]
    if name.endswith(".json"):
        spec = json.load(open(name))
        lay, moves = spec, spec["moves"]
    else:
        lay, moves = LAYOUTS[name], MOVES[name]
    if src == "-":
        preps = spec["preps"]
    elif src.endswith(".json"):
        preps = json.load(open(src))
    else:                                   # comma list of block=file
        preps = {kv.split("=")[0]: json.load(open(kv.split("=")[1])) for kv in src.split(",")}
    text, data, R, pre_end = build(preps, order, lay, moves)
    open(sys.argv[3] + ".qasm", "w").write(text)
    json.dump({"data_qubits": data, "source": f"merge.py {name} {src} {order}"}, open(sys.argv[3] + ".json", "w"))
    print(sys.argv[3], "written; pre-stage ends at step", pre_end, "round starts at", R)
