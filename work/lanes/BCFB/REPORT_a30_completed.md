# BCFB — A on v30f

Status: **completed historical v30f search**. Current v34m work is in [REPORT.md](REPORT.md). No submissions, commits, pushes, credentials access or subagents.

Best verified circuit: **`a30/finalists/a30_fastpick_feedback_neighbors_05085`**, also copied to **[best.qasm](best.qasm)** / [best.json](best.json). All-orders **5.8186015663449e-05**, acceptance **0.527826391823**: delta 1-F **-7.51726378732e-07** (**1.275% lower**) versus v30f. Delta A1 **-0.000585800870721**. This remains above the supplied 5.067e-5 leader.

Unchanged exact2 --third confirms c1 2.6645352591e-19, second 4.5889632754711e-05, cubic 1.1630246804962e-05, total **5.7519879559673e-05**; exp(-A1) **0.527996414512**. Cubic delta -7.19451954528e-07. Judge 1e6 PASS, seed-0 acceptance 0.528254. XTIM FAST 6.999 s/1e6; complete zebra fast_check command 3.308 s. Three-seed 1e8-shot MC mean **5.720757e-05**; individual seed scores are below.

The A encoder has 11 CX and plus pivots [1,14,9,2]. Total CX remains 189 and R remains 48. B/C preparation, data operations, their timings and the round are retained. The final FAST variant reuses q14’s postselected X state, checks X on q1/q14/q9 and Z on q8/q15, and retains q2’s RX reset while dropping its subsequent MX check. It orders the three early CXs into q8 as 14→8, 2→8, 9→8. Complete options and native outside-A equality are in the finalist metadata and diff receipt.

| Fully checked stem | Exact cubic total | exp(-A1) | All-orders | Delta all-orders | MC seeds 0 / 1000 / 2000 | MC mean |
|---|---:|---:|---:|---:|---|---:|
| `a30_fastpick_feedback_neighbors_05085` | 5.751987956e-05 | 0.5279964145 | 5.81860156634e-05 | -7.5172638e-07 | 5.813176e-05 / 5.679062e-05 / 5.670033e-05 | 5.720757e-05 |
| `a30_fastpick_feedback_neighbors_05061` | 5.751987956e-05 | 0.5285265505 | 5.81861726823e-05 | -7.5156936e-07 | 5.84876e-05 / 5.806857e-05 / 5.990934e-05 | 5.882184e-05 |
| `a30_fbn_00549` | 5.807951946e-05 | 0.5276485143 | 5.8746168852e-05 | -1.9157319e-07 | 5.976216e-05 / 5.843586e-05 / 5.855952e-05 | 5.891918e-05 |
| `a30_fb_s810_00837` | 5.818682763e-05 | 0.5292338366 | 5.88599584178e-05 | -7.7783624e-08 | 5.774892e-05 / 5.794255e-05 / 6.035219e-05 | 5.868122e-05 |
| `a30_near_acheck_10046` | 5.865696703e-05 | 0.5299387754 | 5.93724241869e-05 | +4.3468214e-07 | 5.74911e-05 / 5.901845e-05 / 6.033349e-05 | 5.894768e-05 |

Each MC seed uses 1e8 shots; SEM is about 9e-7. Those draws cannot resolve a gain of order 1e-7. Ranking uses validated all-orders loss, not a favorable single draw. All-orders kernel-cutoff bounds are about 1.1e-14 and exclude floating-point roundoff. Differences around 1e-16 are ties.

Baseline independently reproduced: exact second 4.6200534608726e-05, cubic 1.2038796905476e-05, total 5.8239331514202e-05; exp(-A1) 0.527687204329; all-orders 5.893774204218101e-05, acceptance 0.5275245061355753. Baseline MC is external evidence from FRESH/REPORT.md: seeds 0/1000/2000 = 5.90419220e-5 / 5.88640000e-5 / 5.89256e-5; mean 5.89438407e-5. This lane does not claim those MC runs as new.

## Search table

| Formulation | Attempted / valid cubic / exp(-A1) floor passes | Best eligible cubic | Status |
|---|---:|---:|---|
| Both ENDSTATE libraries, stationary A, commuting orders/checks, R48–51 | 701 / 423 / 283 | 5.823933151e-05 | complete |
| 521 ACHECK encoders × checks × R48–52 | 10420 / 541 / 88 | 5.823933151e-05 | complete |
| A timing ±1/2, initialization and zero-CX check neighbors | 196 / 22 / 22 | 5.823933151e-05 | complete |
| Post-coupling X-parity checks | 32 / 32 / 32 | 0.0002616183793 | complete |
| Staggered A endpoint coupling/readout | 66 / 50 / 50 | 5.823933151e-05 | complete |
| Internal two-CX windows and A15 three-CX parity stars | 23702 / 32 / 6 | 7.431167624e-05 | complete |
| Library input reuse and A16 early-hop release | 23976 / 715 / 715 | 5.823933151e-05 | complete |
| q2/q14 MX-state reuse and basis changes | 18864 / 412 / 412 | 5.826625997e-05 | complete |
| Free-cell exact-library staging plus explicit endpoint swaps | 120 / 118 / 0 | none | complete |
| Winning SAT encoder: 12 commuting orders × 128 check masks × 6 reuse sets | 9216 / 2456 / 2456 | 5.729784676e-05 | complete |
| Lowest-cubic CX order: all 128 reuse × 128 check masks | 16384 / 1728 / 1728 | 5.729784676e-05 | complete |
| Exact-loss SAT feedback: seeds 810–817, depths 6–9, caps 14/16/18; 8 × 1200 s | 7046 / 7046 / 7046 | 5.818682763e-05 | 8 full budgets complete |

