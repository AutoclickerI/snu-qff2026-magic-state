#!/usr/bin/env python3
import json, os, sys, time
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
from pathlib import Path
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
from fast_check import check

tag, qasm, meta = sys.argv[1:4]
shots = 10**8
text = Path(qasm).read_text()
data = json.loads(Path(meta).read_text())["data_qubits"]
out = {}
t0 = time.time()
for seed in (0, 1000, 2000):
    r = check(text, data, shots=shots, seed=seed, procs=8)
    out[str(seed)] = {"score": r.score, "sem": r.sem, "acceptance": r.acceptance,
                      "n_2q": r.n_2q, "passed": r.passed}
    print(tag, seed, r.score, r.acceptance, r.passed, flush=True)
out["mean"] = sum(out[str(s)]["score"] for s in (0, 1000, 2000)) / 3
out["elapsed"] = time.time() - t0
Path(f"/home/jihoon/competitions/quantumn/work/lanes/EARLY/{tag}.mc.json").write_text(json.dumps(out, indent=2) + "\n")
print(tag, "mean", out["mean"], "elapsed", out["elapsed"], flush=True)
