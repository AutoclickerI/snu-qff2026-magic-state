# Plan

## Status (2026-10-24 21:45 KST)
- Board: Placeholder 5.067e-5 (197 CX, 20:46); us 5.62881e-5 = v30f_r454 (rank 2, 189 CX). Gap 10%. v30f all-orders
  5.89377e-5; the next slot needs a v30f-lineage gain (COMP29, WAITPROT, SEPBC, BCPOL, ST2) or a new placement (FRESH, ENDSTATE).
- **Total redesign (Jihoon, 2026-10-24 19:50: "we need total redesign for the larger jump").** Polishing the v23/v25 lineage
  tops out near 6.0e-5 if every verified edit composes. LADDER (adjacency ignored, our prefix): separate small B/C + standard
  A at R45 give 5.03e-5, an earlier round 3.74e-5 at R33; the grid-free reference is 3.55e-5; any circuit ≥ 1.162e-5
  (proved). Data hops cost ~0, so data can travel to compact blocks. The core open question is the end-state geometry.
- Loss ledger (FINDINGS): of v23h_c2c9's 6.92e-5, the round alone is 2.87e-5 and ≈ 4e-5 is cross-region.

## Critical path
Redesign: end-state geometry (ENDSTATE) → prefix embedding and data/block routing to it with the earliest R (ST1, SEPBC,
FRESH) → full build → exact2 --third → speed gate → mc3 → `work/promote.sh`. Bottleneck: the end-state feasibility with
small grid-native block preps; every earlier closure of it was model-bound.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P71 | G1 | ENDSTATE: separate moved blocks closed (exposure; best 2.08e-4 at R56). Now in-place joint B∪C regions on cells free during the prefix (time-indexed, 48 embeddings), A on released cells, resource synthesized in place with FRESH's synthesizer and reviewer 4's helper primitives | complete circuits below v30f, or the binding constraint on R | Codex lane ENDSTATE (`work/lanes/ENDSTATE`, zebra, hippo) | active |
| 2 | P66 | G1 | ST1: prefix/round co-design from scratch: prefix embedding (48) or re-synthesized cat layout, ENDSTATE end-states, data hops out of the prefix, just-in-time compact block preps, teleports, earliest R; full builds with exact feedback | a grid circuit below 5.0e-5 exact, then lower | Codex lane ST1 (`work/lanes/ST1`, owl, zebra) | active |
| 3 | P72 | G1 | FRESH: delivered v30f (correlated rank-3 B/C); local early-round attempts stop at R44–45 (FINDINGS). Now a global joint re-synthesis of the cultivation prefix placement/schedule with the end-state (earliest R, then exposure); ST1 does local relayout macros | a verified grid circuit below 5e-5 true, or designs closed by mechanism | Codex lane FRESH (`work/lanes/FRESH`, zebra, sunfish) | active |
| 4 | P69 | G1 | SEPBC: delivered v28s, the q5 detectors on v29c and the ENDSTATE emitter (FINDINGS). Now v30f's round-start critical path: which chain forces R48, then shorten it (shallower in-place resource with reviewer 4's helper primitives, early layers on early-free cells, prefix-tail reorder, earlier A) | each R step ≈ 1.4e-6; a v30f-lineage circuit with earlier R below v30f | Codex lane SEPBC (`work/lanes/SEPBC`, tom, zebra) | active |
| 6 | P67 | G1 | ST2: macro-rewrite population search on v30f (init/check forms, commuting schedule, transfer phase, readout edge, timing, idle-slot detectors), seeded with COMP29's finalists | a v30f-lineage finalist below COMP29's best by 3-seed mean | Codex lane ST2 (`work/lanes/ST2`, zebra, sunfish, tom) | active |
| 5 | P73 | G1 | COMP29: port the v23h→v29c local edits (blue XZ check, exchange, instrument, readout copy, LNS2/ST2 edits, timing feedback, known-zero detectors) onto v30f and price every combination | a v30f-lineage finalist below v30f by 3-seed mean | Codex lane COMP29 (`work/lanes/COMP29`, jerry, owl) | active |
| 5 | P74 | G1 | WAITPROT: reviewer 4's selective Z protection of waiting data on v30f (helper \|+⟩, CX h→q twice around the wait, MX h; Fano-line triple meets every weight-3 Z logical) | priced singles/pairs/Fano triples; a finalist below v30f or the mechanism | Codex lane WAITPROT (`work/lanes/WAITPROT`, tom, zebra) | active |
| 6 | P59 | G1 | BCFB: port its best clean B+C preps into v25k/v26n and re-run the exact feedback search in situ | a v25k-lineage circuit below v27x by re-draws | Codex lane BCFB (`work/lanes/BCFB`, owl) | active |
| 7 | P62 | G1 | BCPOL: endpoint machinery on v30f's resource (boundary cache rebuilt for v30f, rank-4 endpoints, partial clean, reviewer 4's encoded-Bell endpoint via FRAME_X, C6, helper primitives) | a v30f-lineage resource below v30f by all-orders | Codex lane BCPOL (`work/lanes/BCPOL`, jerry, hippo) | active |
| 8 | P70 | G2 | XTIM: the trigger of xtim's per-shot slow path, a fast speed predictor, physics-preserving rewrites (q8's −1.2% on v26n) | rule + validated `work/lanes/XTIM/speed_predict.py` | Codex lane XTIM (`work/lanes/XTIM`, zebra) | active |
| 10 | P2 | G1 | Hourly submission of the best verified candidate (`work/promote.sh`, seed-0 re-draws, R-20261023-10) | each slot with a gain used; final best in by 2026-10-30 10:00 | main session | active |
Done today (FINDINGS): ST_BC (disposed 21:45, R-20261024-6), BCPOL v25k pass (rank4_3: all-orders 6.1146e-5), KNAP (v25k), LNS2 (v26n), LADDER, BIRD, GAP, XTIM, WALSH (`work/lanes/WALSH/allorders.py`), LNS (stopped), and the closed lanes listed there.

