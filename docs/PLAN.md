# Plan

## Status (2026-10-24 20:25 KST)
- Board: Placeholder 5.166e-5 (195 CX); us 6.32297e-5 = v25k_r262 (rank 2). v26n_r115 (seed-0 6.18621e-5; 120 re-draws
  mean 6.5202e-5) goes in at 20:37. v30f (FRESH's correlated rank-3 B/C, 189 CX, 3-seed mean 5.8944e-5, acceptance 0.5275)
  is the new base and in re-draws for 21:37 (v29c's 189 draws: mean 6.3468e-5, min 6.11141e-5, superseded).
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
| 1 | P71 | G1 | ENDSTATE: encoder library and end-state witness done (FINDINGS); now time-indexed prefix-compatible end-states (prefix symmetries, preps on cells free at that time, just in time), earliest R then least exposure, complete circuits priced | complete circuits with loss split; below 5e-5 or the mechanism that stops it | Codex lane ENDSTATE (`work/lanes/ENDSTATE`, zebra) | active |
| 2 | P66 | G1 | ST1: prefix/round co-design from scratch: prefix embedding (48) or re-synthesized cat layout, ENDSTATE end-states, data hops out of the prefix, just-in-time compact block preps, teleports, earliest R; full builds with exact feedback | a grid circuit below 5.0e-5 exact, then lower | Codex lane ST1 (`work/lanes/ST1`, owl, zebra) | active |
| 3 | P72 | G1 | FRESH: delivered v30f (correlated rank-3 B/C); now an earlier round (R ≤ 40) with that resource prepared during the prefix, no unchecked B wait | a verified grid circuit below 5e-5 true, or designs closed by mechanism | Codex lane FRESH (`work/lanes/FRESH`, zebra, sunfish) | active |
| 4 | P69 | G1 | SEPBC: delivered v28s; stationary separate B/C proved impossible (FINDINGS). Now (a) its free q5 detector on v29c, (b) the reusable emitter that attaches ENDSTATE end-states to the real prefix, priced with a loss split | (a) priced; (b) every ENDSTATE end-state priced | Codex lane SEPBC (`work/lanes/SEPBC`, tom, zebra) | active |
| 6 | P67 | G1 | ST2: macro-rewrite population search on v30f (init/check forms, commuting schedule, transfer phase, readout edge, timing, idle-slot detectors), seeded with COMP29's finalists | a v30f-lineage finalist below COMP29's best by 3-seed mean | Codex lane ST2 (`work/lanes/ST2`, zebra, sunfish, tom) | active |
| 5 | P73 | G1 | COMP29: port the v23h→v29c local edits (blue XZ check, exchange, instrument, readout copy, LNS2/ST2 edits, timing feedback, known-zero detectors) onto v30f and price every combination | a v30f-lineage finalist below v30f by 3-seed mean | Codex lane COMP29 (`work/lanes/COMP29`, jerry, owl) | active |
| 6 | P59 | G1 | BCFB: port its best clean B+C preps into v25k/v26n and re-run the exact feedback search in situ | a v25k-lineage circuit below v27x by re-draws | Codex lane BCFB (`work/lanes/BCFB`, owl) | active |
| 7 | P62 | G1 | BCPOL: B+C contract relaxations (partial clean, joint prep+check endpoints, C6, boundary cache), priced in v23h_c2c9 and v25k | each relaxation priced with its mechanism; C6 feeds ENDSTATE | Codex lane BCPOL (`work/lanes/BCPOL`, jerry, hippo) | active |
| 8 | P70 | G2 | XTIM: the trigger of xtim's per-shot slow path, a fast speed predictor, physics-preserving rewrites (q8's −1.2% on v26n) | rule + validated `work/lanes/XTIM/speed_predict.py` | Codex lane XTIM (`work/lanes/XTIM`, zebra) | active |
| 10 | P2 | G1 | Hourly submission of the best verified candidate (`work/promote.sh`, seed-0 re-draws, R-20261023-10) | each slot with a gain used; final best in by 2026-10-30 10:00 | main session | active |
| 11 | P14 | G1 | Smaller fault-tolerant joint B+C prep for L5 (sat6/sat7, old rule) | a merged circuit below the best by 3-seed MC | Sonnet lane ST_BC (kept running by Jihoon's answer, no new result since 02:05) | active |
Done today (FINDINGS): KNAP (v25k), LNS2 (v26n), LADDER, BIRD, GAP, XTIM, WALSH (`work/lanes/WALSH/allorders.py`), LNS (stopped), and the closed lanes listed there.

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

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us
  either way.
