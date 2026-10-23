#!/usr/bin/env python
"""SCHED's exact quadratic scheduler (lanes/SCHED/schedule.py) on any circuit.

    sched_any.py <in stem> <out stem> [--iterations 20000] [--seed S] [--max-a1 0.66]
"""
import argparse
import json
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "SCHED"))
import schedule as S  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--iterations", type=int, default=20000)
ap.add_argument("--seed", type=int, default=20261024)
ap.add_argument("--max-a1", type=float, default=0.66)
a = ap.parse_args()
source = open(a.src + ".qasm").read()
data = json.load(open(a.src + ".json"))["data_qubits"]
header, raw, suffix = S.qasm_ops(source)
units = S.fold_units(raw)
seed_times = S.source_times(source, units)
quad = S.Quadratic(source, data, units, header, suffix)
assert quad.feasible(seed_times)
base = quad.score(seed_times)
print("base", {k: base[k] for k in ("loss2", "A1", "exp_minus_A1")}, "depth", max(seed_times) + 1, flush=True)
best_times, best = S.optimize(quad, seed_times, max(1, a.iterations // 10), a.seed, a.iterations, max_a1=a.max_a1)
open(a.out + ".qasm", "w").write(S.emit(header, units, best_times, suffix))
json.dump({"data_qubits": data, "source": f"{a.src} + SCHED exact quadratic scheduler (lanes/MAIN/sched_any.py, seed {a.seed})"},
          open(a.out + ".json", "w"))
print("best", {k: best[k] for k in ("loss2", "A1", "exp_minus_A1")}, "depth", max(best_times) + 1, flush=True)
