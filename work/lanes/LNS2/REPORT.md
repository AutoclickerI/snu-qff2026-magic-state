# LNS2

**Status: complete; speed-safe finalist verified.**

Best circuit: [`safe_best.qasm`](safe_best.qasm) / [`safe_best.json`](safe_best.json), 219 CX, native depth 51, round R=48. Exact third-order parts are `second=5.002515704477e-5` and `third=1.427183454092e-5`, for **1-F = 6.429699158568e-5**; `c1=2.66e-19`, `exp(-A1)=0.5032521764` (`A1=0.6866638898`). The official 1e6 check passed with acceptance `0.503023` and took **3.91 s per 1e6** in the final staged run (the checker’s reported kernel time was 3.8 s), below the 20 s gate.

The required 1e8-shot MC was run with `inputs/mc3.py --procs 16`:

| seed | 1-F | acceptance |
|---:|---:|---:|
| 0 | 6.609517e-5 | 0.50321 |
| 1000 | 6.647643e-5 | 0.50319 |
| 2000 | 6.652392e-5 | 0.50313 |
| **mean** | **6.636517e-5** | — |

The parent `safe_q19_q11` had mean `6.639501e-5`; the final 14→15 readout edge wins the measured three-seed ranking.

| edit (stage) | delta 1-F vs previous | delta A1 | speed s/1e6 | result |
|---|---:|---:|---:|---|
| v25k control | — | — | 3.34 | exact `6.505010287762e-5`, exp `0.5106215532` |
| Reviewer item 1, corrected helper readout copy4 | `-4.496404e-7` | `+0.0104000` | 3.54 | exact `6.460046251348e-5`, exp `0.5053386080` |
| timing + commuting reorder | `-1.324709e-7` | `+3.9929e-6` | 3.64 | exact `6.446799159236e-5` |
| q19 RX check | `~0` | `+0.00166667` | 3.61 | acceptance budget; exact unchanged |
| q11 reset→measure | `-4.373144e-8` | `+0.00166667` | 4.42 | exact `6.442426015053e-5` |
| final readout edge 14→15 | `-1.272686e-7` | `+0.0008000` | 3.91 | **safe_best** |
| q8 MX reuse (rejected) | `-7.468948e-7` | `-0.0122022` | **>100** | exact gain, but fails the 20 s gate |

All deltas in the table are conditional exact2 third-order values; the final ranking is by the completed three-seed MC above. The final acceptance remains above the requested `exp(-A1) >= 0.5002` target.

## Reviewer item 1 port diagnosis

The first direct KNAP-style port was invalid. It selected the early `measure q[25] -> c[38]` instead of v25k’s terminal `c[22]` record, and it left the `q29`/`q28` readouts before their copy CXs. It also reset fresh cells `q18,q31,q35,q34` that v25k omits from its barrier lists; xtim then assigned them long idle spans. This produced anti-deterministic detectors (the KNAP numbering was `#37,#38,#43,#46,#47`; my direct reproduction had the same defect with shifted indices `#46,#47,#52,#55`).

The corrected port moves `q29/q28` measurements after the copy layer, places helper measurements at the terminal `q25 -> c[22]` suffix, includes all four fresh helpers in every barrier, and updates the two old detector parities before adding four equality detectors. It has zero anti detectors, passes correctness, and gives the item-1 exact value reported above.

## Verified versus inferred

Verified: exact2 and the lane Fourier contraction agree for the baseline, corrected reviewer port, and `safe_best`; `|c1| < 1e-12`; nearest-neighbour CX legality; format, class, correctness, and acceptance at the official 1e6 check; zebra timing; and all three 1e8 MC seeds. The q8 speed run exceeded 100 s per 1e6 before completion; it is excluded despite its lower exact screen. No submission, commit, or push was made.

Inferred: q8’s slowdown is caused by xtim’s per-shot branching around the reused random-MX state; the timing correlation is strong but xtim internals were not independently inspected. The reviewer diagnosis above is established by the anti-detector and idle-channel traces; the internal implementation mechanism remains an inference.
