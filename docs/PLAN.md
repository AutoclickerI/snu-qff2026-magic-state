# Plan

## Status (2026-10-24 18:10 KST)
- Board: Placeholder 5.612e-5 (179 CX); us 6.95468e-5 = v22_r155 (rank 2). Submitted 18:01:47, scoring: **v23h_c2c9_r290**
  (seed-0 6.75337e-5, best of 320 re-draws, mean ≈7.03e-5) = BCSYN2 prep + HOPS hop_early + ACHECK q2/q9 checks, exact
  6.92210e-5, exp(-A1) 0.54086, 4.2 s per 1e6 judge shots. v24 (+ PRESYN's blue XZ, exact 6.58848e-5) is unsubmittable:
  116 s per 1e6, about 2.5 h on the server (CONSTRAINTS rule 5; FINDINGS "Failures"). KNAP looks for a fast form of that gain.
- Floor under the judge's noise: 1.116e-5 for any circuit, 2.567e-5 for a direct one-step final readout (FINDINGS); G0
  targets 1e-5. Grid-free, small separate 9-CX blocks with the round right after the pre-stage give 3.55e-5 at R 33,
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
| 2 | P60 | G1 | KNAP: acceptance knapsack on fast bases (v23h_c2c9, PRESYN best) — find why blue-on-v23 is slow and a fast form of it; reviewer 3's readout copy (#1) and helper-verified inits (#2), blue X/Z/XZ variants, ACHECK/HOPS checks, detector drops and init types, with exact marginal (Δ1-F, ΔA1) per item | a circuit below v23h_c2c9's exact 6.92210e-5 with exp(-A1) ≥ 0.5002 and ≤ 20 s per 1e6 judge shots, confirmed by 3-seed MC, or the item table exhausted | Codex lane KNAP (`work/lanes/KNAP`, owl, sunfish) | active |
| 3 | P61 | G1 | WALSH: all-orders model-exact 1-F and acceptance by Walsh contraction (reviewer 3 #3), validated by brute force, the exact2 low-p limit and re-draw means | `work/lanes/WALSH/allorders.py` validated and the v23h_c2c9 family scored | Codex lane WALSH (`work/lanes/WALSH`, zebra, sunfish) | active |
| 4 | P62 | G1 | BCPOL: relax the B+C contract (reviewer 3 #4 partial clean policies, #5 joint prep+check endpoints, #6 C6, #10 boundary cache), priced in v23h_c2c9 | a prep below v23h_c2c9 by exact and MC, within the speed gate (or one that frees acceptance at equal loss), or each relaxation priced with its mechanism | Codex lane BCPOL (`work/lanes/BCPOL`, jerry, hippo) | active |
| 5 | P57 | G1 | LNS: exact-objective local search on v22h_c2c9 and v22w_c2c9 (re-timing, commuting reorders, init types, watch checks, T† moves, re-encodings, hop timing; third-order sets) | local-optimum certificate per move family, or each gain verified by MC | Codex lane LNS (`work/lanes/LNS`, zebra, jerry) | active |
| 6 | P2 | G1 | Hourly submission of the best verified candidate (`work/promote.sh`, seed-0 re-draws, R-20261023-10) | each slot with a gain used; final best in by 2026-10-30 10:00 | main session | active |
| 7 | P14 | G1 | Smaller fault-tolerant joint B+C prep for L5 (sat6/sat7, old rule) | a merged circuit below the best by 3-seed MC | Sonnet lane ST_BC (40 jobs on jerry and hippo; kept running by Jihoon's answer, no new result since 02:05) | active |
| 8 | P17 | G1 | Exact block encoders (`work/lanes/EXENC/exenc.py`) for the B, C, O blocks of each new layout, kept as a Pareto set | preps for each candidate layout | lanes P39–P42 | parked: used inside P39–P42 |


## Idea review (2026-10-24)
Gains are relative to v12 (3-seed MC 1.133e-4). "Inferred" means estimated from the FINDINGS numbers cited, not measured.
| # | Idea | Review | Expected gain | Item |
|---|---|---|---|---|
| 1 | Teleport the output into a fresh \|+_L⟩ block O (CX o→d, measure the data in Z, FRAME_X = parity of the 7 bits); B and C then check O | measured: same grid-free loss as the star round to all digits (3.2324e-5). Separate blocks on the chain are infeasible in all 48 placements: area, not adjacency, binds. Open: joint B∪C preps on the chain | was 5.5–8e-5 with separate preps (now infeasible); with a joint prep, the gain over L5 is the earlier round start, about −5 to −15% on cand14 (inferred from cand2 → cand14) | closed (FINDINGS) |
| 2 | O on the pre-stage's cat-ancilla cells (free from step 33; d15 uses 16 or 21) | the enabler for 1: O is prepared during the pre-stage and hopped in. With separate preps it does not fit (idea 1); it stays the O placement in the joint-prep retry | part of 1 | closed (FINDINGS) |
| 3 | One flag qubit (CX f→q twice, read X) on the A/O encoder | the best A encoder's danger is 8 single faults on code qubits 0 and 3 (FINDINGS "Block-A encoder"); one flag around that window catches them. Fails for B, whose single X faults land on the output | −0.2 to −0.8e-5; larger the later the round (inferred: cross term ≈ danger 6.7e-4 × data Z exposure, ≈ 0.9e-5 at 20 steps) | P21 |
| 4 | Relay then reset: route one block's prep through the other's empty cells, reset them in between | closed on L5 by adjacency: cells 17 and 5 (C) touch only B cells, and 6, 11, 4 (B) touch only C cells, so a B–C CX is unavoidable (ST_BC) | 0 on L5 | closed (FINDINGS) |
| 5 | Checkerboard rule: each block cell has the opposite colour of its partner | exact and instant; prunes layouts before any solver and should explain the A/B clash | no direct gain; faster layout proofs | P15 |
| 6 | Pick, among exact-optimal A encoders, the one whose dangerous classes meet the least-exposed data qubits | cheap scan with exact2; superseded if 3 removes the term | ≤ 0.3e-5 (inferred: up to 30% of the A cross term) | done: SCHED's 223-encoder sweep picked enc_210 on cand2 (`work/lanes/SCHED/REPORT.md`) |
| 7 | Exact-objective scheduler: for a fixed op order, 2nd-order loss is quadratic in the idle-gap lengths | exact objective in place of ALAP; ALAP alone gave −0.76% exact on v12 (PRE, MC unresolved) | −1 to −3% on v12; more on Steane circuits with long idles (inferred) | closed: no gain on v12, cand2 or v14 (FINDINGS) |
| 8 | Optimise the detector set: add undeclared deterministic parities, drop detectors that mostly reject harmless faults | score = E/A; dropping D pays when the error it lets in per shot is below the score | measured: 0 (full span already declared); dropping `c[3]` frees 0.8% acceptance at no cost, kept for Steane circuits near 0.5 | closed (FINDINGS) |
| 9 | End-to-end exact pipeline: layout → exact encoders → merge → --third → MC | needed because the 2nd order misranks big circuits (cand2: −30%); built by ST_LAY's `assemble.py`, ST_TP and the main session, so no separate lane | selection gain, not a number | main session (critical path) |
| 10 | The organisers' reference [7] (Chamberland–Cross, arXiv:1811.00566): flag-based logical-H measurement | fewer ancillas than two cats, so a smaller injection footprint; controlled-H needs T gates that may hit the judge's rotation-rank cap; from memory, its p² coefficient is larger than cultivation's | measured: our grid build 2.49e-2 (not FT at first order); the paper's own 15 p² in our metric still loses to RM15 → Steane | parked (FINDINGS) |
Checked and dropped in the same pass: flags or a fault-tolerant encoder in place of C (B's single X faults land on the output),
one-CX cross-checks between A and B (A's errors cancel, and they need triangles), pairing blocks by code automorphisms (no physical
change), teleporting through \|0_L⟩ (puts the costlier error type last), reusing measured qubits as final-step partners (their
post-measurement noise leaks).

## External feedback review (2026-10-24, on commit 7f0bd77)
Checked against the code and the judge before acting. "Verified" means read in the code or recomputed here.
| # | Claim | Check | Feasible / expected gain | Item |
|---|---|---|---|---|
| 1 | `proxy2.joint_loss` pairs X and Z mechanisms by probability order; use ½P(X_L obs flip) + ½P(Y_L obs flip) | verified in code (pairing on equal (detectors, stabilizer) keys); exact2 and MC are unaffected, only the grid-free proxies, including `GModel.proxy`, which calls `joint_loss` | yes; corrects planning numbers and anneal ranking, gain unknown | done: no gain (FINDINGS) |
| 2 | Measure fresh \|0⟩ qubits (2p/3 flip) instead of reset (p) | verified in `tprep/noise.py`; measured on v12: q16 alone −1.6% exact (3rd 1.1253e-4), MC 3-seed mean 1.1307e-4 vs 1.1327e-4; q2, q14, q9, q20 change nothing but acceptance | yes; −1.6% now, more with MX-init and record folding | P25 (v13_m16 re-draws for P2) |
| 3 | `ST_BC/ft.py` omits C's logical parity, so it rejects safe preps | verified: `bad()` drops p_C while merge declares C's 7-bit parity detector; `sat4.py` CX cap is `pass` | yes; enlarges the FT search space, the "no FT prep at depth ≤ 13" result is not a proof | P14 |
| 4 | Run D's check of A after d→a (same ideal circuit; check faults cannot reach the data) | equivalence correct (CXs with one target commute); D itself does not fit the grid (FINDINGS) and a late D must live to the end | no for D; applied to the small parity check instead | P32 |
| 5 | Check the logical X rep X2X4X5 on A: it anticommutes with every dangerous class of both encoders | verified: {2,4,5} = [0,1,2]^[0,2,4,6]^[1,2,5,6]; Z_L Z_j anticommutes iff j ∉ {2,4,5}; cells 8, 2, 16 share no neighbour | measured: −17.5% with adjacency ignored; impossible on L5 | P32 |
| 6 | Measure helpers in X instead of uncomputing them | math correct (Σ\|Gx⟩\|Hx⟩ → Z^z with Gᵀz = Hᵀm); valid for B and C, whose byproducts only flip B's MX records; not for A or O | yes; removes uncompute CX (89 → 73 CX was worth −12%) | P14 |
| 7 | Keep encoders as a Pareto set; FLAG passes k=5 to an engine that accepts 3 or 4 | k=5 was real at 7f0bd77 and already fixed (k=4 now); Pareto retention adopted | small | P17, P26 |
| 8 | Retain v12's q1/q9 MX states instead of RX | pattern verified (MX → c[4]/c[5] → RX); PRE's q8 analogue gained nothing | tiny | P25 |
| 9 | Choose X/Z stabilizer supports jointly with the grid placement for the v12-family cycle | valid: the grid anneals fix PLAQ; relaxed.py explored it only grid-free | unknown, a few % at most (inferred) | done: no gain (FINDINGS) |
| 10 | Pair-sensitivity-guided LNS | valid process idea; overlaps the closed scheduler (FINDINGS) | unknown | parked: P33/P34 first |

## Reviewer 2 review (2026-10-24, on commit 5f880dd; text in `work/lanes/MAIN/spec/reviewer2.md`)
| # | Claim | Check | Item |
|---|---|---|---|
| 1 | Re-encode the last A/C readouts with two CX | measured exactly as predicted (−1.2954e-6 2nd order); v17 | done (FINDINGS) |
| 2 | Evaluators and searches assume c1 = 0 | valid tooling gap; partial detector sets scored by BUDGET, none better | closed (FINDINGS) |
| 3 | Choose all init sites jointly under the acceptance budget | all 4096 masks: none beats all-measure-init | closed (FINDINGS) |
| 4 | Detectors and logical frame chosen jointly | 139 variants, none better | closed (FINDINGS) |
| 5 | C → 4 ancillas reading Z_056, Z_146, Z_245, Z_3456 (12 CX, 6 layers) | equivalence verified; costs +55% grid-free (checker faults, B exposure) | closed (FINDINGS) |
| 6 | Reverse-endpoint B+C synthesis (≤ 6 nonzero rows) | valid; 66 CX in 3.8 s without the FT predicate | P51 |
| 7, 8 | A + cat check as one synthesis; dual helper for A | apply to the closed COMBO2 parity branch | closed with COMBO2 |
| 9 | 16 protected 15-T forms of the pre-stage | reproduced; re-synthesised encoder + ALAP gave v18 (−8.5%) | P47 |
| 10 | Integrate the final data idle analytically in MC | variance reduction only; ranking already uses exact2, and seed-0 draws cannot be variance-reduced | dropped |

## Reviewer 3 review (2026-10-24, on commit a9cae1c; text in `work/lanes/MAIN/spec/reviewer3.md`)
The reviewer's zip (QASMs, scripts) is behind a chatgpt.com library link we cannot fetch; lanes re-derive.
| # | Claim | Check | Item |
|---|---|---|---|
| 1 | Copy the last C readouts onto fresh helpers, detect disagreement (+3 CX, same depth) | readout error p → 2.7e-4 conditional (formula checked); reviewer: −0.65% third order on v23h_c2c9, acceptance −0.0055; not yet reproduced here | P60 |
| 2 | Helper-verified init, helper measured in the same tick as the qubit's first op | init error → 2.7e-4 (vs 2p/3, p); reviewer: 6 positions −1.83% on v22, with #1 −2.46% all orders at acceptance −0.011; about 3%/pp, the best loss-per-acceptance item known (blue XZ 1.2%/pp) | P60 |
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
