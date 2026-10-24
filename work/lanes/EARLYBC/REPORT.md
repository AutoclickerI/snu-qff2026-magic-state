# EARLYBC report

The completion gate is met by **[reuse10.qasm](reuse10.qasm)** and [reuse10.json](reuse10.json): three-seed 100,000,000-shot mean **8.127370e-05**, seed-0 acceptance **0.54701964**, and PASS at 1,000,000 shots. This is a measured **2.63%** reduction from v17a's published three-seed mean 8.347295e-5 ([reference receipt](../MAIN/spec/mc3_v17.log)).

The winner starts the round at **R=49**, one actual judge step earlier than v17a. It retains the exact 82-CX B+C encoder, the 11-CX A encoder present in the source circuit, both readout re-encoding edges **17→16 and 19→25**, and all existing measurement-initialization records. It has the same 209 CX and six data hops. No block teleports were added. The target **R≤40 remains unachieved**; this report satisfies the first completion condition, not a universal infeasibility claim.

## What changed

The pre-stage's native X measurement on cell 10 leaves a known |+⟩ on accepted branches because c[8] is already postselected to zero. `reuse10` preserves that native MX with `h; measure; h`, removes the following reset, and implements the data-4 transfer with **CX 10→4; CX 4→10**. A two-CX transfer into |+⟩ uses this reverse order. The source cell is subsequently reset for the B encoder, as before. The judge's correctness check verifies the actual full circuit and detector conventions.

The hop runs at steps **33–34**, replacing **34–35**. Cell 4 is reset for B at 35 instead of 36; the B+C critical path and final round then move one step earlier. All other prefix operations retain their measured timing. `simplify.py` also commutes compatible CNOTs and reaches R=48 (`reuse10_commute`), but its measured three-seed mean ranks behind `reuse10`, despite a slightly lower third-order screen.

The unchanged per-qubit-order schedule has the exact critical chain recorded in [fixed_critical_path.json](fixed_critical_path.json): reset 10 at 33 → the two data-hop CXs → reset 4 at 36 → the B+C chain through its last CX at 49. Its earliest possible round is 50. Thus moving unrelated preparation gates earlier cannot shorten that chain.

## Source roles and geometry

In code order 0…6:

- Pre-stage data: `[0,20,7,4,3,15,8]`; round/output data: `[0,20,7,10,3,22,21]`.
- A: `[1,14,8,9,2,16,15]`; B: `[6,26,13,11,4,23,27]`; C: `[12,25,19,17,5,29,28]`.
- Data routes: `4→10`, `15→16→22`, `8→9→15→21`; the other four data qubits stay in place.
- B+C interaction path: `6–12–13–19–25–26–27–28–29–23–17–11–5–4`.
- A interaction tree: `1–2–8–14–15–16`, with the extra branch `8–9`.

At step 33, the available partners of the original data cells are: `0:(1, 6)`, `20:(14, 19, 21, 26)`, `7:(1, 6, 13)`, `4:(5, 10)`, `3:(2, 9)`, `15:(9, 14, 16, 21)`, `8:(2, 9, 14)`. Their union has 12 cells, so 14 simultaneous A/B partners require movement. B+C also conflicts with data cell 4, not only cell 6; cells 13 and 19 become available at 20 and 16.

Two source-metadata corrections were verified from the actual model text: q3's `T_DAG` is at **31**, the other six are at **32**; and the A encoder contains **11 CX** after its final initializations, although old metadata says 13. These do not change the baseline R=50 diagnosis. [v17a_source.check.json](v17a_source.check.json) records a fresh 1e6-shot source check.

## Schedules

Every step below comes from `tprep.noise.schedule(Model(...).text)`, independently of the builders; see [audit_schedule.py](audit_schedule.py), [schedule_summary.json](schedule_summary.json), and each `*.judge_schedule.json`. Preparation intervals include initialization. `c1 p` is exact2's printed first-order contribution at p=0.001, not the unscaled coefficient. All are numerically zero, so the third-order screen applies. “Exact total” means the exact expansion **through order three**, an estimate of the full noisy score; `exp(-A1)` is an acceptance estimate. Every row has a matching JSON containing `data_qubits` and a fresh `*.check.json` at 1e6 shots.

