# HOPS

**Complete. Delivery: [best.qasm](best.qasm) and [best.json](best.json), identical to `advance_watch_all`.** Its three-seed 1e8-shot MC mean is **7.261248e-05**, 0.28% below the supplied 7.282e-5 bar; seed-0 acceptance is **0.53703**. It passes the actual 1e6-shot judge and the unmodified `exact2.py --third` confirmation.

All dates and resource limits refer to this lane task. CPU worker maxima were 3 on zebra, 8 on hippo, and 2 on jerry before 15:40 KST / 20 afterwards, with OpenMP/BLAS fixed to one and load checked at launch. No submission, commit, push, credential access, or other-lane writes were performed. All QASM files have sibling metadata containing `data_qubits`.

## Variants

Every row below passed the actual 1e6-shot judge. R is extracted from the judge native schedule; all seven data→A and B→C checks agree. `c1` is exact2’s printed `c1 p` contribution at p=0.001; all are below 1e-12. Second and third are expansion terms, total is through third order, and exp(-A1) is an acceptance estimate. Exploration uses TREP2’s algebraically pruned exact2 implementation; final reference receipts use the unmodified exact2 CLI.

| Variant | Moves data / block | CX | R native | c1 | 2nd | 3rd | Exact total | exp(-A1) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [hop_early](hop_early.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.72320e-05 | 7.16408e-05 | 0.53526 |
| [hop_early_t](hop_early_t.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.72349e-05 | 7.16437e-05 | 0.53526 |
| [watch9](watch9.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.72906e-05 | 7.16994e-05 | 0.53594 |
| [advance_watch_all](advance_watch_all.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.74656e-05 | 7.18744e-05 | 0.53701 |
| [watch_11](watch_11.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.75860e-05 | 7.19948e-05 | 0.53698 |
| [advance_watch9](advance_watch9.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.77375e-05 | 7.21463e-05 | 0.53769 |
| [hop_early_cancel_keep](hop_early_cancel_keep.qasm) | 6 / 0 | 199 | 45 | 2.92360e-19 | 5.47038e-05 | 1.75717e-05 | 7.22755e-05 | 0.53335 |
| [watch_3](watch_3.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.79180e-05 | 7.23269e-05 | 0.53748 |
| [watch9_cancel_keep](watch9_cancel_keep.qasm) | 6 / 0 | 199 | 45 | 2.92360e-19 | 5.47038e-05 | 1.76279e-05 | 7.23317e-05 | 0.53402 |
| [watch_10](watch_10.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.79321e-05 | 7.23409e-05 | 0.53748 |
| [watch_9](watch_9.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.79873e-05 | 7.23961e-05 | 0.53891 |
| [advance_watch](advance_watch.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.80094e-05 | 7.24182e-05 | 0.53909 |
| [watch_2](watch_2.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.82677e-05 | 7.26765e-05 | 0.53798 |
| [m15](m15.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.83313e-05 | 7.27401e-05 | 0.53941 |
| [watch_8](watch_8.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.83438e-05 | 7.27527e-05 | 0.53941 |
| [tdg_6](tdg_6.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.85225e-05 | 7.29313e-05 | 0.53991 |
| [tdg_7](tdg_7.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44119e-05 | 1.85235e-05 | 7.29354e-05 | 0.53990 |
| [tdg_4](tdg_4.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.85805e-05 | 7.29893e-05 | 0.53991 |
| [tdg_5](tdg_5.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44119e-05 | 1.85815e-05 | 7.29934e-05 | 0.53990 |
| [advance](advance.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.86266e-05 | 7.30354e-05 | 0.54010 |
| [tdg_2](tdg_2.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.86276e-05 | 7.30364e-05 | 0.53991 |
| [tdg_3](tdg_3.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44119e-05 | 1.86286e-05 | 7.30405e-05 | 0.53991 |
| [m15_reuse9](m15_reuse9.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.86485e-05 | 7.30573e-05 | 0.53923 |
| [tdg_0](tdg_0.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.86914e-05 | 7.31002e-05 | 0.53992 |
| [tdg_1](tdg_1.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44119e-05 | 1.86924e-05 | 7.31043e-05 | 0.53991 |
| [reuse9](reuse9.qasm) | 6 / 0 | 203 | 45 | 2.92360e-19 | 5.44088e-05 | 1.90077e-05 | 7.34165e-05 | 0.53974 |
| [hop_early_cancel_alap](hop_early_cancel_alap.qasm) | 6 / 0 | 199 | 45 | 2.92360e-19 | 5.54241e-05 | 1.85697e-05 | 7.39938e-05 | 0.52529 |
| [watch9_cancel_alap](watch9_cancel_alap.qasm) | 6 / 0 | 199 | 45 | 2.92360e-19 | 5.62287e-05 | 1.84794e-05 | 7.47081e-05 | 0.52594 |
| [watch_15](watch_15.qasm) | 6 / 0 | 203 | 46 | 2.92360e-19 | 5.99373e-05 | 1.98481e-05 | 7.97853e-05 | 0.52435 |
| [watch_7](watch_7.qasm) | 6 / 0 | 203 | 46 | 2.92360e-19 | 5.99373e-05 | 2.01982e-05 | 8.01355e-05 | 0.52484 |
| [watch_14](watch_14.qasm) | 6 / 0 | 203 | 46 | 2.92360e-19 | 5.99373e-05 | 2.02142e-05 | 8.01515e-05 | 0.52484 |
| [watch_13](watch_13.qasm) | 6 / 0 | 203 | 46 | 2.92360e-19 | 5.99373e-05 | 2.02808e-05 | 8.02181e-05 | 0.52659 |
| [watch_6](watch_6.qasm) | 6 / 0 | 203 | 46 | 2.92360e-19 | 5.99373e-05 | 2.05680e-05 | 8.05053e-05 | 0.52533 |
| [watch_5](watch_5.qasm) | 6 / 0 | 203 | 46 | 2.92360e-19 | 5.99373e-05 | 2.06433e-05 | 8.05805e-05 | 0.52708 |
| [watch_12](watch_12.qasm) | 6 / 0 | 203 | 46 | 2.92360e-19 | 5.99373e-05 | 2.06578e-05 | 8.05950e-05 | 0.52708 |
| [watch_4](watch_4.qasm) | 6 / 0 | 203 | 46 | 2.92360e-19 | 5.99373e-05 | 2.10239e-05 | 8.09612e-05 | 0.52757 |

## Finalists ranked only by MC mean

Each seed uses 1e8 shots at p=0.001 via the requested unchanged `MAIN/spec/mc3.py`, which first runs `tprep.check` at 1e6 shots. Acceptance is a gate only. The tdg_0/v20 MC receipt is copied from TREP2 after verifying byte-identical QASM; its 1e6-shot check and exact screen were rerun here.

| Finalist | Seed 0 | Seed 1000 | Seed 2000 | Mean | Seed-0 acceptance | Files |
|---|---:|---:|---:|---:|---:|---|
| advance_watch_all | 7.412023e-05 | 7.162317e-05 | 7.209405e-05 | **7.261248e-05** | 0.53703 | [QASM](advance_watch_all.qasm), [JSON](advance_watch_all.json), [MC](advance_watch_all.mc.log), [check](advance_watch_all.check.json) |
| tdg_0 | 7.260949e-05 | 7.205880e-05 | 7.378347e-05 | **7.281725e-05** | 0.54001 | [QASM](tdg_0.qasm), [JSON](tdg_0.json), [MC](tdg_0.mc.log), [check](tdg_0.check.json) |
| watch_11 | 7.313044e-05 | 7.260703e-05 | 7.335112e-05 | **7.302953e-05** | 0.53705 | [QASM](watch_11.qasm), [JSON](watch_11.json), [MC](watch_11.mc.log), [check](watch_11.check.json) |
| hop_early | 7.211275e-05 | 7.364458e-05 | 7.377626e-05 | **7.317786e-05** | 0.53527 | [QASM](hop_early.qasm), [JSON](hop_early.json), [MC](hop_early.mc.log), [check](hop_early.check.json) |
| watch9 | 7.320892e-05 | 7.164825e-05 | 7.499400e-05 | **7.328372e-05** | 0.53593 | [QASM](watch9.qasm), [JSON](watch9.json), [MC](watch9.mc.log), [check](watch9.check.json) |

## Mechanism and search coverage

- `watch_11` changes three Z resets to measured initialization plus deterministic detectors: cell 15 between two data transfers, and cells 8 and 16 before A preparation. The round and CX count stay fixed. `watch9` also monitors cell 9 at step 37 before its A reset at 38.
- `advance_watch_all` retains measured-|+⟩ reuse on 9, moves the final T-daggers of data 15 and 8 to output cells 22 and 21 at step 44, advances their transfer chain one step, and checks the vacated cells. The reused-|+⟩ transfer leaves source 8 in |+⟩, so its Z reset is retained; a Z-monitor there would be random and was rejected by correctness during development.
- `hop_early` instead retains the |0⟩ transfer into 9, advances the final pre-stage CXs into data 15 and 8 and the subsequent transfer chain, and monitors five vacated-source events without increasing R. `hop_early_t` additionally puts those two final T-daggers after the transfers.
- `tdg_0` is byte-identical to MAIN/v20 (SHA256 c2a65ea7cfb3fd2f97d9c60afcb6f9e963b6ac6bb8dd8c275370697a351542a4). Masks 1–7 relocate the final T-daggers of data 4, 15, and 8 to the destination at native step 44.
- `watch_*` enumerates monitors at source 15 between transfers, source 8 before A, source 15 before its A RX, and source 16 before A. Monitoring source 15 before A without advancing the transfer adds one native step and loses; these are built prices for that timing, not a general exclusion.
- The joint-prep cancellation variants delete two commuting CX pairs (4 CX total). Their timing and full-noise prices are measured independently; fewer CX is not treated as the ranking objective.

## Hop fault attribution

The provenance label “hop” includes idle channels following hop CXs. Exact2 pair/triple analysis is in [tdg_0.attribution.json](tdg_0.attribution.json). The leading hop pair is a Z/Y idle on cell 10 at steps 31–44 with an A-encoder fault; the A×hop pair sum is 2.751877584e-6. Its eight leading individual pairs are each 3.084291425e-7. This is predominantly waiting exposure, rather than the two CXs alone. The retained triple list is thresholded at 3e-13 and is not claimed to sum to the entire third-order term.

On v20, controlled noise ablations through third order are [hop_ablation.json](hop_ablation.json): removing only hop-CX noise gives 7.069863192e-5 (−3.29%); removing the idle noise attributed to hops gives 6.427612309e-5 (−12.07%); removing both gives 6.234977024e-5 (−14.71%). These are diagnostic modified-noise evaluations, not submitted/full-noise circuit scores.

## Geometry and limits

The fixed-start-cell endpoint relaxation (data paths ≤3, block distance ≤2, at most five data hops) has optimum 20 for the explicitly stated proxy 3×data-distance + block-distance, both with fixed labels and all 168 automorphisms: five data hops plus five block-distance units. Its witness cannot be assumed routable. The complete FREELAY lifetime model, where each wire moves only after its final encoder operation (or final pre-stage operation for data), with the current A/BC starting cells, at most two block teleports per wire, three data hops per wire, R≤55, and all 168 label automorphisms proves INFEASIBLE for ≤5 total data hops ([receipt](relocation5.receipt.json)); it reserves source and destination live intervals and includes encoder dependencies. This is a bounded model result, not a universal obstruction.

The six translated-prefix endpoint relaxations, with all label automorphisms and ≤6 data hops, give movement-CX lower bounds 12, 23, 15, 13, 26, 25 for r0c0, r0c1, r1c0, r1c1, r2c0, r2c1, while the current preparation cells stay fixed. The objective here is 2×data-distance + block-distance. Different block preparations, longer routes, and general interleaving remain open. No full block-teleport candidate from this search is claimed. The first completion branch makes exhaustive closure of those options unnecessary.

## Reproduction

Use the project `.venv/bin/python` with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`. `build.py`, `extra.py`, `combine.py`, `monitor.py`, and `cancel.py` generate full circuit families; `evaluate.py --fast` explores exact2 with validated triple pruning; `reference.py` runs unmodified exact2; `MAIN/spec/mc3.py <stem> --procs N` ranks finalists. Every saved candidate schedule is re-parsed and required to equal the judge native schedule. Geometry outputs are proxy/feasibility results only.

## Verification and remaining limits

The four new MC finalists have unmodified exact2 reference receipts; their printed third-order totals agree with the accelerated exploration to all printed digits. [manifest.json](manifest.json) records QASM hashes, data metadata, native R/CX, and passing 1e6-shot check evidence for every saved circuit, including the delivery alias. The copied MC runner in `inputs/mc3.py` is byte-identical to `MAIN/spec/mc3.py`; the local copy was required because that path was missing on jerry. The native-schedule comparison and actual judge gates, rather than builder layer labels, verify the deliverable.

The improvement is the observed three-seed mean required by the task; the difference is small relative to per-seed Monte Carlo uncertainty and does not establish statistical superiority of the true mean. No physical implementation or official submission was attempted. General block relocation, other encoder footprints, and routes inside the pre-stage with later CX partners following remain open. All lane-launched computation was collected on process exit; no HOPS worker is intentionally left running.
