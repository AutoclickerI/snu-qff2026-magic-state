"""Block preparations for layout L5: A alone on its 7 cells (several seeds, keep the lowest danger),
B and C jointly on B+C plus free cells.

    python synth_l5.py a <seed0> <n seeds> <depth> | bc <depth min> <depth max>
"""
import json
import sys

import synth
from steane_full import GENS, LAYOUTS

LAY = LAYOUTS["L5"]
HAM = GENS + [[0, 1, 2]]
used = set(LAY["d"]) | set(LAY["a"]) | set(LAY["b"]) | set(LAY["c"])
free = [q for q in range(36) if q not in used]

if __name__ == "__main__":
    if sys.argv[1] == "a":
        s0, n, depth = map(int, sys.argv[2:5])
        rows = [{LAY["a"][i] for i in r} for r in HAM]
        for sd in range(s0, s0 + n):
            r = synth.synth_cells(rows, LAY["a"], depth, seconds=60, workers=8, seed=sd)
            if not r:
                print("seed", sd, "none", flush=True)
                continue
            ops, piv, st = r
            dz = synth.dangerous_z(ops, piv, LAY["a"], [])
            print(f"seed {sd} {st} cx {sum(map(len, ops))} layers {len(ops)} danger {dz:.3e}", flush=True)
            json.dump({"ops": ops, "pivots": piv, "danger": dz}, open(f"prepA_L5_s{sd}.json", "w"))
    else:
        d0, d1 = map(int, sys.argv[2:4])
        rows = [{LAY[k][i] for i in r} for k in "bc" for r in GENS]
        for depth in range(d0, d1 + 1):
            r = synth.synth_cells(rows, LAY["b"] + LAY["c"] + free, depth, seconds=600, workers=16)
            if not r:
                print("depth", depth, "none", flush=True)
                continue
            ops, piv, st = r
            print(f"depth {depth} {st} cx {sum(map(len, ops))} layers {len(ops)}", flush=True)
            json.dump({"ops": ops, "pivots": piv}, open(f"prepBC_L5_d{depth}.json", "w"))
            if st == "OPTIMAL":
                break
