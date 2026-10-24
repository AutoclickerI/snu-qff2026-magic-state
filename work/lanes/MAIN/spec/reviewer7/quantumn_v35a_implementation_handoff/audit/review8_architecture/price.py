"""Price every requested candidate at all orders with all 73 moments.

At most two independent single-threaded Python processes run concurrently.
Receipts are copied into this lane only after the corresponding process exits.
"""
from pathlib import Path
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVALUATOR = ROOT / "audit/reaudit_evaluation/portable"


def run(name):
    stem = HERE / name
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    with stem.with_suffix(".log").open("w") as log:
        process = subprocess.run(
            [sys.executable, str(EVALUATOR / "sparse_walsh.py"), str(stem), "72", "canonical"],
            stdout=log, stderr=subprocess.STDOUT, env=env,
        )
    if process.returncode:
        return {"name": name, "error": process.returncode}
    receipt = EVALUATOR / (name + "_canonical_sparse_result.json")
    shutil.copyfile(receipt, HERE / receipt.name)
    result = json.loads(receipt.read_text())
    assert len(result["results"]) == 73
    return {"name": name, "moments": len(result["results"]), **{key: result[key] for key in
            ["loss", "acceptance", "seconds", "conditioned_width", "conditional_loss_kernel_omission_bound"]}}


if __name__ == "__main__":
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for completed in concurrent.futures.as_completed([pool.submit(run, name) for name in sys.argv[1:]]):
            result = completed.result()
            results.append(result)
            print(json.dumps(result), flush=True)
    (HERE / "latest_prices.json").write_text(json.dumps(results, indent=2) + "\n")
