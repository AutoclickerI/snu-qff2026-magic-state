"""Teleport-output round merged into the (relabelled) v11 pre-stage tail.

    python merge_tp.py <layout.json> <out stem>

layout.json: {"d","o","b","c": code-ordered cells (d_i ~ o_i ~ b_i ~ c_i), "map": {orig cell: placed cell},
"preps": {"o": {...}, "bc": {...}}, "order": ["o","bc"]}.  Round at R: CX o->d, CX b->c; R+1: Z-read D and C,
CX b->o; R+2: X-read B.  Output = O; FRAME_X = XOR of the 7 D bits.
"""
import json
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR")
import merge as mg  # noqa: E402
from steane_full import GENS, PRE_DETECTORS  # noqa: E402

QRE = mg.QRE


def build(lay):
    head, stmts = mg.prefix_steps()
    M = {int(k): v for k, v in lay["map"].items()}
    stmts = [[QRE.sub(lambda m: f"q[{M[int(m.group(1))]}]", s), st] for s, st in stmts]
    release = {}
    for s, st in stmts:
        for q in map(int, QRE.findall(s)):
            release[q] = max(release.get(q, 0), st + 1)
    o, b, c, d = lay["o"], lay["b"], lay["c"], lay["d"]
    units = mg.suffix_jobs({}, [], {}, lay["moves"])
    parts = {}
    st = lay.get("o_stage")
    parts["o"] = mg.suffix_jobs({"o": lay["preps"]["o"]}, ["o"], {"o": st or o}, [])
    if st:
        for i in range(7):
            parts["o"] += [([f"reset q[{o[i]}];"], [o[i]]), ([f"cx q[{st[i]}],q[{o[i]}];"], [st[i], o[i]]),
                           ([f"cx q[{o[i]}],q[{st[i]}];"], [st[i], o[i]])]
    parts["bc"] = mg.suffix_jobs({"bc": lay["preps"]["bc"]}, ["bc"], {"b": b, "c": c}, [])
    for k in lay["order"]:
        units += parts[k]
    round_q = set(o) | set(b) | set(c) | set(d)

    def alap(R):
        latest = {q: R for q in round_q}
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
        r0 += [f"cx q[{o[i]}],q[{d[i]}];", f"cx q[{b[i]}],q[{c[i]}];"]
    for k, cells in (("d", d), ("c", c)):
        for i in range(7):
            bits[(k, i)] = n
            r1.append(f"measure q[{cells[i]}] -> c[{n}];")
            n += 1
    for i in range(7):
        r1.append(f"cx q[{b[i]}],q[{o[i]}];")
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
    for k in "dbc":
        for S in GENS:
            dets.append(" ".join(f"c[{bits[(k, i)]}]" for i in S))
    dets.append(" ".join(f"c[{bits[('c', i)]}]" for i in range(7)))
    out += [f"// DETECTOR {x}" for x in dets]
    out.append("// FRAME_X(0) " + " ".join(f"c[{bits[('d', i)]}]" for i in range(7)))
    out.append("// FRAME_Z(0)")
    return "\n".join(out) + "\n", list(o), R, max(release.values())


if __name__ == "__main__":
    lay = json.load(open(sys.argv[1]))
    text, data, R, pre_end = build(lay)
    open(sys.argv[2] + ".qasm", "w").write(text)
    json.dump({"data_qubits": data, "source": f"merge_tp.py {sys.argv[1]}"}, open(sys.argv[2] + ".json", "w"))
    print(sys.argv[2], "written; pre-stage ends at step", pre_end, "round starts at", R)
