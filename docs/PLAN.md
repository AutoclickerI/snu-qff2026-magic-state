# Plan

## Status (2026-10-26 10:30 KST)
- Board: **rank 1** with v37f_h2609_r343039, **server 3.338e-5** (key 3.34e-5, 09:24); next team Placeholder 3.856e-5
  (unchanged since 2026-10-25 22:53). The hourly loop `work/receipts/draw_loop.sh` races seed-0 draws of the stem in
  `work/receipts/next_stem.txt` (read at HH:20) and submits the hour's best once the server's one-hour cooldown ends
  (now about HH:24), only if it beats the board key. v37f's six slots scored 3.338–3.376e-5 (SOTA).
- **Best expected circuit: v37h** (`work/lanes/MAIN/v37h`): **all-orders 3.611955e-5, acceptance 0.50155**, 406 CX,
  48 ticks: MERGE pass 4 on v37f (v37g 3.621124e-5) plus reviewer 17's q17 reset-then-herald and DETECTOR c[309]
  (−9.17e-8); races from the 11:20 race; judge time equal to v37g's, 1.17× v37f's. Round R45 on GLOBAL's R46 layout (data [6,20,19,10,2,22,16]). Since v36h (3.815473e-5):
  greedy bundles, R46 with both A-flag-gap helpers (v37a 3.761822e-5), POLISH (v37b), MERGE passes (v37c, v37d
  3.676347e-5), BC3 (v37e 3.637096e-5, v37f 3.630561e-5), MERGE pass 4 (v37g), reviewer 17 (v37h). Lane gains on a
  shared base compound.
