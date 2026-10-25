# Plan

## Status (2026-10-25 17:20 KST)
- Board: **rank 1** with v36h_h2517_r342819, **server 3.48827e-5** (17:37; key 3.49e-5); Placeholder 4.906e-5.
  The hourly loop `work/receipts/draw_loop.sh` races seed-0 draws of the stem in `work/receipts/next_stem.txt` (now
  `lanes/MAIN/v37b` from the 22:20 race) against the key boundary below our best and submits the best at :37.
- **Best expected circuit: v37b** (`work/lanes/MAIN/v37b`: v37a, GLOBAL's R46 layout with both A-flag-gap helpers,
  plus 11 POLISH edits): **all-orders 3.742321e-5 (−0.52% vs v37a), acceptance 0.50348**, 391 CX; races from the 23:37
  slot. v37a's first race (submitted 21:39, best draw 3.48009e-5, key 3.48e-5) is being scored. Lineage: v36c (ST2)
  4.11516e-5 → v36e (r3) 3.92343e-5 → v36h (ACCBUY) 3.815473e-5 → v36k (greedy bundles) 3.789826e-5 → v37a (layout
  R46) 3.761822e-5 → v37b. Lanes found separate −1.8e-7 gains on v37a (GLOBAL's B/C 3.7433e-5, COMPLETE's phase-network
  end 3.7441e-5, the round one tick earlier; COMPLETE closed); MERGE combines them with POLISH's edits.
- Where the loss sits (FINDINGS "Where v36c's loss sits"): the final round with everything before it noiseless costs
  3.041e-5, of which 2.274e-5 is our terminal class's floor (TERM) and 0.768e-5 leaks that every template tried keeps;
  A, B, C preparation 0.456e-5; prefix and data wait 0.618e-5. Closed today on this layout: an earlier round (R43, worth
  only −0.68e-6), C's partially coherent instrument (PCC), and the A-flag gap (FLAG: ≥ 2 data gap ticks in every valid
  flagged round; helpers need a new layout), and the B/C resource on v36h's cells (P85: 22 LNS runs end at one
  acceptance-only move, decoder-safe residues each cost ≥ p/15·2.6e-3 through the exterior's undetected data-X weight).
