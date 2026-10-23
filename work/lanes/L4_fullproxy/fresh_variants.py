import os
import sys
import time

ROOT = "/home/jihoon/competitions/quantumn/work"
UP = "/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem"
sys.path[:0] = [os.path.dirname(__file__), ROOT, UP]

import cultiv_port as cp
import batch_score
from evaluator import evaluate
from fast_check import check


def main():
    os.chdir(ROOT)
    cands = [("port_lockstep_z", None)]
    for f, idx in [("gen2_t1c13+t2c42_10_1792742380.json", 0),
                   ("gen2_t1c13+t2c42_9_1792742378.json", 0),
                   ("gen2_t1c13+t2c42_9_1792742175.json", 11)]:
        cands.append((f"{f}#{idx}", {"kind": "gen2", "file": f, "idx": idx, "lazy": True}))
    for label, spec in cands:
        if spec is None:
            c = cp.build(("inject", "check", "cycle"), "Tswap", z_first=True, lockstep=True)
        else:
            c, _ = batch_score.make(spec)
        t = time.perf_counter()
        est = evaluate(c.text(), cp.DATA, details=True)
        te = time.perf_counter() - t
        t = time.perf_counter()
        rep = check(c.text(), cp.DATA, shots=5_000_000, seed=0, procs=8)
        tm = time.perf_counter() - t
        print(label, "estimate", est["estimate"], "eval_s", te,
              "mc5m", rep.score, "sem", rep.sem, "mc_s", tm, "n2q", rep.n_2q, flush=True)


if __name__ == "__main__":
    main()
