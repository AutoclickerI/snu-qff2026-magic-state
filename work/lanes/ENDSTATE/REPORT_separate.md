# ENDSTATE

**Status: priority 1 SAT; eight complete C7 grid circuits evaluated; no eligible improvement. Bounded searches are finished; global dynamic feasibility/performance remains open.**

The best fully checked member, `abstract_opt08`, has exact-through-third loss **2.08378e-4**, native **R56**, measured acceptance **0.387448**, and FAST runtime. All eight catalog circuits pass format/class/correctness and fail acceptance. They do not approach MAIN v29c (supplied 3-seed mean 6.345e-5), the supplied leader 5.166e-5, or the 5e-5 target. This does **not** prove that the broader moving/helper/MB family cannot reach that target.

## Priority 1: a physical one-hop witness

**YES:** [`witness12_h1.qasm`](witness12_h1.qasm), [`metadata`](witness12_h1.json), and [`independent verification`](witness12_h1.verified.json). It uses no helpers and encoder counts A/B/C = **10/11/11 CX**, with at most one move per ancilla qubit. Data, in code-label order, are `[2,6,17,14,25,28,30]`.

| Block | Initial cells, code-label order | Final cells, same order | Encoder CX | Measured moves |
|---|---|---|---:|---:|
| A | [7, 13, 22, 19, 20, 21, 18] | [1, 12, 23, 13, 19, 22, 24] | 10 | 7 |
| B | [9, 8, 15, 21, 27, 33, 32] | [3, 7, 16, 20, 26, 34, 31] | 11 | 7 |
| C | [10, 8, 9, 15, 21, 27, 33] | [9, 8, 15, 21, 27, 33, 32] | 11 | 6 |

Prepare/move A, B, then C with data held at the final cells. Every occupied-cell transition and nearest-neighbour gate is checked. Cost: **32 encoder CX + 20 transfer CX + 21 transversal CX = 73 CX**. The ≤12 cap counts encoder CX separately from the explicitly allowed moves; inclusive cost is provided. The three matchings use exactly the same Steane labels. An encoded data qubit entangled with a reference retains all six stabilizers and both logical correlations; all detectors are deterministic, and 4,096 noiseless samples have no defects. This fragment is not a complete magic-state submission.

| Original relaxation rung | Result |
|---|---|
| ≤12 encoder CX, ≤1 move/qubit, C7 | SAT, above witness; actually ≤11 |
| ≤14 encoder CX, ≤1 move/qubit, C7 | SAT, same witness |
| ≤12 or ≤14 encoder CX, ≤2 moves/qubit, C7 | SAT, same witness |
| C6, all B/C outputs stationary and connected | UNSAT geometrically, any CX count; proof below |
| Moving or helper-assisted C6 | Not closed |

## Time-indexed prefix compatibility

Both actual MAIN prefixes were extracted by the backward quantum causal cone of terminal T† gates and cultivation records, with reset boundaries cutting dependencies. Every detector on retained records was kept. v29c’s fused moves change its output locations. Extracted ASAP prefixes independently pass the unchanged judge’s format/class/correctness checks; the 1,000-shot diagnostics are not score estimates.

| Prefix | Prefix CX | Output cells in code order | Last data steps as written | Last data steps after ASAP retiming | ASAP depth |
|---|---:|---|---|---|---:|
| v23h_c2c9 | 75 | 0,20,7,4,3,15,8 | 44,44,44,28,44,29,30 | 29,29,29,28,28,29,29 | 30 |
| v29c | 81 | 0,20,7,10,3,16,8 | 35,47,36,47,29,41,30 | 27,27,27,27,26,30,27 | 31 |

[`v23h_c2c9.prefix.json`](v23h_c2c9.prefix.json) and [`v29c.prefix.json`](v29c.prefix.json) retain every operation, actual/ASAP times, complete cell-live intervals, releases, and all 48 legal prefix embeddings. Free-endpoint searches use six classes modulo whole-grid D4; fixed-endpoint searches use all 48. The model preserves the prefix’s physical per-wire order, allows coherent two-CX data hops after the last non-T† prefix operation, and places terminal T† on the appropriate live data segment. A quiet live wire is never treated as free.

## Ranked, fully checked native circuits

All values below are measured. “Exact 3rd” is a truncated expectation through third order, not an all-orders score; truncation is material at these low acceptances. The unchanged `work/lanes/EVAL/exact2.py --third` ran on seven rows. `helper_shared_opt14` has 66 detector projectors and uses the separately identified wide-integer adapter described below. The 1e6-shot judge uses unchanged `work/fast_check.py`; speed uses unchanged XTIM predictor arithmetic with cache writes redirected into this lane.

