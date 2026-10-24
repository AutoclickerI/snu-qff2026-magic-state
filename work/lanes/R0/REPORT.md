# R0 report

**No improved judge-valid circuit was found.** The success condition is not met. No submission was made.

The v16 reference was rerun on owl through the same evaluation pipeline: **8.55379233064e-5** mean over 100,000,000 shots at each of seeds 0, 1000, 2000; seed-0 acceptance **0.53313237**. Its exact total through third order is **8.41984e-5**.

The smallest physically audited routing objective with preparation connectivity is a **last round CX of 39** (`good10`); A couplings span **33–38**. This is a routing witness, not a synthesized full circuit. The smallest completed full circuit has A couplings **33–42**, last round CX **43**, and passes format/class/correctness at 1e6 shots, but fails acceptance. ALAP scheduling changes the A range to **34–42**, with the same last CX. There is no new fully judge-valid R to report.

## Full-circuit measurements

R is reported as **first A CX / last A CX / last round CX**, to avoid calling a highly staggered round “R=33” while it finishes at 43. Wait entries are each data qubit's first A coupling minus 33, in code-index order; they include intervals overlapped by moves. Move counts are two-CX transfers, excluding resets. `c1` is the contribution at p=0.001, as printed by exact2. The second/third columns are used only for |c1| < 1e-12. `exp(-A1)` is an analytical **estimate**, not an acceptance measurement. MC entries are each 1e8 shots.

| Candidate | R first / last A / last CX | Wait steps | Data moves | Block moves | Staggered | CX | c1 | 2nd | 3rd increment | Exact total | exp(-A1), estimate | MC 0 | MC 1000 | MC 2000 | Mean | Seed-0 acceptance, 1e8 | Acceptance, 1e6 | Judge, 1e6 | Files |
|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| [v16_bc2m](v16_bc2m.qasm) | 50 / 50 / 51 | 17 each | 6 | 0 | no | 207 | 3.1826e-19 | 5.83953e-05 | 2.58031e-05 | 8.41984e-05 | 0.53306 | 8.61136982e-05 | 8.52861662e-05 | 8.52139056e-05 | 8.55379233e-05 | 0.53313237 | 0.532286 | [PASS](v16_bc2m.check.log) | [JSON](v16_bc2m.json), [scores](v16_bc2m.score.json) |
| [abc_ideal](abc_ideal.qasm) | 33 / 42 / 43 | 8,0,3,7,9,5,9 | 6 | 19 | yes | 263 | 0.0025667 | invalid: c1 ≠ 0 | — | — | 0.47443 | 0.00326444899 | 0.00325184023 | 0.00326015221 | 0.00325881381 | 0.47591799 | 0.475811 | [FAIL acceptance](abc_ideal.check.log) | [JSON](abc_ideal.json), [scores](abc_ideal.score.json) |
| [abc_base](abc_base.qasm) | 33 / 42 / 43 | 8,0,3,7,9,5,9 | 6 | 19 | yes | 310 | 1.3695e-18 | 0.00070236 | 6.224e-05 | 0.0007646 | 0.45608 | — | — | — | — | — | 0.456927 | [FAIL acceptance](abc_base.check.log) | [JSON](abc_base.json), [scores](abc_base.score.json) |
| [alap_ideal](alap_ideal.qasm) | 34 / 42 / 43 | 9,1,3,9,9,5,9 | 6 | 19 | yes | 263 | 0.0025667 | invalid: c1 ≠ 0 | — | — | 0.4573 | 0.00314433214 | 0.00313679782 | 0.00315149735 | 0.0031442091 | 0.45888759 | 0.457704 | [FAIL acceptance](alap_ideal.check.log) | [JSON](alap_ideal.json), [scores](alap_ideal.score.json) |
| [alap_base](alap_base.qasm) | 34 / 42 / 43 | 9,1,3,9,9,5,9 | 6 | 19 | yes | 310 | 1.0752e-18 | 0.00054029 | 7.336e-05 | 0.00061365 | 0.43901 | — | — | — | — | — | 0.440789 | [FAIL acceptance](alap_base.check.log) | [JSON](alap_base.json), [scores](alap_base.score.json) |

`abc_ideal` and `alap_ideal` are state-correct joint B+C encoders with nonzero first-order loss. They were **not** excluded on c1: both received all three full MC seeds. They fail the judge's acceptance gate as well as having much higher 1-F. Their printed second-order diagnostic is deliberately not treated as a valid screen.

