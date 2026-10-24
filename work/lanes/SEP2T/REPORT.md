# SEP2T — separate blocks built and priced

Best measured three-seed circuit: **[abstract_final](abstract_final.qasm)**, mean **1.775699e-04** at 1e8 shots per seed; seed-0 acceptance **0.37764**. It **fails the 0.5 acceptance gate** and does not beat v19’s supplied mean 7.537e-5. No eligible improvement was found. The broad separate-block question remains open; the completed work satisfies the build/price/breakdown branch, not a global impossibility proof.

All reported circuits use the real 6×6 grid, separate A/B/C preparation, correct teleport-frame detectors, and native ALAP timing. Every reported circuit received the full 1e6-shot judge. No submission, commit, push, credential access, sub-agent, or write to another lane was performed.

## Models and searches

“INFEASIBLE” applies only to the stated formulation and bounds. TIMEOUT is never called UNSAT. Interrupted searches are identified explicitly. A placement proxy or abstract preparation duration is not a native circuit measurement.

| Method | Budget | Status | Best schedule found |
|---|---|---|---|
| Arbitrary connected seven-cell graphs; one-hop moves into initial holes | 240 s / 2 workers | [TIMEOUT](connected_h1.receipt.json) | none |
| 10-CX LAYOUT3 encoder graphs; one-hop placement relaxation | 120 s cap / 1 worker | [FEASIBLE placement relaxation](geom_l3_h1.json) | placement only; no timing claim |
| 10-CX graphs; complete lifetimes, early A, one block hop, ≤2 data hops, R≤80 | 240 s cap / 2 workers | [INFEASIBLE](l3_h1_time.receipt.json) | none |
| Arbitrary connected graphs; one-hop relocation chains | 600 s / 8 workers | [TIMEOUT](connected_chain_h1.receipt.json) | none |
| Original FREELAY L5 two-teleport model, r0c0, fixed labels, no early A, ≤2 data hops, R≤60 | 3600 s cap / 6 workers; proof in 2618.1 s | [INFEASIBLE](long_h2_r0c0.receipt.json) | none; bounded-model infeasibility proof |
| 10-CX graphs, two block hops, early A, ≤3 data hops, R≤80 | 3600 s planned / 16 workers; interrupted at 1177 s | [INTERRUPTED](long_l3_h2.receipt.json) | no incumbent |
| Fixed L5 endpoints; exact vacancy routing, first solution | 600 s cap / 6 workers; first solution 1.36 s | [FEASIBLE](routed_auto.receipt.json) | 122 teleports; pruned build 72, native R73 |
| Same routing, optimization with complete feasible hint | 600 s / 6 workers | [FEASIBLE](routed_auto_opt.receipt.json) | 54 teleports, lower bound 46; checked native R63 |
| Free final positions, in-place A, separately staged B/C, code automorphisms | 180 s / 2 workers | [FEASIBLE](free_l3_auto.receipt.json) | proxy65: 7 data + 30 block Manhattan distance |
| Route that placement with stationary final data | 600 s cap / 4 workers | [INFEASIBLE](routed_free.receipt.json) | 16 batches and ≤60 moves: infeasible in this bound |
| Connected-cell timing model, six-step placeholder encoders, two block hops | 1200 s planned / 6 workers; stopped at 511 s to build | [FEASIBLE_ABSTRACT_PLACEMENT](abstract_h2.receipt.json) | 21 block + 12 data moves; exact encoders rebuilt at native R56 |
| 10-CX graphs; block CX chains may overlap preceding source measurement | 1800 s + ≤30 s tie-break / 4 workers | [FEASIBLE; ALAP tie-break TIMEOUT](pipeline_l3_h2.receipt.json) | checked reconstruction: native R56, 24 block + 13 data moves |
| Allow measured A endpoints to be reused by B/C; first solution | 1800 s cap + ≤30 s tie-break / 16 workers | [FEASIBLE; ALAP tie-break TIMEOUT](reuseA_l3_h2.receipt.json) | checked native A50 / BC74; 39 block moves |
| Optimize A-cell reuse with complete witness hint | 1200 s planned / 16 workers; interrupted at 493 s | [FEASIBLE_INTERRUPTED](reuseA_opt.receipt.json) | checked native A45 / BC58; 29 block moves |
| Real EXENC A15/B15/C12 graphs, complete timing/routing, two block hops | 1200 s + ≤30 s tie-break / 16 workers | [FEASIBLE; ALAP tie-break TIMEOUT](general_exact_h2.receipt.json) | checked general_final native R51, 27 block + 16 data moves |
| Constructive vacancy clearing, independent 11-CX blocks | 3000 trials | FEASIBLE | 87 teleports, native R100; `route_l5` |
| EXENC on the actual A graph, pure-logical danger prioritized before correlated danger | all 6,303,146 canonical paths at 12–15 CX; 3 workers | EXHAUSTIVE for these path classes / ASAP schedules | A15, depth7, danger vector `[0,7,0,0,7,0,0,0]`; no class skipped |

