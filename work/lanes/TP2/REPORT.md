# TP2 report

**No candidate met the required improvement. The success condition was not met.** No submission was made.

The smallest full circuit built has teleport couplings at **33–47**, last round CX **48**, and final measurement **49**. It passes format, class and correctness, but fails acceptance and is much noisier than v16. The smallest fully judge-valid new circuit starts at **50**. The best new candidate measured at 1e8 shots on all three seeds is `tp_v16_reuse`: mean **1.74393709220e-4**, seed-0 acceptance **0.50536187**, versus v16's **8.55379233064e-5** and **0.53313237**.

The relaxed CP-SAT routing minimum is **last CX 41**, with teleport couplings **33–40**, 17 two-CX transfers, and final measurement 42. Last CX <=40 is INFEASIBLE with presolve disabled, even with preparation connectivity and C omitted and immediate reuse of measured prefix cells allowed. This is a conditional bound for the model described below, not a general circuit impossibility result.

## Candidate measurements

All exact values use EVAL/exact2.py `--third`, and every c1 is below 1e-12. c1 is its contribution at p=0.001. Third means the incremental third-order term. `exp(-A1)` is an analytical **estimate**. R is **first teleport CX / last teleport CX / last round CX**, not a claim that the complete round ran at its first coupling. Every QASM has adjacent JSON listing the final physical cells of logical O in code order. All six candidates passed format/class/correctness at 1e6 shots. MC columns are 100,000,000 shots each; dashes mean not run. None had exact total <8.6e-5, so no mandatory MC is outstanding. Only measured MC means establish ranking.

| Candidate | R first / last / last CX | CX | c1 p | 2nd | 3rd increment | Exact total | exp(-A1), estimate | MC 0 | MC 1000 | MC 2000 | MC mean | Seed-0 acceptance, 1e8 | Acceptance, 1e6 | Judge, 1e6 | Files |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| [tp_v16](tp_v16.qasm) | 50 / 50 / 55 | 221 | 9.542e-19 | 0.000224041 | 4.55656e-05 | 0.000269607 | 0.50501 | — | — | — | — | — | 0.505265 | PASS | [tp_v16.json](tp_v16.json) · [receipt](tp_v16.score.json) |
| [tp_v16_omove](tp_v16_omove.qasm) | 50 / 50 / 55 | 221 | 8.0666e-19 | 0.000175932 | 4.57919e-05 | 0.000221724 | 0.4957 | — | — | — | — | — | 0.495791 | FAIL acceptance | [tp_v16_omove.json](tp_v16_omove.json) · [receipt](tp_v16_omove.score.json) |
| [tp_v16_reuse](tp_v16_reuse.qasm) | 50 / 50 / 54 | 221 | 6.5873e-19 | 0.000130164 | 3.97289e-05 | 0.000169893 | 0.50501 | 0.000173568694 | 0.000176003531 | 0.000173608902 | 0.000174393709 | 0.50536187 | 0.505376 | PASS | [tp_v16_reuse.json](tp_v16_reuse.json) · [receipt](tp_v16_reuse.score.json) |
| [tp_joint52](tp_joint52.qasm) | 33 / 47 / 48 | 286 | 3.2629e-18 | 0.00193537 | 9.30512e-06 | 0.00194468 | 0.47662 | — | — | — | — | — | 0.47812 | FAIL acceptance | [tp_joint52.json](tp_joint52.json) · [receipt](tp_joint52.score.json) |
| [tp_joint52_m11_21_22](tp_joint52_m11_21_22.qasm) | 33 / 47 / 48 | 286 | 3.2629e-18 | 0.00193536 | 9.04466e-06 | 0.0019444 | 0.47424 | — | — | — | — | — | 0.474432 | FAIL acceptance | [tp_joint52_m11_21_22.json](tp_joint52_m11_21_22.json) · [receipt](tp_joint52_m11_21_22.score.json) |
| [tp_joint52_alap](tp_joint52_alap.qasm) | 33 / 47 / 48 | 286 | 3.2621e-18 | 0.00191421 | 1.38943e-05 | 0.0019281 | 0.47538 | — | — | — | — | — | 0.476666 | FAIL acceptance | [tp_joint52_alap.json](tp_joint52_alap.json) · [receipt](tp_joint52_alap.score.json) |
| [v16 reference](../../candidates/v16_bc2m.qasm) | 50 / 50 / 51 (star) | 207 | 3.1826e-19 | 5.83953e-05 | 2.58031e-05 | 8.41984e-05 | 0.53306 | 8.61136982e-05 | 8.52861662e-05 | 8.52139056e-05 | 8.55379233e-05 | 0.53313237 | 0.532286 | PASS | [cached same-text receipt](baseline_receipt.json) |

The baseline numbers are R0's completed same-seed run, reused after verifying its QASM SHA-256 matches `work/candidates/v16_bc2m.qasm`; TP2 did not claim a second independent baseline run. Reuse's full MC receipt is [tp_v16_reuse.mc.json](tp_v16_reuse.mc.json).

## Geometry and construction