| Circuit | R | A/B/C encoder CX | Block moves A/B/C | Data hops | Ancilla idle ticks before R | Exact 3rd | Judge acceptance | Runtime s/1e6 |
|---|---:|---|---|---:|---:|---:|---:|---:|
| [abstract_opt08](abstract_opt08.qasm) | 56 | 11/14/12 | 0/8/12 | 16 | 282 | 0.000208378391 | 0.387448 FAIL | 11.951 FAST |
| [abstract_opt10](abstract_opt10.qasm) | 56 | 11/14/12 | 0/8/12 | 14 | 282 | 0.000210023764 | 0.388612 FAIL | 10.670 FAST |
| [abstract_opt11](abstract_opt11.qasm) | 56 | 11/14/12 | 0/8/12 | 14 | 282 | 0.000210023764 | 0.388922 FAIL | 12.890 FAST |
| [helper_shared_best](helper_shared_best.qasm) | 59 | 13/11/15 | 0/7/13 | 20 | 245 | 0.000241617596 | 0.393909 FAIL | 8.132 FAST |
| [legacy_opt48](legacy_opt48.qasm) | 56 | 12/14/12 | 0/9/12 | 15 | 245 | 0.000266531278 | 0.413119 FAIL | 10.026 FAST |
| [legacy_opt46](legacy_opt46.qasm) | 56 | 12/14/12 | 0/9/12 | 15 | 246 | 0.000266639514 | 0.413445 FAIL | 12.164 FAST |
| [legacy_depth](legacy_depth.qasm) | 55 | 12/15/12 | 0/9/12 | 15 | 236 | 0.000271260206 | 0.422179 FAIL | 7.648 FAST |
| [helper_shared_opt14](helper_shared_opt14.qasm) | 60 | 11/9/14 | 0/14/11 | 26 | 318 | 0.000272377383 | 0.346302 FAIL | 11.545 FAST |

The five no-helper minimum-CX builds use ≤14 encoder CX per block and ≤2 moves per B/C qubit, with A stationary. `legacy_depth` deliberately tests 15 CX in B to reduce preparation depth: its model optimum improves R56→R55 but its scored loss worsens. `helper_shared_best` also explores 15 CX in C. These two depth/performance variants are outside the original ≤14-CX rung; `helper_shared_opt14` uses 11/9/14 CX and one shared helper within that bound. No candidate falls below 6.2e-5, so the requested conditional 3-seed 1e8-shot MC trigger was not met. No seed-0 draw is presented as a mean.

Every catalog QASM has sibling `.json`, `.plan.json`, `.check.json`, `.speed.json`, `.split.json`, and native lifetime/distance files. Seven also have unchanged `.exact.log` and `.sens.json` receipts; `helper_shared_opt14` has `.wide_screen.json` instead of an unchanged third-order receipt. [`evaluator_agreement.json`](evaluator_agreement.json) verifies accelerated-screen agreement with the unchanged evaluator and pair-attribution agreement to <1e-13. The five primary circuits have 185–191 CX; depth-optimal B adds one CX.

## Loss split

Entries are in **1e-5**. The pair-class table is disjoint; “teleport-involving” and “exposure-involving” are overlapping marginals and must not be added. All pre-R idle noise is exposure, including data waiting; operation noise follows emitted provenance. The net third-order increment includes its normalization correction.

| Circuit | Round × round, 2nd | Pre-round-only pairs | Teleport-involving pairs | Exposure-involving pairs | Net 3rd |
|---|---:|---:|---:|---:|---:|
| abstract_opt08 | 2.8840 | 8.3277 | 1.1822 | 6.5436 | 9.0124 |
| abstract_opt10 | 2.8840 | 8.3383 | 1.1822 | 6.5578 | 9.1663 |
| abstract_opt11 | 2.8840 | 8.3383 | 1.1822 | 6.5578 | 9.1663 |
| helper_shared_best | 2.8840 | 10.9227 | 1.3427 | 8.6921 | 9.5353 |
| legacy_opt48 | 2.8840 | 14.9778 | 2.0436 | 12.3133 | 7.7486 |
| legacy_opt46 | 2.8840 | 14.9745 | 2.0436 | 12.3101 | 7.7627 |
| legacy_depth | 2.8840 | 15.8867 | 2.1196 | 12.8665 | 7.2759 |
| helper_shared_opt14 | 2.8840 | 10.8380 | 1.4862 | 8.2561 | 12.7078 |

For `abstract_opt08`, preparation × exposure alone is **4.83136e-5**, and the pre-round-only second-order pairs total **8.32769e-5**. Round × round is the familiar **2.884e-5** from LADDER/ARCH. The measured excess therefore sits before the round and in cross terms; reducing the encoder gate count has not removed the live-state waiting cost. LADDER’s R33–R45 values are complete-package counterfactuals, not a per-CX price. These native circuits are ranked by their actual evaluations, with no extrapolated LADDER score substituted.

