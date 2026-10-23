"""python o_synth.py <layout.json> <depth> <seed0> <nseeds> <tag>: |+_L> prep for O (stage cells if staged) with helpers."""
import json
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR")
import synth  # noqa: E402

lay = json.load(open(sys.argv[1]))
depth, s0, n, tag = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
cells = lay["o_stage"] or lay["o"]
helpers = [q for q in lay["o_help"] if q not in cells]
HAM = [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6], [0, 1, 2]]
rows = [{cells[i] for i in r} for r in HAM]
for sd in range(s0, s0 + n):
    r = synth.synth_cells(rows, cells + helpers, depth, seconds=90, workers=4, seed=sd)
    if not r:
        print("seed", sd, "none", flush=True)
        continue
    ops, piv, st = r
    dz = synth.dangerous_z(ops, piv, cells, helpers)
    print(f"seed {sd} {st} cx {sum(map(len, ops))} layers {len(ops)} danger {dz:.3e}", flush=True)
    json.dump({"ops": ops, "pivots": piv, "danger": dz}, open(f"o_{tag}_d{depth}_s{sd}.json", "w"))
