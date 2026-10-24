# Plan

## Status (2026-10-24 11:45 KST)
- Board (11:45): Placeholder 5.879e-5 (169 CX, acc 0.535); us 8.28792e-5 = v16 (server, bit-identical; BC2 clean B+C
  prep + measure-init; 245-draw mean 8.584e-5, exact 8.42e-5), rank 2. Re-draw means run ≈ 2% above exact 3rd order.
- Floor under the judge's noise: 1.116e-5 for any circuit, 2.567e-5 for a direct one-step final readout (FINDINGS); G0
  targets 1e-5. A round alone costs ≈ 2.87e-5 on our circuits.
- Measured levers (FINDINGS): clean B+C rule −18.4% (BC2), pre-stage kept (PRE2), earlier round −10.6% on L5 (EARLY,
  R 48), parity check on A −2.8% at R=54 (LAYOUT2), data wait ≈ −1.7 to −2% per step. DK and RM15 closed. Lanes now
  stack them: COMBO5 (L5), COMBO2 (parity layout), LAYOUT3 (B+C parallel to the pre-stage).

## Critical path
edit (minutes) → `lanes/EVAL/exact2.py <qasm> --third` (30 s) and `lanes/MAIN/ablate.py --pairs` (1 min) → 1e8-shot MC at
seeds 0/1000/2000 → `work/promote.sh` (re-draws over hosts ≈ 10 min, sequential judge, commit, submit at the next slot).
Bottleneck: the data wait before the round (R − 32 = 15–22 steps on every layout so far; LAYOUT3).

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P38 | G1 | Stack BC2's clean B+C rule with EARLY's release-aware merge on L5 (late cells in late layers, depths 13–15) + measure-init | 3-seed MC mean below 8.46431e-5 | Codex lane COMBO5 (`work/lanes/COMBO5`, zebra, sunfish) | active |
| 2 | P39 | G1 | Clean B+C rule on LAYOUT2's parity layout, earliest R, data-move variants, measure-init | 3-seed MC mean below 8.46431e-5 | Codex lane COMBO2 (`work/lanes/COMBO2`, owl) | active |
| 3 | P40 | G1 | New layouts with B+C prepared in parallel with the pre-stage (CP-SAT over pre-stage symmetries/translations), A in released cells, parity cat if it fits | 3-seed MC mean below 8.46431e-5, or the smallest R per approach | Codex lane LAYOUT3 (`work/lanes/LAYOUT3`, tom, hippo, jerry) | active |
| 4 | P2 | G1 | Hourly submission of the best verified candidate (`work/promote.sh`, seed-0 re-draws, R-20261023-10) | each slot with a gain used; final best in by 2026-10-30 10:00 | main session | active |
| 5 | P14 | G1 | Smaller fault-tolerant joint B+C prep for L5 (sat6/sat7, old rule) | a merged circuit below the best by 3-seed MC | Sonnet lane ST_BC (40 jobs on jerry and hippo; kept running by Jihoon's answer, no new result since 02:05) | active |
| 6 | P17 | G1 | Exact block encoders (`work/lanes/EXENC/exenc.py`) for the B, C, O blocks of each new layout, kept as a Pareto set | preps for each candidate layout | lanes P38–P40 | parked: used inside P38–P40 |
| 7 | P21 | G1 | One or two flag qubits on the A/O encoder (idea 3) | Pareto table of flagged danger vs depth, Stim-checked | — | parked: the parity check on A (LAYOUT2) covers A's danger where it fits |

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

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us
  either way.