## Parked ideas (from the earlier idea and reviewer 1–2 reviews; outcomes of the rest are in FINDINGS)
- One flag qubit (CX f→q twice, read X) on the A encoder's window where its 8 dangerous single faults sit (inferred
  −0.2 to −0.8e-5); ACHECK's zero-CX checks took part of that term.
- Checkerboard rule (each block cell opposite in colour to its partner) to prune layouts before any solver.
- Chamberland–Cross flagged logical-H measurement: our grid build was not FT at first order (implementation suspect).

## Reviewer 3 review (2026-10-24, on commit a9cae1c; text in `work/lanes/MAIN/spec/reviewer3.md`)
The reviewer's zip (QASMs, scripts) is behind a chatgpt.com library link we cannot fetch; lanes re-derive.
| # | Claim | Check | Item |
|---|---|---|---|
| 1 | Copy the last C readouts onto fresh helpers, detect disagreement (+3 CX, same depth) | **reproduced** by exact2: v23h_c2c9 + copy4 6.87707e-5 (−0.65%), exp(-A1) 0.535, 3.6 s per 1e6 | P60 |
| 2 | Helper-verified init, helper measured in the same tick as the qubit's first op | **reproduced** on v22 by exact2: init6 7.00021e-5 (−1.83%), copy4 + init6 6.95552e-5 (−2.46%), exp(-A1) 0.523, 2.7 s per 1e6; port to v23's MX-init prep pending | P60 |
| 4 | 128 partial clean policies between base and clean | valid: BCSYN2's `Model.cut` forces s_B = 0 when d = 0 | P62 |
| 5 | Synthesize prep + B→C check as one; C's endpoint uniform over U ⊆ S (16 endpoints) | valid relaxation, unpriced | P62 |
| 6 | C6: drop one C qubit (W_i = S + e_i), 6-CX C6 encoder | frees one cell on an area-bound grid; unpriced | P62 |
| 7 | A as 3 direct Z checks or a 4-qubit GHZ meter | reviewer measured +28% grid-free standalone | parked: only with a layout that uses the freed cells |
| 8 | Move data during the prefix (time-indexed placement) | outside HOPS/FREELAY's bounded models | parked (placement lane) |
| 9 | Live data as a 4-CX bridge (CX a→b through h) | identity correct; adds correlated data errors | parked |
| 10 | B/C boundary cache (2^11 classes) to price preps fast | accelerator for 4–6 | P62 |

## Reviewer 4 review (2026-10-24 21:10, on commit 57e99b9; bundle in `work/lanes/MAIN/spec/reviewer4/`)
| # | Claim | Check | Item |
|---|---|---|---|
| 1 | Measured-helper remote CX (CX B→h, CX h→C, MX h = Z_B^m CX(B,C)); pipelined B→h at R, h→C at R+1 lets C finish 2 ticks later; +1.18e-6 at R34 grid-relaxed | identity standard; obstruction re-checked (FINDINGS) | geometry lanes (ENDSTATE, FRESH, ST1) at their next turn |
| 2 | Moving check (CX A→D, CX D→A, MZ D; output on A), 128 masks | identity plausible; adds a round CX on the output path, where the round's data-side loss sits (ARCH) | price only inside a placement model that saves R |
| 3 | Dirty bus UVUV: 2×2 remote CX in 8 CX through one helper | identity standard; helper faults correlate outputs | B/C prep synthesis (BCPOL/FRESH) |
| 4 | Encoded-Bell B/C endpoint, B = \|b_L⟩ with FRAME_X from C's parity | FRAME_X with record bits is legal (P l.161) | BCPOL endpoint family |
| 5 | Measured partial uncompute in the phase network (7 CX → 4 CX + 2 MX toy; 14 of 15 axes unsafe alone) | unpriced | parked (prefix length) |
| 6 | Selective Z protection of waiting data (Fano line) | targets v30f's wait-driven cubic term | P74 |
| 7 | Allow c1 ≠ 0 under a budget | one harmful 2q Pauli costs ≥ p/15 × 1/2 = 3.3e-5, above the whole non-round loss; no gain possible | rejected |
| 8 | Exact rational timing L(z) = P4/Q4 per CX shift | refinement of ST1's exact timing loop | COMP29/ST2 timing |
| 9 | Sparse Walsh + detector basis change: v29c all-orders 6.34391e-5 in 28 s (v23: 261 s → 19 s) | **reproduced exactly**; adopted as `work/lanes/MAIN/sparse/sparse_walsh.py` (AGENTS ranking); v30f 5.89377e-5 | done |
| 10 | Graph-resource + measurement-branch synthesis | no legal witness yet | parked |

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us
  either way.