O/B/C columns give cells at preparation completion. `Output O` gives cells after all transfers, and equals the JSON `data_qubits`. A move is one two-CX transfer; v16-derived rows include its six data moves plus seven additional transfers. The joint family leaves the original data unmoved and transfers O/B 34 times.

| Candidate | O prep cells | B prep cells | C prep cells | Output O | Moves |
|---|---|---|---|---|---:|
| tp_v16 | [1, 14, 8, 9, 2, 16, 15] | [6, 26, 13, 11, 4, 23, 27] | [12, 25, 19, 17, 5, 29, 28] | [1, 14, 8, 9, 2, 16, 15] | 13 |
| tp_v16_omove | [1, 14, 8, 9, 2, 16, 15] | [6, 26, 13, 11, 4, 23, 27] | [12, 25, 19, 17, 5, 29, 28] | [0, 20, 7, 10, 3, 22, 21] | 13 |
| tp_v16_reuse | [1, 14, 8, 9, 2, 16, 15] | [6, 26, 13, 11, 4, 23, 27] | [12, 25, 19, 17, 5, 29, 28] | [0, 20, 7, 10, 3, 22, 21] | 13 |
| tp_joint52 | [16, 22, 28, 5, 11, 21, 17] | [12, 32, 24, 34, 23, 33, 31] | [18, 26, 30, 35, 29, 27, 25] | [1, 26, 13, 16, 11, 21, 20] | 34 |
| tp_joint52_m11_21_22 | [16, 22, 28, 5, 11, 21, 17] | [12, 32, 24, 34, 23, 33, 31] | [18, 26, 30, 35, 29, 27, 25] | [1, 26, 13, 16, 11, 21, 20] | 34 |
| tp_joint52_alap | [16, 22, 28, 5, 11, 21, 17] | [12, 32, 24, 34, 23, 33, 31] | [18, 26, 30, 35, 29, 27, 25] | [1, 26, 13, 16, 11, 21, 20] | 34 |

`tp_joint52` uses EXENC's exhaustive 7-cell O encoder: **12 CX, depth 8, danger 0.0008**. The minimum-CX proof is 11 and minimum depth is 6; the selected 12-CX circuit has the lower enumerated danger. Receipts: [joint52_O.json](joint52_O.json), [stats](joint52_O_stats.json). Separate B/C connected regions with direct initial pairings cannot be packed alongside O; the constructed alternative is a **104-CX, 22-layer joint B+C** encoder. BC2's independent fault checker finds **0 base-rule violations**, **64 clean-rule violations**, and **62 robust-rule violations**. Full exact c1 also confirms first-order safety. The depth-16 clean search timed out after adding 82 fault constraints: [receipt](joint52_BC16clean.receipt.json). This is not an UNSAT result.

C checks B at step 30 and is measured at 31, releasing routing space. The round then transfers O to data neighbours, measures data in place, transfers O where necessary, and applies B->O. The builder schedules actual per-cell prep gates ALAP, rather than initializing all blocks at time zero. `alap.py` also optimizes fixed-route gate times to shorten O's post-teleport exposure; it preserves the minimum final CX 48. `tp_joint52_m11_21_22` uses MAIN/minit.py on O's three nonpivot first-use Z resets. Its exact total is slightly lower than the base, with lower acceptance; it cannot rescue the acceptance failure. The original v16 prefix is preserved even in this variant.

`check_prefix.py` independently converts every full candidate with the judge and verifies all **137 native prefix operations** have identical gates, cells and times 0–32 to v16. Each candidate's `.prefix.json` is a receipt. `audit_route.py` checks routing cell occupancy, move/reset conflicts, adjacency, and logical operation ordering. It does not certify a missing encoder.

## A validated exception to the output-offset warning

`tp_v16_reuse` removes the reset between measuring D and transferring O into those same D cells. Its two-CX transfer leaves an X^m offset on the transferred block. The three declared D parity checks ensure accepted m is a Hamming codeword; X^m is therefore an X stabilizer times X_L raised to parity(m). This cancels the teleport X_L frame. The candidate declares an empty X frame, and **the judge confirms correctness**, c1 is negligible, and acceptance passes at 1e8 shots. This is a validated codeword/frame cancellation, not permission to leave an arbitrary untracked offset on output. No project rule/document was changed. It saves one step against the reset-based O transfer but remains above v16.

## Solver domain, receipts and binding constraint

`route.py` reserves both cells for every two-CX move, explicitly reserves destination reset, releases each data cell only after its actual Z measurement, permits O moves after teleportation, and requires B->O after the final O move. The initial O/B sites are in the 21 never-used cells. Prefix cells remain occupied through step 32. `--fast-prefix` allows a first transfer at 33 into a released, measured prefix cell without reset; MX destinations use the dual transfer. Bounds allow four transfers per token, more than fit before last CX 40 at two steps per transfer. C and encoder connectivity are omitted in the relaxed bound. Later reuse of moved-from known states without reset, routing before 33, arbitrary interleaved encoders and changes to the unchanged prefix are outside that bound.

