"""Racing seed-0 re-draws: reorder.py's variants, scored chunk by chunk, dropped once they cannot win.

The official score is tprep's 1e8 shots in 100 chunks (chunk k uses seed k) summed in chunk order. Each variant
(reorder.shuffle with rng k, noise schedule signature asserted, gates re-run by tprep.check) is sampled chunk by
chunk in that order with the same per-chunk code as fast_check._chunk. At each checkpoint a normal model of the
remaining chunks, fitted to every chunk this process has sampled, gives the probability that the variant's completed
score ends below the threshold; below KAPPA times that probability for a variant not yet sampled, the variant is
dropped (a fixed floor would drop nearly every eventual winner at chunk 3 once the threshold is ~4 sigma deep). A completed variant's score, sem and acceptance
are therefore the official ones, bit for bit. Threshold: env RACE_THRESHOLD (default: never drop), lowered by every
completed variant that beats it and by reorder/<name>.thr, where promote.sh relays the best completed score of every host.

    RACE_THRESHOLD=3.875e-5 python race.py <stem> <n variants> [procs] [first variant]  ->  reorder/<name>_r<k>.*
"""
import json
import math
import multiprocessing as mp
import os
import random
import sys

import numpy as np

import tprep
import tprep.check  # noqa: F401  (tprep/__init__ rebinds tprep.check to the function)
from reorder import shuffle, signature
from race_identity import load_mean

tc = sys.modules["tprep.check"]
KAPPA = 0.7
CHECKS = (1, 2, 3, 4, 6, 8, 10, 15, 20, 30, 45, 60, 80)
N_CHUNKS = 100
_orig = tc._sample
_G = {}


def _capture(circuit, shots, seed, plan=None):
    """tprep.check's sampler hook: run the 64-shot noiseless cross-check, keep the noisy circuit for racing."""
    if shots == 64:
        return _orig(circuit, shots, seed, plan)
    _G["circuit"], _G["plan"] = circuit, plan
    return {"score": 0.0, "sem": 0.0, "acceptance": 1.0, "corrected": 0}


