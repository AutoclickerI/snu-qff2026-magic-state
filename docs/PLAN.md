# Plan

## Status (2026-10-23 21:40 KST)
- Board 21:08: Placeholder 8.475e-5 (147 CX, acc 0.603, 20:36), us 1.194e-4 (v11, 115 CX; true mean
  1.219e-4).
- Jihoon stopped all work at 21:15 to re-analyze the lower bound and the route to it first. All lanes
  and host jobs are stopped. Nothing is armed to submit.
- v11 loss split: the final round is ≈98% (round alone 9.96e-5, plus 1.8e-5 cross with the pre-stage);
  the injection + double-cat check alone is 1.4e-6. Floors: any circuit ≥ 2.57e-5 (direct readout
  tails); our Bell-pair class ≥ 5.86e-5.

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
| 3 | P4 | G1 | Layout co-design (moves, roles, extras) with the schedule | best layout for the cycle found or bounded | Claude agent L2 (`work/lanes/L2_layout_cpsat`) | active |
| 4 | P5 | G2 | Full-circuit fast evaluator validated against 3-seed means | ranks new-architecture candidates like 3-seed means | Codex L4 (`work/lanes/L4_fullproxy`) | active |
| 5 | P6 | G1 | CP-SAT on the A1 layout and on P4 layouts | certified or improved proxy optimum | Codex L1 (`work/lanes/L1_cpsat_schedule`) | active |
| 6 | P7 | G1 | Pre-cycle and boundary changes beyond ALAP | gain in 3-seed means | Codex L5 (`work/lanes/L5_precycle`) | active |
| 7 | P8 | G4 | ≤ 113 CX at our best key (v6-layout cycle: proxy 1.12744e-4, mean 1.2339e-4) | a ≤ 113-CX candidate at our key | main session | next |
| 8 | P9 | G2 | Tell lanes that c1 = 0 is not required and that the hosts in CONSTRAINTS rule 9 are usable | lanes use them | main session | next: at each lane's next resume |

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us
  either way.
