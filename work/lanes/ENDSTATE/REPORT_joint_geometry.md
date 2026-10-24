# ENDSTATE — scored prefix-free joint resources

**Status: RUNNING: scored circuits and bounded search results below; final validation jobs remain.**

Best fully validated new FAST circuit: **region2_k56_A2_safe**, R39, all-orders **5.753110335e-05**, acceptance **0.586886656**. The reproduced v30f control is **5.8937742042181006e-5**. The SLOW source-reuse row2 circuit reaches **5.799916445862596e-5**, but fails the required runtime gate (117.45 s/1e6). Its requested three-seed Monte Carlo run is recorded separately. No measured new circuit reaches 5e-5. No universal conclusion over all role assignments, A preparations, or helpers follows.

Leading FAST all-orders candidate: **[region2_k56_A2_safe_dest](joint/region2_k56_A2_safe_dest.qasm)**, native **R38**, loss **5.61375001753e-05**. Its exact-third/judge/MC completion is stated in the tables below; an all-orders screen alone is not called a completed full gate.

## Separate-block closure and original feasibility answer

The tested independent-block family is closed as a performance direction: eight full C7 circuits, stationary A, tested B/C moves and helper-assisted variants, best exact cubic **2.083783914e-4 at R56**, acceptance **0.387448**. All eight fail acceptance. Pre-round-only second-order pairs contribute **8.32769e-5**, preparation × exposure **4.83136e-5**, and round × round **2.884e-5**. This mechanism-backed closure does not cover arbitrary MB or dynamically interleaved preparation. Full evidence: [REPORT_separate.md](REPORT_separate.md).

Original priority1 is **SAT**: [witness12_h1.qasm](witness12_h1.qasm), [metadata](witness12_h1.json), [independent entangled-reference verification](witness12_h1.verified.json). A/B/C require **10/11/11 encoder CX**, no helpers, and **7/7/6 one-CX measured transfers**, at most one per ancilla wire. Cost is **32 preparation +20 transfer +21 round =73 CX**. Thus the ≤12/one-move rung and its ≤14/two-move relaxations are feasible. Static connected B7/C6 with all required outside D partners is exhaustively impossible in the separate geometric model; moving/helper C6 remains open. The positive fragment is not a full magic-state circuit.

## Prefix and exhaustive region-membership screen

v30f prefix: 78 CX on 15 cells, output logical order `[0,20,7,10,3,15,8]`. Last touches as written: `[35,47,36,33,29,32,30]`; ASAP: `[27,27,27,27,26,27,27]`, depth28. Nondata cell13 releases at15, cell19 at9, and cells1/2/4/6/9/14 at28. [v30f.prefix.json](v30f.prefix.json) retains native operations, releases, and all48 embeddings. Older v29c/v23 timelines remain linked in the separate report.

All 14-subsets of the available cells were enumerated for each of six translation classes; eight whole-grid symmetries cover all48 embeddings. Windows: initially free, and free by16. Requirements: connected BC14, BC perfect matching, a distinct outside D neighbor for each B, and a connected stationary A7 matched to D. Initial-free feasible-region counts are `[4,4,7,9,10,5]`; by16 counts `[4,4,10,9,10,11]`. Deduplication leaves **48 embedding/region cases**. Enumeration stats/receipts are `joint/enum_v30f_e*_t*`; all complete.

**Exhaustive scope:** region membership under those restrictions. Only the first B/C/D/A role assignment and BC matching per region are retained. Subsequent code labelling tests all30 Steane classes and selects a distance-optimal automorphism per class; A is chosen from the exact native libraries. This produces1439 candidates. Data routes are deterministic weighted vacancy routes; CP-SAT optimizes timing on each fixed route, role assignment, A encoder, and ASAP prefix. No helper-assisted/disconnected A or alternative role enumeration is claimed.

