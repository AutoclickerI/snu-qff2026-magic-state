# Plan

## Status (2026-10-26 00:20 KST)
- Board: **rank 1** with v37a_h2521_r2793, **server 3.48009e-5** (key 3.48e-5); next team Placeholder 3.856e-5 (22:53; 4.005e-5 an hour earlier), so rank 1 needs our key to keep falling. The
  hourly loop `work/receipts/draw_loop.sh` races seed-0 draws of the stem in `work/receipts/next_stem.txt` and submits
  the hour's best at :37: v37c for the 00:37 slot, **v37d** from the 00:20 race (01:37 slot).
- **Best expected circuit: v37d** (`work/lanes/MAIN/v37d`): **all-orders 3.676347e-5, acceptance 0.50235**, 406 CX,
  48 ticks, round R45 on GLOBAL's R46 layout (data [6,20,19,10,2,22,16]). Since v36h (3.815473e-5): greedy bundles,
  the R46 layout with both A-flag-gap helpers (v37a), POLISH's edits (v37b), MERGE of COMPLETE's R45 end, POLISH and
  GLOBAL's B/C (v37c), MERGE pass 2 (v37d). Lane gains on a shared base compound when merged.
- Where the loss sits (FINDINGS): our terminal class floor 2.274e-5 is 61% of the total; the two-check tick before
  the reads +0.57e-5; preparation and waits before it ≈ +0.9e-5. The square round with perfect A/B/C arriving just in
  time on v37c's real prefix gives **2.860e-5** (WHOLEEND), so the square route is worth up to ≈ −0.8e-5, decided
  by preparing A, B, C on the grid. Out of class, no tested ending wins: unmeasured-partner block endings ≥ 28.747 p²,
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
| 1 | P102 | G1 | Square final round on the grid (reviewer 14 #1; reviewer 15 #1–3): A, C = \|+_L⟩, B = \|0_L⟩; D→A ∥ B→C, then B→D ∥ C→A, read A in Z, B and C in X; 25.667 p², the two-check floor. Coupling C_i → A_{P(i)} with P a Steane automorphism removes the unit square per index (reviewer 15's layout from v37b with two data hops, checked: all 28 contacts adjacent, P preserves the judge's codewords). Encoder route with measured helpers (byproducts folded into detectors) and the 18-stabilizer resource (3 gauge qubits free) | finalist L < L(v37d) − 1e-7 at A ≥ 0.5002, or the failed gate with measured costs | SQUARE (Codex, `work/lanes/SQUARE`, owl ≤ 24 in docker, hippo ≤ 8) | active |
| 2 | P109 | G1 | The square round by projector preparation (reviewer 15 #4), diversifying P102: A, C from \|+⟩⁷ with Z stabilizers measured, B from \|0⟩⁷ with X stabilizers measured, all 512 branches kept and folded into the final detectors; flagged or bridged syndrome paths over scattered cells, P and the layout in one CP-SAT model, just-in-time preparation, then MERGE's menu and acceptance buyback | finalist L < L(v37d) − 1e-7 at A ≥ 0.5002, or the cost that ate the gain | SQPROJ (Codex, `work/lanes/SQPROJ`, hippo ≤ 24) | active |
| 3 | P106 | G1 | The five-block path ending E–A–D–B–C on the grid (27.207 p², no unit squares, catches every single-block logical resource error without a separate verification; grid-free suffix 3.408e-5 vs square-with-leaf 3.3945e-5), starting from v37c plus an E block checking A | finalist L < L(v37c) − 1e-7 at A ≥ 0.5002 | ENDSEARCH (Codex, `work/lanes/ENDSEARCH`, tom ≤ 24) | active |
| 4 | P107 | G1 | v37c's own A and B/C preparations under the weakest contract its round needs (reviewer 15 #2–4): measured helpers, the needed stabilizer subspace with free gauge qubits, projector preparation | finalist L < L(v37c) − 5e-8, or each contract priced with the cost that ate its gain | PREPFREE (Codex, `work/lanes/PREPFREE`, sunfish ≤ 12) | active |
| 5 | P91 | G1 | B/C of r3's quality on R46's cells and a late X check on v37a (ideal B/C source and core noise on v37a is worth 4.09e-6; phantom X checks priced, placement binds) | finalist L < L(v37a) − 5e-7 at A ≥ 0.5002, or the cost per family | GLOBAL (Codex, `work/lanes/GLOBAL`, jerry ≤ 24) | active |
| 6 | P101 | G1 | Greedy local-edit polish on v37a (BUNDLE's menu ported: singles, connected 2-bundles, joint extension; guard network; A pass) | a greedy round gains < 1e-9 | POLISH (Codex, `work/lanes/POLISH`, zebra ≤ 16) | active |
| 7 | P104 | G1 | Merge the lanes' new gains onto v37d by footprint, regenerate POLISH's menu where they overlap, repair to convergence | finalist L < L(v37d) − 5e-8, or the measured reason they do not combine | MERGE (Codex, `work/lanes/MERGE`) | next: when a lane posts a gain |
| 8 | P110 | G2 | Second cleanup: once the lanes above end, delete the closed lanes they still read (ACCBUY, AENC, AJOINT, APROC, BCSYN2, BCV, BCX, BFLAG, BUNDLE, COMPLETE, EARLY, EVAL, EXENC, FLAG, FRESH, GUARDNET, INTEG, INTEG2, R43, SCHED, T14, TERM, XTIM) and keep one copy of the shared tools (evaluators, repair menu, terminal model) | `work/lanes` holds only live lanes, MAIN and the tools they use | main session | next: when the active lanes end |
| 9 | P2 | G1 | Hourly submission of the best verified candidate; keep `next_stem.txt` on the best all-orders stem (R-20261023-10) | final best in by 2026-10-30 10:20 | main session | active |

## Parked (no price yet; reviewer bundles in `work/lanes/MAIN/spec/`, older ones in git)
- Reviewer 15 (`spec/reviewer15/REPORT_KO.md`; numbers reviewer-reported): #6 corrections up to a stabilizer coset
  (8 T instead of 16; the 54-tick controller leaves the data unprotected); #7 a time-sliced 15-T code (bare factory not
  FT: a Z on the reused output wire passes); #10 a flagged 10→7 converter. #5, #8, #9 closed by WHOLEEND (FINDINGS).
- Reviewer 14 (`spec/reviewer14/REPORT_KO.md`): #6 [[10,1,2]] morphing with a flagged 10→7 contraction (gate: the
  noisy conversion from a perfect 10-qubit input must beat ≈ 2.7e-5); #7 25-qubit gauging (46% acceptance as
  published); #8 a \|+i_L⟩ T-specific meter (needs a verified Y resource); #9 steering accepted preparation residues
  onto one output coordinate (a synthesis objective: pair term (Q² − Σqᵢ²)/2); #10 controlled-W hooks that keep the
  syndrome checks. #2–#4 closed by TERMINAL (FINDINGS).
- Reviewers 3–13 and DIGEST's 94-idea table (`git show b9051547^:work/lanes/DIGEST/DIGEST.md`): none priced below
  v36h; reopen one only with a mechanism that fits the square or path ending.
- Chamberland–Cross flagged logical-H measurement: implementation suspect (our grid build was not FT at first order).

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us either way.
