# Plan

## Status (2026-10-23 20:0x KST)
- Board: us 0.000123 (v8, 115 CX), Placeholder 0.000129 (103 CX, improving fast).
- v10 submitted 20:05:30: A1 layout + interleaved cycle seeded from L1's CP-SAT orders + ALAP.
  Seed-0 1.21115e-4 (key 0.000121), 3-seed mean 1.2208e-4, 115 CX.
- Cycle schedules have converged for the A1 layout (proxy 1.09799e-4) and the v6 layout (1.12744e-4).
  About 80% of the remaining loss is data idle in the final readout cycle, so the next lever is
  structural (P3 readout, P4 layout).
- Milestone: lanes report by 23:00; the session report is due 2026-10-23 23:59 KST (R-20261023-5).

## Critical path
edit (minutes) → proxy (0.2 s) → anneal on hippo (~1 min per 24 chains) → full circuit + ALAP variants
(1 s) → official seed-0 score (10 s at 20 processes) → 3-seed mean (30 s) → sequential judge (2 min) →
submit (hourly, ~2 min to score). Bottleneck: the cycle-only proxy ranks only Bell-pair circuits with
ALAP applied, so new architectures need official MC to rank (10–30 s per candidate). Fix: P5. Second
limit: the hourly quota, so the next candidate is verified before each slot.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P2 | G1 | Submit the best verified candidate in every hourly slot | every slot used until 2026-10-30 12:00 | main session (`work/submit_when_ready.sh`) | active |
| 2 | P3 | G1 | Direct-readout final round with hook protection; the tail floor is 2.6e-5 vs 5.9e-5 for Bell pairs | a valid candidate beats the best Bell-pair true mean, or a mechanism rules it out | Codex L3 (`work/lanes/L3_direct_readout`) | active |
| 3 | P4 | G1 | Layout co-design (moves, roles, extras) with the schedule | best layout for the cycle found or bounded | Codex L2 (`work/lanes/L2_layout_cpsat`) | active |
| 4 | P5 | G2 | Full-circuit fast evaluator validated against 3-seed means | ranks new-architecture candidates like 3-seed means | Codex L4 (`work/lanes/L4_fullproxy`) | active |
| 5 | P6 | G1 | CP-SAT on the A1 layout and on P4 layouts | certified or improved proxy optimum | Codex L1 (`work/lanes/L1_cpsat_schedule`) | active |
| 6 | P7 | G1 | Pre-cycle and boundary changes beyond ALAP | gain in 3-seed means | Codex L5 (`work/lanes/L5_precycle`) | active |
| 7 | P8 | G4 | ≤ 113 CX at our best key (v6-layout cycle: proxy 1.12744e-4, mean 1.2339e-4) | a ≤ 113-CX candidate at our key | main session | next |
| 8 | P9 | G2 | Tell lanes that c1 = 0 is not required and that the hosts in CONSTRAINTS rule 9 are usable | lanes use them | main session | next: at each lane's next resume |

## Open questions
- Jihoon: standing rules? (a) Codex lanes for expansion work (R-20261023-1, R-20261023-5); (b) run
  everything parallel, never block on one experiment (R-20261023-5, R-20261023-6); (c) prefer solver- or
  simulation-backed search (R-20261023-4). Each is carried out now either way.
- Jihoon: does the ~75% CPU cap (R-20261023-8) apply to every host? Read as yes.
- Jihoon: FuriosaNPUChallenge CONSTRAINTS 13 still says zebra is light-only; correct it there?
- Jihoon: who attends the 2026-10-31 16:30 ceremony if we win (CONSTRAINTS rule 10)?
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us
  either way.
