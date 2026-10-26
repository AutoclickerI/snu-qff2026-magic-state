# Plan

## Status (2026-10-26 20:00 KST)
- Board: **rank 2**. Placeholder took rank 1 at 19:31 with **3.086e-5** (key 3.09e-5, 293 CX, acceptance 0.510; their
  entries were 6.286e-5 at 169 CX and 3.856e-5 at 201 CX). Ours: v37i_h2617_r1992, 3.325e-5 (17:29). v37j's mean
  3.587e-5 would need a 7σ draw to reach 3.08e-5, so racing cannot recover rank 1: a true mean ≲ 3.35e-5 is needed
  (hourly bests sit ≈ 3.8σ below the mean), lower as they improve. Ties go to fewer CX (theirs 293). The hourly loop
  `work/receipts/draw_loop.sh` races the stem in `work/receipts/next_stem.txt` (read at HH:20) and
  `submit_when_ready.sh` submits the hour's pick when its key beats our board key.
- **Best expected circuit: v37j** (`work/lanes/MAIN/v37j`): **all-orders 3.587095e-5, acceptance 0.50102**, 412 CX,
  49 native ticks: MERGE's pass 5 on v37i (3.591182e-5, EARLIER's R45 route repair) combined with EARLIER's last
  finalist; races from the 19:20 race; judge time 1.2–1.27× v37i's (expected-key delta ≈ +1e-8). Round R45 on GLOBAL's
  R46 layout (data [6,20,19,10,2,22,16]). Since v36h (3.815473e-5): greedy bundles, R46 with both A-flag-gap helpers
  (v37a 3.761822e-5), POLISH (v37b), MERGE passes (v37c, v37d 3.676347e-5), BC3 (v37e, v37f 3.630561e-5), MERGE pass 4
  (v37g), reviewer 17 (v37h 3.611955e-5), EARLIER (v37i), MERGE pass 5 (v37j).
- Lanes (20:00): the route back is a new ending on the contracted prefix. REDESIGN contracted the prefix (40 ideal-identity
  CXs, relabelled moves, dead resets; done at tick 37) and priced square + leaf 2.942e-5, path 3.017e-5, square 3.114e-5
  grid-free before repair; all priority now goes to their grid embedding (REDESIGN by CP-SAT, EMBED by constructive
  search), FLAGH's lean flag-based design (3.020e-5 grid-free, 180 CX) is the second route, and WAITCUT tests the B/C factory's
  movement. EARLIER (P111) and CONTRACTS (P117)
  closed (FINDINGS "Closed recipes").
