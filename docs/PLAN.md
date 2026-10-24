# Plan

## Status (2026-10-24 20:00 KST)
- Board: Placeholder 5.166e-5 (195 CX, improving ~3%/h); us 6.32297e-5 = v25k_r262 (rank 2; 300 re-draws mean 6.5912e-5).
  v27x (ST2's exchange4, MC mean 6.4768e-5) in re-draws for 20:37.
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
| 1 | P71 | G1 | ENDSTATE: exhaustive SAT catalog of final geometries (D, A, B, C or C6; transversal adjacencies; grid-native preps ≤ 12–14 CX with helpers, MB preps, ≤ 1–2 moves per block qubit), data hop distance per prefix embedding, earliest R, calibrated loss | witness or certificate for small preps, ranked catalog with emitted fragments | Codex lane ENDSTATE (`work/lanes/ENDSTATE`, zebra) | active |
| 2 | P66 | G1 | ST1: prefix/round co-design from scratch: prefix embedding (48) or re-synthesized cat layout, ENDSTATE end-states, data hops out of the prefix, just-in-time compact block preps, teleports, earliest R; full builds with exact feedback | a grid circuit below 5.0e-5 exact, then lower | Codex lane ST1 (`work/lanes/ST1`, owl, zebra) | active |
| 3 | P72 | G1 | FRESH: independent from-scratch redesign team; every inherited choice open | a verified grid circuit below 5e-5 true, or designs closed by mechanism | Codex lane FRESH (`work/lanes/FRESH`, zebra, sunfish) | active |
| 4 | P69 | G1 | SEPBC: separate small B and C (and standard A) on the current lineage's cells at R≈45 via compact preps + teleports or new roles; then the blue check | a grid circuit below v25k (≈ 5.0–5.7e-5 before the blue check) | Codex lane SEPBC (`work/lanes/SEPBC`, tom, zebra) | active |
| 5 | P67 | G1 | ST2: composition of verified edits (exchange4, v26n's edits, BCFB/BCPOL preps) and population search on the v25k lineage; feeds the hourly slots until the redesign lands | compositions MC-verified | Codex lane ST2 (`work/lanes/ST2`, sunfish, zebra) | active |
| 6 | P59 | G1 | BCFB: port its best clean B+C preps into v25k/v26n and re-run the exact feedback search in situ | a v25k-lineage circuit below v27x by re-draws | Codex lane BCFB (`work/lanes/BCFB`, owl) | active |
| 7 | P62 | G1 | BCPOL: B+C contract relaxations (partial clean, joint prep+check endpoints, C6, boundary cache), priced in v23h_c2c9 and v25k | each relaxation priced with its mechanism; C6 feeds ENDSTATE | Codex lane BCPOL (`work/lanes/BCPOL`, jerry, hippo) | active |
| 8 | P70 | G2 | XTIM: the trigger of xtim's per-shot slow path, a fast speed predictor, physics-preserving rewrites (q8's −1.2% on v26n) | rule + validated `work/lanes/XTIM/speed_predict.py` | Codex lane XTIM (`work/lanes/XTIM`, zebra) | active |
| 9 | P61 | G2 | WALSH: all-orders evaluator with wider scope than the reviewer's (width > 23 for blue circuits) | validated `work/lanes/WALSH/allorders.py` | Codex lane WALSH (`work/lanes/WALSH`, zebra, sunfish) | active |
| 10 | P2 | G1 | Hourly submission of the best verified candidate (`work/promote.sh`, seed-0 re-draws, R-20261023-10) | each slot with a gain used; final best in by 2026-10-30 10:00 | main session | active |
| 11 | P14 | G1 | Smaller fault-tolerant joint B+C prep for L5 (sat6/sat7, old rule) | a merged circuit below the best by 3-seed MC | Sonnet lane ST_BC (kept running by Jihoon's answer, no new result since 02:05) | active |
Done today (FINDINGS): KNAP (v25k), LNS2 (v26n), LADDER, BIRD, GAP, LNS (stopped), and the closed lanes listed there.

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
| 3 | All-orders Walsh-contraction evaluator (~4 min) | reviewer's values match our re-draw means: v22 7.2365e-5 vs 7.2405±0.006e-5, v23h_c2c9 7.0262e-5 vs 7.0298±0.007e-5 | P61 |
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
