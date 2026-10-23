# L1 CP-SAT final-cycle scheduling

Finalized 2026-10-23 19:57 KST. Current layout and extras `t1c13,t2c42` retained. No contest submission.

Best measured official **1-F = 0.00012580301137380046**, below the requested `1.3103e-4` benchmark. The remeasured reference is `0.00013103021409913631`; the measured reduction relative to that reference is **3.989%**. Best cycle proxy is **0.00011274399214113765**, versus `0.00011839336692347942` (4.772% lower). These are different selection criteria: the best official schedule is not the minimum-proxy schedule.

## Top five by measured official score

Each row used `fast_check.check` on the complete injection + check + final-cycle circuit, with real grid adjacency, `shots=100000000`, `seed=0`, and `passed=True`. All have 113 two-qubit gates. The numerical-c1 exception below applies to every row.

| JSON index | Cycle proxy | Official 1-F | SEM | Acceptance |
|---:|---:|---:|---:|---:|
| 0 | 0.000112977532519 | 0.000125803011374 | 1.16647e-06 | 0.66544512 |
| 1 | 0.000112918769617 | 0.000125848088306 | 1.16778e-06 | 0.66544515 |
| 2 | 0.000113161142723 | 0.000126400671573 | 1.17272e-06 | 0.66554235 |
| 3 | 0.000113219873054 | 0.000126971535282 | 1.17579e-06 | 0.66554287 |
| 4 | 0.000113458446124 | 0.000127348901655 | 1.1866e-06 | 0.66549455 |

Schedules: [top5_schedules.json](top5_schedules.json), in the original five-field gen2 format. Exact measured receipts, raw c1, circuit hashes and provenance: [top5_results.json](top5_results.json). Builder specifications: [build_specs.json](build_specs.json). Best measured circuit: [best_schedule.json](best_schedule.json), [best.qasm](best.qasm), [best_result.json](best_result.json). Minimum-proxy schedule: [best_proxy.json](best_proxy.json).

The scores are fixed-seed Monte Carlo measurements with the listed SEMs. Selecting among candidates does not establish a statistically significant improvement in the underlying expected infidelity.

## What was modeled

`cpsat.py` implements integer layers, orientation booleans, one gate per qubit per layer, post-unbell restrictions, extra attachment precedence, and all nine tile-pair parity constraints. `validity.py` adds backward CSS Pauli propagation; Stim remains the oracle. Its filter accepted all 112 current Stim-valid schedules in the original two-extra files, with no measured false negatives. Twenty-four older stored schedules fail the current oracle.

`ordered_objective.py` includes reset, gate, measurement and idle faults, all empty-signature tail pairs, and all equal non-empty-signature partial-window pairs. Logical Y has the current joint cost 1/2. Within a fixed per-qubit gate order, each grouped DEM mass is `(1 - a1^n1 * a2^n2 * ar^nr)/2`, with `a1=sqrt(1-4p/3)`, `a2=(1-16p/15)^(1/8)`, `ar=1-2p`, and `p=1e-3`. Idle exponents are affine layer differences; gate/reset exponents are fixed. Ambiguous logical-basis mechanisms use the same probability sorting and max matching as `proxy2.joint_loss`.

Probabilities are scaled by `10^9`; pair products and the objective are integers. Per-solve conservative rounding-error bounds are retained. OR-Tools 9.15 presolve falsely declared a known-feasible element/product model infeasible; the reproducer and log are preserved in `infeasible_reproducer.pbtxt` and `solver_diagnosis.log`. Presolve is disabled for the complete-objective solves, and the affected runs were repeated.

Calibration: 54 existing order classes and 152 generated order classes each give Pearson correlation **1.0** between the unrounded closed form and `Model.proxy`. The maximum absolute disagreement across those sets is **1.3444106938820255e-17**. A further 20 leading order classes also agree. Scaled-integer objective errors are separately checked against their bounds in [calibration_audit.json](calibration_audit.json).

## Solver status and limits

CP-SAT examined **2,214,702** schedules across the eight short-depth orientation partitions, with a Stim oracle call for each enumerated schedule. Five orientation searches timed out after 1800 seconds (`FEASIBLE`); two were exhausted (`OPTIMAL`), and one was infeasible. See [orientation_search_audit.json](orientation_search_audit.json). The global complete-proxy lower bound remains **0**, so the unresolved global relative gap is **100%**. **There is no global optimality certificate for LMAX 8 or 9.**

Complete-objective retiming was solved at LMAX 8 and 9, with `OPTIMAL` referring only to the rounded objective and fixed order class. Additional exact CP-SAT neighborhood enumeration exhausted 34,696 schedules within four layer changes of the new proxy incumbent at LMAX 8 and 13,451 within three changes at LMAX 9, without improving it. The baseline LMAX-8 radius-4 neighborhood was also exhausted without improvement. A 45,360-schedule Z-before-X family was exhausted; the new proxy improvement requires interleaving.

Unrestricted pure-data and extra-cat tail objectives were used only to generate candidates; their bounds are not claimed as complete-proxy bounds. Invalid schedules were rejected by Stim and no-good cuts. Final selection uses measured full-circuit scores, not a surrogate. No annealing was used in this lane.

## First-order verification and explicit exception

The literal `c1 == 0` requirement fails even for the reference (raw `3.7007434154171901e-17`). Selected candidates have raw c1 values **3.7007434154171901e-17**, with empty harmful-instruction lists. [residue_audit.json](residue_audit.json) traces the reference result to five contributions of `7.401486830834377e-18`, each a weight-1/15 fault with unweighted numerical infidelity `2^-53`. The audit leaves every scanner return value unchanged.

Following the later user instruction to take measured performance gains when an earlier user rule blocks them, this lane accepts these records only when `abs(c1) <= sys.float_info.epsilon` (`2.220446049250313e-16`) and `by_instruction == []`. **This is a lane-specific exception, not a claim that the raw value equals zero.** The strict result and every raw result are preserved. I recommend replacing literal floating-point equality with this numerical-zero criterion; no standing rule was silently changed.

All delivered JSON entries were rebuilt through `batch_score.make(kind="gen2", lazy=True)`, and their complete QASM hashes were checked against the measured receipts. All writes and caches remain in this lane. At most eight CPU workers were used, credentials were not read, and nothing was submitted.

Reproduction commands are in [README.md](README.md). Earlier checkpoints and diagnosis history are retained in [RUN_NOTES.md](RUN_NOTES.md).
