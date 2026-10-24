# Plan

## Status (2026-10-25 02:45 KST)
- Board: **rank 1**. 01:37 entry v35b_r1007 4.12926e-5 (server); 02:37 entry **v36a_r665, server 3.90052e-5** (best of 978
  draws; all-orders 4.14605e-5); Placeholder 4.984e-5, Inae 1.45e-4. 03:37: best v36b draw (`work/receipts/chain_v36b.sh`).
  From 04:37 the hourly loop `work/receipts/draw_loop.sh` re-draws whatever `work/receipts/next_stem.txt` names.
- **Best expected circuit: v36c** (`work/lanes/MAIN/v36c` = ST2 `pop36b/zebra/g05_68249cb83c3226`, population edits on
  v36b): **all-orders 4.11516e-5, acceptance 0.50273**, judge PASS, FAST. v36b = FRESH `r35/sepbc_reset_40_41_42`
  (v36a + timing, echo and reset trades): 4.12933e-5, acceptance 0.50144, 211 CX, R44, 47 ticks (structure:
  reference/circuit.md, written for v36a).
- Where the loss sits (SEPBC ledger on v36a, removal gains, overlapping): the round 3.34e-5 of 4.146e-5 (final data
  idle 2.76e-5, B→D 1.38e-5, B→C 4.2e-6, D→A 3.3e-6); BC resource 5.8e-6, waiting data 4.8e-6, prefix 4.3e-6, A 1.9e-6,
  readout 1.6e-6. Proved floor 1.162e-5; any Steane-type round ≈ 2.884e-5 on the data side (ARCH).
- Free acceptance: SEPBC's prep-reset delays and initial-check trades raise v36a's acceptance 0.50083 → 0.51692 at
  unchanged loss; every lane now spends it on v36b.