The prior FREELAY one-hop infeasibility results remain limited to its fixed encoder families and final-cell assumptions. Its two-hop timeouts were not proofs. This lane found actual two-hop placement witnesses using different encoder graphs. It also identified two restrictive timing assumptions: successive block teleports can overlap the prior source measurement, and early-measured A endpoints can be reused. The latter is governed by lifetime occupancy, rather than a global final-cell distinctness constraint.

The first abstract timing witness used a six-step preparation allowance. Actual EXENC preparations were inserted in expanded ticks and the complete circuit was rescheduled and checked. Its model R is never substituted for native R. An old pipelining formulation also allowed a skipped terminal move to relax a coupling deadline; this was corrected to depend on the last actual move. Older witnesses were reconstructed with explicit physical dependencies before reporting.

## Full circuits

R is **A coupling / B→C check**, read from the judge’s native schedule; B→data follows B→C by one step. Moves are data hops / one-CX block teleports. c1 is the first-order contribution at p=0.001; 2nd and 3rd are increments. “Exact total” is through order three, and is omitted when |c1|≥1e-12. exp(-A1) is an acceptance **estimate**. MC seeds are 0/1000/2000, each at 1e8 shots. Acceptance-failing results are diagnostics, not eligible ranked submissions.

| Circuit | R native A/BC | CX | Moves D/block | c1 | 2nd | 3rd | Exact total | exp(-A1), estimate | MC seeds → mean | Seed-0 acceptance | Files |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| abstract_final | 56/56 | 183 | 12/21 | 2.9236e-19 | 8.75571e-05 | 8.05378e-05 | 0.000168095 | 0.37703 | 0.0001780006 / 0.0001780316 / 0.0001766776 → **0.0001775699** | 0.37764 (1e8); FAIL | [QASM](abstract_final.qasm), [JSON](abstract_final.json), [check](abstract_final.check.log), [exact](abstract_final.exact.log) |
| abstract_trim | 56/56 | 183 | 12/21 | 2.9236e-19 | 8.76625e-05 | 8.05357e-05 | 0.000168198 | 0.37698 | 0.0001799381 / 0.0001807188 / 0.0001802428 → **0.0001802999** | 0.37757 (1e8); FAIL | [QASM](abstract_trim.qasm), [JSON](abstract_trim.json), [check](abstract_trim.check.log), [exact](abstract_trim.exact.log) |
| abstract_cleanA | 56/56 | 183 | 12/21 | 2.9236e-19 | 8.76625e-05 | 8.29072e-05 | 0.00017057 | 0.35961 | 0.0001815413 / 0.0001797621 / 0.0001819821 → **0.0001810951** | 0.36006 (1e8); FAIL | [QASM](abstract_cleanA.qasm), [JSON](abstract_cleanA.json), [check](abstract_cleanA.check.log), [exact](abstract_cleanA.exact.log) |
| routed56 | 63/63 | 195 | 6/54 | 2.9236e-19 | 9.55038e-05 | 0.000136904 | 0.000232408 | 0.28975 | 0.0002649274 / 0.0002580225 / 0.0002620552 → **0.0002616684** | 0.29119 (1e8); FAIL | [QASM](routed56.qasm), [JSON](routed56.json), [check](routed56.check.log), [exact](routed56.exact.log) |
| abstract_built | 56/56 | 181 | 12/21 | 0.00026667 | 0.00014019 | — | — | 0.35843 | 0.0005292569 / 0.0005162323 / 0.0005240106 → **0.0005231666** | 0.3590884 (1e8); FAIL | [QASM](abstract_built.qasm), [JSON](abstract_built.json), [check](abstract_built.check.log), [exact](abstract_built.exact.log) |
| general_final | 51/51 | 197 | 16/27 | 2.3315e-19 | 0.00011456 | 7.62629e-05 | 0.000190823 | 0.40701 | — | 0.408148 (1e6); FAIL | [QASM](general_final.qasm), [JSON](general_final.json), [check](general_final.check.log), [exact](general_final.exact.log) |
| general51 | 52/52 | 197 | 16/27 | 2.3315e-19 | 0.000135439 | 8.86978e-05 | 0.000224137 | 0.38138 | — | 0.381903 (1e6); FAIL | [QASM](general51.qasm), [JSON](general51.json), [check](general51.check.log), [exact](general51.exact.log) |
| pipeline_alap | 56/56 | 176 | 13/24 | 2.3315e-19 | 0.000155394 | 0.000182722 | 0.000338116 | 0.40108 | — | 0.402474 (1e6); FAIL | [QASM](pipeline_alap.qasm), [JSON](pipeline_alap.json), [check](pipeline_alap.check.log), [exact](pipeline_alap.exact.log) |
| routed_auto_pruned | 73/73 | 213 | 6/72 | 2.9236e-19 | 0.000126354 | 0.000252505 | 0.000378859 | 0.22233 | — | 0.224406 (1e6); FAIL | [QASM](routed_auto_pruned.qasm), [JSON](routed_auto_pruned.json), [check](routed_auto_pruned.check.log), [exact](routed_auto_pruned.exact.log) |
| reuseA_refined | 45/58 | 165 | 5/29 | 1.1877e-18 | 0.000494388 | 0.000149274 | 0.000643662 | 0.40701 | — | 0.408329 (1e6); FAIL | [QASM](reuseA_refined.qasm), [JSON](reuseA_refined.json), [check](reuseA_refined.check.log), [exact](reuseA_refined.exact.log) |
| l2_alap | 59/59 | 180 | 10/0 | -4.9352e-34 | 0.000655174 | 0.000137522 | 0.000792697 | 0.40837 | — | 0.408833 (1e6); FAIL | [QASM](l2_alap.qasm), [JSON](l2_alap.json), [check](l2_alap.check.log), [exact](l2_alap.exact.log) |
| route_l5 | 100/100 | 228 | 6/87 | 2.9236e-19 | 0.00013731 | 0.00084274 | 0.00098005 | 0.10984 | — | 0.114528 (1e6); FAIL | [QASM](route_l5.qasm), [JSON](route_l5.json), [check](route_l5.check.log), [exact](route_l5.exact.log) |
| reuseA_alap | 50/74 | 185 | 10/39 | 1.9696e-18 | 0.00112711 | 0.000446945 | 0.00157405 | 0.3427 | — | 0.344449 (1e6); FAIL | [QASM](reuseA_alap.qasm), [JSON](reuseA_alap.json), [check](reuseA_alap.check.log), [exact](reuseA_alap.exact.log) |

