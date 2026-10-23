# LAYOUT2 — physical late logical-X parity check

All changes and artifacts are confined to this lane. No credentials were read and no submission was made. Python jobs used thread caps; no agents were spawned.

## Result

Best completed exact score: `c7e_m5_11_18.qasm`, 212 CX, first order 4.2188e-19, exact second 6.11575e-05, exact third total 9.73373e-05, exp(-A1) 0.51209; official 1e6-shot PASS, acceptance 0.51139.

Best completed three-seed mean: `c7e_m5_11_18.qasm`, 0.000100842765; seed-0 key 0.000101329603; 2.78% below the supplied baseline mean.

The final artifact is [best.qasm](best.qasm) with [best.json](best.json). It is byte-identical to the named winner and includes the data-qubit mapping, layout, provenance, exact scores, all MC seeds, and SHA-256.

The lowest measured seed-0 key among these candidates is `c12.qasm`: 0.000100232998, with mean 0.0001011206. The mean-based ranking is used for `best`; this lane does not submit. Close rankings among the finalists are within MC sampling uncertainty.

Comparison supplied in the task: cand_best_m exact third total 1.01894e-4; 1e8-shot seeds 0/1000/2000 mean 1.0373e-4; acceptance 0.544.

## Reproducible full-circuit layout

The passing r23_1_3 family has:

```text
d = [7,25,19,16,15,17,8]
A = [13,26,20,22,21,23,14]
B = [6,24,18,10,9,11,2]
C = [0,30,12,4,3,5,1]
M = {1,3,5}; target cells = [26,22,23]
cat = [27,28,29]; CX tree 27->28->29
R+1 checks: 27->26, 28->22, 29->23; cat MX parity at R+2
data moves = [[15,16,17],[4,10,16],[3,9,15],[7,13,19],[0,6,7],[20,26,25]]
hops = 12; BC helpers = 0
```

A: 13 CX, depth 8, danger vector [0,9,0,23,0,4,0,0] in p/15 units. M avoids every occupied Z_L Z_j bin; it also detects a pure Z_L. The emitted encoder and its Pareto alternatives were independently checked against synth.check and synth.dangerous_z.

The 68-CX BC preps have 14 layers and zero bad X faults at every cell/time under the required rule sB==sC and pB==pC and pB==(sB==0). Every emitted SAT circuit also passes a GF(2) target-space rank check and the actual at-most-K cap.

The merge preserves the judge schedule of the existing pre-stage, respects each cell’s release, and schedules routes, both preps, and cat preparation together. The cat may reuse a helper only after its prep duties end. The `e` variant reads A\M at R+1; only M needs to wait for the R+1 cat couplings. This change is separately validated by the full judge.

## Full-circuit measurements

Third is the total through order three, not the isolated cubic term. Judge acceptance is measured at 1e6 shots; exp(-A1) is the analytical estimate.

| Circuit | R | CX | First | Exact second | Exact third | exp(-A1) | Judge acceptance | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| [c0](c0.qasm) | 63 | 226 | 3.1086e-19 | 5.01584e-05 | 0.000133873 | 0.4342 | 0.434366 | FAIL |
| [c0_mall](c0_mall.qasm) | 63 | 226 | 3.1086e-19 | 4.84473e-05 | 0.00013089 | 0.42207 | 0.422289 | FAIL |
| [c1](c1.qasm) | 62 | 224 | 5.7673e-19 | 7.76326e-05 | 0.00016078 | 0.43866 | 0.439388 | FAIL |
| [c10](c10.qasm) | 55 | 212 | 4.2929e-19 | 6.52539e-05 | 0.000105432 | 0.50889 | 0.509506 | PASS |
| [c11](c11.qasm) | 54 | 213 | 4.2188e-19 | 6.11585e-05 | 9.80719e-05 | 0.51134 | 0.511236 | PASS |
| [c12](c12.qasm) | 54 | 213 | 4.2188e-19 | 6.11575e-05 | 9.83296e-05 | 0.51009 | 0.509573 | PASS |
| [c1_mall](c1_mall.qasm) | 62 | 224 | 5.5822e-19 | 7.53943e-05 | 0.000157258 | 0.42627 | 0.426001 | FAIL |
| [c2](c2.qasm) | 55 | 219 | 5.2151e-19 | 7.05352e-05 | 0.000110564 | 0.5089 | 0.508551 | PASS |
| [c3](c3.qasm) | 56 | 223 | 3.5527e-19 | 7.23288e-05 | 0.000118992 | 0.49387 | 0.493462 | FAIL |
| [c4](c4.qasm) | 57 | 223 | 3.1086e-19 | 6.44096e-05 | 0.000111691 | 0.49287 | 0.49274 | FAIL |
| [c5](c5.qasm) | 55 | 212 | 4.2929e-19 | 6.51499e-05 | 0.000105587 | 0.50822 | 0.508125 | PASS |
| [c6](c6.qasm) | 56 | 214 | 4.1818e-19 | 6.12827e-05 | 0.000105556 | 0.49737 | 0.49738 | FAIL |
| [c7](c7.qasm) | 54 | 212 | 4.2188e-19 | 6.21852e-05 | 9.90954e-05 | 0.51329 | 0.513581 | PASS |
| [c7e](c7e.qasm) | 54 | 212 | 4.2188e-19 | 6.21352e-05 | 9.83524e-05 | 0.51466 | 0.514875 | PASS |
| [c7e_m5_11_18](c7e_m5_11_18.qasm) | 54 | 212 | 4.2188e-19 | 6.11575e-05 | 9.73373e-05 | 0.51209 | 0.51139 | PASS |
| [c8](c8.qasm) | 54 | 212 | 4.2929e-19 | 6.27989e-05 | 9.9859e-05 | 0.51336 | 0.513519 | PASS |
| [c9](c9.qasm) | 55 | 212 | 4.2188e-19 | 6.38303e-05 | 0.000104235 | 0.50791 | 0.508635 | PASS |

