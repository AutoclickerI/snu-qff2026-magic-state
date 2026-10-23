# Lane L5: pre-cycle optimization against v10

Updated 2026-10-23 21:09:19 KST. Active; final due 23:00 KST.

G1 objective: minimize the official 100,000,000-shot mean over seeds 0, 1000, 2000. Eligibility is format, class, correctness and acceptance PASS. `fault_scan.c1` is diagnostic only. No submissions. All artifacts and caches stay in this lane. Numerical-library threads are capped at one; worker counts are chosen after host-capacity checks.

v10 baseline: seed 0 **0.00012111467445**; three-seed mean **0.000122077299614**; 115 CX. Reconstructed QASM matches the submitted artifact byte for byte; fresh official evaluations reproduce seed 0 exactly.

## Best completed candidate per change

| Change | Candidate | Seed 0 | Δ seed 0 vs v10 | Three-seed mean | Δ mean vs v10 | CX | Completed |
|---|---|---:|---:|---:|---:|---:|---:|
| Boundary timing + retained X readouts | [combined_lns_0012](combined_lns_0012.qasm) | 0.000114650959 | -6.464e-06 | 0.000113270716 | -8.807e-06 | 115 | 32 |
| Exhaustive boundary CX/readout moves | [grid_001](grid_001.qasm) | 0.000117276363 | -3.838e-06 | 0.000117268423 | -4.809e-06 | 115 | 17 |
| Pre-cycle + first three cycle layers | [joint1_0026](joint1_0026.qasm) | 0.000118481976 | -2.633e-06 | 0.000117323313 | -4.754e-06 | 115 | 3 |
| Retain final-cycle X readouts | [retain_cycle_m7_s5](retain_cycle_m7_s5.qasm) | 0.000115249104 | -5.866e-06 | 0.000117364223 | -4.713e-06 | 115 | 14 |
| Delay tile-0 Bell preparation | [bell0_delay_lns1_0013](bell0_delay_lns1_0013.qasm) | 0.000117406804 | -3.708e-06 | 0.000118467717 | -3.61e-06 | 115 | 3 |
| Pre-cycle MC local/LNS search | [lns1_0116](lns1_0116.qasm) | 0.000120987377 | -1.273e-07 | 0.000118532691 | -3.545e-06 | 115 | 120 |
| Per-qubit boundary deadlines | [boundary_cm0_s5](boundary_cm0_s5.qasm) | 0.000120243052 | -8.716e-07 | 0.000120415537 | -1.662e-06 | 115 | 8 |
| Commuting boundary deadlines | [boundary_cm1_s0](boundary_cm1_s0.qasm) | 0.000120000926 | -1.114e-06 | 0.000121246891 | -8.304e-07 | 115 | 8 |
| Retain central cat X readout | [nreset_s4_b0](nreset_s4_b0.qasm) | 0.000123173622 | +2.059e-06 | 0.000121522361 | -5.549e-07 | 115 | 1 |
| Baseline | [v10_reference](v10_reference.qasm) | 0.000121114674 | +0 | 0.0001220773 | +0 | 115 | 1 |
| Transversal T sign patterns | [cat_sign_2](cat_sign_2.qasm) | 0.00012117238 | +5.771e-08 | 0.000122096417 | +1.912e-08 | 115 | 7 |
| Remove central cat readout | [prune_cat_4](prune_cat_4.qasm) | 0.000123020531 | +1.906e-06 | 0.000122478426 | +4.011e-07 | 115 | 1 |
| Enumerated shallow double-cat trees | [enumcat_084_r8](enumcat_084_r8.qasm) | 0.000124005894 | +2.891e-06 | 0.000122656946 | +5.796e-07 | 115 | 2 |
| Random double-cat trees | [cat_007_r8](cat_007_r8.qasm) | 0.000124005894 | +2.891e-06 | 0.000122656946 | +5.796e-07 | 115 | 60 |
| Remove leaf flag q1 | [prune_cat_1](prune_cat_1.qasm) | 0.000122050179 | +9.355e-07 | 0.000122889486 | +8.122e-07 | 113 | 1 |
| Remove leaf flag q2 | [prune_cat_2](prune_cat_2.qasm) | 0.000131029773 | +9.915e-06 | 0.000131588074 | +9.511e-06 | 113 | 1 |
| Remove both leaf flags | [prune_cat_3](prune_cat_3.qasm) | 0.000137361121 | +1.625e-05 | 0.000137617673 | +1.554e-05 | 111 | 1 |

Every row above has all four gates PASS at every official seed. [SCOREBOARD.csv](SCOREBOARD.csv) records each completed candidate, each seed, both deltas, and provenance. JSON files contain full gate receipts and exact schedules.

## Independent-seed evidence

Seeds 3000, 4000, 5000 were not used by the initial three-seed search. Selection among many MC candidates can bias the search mean downward; a lower search mean alone does not establish lower expected infidelity.