All1439 fixed-route timing models finish OPTIMAL at each nominal BC depth9/10/11, with **minimum R38 at every depth**. These proxy timings are not synthesized-resource witnesses. Files: [depth9](joint/timed_regions_d9.json), [depth10](joint/timed_regions_d10.json), [depth11](joint/timed_regions_d11.json). Presolve is disabled. No global optimum or global no-better-than-5e-5 theorem follows.

## Real clean resources and choices

Five leading timing layouts were synthesized with unchanged FRESH `synth.py`, `sat_core.py`, `ft.py` snapshotted read-only under this lane. The endpoint is the **rank-three state sum(x in S) |x>_B |x>_C**. After transversal B→C, B is `|0_L>` and all seven C cells are literal zeros. All seven C outcomes are checked; replacing them by only Steane syndromes would change the contract. Every accepted resource passes FRESH physical X/XX single-fault cuts plus an independent Stim endpoint check. Full circuit single-fault and judge checks include phase faults.

Row89 final label order: D `[12,32,13,22,16,28,14]`; A `[18,26,19,21,15,27,20]`; B `[6,33,7,23,10,29,8]`; C `[0,34,1,17,11,35,9]`. BC is entirely prefix-free, A uses released prefix cells, and data make four coherent one-cell hops (eight CX). Real clean resources: depth11/CX57, depth10/CX52, and depth10/CX45. Depth9/cap63 on these fixed labels/cells/no-helper is solver-UNSAT; cap40/depth10 reached UNKNOWN after100s. UNSAT is a reproducible solver result, not an independently checked DRAT certificate.

Choice: fixed-wire ALAP retiming follows geometry/routing and preserves logical ordering. Some A sources reuse detector-certified prefix measurements. Full reuse is SLOW; selective reuse of cells18/19/21/26 avoids the measured q20/q27 slowdown. Twenty exact low-danger A encoders are screened as full circuits; SLOW cases are excluded before all-orders pricing. Minimum round time alone is insufficient: lower-danger A encoders at R41 beat the initial R38 circuit. Deterministic BC-zero checks are inserted only in free slots; their impact is measured, never assumed.

Measured helper: a virtual 1↔8 resource edge expands through prefix-free helper2 into reset, CX control→2, CX2→target, MX2. Its record produces Z on the control and is propagated exactly into B readout detectors. Fixed row89/depth9/cap48 with this shortcut is solver-UNSAT; depth10/cap45 with a required shortcut is SAT. The physical complete circuit uses46 resource CX and expanded nominal depth13, retimes toR41, passes single-fault and judge checks, and is FAST. Its all-orders loss is **7.186755638267783e-5**, so this tested helper does not help.

A direct adjacent B–C pair has opposite checkerboard parity and cannot share a grid neighbor. Consequently the two-edge pipelined B→helper→C round requires a different distance-two endpoint geometry. That geometry is outside this direct-matching enumerator and remains unsearched; no broad helper/pipeline impossibility is claimed.

## Ranked complete circuits

All-orders values use unchanged MAIN sparse arithmetic,72/canonical, with full-used-qubit barriers and no FRAME/POSTSELECT. Snapshot hashes and the positive control are retained. MAIN subsequently added parallel row dispatch; the stored serial arithmetic is identical. Exact3 is unchanged `EVAL/exact2.py --third`; judge is unchanged `fast_check.py` at1e6; FAST is the unchanged XTIM predictor. Cache/output paths alone are redirected inside ENDSTATE. Three-seed MC is triggered by the full source-reuse row2 finalist despite its SLOW classification; speed-only or all-orders-only diagnostic variants are not promoted to finalists.

