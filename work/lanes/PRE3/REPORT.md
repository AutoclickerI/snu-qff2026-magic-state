# PRE3 — release schedule, re-embedding, and early-round prices

This lane used the v16e cultivation prefix through nominal step 32 (the barrier at source line 204), then the same separate 9-CX A/B/C encoders and three-step Steane suffix used by `MAIN/gf/gf33.py`, with adjacency disabled only for the prices. The data cells are `[0,20,7,4,3,15,8]` in code order, i.e. the set `{0,3,4,7,8,15,20}`. Every generated QASM has a matching JSON file with `data_qubits`.

The data qubits' last gates are all at step 32: `q0=q20=q7=q4=q3=q15=q8=32` (the final `tdg`). For the occupied neighbouring ancillas, q19's last CX is step 14 and q13's is step 18; q1, q2, q6, q9, q10, and q14 have their last CX at step 31 and their terminal readout at step 32. The 12 distinct non-data neighbours are `1,2,5,6,9,10,13,14,16,19,21,26`; their detector-safe release is measured at the step below and therefore usable from the following step.

| Prefix variant / method | Release step for neighbours `1,2,5,6,9,10,13,14,16,19,21,26` | Free distinct partners at steps 33 / 34 / 35 | Grid-free exact 1-F with round at 33 | Grid-free check | Files |
|---|---|---:|---:|---|---|
| `base` — v16e barriers and terminal readouts | `33,33,0,33,33,33,33,33,0,33,0,0` | 12 / 12 / 12 | `4.93973e-5` (third order) | PASS | [base.qasm](base.qasm), [base.json](base.json), [base.exact.txt](base.exact.txt) |
| `q13_19` — move q13 `h;measure` to step 19 and drop its later barriers | `33,33,0,33,33,33,20,33,0,33,0,0` | 12 / 12 / 12 | `4.91823e-5` (third order) | PASS | [q13_19.qasm](q13_19.qasm), [q13_19.json](q13_19.json), [q13_19.exact.txt](q13_19.exact.txt) |
| `q19_13_prompt` — move q19 Z measurement to step 15 and q13 X measurement to step 19 | `33,33,0,33,33,33,20,33,0,16,0,0` | 12 / 12 / 12 | `4.91823e-5` (third order) | PASS | [q19_13_prompt.qasm](q19_13_prompt.qasm), [q19_13_prompt.json](q19_13_prompt.json), [q19_13_prompt.exact.txt](q19_13_prompt.exact.txt) |
| `q19_11` — physical earliest q19 measurement (step 11) | `33,33,0,33,33,33,33,33,0,12,0,0` | 12 / 12 / 12 | —; detectors #1/#8/#22 nondeterministic | FAIL correctness | [q19_11.qasm](q19_11.qasm), [q19_11.check.json](q19_11.check.json) |
| `q19_15` — q19 alone at its last-CX successor | `33,33,0,33,33,33,33,33,0,16,0,0` | 12 / 12 / 12 | —; detectors #1/#8/#22 nondeterministic | FAIL correctness | [q19_15.qasm](q19_15.qasm), [q19_15.check.json](q19_15.check.json) |
| `q19_13_earliest` — q19 at 11 and q13 at 19 | `33,33,0,33,33,33,20,33,0,12,0,0` | 12 / 12 / 12 | —; detectors #1/#2/#22 nondeterministic | FAIL correctness | [q19_13_earliest.qasm](q19_13_earliest.qasm), [q19_13_earliest.check.json](q19_13_earliest.check.json) |
| `active` — barrier on only the layer's touched cells | ASAP schedule; nominal partner set unchanged | 12 / 12 / 12 | `1.54480e-4` (third order), acceptance estimate `0.43106` | PASS correctness, FAIL acceptance | [active.qasm](active.qasm), [active.json](active.json), [active.exact.txt](active.exact.txt) |
| `active_q19_13` — active barriers plus both early readouts | ASAP schedule | 12 / 12 / 12 | —; detectors #1/#2/#22 nondeterministic | FAIL correctness | [active_q19_13.qasm](active_q19_13.qasm), [active_q19_13.check.json](active_q19_13.check.json) |

The partner sets are unchanged across steps 33–35 because all remaining occupied ancillas are measured at step 32. Per data qubit they are:

| Data cell | Free partner cells at 33–35 |
|---:|---|
| 0 | 1, 6 |
| 3 | 2, 9 |
| 4 | 5, 10 |
| 7 | 1, 6, 13 |
| 8 | 2, 9, 14 |
| 15 | 9, 14, 16, 21 |
| 20 | 14, 19, 21, 26 |

Thus the end-of-prefix geometry has only 12 distinct partner cells, below A+B's 14 requirement. Moving q19/q13 earlier changes when those cells can be used during the last prefix layers, but cannot change the 12-cell boundary union.

## Alternative embeddings

`scan_embeddings.py` enumerated the 8 grid isometries and all legal translations of the 15-cell v16 interaction footprint (58 legal placements). It preserves direct CX adjacency and the data-role placement; relabelling cat members within the same footprint leaves the geometry unchanged. The best placements are:

