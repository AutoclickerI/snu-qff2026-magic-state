#!/usr/bin/env python3
"""Short exact-engine speed probe for a QFF submission.

Usage::

    .venv/bin/python work/lanes/XTIM/speed_predict.py work/lanes/MAIN/v25k

The probe uses the judge's STANDARD noise model and the exact sampler.  It times
the compiled sampler only (repeated batches), so parser/reference setup is
not mistaken for per-shot work.  The 20 s/1e6 threshold is the repository's
submission gate; pass ``--shots`` to trade probe time for noise in the estimate.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import statistics
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "upstream" / "snu-qff2026-problem"))

# Keep reference-cache writes inside this lane.  The predictor itself does not
# modify the installed xtim package or the candidate files.
import xtim  # noqa: E402

xtim.cache_dir = str(Path(__file__).resolve().parent / ".xtim_cache")

from tprep.noise import STANDARD, apply_noise  # noqa: E402
from tprep.qasm import to_stim  # noqa: E402

_check = importlib.import_module("tprep.check")


def _stem_paths(stem: str) -> tuple[Path, Path]:
    p = Path(stem)
    qasm = p if p.suffix == ".qasm" else p.with_suffix(".qasm")
    meta = qasm.with_suffix(".json")
    if not qasm.is_file():
        raise FileNotFoundError(qasm)
    if not meta.is_file():
        raise FileNotFoundError(meta)
    return qasm, meta


def _features(stim_text: str) -> dict[str, int]:
    rows = []
    for line in stim_text.splitlines():
        body = line.split("#", 1)[0].strip()
        if body:
            rows.append(body.split())
    t_positions = [i for i, r in enumerate(rows) if r and r[0] in {"T", "T_DAG"}]
    mx_positions = [i for i, r in enumerate(rows) if r and r[0] in {"MX", "MRX"}]
    return {
        "instructions": len(rows),
        "t_gates": len(t_positions),
        "mx_records": len(mx_positions),
        "mx_after_first_t": sum(i > min(t_positions) for i in mx_positions) if t_positions else 0,
        "mx_after_last_t": sum(i > max(t_positions) for i in mx_positions) if t_positions else 0,
        "detectors": sum(bool(r and r[0] == "DETECTOR") for r in rows),
    }


def predict(stem: str, shots: int = 50_000, repeats: int = 2) -> dict:
    qasm_path, meta_path = _stem_paths(stem)
    qasm = qasm_path.read_text(encoding="utf-8")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    stim_text, errors = to_stim(qasm)
    if errors:
        raise ValueError("QASM conversion failed: " + "; ".join(errors))

    features = _features(stim_text)
    noisy = apply_noise(stim_text, 1e-3, STANDARD)
    data = [int(q) for q in meta["data_qubits"]]
    # All incumbent circuits use the automatically found zero frame.  The tail
    # is included because it is part of the judge run and contributes a fixed
    # amount of compiled work.  If a future candidate has an incompatible tail,
    # fall back to timing its submitted body rather than refusing the prediction.
    try:
        body = xtim.Circuit(noisy)
        n_pre = body.num_measurements
        plan = _check.Plan(data, {"X": (0, []), "Z": (0, [])}, (), n_pre)
        circuit = xtim.Circuit(noisy + "\n" + plan.tail)
    except Exception:
        circuit = xtim.Circuit(noisy)
    sampler = circuit.compile_detector_sampler(seed=0, engine="exact")

    # Remove one-time sampler state effects before collecting timed batches.
    sampler.sample(64, return_expectations=True, return_measurements=True, bit_packed=True)
    timings = []
    for _ in range(repeats):
        start = time.perf_counter()
        sampler.sample(shots, return_expectations=True, return_measurements=True, bit_packed=True)
        timings.append(time.perf_counter() - start)
    per_million = statistics.median(timings) * 1_000_000.0 / shots
    result = {
        "stem": str(qasm_path),
        "shots": shots,
        "repeats": repeats,
        "seconds": timings,
        "median_seconds_per_1e6": per_million,
        "classification": "SLOW" if per_million >= 20.0 else "FAST",
        "measurements": circuit.num_measurements,
        "detectors": circuit.num_detectors,
        **features,
    }
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("stem", help="candidate stem, with or without .qasm")
    ap.add_argument("--shots", type=int, default=50_000,
                    help="shots per timed batch (default: 50000)")
    ap.add_argument("--repeats", type=int, default=2,
                    help="timed batches (default: 2)")
    args = ap.parse_args()
    if args.shots <= 0 or args.repeats <= 0:
        ap.error("--shots and --repeats must be positive")
    print(json.dumps(predict(args.stem, args.shots, args.repeats), sort_keys=True))


if __name__ == "__main__":
    main()