Each row has `<stem>_check.log`, `<stem>_exact.log`, and `<stem>_metrics.json`. Acceptance failures are retained as counterexamples. All checked circuits pass format, class, and correctness; their failures are acceptance failures.

## Monte Carlo

| Circuit | seed 0 | seed 1000 | seed 2000 | mean | Acceptance mean |
|---|---:|---:|---:|---:|---:|
| c11 | 0.000102689 | 0.000100673 | 0.000101152 | 0.000101505 | 0.5117 |
| c12 | 0.000100233 | 0.000101323 | 0.000101806 | 0.000101121 | 0.510463 |
| c7 | 0.000101634 | 0.000103219 | 0.000102827 | 0.00010256 | 0.513682 |
| c7e | 0.000102347 | 0.00010177 | 0.000100108 | 0.000101408 | 0.51503 |
| c7e_m5_11_18 | 0.00010133 | 0.000101104 | 0.000100095 | 0.000100843 | 0.512481 |
| c8 | 0.000103192 | 0.000101322 | 0.00010282 | 0.000102445 | 0.51374 |

## Layout search and A encoder screen

`layout.py` is CP-SAT over data and A/B/C placements, legal ordered data routes, checkerboard partner colors, connected A, connected B+C+helpers, a Fano logical-X line, and a connected three-cell cat with three simultaneous adjacent targets. Two cat controls cannot perform three CX at R+1. Geometry is optimized by round-time lower-bound surrogate, hops, then helpers; actual R comes from the full merged schedule. Encoder-dependent admissibility is enforced by exact post-synthesis screening, not inferred from geometry.

A search keeps a nondominated set over all eight danger bins, depth, and CX. The initial screen enumerates all ASAP circuits from minimum CX through minimum+2. These are finite-domain conclusions, not unrestricted encoder optimality claims. The selected layout was extended through minimum+4 (15 CX): 43,516,789 canonical circuits in the 15-CX class alone, with all emitted witnesses independently verified. See `a_extra3_layout_A_stats.json` and `a_extra4_layout_A_stats.json`.

