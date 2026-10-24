# LAYOUT3 — overlap layout search and full-circuit result

No submission was made and no credentials were read. All artifacts are in this directory. The search keeps B/C (and any helper) in cells unused by the transformed pre-stage, and allows A/data to use cells after the pre-stage releases them.

## Result

The best complete layout found is `h1_s4_r0_c2`: transformed pre-stage `s4_r0_c2`, one B/C helper, a 14-layer clean B+C prep, and a 6-layer 10-CX A encoder. Its release-aware merge starts the Steane round at `R=42`, nine data wait steps after pre-stage step 32, and uses 204 CX. It passes every judge gate at 1e6 shots, but its exact third-order loss is above the MC-screen gate and above the current best. The zero-wait ablation is within the target window, so the measured gap is scheduling/geometry rather than first-order fault tolerance.

| Candidate | layout | R | wait | parity | CX | c1 | 2nd | 3rd term | exact total | exp(-A1) | MC 0 / 1000 / 2000 | MC mean | seed-0 acceptance | files |
|---|---|---:|---:|:---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| incumbent `v16_bc2m` | L5 / BC2 | 50 | 17 | no | 207 | ~0 | — | — | 8.41984e-5 | 0.533 | 8.401227e-5 / 8.518898e-5 / 8.472808e-5 | 8.464311e-5 | 0.532286 | `work/candidates/v16_bc2m.{qasm,json}` |
| LAYOUT3 best | `s4_r0_c2` + h31 | 42 | 9 | no | 204 | 3.18264e-19 | 8.70618e-5 | 1.29654e-5 | 1.00027e-4 | 0.55775 | 9.92341e-5 / — / — | — | 0.5580 (1e8 seed 0) | [`l3_base_mall.qasm`](l3_base_mall.qasm), [`l3_base_mall.json`](l3_base_mall.json), [`l3_base_mall.check.json`](l3_base_mall.check.json) |

The full-circuit exact receipt is [`l3_base_mall.exact.json`](l3_base_mall.exact.json). The required 1e8-shot seed-0 verification is [`l3_base_mall.mc0.json`](l3_base_mall.mc0.json), score `9.92341e-5` and acceptance `0.5580`; the other two seeds were correctly skipped because the exact total is outside the 3% MC screen. The 1e6-shot judge receipt is [`l3_base_mall.check.json`](l3_base_mall.check.json): format, class, correctness and acceptance all pass. The first-order diagnostic is numerical zero. Since `1.00027e-4 > 1.03 * 8.41984e-5`, this candidate is correctly excluded from the required 1e8-shot MC ranking.

## Wait and init pricing

[`ablate.log`](ablate.log) prices the same full circuit with the wait noise scaled: zero wait gives exact `8.2435e-5` (2nd `7.6919e-5`, 3rd `5.5156e-6`, exp `0.5885`), half wait gives `9.0669e-5`, and the real nine-step wait gives `1.0003e-4`. The zero-wait value is an ablation, not a judge-valid circuit.

[`minit_screen.json`](minit_screen.json) screens every first-use measurement rewrite at exact second order. The all-sites rewrite used by the candidate is the best (`8.70618e-5`); the best single-site rewrite is q1 (`8.91395e-5`), so no single-site variant enters the exact-third/MC gate.

## Layout and synthesis receipts

[`solver_receipts.json`](solver_receipts.json) records the tested formulations. The strict formulation with B/C and A entirely in released cells and data in pre-stage cells is infeasible for every 8 grid symmetries and legal translations. Relaxing A/data placement gives 24 geometries with lower-bound `R=36`; the one-helper formulation gives 21 feasible geometries with the same lower bound. The only clean witness found in the tested top geometries is the 86-CX, depth-14 witness for `h1_s4_r0_c2`; its SAT/CEGAR receipt is [`h1_s4_r0_c2.piv14.log`](h1_s4_r0_c2.piv14.log). The A encoder receipt is [`h1_s4_r0_c2_A.json`](h1_s4_r0_c2_A.json), 10 CX/depth 6.

The best geometry's B/C prep is the clean rule: no single prep X fault survives the C stabilizer parities plus logical parity. The parity cat was not fitted: the one helper is needed by B/C, while the remaining released/pre-stage cells are occupied by A/data roles, leaving fewer than three cat controls without disturbing a block or data.

## Decision

No LAYOUT3 circuit beats `8.46431e-5`; the lane result is therefore a measured negative for this overlap family. The useful bound is operational: eliminating the nine data wait steps would beat the incumbent, but the available 6x6 geometry forces a data move through the A region and the release-aware schedule reaches `R=42`.
