#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Exact Steane encoder synthesis; see REPORT.md for the finite optimality domain.

Example (run long jobs with nice -n 5):
  .venv/bin/python work/lanes/EXENC/exenc.py --cells 1,14,8,9,2,16,15 \
      --type plus --helpers '' --extra 2 --out work/lanes/EXENC/prepA_L5_exact.json

The C++ engine is an implementation of the same exhaustive algorithm, not a
solver/heuristic fallback. Compilation, scratch, and all outputs stay in EXENC.
"""
import sys
sys.dont_write_bytecode = True

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "DR"))
import synth
from steane_full import GENS


def rows_for(kind):
    return GENS + ([[0, 1, 2]] if kind == "plus" else [])


def score(ops, pivots, cells, avail):
    """Integer fault weights in units p/15, with bins [Z_L, Z_L Z_0,...,Z_L Z_6].

    Match synth.dangerous_z's actual reset/idle semantics, including its omitted
    nonpivot reset flips and unused idle_after argument. No extra noise is added.
    """
    avail = sorted(set(avail) | set(cells) | {q for layer in ops for e in layer for q in e})
    first, last = {}, {}
    for t, layer in enumerate(ops):
        for u, v in layer:
            for q in (u, v):
                first.setdefault(q, t)
                last[q] = t
    for q in cells:
        first.setdefault(q, 0)
    z = {q: ((cells.index(q) + 1) | 8) if q in cells else 0 for q in avail}
    x = {q: cells.index(q) + 1 if q in cells else 0 for q in avail}
    weights = [0] * 8

    def add(zz, xx, w):
        if not xx and bool(zz & 8) != bool(zz & 7):
            weights[zz & 7] += w

    for t in range(len(ops) - 1, -1, -1):
        layer = ops[t]
        busy = {q for e in layer for q in e}
        for u, v in layer:
            for pu in range(4):  # I, X, Z, Y: bit 0 = X, bit 1 = Z
                for pv in range(4):
                    if pu or pv:
                        add((z[u] if pu & 2 else 0) ^ (z[v] if pv & 2 else 0),
                            (x[u] if pu & 1 else 0) ^ (x[v] if pv & 1 else 0), 1)
        for q in avail:
            if q in busy or first.get(q, len(ops)) >= t:
                continue
            if q not in cells and t > last.get(q, -1):
                continue
            add(0, x[q], 5)
            add(z[q], 0, 5)
            add(z[q], x[q], 5)
        for u, v in layer:
            z[v] ^= z[u]
            x[u] ^= x[v]
        for q in pivots:
            if first.get(q) == t:
                add(z[q], 0, 15)
    if not ops:
        for q in pivots:
            add(z[q], 0, 15)
    return weights


def verify(circuit, cells, kind, helpers):
    ops, pivots = circuit["ops"], circuit["pivots"]
    avail = sorted(set(cells + helpers))
    assert len(pivots) == len(rows_for(kind)) and len(set(pivots)) == len(pivots)
    assert set(pivots) <= set(avail)
    for layer in ops:
        assert layer
        assert len({q for e in layer for q in e}) == 2 * len(layer)
        assert all(u in avail and v in synth.nbrs(u) and v in avail for u, v in layer)
    assert synth.check(cells, rows_for(kind), avail, ops, pivots), circuit
    weights = score(ops, pivots, cells, avail)
    reference = synth.dangerous_z(ops, pivots, cells, avail)
    assert math.isclose(sum(weights) * 1e-3 / 15, reference, abs_tol=1e-15)
    if "danger_units" in circuit:
        assert circuit["danger_units"] == sum(weights), (circuit, weights)
    if "danger_vector_units" in circuit:
        assert circuit["danger_vector_units"] == weights, (circuit, weights)
    circuit.update(danger=reference, danger_units=sum(weights),
                   danger_vector_units=weights,
                   danger_pure_logical=weights[0] * 1e-3 / 15,
                   danger_per_qubit=[w * 1e-3 / 15 for w in weights[1:]],
                   cx=sum(map(len, ops)), depth=len(ops))
    return circuit


def baseline_check():
    cells = [1, 14, 8, 9, 2, 16, 15]
    baseline = json.loads((HERE.parent / "DR/prepA_L5_s7307.json").read_text())
    verify(baseline, cells, "plus", [])
    assert baseline["danger_units"] == 10
    return baseline


def output_path(value):
    p = Path(value)
    if not p.is_absolute() and p.parent == Path("."):
        p = HERE / p
    p = p.resolve()
    if not p.is_relative_to(HERE):
        raise ValueError(f"All writes must be inside {HERE}: {p}")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def compile_engine():
    src, binary = HERE / "exact.cpp", HERE / "exact"
    if not binary.exists() or binary.stat().st_mtime < src.stat().st_mtime:
        tmp = HERE / ".tmp"
        tmp.mkdir(exist_ok=True)
        subprocess.run(["g++", "-O3", "-std=c++20", "-pthread", "-Wall", "-Wextra",
                        str(src), "-o", str(binary)], check=True,
                       env={**os.environ, "TMPDIR": str(tmp)})
    return binary


def run(cells, kind, helpers, extra, out, workers=16, alternatives=True,
        enumerate_circuits=True, max_class=0):
    started = time.monotonic()
    if len(cells) != 7 or len(set(cells)) != 7:
        raise ValueError("--cells must list seven distinct cells in code-qubit order")
    if len(set(helpers)) != len(helpers) or set(helpers) & set(cells):
        raise ValueError("Helpers must be distinct from each other and from code cells")
    if any(q < 0 or q >= 36 for q in cells + helpers):
        raise ValueError("Cells must lie in the 6x6 grid (0..35)")
    if not 1 <= workers <= 16 or extra < 0:
        raise ValueError("workers must be 1..16 and extra must be nonnegative")
    out = output_path(out)
    baseline = baseline_check()
    binary = compile_engine()
    raw = out.with_name(out.stem + "_raw.json")
    request = " ".join(map(str, [len(cells + helpers), len(rows_for(kind)), extra,
                                workers, int(alternatives), int(enumerate_circuits),
                                max_class, *cells, *helpers])) + "\n"
    print(f"reference danger={baseline['danger']:.12g}; starting {out.stem}", flush=True)
    with raw.open("w") as f:
        subprocess.run([str(binary)], input=request, text=True, stdout=f, check=True)
    result = json.loads(raw.read_text())
    if result.get("unreachable"):
        result.update(cells=cells, helpers=helpers, type=kind,
                      runtime_seconds=time.monotonic() - started)
        out.with_name(out.stem + "_stats.json").write_text(json.dumps(result, indent=2) + "\n")
        return result
    if cells == [1, 14, 8, 9, 2, 16, 15] and not helpers and kind == "plus":
        assert result["min_cx"] <= 11
    for c in result["top"]:
        verify(c, cells, kind, helpers)
    for c in result["classes"]:
        if c.get("best"):
            verify(c["best"], cells, kind, helpers)
    verify(result["depth_optimal"], cells, kind, helpers)
    for c in result.get("verification_samples", []):
        verify(c, cells, kind, helpers)
    best = result["top"][0] if kind == "plus" and result["top"] else result["depth_optimal"]
    result.update(cells=cells, helpers=helpers, type=kind,
                  reference_danger=baseline["danger"],
                  reference_vector_units=baseline["danger_vector_units"],
                  runtime_seconds=time.monotonic() - started,
                  verification="Every emitted circuit passed synth.check, topology/layer checks, "
                               "and independent scoring against synth.dangerous_z.")
    out.write_text(json.dumps(best, indent=2) + "\n")
    out.with_name(out.stem + "_top.json").write_text(json.dumps(result["top"], indent=2) + "\n")
    out.with_name(out.stem + "_stats.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("min_cx", "min_depth", "min_depth_cx",
                                            "states", "runtime_seconds")}))
    print(f"best danger={best['danger']:.12g}, cx={best['cx']}, depth={best['depth']}", flush=True)
    return result


def numbers(values):
    return [int(s) for v in values for s in v.replace(",", " ").split()]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", nargs="+", required=True)
    ap.add_argument("--type", choices=("plus", "zero"), required=True)
    ap.add_argument("--helpers", nargs="*", default=[])
    ap.add_argument("--extra", type=int, default=2)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--no-alternatives", action="store_true",
                    help="Enumerate and score ASAP schedules only; explicitly recorded")
    ap.add_argument("--proof-only", action="store_true",
                    help="Prove minimum CX and depth, emit depth-then-CX optimum; no enumeration")
    ap.add_argument("--max-class", type=int, default=0,
                    help="Skip whole CX classes with more than this many canonical circuits (0=unlimited)")
    args = ap.parse_args()
    run(numbers(args.cells), args.type, numbers(args.helpers), args.extra, args.out,
        args.workers, not args.no_alternatives, not args.proof_only, args.max_class)


if __name__ == "__main__":
    main()
