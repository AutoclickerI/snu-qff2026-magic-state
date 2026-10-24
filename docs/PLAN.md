# Plan

## Status (2026-10-25 01:20 KST)
- Board: **rank 1**, v35b_r1007 4.12926e-5 (server, 01:37 slot; all-orders 4.37602e-5); Placeholder 4.984e-5, Inae 1.45e-4.
  02:37 slot: **v36a** in re-draws
  (cut 02:20). 03:37 slot: **v36b** (FRESH: v36a + timing, echoes and reset trades, all-orders 4.12933e-5, acceptance
  0.50144, 211 CX), re-draws 02:20–03:20 (`work/receipts/chain_v36b.sh`). Every slot gets the best-expected circuit's best draw.
- **Incumbent v36a** (`work/lanes/MAIN/v36a`, SEPBC `checked16_timing_0`): guard5 lineage (R44, five storage guards) + a
  12-CX A encoder synthesized against the actual cell releases + the A partial decoder + a q16 known-X check:
  **all-orders 4.14605e-5, acceptance 0.50083**, 207 CX, 47 ticks, MC3 4.1770e-5 (structure: reference/circuit.md).
- Gap: proved floor 1.162e-5; grid-free reference 3.55e-5 (R33); ST1's R38 redesign 4.808e-5 without the A decoder.
  Each tick earlier on the round was worth ≈ 1.4e-6 on the v30 lineage. Acceptance is the binding budget.

## Critical path
Lanes find priced mechanisms → re-derive each on the incumbent → all orders → judge 1e6, speed, MC3 → `work/promote.sh`
→ hourly slot. Bottleneck: the incumbent moved four times in three hours (v34m → v35a → v35b → v36a) while lanes priced
their mechanisms on the base they started from, and the incumbent has no current loss ledger. Fix: one integration
lane (P75) owns the incumbent: its ledger first, then every lane's mechanism re-derived on it; lanes report mechanisms
as deltas with their acceptance cost.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P75 | G1, G3 | Integration on v36a: all-orders loss ledger (removal gains by region, top pair classes); port ST2's echoes, COMP29's acceptance-only removals and readout edges, WAITPROT's menu, BCFB's encoders, FRESH's SX if FAST; acceptance knapsack over all of them | a finalist below v36a each time a lane delivers | SEPBC (`work/lanes/SEPBC`) | active |
| 2 | P59 | G1 | Flag-conditioned A-encoder synthesis (reviewer 7 M01/M03): re-rank EXENC/ACHECK paths by flag-blind vs flag-detected danger (Pareto, no c1/p30 pruning), build the frontier with input pivots and flag choice; v36a's encoder already gained 5.6% this way | a frontier encoder below v36a | BCFB (`work/lanes/BCFB`, on v35b; ported via P75) | active |
| 3 | P76 | G1 | Earlier round with the decoder: ENDSTATE/ST1's R38–40 geometry with the A encoder and flag co-synthesized (routes, roles and prefix topology free; ST1 found R38 infeasible with fixed routes and R39 witnesses lost to waiting), then guards/echoes | a circuit below v36a with R ≤ 42 | ST1 (`work/lanes/ST1`) | active |
| 4 | P77 | G1, G3 | Final round redesigned backward (reviewer 8 #10): the round costs ≈ 2.884e-5 of v36b's 4.129e-5 in any Steane-type form, the proved floor is 1.162e-5; terminal templates screened by an optimistic relaxation, survivors built into v36b; evaluator extended to FRAME/POSTSELECT where a template needs it | a template that beats the Steane round's data-side cost, built, or each template closed with its screen value | TERM (`work/lanes/TERM`, thread 01a16ee7) | active |
| 5 | P71 | G1 | R38 base's acceptance headroom (0.087): A decoder for its A placement, echoes, guards, mz inits, knapsack | a finalist below v36a | ENDSTATE (`work/lanes/ENDSTATE`) | active |
| 6 | P72 | G1, G2 | xtim slow path: established (FRESH) — the circuit-wide `has_general` flag is set when any noise atom needs the PPR retry, and then every noisy shot takes the general path. Now: a static atom-count speed predictor, and FAST realizations of SLOW-but-better edits on v36b (q8 reuse after the flag: R44→43, +0.009 acceptance; data SX layer; source reuse) | FAST finalists below v36b | FRESH (`work/lanes/FRESH`) | active |
| 7 | P73 | G1 | Acceptance-only check removal (q16's c43 type), readout edges, a second independent A flag; then reviewer 7's M10 joint-record oracle | priced deltas for P75 | COMP29 (`work/lanes/COMP29`, on v35b) | active |
| 8 | P67 | G1 | Population search with all-orders fitness under the acceptance floor, now on v36b (v35b round: −0.475%, and +0.0038 acceptance at −0.45%) | a finalist below v36b | ST2 (`work/lanes/ST2`, on v36b) | active |
| 9 | P74 | G1 | Acceptance-efficient waiting-data protection (gain per acceptance) | menu `WAITPROT/menu_v35a.json` for P75 | WAITPROT (`work/lanes/WAITPROT`, on v35a) | active |
| 10 | P62 | G1, G2 | B/C boundary cache with acceptance (0.035 s per variant) for a wide B/C search | priced deltas for P75 | BCPOL (`work/lanes/BCPOL`, on v35a) | active |
| 11 | P2 | G1 | Hourly submission of the best verified candidate (`work/promote.sh`, R-20261023-10) | final best in by 2026-10-30 10:00 | main session | active |

## Parked (an identity or legal witness, no price yet; evidence in FINDINGS and `work/lanes/MAIN/spec/`)
- Reviewer 8 (`work/lanes/MAIN/spec/reviewer8/`): mid-preparation B flags (a B logical-Z representative shrinks to Z12·Z13·Z19 near tick 34; test with an ideal meter first) for COMP29; error-path-weighted CEGAR targets for the synthesizers; the linear score N − L0·A with measured pair interactions for P75's knapsack; detector-basis reduction (112 → 85 record terms, official PASS) and frame gauges for speed only.
- Reviewer 7 M02 seed: C-copy exchange (+0.0024 acceptance for +1.03e-7 loss, −1 CX), for P75's knapsack.
- Reviewer 7 M04 nonlinear acceptance (8-CX/7-T AND), M05 measured graph resources (star → triangle), M06 transient flags
  on encoded resource wires, M07 C-free post-use verification with a terminal-latency budget, M08 a syndrome-dressed
  W_L verifier, M09 conditional sampling: each needs an optimistic-oracle or algebraic gate before a build.
- Reviewer 4: moving check (CX A→D, D→A, MZ D), dirty-bus remote CX, measured partial uncompute in the phase network.
- Reviewer 3 #7: A as three direct Z checks or a GHZ meter, only with a layout that uses the freed cells.
- Chamberland–Cross flagged logical-H measurement: implementation suspect (our grid build was not FT at first order).

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us either way.
