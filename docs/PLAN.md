# Plan

## Status (2026-10-24 02:25 KST)
- Board: Placeholder 7.604e-5 (161 CX, acc 0.590); us 1.127e-4 (v12, 3-seed MC mean 1.133e-4).
- Steane-type final round (FINDINGS): 3.23e-5 grid-free at 2nd order. On the grid only L5 with a joint fault-tolerant
  B+C prep works so far: 89 CX at round step 53 gives MC 1.31e-4, 73 CX at step 51 (`cand14`) gives MC 1.153e-4, 1.8%
  short of v12. Separate block preps do not fit the board (ST_TP: chain infeasible in all 48 placements, area-bound), so
  the levers now are a smaller joint prep (P14), joint preps on the chain (P20), and scheduling, detectors and flags on
  `cand14` (P21–P23).

## Critical path
edit (minutes) → `lanes/EVAL/exact2.py <qasm> --third` (30 s; the 2nd order alone is 2% low on v12 and 30% low on
big Steane circuits) → 1e8-shot MC at seeds 0/1000/2000 (about 1 min on hippo) → sequential judge (2 min) → submit
(hourly, about 2 min to score). Bottleneck: the joint B+C prep's size and its late round start (P14, P20).

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P14 | G1 | Smaller fault-tolerant joint B+C prep for L5 (`sat4.py` CEGAR at depths 12–15, plus a CX-count cap of 65/60/55) | a merged circuit below v12 by 3-seed MC | Sonnet lane ST_BC (`work/lanes/ST_BC`; jerry 12 jobs, hippo 10, logs `log5_*`) | active |
| 2 | P20 | G1 | Teleport-output round (ideas 1, 2) with joint B∪C (or O∪B) preps: separate blocks proved infeasible in all 48 placements | layout with T < 51, full circuit scored by --third and MC | Sonnet lane ST_TP (`work/lanes/ST_TP`, owl, sunfish) | active |
| 3 | P15 | G1 | Star round co-placed with the pre-stage: ~48 symmetry/translation placements, staged blocks with one-hop moves, optional block D; checkerboard pruning (idea 5) | per placement: feasible, R, --third score of the winners (c1 = 0) | Sonnet lane ST_LAY (`work/lanes/ST_LAY`) | parked: P20 (staged star gives R ≈ 46 with 20/32-CX B/C preps, FINDINGS; time-aware data routes, placements and colour pruning not run) |
| 4 | P21 | G1 | One or two flag qubits on the A/O encoder (idea 3) | Pareto table of flagged danger vs depth, Stim-checked | Codex lane FLAG (`work/lanes/FLAG`) | active |
| 5 | P18 | G1 | Block D (\|+_L⟩) checking A's Z errors before A couples | proxy with and without D, layout, --third score | Sonnet lane ST_AV (`work/lanes/ST_AV`, owl) | active |
| 6 | P22 | G1 | Exact-objective scheduler (idea 7) and encoder choice by full-circuit score (idea 6), on v12 and cand2 (then cand14) | scheduled circuits with --third and 3-seed MC | Codex lane SCHED (`work/lanes/SCHED`, zebra, sunfish) | active |
| 7 | P24 | G1 | Chamberland–Cross flag-based injection (idea 10) as a full circuit or a smaller pre-stage | judge-valid grid circuit, scores, verdict | Codex lane CC (`work/lanes/CC`, jerry) | active |
| 9 | P17 | G1 | Exact block encoders (`work/lanes/EXENC/exenc.py`) for the B, C, O blocks of each new layout | preps for each candidate layout | main session | parked: P20/P15 layouts |
| 10 | P16 | G1 | Integrate, rank by --third then MC (idea 9), submit the best verified candidate | official 3-seed mean below 7.6e-5 | main session | parked: P20/P15 |
| 11 | P2 | G1 | Hourly submission of the best verified candidate (seed-0 re-draws, R-20261023-10) | each slot with a gain used; each new best submitted at once (ties go to fewer 2q gates, then the earlier entry); final best in by 2026-10-30 10:00 | main session | active |

