# Plan

## Status (2026-10-24 18:45 KST)
- Board: Placeholder 5.335e-5 (187 CX); us 6.75337e-5 = v23h_c2c9_r290 (rank 2); v25k_r262 (seed-0 6.32297e-5, 300 re-draws mean
  6.5912e-5) submitted 19:36, scoring; v27x (ST2's exchange4, MC mean 6.4768e-5) in re-draws for 20:37. In re-draws for the next slot: **v25k** = KNAP's `final_m04_l2` (v23h_c2c9 + blue XZ + q19 reset+H +
  timing/check pack), exact 6.50501e-5, MC mean 6.6015e-5, acceptance 0.5106, 4.3 s per 1e6.
- Loss ledger (FINDINGS): of v23h_c2c9's 6.92e-5, the round alone is 2.87e-5 (its floor class) and ≈ 4e-5 is cross-region
  (prefix/wait residual + one later fault); the grid-free early round is 3.55e-5. LADDER: at fixed R45, separate small B and C
  encoders alone would give 5.71e-5 and with a standard A 5.03e-5 (adjacency ignored); ST1 and ST2 target their grid realization first.
- Floors (FINDINGS): any circuit ≥ 1.162e-5 in expectation (proved), a direct one-step final readout ≥ 2.567e-5; G0's 1e-5 is out of reach, so the gap is the measure. Grid-free, small separate 9-CX blocks with the round right after the pre-stage give 3.55e-5 at R 33,
  4.12e-5 at R 39, 5.79e-5 at R 50; the round itself is 3.14e-5 of that (FINDINGS).
- Every grid layout so far hits the area wall: separate unitary B and C encoders do not fit next to the data early
  (R0, LAYOUT3, TP2, R1, REVSAT, FREELAY), so the 82-CX joint B+C prep stays; BCSYN2's feedback search found a better 82-CX prep
  (−2.9%); BCFB continues it, BCPOL relaxes its contract; MBP's measurement-based preps and SEP2T's separate
  blocks did not help (FINDINGS). Closed today: ARCH, REVSAT, EARLYBC, ANC4, R1, PRE3, BUDGET, TREP2, ACHECK, HOPS, SEP2T, BCSYN2, PRESYN, MBP (FINDINGS).

## Critical path
edit (minutes) → `lanes/EVAL/exact2.py <qasm> --third` (30 s) and `lanes/MAIN/ablate.py --pairs` (1 min) → 1e8-shot MC at
seeds 0/1000/2000 → `work/promote.sh` (re-draws over hosts ≈ 10 min, sequential judge, commit, submit at the next slot).
Bottleneck: the B+C prep footprint (82 CX; noiseless −26.5% on v19) and the data's waiting exposure before the round
(cells 10 and 0 idle 13 steps against late A-encoder faults).

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P59 | G1 | BCFB: continue BCSYN2's exact-loss feedback search for clean 82-CX B+C preps, priced inside v23h_c2c9 (depth 14–15, MX/measure-init on any B/C cell, prep timing vs hops and A, automorphisms) | a prep below v23h_c2c9's exact 6.92210e-5 confirmed by 3-seed MC, or the feedback loop converged | Codex lane BCFB (`work/lanes/BCFB`, tom, owl) | active |
| 2 | P60 | G1 | KNAP: acceptance knapsack on fast bases (v23h_c2c9, PRESYN best) — find why blue-on-v23 is slow and a fast form of it; reviewer 3's readout copy (#1) and helper-verified inits (#2), blue X/Z/XZ variants, ACHECK/HOPS checks, detector drops and init types, with exact marginal (Δ1-F, ΔA1) per item | a circuit below v23h_c2c9's exact 6.92210e-5 with exp(-A1) ≥ 0.5002 and ≤ 20 s per 1e6 judge shots, confirmed by 3-seed MC, or the item table exhausted | Codex lane KNAP (`work/lanes/KNAP`) | done: `final_m04_l2` = v25k (FINDINGS) |
| 3 | P61 | G1 | WALSH: all-orders model-exact 1-F and acceptance by Walsh contraction (reviewer 3 #3), validated by brute force, the exact2 low-p limit and re-draw means | `work/lanes/WALSH/allorders.py` validated and the v23h_c2c9 family scored | Codex lane WALSH (`work/lanes/WALSH`, zebra, sunfish) | active |
| 4 | P62 | G1 | BCPOL: relax the B+C contract (reviewer 3 #4 partial clean policies, #5 joint prep+check endpoints, #6 C6, #10 boundary cache), priced in v23h_c2c9 | a prep below v23h_c2c9 by exact and MC, within the speed gate (or one that frees acceptance at equal loss), or each relaxation priced with its mechanism | Codex lane BCPOL (`work/lanes/BCPOL`, jerry, hippo) | active |
| 5 | P57 | G1 | LNS: exact-objective local search on v22h_c2c9 and v22w_c2c9 (re-timing, commuting reorders, init types, watch checks, T† moves, re-encodings, hop timing; third-order sets) | local-optimum certificate per move family, or each gain verified by MC | Codex lane LNS (`work/lanes/LNS`) | stopped 19:30: superseded by LNS2 on v25k; best 6.758e-5 exact on the v22 family |
| 6 | P63 | G1 | GAP: a structurally different circuit at the leader's scale (5.612e-5 at 179 CX vs our 215): CX/depth budget by region, grid-free pricing of new architectures (smaller pre-stage footprint, no hops, fewer block cells, checks spread over the wait), grid builds of the best | a built circuit below v23h_c2c9 by exact and MC within the speed gate, or each architecture priced with its mechanism | Codex lane GAP (`work/lanes/GAP`) | done: nothing below 5.6e-5; dynamic routing not searched (FINDINGS) |
| 7 | P64 | G3 | LADDER: matched one-change-at-a-time pricing from v23h_c2c9 to the grid-free early round (joint B+C prep → separate encoders, A encoder, hops, R, prefix), both orders | each grid constraint's share of the 6.92e-5 − 3.55e-5 gap measured | Codex lane LADDER (`work/lanes/LADDER`) | done: B+C package 36% of the gap, A 20%, timing 39% (FINDINGS) |
| 8 | P65 | G2 | BIRD: independent bird's-eye review of floors, loss ledger, locked-in decisions and missing optimization methods, from the repo only | REPORT.md with ranked methods and first experiments | Codex lane BIRD (`work/lanes/BIRD`) | done: FINDINGS "Independent review" |
| 9 | P66 | G1 | ST1: joint dynamic placement and instrument synthesis across the prefix-to-round boundary (BIRD's top direction) by solver loops: data wires moved during the prefix with retargeted CXs, early ancilla release, joint A/B/C/C6 roles, 1-CX block teleports, exact third-order scoring with pair/triple feedback | a judge-valid circuit below 4.8e-5 exact (or below v25k), or each family closed by mechanism | Codex lane ST1 (`work/lanes/ST1`, owl, zebra) | active |
| 10 | P67 | G1 | ST2: the same goal by population search over macro rewrites (window re-placement, role swaps, prep witnesses, checks, init types) with validity repair and a loss/acceptance/runtime/diversity Pareto front | as P66 | Codex lane ST2 (`work/lanes/ST2`, sunfish, zebra, tom) | active |
| 11 | P68 | G1 | LNS2: LNS move families and a correct reviewer #1 port on v25k | v25k's local optimum certified per move family, gains MC-verified | Codex lane LNS2 (`work/lanes/LNS2`) | done: v26n (FINDINGS), in re-draws |
| 12 | P69 | G1 | SEPBC: grid realization of LADDER's separate small B and C (and standard A) at R≈45: compact preps in the 21 cells free during the prefix, 1-CX teleports into final cells, C checks B right before coupling; or new final roles; then the blue check | a grid circuit below v25k (target ≈ 5.0–5.7e-5 before the blue check) | Codex lane SEPBC (`work/lanes/SEPBC`, tom, zebra) | active |
| 13 | P70 | G2 | XTIM: the exact trigger of xtim's per-shot slow path (q19 MX init, q8 MX reuse, blue-on-v23), a fast speed predictor, and physics-preserving rewrites that avoid it (q8's −1.2% on v26n) | rule + validated `work/lanes/XTIM/speed_predict.py` | Codex lane XTIM (`work/lanes/XTIM`, zebra) | active |
| 14 | P2 | G1 | Hourly submission of the best verified candidate (`work/promote.sh`, seed-0 re-draws, R-20261023-10) | each slot with a gain used; final best in by 2026-10-30 10:00 | main session | active |
| 15 | P14 | G1 | Smaller fault-tolerant joint B+C prep for L5 (sat6/sat7, old rule) | a merged circuit below the best by 3-seed MC | Sonnet lane ST_BC (40 jobs on jerry and hippo; kept running by Jihoon's answer, no new result since 02:05) | active |
| 16 | P17 | G1 | Exact block encoders (`work/lanes/EXENC/exenc.py`) for the B, C, O blocks of each new layout, kept as a Pareto set | preps for each candidate layout | lanes P39–P42 | parked: used inside P39–P42 |


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
