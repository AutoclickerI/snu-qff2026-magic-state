# Plan

## Status (2026-10-25 06:30 KST)
- Board: **rank 1** with v36d_h2506_r53, **server 3.75483e-5** (06:37; key 3.75e-5); Placeholder 4.984e-5.
  The hourly loop `work/receipts/draw_loop.sh` races seed-0 draws of the stem in `work/receipts/next_stem.txt` (now
  `lanes/MAIN/v36e`) against the key boundary below ours and submits the best at :37.
- **Best expected circuit: v36e** (`work/lanes/MAIN/v36e` = BFLAG `final/bflag_d3`: v36d with the B/C resource replaced
  by the 56-CX r3): **all-orders 3.92343e-5 (−2.61% vs v36d, −4.66% vs v36c), acceptance 0.50771**, 281 CX, R44, FAST
  (4.1 s/1e6); the hourly stem from the 07:37 slot. v36d = v36c + INTEG's trades and 34 gadgets (4.02862e-5). Lanes'
  deltas are priced on v36c and compose additively (BFLAG's r3: −1.087e-6 on v36c, −1.052e-6 on v36d).
- Where v36c's loss sits (FINDINGS "Where v36c's loss sits"): the final round with everything before it noiseless costs
  3.041e-5, of which 2.274e-5 is a floor for every circuit whose outputs end on a CX with a measured partner (TERM) and
  0.768e-5 are leaks that every template tried on this grid keeps; A, B, C preparation 0.456e-5; prefix and data wait
  0.618e-5. Earlier round (R42 floor) and placement changes are closed (EARLY); what remains is B/C and A preparation
  and the masking terms (IDEAS bounds −9.04%, −8.95%; the A encoder is optimal, AENC), and late data idles without a
  free neighbour.
- **Codex is down** (429, ~6-day retry, from 2026-10-25 02:26 KST). Workers are Claude subagents (R-20261025-1); their
  dirs are `work/lanes/<LANE>` and they report to the main session, which verifies and promotes.

## Critical path
Lane finds a priced mechanism → re-derived on v36c → all orders (≈ 10 s) → judge 1e6, speed, MC3 → `work/promote.sh`
→ hourly slot. Bottleneck: the remaining gains are many small deltas that compete for the same acceptance; fix: one
integrator (INTEG) composes every lane's v36c deltas by Δloss per Δlog-acceptance, and the other lanes deliver deltas
on v36c (or acceptance), not new bases.
Draw cost: racing examines ≈ 7.6× more draws per hour than plain re-draws (FINDINGS "Racing in production").

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P75 | G1, G3 | Integration: compose each lane's v36c deltas with INTEG's trades and gadgets (`work/lanes/INTEG`, REPORT.md: menu of 332 priced singles, greedy by gain, leave-one-out), each joint re-priced by all orders; v36d is its first result | a finalist below v36d each time a lane delivers | main session, INTEG code | next |
| 2 | P73 | G1 | B/C side on v36c (outside the prefix cap): IDEAS' bounds −9.04% (third-order masking by B/C Z flips) and −8.95% (correlated B/C X escaping C's check); mid-preparation B flag (ideal meter first), resource re-synthesis by in-situ loss with the masking objective, B/C acceptance trades | v36c deltas or a finalist below v36c | BFLAG (Claude, `work/lanes/BFLAG`) | active |
| 3 | P82 | G1 | Prefix change that releases a cultivation guard/helper cell next to q7, q3 or q20 by ≈ tick 33 (A, B/C untouched) for a gadget on their late idles (residual 1.24/1.07/1.05e-6; FINDINGS "Freeing neighbours") | a priced bound, then a finalist below v36d or a closure | PRECELL (Claude, `work/lanes/PRECELL`) | active |
| 4 | P2 | G1 | Hourly submission of the best verified candidate; keep `next_stem.txt` on the best all-orders stem (R-20261023-10) | final best in by 2026-10-30 10:00 | main session | active |
| 5 | P72 | G1, G2 | FAST realizations of SLOW-but-better edits (q8 reuse after the flag: R44→43, +0.009 acceptance; data SX layer) | FAST deltas on v36c | next free worker (FRESH code on disk) | next |
| 6 | P81 | G2 | Delete FRESH's untracked bulk (BCFB, COMP29, SEPBC, WAITPROT, ST2 done on every host 2026-10-25 06:00; essentials in `b2a5243`; locally hidden by `.git/info/exclude`) | only what future search needs is left | main session | parked: BFLAG reads FRESH outputs |

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