| Circuit | R | B+C prep | A prep | Moves (data/block) | CX | c1 p | 2nd | 3rd increment | Exact total through 3rd | exp(-A1) | 1e6 judge |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| [fixed_alap](fixed_alap.qasm) / [JSON](fixed_alap.json) | 50 | 35–49 | 43–49 | 6 / 0 | 209 | 3.183e-19 | 5.707720e-05 | 2.537690e-05 | 8.245410e-05 | 0.54287 | PASS (0.542591) |
| [reuse10](reuse10.qasm) / [JSON](reuse10.json) | 49 | 34–48 | 42–48 | 6 / 0 | 209 | 3.183e-19 | 5.672400e-05 | 2.350700e-05 | 8.023110e-05 | 0.54681 | PASS (0.547243) |
| [reuse10_commute](reuse10_commute.qasm) / [JSON](reuse10_commute.json) | 48 | 32–47 | 41–47 | 6 / 0 | 209 | 3.183e-19 | 5.727610e-05 | 2.282780e-05 | 8.010390e-05 | 0.54795 | PASS (0.547713) |
| [reuse9_10](reuse9_10.qasm) / [JSON](reuse9_10.json) | 49 | 34–48 | 42–48 | 6 / 0 | 209 | 3.183e-19 | 5.672400e-05 | 2.463180e-05 | 8.135580e-05 | 0.54590 | PASS (0.545983) |
| [reuse9_10_15](reuse9_10_15.qasm) / [JSON](reuse9_10_15.json) | 49 | 34–48 | 42–48 | 6 / 0 | 209 | 3.183e-19 | 6.274980e-05 | 2.434730e-05 | 8.709710e-05 | 0.54630 | PASS (0.545508) |
| [reuse9_10_15_6](reuse9_10_15_6.qasm) / [JSON](reuse9_10_15_6.json) | 49 | 32–48 | 42–48 | 6 / 0 | 209 | 3.183e-19 | 6.308260e-05 | 2.484190e-05 | 8.792450e-05 | 0.54539 | PASS (0.544798) |
| [commute](commute.qasm) / [JSON](commute.json) | 49 | 33–48 | 42–48 | 6 / 0 | 209 | 3.183e-19 | 5.768050e-05 | 2.462400e-05 | 8.230450e-05 | 0.54400 | PASS (0.543860) |
| [cancel_alap](cancel_alap.qasm) / [JSON](cancel_alap.json) | 50 | 35–49 | 43–49 | 6 / 0 | 205 | 3.183e-19 | 5.732620e-05 | 2.565370e-05 | 8.297990e-05 | 0.54129 | PASS (0.540437) |
| [cancel_commute](cancel_commute.qasm) / [JSON](cancel_commute.json) | 49 | 33–48 | 42–48 | 6 / 0 | 205 | 3.183e-19 | 5.814100e-05 | 2.490460e-05 | 8.304560e-05 | 0.54242 | PASS (0.542366) |
| [mx_init](mx_init.qasm) / [JSON](mx_init.json) | 50 | 35–49 | 43–49 | 6 / 0 | 209 | 3.183e-19 | 5.687720e-05 | 2.499840e-05 | 8.187560e-05 | 0.54359 | PASS (0.543576) |
| [partial24](partial24.qasm) / [JSON](partial24.json) | 49 | 24–48 | 42–48 | 6 / 0 | 209 | 3.183e-19 | 8.412260e-05 | 3.963700e-05 | 1.237600e-04 | 0.48510 | FAIL acceptance (0.485778) |
| [partial15](partial15.qasm) / [JSON](partial15.json) | 49 | 15–48 | 42–48 | 6 / 0 | 209 | 3.183e-19 | 1.478710e-04 | 5.692960e-05 | 2.048010e-04 | 0.44270 | FAIL acceptance (0.443306) |

## Finalists ranked only by 1-F

Each MC column is 1e8 shots with STANDARD noise and the actual grid. Runs use `fast_check.check`, the repository's judge-equivalent chunked sampler, after `tprep.check(..., shots=10**6)` in [mc_rank.py](mc_rank.py). Acceptance above 0.5 does not enter the ranking. Source records and standard errors are retained in each `*.mc.json`.

| Circuit | Seed 0 | Seed 1000 | Seed 2000 | Mean | Seed-0 acceptance | Files |
|---|---:|---:|---:|---:|---:|---|
| **reuse10** | 8.194404e-05 | 7.944132e-05 | 8.243573e-05 | 8.127370e-05 | 0.54701964 | [QASM](reuse10.qasm), [JSON](reuse10.json), [MC](reuse10.mc.json), [check](reuse10.check.json) |
| reuse9_10 | 8.222870e-05 | 8.190005e-05 | 8.464772e-05 | 8.292549e-05 | 0.54603803 | [QASM](reuse9_10.qasm), [JSON](reuse9_10.json), [MC](reuse9_10.mc.json), [check](reuse9_10.check.json) |
| reuse10_commute | 8.356062e-05 | 8.299209e-05 | 8.253062e-05 | 8.302778e-05 | 0.54810509 | [QASM](reuse10_commute.qasm), [JSON](reuse10_commute.json), [MC](reuse10_commute.mc.json), [check](reuse10_commute.check.json) |
| mx_init | 8.280201e-05 | 8.518379e-05 | 8.418470e-05 | 8.405683e-05 | 0.54376701 | [QASM](mx_init.qasm), [JSON](mx_init.json), [MC](mx_init.mc.json), [check](mx_init.check.json) |
| cancel_commute | 8.487588e-05 | 8.426959e-05 | 8.436443e-05 | 8.450330e-05 | 0.54261585 | [QASM](cancel_commute.qasm), [JSON](cancel_commute.json), [MC](cancel_commute.mc.json), [check](cancel_commute.check.json) |
| commute | 8.514890e-05 | 8.471857e-05 | 8.368158e-05 | 8.451635e-05 | 0.54422311 | [QASM](commute.qasm), [JSON](commute.json), [MC](commute.mc.json), [check](commute.check.json) |