| Placement | Data cells in code order | Distinct free neighbours | Minimum free degree over the 7 data | Sum of free degrees |
|---|---|---:|---:|---:|
| incumbent `s0_r0_c0` | `[0,20,7,4,3,15,8]` | 4 | 0 | 5 |
| `s4_r0_c2` (LAYOUT3 transform) | `[2,17,9,26,20,22,15]` | 6 | 0 | 7 |
| `s0_r1_c0` | `[6,26,13,10,9,21,14]` | 7 | 0 | 8 |
| `s1_r1_c2` (best in this scan) | `[12,28,17,8,9,21,16]` | **8** | 0 | 9 |

Every placement has at least one data cell with no free neighbour; the maximum distinct union is 8, so isometric re-embedding cannot supply 14 distinct partners. The binding graph feature is that the two interior data vertices corresponding to cells 7 and 8 have graph degree four, so all four grid neighbours are already occupied by the prefix interaction graph. Adding cat members only consumes free cells and cannot release one of those four neighbours. The scan receipt is [embedding_scan.json](embedding_scan.json); it is a bounded isometry/translation search, not a proof against an unrestricted new cultivation graph.

## Data movement during idle gaps

The static one-hop screen in [movement_screen.json](movement_screen.json) checks every untouched adjacent destination and requires it to touch every later partner of the moved data token. It finds:

| Data token | Untouched adjacent destinations | Binding later partner |
|---:|---|---|
| 0 | none | — |
| 3 | none | — |
| 4 | 5 | q10 at step 31; q5 is not adjacent to q10 |
| 15 | 16 or 21 | q9 at step 31; neither destination is adjacent to q9 |
| 20 | 21 or 26 | q14 at step 31; neither destination is adjacent to q14 |

The idle windows around steps 23–30 therefore do not admit a one-hop data move that preserves the later CXs. Moving the corresponding partner as well needs a coupled two-token chain (at least six additional CX/reset units), gives no new end-of-prefix partner cell, and leaves no tested schedule that beats the q13 release. This is why no moved-data QASM is included as a candidate.

## Grid-free full-circuit prices and MC ranking

All three release variants below have 129 CX and `|c1|=3.18e-19`; the exact third-order screen is valid. The 1e8-shot values are `fast_check` with seeds 0, 1000 and 2000. The suffix is deliberately grid-free; the real-grid format check fails on the first non-neighbouring block CX, as recorded in [real_grid_checks.json](real_grid_checks.json). No real-grid full circuit was built because the 12-versus-14 partner shortage remains binding.

| Variant | R | CX | c1 | 2nd | 3rd increment | exp(-A1) | MC seed 0 / 1000 / 2000 | MC mean | seed-0 acceptance | Files |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| `base` | 33 | 129 | `3.18e-19` | `4.09141e-5` | `8.48318e-6` | `0.57462` | `5.01199e-5 / 5.02754e-5 / 4.83988e-5` | `4.95980e-5` | `0.57442261` | [base.mc.json](base.mc.json) |
| `q13_19` | 33 | 129 | `3.18e-19` | `4.09141e-5` | `8.26819e-6` | `0.57958` | `4.94306e-5 / 4.82481e-5 / 4.92107e-5` | **`4.89631e-5`** | `0.57939789` | [q13_19.mc.json](q13_19.mc.json) |
| `q19_13_prompt` | 33 | 129 | `3.18e-19` | `4.09141e-5` | `8.26819e-6` | `0.58612` | `4.98291e-5 / 4.94151e-5 / 5.02916e-5` | `4.98453e-5` | `0.58590255` | [q19_13_prompt.mc.json](q19_13_prompt.mc.json) |
| `active` | 33 | 129 | `3.18e-19` | `5.26435e-5` | `1.01837e-4` | `0.43106` | not run (acceptance below 0.5) | — | `0.431994` at 1e6 | [active.exact.txt](active.exact.txt), [active.check.json](active.check.json) |

The measured three-seed ranking selects `q13_19`. The q19+q13 schedule releases one more cell at step 16 and raises acceptance, but its three-seed MC draw is higher; the exact third-order values tie at the printed precision. These prices are estimates for the real-grid goal because adjacency was intentionally ignored.

## Verification and binding constraint

`verify_variants.py` ran the judge at 1e6 shots with adjacency disabled. `base`, `q13_19`, and `q19_13_prompt` pass format, class, deterministic detectors, correctness, and acceptance. `q19_11`, `q19_15`, `q19_13_earliest`, and `active_q19_13` fail the deterministic-detector check; `active` passes correctness but fails the 0.5 acceptance gate. The real-grid checks for the three priced variants fail only the expected non-neighbouring suffix CX format gate.

The best deliverable is therefore the `q13_19` prefix release: q13 is free from step 20, the 12 partner cells are all free by step 33, and its grid-free round price is `4.89631e-5` by the required three-seed MC mean. The binding constraint for a complete grid circuit is spatial, not prefix noise: the cultivation footprint leaves only 12 distinct cells adjacent to the data, while the fault-tolerant A/B round needs 14 distinct partners. No submission was made and no credentials were read.
