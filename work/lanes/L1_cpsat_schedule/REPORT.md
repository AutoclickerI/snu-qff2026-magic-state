# L1 CP-SAT final-cycle scheduling

Started 2026-10-23 18:00 KST. Updated 19:32 KST. Work in progress.

Scope: existing layout, extras `t1c13,t2c42`, layers 2..8 and 2..9. All artifacts and runtime caches remain in this lane. No submissions. At most eight CPU workers.

Read `gen2_cycle.py`, `proxy2.py`, `decompose.py`, `bounds.py`, `fast_check.py`, `batch_score.py`, `qcirc.py`, and the judge noise/fault-scan code.

Important modeling issue: first-order window masses are linear in idle gaps, but `Model.proxy` uses finite-noise Stim DEM probabilities, which merge identical mechanisms nonlinearly. Exactness against that proxy must be calibrated, not assumed. The baseline JSON's stored value predates the current joint logical-Y pricing and will be recomputed.

Planned verification: full circuit built through `batch_score.make`, real adjacency, `fast_check.check(shots=10**8, seed=0, procs<=8)`, `passed=True`, and `tprep.fault_scan(processes<=8).c1 == 0` for reported official results.

## Implemented model and current results

`cpsat.py` implements integer operation layers, orientation variables, per-qubit all-different constraints, post-unbell rules, attachment precedence, and all nine supplied tile-pair parity constraints. Empty operation layers are removed. `validity.py` adds symbolic backward Pauli propagation of the six readouts, six output stabilizers, and both output logical operators. Its current conditions accept all 112 Stim-valid schedules in the existing two-extra files; 24 older entries fail the current Stim oracle. This empirical check is not a proof that these strengthening constraints are necessary for all possible schedules.

`ordered_objective.py` extracts every physical fault signature from Stim for a fixed per-qubit gate order, including reset, gate, measurement, and idle noise. For a grouped mechanism the probability is

`m = (1 - a1^n1 * a2^n2 * ar^nr)/2`,

where `a1 = sqrt(1 - 4p/3)`, `a2 = (1 - 16p/15)^(1/8)`, `ar = 1 - 2p`, and `p=1e-3`. Here `n1` is an affine expression in operation layers and the final layer, while `n2,nr` are constant within the gate-order class. All equal-detector-signature pairs are included, both empty and non-empty, with the current joint logical-Y pricing. This reproduces finite-noise DEM merging, rather than replacing it by linear first-order masses.

CP-SAT uses probability tables rounded to `1e-9` and integer pair products. Each solve records a conservative objective rounding bound (typically about `5e-10` in proxy units). Consequently, `OPTIMAL` certifies the rounded model within its specified order class, not unrounded global optimality.

Calibration on 54 distinct existing valid gate orders: Pearson correlation **1.0**, maximum absolute error **4.472333961502706e-18**, RMSE **3.1459328881601515e-18**. Raw measurements: `existing_refined_calibration.json` and `existing_refined_calibration_summary.json`.

The named baseline recomputes to **1.1839336692347942e-4**. Its decomposition is tail `9.4210509380546e-5`, partial windows `2.418285754293341e-5`, first order zero. Retiming its fixed order at LMAX 8 returned `OPTIMAL`, with rounded objective/bound `1.18393409962494e-4`, and returned the same proxy. This does not certify global optimality.

Unrestricted CP-SAT search with a pure-data tail objective exposed invalid schedules missed by parity alone; exact Stim no-goods were added by order class. The stronger propagation model subsequently yielded valid candidates, but their full proxies are substantially worse than the incumbent. The tail objective is therefore used only to generate orders; its solver bound is **not** a bound on the complete proxy. Structured searches at LMAX 8/9 and exact neighborhood enumeration are underway.

## Verification issue requiring an explicit criterion decision

The baseline full-circuit official check passed. However, its raw fault scan returns **c1 = 3.70074341541719e-17**, with 2076 faults tested and no harmful-fault entries in the scanner's report. Therefore the literal `c1 == 0` contract fails even for the reference. No official score is certified here yet. The raw check/scan evidence is retained in `baseline_official.json`. The user has been asked whether to allow `c1 <= 1e-12` only when the harmful-instruction list is empty, with every raw c1 still reported. Pending that answer, verification remains strict.