`abc_base` and `alap_base` use the independently checked base FT rule, not the stronger clean rule. Their exact totals are far outside the mandatory MC threshold 8.6724352e-5, and their measured 1e6 acceptance fails. No threshold-eligible candidate is awaiting MC. No new circuit has measured 1e8 acceptance above 0.5. First-use measurement variants were not expanded after these acceptance failures: that rewrite spends acceptance, so it cannot rescue these circuits.

## Binding constraints and solver receipts

The phase model prepares/checks B+C in the never-used region, consumes C, and prepares A in that region without touching the already-prepared B. It reserves both cells of each transfer, separately reserves destination initialization, permits data moves between A and B couplings, and requires each data A CX before its B CX. It allows two data moves and three block moves in the step-38 feasibility tests; more sequential two-CX transfers cannot fit before the required coupling in that time window. A may use all seven spare cells as preparation helpers. C partners are distinct, adjacent to their B qubits, and in the never-used region.

With CP-SAT presolve **disabled**, all six translation representatives are **INFEASIBLE for last round CX <= 38**. Their receipts below include solver response statistics and complete arguments. The other seven orientations are grid isometries of these six translations, so this covers the symmetry/translation placements for this model. This is a conditional model result, **not** an impossibility proof for every permitted circuit architecture.

| Search | Status | Wall seconds | Transform | First A | Last A | Last CX | Data moves | Block moves |
|---|---|---:|---|---:|---:|---:|---:|---:|
| [bound38_00](bound38_00.json) | INFEASIBLE | 0.808765304 | 0,0,0 | — | — | — | — | — |
| [bound38_01](bound38_01.json) | INFEASIBLE | 0.734502247 | 0,0,1 | — | — | — | — | — |
| [bound38_10](bound38_10.json) | INFEASIBLE | 5.01651116 | 0,1,0 | — | — | — | — | — |
| [bound38_11](bound38_11.json) | INFEASIBLE | 5.61523546 | 0,1,1 | — | — | — | — | — |
| [bound38_20](bound38_20.json) | INFEASIBLE | 1.57009794 | 0,2,0 | — | — | — | — | — |
| [bound38_21](bound38_21.json) | INFEASIBLE | 0.569148501 | 0,2,1 | — | — | — | — | — |
| [good10](good10.json) | OPTIMAL | 53.6884374 | 0,1,0 | 33 | 38 | 39 | 4 | 15 |
| [good20](good20.json) | FEASIBLE | 120.179276 | 0,2,0 | 33 | 40 | 41 | 1 | 15 |
| [compact10](compact10.json) | FEASIBLE | 180.182716 | 0,1,0 | 33 | 41 | 42 | 5 | 25 |
| [compact20](compact20.json) | FEASIBLE | 180.166687 | 0,2,0 | 33 | 40 | 41 | 4 | 14 |
| [abc_long](abc_long.json) | FEASIBLE | 180.268443 | 0,1,0 | 33 | 42 | 43 | 6 | 19 |
| [abc_alap](abc_alap.json) | OPTIMAL | 0.154002709 | 0,1,0 | 34 | 42 | 43 | 6 | 19 |

The physical transfer model allows an initial no-reset B move into a prefix MX cell at step 33: `CX destination->source; CX source->destination`. The measurement's known Z offset stays on B and is XORed into B's readout detectors. A can similarly reuse the one Z-measured prefix cell. Other destinations are initialized; initialization may overlap earlier work on the source. Later reuse of known source/measurement states is not exhaustively modeled, so this is another explicit limit of the bound.

Two geometric facts explain the gap:

1. The two-row shifts leave a two-cell disconnected component in the never-used region (`[24,30]` for transform 0,2,0). A seven-qubit block cannot be prepared across this disconnected component and the main component before step 33. The first relaxed step-37 routing witnesses placed B there and are **not preparation-feasible**. `bc20.receipt.json` independently returned UNSAT before adding any fault constraints. `good20` excludes these initial cells.
2. Exhaustive connected-region enumeration (`packing.py`, `packing.json`) finds only **15, 11, 2, 1, 0, 0** concurrent A+BC packings for translations (0,0), (0,1), (1,0), (1,1), (2,0), (2,1). Here A occupies seven connected cells, BC the other fourteen connected cells, and BC admits seven distinct adjacent B–C pairs. The two one-row/left packings put A along the bottom boundary, forcing substantial A transfers to upper data. This closes only the stated concurrent connected-region recipe.

