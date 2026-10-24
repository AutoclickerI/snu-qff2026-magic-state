# TREP2

Complete.

Best measured three-seed mean: **7.281725e-05**, `reuse19_tuned`, **4.64% below v18**, seed-0 acceptance **0.54001**. Delivery: [best.qasm](best.qasm) and [best.json](best.json). Rank uses the 1e8-shot mean at seeds 0/1000/2000; acceptance is only a gate.

The lever split is measured: the original 25-CX encoder with prefix ALAP gives **7.645170e-5** mean, the 11-CX initial-resource variant with prefix ALAP gives **7.675544e-5**, and the 19-CX encoder with prefix ALAP (v18) gives **7.636083e-5**. The schedule alone captures almost all of the observed v17a-to-v18 gain. The small encoder differences are comparable to sampling variation; the required observed means determine the order.

Timing comes from `tprep.noise.schedule`, including folded RX/MX. R is the native range of all seven data→A and seven B→C checks. B→data ranges and total depths are in `results.json`. In particular whole-circuit ASAP spans R=37–46; using only q0 would incorrectly label that staggered schedule R=44.

The whole-circuit search preserves every per-wire operation order. It covers ASAP, ALAP, random priority placements, an exact quadratic objective over all idle boundaries, and local proposals evaluated through third order. The spectator construction in `quadratic_search.py` exposes every potentially nonzero gap; three placements matched independent exact2 pair calculations to relative error below 3e-16. The low second-order schedules lost after third-order and MC confirmation.

The complete third-order placement trace is in [placement_search.csv](placement_search.csv) (272 trials). The 16 form certificates also check 1,680 physical T-phase fault pairs. The scheduler audit found no empty-layer compaction discrepancies in those placement trials. The quadratic optimizer now repairs initial schedules that exceed its A1 budget; [feasibility_repair.json](feasibility_repair.json) verifies that correction on an actual over-budget priority schedule.

The joint CP-SAT encoder/timing model found a 21-CX injection encoder with R=44 and depth 47. Its seven- and eight-layer models were solved optimally for their stated makespan/CX/late-prefix objective; this is not a global score-optimality claim. Both whole ALAP and rigid-suffix prefix ALAP were priced. Final-readout edges 17→16 and 19→25 were rechecked against the last Z measurements; alternatives and all fresh-measurement-versus-reset choices were evaluated.

The final combination incorporates [EARLYBC’s measured-|+⟩ q10 transfer](../EARLYBC/REPORT.md): retain the X-measured q10 state, remove its reset, and reverse the two data-transfer CX directions. This saves one native step without adding CX. Combining it with the encoders and exact-objective timing moves was priced and sampled in this lane. The final 19-CX-encoder candidate keeps the two original readout re-encoding edges and all first-use measurement preparations; it has **203 CX, R=45, native depth 48**. Its six additional timing requests and their feasible native placements are in [reuse19_tuned.transfer.json](reuse19_tuned.transfer.json).

Protected forms priced: **16/16**, including the original form as a control. Each alternative was physically built using the resynthesized encoder, a verified |+_L⟩ resource, a fixed-coordinate grid parity network, 15 signed rotations, and the retained Steane suffix. The forms are not coordinate relabelings of the same QASM. `forms.py` also builds depth-prioritized variants and certifies the phase-support map. Every new form has negligible full-fault c1 and passes format/class/noiseless correctness; these implementations fail acceptance. This excludes the built networks, not better implementations of those forms.

All exact totals below require |c1|<1e-12 and are expansions through third order, not all-orders fidelities. exp(-A1) is an acceptance estimate. The evaluator acceleration only prunes triples that violate state-independent detector-parity relations; surviving triples retain exact2’s original arithmetic. On v18, the scalar-pruned and unmodified third-order terms agreed exactly (19.451 s versus 324.322 s on jerry); the generalized dependency filter agreed within 2.8e-20. The final winner is also confirmed with the unmodified exact2 CLI. Every MC finalist receives the requested mc3.py judge/MC run. Receipts are beside each QASM.