## Catalog, release use, and prefix embedding classes

[`catalog.json`](catalog.json) contains the labelled initial/final geometry, preparation CX, moves, actual R, and measured exposure for every catalog candidate. Each `<name>.timeline.json` records which cell is required from which native time through release. Each `<name>.catalog.prefix_distances.json` evaluates **all 48 prefix embeddings and all 168 common code automorphisms** for both prefixes and gives each data label’s Manhattan distance, totals, and six-class summaries. These distances and derived R values are **routing lower bounds**; they omit collisions and preparation dependencies. Actual routes and their native times are in the solved schedule/plan files.

For the best checked geometry (`abstract_opt08`), the per-class distance ranges are:

| Prefix | D4 prefix class | Total hops lower bound, min–max over its 8 orientations | Data-only R lower bound, min–max |
|---|---|---:|---:|
| v23h_c2c9 | r0c0 | 9–24 | 34–39 |
| v23h_c2c9 | r0c1 | 10–23 | 34–40 |
| v23h_c2c9 | r1c0 | 8–19 | 34–37 |
| v23h_c2c9 | r1c1 | 7–19 | 34–38 |
| v23h_c2c9 | r2c0 | 8–16 | 36–38 |
| v23h_c2c9 | r2c1 | 12–16 | 36–37 |
| v29c | r0c0 | 9–22 | 33–37 |
| v29c | r0c1 | 11–23 | 33–38 |
| v29c | r1c0 | 8–17 | 32–35 |
| v29c | r1c1 | 9–18 | 33–37 |
| v29c | r2c0 | 10–17 | 34–36 |
| v29c | r2c1 | 12–17 | 35–37 |

“Earliest R” is model-specific. The seeded fixed endpoint with the selected minimum-CX encoders has proven model optimum **R56**; the depth-optimal encoder variant has **R55**. Those proofs cover the stated fixed geometry, code automorphisms, 48 prefix embeddings, ≤3 data hops/wire, ≤2 block moves/wire, and the retained prefix/round order. They do not optimize over arbitrary encoders, early A coupling, different endpoints, or MB preparations. The final native scheduler separately proves the minimum for each emitted physical wire order.

## Exact preparation libraries

107 free heptomino shapes fit the board, with 8,856 labelled shape embeddings and **7,816 distinct connected cell sets**. There are 30 inequivalent Steane labellings modulo the 168 automorphisms, giving **3,210** shape/labelling classes. All fixed-cell CSS CX preparations in this domain are covered. All 35 coordinate input subspaces are allowed. Logical-plus preparation is obtained by Hadamard duality.

Minimum-CX histogram: **8:112, 9:402, 10:746, 11:868, 12:570, 13:212, 14:300**. Thus 2,698 classes have ≤12 CX, and all have ≤14. Every shape has some labelling requiring ≤11 CX. These are not fault-tolerance guarantees for arbitrary use of the encoder. The compact 8-CX choices used in searches were separately checked for zero pure-logical single-Z sources in A.

[`library_distance_certificate.bin`](library_distance_certificate.bin) and [`independent checker receipt`](library_certificate_verified.json) establish every minimum: the integer potential is zero on all coordinate inputs, changes by at most one along all allowed CX transitions, and equals the verified witness length at each target. The independent checker tested **15,850,362** transitions. A second Dijkstra search over disjoint CX layers produces [`library_depth_encoders.json`](library_depth_encoders.json), with state/adjacency verification in [`library_depth_verification.json`](library_depth_verification.json).

Scope: seven fixed cells, product X/Z initialization, CX-only unitary preparation, no helpers or movement within this library. General Clifford/measurement-based/helper-assisted preparations are outside the library completeness statement.

## Closed models and unresolved searches