`general_alap` was independently checked at 1e6 shots and then proved equivalent to `abstract_cleanA` by identical native operations/times, detector declarations, and data ordering. Only simultaneous written operation order differs; its redundant exact run was stopped, and no separate score is claimed ([receipt](general_alap.equivalence.json)).

## Measured loss breakdown

For **abstract_final**, the exact-through-third total is **1.680949257e-04**. With one region noiseless:

- **idle**: 4.683672904e-05; reduction 1.212581966e-04 (72.14%).
- **moves**: 1.340459087e-04; reduction 3.404901694e-05 (20.26%).
- **pre**: 1.522571705e-04; reduction 1.583775515e-05 (9.42%).
- **prep_a**: 1.212743772e-04; reduction 4.682054849e-05 (27.85%).
- **prep_b**: 1.593509983e-04; reduction 8.743927395e-06 (5.20%).
- **prep_c**: 1.606594229e-04; reduction 7.435502816e-06 (4.42%).
- **round**: 1.139852501e-04; reduction 5.410967556e-05 (32.19%).

These marginal reductions overlap and must not be added: faults in different regions interact. Idle is every pre-round idle channel; round includes the final data idle. Preparation/teleport/prefix operation noise is assigned by operation provenance, not a time cut. B and C remain independently prepared even when their encoder cells are reused at different times.
[Full ablation](abstract_final.ablation.json), [log](abstract_final.ablation.log), [second-order region pairs](abstract_final.pairs.json).

