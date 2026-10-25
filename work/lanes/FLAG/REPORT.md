# FLAG: removing or protecting the A-flag gap idles of v36h (PLAN P88)

Verdict: **closed, no finalist.** On v36h's roles every valid flagged round leaves at least two data gap ticks and
q10 always takes one; protecting a gap needs a free neighbour at the gap tick, and every way to free one creates
another gap, breaks B's check, or needs a much worse A encoder. v36h reproduced at 3.8154733224167045e-5.

## Prize (all orders, counterfactuals on v36h, `region2.py`, `cf/`)
| Change | 1-F | Δ |
|---|---:|---:|
| both gap idles (q10, q21 at 44) noiseless | 3.5491042052e-5 | −2.664e-6 (−7.0%) |
| q21's gap tick moved onto q10 | 3.8115103027e-5 | −3.96e-8 |
| q10's gap twice as long | 3.9523832206e-5 | +1.369e-6 |
Moving gap ticks between data is worth ≤ 4e-8; only removing or protecting them pays.

## The structural claim, corrected (`flagenum.py`: exact GF(2) model of the round)
"Both qubits of the first decoder CX must be coupled by t43" is false as stated: CX9→15 and D21→A15 share only a
target and commute; A15 couples at 43 only because it is busy at 44. The stronger statement holds: a decoder CX whose
control is cell c needs c's D→A before it; a decoder entirely at tick 45 cannot keep the full X-syndrome readout (a
one-cell record loses the checks containing it, a two-cell record conflicts with one), so the flag needs gates at 44,
and a cell busy at 44 forces its data to couple at 43 and wait. With ≤ 1 gap tick: 4,198,620 configurations, 0 valid.
With 2: 18,387,060, 104 valid, in three placements: {q10, q21} (v36h's decoder), {q7, q10} (CX9→8 @44, CX9→15 @45,
MX9), {q10, q10} (D10→A9 @42, CX9→15 @43, CX8→9 @45). All 104 read the {8,9,15} line and catch the same faults. The model
reproduces v36h's flag and rejects IDEAS' "decoder CX before D10→A9".

## Leads (each closes only the recipe tested)
| Recipe | Price | Result |
|---|---|---|
| Star decoder (CX9→15 @44, CX9→8 @45, MX9) | `v36h_star9`: 3.815473322416705e-5, judge 1e6 PASS, same seed-0 draw | exactly equivalent to v36h |
| Mirror placement (gaps q7, q10) | AENC exhaustive A-encoder search: 0 legal encoders | closed |
| Both gap ticks on q10 (frees q21) | data side −3.96e-8; 49 legal encoders, best first-order 4.759e-6 vs v36h's 1.858e-6 | closed (+2.9e-6 encoder, AENC first-order estimate) |
| B→D earlier for the gap data | the gap idle (≈ 1.35e-6) becomes a post-B idle (≈ 5.4e-6) | closed (inferred from adjoint costs) |
| B→D later | needs a 48th tick: every output idles | closed |
| One qubit with B→D before D→A | A's rows stay deterministic only if none or all 7 are reversed (126 subsets checked) | invalid (as TERM's `v36c_d21r`) |
| Another weight-3 X_L line | of the 7 on A's cells only {8,9,15} is a grid path | closed |
| Relabel A by a Steane automorphism | the D–A (and D–B) pairing on the grid is unique | no change |
| Known-state guard at 44 | every neighbour of every data qubit is busy at 44 (except q21 itself) | closed on these roles |
| Identity pair on q10 with A16 (D22→A16 to 43, CX10→16 at 42 and 44, q10's T† to 41) | `v36h_e16`: 3.9862650268926e-5 (+1.708e-6), judge 1e6 PASS; q22's new gap 1.341e-6, CX at 42 0.756e-6 | closed: A16's Z errors land on q22 and q10 |
| Identity pair on q10 with B4 (CX10→4 at 41, 43) | needs both gap ticks on q10 (+2.9e-6 encoder); B4's Z errors hide in B's syndrome | closed (masking inferred) |
| Pair between data (q21 with q20 or q22) | cannot straddle both D→A without a conflicting order | closed |
| Check X_L before coupling (decode, measure, re-encode) | needs cells 8, 9, 15 for 5 ticks; 15 is free only from 39 | closed by timing |
Open: a new layout with a free or known-state cell next to q10 at 44 plus one next to q21 or q7 (R43: round tick ≥ 45,
12 hops); upside ≤ −1.61e-6 with helpers, −2.66e-6 if both gaps were noiseless.

## Verified vs inferred
Verified: every all-orders price; both builds pass the judge at 1e6; `dets.py` marks all 79 v36h detectors
deterministic; the enumeration reproduces v36h's flag and IDEAS' invalid move; AENC re-run reproduces 87 encoders for
v36h's timing and 0 for the mirror. Inferred: the post-B idle and B4 masking costs; the +2.9e-6 encoder penalty is AENC's
first-order estimate on v36c's surroundings. The impossibility assumes depth 47, B→D at 45, B checked immediately before
coupling, and a decoder on A's cells.

## Files
`results.json` (keyed by QASM sha256, data_qubits and evaluator hashes), `flagenum.py`, `flagenum_g{1,2}.json`, `dets.py`,
`region2.py`, `cf/`, `enc/`, `v36h_star9.*`, `v36h_e16.*`, `build_echo16.py`, `*.allorders.txt`, `*.judge1e6.txt`.
(Written by the main session from the lane's final message; the lane's own write was blocked.)