## Critical path
Lanes find priced mechanisms → re-derive each on the incumbent → all orders → judge 1e6, speed, MC3 → `work/promote.sh`
→ hourly slot (best seed-0 draw). Bottlenecks: (1) lanes priced mechanisms on the base they started from; fix: all
mechanism lanes rebased on v36b at 02:25 and publish v36b deltas with acceptance cost, SEPBC (P75) composes them.
(2) Each draw costs a full 1e8 shots; fix: DRAW (P78) races draws chunk by chunk and drops hopeless ones early.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P75 | G1, G3 | Integration on v36b: SEPBC's acceptance-only trades re-derived on v36b and v36c, then a knapsack (N − L0·A with measured pair interactions) over ST2, FRESH, WAITPROT, COMP29, BCFB and BCPOL v36b deltas, every conjunction re-priced by all orders | a finalist below v36c each time a lane delivers | SEPBC (`work/lanes/SEPBC`) | active |
| 2 | P59 | G1 | Flag-conditioned A-encoder synthesis (reviewer 7 M01/M03) against v36b's releases, decoder and q16 check: Pareto by flag-blind vs flag-detected danger, no c1/p30 pruning | v36b encoder deltas | BCFB (`work/lanes/BCFB`, on v36b) | active |
| 3 | P76 | G1 | Earlier round with the decoder: ENDSTATE/ST1's R38–40 geometry with the A encoder and flag co-synthesized (routes, roles and prefix topology free; ST1 found R38 infeasible with fixed routes and R39 witnesses lost to waiting), then guards/echoes | a circuit below v36a with R ≤ 42 | ST1 (`work/lanes/ST1`) | active |
| 4 | P77 | G1, G3 | Final round redesigned backward (reviewer 8 #10): the round costs ≈ 2.884e-5 of v36b's 4.129e-5 in any Steane-type form, the proved floor is 1.162e-5; terminal templates screened by an optimistic relaxation, survivors built into v36b; evaluator extended to FRAME/POSTSELECT where a template needs it | a template that beats the Steane round's data-side cost, built, or each template closed with its screen value | TERM (`work/lanes/TERM`, thread 01a16ee7) | active |
| 5 | P71 | G1 | R38 base's acceptance headroom (0.087): A decoder for its A placement, echoes, guards, mz inits, knapsack | a finalist below v36a | ENDSTATE (`work/lanes/ENDSTATE`) | active |
| 6 | P72 | G1, G2 | xtim slow path: established (FRESH) — the circuit-wide `has_general` flag is set when any noise atom needs the PPR retry, and then every noisy shot takes the general path. Now: a static atom-count speed predictor, and FAST realizations of SLOW-but-better edits on v36b (q8 reuse after the flag: R44→43, +0.009 acceptance; data SX layer; source reuse) | FAST finalists below v36b | FRESH (`work/lanes/FRESH`) | active |
| 7 | P73 | G1 | On v36b: acceptance-only removals and prep timing, idle_star and joint guards re-derived, reviewer 8's mid-preparation B flag (ideal meter priced first), a second A flag, M10 oracle | v36b deltas for P75 | COMP29 (`work/lanes/COMP29`, on v36b) | active |
| 8 | P67 | G1 | Population search with all-orders fitness under the acceptance floor on v36b (g05 → v36c, −0.34%) | a finalist below v36c | ST2 (`work/lanes/ST2`, on v36b) | active |
| 9 | P74 | G1 | Acceptance-efficient waiting-data protection re-placed on v36b (v35a menu: terminal_joint −2.3% at acceptance 0.515) | `WAITPROT/menu_v36b.json` for P75, finalists | WAITPROT (`work/lanes/WAITPROT`, on v36b) | active |
| 10 | P62 | G1, G2 | B/C boundary cache rebuilt on v36b's exterior, wide B/C search with acceptance | v36b deltas for P75 | BCPOL (`work/lanes/BCPOL`, on v36b) | active |
| 11 | P78 | G1 | Racing re-draws: chunk-by-chunk seed-0 sampling, prune draws that cannot beat the threshold, bit-identical completed scores; launcher for promote | more draws per CPU-hour, adopted into `work/` | DRAW (`work/lanes/DRAW`) | active |
| 12 | P79 | G1 | Fresh-eyes structural review that builds: list v36b's design assumptions tick by tick, break each with an optimistic ideal-noise or ideal-meter screen, build ideas bounded above 0.5% that no active lane owns | ranked idea table with bounds, finalists | IDEAS (`work/lanes/IDEAS`) | active |
| 13 | P2 | G1 | Hourly submission of the best verified candidate (`work/receipts/draw_loop.sh` runs `work/promote.sh` on `receipts/next_stem.txt` each hour; keep that file on the best all-orders stem; R-20261023-10) | final best in by 2026-10-30 10:00 | main session | active |

## Parked (an identity or legal witness, no price yet; evidence in FINDINGS and `work/lanes/MAIN/spec/`)
- Reviewer 8 (`work/lanes/MAIN/spec/reviewer8/`): error-path-weighted CEGAR targets for the synthesizers; detector-basis reduction (112 → 85 record terms, official PASS) and frame gauges for speed only. (Mid-preparation B flags are in P73, N − L0·A in P75.)
- Reviewer 7 M02 seed: C-copy exchange (+0.0024 acceptance for +1.03e-7 loss, −1 CX), for P75's knapsack.
- Reviewer 7 M04 nonlinear acceptance (8-CX/7-T AND), M05 measured graph resources (star → triangle), M06 transient flags
  on encoded resource wires, M07 C-free post-use verification with a terminal-latency budget, M08 a syndrome-dressed
  W_L verifier, M09 conditional sampling: each needs an optimistic-oracle or algebraic gate before a build.
- Reviewer 4: moving check (CX A→D, D→A, MZ D), dirty-bus remote CX, measured partial uncompute in the phase network.
- Reviewer 3 #7: A as three direct Z checks or a GHZ meter, only with a layout that uses the freed cells.
- Chamberland–Cross flagged logical-H measurement: implementation suspect (our grid build was not FT at first order).

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us either way.
