# Exact Steane encoder search

## Reproducibility

Run from the repository root with:

```sh
nice -n 5 .venv/bin/python work/lanes/EXENC/exenc.py \
  --cells 1,14,8,9,2,16,15 --type plus --helpers '' --extra 2 \
  --out work/lanes/EXENC/prepA_L5_exact.json
```

The run uses 16 worker threads, enumerates all canonical shortest paths and all
paths with two extra CX gates, and scores every ASAP schedule. It also scores
all schedules of depth at most the proven minimum depth plus one. The exact
state graph has 11,811 rank-four subspaces, equal to the Gaussian binomial
coefficient \([7\\choose4]_2\). Its target-to-coordinate BFS proves minimum
CX 11. A separate matching-layer BFS proves minimum depth 5 and finds an
11-CX depth-5 witness.

## Target A: L5 `a=[1,14,8,9,2,16,15]`, no helpers

The supplied reference is reproduced at exactly `0.0006666666666666669`,
with danger vector (pure logical, `Z_L Z_0` through `Z_L Z_6`) in units of
`p/15`: `[0,3,3,0,4,0,0,0]`. The best enumerated circuit is in
`prepA_L5_exact.json`: 12 CX, depth 9, danger `0.0005333333333333335`,
vector `[0,5,0,0,3,0,0,0]`.

| CX | ASAP depth | ASAP circuits | alternative schedules | minimum danger | best vector units |
|---:|---:|---:|---:|---:|---|
| 11 | 5 | 20 | 8 | 1.6666667e-3 | [0,3,18,0,4,0,0,0] |
| 11 | 6 | 106 | 1172 | 6.6666667e-4 | [0,3,3,0,4,0,0,0] |
| 11 | 7 | 610 | 0 | 6.6666667e-4 | [0,3,3,0,4,0,0,0] |
| 11 | 8 | 1300 | 0 | 7.3333333e-4 | [0,3,4,0,4,0,0,0] |
| 11 | 9 | 986 | 0 | 1.0666667e-3 | [0,0,0,10,6,0,0,0] |
| 11 | 10 | 476 | 0 | 1.6666667e-3 | [0,22,0,0,3,0,0,0] |
| 11 | 11 | 90 | 0 | 2.0666667e-3 | [0,22,0,0,9,0,0,0] |
| 12 | 5 | 32 | 0 | 2.8e-3 | [0,3,18,0,21,0,0,0] |
| 12 | 6 | 1302 | 7262 | 6.6666667e-4 | [0,3,3,0,4,0,0,0] |
| 12 | 7 | 9057 | 0 | 6.6666667e-4 | [0,3,3,0,4,0,0,0] |
| 12 | 8 | 26922 | 0 | 6.6666667e-4 | [0,3,3,0,4,0,0,0] |
| 12 | 9 | 36907 | 0 | **5.3333333e-4** | [0,5,0,0,3,0,0,0] |
| 12 | 10 | 26737 | 0 | 6e-4 | [0,5,0,0,4,0,0,0] |
| 12 | 11 | 12178 | 0 | 6.6666667e-4 | [0,5,0,0,5,0,0,0] |
| 12 | 12 | 2486 | 0 | 8e-4 | [0,3,3,0,6,0,0,0] |
| 13 | 6 | 5651 | 15760 | 6.6666667e-4 | [0,3,3,0,4,0,0,0] |
| 13 | 7 | 76879 | 0 | 6e-4 | [0,0,0,0,0,4,2,3] |
| 13 | 8 | 342317 | 0 | 6e-4 | [0,0,0,0,3,3,0,3] |
| 13 | 9 | 719585 | 0 | **5.3333333e-4** | [0,5,0,0,3,0,0,0] |
| 13 | 10 | 840800 | 0 | **5.3333333e-4** | [0,5,0,0,3,0,0,0] |
| 13 | 11 | 581553 | 0 | **5.3333333e-4** | [0,5,0,0,3,0,0,0] |
| 13 | 12 | 251488 | 0 | 6e-4 | [0,6,0,0,3,0,0,0] |
| 13 | 13 | 49731 | 0 | 7.3333333e-4 | [0,3,3,0,5,0,0,0] |

Totals are 2,987,213 ASAP circuits and 24,202 alternative schedules. The
shortest-path counts (all canonical circuits, before ASAP grouping) are 3,588,
115,621, and 2,868,004 for 11, 12, and 13 CX respectively; all three classes
were fully enumerated. Algebraic commutation-class counts are 251, 7,016, and
129,159. Shared-control/target gate orders were retained because a checked
counterexample changes danger from 30 to 35 units after swapping two such
gates.

Runtime was 58.93 seconds wall time (22.85 seconds in the native engine).
Every emitted best, top-20, and verification-sample circuit passed
`synth.check`, nearest-neighbour and disjoint-layer checks, and an independent
implementation whose score agrees with `synth.dangerous_z` to machine
precision. The independent verifier also checked all 16,384 Z/X Pauli
signatures and matching-layer count agreement through depth 6.

## Targets B and C

`work/lanes/ST_LAY/layouts.json` was absent at completion, so no B/C target was
defined and no B/C search was run.

## Exhaustiveness statement

The 11, 12, and 13 CX canonical path classes are exhaustive over every pivot
choice and every allowed oriented nearest-neighbour CX path, modulo only
reordering of disjoint gates; counts are checked by independent dynamic
programming. ASAP schedules are exhaustive for those paths. Alternative
layerings are exhaustive through depth `minimum depth + 1 = 6` (the reported
alternative rows); deeper alternative layerings were not enumerated. No random
sampling or solver result is used for the optimality claims.