| Variant | Encoder | Schedule | R native | CX | c1 | 2nd | 3rd | Exact total | exp(-A1) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| [encoder19](encoder19.qasm) | 19 CX | original placement | 47 | 203 | 2.516500e-19 | 5.707720e-05 | 2.581080e-05 | 8.288810e-05 | 0.55250 |
| [encoder19_reuse10_alap_two_moves](encoder19_reuse10_alap_two_moves.qasm) | 19 CX | q10 reuse + optimized ALAP | 45 | 203 | 2.923600e-19 | 5.465070e-05 | 1.904410e-05 | 7.369480e-05 | 0.53494 |
| [f00_0_parity](f00_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 76 | 233 | 1.979900e-19 | 4.830060e-04 | 8.008740e-05 | 5.630930e-04 | 0.35402 |
| [f02_0_parity](f02_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 74 | 239 | 1.683800e-19 | 5.935610e-04 | 8.436470e-05 | 6.779260e-04 | 0.36441 |
| [f04_0_parity](f04_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 74 | 241 | 2.516800e-19 | 3.764760e-04 | 7.335410e-05 | 4.498300e-04 | 0.36968 |
| [f06_0_parity](f06_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 72 | 241 | -2.405500e-20 | 4.242800e-04 | 7.584840e-05 | 5.001280e-04 | 0.38095 |
| [f09_0_parity](f09_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 77 | 239 | 1.128700e-19 | 3.368570e-04 | 6.991060e-05 | 4.067670e-04 | 0.35494 |
| [f11_0_parity](f11_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 70 | 243 | 2.849600e-19 | 3.189750e-04 | 6.235080e-05 | 3.813250e-04 | 0.39163 |
| [f13_0_parity](f13_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 73 | 241 | 3.404700e-19 | 2.986950e-04 | 8.085420e-05 | 3.795490e-04 | 0.36724 |
| [f15_0_parity](f15_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 67 | 237 | 9.251900e-21 | 2.427100e-04 | 6.030820e-05 | 3.030190e-04 | 0.40328 |
| [f17_0_parity](f17_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 69 | 233 | 8.807800e-19 | 1.678180e-04 | 5.904010e-05 | 2.268580e-04 | 0.39357 |
| [f19_0_parity](f19_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 74 | 239 | 2.590500e-20 | 4.323700e-04 | 6.775970e-05 | 5.001300e-04 | 0.36511 |
| [f21_0_parity](f21_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 67 | 243 | 3.182600e-19 | 2.642100e-04 | 5.144750e-05 | 3.156570e-04 | 0.40323 |
| [f23_0_parity](f23_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 74 | 243 | 5.921200e-20 | 4.056140e-04 | 7.775380e-05 | 4.833670e-04 | 0.37027 |
| [f24_0_parity](f24_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 76 | 243 | 1.054700e-18 | 3.774060e-04 | 7.637320e-05 | 4.537790e-04 | 0.35781 |
| [f26_0_parity](f26_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 75 | 243 | -1.850400e-20 | 3.473570e-04 | 8.867540e-05 | 4.360320e-04 | 0.36087 |
| [f28_0_parity](f28_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 72 | 245 | 2.720000e-19 | 2.612400e-04 | 6.596600e-05 | 3.272060e-04 | 0.37964 |
| [f30_0_parity](f30_0_parity.qasm) | 19-CX + parity network | ALAP / parity synthesis | 78 | 247 | 3.182600e-19 | 6.585190e-04 | 9.725670e-05 | 7.557760e-04 | 0.35380 |
| [init_state_d5_s1](init_state_d5_s1.qasm) | 11-CX resource | original placement | 49 | 208 | 3.182600e-19 | 5.707720e-05 | 2.533400e-05 | 8.241120e-05 | 0.54576 |
| [init_state_d5_s1_alap](init_state_d5_s1_alap.qasm) | 11-CX resource | prefix ALAP | 48 | 208 | 3.182600e-19 | 5.622620e-05 | 1.933690e-05 | 7.556300e-05 | 0.52160 |
| [init_state_d5_s1_alap_two_moves](init_state_d5_s1_alap_two_moves.qasm) | 11-CX resource | prefix ALAP + two CX advances | 48 | 208 | 3.182600e-19 | 5.523000e-05 | 1.934280e-05 | 7.457280e-05 | 0.52159 |
| [init_state_d5_s1_reuse10_alap_two_moves](init_state_d5_s1_reuse10_alap_two_moves.qasm) | 11-CX resource | q10 reuse + optimized ALAP | 47 | 208 | 3.182600e-19 | 5.465070e-05 | 1.854980e-05 | 7.320050e-05 | 0.52869 |
| [joint21_compact_alap](joint21_compact_alap.qasm) | 21 CX | prefix ALAP | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.953350e-05 | 7.575970e-05 | 0.53442 |
| [joint21_compact_alap_re_17-16](joint21_compact_alap_re_17-16.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 204 | 2.923600e-19 | 5.763730e-05 | 1.957000e-05 | 7.720730e-05 | 0.53413 |
| [joint21_compact_alap_re_17-16_19-25_14-15](joint21_compact_alap_re_17-16_19-25_14-15.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 206 | 2.923600e-19 | 5.611400e-05 | 1.966130e-05 | 7.577530e-05 | 0.53399 |
| [joint21_compact_alap_re_17-16_19-25_14-8](joint21_compact_alap_re_17-16_19-25_14-8.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 206 | 2.923600e-19 | 5.606900e-05 | 1.965930e-05 | 7.572830e-05 | 0.53399 |
| [joint21_compact_alap_re_19-25](joint21_compact_alap_re_19-25.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 204 | 2.923600e-19 | 5.753250e-05 | 1.963050e-05 | 7.716300e-05 | 0.53413 |
| [joint21_compact_alap_re_none](joint21_compact_alap_re_none.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 203 | 2.923600e-19 | 5.894360e-05 | 1.966760e-05 | 7.861120e-05 | 0.53385 |
| [joint21_compact_alap_reset_14](joint21_compact_alap_reset_14.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.953350e-05 | 7.575970e-05 | 0.53531 |
| [joint21_compact_alap_reset_16](joint21_compact_alap_reset_16.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.960050e-05 | 7.582670e-05 | 0.53531 |
| [joint21_compact_alap_reset_2](joint21_compact_alap_reset_2.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.953350e-05 | 7.575970e-05 | 0.53531 |
| [joint21_compact_alap_reset_20](joint21_compact_alap_reset_20.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.953350e-05 | 7.575970e-05 | 0.53531 |
| [joint21_compact_alap_reset_21](joint21_compact_alap_reset_21.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.960050e-05 | 7.582660e-05 | 0.53531 |
| [joint21_compact_alap_reset_22](joint21_compact_alap_reset_22.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.960050e-05 | 7.582670e-05 | 0.53531 |
| [joint21_compact_alap_reset_23](joint21_compact_alap_reset_23.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.953860e-05 | 7.576480e-05 | 0.53531 |
| [joint21_compact_alap_reset_25](joint21_compact_alap_reset_25.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.634840e-05 | 1.954400e-05 | 7.589240e-05 | 0.53531 |
| [joint21_compact_alap_reset_27](joint21_compact_alap_reset_27.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.954630e-05 | 7.577250e-05 | 0.53531 |
| [joint21_compact_alap_reset_28](joint21_compact_alap_reset_28.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.659280e-05 | 1.954630e-05 | 7.613910e-05 | 0.53531 |
| [joint21_compact_alap_reset_29](joint21_compact_alap_reset_29.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.638170e-05 | 1.954650e-05 | 7.592820e-05 | 0.53531 |
| [joint21_compact_alap_reset_8](joint21_compact_alap_reset_8.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.953370e-05 | 7.575980e-05 | 0.53531 |
| [joint21_compact_alap_reset_8_14_2_20_16_28_29_23_27_25_21_22](joint21_compact_alap_reset_8_14_2_20_16_28_29_23_27_25_21_22.qasm) | 21 CX | prefix ALAP + readout/init | 44 | 205 | 2.923600e-19 | 5.687060e-05 | 1.979130e-05 | 7.666190e-05 | 0.54521 |
| [joint21_compact_alap_third_best](joint21_compact_alap_third_best.qasm) | 21 CX | exact third-order search | 44 | 205 | 2.923600e-19 | 5.523000e-05 | 1.954020e-05 | 7.477030e-05 | 0.53442 |
| [joint21_compact_reuse10_alap_two_moves](joint21_compact_reuse10_alap_two_moves.qasm) | 21 CX | q10 reuse + optimized ALAP | 43 | 205 | 2.923600e-19 | 5.465070e-05 | 1.874640e-05 | 7.339700e-05 | 0.54169 |
| [joint21b_compact_alap](joint21b_compact_alap.qasm) | 21 CX | prefix ALAP | 44 | 205 | 2.923600e-19 | 5.622620e-05 | 1.953350e-05 | 7.575970e-05 | 0.53442 |
| [joint21b_compact_alap_two_moves](joint21b_compact_alap_two_moves.qasm) | 21 CX | prefix ALAP + two CX advances | 44 | 205 | 2.923600e-19 | 5.523000e-05 | 1.954020e-05 | 7.477030e-05 | 0.53442 |
| [joint_d7_s0](joint_d7_s0.qasm) | 21 CX | joint synthesis / whole ALAP | 44 | 205 | 2.923600e-19 | 5.661450e-05 | 2.026340e-05 | 7.687790e-05 | 0.53087 |
| [reuse19_tuned](reuse19_tuned.qasm) | 19 CX | q10 reuse + optimized ALAP | 45 | 203 | 2.923600e-19 | 5.440880e-05 | 1.869140e-05 | 7.310020e-05 | 0.53992 |
| [reuse21_tuned](reuse21_tuned.qasm) | 21 CX | q10 reuse + optimized ALAP | 43 | 205 | 2.923600e-19 | 5.445320e-05 | 1.891870e-05 | 7.337200e-05 | 0.54170 |
| [reuse25_tuned](reuse25_tuned.qasm) | 25 CX | q10 reuse + optimized ALAP | 48 | 209 | 3.182600e-19 | 5.440880e-05 | 1.864740e-05 | 7.305620e-05 | 0.52571 |
| [v17a](v17a.qasm) | 25 CX | original placement | 50 | 209 | 3.182600e-19 | 5.707720e-05 | 2.537690e-05 | 8.245410e-05 | 0.54287 |
| [v17a_alap](v17a_alap.qasm) | 25 CX | prefix ALAP | 49 | 209 | 3.182600e-19 | 5.622620e-05 | 1.925760e-05 | 7.548370e-05 | 0.51797 |
| [v17a_alap_third_best](v17a_alap_third_best.qasm) | 25 CX | exact third-order search | 49 | 209 | 3.182600e-19 | 5.523000e-05 | 1.926350e-05 | 7.449350e-05 | 0.51797 |
| [v17a_reuse10_alap_two_moves](v17a_reuse10_alap_two_moves.qasm) | 25 CX | q10 reuse + optimized ALAP | 48 | 209 | 3.182600e-19 | 5.465070e-05 | 1.847630e-05 | 7.312690e-05 | 0.52502 |
| [v18](v18.qasm) | 19 CX | prefix ALAP | 46 | 203 | 2.923600e-19 | 5.622620e-05 | 1.983790e-05 | 7.606400e-05 | 0.52776 |
| [v18_quad0_s0](v18_quad0_s0.qasm) | 19 CX | exact quadratic search | 46 | 203 | 3.182600e-19 | 5.476100e-05 | 2.694990e-05 | 8.171090e-05 | 0.51119 |
| [v18_quad3_s0](v18_quad3_s0.qasm) | 19 CX | exact quadratic search | 46 | 203 | 1.317500e-18 | 5.474700e-05 | 2.735610e-05 | 8.210310e-05 | 0.50641 |
| [v18_third_best](v18_third_best.qasm) | 19 CX | exact third-order search | 46 | 203 | 2.923600e-19 | 5.523000e-05 | 1.984470e-05 | 7.507470e-05 | 0.52776 |
| [v18_tight_quad0_s0](v18_tight_quad0_s0.qasm) | 19 CX | exact quadratic search | 46 | 203 | 2.794100e-19 | 5.476660e-05 | 2.387430e-05 | 7.864100e-05 | 0.52811 |
| [v18_whole_alap0_s0](v18_whole_alap0_s0.qasm) | 19 CX | alap0 | 46 | 203 | 2.923600e-19 | 5.661450e-05 | 2.056870e-05 | 7.718310e-05 | 0.52425 |
| [v18_whole_asap0_s0](v18_whole_asap0_s0.qasm) | 19 CX | asap0 | 37–46 | 203 | 6.536800e-19 | 3.546090e-04 | 1.397510e-04 | 4.943600e-04 | 0.36271 |
| [v18_whole_data0_s0](v18_whole_data0_s0.qasm) | 19 CX | data0 | 46 | 203 | 3.053100e-19 | 9.276720e-05 | 5.276800e-05 | 1.455350e-04 | 0.42098 |
| [v18_whole_priority0_s0](v18_whole_priority0_s0.qasm) | 19 CX | priority0 | 37–46 | 203 | -4.070800e-20 | 8.557240e-05 | 6.966620e-05 | 1.552390e-04 | 0.44518 |

Each seed below uses 1e8 shots. Every listed MC log includes the 1e6-shot `tprep.check` result. Original-reference receipts were copied from TREP after confirming the circuit source; new receipts were produced in this lane.

| Finalist | MC 0 | MC 1000 | MC 2000 | Mean | Seed-0 acceptance | Files |
|---|---:|---:|---:|---:|---:|---|
| reuse19_tuned | 7.260949e-05 | 7.205880e-05 | 7.378347e-05 | **7.281725e-05** | 0.54001 | [QASM](reuse19_tuned.qasm), [JSON](reuse19_tuned.json), [MC](reuse19_tuned.mc.log) |
| v17a_reuse10_alap_two_moves | 7.398446e-05 | 7.424615e-05 | 7.220754e-05 | **7.347938e-05** | 0.52511 | [QASM](v17a_reuse10_alap_two_moves.qasm), [JSON](v17a_reuse10_alap_two_moves.json), [MC](v17a_reuse10_alap_two_moves.mc.log) |
| encoder19_reuse10_alap_two_moves | 7.510407e-05 | 7.326227e-05 | 7.373959e-05 | **7.403531e-05** | 0.53499 | [QASM](encoder19_reuse10_alap_two_moves.qasm), [JSON](encoder19_reuse10_alap_two_moves.json), [MC](encoder19_reuse10_alap_two_moves.mc.log) |
| reuse25_tuned | 7.411782e-05 | 7.436860e-05 | 7.391015e-05 | **7.413219e-05** | 0.52578 | [QASM](reuse25_tuned.qasm), [JSON](reuse25_tuned.json), [MC](reuse25_tuned.mc.log) |
| joint21_compact_reuse10_alap_two_moves | 7.347458e-05 | 7.504156e-05 | 7.436663e-05 | **7.429426e-05** | 0.54175 | [QASM](joint21_compact_reuse10_alap_two_moves.qasm), [JSON](joint21_compact_reuse10_alap_two_moves.json), [MC](joint21_compact_reuse10_alap_two_moves.mc.log) |
| reuse21_tuned | 7.381354e-05 | 7.593021e-05 | 7.420375e-05 | **7.464917e-05** | 0.54184 | [QASM](reuse21_tuned.qasm), [JSON](reuse21_tuned.json), [MC](reuse21_tuned.mc.log) |
| init_state_d5_s1_reuse10_alap_two_moves | 7.523493e-05 | 7.465570e-05 | 7.531305e-05 | **7.506789e-05** | 0.52881 | [QASM](init_state_d5_s1_reuse10_alap_two_moves.qasm), [JSON](init_state_d5_s1_reuse10_alap_two_moves.json), [MC](init_state_d5_s1_reuse10_alap_two_moves.mc.log) |
| init_state_d5_s1_alap_two_moves | 7.623794e-05 | 7.577204e-05 | 7.496190e-05 | **7.565730e-05** | 0.52166 | [QASM](init_state_d5_s1_alap_two_moves.qasm), [JSON](init_state_d5_s1_alap_two_moves.json), [MC](init_state_d5_s1_alap_two_moves.mc.log) |
| v17a_alap_third_best | 7.591178e-05 | 7.495802e-05 | 7.626860e-05 | **7.571280e-05** | 0.51804 | [QASM](v17a_alap_third_best.qasm), [JSON](v17a_alap_third_best.json), [MC](v17a_alap_third_best.mc.log) |
| joint21_compact_alap_third_best | 7.672299e-05 | 7.736582e-05 | 7.398618e-05 | **7.602500e-05** | 0.53452 | [QASM](joint21_compact_alap_third_best.qasm), [JSON](joint21_compact_alap_third_best.json), [MC](joint21_compact_alap_third_best.mc.log) |
| v18_third_best | 7.611146e-05 | 7.606477e-05 | 7.619169e-05 | **7.612264e-05** | 0.52784 | [QASM](v18_third_best.qasm), [JSON](v18_third_best.json), [MC](v18_third_best.mc.log) |
| v18 | 7.742218e-05 | 7.508943e-05 | 7.657090e-05 | **7.636083e-05** | 0.52782 | [QASM](v18.qasm), [JSON](v18.json), [MC](v18.mc.log) |
| v17a_alap | 7.584194e-05 | 7.640000e-05 | 7.711316e-05 | **7.645170e-05** | 0.51792 | [QASM](v17a_alap.qasm), [JSON](v17a_alap.json), [MC](v17a_alap.mc.log) |
| init_state_d5_s1_alap | 7.708103e-05 | 7.517887e-05 | 7.800643e-05 | **7.675544e-05** | 0.52166 | [QASM](init_state_d5_s1_alap.qasm), [JSON](init_state_d5_s1_alap.json), [MC](init_state_d5_s1_alap.mc.log) |
| joint21b_compact_alap_two_moves | 7.692168e-05 | 7.565311e-05 | 7.829985e-05 | **7.695821e-05** | 0.53444 | [QASM](joint21b_compact_alap_two_moves.qasm), [JSON](joint21b_compact_alap_two_moves.json), [MC](joint21b_compact_alap_two_moves.mc.log) |
| joint21_compact_alap | 7.870956e-05 | 7.664430e-05 | 7.693205e-05 | **7.742864e-05** | 0.53443 | [QASM](joint21_compact_alap.qasm), [JSON](joint21_compact_alap.json), [MC](joint21_compact_alap.mc.log) |
| joint_d7_s0 | 7.938531e-05 | 7.911024e-05 | 8.053883e-05 | **7.967813e-05** | 0.53095 | [QASM](joint_d7_s0.qasm), [JSON](joint_d7_s0.json), [MC](joint_d7_s0.mc.log) |
| v18_tight_quad0_s0 | 8.105330e-05 | 7.970311e-05 | 7.973484e-05 | **8.016375e-05** | 0.52842 | [QASM](v18_tight_quad0_s0.qasm), [JSON](v18_tight_quad0_s0.json), [MC](v18_tight_quad0_s0.mc.log) |
| v18_quad0_s0 | 8.301884e-05 | 8.409437e-05 | 8.283084e-05 | **8.331468e-05** | 0.51157 | [QASM](v18_quad0_s0.qasm), [JSON](v18_quad0_s0.json), [MC](v18_quad0_s0.mc.log) |
| v17a | 8.393188e-05 | 8.355687e-05 | 8.293009e-05 | **8.347295e-05** | 0.54300 | [QASM](v17a.qasm), [JSON](v17a.json), [MC](v17a.mc.log) |
| init_state_d5_s1 | 8.417347e-05 | 8.228549e-05 | 8.439325e-05 | **8.361740e-05** | 0.54596 | [QASM](init_state_d5_s1.qasm), [JSON](init_state_d5_s1.json), [MC](init_state_d5_s1.mc.log) |
| encoder19 | 8.395208e-05 | 8.440232e-05 | 8.548979e-05 | **8.461473e-05** | 0.55258 | [QASM](encoder19.qasm), [JSON](encoder19.json), [MC](encoder19.mc.log) |
| v18_quad3_s0 | 8.563670e-05 | 8.448810e-05 | 8.392264e-05 | **8.468248e-05** | 0.50679 | [QASM](v18_quad3_s0.qasm), [JSON](v18_quad3_s0.json), [MC](v18_quad3_s0.mc.log) |

Limits: this is a measured search over the listed networks and placements, not a proof of the minimum 1-F over all encoders or schedules. The 1e6-shot scores for acceptance-failing forms are diagnostics, not final rankings. `variants.csv`, `results.json`, solver witnesses, phase certificates, model checks, and search traces retain the evidence. No submission, commit, or push was performed. Repository writes stayed in `work/lanes/TREP2/`; no other lane’s files or workers were changed.
