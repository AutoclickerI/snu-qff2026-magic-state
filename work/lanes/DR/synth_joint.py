"""Joint synthesis of all three Steane-round blocks (A=|+_L>, B=|0_L>, C=|0_L>) as one CSS state on
every non-data cell (cells of any block may route for the others; free cells end in |0>).

    python synth_joint.py <min depth> <max depth> [seconds per depth] -> preps_joint.json
"""
import json
import sys
import time

import synth
import os

from steane_full import GENS, LAYOUTS

LAY = LAYOUTS[os.environ.get("LAYOUT", "L1")]

HAM = GENS + [[0, 1, 2]]

if __name__ == "__main__":
    d0, d1 = int(sys.argv[1]), int(sys.argv[2])
    secs = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    rows = [{LAY["a"][i] for i in r} for r in HAM] + [{LAY[k][i] for i in r} for k in "bc" for r in GENS]
    avail = [q for q in range(36) if q not in LAY["d"]]
    for depth in range(d0, d1 + 1):
        t = time.time()
        r = synth.synth_cells(rows, avail, depth, seconds=secs, workers=16)
        if not r:
            print("depth", depth, "none", f"{time.time() - t:.0f}s", flush=True)
            continue
        ops, piv, st = r
        print("depth", depth, st, sum(map(len, ops)), "cx", len(ops), "layers", f"{time.time() - t:.0f}s", flush=True)
        json.dump({"ops": ops, "pivots": piv, "status": st}, open(f"preps_{os.environ.get('LAYOUT', 'L1')}_joint_d{depth}.json", "w"))
