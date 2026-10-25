# Plan

## Status (2026-10-25 16:10 KST)
- Board: **rank 1** with v36h_h2513_r4852, **server 3.53131e-5** (13:37; key 3.53e-5); Placeholder 4.906e-5.
  The hourly loop `work/receipts/draw_loop.sh` races seed-0 draws of the stem in `work/receipts/next_stem.txt` (now
  `lanes/MAIN/v36h`) against the key boundary below our best and submits the best at :37.
- **Best expected circuit: v36h** (`work/lanes/MAIN/v36h` = ACCBUY `accbuy_f1`: v36g + seven known-state guards on idle
  data, two init-check trades): **all-orders 3.815473e-5 (−0.54% vs v36g), acceptance 0.50164**, 327 CX, R44, FAST.
  Lineage: v36c (ST2) 4.11516e-5 → v36d (INTEG gadgets) 4.02862e-5 → v36e (BFLAG resource r3) 3.92343e-5 → v36f
  (PRECELL guards) 3.83761e-5 → v36g (INTEG2) 3.83605e-5 → v36h. Gadgets, guards and acceptance buyers on this schedule
  are used up (INTEG2, ACCBUY).
- Where the loss sits (FINDINGS "Where v36c's loss sits"): the final round with everything before it noiseless costs
  3.041e-5, of which 2.274e-5 is our terminal class's floor (TERM) and 0.768e-5 leaks that every template tried keeps;
  A, B, C preparation 0.456e-5; prefix and data wait 0.618e-5. Closed today on this layout: an earlier round (R43, worth
  only −0.68e-6), C's partially coherent instrument (PCC), and the A-flag gap (FLAG: ≥ 2 data gap ticks in every valid
  flagged round; helpers need a new layout), and the B/C resource on v36h's cells (P85: 22 LNS runs end at one
  acceptance-only move, decoder-safe residues each cost ≥ p/15·2.6e-3 through the exterior's undetected data-X weight).
  Local edits on v36h pay little: BUNDLE's best 2-edit bundle is −1.75e-8 at acceptance ≥ 0.5005 with 41% of the 2-edit
  neighbourhood enumerated (the rest is finishing as a script).
- Reviewers 11 and 12 (bundles in `work/lanes/MAIN/spec/reviewer{11,12}/`; untrusted, run with `python -I`): B/C
  search widenings (P85, P90), evaluator and racer speedups (done: character tables, quotient contraction, packed
  syndrome decoding), closures (FINDINGS); parked ideas below. Neither found a circuit below the incumbent.
- **Codex is back** (15:28 KST; R-20261025-2): lanes run on Codex workers (`codex:codex-rescue`), Claude only when Codex
  is refused; lane dirs are `work/lanes/<LANE>` and they report to the main session, which verifies and promotes.

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
| 1 | P91 | G1 | Room next to the data on the real grid. Off-grid phantoms on v36h, all orders: both A-flag-gap helpers −1.609e-6, late X check S12X (data 0, 20, 3, 22 at 40–43) −1.150e-6, **both −2.705e-6 (−7.1%)** at acceptance 0.4985 (`work/lanes/GLOBAL/room/prices.txt`); the largest lever left above the round. Blocked in v36h only by occupancy: no free cell next to q10/q21 at 44 or over a stabilizer's support at 39–43; R43's layout model found helper room only with +4–6 hops and 4–17 moved roles, never built (closure inferred). Build cheapest-first (cats or chains over free cells, single role or guard swaps, block translations that keep r3 and the A encoder), then R43's layouts with re-synthesized blocks | finalist L < τ − 5e-7 at A ≥ 0.5002, or every realization priced with the cost that ate the prize per family | GLOBAL (Codex, `work/lanes/GLOBAL`, jerry ≤ 24) | active |
| 2 | P93 | G1 | Prefix-to-suffix interface (DIGEST #1; reviewer 12 #2–4): state-specific completion of the prefix's last stage instead of reversing every routing CX, output placement and earlier releases, kept as a 20–50-profile release archive; first a round-trip model that reproduces v36h with r3. Changes the occupancy that bounded EARLY (R42) and R43's helper layouts; pre-round pool 7.72e-6 | finalist, or three downstream builds priced with none below τ | IFACE (Codex, `work/lanes/IFACE`, hippo ≤ 24) | active |
| 3 | P94 | G1 | A side as one process (DIGEST #2; reviewer 11 Task 5, reviewer 12 #6, reviewer 7 M06): encoder, data guards and partial decoder chosen jointly in 4–6-wire windows, transient encoded flags allowed; A cells 33–42 noiseless −1.64e-6, flag gaps noiseless −2.66e-6 (overlapping) | finalist, or every window around A searched with no witness below τ | APROC (Codex, `work/lanes/APROC`, tom ≤ 12) | active |
| 4 | P90 | G1 | Directly synthesized rank-four B/C resource R_102 (reviewer 12 #1, #5), exact J_τ. Six CP-SAT witnesses all lose (best 4.891e-5; X2 ≥ 4× r3's; acceptance needs region acc1 ≤ 0.3153 vs v36h 0.32187); 24 LNS runs (wave 4) end 16:01, then Pareto pricing (`work/lanes/BCX/HANDOFF.md` §3) | J_τ < 0 finalist, or close with the mechanism in HANDOFF §3.6 | main session (BCX scripts on hippo) | active |
| 5 | P2 | G1 | Hourly submission of the best verified candidate; keep `next_stem.txt` on the best all-orders stem (R-20261023-10) | final best in by 2026-10-30 10:00 | main session | active |

## Parked (an identity or legal witness, no price yet; bundles in `work/lanes/MAIN/spec/`, older ones in git)
- DIGEST (`work/lanes/DIGEST/DIGEST.md`: 94 reviewer ideas from reviewers 1–12 against what we measured since, with closure scope): #3 a B/C verification instrument with an earlier encoded flag and complementary readout (after P90 closes), #4 rank-six 22-T/31-T phase routing with holder protection, #5 C-free post-use verification or another terminal class (no credible estimate).
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