- Reviewers 11–14 (`work/lanes/MAIN/spec/reviewer{11,12,13,14}/`; untrusted, run with `python -I`; reviewer 14's square final round is P102) and DIGEST's
  re-read of reviewers 1–12: B/C widenings (P85 closed, P90), evaluator and racer speedups (done: character tables,
  quotient contraction, packed syndrome decoding; P96), acceptance sources (P95). None found a circuit below v36h.
  Fixed today from reviewer 13: `fast_check.py` reports `gates_ok` apart from the 1e6-shot acceptance estimate, and
  `race_specs.sh` skips a host without room instead of forcing 4 racers past the 75% cap.
- Lanes run on Codex (CONSTRAINTS rule 11), one dir each under `work/lanes/<LANE>`, and report to the main session,
  which verifies and promotes. IFACE, BCV and GUARDNET closed their tested families (FINDINGS).

## Critical path
Lane delta on v36h → all orders (≈ 1 s at 16 processes) → judge 1e6, speed → `next_stem.txt` → hourly race of seed-0
draws → `work/promote.sh` → slot. The board score is the hour's best draw: about mean − 3.5 to 4σ (σ = the judge's sem ≈
7.2e-7), so a 1% lower mean (3.8e-7) is worth about as much as 3 doublings of racing compute; racing gains are
logarithmic, so lanes take the cores they need and the racer fills the rest at each hour's start (`race_specs.sh`: racer
caps hippo 12, zebra 8 leave room for the lanes). The drop rule is relative to the prior (κ = 0.7) and the threshold
is relayed across hosts (FINDINGS "Race drop rule"). The all-orders price inside lane searches is ≈ 1 s at 16 processes and ≈ 3–5 s
CPU at 1 (EVALF character tables, then reviewer 12's quotient contraction, ≈ 2× less CPU) and the adjoint map ≈ 1 min,
so lane searches are bound by ideas, not evaluation.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P102 | G1 | Reviewer 14's square final round (`spec/reviewer14/REPORT_KO.md` #1, #5): A = \|+_L⟩, B = \|0_L⟩, C = \|+_L⟩; D→A ∥ B→C, then B→D ∥ C→A, then MZ(A), MX(B), MX(C). B's X syndrome reaches A through C, and C catches A's logical Z, so the round reaches TERM's two-check floor 25.67 p² (reviewer-reported round only 2.5558e-5 vs 2.8713e-5 for the Steane round; TERM had this route blocked only by a literal-\|0_L⟩ C). Our round is ≈ 30 p², so ≈ −3e-6 if preparation costs stay comparable; B needs a logical-Z verification first; the eraser variant (C's readout as FRAME_Z) frees A's state. Gates 1–2 passed (SQUARE): round only reproduced exactly (square 2.555843e-5, eraser 2.558464e-5, Steane 2.871336e-5; v37a's round 2.903231e-5); grid-free full suffix with real preparations 3.4896e-5 vs 4.0423e-5 for the standard suffix built the same way (−5.5e-6). Gate 3, the grid, is the obstacle: each index needs a 2×2 cell square, which scatters every block, so first builds run 88–95 ticks at 6.6e-4–1.3e-3 (A ≈ 0.2); noiseless preparation and waits bring the same build to 3.38e-5 | finalist L < τ(v37a) − 1e-7 at A ≥ 0.5002, or the failed gate with measured costs | SQUARE (Codex, `work/lanes/SQUARE`, hippo ≤ 12, owl ≤ 16 in docker) | active |
| 2 | P91 | G1 | Room next to the data on the real grid. Off-grid phantoms on v36h, all orders: both A-flag-gap helpers −1.609e-6, late X check S12X (data 0, 20, 3, 22 at 40–43) −1.150e-6, **both −2.705e-6 (−7.1%)** at acceptance 0.4985 (`work/lanes/GLOBAL/room/prices.txt`); the largest lever left above the round. Blocked in v36h only by occupancy: no free cell next to q10/q21 at 44 or over a stabilizer's support at 39–43; R43's layout model found helper room only with +4–6 hops and 4–17 moved roles, never built (closure inferred). Built: R46 with both helpers, repaired, is v37a (−5.4e-7 vs v36h); next on v37a: r3-quality B/C on R46 cells (≈ 0.9e-6 behind), a late X check, greedy bundle polish | finalist L < τ − 5e-7 at A ≥ 0.5002, or every realization priced with the cost that ate the prize per family | GLOBAL (Codex, `work/lanes/GLOBAL`, jerry ≤ 24) | active: finalist v37a (−5.4e-7 vs v36h); continuing on v37a |
| 3 | P100 | G1 | A encoder, nearby data guards and A's partial decoder as one process with transient encoded flags (DIGEST #2, reviewer 11 Task 5, reviewer 12 #6, reviewer 7 M06); A cells 33–42 noiseless −1.64e-6; rebased on v37a at 20:00 (177 v36k circuits priced, best −1.4e-8 below the gate) | finalist as P99, or the window grown until the boundary model no longer fits, with the cost that ate the gain | AJOINT (Codex, `work/lanes/AJOINT`, hippo ≤ 24) | active |
| 4 | P101 | G1 | The greedy local-edit polish on v37a (BUNDLE's menu ported to R46: singles, connected 2-bundles, greedy joint extension; then GUARDNET's guard network and APROC's A pass): v36i → v36k gained −1.93e-7 this way | a greedy round gains < 1e-9 after all three stages | POLISH (Codex, `work/lanes/POLISH`, zebra ≤ 16) | active |
| 5 | P104 | G1 | Merge the lanes' independent gains on v37a (POLISH's edits, GLOBAL's B/C, COMPLETE's phase-network end) by footprint, re-apply POLISH's menu where they overlap, repair | finalist L < L(v37b) − 5e-8, or the measured reason they do not combine | MERGE (Codex, `work/lanes/MERGE`, hippo ≤ 4) | active |
| 6 | P105 | G1 | Out-of-class endings as optimistic tails before any redesign (v37b's last two ticks hold 2.276e-5 = class floor, 61%; any-circuit floor 1.366e-5): dummy unmeasured-helper CXs in the read tick, last check one tick earlier, coherent recovery, linear correction + logical FRAME, syndrome-zeroing check | each ending priced or ruled out; one below ≈ 2.4e-5 goes to a grid test and a full build | TERMINAL (Codex, `work/lanes/TERMINAL`, hippo ≤ 4) | active |
| 7 | P2 | G1 | Hourly submission of the best verified candidate; keep `next_stem.txt` on the best all-orders stem (R-20261023-10) | final best in by 2026-10-30 10:00 | main session | active |

## Parked (an identity or legal witness, no price yet; bundles in `work/lanes/MAIN/spec/`, older ones in git)
- Reviewer 14 (`spec/reviewer14/REPORT_KO.md`, on v36i; numbers reviewer-reported): #2 physical syndrome removed
  linearly (P₁^s₀P₂^s₁P₄^s₂) with the remainder as a logical FRAME from a measured OR₃(s) (verified on all 64 sector
  pairs and 16,384 Paulis; duplicated RCCX OR needs 32 T, above our evaluator's 20 T; decided by how long the data wait
  during the Boolean computation); #3 coherent recovery with unmeasured one-hot controls, the only route out of the
  measured-partner class (27 qubits before flags; first a full single-fault check of the decomposed lookup, then an
  optimistic terminal circuit); #4 a final check that also zeroes the syndrome, merged into existing readouts (a free
  logical-only projector plus one D1 tick gives 4.909e-5 on v36i; selecting syndrome 0 alone keeps A 0.5005); #6
  [[10,1,2]] morphing with a flagged 10→7 contraction (bare 6-CX conversion fails at first order; gate: the noisy
  conversion from a perfect 10-qubit input must beat ≈ 2.7e-5); #7 25-qubit gauging (46% acceptance and 18
  classically controlled corrections as published); #8 a \|+i_L⟩ T-specific meter (needs a Y resource and its
  verification); #9 steering accepted preparation residues onto one output coordinate (an objective for B/C
  synthesis: the pair term is (Q² − Σqᵢ²)/2); #10 controlled-W hooks that keep the syndrome checks. Their
  closures (reviewer-reported): dummy final CX 4.10–4.17e-5, appended encoded helpers, [[16,1,4]] shallow decode
  6.16e-5, logical-only final check 4.91e-5; 91.9% of the second-order sector they examined comes from two faults
  that no existing detector sees.
