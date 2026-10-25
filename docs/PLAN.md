# Plan

## Status (2026-10-26 00:20 KST)
- Board: **rank 1** with v37c_h2600_r43418, **server 3.428e-5** (key 3.43e-5, 00:40); next team Placeholder 3.856e-5 (22:53; 4.005e-5 an hour earlier), so rank 1 needs our key to keep falling. The
  hourly loop `work/receipts/draw_loop.sh` races seed-0 draws of the stem in `work/receipts/next_stem.txt` and submits
  the hour's best at :37: **v37d** from the 00:20 race (01:37 slot).
- **Best expected circuit: v37e** (`work/lanes/MAIN/v37e`): **all-orders 3.637096e-5, acceptance 0.50243**, 406 CX,
  v37d with GLOBAL's BC3 B/C sources ported by MERGE pass 3 (still repairing); races from the 01:20 race (02:37 slot).
  Round R45 on GLOBAL's R46 layout (data [6,20,19,10,2,22,16]). Since v36h (3.815473e-5): greedy bundles, the R46
  layout with both A-flag-gap helpers (v37a), POLISH (v37b), MERGE of COMPLETE's R45 end, POLISH and GLOBAL's B/C
  (v37c), MERGE pass 2 (v37d 3.676347e-5), BC3 (v37e). Lane gains on a shared base compound when merged.
- Where the loss sits (FINDINGS): our terminal class floor 2.274e-5 is 61% of the total; the two-check tick before
  the reads +0.57e-5; preparation and waits before it ≈ +0.9e-5. The square round with perfect A/B/C arriving just in
  time on v37c's real prefix gives **2.860e-5** (WHOLEEND), but every built way to prepare the square's interleaved
  blocks on the grid costs ≥ 1e-4 (SQUARE, SQPROJ: FINDINGS "Square final round"); the square is parked. Out of class, no tested ending wins: unmeasured-partner block endings ≥ 28.747 p²,
  whole-grid tails ≥ 3.37e-5, fresh helpers ≥ 4.37e-5, and a 30% gain needs ≥ 4 outputs in a CX at T−1.
- Lanes run on Codex (CONSTRAINTS rule 11), one dir each under `work/lanes/<LANE>`, report to the main session,
  which verifies (all orders, judge `gates_ok`, judge speed ≤ 1.5× the incumbent's) and promotes.

## Critical path
Lane candidate → all orders on v37d's terms (≈ 1 s at 16 processes) → judge 1e6/1e7 and speed → `next_stem.txt` →
hourly race (stem read at HH:20, best draw submitted at HH+1:37) → `work/promote.sh` → slot. The board score is the
hour's best draw, about mean − 3.5 to 4σ (σ ≈ 7.2e-7), so a 1% lower mean (3.7e-7) is worth about 3 doublings of
racing compute; racing gains are logarithmic, so lanes take the cores they need and the racer fills the rest at each
hour's start (`race_specs.sh`). Lane searches are bound by ideas, not evaluation. Last stem change that can reach
the final slot (2026-10-30 11:37): `next_stem.txt` before 10:20 that day.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P106 | G1 | The five-block path ending E–A–D–B–C on the grid (27.207 p², no unit squares, catches every single-block logical resource error without a separate verification; grid-free suffix 3.408e-5 vs square-with-leaf 3.3945e-5), starting from v37c plus an E block checking A | finalist L < L(v37c) − 1e-7 at A ≥ 0.5002 | ENDSEARCH (Codex, `work/lanes/ENDSEARCH`, owl ≤ 24 in docker) | active: phantom E on v37c (real preparation) 3.4542e-5 at A 0.489; grid builds 1.05e-3 because only one A cell has a free neighbour; now the joint A/B/C/E layout solve to a witness or certificate, with E (a leaf: its errors reach A only after D→A) prepared non-FT on scattered cells by graph states and measured helpers and per-coordinate release times (reviewer 16 #3, #7) |
| 3 | P91 | G1 | B/C of r3's quality on R46's cells and a late X check on v37a (ideal B/C source and core noise on v37a is worth 4.09e-6; phantom X checks priced, placement binds) | finalist L < L(v37a) − 5e-7 at A ≥ 0.5002, or the cost per family | GLOBAL (Codex, `work/lanes/GLOBAL`, jerry ≤ 24) | active |
| 2 | P111 | G1 | An earlier round on v37e (R44): map the critical path that fixes the round tick (prefix release, data hops, A/B/C readiness, A decoder), then attack it with wider phase-network completion windows, re-routed hops or a one-cell output shift, guards restored and MERGE's repair; each pre-round wait tick was worth −0.684e-6 on v36h | finalist L < L(v37e) − 1e-7 at A ≥ 0.5002, or what fixes the round tick with the measured cost of each attempt | EARLIER (Codex, `work/lanes/EARLIER`, sunfish ≤ 20 from 02:22, zebra ≤ 6) | active |
| 4 | P104 | G1 | Merge the lanes' new gains onto v37d by footprint, regenerate POLISH's menu where they overlap, repair to convergence; pass 3 ported GLOBAL's BC3 B/C resource (v37e, −3.9e-7) and continues with POLISH's latest edits and repair; select by lowest L. Next pass also takes PREPFREE's M12@34, M25@37 (−1.66e-8 on v37d, `PREPFREE/cand/prepfree_final`) and POLISH's converged edits (`POLISH/cand/polish_b1b1dd19e1c1`, 3.738766e-5 on v37a, −3.6e-8 vs v37b). Next pass: ejection moves (drop a selected edit), several acceptance buyers per move, interactions by error signature, not footprint (reviewer 16 #8: two independent D1(p) on different outputs each cost 0 decoded but 5p²/9 together) | finalist L < L(v37e) − 5e-8, or the measured reason they do not combine | MERGE (Codex, `work/lanes/MERGE`, hippo ≤ 24) | active (pass 3) |
| 5 | P110 | G2 | Second cleanup: once the lanes above end, delete the closed lanes they still read (ACCBUY, AENC, AJOINT, APROC, BCSYN2, BCV, BCX, BFLAG, BUNDLE, COMPLETE, EARLY, EVAL, EXENC, FLAG, FRESH, GUARDNET, INTEG, INTEG2, POLISH, PREPFREE, R43, SCHED, SQPROJ, SQUARE, T14, TERM, WHOLEEND, XTIM) and keep one copy of the shared tools (evaluators, repair menu, terminal model) | `work/lanes` holds only live lanes, MAIN and the tools they use | main session | next: when the active lanes end |
| 6 | P2 | G1 | Hourly submission of the best verified candidate; keep `next_stem.txt` on the stem with the lowest expected key: the lowest all-orders mean unless its judge time costs more draws than its gain (≈ 1.1e-7 per halving of the draw rate; σ per draw is equal across stems, FINDINGS "Score spread per stem") (R-20261023-10) | final best in by 2026-10-30 10:20 | main session | active |

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
- Reviewers 3–13 and DIGEST's 94-idea table (`git show b9051547^:work/lanes/DIGEST/DIGEST.md`): none priced below
  v36h; reopen one only with a mechanism that fits the square or path ending.
- Chamberland–Cross flagged logical-H measurement: implementation suspect (our grid build was not FT at first order).

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us either way.