## Wait, idle, and movement trade-off

`reuse10` saves one step of pre-round data exposure, adds **zero** CX and **zero** moves, and removes one reset. B+C idle exposure after its initializations and before the round is **28 → 28 qubit-steps**; A idle exposure is **12 → 12**. These counts come from the judge's idle gaps, not wall-clock scheduling. The second-order contribution falls from 5.70772e-5 to 5.67240e-5, and the third-order increment from 2.53769e-5 to 2.35070e-5. The measured total third-order-screen gain is 2.2230e-6. This jointly prices the earlier round and reset replacement; it is not an isolated noiseless-wait ablation.

The partial-overlap tests move every available B+C operation ASAP from a lower bound of 24 or 15 while respecting released cells and the fixed gate order. They actually overlap the pre-stage but still finish at 48 and reach R=49 because cell 4 remains on the critical path. Their B+C idle exposures rise to **152** and **254 qubit-steps** respectively, versus **28** in the winner. Both fail the official acceptance gate: **0.485778** and **0.443306** at 1e6 shots. Their exact screens are 1.237600e-04 and 2.048010e-04. These two tested partial-overlap schedules are worse; other branch timings and relocation remain open.

Reusing cell 9 as well gives no further R reduction and a worse mean. Reusing cell 15 after an earlier data transfer raises the measured second-order contribution. Propagation of residual transfer errors into the next data token is the mechanism inferred from the CX directions; this variant is rejected by score. Removing the two cancellable CX pairs also fails to improve the measured ranking. X-basis measurement initialization of all six B+C pivots is correctness-valid with propagated record frames (`mx_init`), but its three-seed mean is worse than the winner.

## Placement and teleport-routing search coverage

The search retained the original encoder interaction graphs and both re-encoding adjacencies. CP-SAT presolve was disabled throughout, following the documented OR-Tools failure mode. Static Manhattan objectives are placement proxies, not score or schedule measurements.

- **Stationary block embedding:** [place_released_0.json](place_released_0.json) is INFEASIBLE for B+C in the 21 never-used cells plus released cells 13/19, A with its unchanged tree, data at Manhattan distance ≤4 from its pre-stage positions, and both readout edges. The never-used-only domain is a subset. This proof is limited to that fixed-label, no-block-move model.
- **All A/B/C staged early:** [stage_0.receipt.json](stage_0.receipt.json) / [stage_0_60.json](stage_0_60.json) achieve the static optimum 60 for `sum(block Manhattan distances) + 3*sum(data Manhattan distances)`. Preparation fits the free cells, but the routing model reserves each source through its measurement and each destination from initialization. For this placement, [route0.receipt.json](route0.receipt.json) is INFEASIBLE at R≤43 with ≤3 block hops and ≤2 data hops per token. [route1.receipt.json](route1.receipt.json) remains INFEASIBLE at R≤45 with ≤4/3 hops. With ≤6/4 hops and R≤50, [route3.receipt.json](route3.receipt.json) is UNKNOWN; its objective bound implies R≥48 **for that model and starting placement**, with no feasible routing witness found.
- **A allowed in released pre-stage ancilla cells:** static optimum 52 in [stage_2_52.json](stage_2_52.json); its A preparation is only ready at 40 on several wires. [route2.receipt.json](route2.receipt.json) is INFEASIBLE at R≤46 with ≤4 block / 3 data hops per token.
- **Code-coordinate automorphisms:** [autostage.py](autostage.py) allows the 168 Steane coordinate automorphisms for A and B/C independently. The placement search found cost 46 with lower bound 26, not an optimum ([receipt](autostage_0.receipt.json)). Routing the earlier cost-50 incumbent failed at R≤44 in [autoroute0.receipt.json](autoroute0.receipt.json). Later placements have not been routed. This remains an open route to R≤40.

No time-expanded teleport schedule was found, so no full teleport circuit or MC performance is claimed. [route.py](route.py) and the route-assembly branch of [build.py](build.py) remain experimental. The completion condition is satisfied by the measured winner; the global relocation family is not proved exhausted.

## Reproduction and verification

From the repository root, use `.venv/bin/python` with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`:

- `work/lanes/EARLYBC/reuse.py` builds the winner and the other reuse variants from v17a.
- `work/lanes/EARLYBC/evaluate.py 8 reuse10` runs the 1e6-shot judge and `EVAL/exact2.py --third`.
- `work/lanes/EARLYBC/mc_rank.py 8 reuse10` runs the required three 1e8-shot seeds.
- `work/lanes/EARLYBC/audit_schedule.py` independently extracts steps from every candidate's exact model text.

All circuit artifacts, solver receipts, scripts, checks, and MC results are in this lane. No submission, commit, push, credential access, or sub-agent action was performed. Zebra and hippo worker limits were respected; all launched jobs were collected on process completion. [manifest.json](manifest.json) records the delivered QASM/JSON hashes and check status.
