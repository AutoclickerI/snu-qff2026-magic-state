# Plan

## Status (2026-10-25 05:40 KST)
- Board: **rank 1** with v36b_r580, **server 3.87795e-5** (03:37; key 3.88e-5); Placeholder 4.984e-5, Inae 1.45e-4.
  The hourly loop `work/receipts/draw_loop.sh` races seed-0 draws of the stem in `work/receipts/next_stem.txt` (now
  `lanes/MAIN/v36d`) against the key boundary below ours (3.875e-5) and submits the best at :37.
- **Best expected circuit: v36d** (`work/lanes/MAIN/v36d` = INTEG `integ_g1_j8`: v36c + acceptance trades + 34 pair,
  echo and guard gadgets): **all-orders 4.02862e-5 (−2.10% vs v36c), acceptance 0.50596**, 282 CX, R44, 47 ticks, FAST;
  it is the hourly stem from the 06:37 slot. v36c (4.11516e-5, 213 CX) is the base the lanes' deltas are priced on.
- Where v36c's loss sits (FINDINGS "Where v36c's loss sits"): the final round with everything before it noiseless costs
  3.041e-5, of which 2.274e-5 is a floor for every circuit whose outputs end on a CX with a measured partner (TERM) and
  0.768e-5 are leaks that every template tried on this grid keeps; A, B, C preparation 0.456e-5; prefix and data wait
  0.618e-5. The addressable part is ≈ 1.8e-5 (−45%), mostly prefix/wait, preparation, acceptance trades and the tick-44
  D10/D21 gap (−1.5e-6 if a neighbour of cells 10 or 21 were free then).
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
| 3 | P76 | G1 | Earlier round and suffix placement (incl. freeing a neighbour of cells 10/21 at tick 44 for TERM's −1.5e-6 \|+⟩ CX): below R44 needs the prefix, data placement, A encoder and flag co-synthesized (FINDINGS "Earlier round"); with v36c's suffix the data sit in place from ~tick 35 and prefix/wait gains are capped at 6.18e-6, so the suffix placement must change too; ENDSTATE's R38 geometry reached 4.986e-5 without the v36 gadgets, and the A decoder did not help there | a circuit below v36c with R ≤ 42 | EARLY (Claude, `work/lanes/EARLY`) | active |
| 4 | P59 | G1 | Flag-conditioned A-encoder synthesis (reviewer 7 M01/M03): Pareto by flag-blind vs flag-detected danger and X-side masking (IDEAS bound −4.03%), no c1/p30 pruning, against v36c's releases | v36c encoder deltas | AENC (Claude, `work/lanes/AENC`) | active |
| 5 | P2 | G1 | Hourly submission of the best verified candidate; keep `next_stem.txt` on the best all-orders stem (R-20261023-10) | final best in by 2026-10-30 10:00 | main session | active |
| 6 | P72 | G1, G2 | FAST realizations of SLOW-but-better edits (q8 reuse after the flag: R44→43, +0.009 acceptance; data SX layer) | FAST deltas on v36c | next free worker (FRESH code on disk) | next |
| 7 | P81 | G2 | Delete the untracked bulk of BCFB, COMP29, FRESH, SEPBC, WAITPROT, ST2 and their stale tracked files (essentials in `b2a5243`; locally hidden by `.git/info/exclude`) | only what future search needs is left | main session | parked: AENC and BFLAG read BCFB, SEPBC and FRESH outputs |

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
