# P23 — PRESYN's blue stabilizer check on the v23h_c2c9 base

Main-session port. `port23.py` reruns PRESYN's `partial_checks.py` (mask 1, boundary 129) and `blue_reuse.py` (21- or
19-CX injection, both Bell orientations, no state reuse) with `core.BASE` = `inputs/v23h_c2c9`. With the base set back
to v22h_c2c9 it reproduces PRESYN's `blue_x_e21_r0_u0`, `blue_xz_e21_r1_u0` and `blue_xz_e19_r0_u0` byte for byte
(SHA-256 against PRESYN's exact receipts). Scores: unmodified `lanes/EVAL/exact2.py --third` (`*.exact.txt`).

| Variant | CX | R | Exact total | exp(-A1) |
|---|---:|---:|---:|---:|
| base v23h_c2c9 | 203 | 45 | 6.92210e-5 | 0.54086 |
| blue_x_e19_r0 / r1 | 209 | 48 | 6.76384e-5 / 6.76620e-5 | 0.50667 |
| blue_x_e21_r0 / r1 | 211 | 46 | 6.75285e-5 / 6.75521e-5 | 0.51306 |
| blue_xz_e19_r0 / r1 | 213 | 50 | 6.60126e-5 / 6.59880e-5 | 0.49444 (fails) |
| **blue_xz_e21_r1** (= MAIN/v24) | 215 | 48 | **6.58848e-5** | 0.50068 |
| blue_xz_e21_r0 | 215 | 48 | 6.59094e-5 | 0.50068 |

exp(-A1) matches 1e8-shot seed-0 acceptance within ~1e-4 (PRESYN low_c2: 0.505451 vs 0.50535; v22: 0.53384 vs
0.5338–0.5340). v23's B+C prep has 0.007 more acceptance than v20's, which is what lets the full blue XZ check pass here.