All-orders evaluations: 45 including the baseline. Full tables: `a30/search_summary.json`, `a30/allorders_summary.json`, `a30/verified_finalists.json`. Invalid schedules are not cubic prices. Every SAT seed ran its full budget; timeout is not an UNSAT proof. Witnesses and cancelled blue-context data are preserved in the single `witnesses.tar.xz` after final consolidation.

## A attribution and exposure

| Channels removed | Cubic loss | Reduction | Share of baseline |
|---|---:|---:|---:|
| A_CX | 4.600721694e-05 | 1.223211457e-05 | 21.00% |
| A_init_checks | 5.691754492e-05 | 1.321786598e-06 | 2.27% |
| A_encoder | 4.506984557e-05 | 1.316948595e-05 | 22.61% |
| A_idle | 5.535184232e-05 | 2.887489195e-06 | 4.96% |
| A_coupling | 5.332980301e-05 | 4.909528502e-06 | 8.43% |
| A_readout | 5.733940873e-05 | 8.999227865e-07 | 1.55% |
| A_all | 3.819839649e-05 | 2.004093503e-05 | 34.41% |

These are noise counterfactuals, not physical candidate circuits. Their reductions overlap and must not be summed. Coupling ablations remove the whole joint channel, including its data component. Fourteen calculations were independently confirmed with unchanged exact2 run/third_order; maximum Fourier disagreement 4.38e-18.

| Cross term, inclusion–exclusion | Second | Cubic | Total |
|---|---:|---:|---:|
| A_all x data_wait | 3.926920509e-06 | 3.185729003e-06 | 7.112649511e-06 |
| A_all x pre_stage | 4.015123828e-06 | 2.830968135e-06 | 6.846091963e-06 |
| A_CX x data_wait | 3.926920509e-06 | 8.666141118e-07 | 4.79353462e-06 |
| A_CX x pre_stage | 1.842301152e-06 | 6.715166953e-07 | 2.513817847e-06 |

Before R48, A live durations are q1:5, q14:7, q8:7, q9:8, q2:6, q16:4, q15:7 steps. Preparation has 12 idle qubit-steps: q9 contributes 5, q15 3, q16 2, q1/q14 1 each. Data q10/q3 have their last pre-round CX/reset/measurement at step32; q10 still receives T-dagger at33 and its long idle gap is34–47. q10 waiting Z/Y faults paired with late A encoder faults dominate the A-CX cross term. Full channel provenance and top pairs: `a30/attribution_verified.json`.

## Mechanisms and scope

The initial SAT improvement traded a slightly larger second-order term for a smaller normalized cubic term. Commuting CX reorderings, q14 input reuse and the selected checks then reduced loss further. The final FAST variant advances 2→8, delays 9→8, and retains q2’s reset. This changes fault propagation and exposure without adding CX or delaying the round. CX count and depth are not the objective. An encoder-only Pauli-class calculation moves three potential weight-two-Z partner classes from data20 to four on data7, while retaining four on data10 and three on data0. The count rises from10 to11 even though full-circuit loss falls; that surrogate omits the exterior, C17 coupling and conditioning. Details are in a30/fault_class_mechanism.json.

Post-round parity checks lose because the judge adds trailing idle noise to unmeasured data until the last ancilla operation; best tested cubic loss is 2.61618e-4. Internal flag windows either fail to fit or add enough cost to lose their benefit; best floor-passing cubic loss is 7.43117e-5. All 50 valid staggered A-coupling variants failed to improve loss: shorter exposure alone does not preserve error-detection timing.

With B/C and data endpoints fixed, exhaustive nearest-neighbor matching yields exactly one stationary A placement: [1,14,8,9,2,16,15]. There is no A-to-unused-cell edge. The 120 free-cell transports use both exact libraries and all 30 code classes on the connected staging sets; 118 have vanishing c1. Their R spans 102–162 and exp(-A1) spans 0.0212–0.0996. This rules out this endpoint-swap family, not arbitrary interleaved routing or borrowed B/C helpers.

## Speed exclusions

The lowest cubic candidate a30_fbn_08352 has cubic 5.72978467582e-5 and all-orders 5.79840882718e-5, but XTIM measured 180.0 s/1e6 (SLOW). Its MC was terminated by verified host PID before any 1e8 seed completed; unchanged exact2 was allowed to finish. A nearby q2-reuse variant was also SLOW at 146.1 s/1e6. Moving data20’s final T-dagger from step47 to40 preserved cubic loss but remained SLOW (127.2 s/1e6); that edit is rejected and absent from the winner. Twelve best candidates retaining q2’s reset were FAST on owl; finalists were retimed on zebra. The predictor was copied byte-identically into BCFB because owl lacked XTIM’s file.

## Verified versus inferred

Verified: target stabilizers and deterministic flags, exact native folding and times, full-circuit correctness construction, the 14 reference ablations, unchanged exact2 CLI, judge, XTIM and MC receipts for the retained finalists, and all-orders 72/canonical scope assertions. The sparse evaluator is byte-identical to the source snapshot; only its location changed because its CLI writes beside itself. No judge or evaluator arithmetic was edited.

Not proved: global A optimality, arbitrary helper instruments, arbitrary moving placements, or that the remaining gap to the leader is unavoidable. The search counts are finite coverage, not exhaustive synthesis. Prior v25k/v26n work was cancelled by MAIN and was not resumed; its evidence is in `REPORT_v25_v26_cancelled.md`.
