"""merge.py extended with block D (= `e`, |+_L>, control of CX e_i -> a_i one step before A couples to
the data, MX read at the data-coupling step).

    python merge_av.py <spec.json> <out stem>
spec: {"d","a","b","c","e": cells; "moves": [[path]]; "preps": {block: prep json path}; "order": "eabc"}
"""
import json
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR")
import merge as M  # noqa: E402
from steane_full import GENS, PRE_DETECTORS  # noqa: E402

QRE = M.QRE


def build(spec):
    lay, moves, order = spec, spec["moves"], spec["order"]
    preps = {k: json.load(open(f)) for k, f in spec["preps"].items()}
    head, stmts = M.prefix_steps()
    release = {}
    for s, st in stmts:
        for q in map(int, QRE.findall(s)):
            release[q] = max(release.get(q, 0), st + 1)
    a, b, c, d, e = (lay[k] for k in "abcde")
    n = 14
    bits = {}
    for i in range(7):
        bits[("e", i)] = n
        n += 1
    units = M.suffix_jobs(preps, "", lay, moves)
    for k in order:
        units += M.suffix_jobs({k: preps[k]}, k, lay, [])
        if k == "e":                                # D verifies A as soon as both exist; D's cells are then free
            for i in range(7):
                units.append(([f"cx q[{e[i]}],q[{a[i]}];"], [e[i], a[i]]))
            for i in range(7):
                units.append(([f"h q[{e[i]}];", f"measure q[{e[i]}] -> c[{bits[('e', i)]}];"], [e[i]]))
    early = set()
    round_q = set(a) | set(b) | set(c) | set(d)

    def alap(R):
        latest = {q: (R - 1 if q in early else R) for q in round_q}
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
    for k in "abce":
        for S in GENS:
            dets.append(" ".join(f"c[{bits[(k, i)]}]" for i in S))
    dets.append(" ".join(f"c[{bits[('c', i)]}]" for i in range(7)))
    dets.append(" ".join(f"c[{bits[('e', i)]}]" for i in range(7)))
    out += [f"// DETECTOR {x}" for x in dets]
    return "\n".join(out) + "\n", list(d), R, max(release.values())


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    text, data, R, pre_end = build(spec)
    open(sys.argv[2] + ".qasm", "w").write(text)
    json.dump({"data_qubits": data, "source": f"merge_av.py {sys.argv[1]}"}, open(sys.argv[2] + ".json", "w"))
    print(sys.argv[2], "written; pre-stage ends at step", pre_end, "round starts at", R)
