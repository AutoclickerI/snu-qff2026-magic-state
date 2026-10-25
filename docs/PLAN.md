# Plan

## Status (2026-10-25 13:45 KST)
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
  A, B, C preparation 0.456e-5; prefix and data wait 0.618e-5. So the levers left are the B/C resource (P85), the
  A-flag gap (P88) and the masking terms; C's instrument with partial coherence closed on this layout (PCC). An earlier round is worth only −0.68e-6 (R43, closed); the A-flag gap
  idles (q10, q21 at tick 44, 1.36e-6 each) would pay −1.61e-6 with two adjacent helpers, which no layout at R ≤ 44 has.
- Reviewer 11 (bundle in `work/lanes/MAIN/spec/reviewer11/`, TASKS.json; untrusted, run with `python -I`): two
  widenings of the B/C search space (P85; PCC closed), an evaluator speedup (P87), the planner fix (done: warm bases only,
  search only above width 9), and four closures (FINDINGS). It found no circuit below v36g.
- **Codex is down** (429, ~6-day retry, from 2026-10-25 02:26 KST). Workers are Claude subagents (R-20261025-1); their
  dirs are `work/lanes/<LANE>` and they report to the main session, which verifies and promotes.

## Critical path
Lane delta on v36h → all orders (≈ 5 s at 16 processes) → judge 1e6, speed → `next_stem.txt` → hourly race of seed-0
draws → `work/promote.sh` → slot. The board score is the hour's best draw: about mean − 3.5 to 4σ (σ = the judge's sem ≈
7.2e-7), so a 1% lower mean (3.8e-7) is worth about as much as 3 doublings of racing compute; racing gains are
logarithmic, so lanes take the cores they need and the racer fills the rest at each hour's start (`race_specs.sh`: racer
caps hippo 12, zebra 8 leave room for the lanes). The drop rule is relative to the prior (κ = 0.7) and the
threshold is relayed across hosts (FINDINGS "Race drop rule"). The bottleneck of the research loop is the all-orders
price inside lane searches (hundreds per greedy round): P87 cuts it.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P85 | G1 | B/C resource with decoder-safe residues and a joint last-layer window (reviewer 11 Tasks 3, 4): BFLAG's F1 demands s = 0 when no detector fires, but the decoder only needs s ∈ {0, 9..15} (64 of 128 X patterns instead of 8); add X2leak to the LNS objective; extend the synthesized window through B→C at tick 44 with endpoint \|0_L⟩_B\|0⟩^7_C, CX-only, then H/S on charged idles. Prior: FRESH's relaxed-residue R45 builds lost (8.86e-5–1.05e-4) | a resource that beats r3 in all orders on v36h, or the cost that blocks it per lead | BCX (Claude, `work/lanes/BCX`, hippo ≤ 24 cores) | active |
| 2 | P88 | G1 | A-flag gap: q10, q21 idle at 44 (1.36e-6 each; off-grid helpers −1.61e-6, no grid room at R ≤ 44). The "both first-decoder cells coupled by t43" rule ignores that CXs sharing only a target commute: let a flag cell's D→A follow the decoder's first CX, mirror the decoder, relabel A or pick another weight-3 X_L, fill the gap with known-state guards or pairs | a finalist below v36h, or each lead closed with its mechanism | FLAG (Claude, `work/lanes/FLAG`, zebra ≤ 24) | active |
| 3 | P87 | G2 | Evaluator speed: analytic uniform-Pauli characters plus channel merging (reviewer 11 Task 1; on v36g 692 factors/5,580 terms → 438/1,011, all 73 moments within 7.7e-15); swap into `MAIN/sparse` after validation on v29c, v36c–h and edits | `MAIN/sparse` faster end to end with identical moments, consumers (`region.py`, `adjoint_ablation.py`, `ACCBUY/sparse40`) working | EVALF (Claude, `work/lanes/EVALF`, zebra ≤ 8) → main session swaps | active |
| 4 | P2 | G1 | Hourly submission of the best verified candidate; keep `next_stem.txt` on the best all-orders stem (R-20261023-10) | final best in by 2026-10-30 10:00 | main session | active |

## Parked (an identity or legal witness, no price yet; bundles in `work/lanes/MAIN/spec/`, older ones in git)
- Reviewer 11 (`spec/reviewer11/`, TASKS.json): Task 5 joint A encoder + data guard + A decoder across their fixed
  boundary (needs an exterior table built on v36h, AENC's is v36c's); Task 7 non-monotone 2–3-edit bundles on the INTEG2/
  ACCBUY menus, priced as bundles (same-qubit trades are non-additive); Task 8 the 4-T measured-classical RCCX (`physical/
  rccx_probe.py`: nonlinear postselection, 19 T fits the evaluator), each record pair gated by the joint accepted-sector
  oracle first (the first pair lost); Task 9 open-boundary tables for region search.
- Reviewer 9 (`spec/reviewer9/`, TASKS.json): M03 adjoint environment reuse for local edits, M04 finite-p pair
  counterfactuals, M05 affine acceptance with frames, M06 factorized magic-sign kernel for > 20 T, M07 accepted-instrument
  B/C contracts (P86 tests the C-stabilizer form), M09 measured graph resources, M10 coupled MC with a control variate.
- Reviewer 8 (`spec/reviewer8/`): error-path-weighted CEGAR targets for the synthesizers; frame gauges for speed.
- Reviewer 7 (`git show b2a5243:work/lanes/MAIN/spec/reviewer7/...`): M02 C-copy exchange (+1.03e-7, +0.0024 acceptance,
  −1 CX) as an acceptance source; M05 measured graph resources, M06 transient flags on encoded
  resource wires, M07 C-free post-use verification, M09 conditional sampling: each needs an optimistic gate first.
- Reviewer 4: moving check (CX A→D, D→A, MZ D), dirty-bus remote CX, measured partial uncompute in the phase network.
- Reviewer 3 #7: A as three direct Z checks or a GHZ meter, only with a layout that uses the freed cells.
- Chamberland–Cross flagged logical-H measurement: implementation suspect (our grid build was not FT at first order).

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us either way.