| Full circuit | R | Total CX / BC CX | Data hops | Ancilla idle steps | Exact3 | All-orders | Judge acceptance | Speed |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| [region2_k56_A2_safe_dest](joint/region2_k56_A2_safe_dest.qasm) | 38 | 182 / 56 | 9 | 31 | not run | 5.613750018e-05 | not run | FAST 4.97 |
| [region2_k56_A6_safe_dest](joint/region2_k56_A6_safe_dest.qasm) | 38 | 182 / 56 | 9 | 31 | not run | 5.61381316e-05 | not run | FAST 4.49 |
| [region2_k56_same_dest](joint/region2_k56_same_dest.qasm) | 38 | 182 / 56 | 9 | 29 | not run | 5.722802425e-05 | not run | FAST 4.27 |
| [region2_k56_A2_safe](joint/region2_k56_A2_safe.qasm) | 39 | 182 / 56 | 9 | 31 | 5.71244e-05 | 5.753110335e-05 | 0.587157 PASS | FAST 4.68 |
| [region2_k56_A6_safe](joint/region2_k56_A6_safe.qasm) | 39 | 182 / 56 | 9 | 31 | 5.71236e-05 | 5.753175803e-05 | 0.585489 PASS | FAST 5.81 |
| [region2_k56_A10_safe](joint/region2_k56_A10_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.762343892e-05 | not run | FAST 4.70 |
| [region2_k56_A13_safe](joint/region2_k56_A13_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.762408802e-05 | not run | FAST 6.45 |
| [region2_reuse_same](joint/region2_reuse_same.qasm) | 39 | 189 / 63 | 9 | 27 | not run | 5.768926561e-05 | not run | FAST 6.50 |
| [region2_k56_A5_safe](joint/region2_k56_A5_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.774605448e-05 | not run | FAST 5.40 |
| [region2_reuse_q27](joint/region2_reuse_q27.qasm) | 39 | 189 / 63 | 9 | 27 | not run | 5.775708882e-05 | not run | SLOW 154.23 |
| [region2_reuse_q21](joint/region2_reuse_q21.qasm) | 39 | 189 / 63 | 9 | 27 | not run | 5.775736208e-05 | not run | SLOW 112.71 |
| [region2_reuse_drop13](joint/region2_reuse_drop13.qasm) | 39 | 189 / 63 | 9 | 27 | not run | 5.782618897e-05 | not run | SLOW 105.15 |
| [region2_reuse_q13](joint/region2_reuse_q13.qasm) | 39 | 189 / 63 | 9 | 27 | not run | 5.786022156e-05 | not run | SLOW 114.64 |
| [region2_k56_A12_safe](joint/region2_k56_A12_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.786388277e-05 | not run | FAST 5.33 |
| [region2_reuse_drop27](joint/region2_reuse_drop27.qasm) | 39 | 189 / 63 | 9 | 27 | not run | 5.792911681e-05 | not run | SLOW 99.06 |
| [region2_reuse_drop21](joint/region2_reuse_drop21.qasm) | 39 | 189 / 63 | 9 | 27 | not run | 5.792922855e-05 | not run | SLOW 97.85 |
| [region2_d11_reuseA](joint/region2_d11_reuseA.qasm) | 39 | 189 / 63 | 9 | 27 | 5.76084e-05 | 5.799916446e-05 | 0.582442 PASS | SLOW 117.45 |
| [region2_k56_A3_safe](joint/region2_k56_A3_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.828249326e-05 | not run | FAST 4.07 |
| [region2_k56_A7_safe](joint/region2_k56_A7_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.828295375e-05 | not run | FAST 7.45 |
| [region2_k56_A11_safe](joint/region2_k56_A11_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.834321971e-05 | not run | FAST 8.45 |
| [region2_k56_A14_safe](joint/region2_k56_A14_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.834367454e-05 | not run | FAST 8.16 |
| [region2_k56_same](joint/region2_k56_same.qasm) | 39 | 182 / 56 | 9 | 29 | 5.81333e-05 | 5.852223112e-05 | 0.586846 PASS | FAST 5.57 |
| [region2_k56_A4_safe](joint/region2_k56_A4_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.86009713e-05 | not run | FAST 4.89 |
| [region2_k56_A8_safe](joint/region2_k56_A8_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.86014257e-05 | not run | FAST 4.60 |
| [region2_k56_A18_safe](joint/region2_k56_A18_safe.qasm) | 40 | 182 / 56 | 9 | 31 | not run | 5.889048907e-05 | not run | FAST 7.42 |
| [region2_early_A2_safe_zero](joint/region2_early_A2_safe_zero.qasm) | 37 | 182 / 56 | 9 | 31 | not run | 5.896424776e-05 | 0.585588 PASS | FAST 11.33 |
| [region2_k56_A19_safe](joint/region2_k56_A19_safe.qasm) | 40 | 182 / 56 | 9 | 31 | not run | 5.961018791e-05 | not run | FAST 4.91 |
| [region2_k56_A9_safe](joint/region2_k56_A9_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 5.993001762e-05 | not run | FAST 4.55 |
| [region2_k56_A15_safe](joint/region2_k56_A15_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 6.01876537e-05 | not run | FAST 4.50 |
| [region2_k56_A0_safe](joint/region2_k56_A0_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 6.09420554e-05 | not run | FAST 3.35 |
| [region2_k56_A1_safe](joint/region2_k56_A1_safe.qasm) | 39 | 182 / 56 | 9 | 31 | not run | 6.094252292e-05 | not run | FAST 4.03 |
| [region2_d11_alap](joint/region2_d11_alap.qasm) | 40 | 189 / 63 | 9 | 27 | 6.15689e-05 | 6.202552425e-05 | 0.582876 PASS | FAST 4.06 |
| [region2_k56_alap](joint/region2_k56_alap.qasm) | 40 | 182 / 56 | 9 | 29 | not run | 6.287388213e-05 | not run | FAST 7.94 |
| [region2_k56_A16_safe](joint/region2_k56_A16_safe.qasm) | 40 | 182 / 56 | 9 | 31 | not run | 6.292025806e-05 | not run | FAST 4.94 |
| [region2_k56_A17_safe](joint/region2_k56_A17_safe.qasm) | 40 | 182 / 56 | 9 | 31 | not run | 6.29207577e-05 | not run | FAST 6.29 |
| [region89_k45_A5_safe](joint/region89_k45_A5_safe.qasm) | 41 | 164 / 45 | 4 | 47 | not run | 6.725127571e-05 | not run | FAST 6.38 |
| [region89_k45_A1_safe](joint/region89_k45_A1_safe.qasm) | 41 | 164 / 45 | 4 | 47 | 6.66516e-05 | 6.744448433e-05 | 0.577765 PASS | FAST 5.75 |
| [region89_hopT_A1_safe](joint/region89_hopT_A1_safe.qasm) | 41 | 164 / 45 | 4 | 47 | not run | 6.777913944e-05 | 0.578677 PASS | FAST 5.55 |
| [region89_k45_A4_safe](joint/region89_k45_A4_safe.qasm) | 41 | 164 / 45 | 4 | 47 | not run | 6.782954787e-05 | not run | FAST 6.30 |
| [region89_k45_A0_safe_z](joint/region89_k45_A0_safe_z.qasm) | 41 | 164 / 45 | 4 | 47 | not run | 6.802462613e-05 | not run | FAST 3.58 |
| [region89_k45_A0_safe](joint/region89_k45_A0_safe.qasm) | 41 | 164 / 45 | 4 | 47 | 6.72194e-05 | 6.802462613e-05 | 0.578042 PASS | FAST 5.46 |
| [region89_d10_A0_reuse_z](joint/region89_d10_A0_reuse_z.qasm) | 41 | 171 / 52 | 4 | 43 | not run | 6.807879808e-05 | 0.572630 PASS | SLOW 126.78 |
| [region89_d10_A0_reuse](joint/region89_d10_A0_reuse.qasm) | 41 | 171 / 52 | 4 | 46 | 6.73116e-05 | 6.811546937e-05 | 0.574412 PASS | SLOW 180.83 |
| [region89_hopT_A0_safe](joint/region89_hopT_A0_safe.qasm) | 41 | 164 / 45 | 4 | 47 | not run | 6.835780317e-05 | 0.578137 PASS | FAST 5.64 |
| [region564_d11_reuseA](joint/region564_d11_reuseA.qasm) | 38 | 181 / 58 | 7 | 34 | 6.93461e-05 | 6.973964525e-05 | 0.593597 PASS | SLOW 155.05 |
| [region89_d10_reuseA](joint/region89_d10_reuseA.qasm) | 38 | 169 / 52 | 4 | 28 | 6.96149e-05 | 6.997646965e-05 | 0.596578 PASS | SLOW 117.21 |
| [region89_k45_A0_alap](joint/region89_k45_A0_alap.qasm) | 41 | 164 / 45 | 4 | 47 | not run | 7.009144317e-05 | not run | FAST 6.44 |
| [region89_bus](joint/region89_bus.qasm) | 41 | 165 / 46 | 4 | 57 | 7.09974e-05 | 7.186755638e-05 | 0.570219 PASS | FAST 5.07 |
| [region89_k45_q18](joint/region89_k45_q18.qasm) | 38 | 162 / 45 | 4 | 29 | not run | 7.385420545e-05 | not run | FAST 6.57 |
| [region89_k45_A18_safe](joint/region89_k45_A18_safe.qasm) | 43 | 164 / 45 | 4 | 61 | not run | 7.456112023e-05 | not run | FAST 3.89 |
| [region89_k45_A19_safe](joint/region89_k45_A19_safe.qasm) | 43 | 164 / 45 | 4 | 61 | not run | 7.497238879e-05 | not run | FAST 5.90 |
| [region564_d11_alap](joint/region564_d11_alap.qasm) | 39 | 181 / 58 | 7 | 34 | 7.48e-05 | 7.525303311e-05 | 0.592825 PASS | FAST 4.51 |
| [region89_k45_A16_safe](joint/region89_k45_A16_safe.qasm) | 43 | 164 / 45 | 4 | 61 | not run | 7.526015085e-05 | not run | FAST 5.90 |
| [region89_k45_A17_safe](joint/region89_k45_A17_safe.qasm) | 43 | 164 / 45 | 4 | 61 | not run | 7.56240085e-05 | not run | FAST 3.86 |
| [region89_k45_A13_safe](joint/region89_k45_A13_safe.qasm) | 42 | 164 / 45 | 4 | 54 | not run | 7.645770197e-05 | not run | FAST 3.79 |
| [region89_k45_A9_safe](joint/region89_k45_A9_safe.qasm) | 42 | 164 / 45 | 4 | 54 | not run | 7.662306112e-05 | not run | FAST 5.70 |
| [region89_k45_A12_safe](joint/region89_k45_A12_safe.qasm) | 42 | 164 / 45 | 4 | 54 | not run | 7.706942641e-05 | not run | FAST 6.06 |
| [region89_k45_A8_safe](joint/region89_k45_A8_safe.qasm) | 42 | 164 / 45 | 4 | 54 | not run | 7.723679522e-05 | not run | FAST 5.84 |
| [region89_k45_alap](joint/region89_k45_alap.qasm) | 38 | 162 / 45 | 4 | 29 | not run | 7.790313365e-05 | not run | FAST 5.47 |
| [region89_d10_alap](joint/region89_d10_alap.qasm) | 38 | 169 / 52 | 4 | 28 | 7.80332e-05 | 7.841132606e-05 | 0.605902 PASS | FAST 12.14 |
| [region117_d11_alap](joint/region117_d11_alap.qasm) | 39 | 188 / 61 | 9 | 30 | 8.01899e-05 | 8.058482271e-05 | 0.591670 PASS | FAST 7.61 |
| [region117_d11_reuseA](joint/region117_d11_reuseA.qasm) | 38 | 188 / 61 | 9 | 30 | 8.38214e-05 | 8.41778032e-05 | 0.593156 PASS | SLOW 121.78 |
| [region89_d11](joint/region89_d11.qasm) | 38 | 174 / 57 | 4 | 45 | 8.40088e-05 | 8.446024508e-05 | 0.583232 PASS | FAST 10.75 |
| [region1162_d11_reuseA](joint/region1162_d11_reuseA.qasm) | 40 | 173 / 55 | 4 | 48 | 8.6492e-05 | 8.709498678e-05 | 0.577132 PASS | SLOW 109.81 |
| [region1162_d11_alap](joint/region1162_d11_alap.qasm) | 40 | 173 / 55 | 4 | 48 | 9.31862e-05 | 9.380071056e-05 | 0.585153 PASS | FAST 6.15 |

## Row2 refinement and measured progress

The original five-region screen identifies row2 as the best FAST region. Its first clean63-CX resource gives6.202552425e-5 atR40. A56-CX resource was found in0.35s; cap50/depth11 reached UNKNOWN at180s, and cap50/depth10 is solver-UNSAT on the fixed labels/cells. Lower CX is not assumed to improve noise: the reset-only56-CX circuit is slightly worse than63-CX; its advantage appears with the measured source policy and chosen A encoder.

Exact A enumeration on these seven cells covers all40 shortest8-CX encoder circuits,1440 at9CX, and38720 at10CX. Minimum depth4 requires9CX. The twenty lowest-danger candidates were screened as full circuits with source reuse only when the source basis already matches. The top five FAST schedules were selected for full exact-third, judge and three-seedMC validation. Other variants remain explicitly marked all-orders/speed screens.

Reusing cell16 after its checked zero readout as the next coherent-hop destination removes a reset and reduces the native round fromR39 toR38. The leading full circuit has **182 CX =78 prefix +18 coherent-hop +9 A +56 BC +21 round**, with no block teleport. BC cell25 is released by the prefix atstep9; the other13 BC cells are free initially. [Grid diagram](joint/best_geometry.svg).

Transporting terminal Tdg gates with the data and also reusing the physical zero output of the destructive X readout atcell15 produces a verified R37 candidate. Its measured all-orders loss5.896424776e-5 is worse than the R38 candidate. Thus the retained choice is the lower-loss R38 schedule rather than the earliest tested R.

All168 common Steane automorphisms were additionally screened on row2 with the fixed9-CX A encoder, original fresh-destination policy, deterministic routes and depth11 resource lifetime:168 OPTIMAL results, identityR40, next-bestR44. [Complete bounded timing records](joint/autos2.json). This does not prove optimality after changing source-reuse policy or arbitrary routes.

## Three-seed Monte Carlo

Unchanged MAIN `mc3.py` is copied byte-for-byte inside this lane because that source path is absent on hippo. It executes the1e6 gate followed by100-million-shot seeds0,1000,2000. A mean is reported only after all three seeds and successful process exit.

| Circuit | Seed0 | Seed1000 | Seed2000 | Mean | Completion |
|---|---:|---:|---:|---:|---|
| region2_k56_A2_safe | 5.75408e-05 | pending | pending | pending | running / capacity-suspended |
| region2_k56_A6_safe | 5.811245e-05 | 5.701438e-05 | pending | pending | running / capacity-suspended |
| region2_d11_reuseA | pending | pending | pending | pending | running / capacity-suspended |
| region2_k56_same | 5.808895e-05 | 5.66554e-05 | 5.901053e-05 | 5.791829e-05 | complete |

Unchanged exact cubic and judge are required for the five selected region finalists and the best encoder/helper variants; additional encoder-sweep rows are explicitly all-orders/speed screens where those fields say not run. Each QASM has sibling metadata and operation plan. No scores are inferred from R or CX alone.

## Loss attribution and exposure

Values below are second-order contributions in1e-5. Pair-class totals are disjoint; exposure, hops, and bus columns are overlapping marginals and cannot be added. Exposure includes prefix idle/data waiting, while the ranked table counts only ancilla idle ticks from source initialization (or certified source measurement) to its first round use. Attribution is independently checked against the unchanged exact second-order total.

| Circuit | Round × round | Pre-round-only | Exposure-involving | Coherent-hop-involving | Bus-involving |
|---|---:|---:|---:|---:|---:|
| region2_d11_reuseA | 2.8840 | 1.5472 | 0.9717 | 0.0604 | 0.0000 |
| region2_k56_same | 2.8840 | 1.5838 | 0.9861 | 0.0426 | 0.0000 |
| region2_d11_alap | 2.8840 | 1.8133 | 1.2509 | 0.0160 | 0.0000 |
| region89_k45_A1_safe | 2.8840 | 1.8423 | 1.1882 | 0.0140 | 0.0000 |
| region89_k45_A0_safe | 2.8840 | 1.8729 | 1.2176 | 0.0140 | 0.0000 |
| region89_d10_A0_reuse | 2.8840 | 1.9100 | 1.1644 | 0.0229 | 0.0000 |
| region564_d11_reuseA | 2.8840 | 2.3010 | 1.4464 | 0.1816 | 0.0000 |
| region89_d10_reuseA | 2.8840 | 2.5146 | 1.6181 | 0.0147 | 0.0000 |
| region89_bus | 2.8840 | 2.1945 | 1.3555 | 0.0140 | 0.1813 |
| region564_d11_alap | 2.8840 | 2.6601 | 1.6963 | 0.0822 | 0.0000 |
| region89_d10_alap | 2.8840 | 3.1919 | 2.1868 | 0.0147 | 0.0000 |
| region117_d11_alap | 2.8840 | 2.9842 | 1.8068 | 0.0760 | 0.0000 |
| region117_d11_reuseA | 2.8840 | 3.2708 | 1.9192 | 1.0966 | 0.0000 |
| region89_d11 | 2.8840 | 3.5554 | 2.4376 | 0.0102 | 0.0000 |
| region1162_d11_reuseA | 2.8840 | 3.6030 | 2.6885 | 0.1764 | 0.0000 |
| region1162_d11_alap | 2.8840 | 4.1275 | 3.0891 | 0.0675 | 0.0000 |

Every direct joint-resource circuit has **zero block teleports**. Only the explicitly named helper circuit has a measured bus. As in LADDER/ARCH, round × round is2.884e-5. The excess is before the round and in cross terms; LADDER R33–R42 values are calibration controls, not a per-step pricing law.

## Cell lifetimes, embeddings, and deliverables

Each scored `<stem>.metrics.json` lists every A/B/C cell, initialization/certified-source time, round-use time, and idle count, plus all48 prefix-embedding Manhattan distance vectors. Distances for embeddings other than the emitted one are routing lower bounds, not schedules. Actual paths, hop times, and chosen embedding are in metadata/schedule and `.plan.json`. Whole-grid D4 images preserve these native circuit scores. [joint/catalog_scored.json](joint/catalog_scored.json) collects the complete ranked records.

The QASM files linked above are full circuits: real cultivation prefix, data hops, native A/BC preparation, transversal round, readouts, and detector parities. They can be assembled or inspected directly by ST1/SEPBC/FRESH without another fragment emitter. The original independent-block fragment is preserved separately.

## Verified versus inferred / operational record

- Verified: region membership in the stated finite windows; all fixed-route CP timing optima; positive SAT resources and Stim endpoints; adjacency and nonoverlap; judge-native timing audit; complete-circuit exact/all-orders/judge/speed results where listed; loss-attribution equality.
- Inferred or bounded: other-embedding Manhattan distances; generic depth-d proxy resources before synthesis; the mechanism explaining why exposure hurts. No universal lower bound for joint resources, arbitrary roles, helpers, MB, or alternate prefixes is asserted.
- Four initial remote synthesis processes saved valid witnesses but failed receipt hashing because the remote FRESH path was absent. Their `.prep.recovered.json` files explicitly revalidate the saved witnesses; failed exits are not rewritten as successes.
- Zebra repeatedly exceeded host-load48. Only this lane’s processes were terminated by explicit PID and their exits consumed; unfinished evaluations were rerun on hippo. No other lane was stopped. All writes stay inside ENDSTATE. No credentials, submissions, commits, pushes, or agents were used.