The relaxed all-two-step models `relax2_*.json` reached last CX 37, zero data moves. They omit reset-basis costs and preparation constraints and are preserved only as lower-bound diagnostics. They are not full circuit candidates.

## Encoders and verified construction

The complete circuits use `abc_long`'s concurrent layout, A `[24,32,18,27,31,33,30]`, B `[0,34,2,4,17,23,29]`, C `[1,35,3,5,11,22,28]`, with the v16 prefix translated down one row. Exact A enumeration found a 13-CX, depth-7 encoder with danger **0.002** (`abc_long_A.json`, statistics adjacent), versus the supplied v16 A danger 0.0006666667. The encoder was independently checked by EXENC's state/topology/danger checks.

The joint B+C state-correct 24-layer encoder has 98 CX (`abc_ideal24.prep.json`). The 28-layer base-FT encoder has 145 CX and zero base-rule violations after 92 CEGAR constraints (`abc_base28.prep.json`, receipt adjacent). Clean-rule searches at depth 24 and 30 with free basis, and depth 28 with fixed canonical basis, timed out. Those are **timeouts, not infeasibility proofs**.

`build.py` merges native prefix steps, encoders, transfers, staggered couplings and deterministic detectors. Its current implementation schedules preparation and BC verification per cell ALAP; `abc_ideal`/`abc_base` preserve the earlier common-deadline experiment, and `alap_*` are its improved scheduling result. `route.py --alap --fixed-paths ...` fixes positions and C's labeling while maximizing coupling times at the same final CX. `audit_route.py` independently checks adjacency, resource conflicts, live-token occupancy and output mapping.

`check_prefix.py` confirms that all **137 native prefix operations** have exactly the same qubits (under the translation), gates and steps 0–32 as v16. In particular, native MX folding is preserved when a measured prefix cell is reused. This is recorded in the adjacent `.prefix.json` receipts. All four candidate QASMs have adjacent JSON data-qubit mappings and passed full `tprep.check` format/class/correctness, including detector determinism, at 1e6 shots.

## Loss attribution

ALAP scheduling lowers the base-FT exact total from **7.6460e-4 to 6.1365e-4**, but leaves it over seven times v16. The corresponding measured 1e6 acceptance is **0.440789**.

`pairs.py` calls MAIN/ablate.py's unchanged pair/triple evaluation engine with labels derived from the actual moving-token schedule. A single round-start cutoff would classify almost every post-prefix transfer as “round” for these staggered circuits. The receipt is `alap_base.pairs.log`.

The largest exact pair contributions are B idle × B idle **8.120e-5**, BC prep × B idle **7.060e-5**, and BC prep × BC prep **5.415e-5**. B idle × final data tail adds **3.916e-5**, B idle × data wait **3.820e-5**, and B idle × B move **3.159e-5**. Early C consumption releases routing space but leaves B waiting/moving after its verification. That added exposure dominates the data-wait savings in these measured constructions. The four leading pair terms alone exceed v16's entire loss.

## Scope, remaining uncertainty, and reproduction

All R0 compute jobs completed; no R0 background jobs remain. No successful full R35–37 construction was found. The bounded phase model closes last-CX <=38 for the stated preparation/transfer restrictions; unrestricted dynamic reuse of known states, more general preparation interleavings, and additional late B verification remain open. A routing witness is not an encoder or a judge result. The connected-region counts do not prove that arbitrary space-time Clifford preparation is impossible.

The requested MAIN/REPORT.md does not exist; MAIN/minit.py, MAIN/ablate.py and its v16 receipts were read. The other requested reports/tools were read. LAYOUT3 was read only. All generated files and caches are under R0. No credentials were accessed, no submission was attempted, and no agents were spawned. Dragon's expected repo path was absent; compute ran locally and on owl under the requested thread/CPU caps, with capacity checks before launches.

Reproduce from the repository root, with `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`:

```sh
.venv/bin/python work/lanes/R0/proof_batch.py
.venv/bin/python work/lanes/R0/packing.py
.venv/bin/python work/lanes/R0/build.py work/lanes/R0/abc_alap.json work/lanes/R0/abc_long_A.json work/lanes/R0/abc_base28.prep.json work/lanes/R0/alap_base
.venv/bin/python work/lanes/R0/check_prefix.py work/lanes/R0/alap_base
.venv/bin/python work/lanes/R0/evaluate.py alap_base 12
```

The evaluate script changes its working directory to R0. On owl, use the specified fnc-build:22.04 Docker wrapper and check capacity first. `manifest.json` records candidate hashes and confirms the mandatory MC audit.
