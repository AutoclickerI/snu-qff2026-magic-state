"""Synthesize one block's preparation for steane_full.LAY (blocks prepared in `order`; a block may
use as helpers every cell that is neither data nor a block prepared before it).

    python synth_blocks.py <block a|b|c> [order abc] [seconds per depth] -> preps_<order>_<block>.json
"""
import json
import sys
import time

import synth
import os

from steane_full import GENS, LAYOUTS

LAY = LAYOUTS[os.environ.get("LAYOUT", "L1")]

HAM = GENS + [[0, 1, 2]]          # |+_L>: Hamming [7,4] = stabilizers + an X_L representative

if __name__ == "__main__":
    k = sys.argv[1]
    order = sys.argv[2] if len(sys.argv) > 2 else "abc"
    secs = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    done = set().union(*[set(LAY[j]) for j in order[:order.index(k)]])
    rows = HAM if k == "a" else GENS
    avail = [q for q in range(36) if q not in LAY["d"] and q not in done]
    best = None
    for depth in range(4, 14):
        t = time.time()
        r = synth.synth(LAY[k], rows, avail, depth, seconds=secs, workers=16)
        if not r:
            print(k, "depth", depth, "none", f"{time.time() - t:.0f}s", flush=True)
            continue
        ops, piv, st = r
        n = sum(map(len, ops))
        print(k, "depth", depth, st, n, "cx", len(ops), "layers", synth.check(LAY[k], rows, avail, ops, piv),
              f"{time.time() - t:.0f}s", flush=True)
        if best is None or n < best[2]:
            best = (ops, piv, n)
            json.dump({"ops": ops, "pivots": piv}, open(f"preps_{os.environ.get('LAYOUT', 'L1')}_{order}_{k}.json", "w"))
        if st == "OPTIMAL" and depth >= len(ops) + 2:
            break