def _chunk(circuit, plan, k):
    """fast_check._chunk for chunk k of the official run (seed k)."""
    n_syn = 2 * len(tc.SUPPORTS)
    n_meas = circuit.num_measurements
    beta = np.array(list(tc.TARGET.values()))
    dets, exps, meas = circuit.compile_detector_sampler(seed=k, engine="exact").sample(
        tc.CHUNK, return_expectations=True, return_measurements=True, bit_packed=True)
    keep = ~dets.any(axis=1)
    for v, recs in plan.postselect:
        parity = np.zeros(len(keep), dtype=np.uint8)
        for r in recs:
            parity ^= (meas[:, r >> 3] >> (r & 7)) & 1
        keep &= parity == v
    kept = meas[keep]
    syn = [(kept[:, b >> 3] >> (b & 7)) & 1 for b in range(n_meas - n_syn, n_meas)]
    z_fix = np.bitwise_or.reduce(syn[:n_syn // 2]).astype(bool)
    x_fix = np.bitwise_or.reduce(syn[n_syn // 2:]).astype(bool)
    sign = np.stack([np.where(z_fix, -1, 1), np.where(z_fix ^ x_fix, -1, 1)], axis=1) * plan.signs
    infid = (1 - (exps[keep] * sign) @ beta) / 2
    return int(keep.sum()), int((z_fix | x_fix).sum()), infid.sum(), (infid ** 2).sum()


def _init(lines, data, ref, best, thr_file, exact):
    _G.update(lines=lines, data=data, ref=ref, best=best, thr_file=thr_file, exact=exact, totals=[], kepts=[])


def _threshold(best, thr_file):
    """This host's best completed score, or the relayed best of all hosts if lower."""
    try:
        return min(best.value, float(open(thr_file).read()))
    except (OSError, ValueError):
        return best.value


def _p_below(kept, total, c, thr):
    """Normal tail of R=S-tau*K with exact E[S], E[K]; samples estimate spread only."""
    if math.isinf(thr) and thr > 0:
        return 1.0
    if c == N_CHUNKS:
        return float(total < thr * kept)
    t, n = np.asarray(_G["totals"]), len(_G["totals"])
    if n < 30:
        return 1.0
    a, numerator = _G["exact"]
    mu = tc.CHUNK * (numerator - thr * a)
    residuals = t - thr * np.asarray(_G["kepts"])
    variance = float(np.mean((residuals - mu) ** 2))
    m = N_CHUNKS - c
    target = -(total - thr * kept) - m * mu
    if variance == 0:
        return float(target > 0)
    z = target / math.sqrt(m * variance)
    return 0.5 * math.erfc(-z / math.sqrt(2))


def race(k):
    var = "\n".join(shuffle(_G["lines"], random.Random(k)))
    assert signature(var) == _G["ref"], f"variant {k} changes the schedule"
    tc._sample = _capture
    try:
        rep = tprep.check(var, _G["data"], shots=10**8, seed=0)
    finally:
        tc._sample = _orig
    if not rep.correct_ok:
        return k, None, 0
    circuit, plan = _G["circuit"], _G["plan"]
    kept = corrected = 0
    total = total_sq = 0.0
    for c in range(N_CHUNKS):
        if c in CHECKS:
            thr = _threshold(_G["best"], _G["thr_file"])
            if _p_below(kept, total, c, thr) < KAPPA * _p_below(0, 0.0, 0, thr):
                return k, None, c
        a, b, s, s2 = _chunk(circuit, plan, c)
        kept += a
        corrected += b
        total += s
        total_sq += s2
        _G["totals"].append(s)
        _G["kepts"].append(a)
    mean = max(total / kept, 0.0)                     # tprep.check._sample's arithmetic
    var_ = max(total_sq / kept - mean ** 2, 0.0)
    out = {"score": mean, "sem": (var_ / kept) ** 0.5, "acceptance": kept / 10**8, "n_2q": rep.n_2q,
           "passed": kept / 10**8 >= tc.ACCEPTANCE_FLOOR, "text": var}
    with _G["best"].get_lock():
        if out["passed"] and mean < _G["best"].value:
            _G["best"].value = mean
    return k, out, N_CHUNKS


def main():
    stem, n = sys.argv[1], int(sys.argv[2])
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    k0 = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    thr = float(os.environ.get("RACE_THRESHOLD", "inf"))
    text = open(stem + ".qasm").read()
    meta = json.load(open(stem + ".json"))
    exact = load_mean(stem + ".exact.json", text, meta["data_qubits"])
    name = os.path.basename(stem)
    os.makedirs("reorder", exist_ok=True)
    best = mp.Value("d", thr)
    thr_file = f"reorder/{name}.thr"
    used = done = 0
    with mp.get_context("fork").Pool(procs, _init, (text.split("\n"), meta["data_qubits"], signature(text), best, thr_file, exact)) as pool:
        for k, out, c in pool.imap_unordered(race, range(k0, k0 + n)):
            used += c
            if out is None:
                print(f"{name}_r{k} dropped after {c} chunks (threshold {_threshold(best, thr_file):.5e})", flush=True)
                continue
            done += 1
            path = f"reorder/{name}_r{k}"
            open(path + ".qasm", "w").write(out["text"])
            json.dump({"data_qubits": meta["data_qubits"], "score": out["score"], "acceptance": out["acceptance"],
                       "n_2q": out["n_2q"], "passed": out["passed"], "source": f"{stem} reordered, rng {k}"},
                      open(path + ".json", "w"), indent=1)
            print(f"{name}_r{k} 1-F {out['score']:.17g} acc {out['acceptance']:.4f} 2q {out['n_2q']} "
                  f"pass {out['passed']}", flush=True)
    print(f"{name}: {n} variants, {done} completed, {used / N_CHUNKS:.1f} full-run equivalents", flush=True)


if __name__ == "__main__":
    main()
