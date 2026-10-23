"""Benchmark cycle/full proxy candidates against the recorded official MC scores."""
import glob
import json
import os
import sys
import time

ROOT = "/home/jihoon/competitions/quantumn/work"
UP = "/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem"
sys.path[:0] = [os.path.dirname(__file__), ROOT, UP]

import batch_score
from evaluator import evaluate_cycle_proxy


def concordance(a, b):
    good = ties = total = 0
    for i in range(len(a)):
        for j in range(i):
            da, db = a[i] - a[j], b[i] - b[j]
            total += 1
            if da == 0 or db == 0:
                ties += 1
            elif da * db > 0:
                good += 1
    return (good, total, ties, good / (total - ties) if total > ties else 1.0)


def main():
    rows = {}
    for f in glob.glob(os.path.join(ROOT, "batch_scr_*.json")) + glob.glob(os.path.join(ROOT, "batch_gen_*.json")):
        for x in json.load(open(f)):
            s = x.get("spec", {})
            if s.get("kind") not in ("gen2", "gen"):
                continue
            key = (s.get("kind"), s.get("file"), s.get("idx"), bool(s.get("lazy")))
            rows[key] = (x["score"], s)
    out = []
    t0 = time.perf_counter()
    for k, (score, spec) in sorted(rows.items(), key=lambda kv: str(kv[0])):
        c, d = batch_score.make(spec)
        vals = {q: evaluate_cycle_proxy(c.text(), d, q_in=q) for q in (0.0, 0.001, 0.003, 0.006)}
        out.append({"key": k, "score": score, **{f"q{q:g}": v for q, v in vals.items()}})
        print(k, f"mc={score:.10g}", " ".join(f"q{q:g}={v:.10g}" for q, v in vals.items()), flush=True)
    print("n", len(out), "seconds", time.perf_counter() - t0)
    for q in (0.0, 0.001, 0.003, 0.006):
        x = [r[f"q{q:g}"] for r in out]
        y = [r["score"] for r in out]
        ae = [abs(a - b) for a, b in zip(x, y)]
        re = [abs(a - b) / b for a, b in zip(x, y)]
        print("SUMMARY", q, "mae", sum(ae) / len(ae), "maxae", max(ae), "mre", sum(re) / len(re), "rank", concordance(x, y))
    json.dump(out, open(os.path.join(os.path.dirname(__file__), "benchmark.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