## Idea review (2026-10-24)
Gains are relative to v12 (3-seed MC 1.133e-4). "Inferred" means estimated from the FINDINGS numbers cited, not measured.
| # | Idea | Review | Expected gain | Item |
|---|---|---|---|---|
| 1 | Teleport the output into a fresh \|+_L⟩ block O (CX o→d, measure the data in Z, FRAME_X = parity of the 7 bits); B and C then check O | measured: same grid-free loss as the star round to all digits (3.2324e-5). Separate blocks on the chain are infeasible in all 48 placements: area, not adjacency, binds. Open: joint B∪C preps on the chain | was 5.5–8e-5 with separate preps (now infeasible); with a joint prep, the gain over L5 is the earlier round start, about −5 to −15% on cand14 (inferred from cand2 → cand14) | P20 |
| 2 | O on the pre-stage's cat-ancilla cells (free from step 33; d15 uses 16 or 21) | the enabler for 1: O is prepared during the pre-stage and hopped in. With separate preps it does not fit (idea 1); it stays the O placement in the joint-prep retry | part of 1 | P20 |
| 3 | One flag qubit (CX f→q twice, read X) on the A/O encoder | the best A encoder's danger is 8 single faults on code qubits 0 and 3 (FINDINGS "Block-A encoder"); one flag around that window catches them. Fails for B, whose single X faults land on the output | −0.2 to −0.8e-5; larger the later the round (inferred: cross term ≈ danger 6.7e-4 × data Z exposure, ≈ 0.9e-5 at 20 steps) | P21 |
| 4 | Relay then reset: route one block's prep through the other's empty cells, reset them in between | closed on L5 by adjacency: cells 17 and 5 (C) touch only B cells, and 6, 11, 4 (B) touch only C cells, so a B–C CX is unavoidable (ST_BC) | 0 on L5; moot once 1 gives separate preps | closed (FINDINGS) |
| 5 | Checkerboard rule: each block cell has the opposite colour of its partner | exact and instant; prunes layouts before any solver and should explain the A/B clash | no direct gain; faster layout proofs | P15 |
| 6 | Pick, among exact-optimal A encoders, the one whose dangerous classes meet the least-exposed data qubits | cheap scan with exact2; superseded if 3 removes the term | ≤ 0.3e-5 (inferred: up to 30% of the A cross term) | P22 |
| 7 | Exact-objective scheduler: for a fixed op order, 2nd-order loss is quadratic in the idle-gap lengths | exact objective in place of ALAP; ALAP alone gave −0.76% exact on v12 (PRE, MC unresolved) | −1 to −3% on v12; more on Steane circuits with long idles (inferred) | P22 |
| 8 | Optimise the detector set: add undeclared deterministic parities, drop detectors that mostly reject harmless faults | score = E/A; dropping D pays when the error it lets in per shot is below the score | measured: 0 (full span already declared); dropping `c[3]` frees 0.8% acceptance at no cost, kept for Steane circuits near 0.5 | closed (FINDINGS) |
| 9 | End-to-end exact pipeline: layout → exact encoders → merge → --third → MC | needed because the 2nd order misranks big circuits (cand2: −30%); built by ST_LAY's `assemble.py`, ST_TP and the main session, so no separate lane | selection gain, not a number | P16 |
| 10 | The organisers' reference [7] (Chamberland–Cross, arXiv:1811.00566): flag-based logical-H measurement | fewer ancillas than two cats, so a smaller injection footprint; controlled-H needs T gates that may hit the judge's rotation-rank cap; from memory, its p² coefficient is larger than cultivation's | unknown: likely none as a full circuit, possible as a smaller pre-stage | P24 |
Checked and dropped in the same pass: flags or a fault-tolerant encoder in place of C (B's single X faults land on the output),
one-CX cross-checks between A and B (A's errors cancel, and they need triangles), pairing blocks by code automorphisms (no physical
change), teleporting through \|0_L⟩ (puts the costlier error type last), reusing measured qubits as final-step partners (their
post-measurement noise leaks).

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us
  either way.