The native schedules show long live-state exposure while cells are released and blocks move; its cost is measured above. On `abstract_cleanA`, making pre-round idle noiseless lowers the third-order total from 1.705697e-4 to 4.683673e-5. That is an ablation, not a realizable score. Native R alone is insufficient: `general51` starts earlier while adding data hops and teleports, and its measured screen is worse.

## Verification, decisions, and limits

- B→C immediately precedes B→data in every build. Teleport measurement records are XORed into A’s Z checks or B’s X checks; C’s Z teleport frame is propagated through B→C into B’s readout. Full judge correctness checks these frames.
- A-only encoder selection was corrected to distinguish pure logical Z faults from faults requiring a second data error. The original A13 produces nonzero c1 and was evaluated by three-seed MC, not ranked by invalid third order. The extended exact search finds A15 with zero pure-logical danger.
- Full ALAP was refined so terminal/reset-followed measurements run ASAP, and teleport source measurements may overlap the round when their cells are distinct. `abstract_trim` advances seven measurements and removes 72 idle qubit-steps; its exact screen improves but its acceptance still fails.
- MC uses the unchanged `MAIN/spec/mc3.py`; sunfish runs its byte-identical lane-local copy because that mirror lacked the original script. `abstract_built` uses the same check and fast_check seed implementation through evaluate.py because c1 is nonzero. MC receipts retain the precision emitted by the driver; evaluate.py also saves full-precision seed values.
- Best-circuit fast ablations use TREP2’s exact detector-dependency pruning, with the baseline checked against the unchanged exact2 --third result to its printed precision. Earlier complete ablations also use unmodified exact2. No test or judge gate was weakened.
- Untested space remains: other connected encoder graphs, more general encoder/move interleaving, data relocation during the prefix, A coupling before final T_DAG, and longer searches. The fixed-template and bounded routing negatives do not rule these out.

Reproduction uses the project `.venv/bin/python` and `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`. `co_design.py`, `build_abstract.py`, `rebuild_solver.py`, `reschedule.py`, `trim_measurements.py`, `evaluate.py`, and `ablate.py` retain the model and build paths. Each QASM has sibling metadata with `data_qubits`.

[audit.json](audit.json) independently verifies the native timing and reported CX counts for all 13 reported circuits. [manifest.json](manifest.json) verifies all 26 QASM/JSON pairs and identifies which have direct judge receipts. All SEP2T compute jobs have finished or were explicitly interrupted and recorded; none is left running.