- **Stationary A + stationary final D, sequential complete-block preps, B/C ≤1 move/wire, no helpers, arbitrary connected seven-cell regions, any CX count:** CP-SAT INFEASIBLE in 169.719 s (`conn_staticA_h1_seq`). Allowing arbitrary overlapping preparation locations without occupancy is SAT. The negative does not cover interleaved data/preparation motion. The retained solver receipt is not a DRAT certificate.
- **All block outputs/data stationary; connected A7; B/C connected through zero or one helper each, borrowing later-prepared block cells; arbitrary sequential prep order:** INFEASIBLE in 177.041 s (`helper01_borrow_geometry`). This excludes only the named static preparation model.
- **Connected stationary B7/C6, six adjacent B–C matches, and an external data neighbour at every B:** independently exhaustive UNSAT. [`c6_certificate.cpp`](c6_certificate.cpp) generates all 7,816 connected B sets; 6,792 B/drop roles satisfy the necessary local degrees. All **385,752** C matchings were checked; **zero** C sets are connected, before D/A matching is imposed. [`c6_certificate.json`](c6_certificate.json) records the proof argument, counters and source hash. An independent CP-SAT model agrees. No CX cap is needed; movement or disconnected/helper-assisted preparation escapes this theorem.
- **Free-placement compact 8-CX templates, stationary A, one/two moves, stated data-hop bounds and horizons:** bounded runs returned UNKNOWN. They do not establish impossibility.
- **R45 with arbitrary connected preparation regions, six-tick placeholders, stationary A, ≤2 block moves and ≤4 data hops, ASAP non-T† prefix:** UNKNOWN at 600 s. Even this optimistic timing relaxation was not closed. No sub-5e-5 obstruction follows.
- The successful connected-region searches use placeholder durations only to find positions/routes. Real exact encoders replace those placeholders and the complete native circuit is rescheduled before any R/score is reported.

## Helper-assisted branch and evaluator limit

One physical helper reused by B and C is now a feasible timed placement (`shared_helper_h2_R65`). It is realized with unitary preparations returning that helper to |0⟩, followed by a checked Z measurement; full detector records remain intact. The final bounded search stopped FEASIBLE at model R59 with lower bound R35; this is not an optimality proof. Realized `helper_shared_best` is R59, 201 CX, encoder counts 13/11/15, acceptance **0.393909**, FAST, and unchanged third-order loss **2.41618e-4**. The ≤14-CX-per-block member `helper_shared_opt14` is R60, 213 CX, encoder counts 11/9/14, acceptance **0.346302**, FAST, and wide-mask third-order loss **2.72377e-4**. Both use exactly one physical helper shared sequentially by B and C; neither is competitive. An earlier exploratory branch allowed two distinct helpers (one per block), scored 4.29696e-4, and is explicitly outside the one-physical-helper rung.

Helper builds can exceed 63 detector bits. The unmodified vectorized evaluator then raises an integer-overflow error; no detector is removed to hide it. `wide_screen.py` changes only the detector-mask array representation to Python integers in a lane-local runtime adapter. **Every requested decoder table is compared with the unchanged scalar EVAL implementation.** The narrow control matches the unchanged full evaluator; 5,849 tables were checked on the initial shared-helper circuit. These helper screens are explicitly distinct from the unchanged third-order receipts supplied for the seven compatible catalog circuits.

## Decisions, verification, and remaining limits

- The owner clarified that complete scored circuits are the deliverable, so a reproducible exhaustive library/models plus a ranked native catalog took priority over enumerating every endpoint geometry.
- Prefix retiming preserves physical wire order. Dense renumbering of classical records prevents prefix/suffix collisions without changing a detector parity. Preparation, routing, and round frames are assembled through existing ST1 logic and SEPBC’s native emitter; SEPBC’s original-witness routing work was not duplicated.
- Code automorphisms are consistent across every matching. Data move coherently in two CX; ancilla moves use one CX plus measurement and detector-frame propagation. Physical occupancy includes destination initialization and source measurement.
- The secondary timing objective counts ancilla idle ticks, measured teleports, and data-hop CX at fixed R. R has a dominating weight larger than the full secondary range. Actual exposed ticks are recomputed from emitted native lifetimes.
- CPU saturation prompted PID-specific termination and rerouting of two eight-worker searches from zebra to hippo. Completed artifacts and incumbents were retained. No timeout/interruption is called UNSAT. No ENDSTATE worker remains running at handoff.
- Verified: priority-1 instrument, exact fixed-cell libraries, independent C6 obstruction, emitted grid adjacency/native schedules, seven unchanged third-order runs, eight catalog 1e6-shot judges and FAST probes, and exact second-order attribution agreement.
- Unverified/open: global earliest R; exhaustive dynamic endpoints; general measurement-based preparations; lower-loss encoders beyond these choices; acceptance-passing members of this redesign; moving C6 performance. No all-orders score or 3-seed mean is claimed for the failing circuits.
- Writes are confined to ENDSTATE on the authorized hosts. No credentials were read; no submissions, commits, pushes, or sub-agent/collaboration tools were used.

## Reproduce

Use `.venv/bin/python` with `PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`. Search receipts record complete arguments and models. `prefixes.py` extracts releases; `spacetime.py` runs placement/lifetime models; `build_schedule.py <schedule.json> <name>` assembles through SEPBC; `evaluate.py exact|check|speed|split <stem>` runs checks; `catalog.py` and `embedding_classes.py` regenerate the catalog; `check_certificate.py` verifies the CX-minimum certificate. No scripts submit or modify another lane.