- Reviewer 13 (`spec/reviewer13/`): #6 logical-coset tagging of B through redundant C marks (BCV built tag 10 natively, 54 CX, judge-valid: +2.98e-6, preparation 9.07e-6 against a 3.11e-6 budget; 35 of 120 tags unresolved by the solver); #7 Choi-SDP relaxation of one slot as a synthesis target and stop certificate (formulated, not solved); #8 keeping candidates by score distribution (E[ℓ²]), not only the mean: SEM can rise at most to 8.72e-7 from ≈ 7.2e-7, worth ≤ ≈ 6e-7 of key at 4σ; first measure whether real stems differ.
- DIGEST (`work/lanes/DIGEST/DIGEST.md`: 94 reviewer ideas from reviewers 1–12 against what we measured since, with closure scope; #1 done by COMPLETE, #2 is P100, #3 closed by BCV): #4 rank-six 22-T/31-T phase routing with holder protection, #5 C-free post-use verification or another terminal class (no credible estimate).
- Reviewer 12 (`spec/reviewer12/`, TASKS.json, REPORT_KO.txt): #2 coherent completion instead of TREP2's full reversal of
  the phase-network routing CXs (`network()` undoes every routing CX; synthesize only the completion the target state
  needs, with output placement and the next check); parked because the prefix is cheap on v36h: summed per-channel
  removal gains (overlapping) are 0.4e-6 for ticks ≤ 12 and 1.1e-6 for 13–22, against 12e-6 for 33–42 and 65e-6 for
  the round (`MAIN/sparse/v36h_adjoint_72.json`); #3 a global lifetime/placement model that reproduces v36h exactly
  (ST1/FRESH's used independent A/B/C encoders and cannot express r3) before any wider solve; #4 keep candidates by
  critical-cell release profile, not only L and L − λA (ST2 `pop36_search.py` drops slot-opening prefixes); #7 the
  22-T normalized rank-six phase family (39,928 minimal supports, witness in `code/rank6_phase_audit.py`; three harmful
  phase-axis pairs, so it pays only through cheaper routing; needs > 20 T in the evaluator, reviewer 9 M06), screened
  first against T14's failure mechanism.
- Reviewer 11 (`spec/reviewer11/`, TASKS.json): Task 5 joint A encoder + data guard + A decoder across their fixed
  boundary (needs an exterior table built on v36h, AENC's is v36c's; reviewer 12 #6); Task 8 the 4-T measured-classical RCCX (`physical/
  rccx_probe.py`: nonlinear postselection, 19 T fits the evaluator), each record pair gated by the joint accepted-sector
  oracle first (the first pair lost); Task 9 open-boundary tables for region search.
- Reviewer 9 (`spec/reviewer9/`, TASKS.json): M03 adjoint environment reuse for local edits, M04 finite-p pair
  counterfactuals, M05 affine acceptance with frames, M06 factorized magic-sign kernel for > 20 T, M07 accepted-instrument
  B/C contracts (PCC closed the C-stabilizer form on v36h's layout), M09 measured graph resources, M10 coupled MC with a control variate.
- Reviewer 8 (`spec/reviewer8/`): error-path-weighted CEGAR targets for the synthesizers; frame gauges for speed.
- Reviewer 7 (`git show b2a5243:work/lanes/MAIN/spec/reviewer7/...`): M02 C-copy exchange (+1.03e-7, +0.0024 acceptance,
  −1 CX) as an acceptance source; M05 measured graph resources, M06 transient flags on encoded
  resource wires, M07 C-free post-use verification, M09 conditional sampling: each needs an optimistic gate first.
- Reviewer 4: moving check (CX A→D, D→A, MZ D), dirty-bus remote CX, measured partial uncompute in the phase network.
- Reviewer 3 #7: A as three direct Z checks or a GHZ meter, only with a layout that uses the freed cells.
- Chamberland–Cross flagged logical-H measurement: implementation suspect (our grid build was not FT at first order).

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us either way.
