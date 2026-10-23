# Plan

## Status (2026-10-24 03:10 KST)
- Board (03:10): Placeholder 6.274e-5 (163 CX, acc 0.543); us 1.00638e-4 = v14 (server, bit-identical; 100-draw mean
  1.0382e-4), rank 2. Next slot 04:01.
- Floor under the judge's noise: 1.116e-5 for any circuit, 2.567e-5 for a direct one-step final readout (FINDINGS); G0
  targets 1e-5, so the gap is measured against that floor. v14's round alone costs 2.87e-5.
- v14 decomposition (FINDINGS): B+C prep noiseless −39.6%, data wait −28.8%, A −26.6%, pre-stage −18.4%. The joint
  B+C prep leaves single-fault X errors on B that C misses or sees at weight 1 (P33). The data idle 17 steps between
  the pre-stage and the round (P34). RM15 → Steane is closed on the grid (FINDINGS "Closed recipes").

## Critical path
edit (minutes) → `lanes/EVAL/exact2.py <qasm> --third` (30 s; the 2nd order alone is 2% low on v12 and 30% low on
big Steane circuits) and `lanes/MAIN/ablate.py --pairs` (1 min, region shares) → 1e8-shot MC at seeds 0/1000/2000
(about 1 min on hippo) → sequential judge (2 min) → submit (hourly, about 2 min to score). Bottleneck: a B+C prep whose
single faults leave B clean (P33) and a round that starts soon after the pre-stage (P34).

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P33 | G1 | Joint B+C prep under a stricter rule: no single fault leaves any X on B unseen by C, no single fault + one C readout flip leaves a dangerous X on B, then pairs (CEGAR copy of sat6/ft); else independent B/C encoders or a second verifier | 3-seed MC mean below v14's 1.0382e-4 (c1 not required), or per-rule solver negatives | Codex lane BC2 (`work/lanes/BC2`, jerry, owl) | active |
| 2 | P34 | G1 | Start the round soon after the pre-stage: release-aware B+C prep on L5, co-scheduled A and moves, and layouts with B+C in cells the pre-stage never uses (CP-SAT over pre-stage symmetries) | 3-seed MC mean below v14's 1.0382e-4 (c1 not required), or the smallest R per approach with receipts | Codex lane EARLY (`work/lanes/EARLY`, tom, sunfish) | active |
| 3 | P36 | G1 | Redesign the pre-stage (injection, encoding, logical check): decompose what each part buys in the full circuit, then compact variants that finish sooner, use fewer cells or leave the cells next to the data free | 3-seed MC mean below v14's 1.0382e-4, or measured negatives per variant | Codex lane PRE2 (`work/lanes/PRE2`, owl) | active |
| 4 | P32 | G1 | New Steane-round layout with free cells next to A for a late X_L parity check, joint FT B+C prep (sat6, CX cap), measurement-init | 3-seed MC mean below v14's 1.0382e-4 | Codex lane LAYOUT2 (`work/lanes/LAYOUT2`, owl, tom) | active; its brief wrongly requires negligible first order: lift that at its report |
| 5 | P30 | G1 | Literature table: every candidate protocol's reported error, acceptance, size, output-tail treatment and our-metric estimate | ranked top 3 with citations | Codex lane LIT (`work/lanes/LIT`) | active |
| 6 | P14 | G1 | Smaller fault-tolerant joint B+C prep for L5 (sat6/sat7 CEGAR at depths 12–15 with CX caps) | a merged circuit below v14 by 3-seed MC | Sonnet lane ST_BC (`work/lanes/ST_BC`; ~40 sat6/sat7 jobs on jerry and hippo, `auto.sh` + `minpipe.sh` score each; minpipe picks measure-init sites by 2nd order, a proxy) | active: best `cand_best_m` = v14 |
| 7 | P25 | G1 | Measurement-based preps: first-use measure + detector, MX-init with folded records, retained measurements (feedback 2, 8), on v12 and cand14 | variants with --third and 3-seed MC | Codex lane INIT (`work/lanes/INIT`, owl) | active |
| 8 | P2 | G1 | Hourly submission of the best verified candidate (seed-0 re-draws, R-20261023-10) | each slot with a gain used; each new best submitted at once (ties go to fewer 2q gates, then the earlier entry); final best in by 2026-10-30 10:00 | main session | active |
| 9 | P35 | G1 | Daguerre–Kim two-block RM15 → Steane switch (arXiv:2410.07327; source claim 25.5p² without idles vs Gao–Yuan–Yao's 183.81p²): reproduce, score grid-free under STANDARD, then a grid-native embedding if below ~6e-5 | grid-free 3-seed MC; grid circuit with 3-seed MC or the smallest grid CX reached | Codex lane DK (`work/lanes/DK`, zebra, hippo) | active |
| 10 | P15 | G1 | Star round co-placed with the pre-stage: ~48 symmetry/translation placements, staged blocks with one-hop moves, optional block D; checkerboard pruning (idea 5) | per placement: feasible, R, --third score of the winners (c1 = 0) | Sonnet lane ST_LAY (`work/lanes/ST_LAY`) | parked: P34 covers it with the B+C-in-parallel layouts (staged star gave R ≈ 46, FINDINGS) |
| 11 | P17 | G1 | Exact block encoders (`work/lanes/EXENC/exenc.py`) for the B, C, O blocks of each new layout, kept as a Pareto set over danger vector, depth and CX (feedback 7) | preps for each candidate layout | main session | parked: P34 layouts |
| 12 | P21 | G1 | One or two flag qubits on the A/O encoder (idea 3) | Pareto table of flagged danger vs depth, Stim-checked | Codex lane FLAG (`work/lanes/FLAG`) | parked: P32 (job ended without a report; scorer and candidates in the lane dir are unverified) |

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