No contest submission or credential access occurred. Runtime imports disable bytecode writes, and xtim caches are created under this lane's working directory.

## 19:02 KST update

Unrestricted short-depth CP-SAT enumeration has found a new interleaved schedule with proxy **1.1274399214113765e-4**, approximately 4.77% below the named baseline. The search is ongoing. An immutable copy is in `newbest_snapshot.json`; complete-objective retiming results are in `newbest_refined.json`. The candidate has passed the official full-circuit check; its raw c1 has the same `3.70074341541719e-17` residue, so strict verification remains unresolved.

For orientation `[0,1,1]`, all **45,360** schedules in the strengthened validity model with layers 2..7 and every Z CNOT before every X CNOT were enumerated (`OPTIMAL` exhaustion). The best proxy there is `1.1831196817148951e-4`; the new improvement uses interleaving. The baseline radius-4 Hamming neighborhood at LMAX 8 was also exhausted: 68,619 schedules, 12,123 rejected by Stim, no improvement over the baseline. These are restricted-scope certificates, not a global bound for LMAX 8 or 9.

A solver issue was identified and preserved: OR-Tools 9.15 presolve reported `INFEASIBLE` for a probability-table/product model that becomes feasible when its known seed assignment is fixed. With presolve disabled, the same unrestricted order model solves `OPTIMAL`. The reproducer is `infeasible_reproducer.pbtxt`, with logs in `solver_diagnosis.log`. Presolve is now disabled for complete-objective models. All 54 original order optimizations were rerun under this setting (`existing_nopresolve_runs.json`), including the formerly rejected cases. Earlier presolve-based certificates are superseded by these reruns.

The complete-objective extractor currently requires a unique mechanism for each `(detector signature, final stabilizer signature)` in each logical-basis DEM. It raises and records an error for ambiguous mappings rather than silently approximating them. One high-cost generated order hit this limitation (`generated_refined.log`). The 54 existing calibration classes and 14 new candidate classes match the exact proxy; all current leading candidates are supported.

The first top-five full-circuit batch is saved in `top5_official.json`. Every candidate passed, and every raw c1 was the same nonzero numerical residue. Official-score certification is still held pending the explicitly requested criterion decision. Subsequent verification uses immutable schedule snapshots to prevent a running search from changing a builder input between proxy evaluation and circuit construction.

## 19:32 KST update

The ambiguity limitation above is now resolved. `ordered_objective.py` models both logical-basis DEMs, sorts ambiguous mechanisms by unrounded probability and flip-bit tie break, and applies the same maximum-probability matching as `joint_loss`. The previously unsupported case now solves `OPTIMAL` and agrees with the oracle (`general_test.log`). Across **152 generated order classes**, unrounded closed-form versus Stim Pearson correlation is **1.0**, maximum absolute error **1.3444106938820255e-17**, RMSE **4.813847344072555e-18** (`generated_complete_calibration_summary.json`). All these complete-objective optimizations use presolve disabled.

The broad orientation `[0,1,1]` short-depth search **timed out at 1800 seconds**, after **364,875** valid schedules. Best proxy remains `1.1274399214113765e-4`; the only safe complete-proxy lower bound for the unfinished search is **0**, so there is no global optimality claim. Orientation `[1,0,1]` was exhausted over **82,132** schedules with a worse optimum `1.2329167618816908e-4`. The new incumbent's LMAX 9 radius-3 neighborhood was exhausted over **13,451** valid schedules with no improvement. Further orientation and radius-4 searches are running.

`interleaved_top5.json` contains full-circuit official checks and fault scans of the five leading interleaved order classes at that checkpoint, using the immutable `interleaved_top5_schedules.json`. All five passed the official format, correctness, and acceptance checks. All five still fail literal `c1 == 0` by the same raw residue. A broader orientation expansion checked **2360** distinct schedules, retaining **908** Stim-valid schedules; its best 50 are in `candidate_pool.json` and are being refined.

`residue_audit.json` traces the baseline scan without changing any returned contribution: exactly five faults contribute `7.401486830834377e-18` each, with weight `1/15` and unweighted numerical infidelity `1.1102230246251565e-16`. The raw sum is `3.70074341541719e-17`; the scanner's `by_instruction` list is empty. This supports floating-point roundoff, but the requested literal acceptance criterion is still not overridden.
