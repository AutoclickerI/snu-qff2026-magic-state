# Plan

## Status (2026-10-25 10:25 KST)
- Board: **rank 1** with v36f_h2509_r154749, **server 3.58239e-5** (09:37; key 3.58e-5); Placeholder 4.984e-5.
  The hourly loop `work/receipts/draw_loop.sh` races seed-0 draws of the stem in `work/receipts/next_stem.txt` (now
  `lanes/MAIN/v36f`) against the key boundary below our best and submits the best at :37.
- **Best expected circuit: v36g** (`work/lanes/MAIN/v36g` = INTEG2 `integ2_h2`: v36f + 10 small gadgets, 4 init-check
  trades, 6 timing shifts): **all-orders 3.836054e-5 (−0.04% vs v36f), acceptance 0.50151**, 320 CX, R44, FAST; the
  hourly stem from the 10:20 race. Lineage: v36c (ST2) 4.11516e-5 → v36d (INTEG gadgets) 4.02862e-5 → v36e (BFLAG
  resource r3) 3.92343e-5 → v36f (PRECELL guards) 3.83761e-5 → v36g. The gadget space on v36f is used up (INTEG2); ≈ 0.018
  acceptance is free for < 2e-8 loss and nothing on v36f buys it.
- Where v36c's loss sits (FINDINGS "Where v36c's loss sits"): the final round with everything before it noiseless costs
  3.041e-5, of which 2.274e-5 is a floor for every circuit whose outputs end on a CX with a measured partner (TERM) and
  0.768e-5 are leaks that every template tried on this grid keeps; A, B, C preparation 0.456e-5; prefix and data wait
  0.618e-5. Earlier round (R42 floor) and placement changes are closed (EARLY); what remains is B/C and A preparation
  and the masking terms (IDEAS bounds −9.04%, −8.95%; the A encoder is optimal, AENC), and late data idles without a
  free neighbour.
- **Codex is down** (429, ~6-day retry, from 2026-10-25 02:26 KST). Workers are Claude subagents (R-20261025-1); their
  dirs are `work/lanes/<LANE>` and they report to the main session, which verifies and promotes.

## Critical path
Lane delta on v36f → all orders (≈ 11 s) → judge 1e6, speed → `next_stem.txt` → hourly race of seed-0 draws →
`work/promote.sh` → slot. The board score is the hour's best draw: about mean − 3.5 to 4σ (σ = the judge's sem ≈ 7.2e-7), so
a 1% lower mean (3.8e-7) is worth about as much as 3 doublings of racing compute; racing gains are logarithmic, so
lanes take the cores they need and the racer fills the rest at each hour's start (`race_specs.sh`). From the hour to
09:20 the drop rule is relative to the prior (κ = 0.7) and the threshold is relayed across hosts (FINDINGS "Race drop
rule"); before that racing examined ≈ 7.6× more draws than plain re-draws.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P83 | G1 | Spend free acceptance (≈ 0.018 for < 2e-8 loss, INTEG2) on loss: a second colour-code check in the cultivation stage on cells A/B/C use only from ≈ 32 (PRESYN's blue XZ check: −2.8% for ≈ 0.028 on v22), checks/flags in the T-check region, late checks borrowing A/B/C cells before their roles; R44 must hold | a finalist below v36g, or closures with mechanisms | ACCBUY (Claude, `work/lanes/ACCBUY`, zebra ≤ 24 processes) | active |
| 2 | P2 | G1 | Hourly submission of the best verified candidate; keep `next_stem.txt` on the best all-orders stem (R-20261023-10) | final best in by 2026-10-30 10:00 | main session | active |

## Parked (an identity or legal witness, no price yet; bundles in `work/lanes/MAIN/spec/`, older ones in git)
- Reviewer 9 (`spec/reviewer9/`, TASKS.json): M03 adjoint environment reuse for local edits, M04 finite-p pair
  counterfactuals, M05 affine acceptance with frames, M06 factorized magic-sign kernel for > 20 T, M07 accepted-instrument
  B/C contracts, M09 measured graph resources, M10 coupled MC with a control variate.
- Reviewer 8 (`spec/reviewer8/`): error-path-weighted CEGAR targets for the synthesizers; frame gauges for speed.
- Reviewer 7 (`git show b2a5243:work/lanes/MAIN/spec/reviewer7/...`): M02 C-copy exchange (+1.03e-7, +0.0024 acceptance,
  −1 CX) for P75; M04 nonlinear acceptance (8-CX/7-T AND), M05 measured graph resources, M06 transient flags on encoded
  resource wires, M07 C-free post-use verification, M09 conditional sampling: each needs an optimistic gate first.
- Reviewer 4: moving check (CX A→D, D→A, MZ D), dirty-bus remote CX, measured partial uncompute in the phase network.
- Reviewer 3 #7: A as three direct Z checks or a GHZ meter, only with a layout that uses the freed cells.
- Chamberland–Cross flagged logical-H measurement: implementation suspect (our grid build was not FT at first order).

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us either way.