| Candidate | Search mean | Independent mean | Δ independent vs v10 |
|---|---:|---:|---:|
| combined_p0_m7 | 0.000114989348 | 0.000114845408 | -6.292e-06 |
| combined_p0_m6 | 0.00011521111 | 0.000113815766 | -7.321e-06 |
| combined_p0_m3 | 0.00011531386 | 0.000115658454 | -5.479e-06 |
| grid_001 | 0.000117268423 | 0.000119832279 | -1.305e-06 |
| joint1_0026 | 0.000117323313 | 0.000119213248 | -1.924e-06 |
| retain_cycle_m7_s5 | 0.000117364223 | 0.000117726642 | -3.41e-06 |
| joint1_0032 | 0.000117451717 | 0.000118591402 | -2.546e-06 |
| retain_cycle_m6_s5 | 0.00011756004 | 0.000119557783 | -1.579e-06 |
| retain_cycle_m6_s4 | 0.000117595613 | 0.00011835054 | -2.787e-06 |
| grid_013 | 0.000117734641 | 0.000118553622 | -2.584e-06 |
| grid_010 | 0.000117848797 | 0.000118755527 | -2.382e-06 |
| joint1_0010 | 0.000118302062 | 0.000118296453 | -2.841e-06 |
| lns1_0116 | 0.000118532691 | 0.000119278296 | -1.859e-06 |
| lns1_0110 | 0.000118658155 | 0.000121025837 | -1.113e-07 |
| lns1_0117 | 0.000118717863 | 0.000119194274 | -1.943e-06 |
| bell0_delay_boundary_cm0_s5 | 0.00011890053 | 0.000119341053 | -1.796e-06 |
| boundary_cm0_s5 | 0.000120415537 | 0.000121570344 | +4.332e-07 |
| bell0_delay_v10_reference | 0.000120559873 | 0.000121030492 | -1.066e-07 |
| boundary_cm0_s0 | 0.000121004075 | 0.000121271339 | +1.342e-07 |
| v10_reference | 0.0001220773 | 0.000121137131 | +0 |

## Broader fresh-seed panel

| Candidate | Seeds 6000–17000 mean | Δ vs v10 on same panel |
|---|---:|---:|

## Verified winners

- [joint1_0010.qasm](joint1_0010.qasm), [joint1_0010.json](joint1_0010.json): seed 0 0.000117891258574; three-seed mean 0.000118302062152; Δ -3.77524e-06; 115 CX. Direct sequential `tprep.check`: PASS.

## Methods and decisions

- Boundary schedules use individual qubit deadlines while preserving the complete v10 cycle timing. A second family permits proven gate commutations across the boundary.
- `lns.py` searches legal single-operation timing moves and larger schedule neighborhoods using all three official seeds at 1e8 shots each. `joint1` also moves the cycle preparation and first interaction layer; its later cycle gates remain fixed.
- `cat_trees.py` replaces the double-cat contraction/expansion network with a grid spanning tree, choosing its root and leaf-ancilla flag directions. Injection and the final cycle stay fixed. All 60 generated trees passed the initial exact correctness/acceptance screen; final ranking uses full official MC.
- Modified-noise diagnostics are isolated in `idle_windows.py`; they are not candidate scores. Removing double-cat-window idle gives mean 1.12874938e-4, first-check-window idle 1.21367855e-4, pre-cycle data idle 1.14044114e-4, and pre-cycle ancilla idle 1.19200626e-4. This motivated concentrating work on the double-cat stage.
- Native h-measure-h readout retains the measured X state (organizer problem.md, section 1.2; tprep/qasm.py `_x_readouts`). Retaining final-cycle X ancillas removes their resets; this is scored with the unmodified official noise model. Retaining the central cat readout passes all four gates and scores 1.21522361e-4 over three seeds. It takes about 500 seconds per seed at six workers; the remaining 15 priority variants were stopped in favor of stronger, faster methods. The completed evidence is preserved.
- Exhaustive enumeration found 776 spanning trees on the original cat footprint. Roots 8, 7, 9 and 14 yielded 85 distinct circuits at depth <=42; two reused exact-QASM receipts, and the other 83 are being scored.
- Single-operation T/TDG timing moves are omitted from the next LNS run because shifting them through commuting gates and depolarizing idle slots often changes MC draws without changing the physical noisy channel. CX/readout moves remain in the search.
- Earlier boundary seed-5 mean improvement did not repeat on independent seeds (independent mean 1.21570344e-4 versus v10 1.21137131e-4). Its expected-value gain is therefore unproven.

## Earlier work

The v6 experiments remain in `results.jsonl` and their original QASM/JSON files. `pre_alap_ordered` scored 0.000128628417625 at seed 0 versus v6 0.000131030214099. ALAP is now in production and is not a new improvement against v10. The old report’s c1 eligibility requirement, eight-process restriction and seed-0-only ranking were removed.

## Remaining verification

Official scoring of the running searches, independent-seed confirmation of finalists, and a direct sequential `tprep.check` for every declared winner. No contest submission is performed by this lane.