| Receipt | Status | Wall seconds | First O->D | Last O->D | Last round CX | Moves |
|---|---|---:|---:|---:|---:|---:|
| [bound40](bound40.json) | INFEASIBLE | 1.48949929 | — | — | — | — |
| [best41](best41.json) | OPTIMAL | 5.96678851 | 33 | 40 | 41 | 17 |
| [fast_bound40](fast_bound40.json) | INFEASIBLE | 2.3040384 | — | — | — | — |
| [fast41](fast41.json) | OPTIMAL | 9.1463865 | 33 | 40 | 41 | 17 |
| [joint52](joint52.json) | FEASIBLE | 240.160872 | 33 | 47 | 48 | 34 |
| [joint52_alap](joint52_alap.json) | OPTIMAL | 0.0158297 | 33 | 47 | 48 | 34 |
| [full52](full52.json) | UNKNOWN | 240.202551 | — | — | — | — |
| [full56table](full56table.json) | UNKNOWN | 240.197807 | — | — | — | — |
| [full56first](full56first.json) | UNKNOWN | 180.187149 | — | — | — | — |
| [full48relax](full48relax.json) | UNKNOWN | 180.103858 | — | — | — | — |
| [fixed60](fixed60.json) | UNKNOWN | 180.157431 | — | — | — | — |

The binding geometric issue is access to the upper-left data while keeping O and B live: releasing D helps, but O must sometimes retreat after its first coupling to admit B. The relaxed optimum has 17 transfers before adding any C preparation/routing. Exhaustive connected-region enumeration finds 677 seven-cell regions in the unused footprint and 168 ordered three-region partitions, but **zero** partitions admitting all seven direct B–C pairings. It also finds zero sequential separate B/C connected preparations with O's reserved region under the tested staging assumptions. Receipts: [packing.json](packing.json), [staged_packing.json](staged_packing.json), [helper_packing.json](helper_packing.json), [three_partitions.json](three_partitions.json).

`fullroute.py` explicitly retains C, reserves its moves and measurements, and limits the B–C-to-B–O gap. Runs with last-CX horizons 51/55 and gap 3/4/6 timed out without a solution; a fully fixed initial placement at horizon 59 and gap 8 also timed out. UNKNOWN is not evidence of impossibility. `joint52` is the completed alternative with C consumed before routing. It exposes B for 13–18 steps after its check and some O qubits for many steps after teleportation. That exposure and transfers dominate the saved pre-round data wait.

## Exact loss attribution

[price.py](price.py) uses MAIN/ablate.py's exact scoring engine with moving-token labels and splits each aggregated idle gap at label boundaries. Static `--a` and final-output data labels would misclassify these circuits, since O moves and preparation overlaps steps 0–32. Each row removes the named region's noise; changes are not additive.

| Region made noiseless | 2nd | 3rd | Total | exp(-A1), estimate |
|---|---:|---:|---:|---:|
| O_exposed | 0.000741758758 | 4.29446836e-05 | 0.000784703441 | 0.489997352 |
| B_exposed | 0.000596372799 | 3.87411049e-05 | 0.000635113904 | 0.513788937 |
| prep | 0.00136131235 | -4.8902958e-05 | 0.00131240939 | 0.625813427 |

Making O’s exposed region noiseless lowers the exact total from 1.94468e-3 to 7.84703441e-4; making B’s exposed region noiseless lowers it to 6.35113904e-4. Removing preparation noise alone leaves 1.31240939e-3. These measurements identify post-check exposure as the principal failure of this construction. Full receipt: [tp_joint52.price.json](tp_joint52.price.json). `O_exposed` includes O's teleport coupling, subsequent movement, B coupling and tail; `B_exposed` includes B after its early C check through readout; `prep` is unused-footprint preparation and C check/readout outside those categories. The original-prefix region is independently identified by cells and times.

## Reproduction and scope

Run from the repository root with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`. Check host capacity before each launch. All files/caches generated here stay in TP2; R0/LAYOUT3 were read only. MAIN/REPORT.md does not exist; the requested MAIN tools and measurement receipts were read. No credentials were accessed, no agents were spawned, and nothing was submitted.

```sh
.venv/bin/python work/lanes/TP2/route.py --horizon 41 --hops 4 --connect none --postmove --no-presolve --fast-prefix --workers 2 --out work/lanes/TP2/recheck_bound40.json
.venv/bin/python work/lanes/TP2/build.py work/lanes/TP2/joint52.json work/lanes/TP2/rebuilt --o work/lanes/TP2/joint52_O.json --bc work/lanes/TP2/joint52_BC22.prep.json
.venv/bin/python work/lanes/TP2/evaluate.py rebuilt --procs 5
.venv/bin/python work/lanes/TP2/teleport_v16.py reuse
.venv/bin/python work/lanes/TP2/mc.py tp_v16_reuse 8
```

`evaluate.py` runs the 1e6 judge first, exact third-order screen next, and automatically runs three MC seeds for every exact total below 8.6e-5 or nonzero c1. `manifest.json` verifies this gate for every generated candidate. The six candidates above are the complete generated-QASM set. The remaining opening is an encoder/routing schedule that keeps C verification late and avoids O's prolonged exposure after teleportation; the present bounded searches do not close it.