- GLOBAL, EARLIER and MERGE were dead from 03:22 to 10:20 (zebra's disk filled; FINDINGS "Failures") and were resumed
  at 10:22; MERGE runs pass 5 on v37h on a fresh thread (`MERGE/BRIEF6.md`).
- Where the loss sits (FINDINGS): our terminal class floor 2.274e-5 is 61% of the total; the two-check tick before
  the reads +0.57e-5; preparation and waits before it ≈ +0.9e-5. The square round with perfect A/B/C arriving just in
  time on v37c's real prefix gives **2.860e-5** (WHOLEEND), but every built way to prepare the square's interleaved
  blocks on the grid costs ≥ 1e-4 (SQUARE, SQPROJ: FINDINGS "Square final round"); the square is parked. Out of class, no tested ending wins: unmeasured-partner block endings ≥ 28.747 p²,
  whole-grid tails ≥ 3.37e-5, fresh helpers ≥ 4.37e-5, and a 30% gain needs ≥ 4 outputs in a CX at T−1.
- Lanes run on Codex (CONSTRAINTS rule 11), one dir each under `work/lanes/<LANE>`, report to the main session,
  which verifies (all orders, judge `gates_ok`, judge speed by the expected-key rule in circuit.md) and promotes.

## Critical path
Lane candidate → all orders on v37d's terms (≈ 1 s at 16 processes) → judge 1e6/1e7 and speed → `next_stem.txt` →
hourly race (stem read at HH:20, best draw submitted after the HH+1:20 cut once the cooldown allows, now about HH+1:24) → `work/promote.sh` → slot. The board score is the
hour's best draw, about mean − 3.5 to 4σ (σ ≈ 7.2e-7), so a 1% lower mean (3.7e-7) is worth about 3 doublings of
racing compute; racing gains are logarithmic, so lanes take the cores they need and the racer fills the rest at each
hour's start (`race_specs.sh`). Lane searches are bound by ideas, not evaluation. Last stem change that can reach
the final slot (2026-10-30 about 11:24): `next_stem.txt` before 10:20 that day; submissions close at 12:00 (CONSTRAINTS
rule 7), so a better stem verified later can still race a shorter window by hand and be submitted before 11:55.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P106 | G1 | The five-block path ending E–A–D–B–C on the grid (27.207 p², no unit squares, catches every single-block logical resource error without a separate verification; grid-free suffix 3.408e-5 vs square-with-leaf 3.3945e-5), starting from v37c plus an E block checking A | finalist L < L(v37c) − 1e-7 at A ≥ 0.5002 | ENDSEARCH (Codex, `work/lanes/ENDSEARCH`, owl ≤ 24 in docker) | active: phantom E on v37c (real preparation) 3.4542e-5 at A 0.489; grid builds 1.05e-3 because only one A cell has a free neighbour; now the joint A/B/C/E layout solve to a witness or certificate, with E (a leaf: its errors reach A only after D→A) prepared non-FT on scattered cells by graph states and measured helpers and per-coordinate release times (reviewer 16 #3, #7) |
| 2 | P111 | G1 | An earlier round on v37g's line (R44): map the critical path that fixes the round tick (prefix release, data hops, A/B/C readiness, A decoder), then attack it with wider phase-network completion windows, re-routed hops or a one-cell output shift, guards restored and MERGE's repair; each pre-round wait tick was worth −0.684e-6 on v36h | finalist L < L(v37g) − 3e-8 at A ≥ 0.5002, or what fixes the round tick with the measured cost of each attempt | EARLIER (Codex, `work/lanes/EARLIER`, sunfish ≤ 20 from 02:22, zebra ≤ 6) | active |
| 3 | P104 | G1 | Merge the lanes' new gains onto the incumbent, repair to convergence, select by lowest L. Pass 3 gave v37f (−4.58e-7 vs v37d), pass 4 (transplants, ejections, multi-buyer funding, signature pairs) gave v37g (−9.44e-8). Pass 5 on v37h adds what the grammar could not express (reviewer 17): reset-then-herald compounds at every reset (R one tick earlier, M plus detector in its place; with neighbouring CX/M retiming where the tick before is busy, e.g. q4) and detector-span completion (each deterministic parity outside the span and small combinations, priced by all orders, no second-order pruning: c309 gained at zero second-order effect), then the pass-4 grammar to convergence. Next pass also prices GLOBAL's last edit with acceptance funding (`GLOBAL/cand/global_v37g_bcflip`: CX25→24 reversed at tick 36, −2.09e-8 on v37g at −0.0032 acceptance) | finalist L < L(v37h) − 3e-8, or the measured reason the grammar is exhausted | MERGE (Codex, `work/lanes/MERGE`, hippo ≤ 24, zebra ≤ 4) | active |
| 4 | P113 | G1 | Prepare A and B/C as one rank-7 process on the 21 resource cells (reviewer 17 #3, #4, #5, #10): today AJOINT fixes B/C, BFLAG synthesizes B+C+helpers only, and PREPFREE's uniqueness is of the ideal resource, not of its preparation path. Start with 4–8-wire windows across the A–B/C bridges (A13–B12, A9–B3, A21–C27) that move both A and B/C operations with actual release times and records, endpoint stabilizers, signs and outputs checked; relax BFLAG's hard F1 (undetected B residue = 0) to one-coordinate correctable residues s ∈ {0, sig(X_i)} so accepted X residues collect on one output (X2leak, Y/Z parts and the exterior priced); first test whether BFLAG's proxy X2 + K_Z R_Z + K_A acc1 ranks 20–50 diverse legal candidates like full (L, A), and guide by the exterior's cost where it does not; compare finite module-choice sets exhaustively on a factorized exterior (AJOINT's rejoin matches full within 2.2e-16) | finalist L < L(incumbent) − 1e-7 at A ≥ 0.5002, or the measured cost per family | JOINTPREP (Codex, `work/lanes/JOINTPREP`, jerry ≤ 24, zebra ≤ 2) | active |
| 5 | P110 | G2 | Second cleanup: once the lanes above end, delete the closed lanes they still read (ACCBUY, AENC, AJOINT, APROC, BCSYN2, BCV, BCX, BFLAG, BUNDLE, COMPLETE, EARLY, EVAL, EXENC, FLAG, FRESH, GLOBAL, GUARDNET, INTEG, INTEG2, POLISH, PREPFREE, R43, SCHED, SQPROJ, SQUARE, T14, TERM, WHOLEEND, XTIM) and keep one copy of the shared tools (evaluators, repair menu, terminal model) | `work/lanes` holds only live lanes, MAIN and the tools they use | main session | next: when the active lanes end |
| 6 | P2 | G1 | Hourly submission of the best verified candidate; keep `next_stem.txt` on the stem with the lowest expected key: the lowest all-orders mean unless its judge time costs more draws than its gain (≈ 1.1e-7 per halving of the draw rate; σ per draw is equal across stems, FINDINGS "Score spread per stem") (R-20261023-10) | final best in by 2026-10-30 10:20 (later only with a shortened race before the 12:00 close) | main session | active |

## Parked (no price yet; reviewer bundles in `work/lanes/MAIN/spec/`, older ones in git)
- Square final round (reviewer 14 #1, reviewer 15 #1–4): worth up to ≈ −0.8e-5, but every built preparation of its
  interleaved blocks costs ≥ 1e-4 (FINDINGS); reopen only with a prefix that prepares the blocks in place before the
  data arrive.
- Reviewer 15 (`spec/reviewer15/REPORT_KO.md`; numbers reviewer-reported): #6 corrections up to a stabilizer coset
  (8 T instead of 16; the 54-tick controller leaves the data unprotected); #7 a time-sliced 15-T code (bare factory not
  FT: a Z on the reused output wire passes); #10 a flagged 10→7 converter. #5, #8, #9 closed by WHOLEEND (FINDINGS).
- Reviewer 14 (`spec/reviewer14/REPORT_KO.md`): #6 [[10,1,2]] morphing with a flagged 10→7 contraction (gate: the
  noisy conversion from a perfect 10-qubit input must beat ≈ 2.7e-5); #7 25-qubit gauging (46% acceptance as
  published); #8 a \|+i_L⟩ T-specific meter (needs a verified Y resource); #9 steering accepted preparation residues
  onto one output coordinate (a synthesis objective: pair term (Q² − Σqᵢ²)/2); #10 controlled-W hooks that keep the
  syndrome checks. #2–#4 closed by TERMINAL (FINDINGS).
- Reviewer 16 (`spec/reviewer16/REPORT_KO.md`, on v37d; numbers reviewer-reported): #2 price 20–50 of WHOLEEND's 4,791
  un-priced T-only contracts with real preparation (tail c2 mis-ranks); #4 choose a tail's last two layers jointly
  (4-block toy: layerwise 44.8 p², joint 28.747 p², at the unmeasured-partner minimum, still above the square); #5
  contracts that fix only the needed detector parities, not each raw record bit; #6 entangled non-CSS logical resources
  (135 stabilizer groups on three logical qubits, 32 entangled with A read in Z and B in X; witness Z_A X_B, X_A Z_B X_C,
  X_B Y_C keeps T up to (X+Y)/√2 with affine frames; its logical X_A, X_C preparation errors pass); #9 SDP bounds over a
  boundary's free gauge qubits with the accepted-map effects. #3, #7, #8 went to ENDSEARCH and MERGE; #1 and #10 are
  measured (FINDINGS).
- Reviewer 17 (`spec/reviewer17/REPORT_KO.html`, on v37f; numbers reviewer-reported): #6 replace A's terminal logical-X
  decoder flag by small hook flags on the 2–3 dangerous encoder CXs (FLAG's ≤ 1-gap impossibility assumed a fixed depth,
  B→D time, immediate B check and a decoder on A's cells; a flag sees only earlier faults, so re-check the record rank);
  #7 obtain the blue source check's information from the A/B/C interactions and final readout parities (port q1/q2,
  A7/A8, 4–8 wires; deleting the check alone loses); #8 general-Clifford intermediate paths for A (EXENC's 11-CX
  minimum is over CX-only rank-4 paths; a local-Clifford frame alone gains nothing under depolarizing noise); #9 =
  reviewer 16 #2. #1, #2 measured (v37h); #3–#5, #10 → P113.
- Reviewers 3–13 and DIGEST's 94-idea table (`git show b9051547^:work/lanes/DIGEST/DIGEST.md`): none priced below
  v36h; reopen one only with a mechanism that fits the square or path ending.
- Chamberland–Cross flagged logical-H measurement: implementation suspect (our grid build was not FT at first order).

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us either way.
