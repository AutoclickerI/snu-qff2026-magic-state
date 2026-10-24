# Plan

## Status (2026-10-25 04:30 KST)
- Board: **rank 1** with v36b_r580, **server 3.87795e-5** (03:37; key 3.88e-5); Placeholder 4.984e-5, Inae 1.45e-4.
  The hourly loop `work/receipts/draw_loop.sh` races seed-0 draws of the stem in `work/receipts/next_stem.txt` (now
  `lanes/MAIN/v36c`) against the key boundary below ours (3.875e-5) and submits the best at :37.
- **Best expected circuit: v36c** (`work/lanes/MAIN/v36c`, ST2 population edits on v36b): **all-orders 4.11516e-5,
  acceptance 0.50273**, 213 CX, R44, 47 ticks, FAST (structure: reference/circuit.md).
- Where the loss sits (FINDINGS "Where v36's loss sits"): the round ≈ 80% (final data idle, B→D CX), then the B/C
  resource, waiting data, prefix, A, readout. Proved floor 1.162e-5; any Steane-type round pays ≈ 2.884e-5 on the data
  side. With v36c's prefix and data wait made noiseless the loss is still 3.497e-5: prefix and waiting work is capped
  at 6.18e-6, the rest needs a different suffix or final check (P77, P76).
- **Codex is down** (429, ~6-day retry, from 2026-10-25 02:26 KST). Workers are Claude subagents (R-20261025-1); their
  dirs are `work/lanes/<LANE>` and they report to the main session, which verifies and promotes.

## Critical path
Lane finds a priced mechanism → re-derived on v36c → all orders (≈ 10 s) → judge 1e6, speed, MC3 → `work/promote.sh`
→ hourly slot. Bottleneck: few workers (Codex down) and each finalist needs a full integration on the incumbent;
fix: one integrator (INTEG) composes every lane's v36c deltas, and the other lanes deliver deltas on v36c, not new bases.
Draw cost: racing (P78) cuts the full-run cost per useful draw ≈ 5.8×.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P77 | G1, G3 | Final round redesigned backward (reviewer 8 #10): terminal templates screened by an optimistic relaxation, survivors built into v36c; partial-rank syndrome extraction with frames (reviewer 9 M08, 2,825 subspaces); evaluator extended to FRAME/POSTSELECT where a template needs it | a template that beats the Steane round's data-side cost, built, or each template closed with its screen value | TERM (Claude, `work/lanes/TERM`) | active |
| 2 | P75 | G1, G3 | Integration on v36c: acceptance-only trades re-derived on v36c, then a knapsack (Δloss vs Δlog-acceptance with measured pair interactions) over every lane's v36c deltas (WAITPROT menu, COMP29, BCFB, FRESH, ST2), each conjunction re-priced by all orders | a finalist below v36c each time a lane delivers | INTEG (Claude, `work/lanes/INTEG`) | active |
| 3 | P76 | G1 | Earlier round: below R44 needs the prefix, data placement, A encoder and flag co-synthesized (FINDINGS "Earlier round"); with v36c's suffix the data sit in place from ~tick 35 and prefix/wait gains are capped at 6.18e-6, so the suffix placement must change too; ENDSTATE's R38 geometry reached 4.986e-5 without the v36 gadgets, and the A decoder did not help there | a circuit below v36c with R ≤ 42 | EARLY (Claude, `work/lanes/EARLY`) | active |
| 4 | P79 | G1 | Fresh-eyes structural review: list v36c's design assumptions tick by tick, break each with an optimistic ideal-noise or ideal-meter screen, build ideas bounded above 0.5% that no lane owns | ranked idea table with bounds, finalists | IDEAS (Claude, `work/lanes/IDEAS`) | active |
| 5 | P67 | G1 | Population search with all-orders fitness under the acceptance floor (g05 → v36c, −0.34%) | a finalist below v36c | ST2 script `pop36_search.py zebra3` (no agent) | active |
| 6 | P78 | G1 | Racing re-draws (`work/race.py`) in the hourly loop | draws per CPU-hour measured in production | main session | active |
| 7 | P2 | G1 | Hourly submission of the best verified candidate; keep `next_stem.txt` on the best all-orders stem (R-20261023-10) | final best in by 2026-10-30 10:00 | main session | active |
| 8 | P72 | G1, G2 | FAST realizations of SLOW-but-better edits (q8 reuse after the flag: R44→43, +0.009 acceptance; data SX layer) | FAST deltas on v36c | next free worker (FRESH code on disk) | next |
| 9 | P59 | G1 | Flag-conditioned A-encoder synthesis (reviewer 7 M01/M03): Pareto by flag-blind vs flag-detected danger, no c1/p30 pruning, against v36c's releases | v36c encoder deltas | next free worker (BCFB code on disk) | next |
| 10 | P73 | G1 | Mid-preparation B flag (ideal meter priced first), a second A flag | v36c deltas | next free worker (COMP29 code on disk) | next |
| 11 | P81 | G2 | Delete the untracked bulk of BCFB, COMP29, FRESH, SEPBC, WAITPROT, ST2 and their stale tracked files (essentials in `b2a5243`; locally hidden by `.git/info/exclude`) | only what future search needs is left | main session | parked: INTEG (P75) and ST2's search (P67) still read these files |

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