| Admissible layout | R surrogate | Hops | Connectivity helpers | M | Cat cells | A CX/depth |
|---|---:|---:|---:|---|---|---|
| h1_0_3.json | 37 | 12 | 0 | [1, 3, 5] | [27, 28, 29] | 13/8 |
| r23_2_10.json | 37 | 14 | 1 | [1, 3, 5] | [27, 28, 29] | 13/8 |
| sep_0_12.json | 39 | 10 | 4 | [0, 5, 6] | [25, 26, 20] | 11/7 |
| t53_1_4.json | 39 | 11 | 0 | [0, 1, 2] | [24, 26, 25] | 13/8 |
| sep_1_17.json | 39 | 11 | 0 | [1, 3, 5] | [21, 22, 28] | 11/7 |
| sep_1_15.json | 39 | 11 | 4 | [2, 4, 5] | [27, 21, 28] | 11/7 |
| h1_2_7.json | 39 | 12 | 0 | [1, 3, 5] | [34, 22, 28] | 13/8 |
| sep_2_9.json | 39 | 12 | 0 | [0, 5, 6] | [25, 26, 20] | 12/7 |
| sep_1_12.json | 39 | 12 | 4 | [1, 3, 5] | [15, 16, 22] | 11/6 |
| sep_0_7.json | 39 | 13 | 0 | [1, 3, 5] | [28, 22, 21] | 11/7 |
| t17_0_2.json | 39 | 13 | 2 | [0, 1, 2] | [24, 31, 25] | 12/9 |
| sep_1_11.json | 39 | 14 | 2 | [2, 4, 5] | [15, 16, 22] | 11/6 |
| h1_2_4.json | 39 | 15 | 0 | [1, 3, 5] | [10, 4, 11] | 13/9 |
| sep_0_3.json | 39 | 15 | 4 | [1, 3, 5] | [28, 22, 21] | 11/7 |
| sep_2_8.json | 39 | 16 | 1 | [0, 1, 2] | [25, 26, 20] | 12/7 |
| sep_2_7.json | 39 | 16 | 2 | [1, 3, 5] | [26, 27, 20] | 12/6 |
| h1_2_2.json | 39 | 17 | 0 | [1, 3, 5] | [10, 4, 11] | 13/8 |
| sep_2_5.json | 41 | 12 | 2 | [1, 4, 6] | [26, 27, 20] | 11/6 |
| sep_2_4.json | 41 | 18 | 2 | [1, 4, 6] | [26, 27, 20] | 12/7 |
| sep_1_6.json | 41 | 18 | 2 | [2, 4, 5] | [16, 15, 22] | 12/7 |

Geometric incumbent JSONs and layout logs preserve all found placements, including failed A screens. `screen.json` summarizes the A screen. All four legal shortest-route combinations of r23_1_3 retain R=55 with the c5 prep (`c5r_routes.json`).

## Synthesis findings and limits

- Unrestricted BC pivot/basis searches mostly timed out (UNKNOWN, not UNSAT). Fixing canonical pivots and their matching output-generator basis made the same target synthesis tractable: 14-layer, 68-CX FT witnesses appeared in seconds.
- The K=60..67 and depth 12..13 UNSAT results apply only with those canonical pivots/basis and the stated depth; they do not prove unrestricted bounds.
- Initial `bc_fixed_*` seed-0 trials used a pivot-order mismatch and are invalid. The corrected `bc_basis_*`, `bf_*`, `narrow_*`, and `vary_*` runs use consistent ordering; final emitted witnesses have independent state and FT checks.
- Independent staged BC encoders plus swaps gave an 82-CX/depth-23 diagnostic. Window SAT reduced this to a certified 80-CX/depth-22 witness, but the resulting R=62 circuit fails acceptance. It was superseded by the direct 14-layer syntheses.
- The existing 73-CX BC template admits 144 relative Steane automorphisms under the FT test. Embedding that template in a cat-compatible layout did not yield a candidate within the searches. Fixed-B permutation infeasibility was also checked with CP-SAT presolve disabled; no global layout impossibility is claimed.
- First-use measurement screening uses the copied minit.py. On c5, q11, q18, q5 improved exact second order by 3.6667e-7, 3.2222e-7, and 1.6667e-7 respectively; full third-order and judge checks assess the combined change.
- Larger 14-CX A encoders reduce the pre-filter danger units from 36 to 25/23, but their full second-order scores stay essentially unchanged and their third-order scores worsen (c11/c12). Once the logical-X filter is present, minimizing raw A danger alone is not the right final objective. The 15-CX Pareto frontier is preserved; it was not promoted to further full-circuit candidates on that proxy alone.
- All six candidates below the exact-third threshold received all three requested 1e8-shot MC seeds. No threshold-triggered MC is pending. Global optimality over layouts, encoders, and joint preparations remains unproved.

## Reproduction

Run from this directory with PYTHONDONTWRITEBYTECODE=1 and OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1:

```bash
A_EARLY=1 /home/jihoon/competitions/quantumn/.venv/bin/python build.py r23_1_3.json r23_1_3_A_filtered.json r23_1_3_BC_d14_k68_s5.json replay
/home/jihoon/competitions/quantumn/.venv/bin/python minit.py replay . 5,11,18
/home/jihoon/competitions/quantumn/.venv/bin/python evaluate.py replay_m5_11_18 16
```

To rerun synthesis separately: `encode.py r23_1_3.json --workers 2 --extra 2`, or `BC_PIVOTS=1 BC_BASIS=1 bc.py r23_1_3.json 14 68 5`, using the required Python executable. Solver reruns may find different witnesses; use the preserved prep JSONs for exact circuit reconstruction.

Use owl’s specified Docker image for pycryptosat; the mirrored wheel requires newer glibc than native tom. The copied enumeration binary also requires owl’s container or local zebra. `evaluate.py` invokes the original exact2.py --third and unmodified tprep.check; it never submits.
