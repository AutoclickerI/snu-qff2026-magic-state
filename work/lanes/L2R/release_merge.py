"""Release-aware LAYOUT2 suffix scheduler.

This keeps the cultivation prefix exactly as emitted by LAYOUT2/merge.py, but
schedules each move/prep CNOT as a one-step job.  Per-cell construction order
is preserved; disjoint cells are allowed to overlap.  The three-cell cat is
scheduled with the same late-check convention as the incumbent merger.
"""
import json, os, re, sys
from pathlib import Path
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = "1"
from ortools.sat.python import cp_model

ROOT = Path("/home/jihoon/competitions/quantumn")
sys.path.insert(0, str(ROOT / "work"))
sys.path.insert(0, str(ROOT / "work" / "lanes" / "LAYOUT2"))
import merge as base
from steane_full import GENS, PRE_DETECTORS

QRE = re.compile(r"q\[(\d+)\]")


def jobs_for(preps, lay, moves, cat):
    jobs = []
    def add(stmts, qs, tag):
        jobs.append(dict(stmts=stmts, qs=tuple(sorted(set(qs))), tag=tag))

    for pi, path in enumerate(moves):
        for hi, (s, d) in enumerate(zip(path, path[1:])):
            add([f"reset q[{d}];"], [d], f"move{pi}.{hi}.reset")
            add([f"cx q[{s}],q[{d}];"], [s, d], f"move{pi}.{hi}.fwd")
            add([f"cx q[{d}],q[{s}];"], [s, d], f"move{pi}.{hi}.back")

    for k, cells in (("a", lay["a"]), ("bc", lay["b"] + lay["c"])):
        p = preps[k]
        first = {}
        for t, layer in enumerate(p["ops"]):
            for u, v in layer:
                first.setdefault(u, t); first.setdefault(v, t)
        for q in cells: first.setdefault(q, 0)
        for q in sorted(first, key=lambda q: (first[q], q)):
            add([f"reset q[{q}];"] + ([f"h q[{q}];"] if q in p["pivots"] else []),
                [q], f"{k}.init.{q}")
        for t, layer in enumerate(p["ops"]):
            for u, v in layer:
                add([f"cx q[{u}],q[{v}];"], [u, v], f"{k}.cx.{t}.{u}.{v}")

    anc = cat["anc"]
    for q in anc:
        add([f"reset q[{q}];"] + ([f"h q[{q}];"] if q == anc[0] else []), [q], f"cat.init.{q}")
    for u, v in cat["tree"]:
        add([f"cx q[{u}],q[{v}];"], [u, v], f"cat.cx.{u}.{v}")
    return jobs


def schedule_jobs(jobs, release, round_q, cat_q, min_r=33, max_r=120):
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
            for u, v in zip(js, js[1:]):
                m.Add(starts[v] >= ends[u])
    R = m.NewIntVar(min_r, max_r, "R")
    for q in round_q:
        for i in byq.get(q, []):
            m.Add(ends[i] <= R)
    # The final cat CNOT may occupy step R; its first check is at R+1.
    for q in cat_q:
        for i in byq.get(q, []):
            m.Add(ends[i] <= R)
    # Lexicographic objective: earliest round first, then push every job as
    # late as possible to minimize idle noise.  The large coefficient keeps
    # the first objective exact.
    m.Minimize(10000 * R - sum(starts))
    s = cp_model.CpSolver()
    s.parameters.num_workers = 8
    s.parameters.max_time_in_seconds = 180
    s.parameters.random_seed = 0
    st = s.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError(s.StatusName(st))
    return [s.Value(x) for x in starts], s.Value(R), s.StatusName(st), s.WallTime()


def build(layout_path, a_path, bc_path, outstem):
    lay = json.loads(Path(layout_path).read_text())
    preps = {"a": json.loads(Path(a_path).read_text()), "bc": json.loads(Path(bc_path).read_text())}
    if isinstance(preps["a"], list): preps["a"] = preps["a"][0]
    if isinstance(preps["bc"], list): preps["bc"] = preps["bc"][0]
    head, stmts = base.prefix_steps()
    release = {}
    by_step = {}
    for text, step in stmts:
        by_step.setdefault(step, []).append(text)
        for q in map(int, QRE.findall(text)):
            release[q] = max(release.get(q, 0), step + 1)
    anc = lay["cat"]
    seen = {anc[0]}; tree = []
    while len(seen) < len(anc):
        e = next((u, v) for u in seen for v in anc if v not in seen and abs(u//6-v//6)+abs(u%6-v%6)==1)
        tree.append(e); seen.add(e[1])
    jobs = jobs_for(preps, lay, lay["moves"], {"anc": anc, "tree": tree})
    round_q = set(lay["a"] + lay["b"] + lay["c"] + lay["d"])
    when, R, status, wall = schedule_jobs(jobs, release, round_q, anc)
    for j, t in zip(jobs, when):
        by_step.setdefault(t, []).extend(j["stmts"])

    n = 14; bits = {}; r0, r1, r2 = [], [], []
    d, a, b, c = lay["d"], lay["a"], lay["b"], lay["c"]
    for i in range(7):
        r0 += [f"cx q[{d[i]}],q[{a[i]}];", f"cx q[{b[i]}],q[{c[i]}];"]
    for k, cells in (("a", a), ("c", c)):
        for i, q in enumerate(cells):
            bits[(k, i)] = n; r1.append(f"measure q[{q}] -> c[{n}];"); n += 1
    for i in range(7): r1.append(f"cx q[{b[i]}],q[{d[i]}];")
    for i, q in enumerate(b):
        bits[("b", i)] = n; r2 += [f"h q[{q}];", f"measure q[{q}] -> c[{n}];"]; n += 1
    checks = list(zip(anc, [a[i] for i in lay["M"]]))
    for u, v in checks: by_step.setdefault(R + 1, []).append(f"cx q[{u}],q[{v}];")
    cat_bits = []
    for q in anc:
        by_step.setdefault(R + 2, []).extend([f"h q[{q}];", f"measure q[{q}] -> c[{n}];"])
        cat_bits.append(n); n += 1
    by_step.setdefault(R, []).extend(r0)
    by_step.setdefault(R + 1, []).extend(r1)
    by_step.setdefault(R + 2, []).extend(r2)
    used = sorted({int(x) for vals in by_step.values() for s in vals for x in QRE.findall(s)})
    bar = "barrier " + ",".join(f"q[{q}]" for q in used) + ";"
    out = head + [f"creg c[{n}];"]
    for t in range(min(by_step), R + 3):
        if t == R: out.append("// region round")
        out += by_step.get(t, []) + [bar]
    out = out[:-1]
    dets = list(PRE_DETECTORS)
    for k in "abc":
        for S in GENS: dets.append(" ".join(f"c[{bits[(k, i)]}]" for i in S))
    dets.append(" ".join(f"c[{bits[('c', i)]}]" for i in range(7)))
    dets.append(" ".join(f"c[{x}]" for x in cat_bits))
    text = "\n".join(out + [f"// DETECTOR {x}" for x in dets]) + "\n"
    Path(outstem + ".qasm").write_text(text)
    Path(outstem + ".json").write_text(json.dumps({"data_qubits": d, "layout": layout_path,
        "A": a_path, "BC": bc_path, "R": R, "pre_end": max(release.values()),
        "solver": status, "solver_wall": wall, "cat": anc, "M": lay["M"],
        "cx": text.count("cx "), "source": "L2R release_merge.py"}, indent=2) + "\n")
    print(outstem, "R", R, "pre_end", max(release.values()), "status", status,
          "wall", wall, "cx", text.count("cx "), flush=True)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