- Where the loss sits (FINDINGS): with only v37g's last 2/3/4 ticks noisy the loss is 2.276/2.847/2.905e-5, so 79%
  survives a noiseless prefix: a ≥ 20% gain needs a different final check or a cleaner state entering it, not polish.
  Floors: any circuit ≥ 2.189e-5 with the penultimate layer kept (reviewer 18; numerics reproduced, reduction audited
  by CONTRACT; 1.366e-5 was loose); our terminal class 2.274e-5 is only 8.5e-7 above it, so leaving the class buys little at
  the terminal itself. Reviewer 18's C4–Steane contraction reaches 2.192e-5 from a perfect 28-qubit input, but every
  priced way to feed it loses (CONTRACT, P114 closed: late growth ≥ 8.7e-5 even from a perfect 7-qubit input, early
  growth's own check + contraction 5.16e-5, best complete alternative 4.37e-5 and 3.61e-5 with perfect resources). The square round
  (2.860e-5 on v37c's real prefix with perfect A/B/C) failed on grid preparation (≥ 1e-4; parked); out-of-class
  endings tested so far lose (unmeasured-partner blocks ≥ 28.747 p², whole-grid tails ≥ 3.37e-5, fresh helpers
  ≥ 4.37e-5).
- Both architecture lanes find the same pattern: a phantom or grid-free design beats v37h by ≈ 3e-6 (WAITCUT's
  just-in-time B/C factory with X-memory 3.282e-5; REDESIGN's path ending with 8-CX templates 3.305e-5), and every
  grid build so far loses before repair (grid factory 5.27e-5, history meter 3.84e-5; joint CP-SAT layouts with one
  transfer per coordinate infeasible through tick 47–60). The measured obstacle is moving resources on the grid.
- Two kinds of lanes: architecture lanes (P115, P116) are judged against full-circuit targets 2.8e-5 (−23%) and
  2.5e-5 (−31%) or a measured obstacle; repair lanes (P104) bank ≥ 3e-8 gains for the hourly race. A
  1e-8-scale win is maintenance, not evidence that the jump is near.
- Lanes run on Codex (CONSTRAINTS rule 11), one dir each under `work/lanes/<LANE>`, report to the main session,
  which verifies (all orders, judge `gates_ok`, judge speed by the expected-key rule in circuit.md) and promotes.

## How lanes run (reviewer 19's process review, adopted 2026-10-26)
- Each experiment names its hypothesis, the smallest result that changes a decision, a budget (prices, hours, cores)
  and what earns more budget. It ends in one class: finalist; certified exclusion (mechanism or solver proof, scope
  named); measured failure (that recipe only); budget exhausted (open); proxy rejection (open, proxy named).
- Families are compared at equal bounded repair: one standard pass (≤ 200 exact prices or 30 min of MERGE's singles),
  and each price records the repair it received. An unrepaired loss closes nothing.
- Architecture questions run concurrently: numerical, preparation and geometry tests per family, several families
  alive until their budgets end them. Fixed parts (the cultivation prefix, a layout, a resource contract) are scope
  with an expiry: each lane names what it fixes and when it tests changing it.
- c1 = 0 is a preference (GOAL non-goals): a bounded-residue track is priced by all orders beside the zero-singles one.
- One promotion policy (circuit.md): exact L, raw validity, `gates_ok`, A ≥ 0.5002, the expected-key speed rule; no
  lane-local speed caps. promote.sh's 20 s per 1e6 shots is our margin under the one-hour scoring limit (≈ 27 server
  minutes at 1e8), not a contest rule. A finalist goes to the main session at once.
- Lanes never signal processes they did not start (racers included); on an overfull host they shrink their own jobs.
- Not adopted: dropping the sequential official check (it finishes inside the cooldown and costs no slot); a mid-hour
  stem switch (≤ half an hour of racing for one stem change; the late-stem shortened race covers the final day).

## Critical path
Lane candidate → all orders on v37d's terms (≈ 1 s at 16 processes) → judge 1e6/1e7 and speed → `next_stem.txt` →
hourly race (stem read at HH:20, best draw submitted after the HH+1:20 cut once the cooldown allows, now about HH+1:24) → `work/promote.sh` → slot. The board score is the
hour's best draw, about mean − 3.5 to 4σ (σ ≈ 7.2e-7), so a 1% lower mean (3.7e-7) is worth about 3 doublings of
racing compute; racing gains are logarithmic, so lanes take the cores they need and the racer fills the rest at each
hour's start (`race_specs.sh`). Lane searches are bound by ideas, not evaluation. Last stem change that can reach
the final slot (2026-10-30 about 11:24): `next_stem.txt` before 10:20 that day; submissions close at 12:00 (CONSTRAINTS
rule 7), so a better stem verified later can still race a shorter window by hand and be submitted before 11:55.

## Levers
Gap: v37j's true mean 3.587e-5 to the floor 2.189e-5 = 1.40e-5. Shares come from v37g's noise cuts (only the last
2/3 ticks noisy: 2.276/2.847e-5); cuts are ordered counterfactuals, not additive allocations.
| Lever | Stage | Ceiling (basis) | Cost per verdict | Standing |
|---|---|---|---|---|
| Preparation and waits before the final check | prefix, A/B/C, data hops | ≤ 0.77e-5, 54% (full vs last 3 ticks noisy); ideal B/C source and core 0.41e-5 (v37a); each earlier round tick ≈ 0.07e-5 (R43 on v36h) | repair pass: hours (MERGE); movement experiment: 8 h (WAITCUT) | deciding: P115, P104; an earlier round on the current line closed (EARLIER: R44/R45 infeasible with its operations, FINDINGS) |
| Final check structure (the D→A / B→C tick) | ending | ≤ 0.57e-5, 40% (last 3 vs 2 ticks noisy); square round −0.29e-5 with perfect resources; C4 contraction lower still | a day per family | deciding: P116 redesigns the layout around a square-type check; grid-free with real preparation square + leaf 3.283e-5, path and square 3.316e-5 (−0.28e-5 vs v37i); no grid embedding yet; contracts chosen for preparation cost lost (CONTRACTS); every C4 feed lost (CONTRACT, ENDSEARCH) |
| Terminal class | last two ticks | ≤ 0.09e-5, 6% (class floor 2.274e-5 vs 2.189e-5) | — | decided: stay in class |
| Racing compute | hourly race | ≈ 1.1e-7 of key per doubling of draws (Gaussian extreme value) | free cores | decided: racer fills the cores lanes leave |
| Judge time per draw | race | ≈ 1.1e-7 of key per halving | one 1e6 timing | decided: expected-key promotion rule (circuit.md) |
| Search-grammar completeness | repair | measured −9.2e-8 once (reviewer 17: herald + detector span) | minutes per incumbent | deciding: MERGE pass 5 |

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P116 | G1 | A new ending on a contracted prefix, on the grid (R-20261026-1). Contracted prefix (40 ideal-identity CXs removed, known-state moves relabelled, dead resets removed; done at tick 37) with real just-in-time preparation, grid-free before repair: square + leaf 2.942e-5, path 3.017e-5, square 3.114e-5. Every CP-SAT embedding so far infeasible or UNKNOWN (fixed prefix placement, ≤ 2 transfers per coordinate; relaxed square witness at R44 with 32 transfers ignores prefix occupancy). Now all budget on a complete grid build: prefix symmetries and translations, re-chosen outputs and hops, more transfers, guards dropped where cells are needed | a grid build ≤ 3.4e-5 at A ≥ 0.5002 to cand/ at once; first priced grid build by 2026-10-27 06:00 | REDESIGN (Codex, CP-SAT, jerry ≤ 24) and EMBED (Codex, constructive local search, `work/lanes/EMBED`, sunfish ≤ 20) | active |
| 2 | P115 | G1 | Attack the preparation-and-waits share (≤ 0.77e-5, 54% of the gap). Measured on v37h (FINDINGS): each pre-44 window of B, C or data made noiseless alone gains 1.1–1.9e-6, jointly less (B/C operations 30–44 3.18e-6 vs 5.44e-6 summed); the surviving mechanisms are X faults on B/C with identical final signatures and late data Y idles. Grid-free just-in-time B/C factory 3.341e-5 (with X-memory 3.282e-5); every grid build loses after bounded repair (factory 4.82e-5, history meter 3.82e-5, retimed history checks fail acceptance); synchronized movement schedules on the real prefix infeasible. Now one budgeted experiment: asynchronous movement with measured transfers between encoder layers and new templates on v37i's prefix (8 h from 17:00; stop if every model is infeasible or the best repaired build is > 1e-6 above v37i) | a full circuit below v37i at A ≥ 0.5002, or the experiment closed with its class | WAITCUT (Codex, `work/lanes/WAITCUT`, owl ≤ 24 in docker, zebra ≤ 2) | active |
| 3 | P119 | G1 | A lean flag-based preparation (Chamberland & Cross 2019; Chamberland & Noh 2020). Grid-free decision test passed: injection + full Steane precheck + two 7-cat shared-basis logical checks + square ending, 180 CX, 36 wires, 15 T, no harmful single fault, **3.0198e-5 at A 0.665** after one bounded repair (without the precheck 3.76–3.99e-5). SABRE and reverse routing to the grid fail (≥ 5e-3). Now grid-native synthesis: data and terminal tiles first, cat states grown along free cells, any encoder per cell set, cell reuse, transfers; then spend the acceptance surplus on loss | a grid build ≤ 3.4e-5 at A ≥ 0.5002 to cand/ at once; first native grid build by 2026-10-27 06:00, checkpoint 14:00 | FLAGH (Codex, `work/lanes/FLAGH`, hippo ≤ 24) | active |
| 4 | P104 | G1 | Merge the lanes' gains onto the incumbent and repair in budgeted passes, selecting by lowest L with judge speed screened before pricing (a measured state reused as an X-basis preparation can send the judge to its slow path, FINDINGS). Pass 5 gave v37j (−4.09e-8 on v37i, judge 1.2–1.27× slower). Passes now gain ≈ 4e-8 at a judge-time cost of ≈ 3e-8, so the lane waits for new material; its hippo cores race meanwhile | repair of any architecture lane's grid build within 1e-6 of v37j, or a new mechanism worth ≥ 1e-7 | MERGE (Codex, `work/lanes/MERGE`, hippo ≤ 24 when active) | next: when P115 or P116 delivers a grid build |
| 5 | P110 | G2 | Second cleanup: once the lanes above end, delete the closed lanes they still read (ACCBUY, AENC, AJOINT, APROC, BCSYN2, BCV, BCX, BFLAG, BUNDLE, COMPLETE, EARLY, EVAL, EXENC, FLAG, FRESH, CONTRACT, ENDSEARCH, GLOBAL, GUARDNET, INTEG, INTEG2, JOINTPREP, POLISH, PREPFREE, R43, SCHED, SQPROJ, SQUARE, T14, TERM, WHOLEEND, XTIM) (shared tools live in `work/tools/qtools`) | `work/lanes` holds only live lanes and MAIN | main session | next: when the active lanes end |
| 6 | P2 | G1 | Hourly race of the stem with the lowest expected key: the lowest all-orders mean unless its judge time costs more draws than its gain (≈ 1.1e-7 per halving of the draw rate; σ per draw is equal across stems, FINDINGS "Score spread per stem") (R-20261023-10); the hour's best draw is submitted when its key beats the board | final best in by 2026-10-30 10:20 (later only with a shortened race before the 12:00 close) | main session | active |

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
- Reviewer 16 (`spec/reviewer16/REPORT_KO.md`, on v37d; numbers reviewer-reported): #2 measured by CONTRACTS (FINDINGS); #4 choose a tail's last two layers jointly
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
  minimum is over CX-only rank-4 paths; a local-Clifford frame alone gains nothing under depolarizing noise); #9 measured by CONTRACTS. #1, #2 measured (v37h); #3–#5, #10 measured by JOINTPREP (FINDINGS).
- Reviewers 3–13 and DIGEST's 94-idea table (`git show b9051547^:work/lanes/DIGEST/DIGEST.md`): none priced below
  v36h; reopen one only with a mechanism that fits the square or path ending.

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us either way.
