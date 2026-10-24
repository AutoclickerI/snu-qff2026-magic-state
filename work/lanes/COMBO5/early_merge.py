#!/usr/bin/env python3
"""Release-aware Steane suffix scheduler.

Each reset/pivot initialization and each CNOT is a unit job.  Jobs are ordered
only by the per-cell dependencies of the data routes and block encoders, so
independent B+C work can occupy cells which the cultivation prefix never uses.
CP-SAT minimizes the first round step subject to these dependencies.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

from ortools.sat.python import cp_model

ROOT = Path("/home/jihoon/competitions/quantumn")
sys.path.insert(0, str(ROOT / "work"))
sys.path.insert(0, str(ROOT / "work" / "lanes" / "DR"))
import tprep.noise as tn  # noqa: E402
import tprep.qasm as tq  # noqa: E402
from steane_full import GENS, LAYOUTS, MOVES, PRE_DETECTORS, PREFIX, CUT  # noqa: E402

QRE = re.compile(r"q\[(\d+)\]")


def prefix_steps():
    raw = Path(PREFIX).read_text().split("\n")[:CUT]
    head = [l for l in raw if l.startswith(("OPENQASM", "include", "qreg"))]
    text = "\n".join(raw) + "\n"
    stim, labels, errors = tq.convert(text)
    assert not errors, errors
    prog, steps, _ = tn.schedule(stim)
    k_step = {}
    for ins, st in zip(prog, steps):
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
    for i, (s, st) in enumerate(stmts):
        if st is not None:
            continue
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


def make_jobs(preps, lay, moves):
    jobs = []
    def add(stmts, qs, tag):
        jobs.append(dict(stmts=stmts, qs=tuple(sorted(set(qs))), tag=tag))

    # A route is reset at every destination, then swapped in two CNOTs.
    for pi, path in enumerate(moves):
        for hi, (s, d) in enumerate(zip(path, path[1:])):
            add([f"reset q[{d}];"], [d], f"move{pi}.{hi}.reset")
            add([f"cx q[{s}],q[{d}];"], [s, d], f"move{pi}.{hi}.fwd")
            add([f"cx q[{d}],q[{s}];"], [s, d], f"move{pi}.{hi}.back")

    for k in ("a", "bc"):
        p = preps[k]
        cells = list(lay["b"] + lay["c"] if k == "bc" else lay[k])
        first = {}
        for t, layer in enumerate(p["ops"]):
            for u, v in layer:
                first.setdefault(u, t)
                first.setdefault(v, t)
        for q in cells:
            first.setdefault(q, 0)
        # Initialization is one native reset/RX unit.  Pivots include h.
        for q in sorted(first, key=first.get):
            add([f"reset q[{q}];"] + ([f"h q[{q}];"] if q in p["pivots"] else []), [q], f"{k}.init.{q}")
        # Keep each cell's layer order, while allowing disjoint edges to run independently.
        for t, layer in enumerate(p["ops"]):
            for u, v in layer:
                add([f"cx q[{u}],q[{v}];"], [u, v], f"{k}.cx.{t}.{u}.{v}")
    return jobs


def solve_schedule(jobs, release, round_q, min_r=33, max_r=120, seconds=120, workers=8):
    m = cp_model.CpModel()
    starts = [m.NewIntVar(0, max_r, f"s{i}") for i in range(len(jobs))]
    ends = [m.NewIntVar(1, max_r + 1, f"e{i}") for i in range(len(jobs))]
    ivals = [m.NewIntervalVar(starts[i], 1, ends[i], f"j{i}") for i in range(len(jobs))]
    byq = {q: [] for q in range(36)}
    for i, j in enumerate(jobs):
        for q in j["qs"]:
            byq[q].append(i)
            m.Add(starts[i] >= release.get(q, 0))
    for q, js in byq.items():
        if js:
            m.AddNoOverlap([ivals[i] for i in js])
            # Preserve the explicit construction order on each cell.  Jobs were
            # created in route order, then encoder layer order.
            for a, b in zip(js, js[1:]):
                m.Add(starts[b] >= ends[a])
    R = m.NewIntVar(min_r, max_r, "R")
    for q in round_q:
        for i in byq.get(q, []):
            m.Add(ends[i] <= R)
    m.Minimize(R)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = seconds
    s.parameters.num_workers = workers
    s.parameters.random_seed = 0
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(f"scheduler status {s.StatusName(st)}")
    best_r = s.Value(R)
    # With the minimum round step fixed, push every preparatory unit as late as
    # possible.  This is the idle-noise objective; the first solve is only the
    # timing feasibility pass.
    m.Add(R == best_r)
    m.ClearObjective()
    m.Maximize(sum(starts))
    st2 = s.Solve(m)
    if st2 not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(f"ALAP status {s.StatusName(st2)}")
    when = [s.Value(x) for x in starts]
    return when, best_r, s.StatusName(st2), s.WallTime()


def build(preps, layout, moves, seconds=120, workers=8):
    head, stmts = prefix_steps()
    release = {}
    by_step = {}
    for text, step in stmts:
        by_step.setdefault(step, []).append(text)
        for q in map(int, QRE.findall(text)):
            release[q] = max(release.get(q, 0), step + 1)
    jobs = make_jobs(preps, layout, moves)
    round_q = set(layout["a"] + layout["b"] + layout["c"] + layout["d"])
    when, R, status, wall = solve_schedule(jobs, release, round_q, seconds=seconds, workers=workers)
    for j, t in zip(jobs, when):
        by_step.setdefault(t, []).extend(j["stmts"])

    n = 14
    bits = {}
    r0, r1, r2 = [], [], []
    d, a, b, c = layout["d"], layout["a"], layout["b"], layout["c"]
    for i in range(7):
        r0 += [f"cx q[{d[i]}],q[{a[i]}];", f"cx q[{b[i]}],q[{c[i]}];"]
    for k, cells in (("a", a), ("c", c)):
        for i, q in enumerate(cells):
            bits[(k, i)] = n
            r1.append(f"measure q[{q}] -> c[{n}];")
            n += 1
    for i in range(7):
        r1.append(f"cx q[{b[i]}],q[{d[i]}];")
    for i, q in enumerate(b):
        bits[("b", i)] = n
        r2 += [f"h q[{q}];", f"measure q[{q}] -> c[{n}];"]
        n += 1
    by_step.setdefault(R, []).extend(r0)
    by_step.setdefault(R + 1, []).extend(r1)
    by_step.setdefault(R + 2, []).extend(r2)
    used = sorted({int(x) for vals in by_step.values() for s_ in vals for x in QRE.findall(s_)})
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
    dets.append(" ".join(f"c[{bits[("c", i)]}]" for i in range(7)))
    out += [f"// DETECTOR {x}" for x in dets]
    return "\n".join(out) + "\n", list(d), R, max(release.values()), status, wall


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout", default="L5")
    ap.add_argument("--a", required=True)
    ap.add_argument("--bc", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seconds", type=float, default=120)
    ap.add_argument("--workers", type=int, default=8)
    z = ap.parse_args()
    preps = {"a": json.loads(Path(z.a).read_text()), "bc": json.loads(Path(z.bc).read_text())}
    layout, moves = LAYOUTS[z.layout], MOVES[z.layout]
    text, data, R, pre_end, status, wall = build(preps, layout, moves, z.seconds, z.workers)
    Path(z.out + ".qasm").write_text(text)
    Path(z.out + ".json").write_text(json.dumps({"data_qubits": data, "layout": z.layout,
        "R": R, "pre_end": pre_end, "solver": status, "solver_wall": wall,
        "source": "EARLY/early_merge.py"}, indent=2) + "\n")
    print(z.out, "R", R, "pre_end", pre_end, "status", status, "wall", wall,
          "cx", text.count("cx "), flush=True)


if __name__ == "__main__":
    main()
