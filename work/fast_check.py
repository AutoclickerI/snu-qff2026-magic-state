"""The official tprep.check score, computed in parallel and bit-identical to the sequential run.

tprep's _sample splits the shots into 10**6-shot chunks; chunk k uses seed + k and contributes the
sums (kept, corrected, total, total_sq). Those sums are added in chunk order here exactly as in
tprep/check.py, so the score, sem and acceptance equal tprep.check(..., shots, seed) to the last
bit (verified against the sequential run and the server for v6).

    python fast_check.py <qasm> <json with data_qubits> [shots] [procs]
    from fast_check import check; rep = check(text, data_qubits, shots=10**8, procs=25)
"""
import multiprocessing as mp
import sys

import numpy as np

import tprep
import tprep.check  # noqa: F401  (tprep/__init__ rebinds tprep.check to the function)
tc = sys.modules["tprep.check"]

_STATE = {}


def _chunk(k):
    circuit, plan, seed, shots = _STATE["args"]
    start = k * tc.CHUNK
    n_syn = 2 * len(tc.SUPPORTS)
    n_meas = circuit.num_measurements
    beta = np.array(list(tc.TARGET.values()))
    dets, exps, meas = circuit.compile_detector_sampler(seed=seed + k, engine="exact").sample(
        min(tc.CHUNK, shots - start), return_expectations=True, return_measurements=True, bit_packed=True)
    keep = ~dets.any(axis=1)
    for v, recs in (plan.postselect if plan else ()):
        parity = np.zeros(len(keep), dtype=np.uint8)
        for r in recs:
            parity ^= (meas[:, r >> 3] >> (r & 7)) & 1
        keep &= parity == v
    kept = meas[keep]
    syn = [(kept[:, b >> 3] >> (b & 7)) & 1 for b in range(n_meas - n_syn, n_meas)]
    z_fix = np.bitwise_or.reduce(syn[:n_syn // 2]).astype(bool)
    x_fix = np.bitwise_or.reduce(syn[n_syn // 2:]).astype(bool)
    sign = np.stack([np.where(z_fix, -1, 1), np.where(z_fix ^ x_fix, -1, 1)], axis=1)
    if plan is not None:
        sign = sign * plan.signs
    infid = (1 - (exps[keep] * sign) @ beta) / 2
    return int(keep.sum()), int((z_fix | x_fix).sum()), infid.sum(), (infid ** 2).sum()


def _parallel_sample(circuit, shots, seed, plan=None):
    if shots <= tc.CHUNK or _STATE.get("procs", 1) <= 1:
        return _orig(circuit, shots, seed, plan)
    _STATE["args"] = (circuit, plan, seed, shots)
    n = (shots + tc.CHUNK - 1) // tc.CHUNK
    with mp.get_context("fork").Pool(min(_STATE["procs"], n)) as pool:
        parts = pool.map(_chunk, range(n), chunksize=1)
    kept = corrected = 0
    total = total_sq = 0.0
    for a, b, c, d in parts:             # same order and arithmetic as tprep's loop
        kept += a
        corrected += b
        total += c
        total_sq += d
    if not kept:
        return {"score": float("nan"), "sem": float("nan"), "acceptance": 0.0, "corrected": corrected}
    mean = max(total / kept, 0.0)
    var = max(total_sq / kept - mean ** 2, 0.0)
    return {"score": mean, "sem": (var / kept) ** 0.5, "acceptance": kept / shots, "corrected": corrected}


_orig = tc._sample


def check(text, data_qubits, shots=10**8, seed=0, procs=25, **kw):
    _STATE["procs"] = procs
    tc._sample = _parallel_sample
    try:
        return tprep.check(text, data_qubits, shots=shots, seed=seed, **kw)
    finally:
        tc._sample = _orig


if __name__ == "__main__":
    import json
    import time
    text = open(sys.argv[1]).read()
    data = json.load(open(sys.argv[2]))["data_qubits"]
    shots = int(float(sys.argv[3])) if len(sys.argv) > 3 else 10**8
    procs = int(sys.argv[4]) if len(sys.argv) > 4 else 25
    t = time.time()
    rep = check(text, data, shots=shots, procs=procs)
    print(f"1-F={rep.score!r} sem={rep.sem:.3g} acc={rep.acceptance!r} n_2q={rep.n_2q} passed={rep.passed} "
          f"({time.time() - t:.1f}s, {procs} procs)")
