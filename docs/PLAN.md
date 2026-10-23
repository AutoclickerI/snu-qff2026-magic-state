# Plan

## Status (2026-10-23 23:30 KST)
- Board: Placeholder 7.604e-5 (161 CX, acc 0.590); us 1.127e-4 (v12 = L5-lane pre-stage gains on the v11 family, true mean 1.142e-4).
- New final round (FINDINGS "Steane-type final round"): 3.20e-5 grid-free, data side at the floor. First grid circuit 6.05e-4
  because of the A-encoder × data-exposure cross term; fixes in progress (low-danger A, blocks prepared during the pre-stage tail,
  parallel block preps). Layout L5 (no helpers, 6 hops) needs a joint B+C prep that CP-SAT has not solved.
- Closed this evening: BP push (1.193e-4, no gain over v12), DRG cat embedding (cat graphs not bipartite), Codex audit (no bound).

## Critical path
edit (minutes) → proxy (0.2 s) → anneal on hippo (~1 min per 24 chains) → full circuit + ALAP variants
(1 s) → official seed-0 score (10 s at 20 processes) → 3-seed mean (30 s) → sequential judge (2 min) →
submit (hourly, ~2 min to score). Bottleneck: the cycle-only proxy ranks only Bell-pair circuits with
ALAP applied, so new architectures need official MC to rank (10–30 s per candidate). Fix: P5. Second
limit: the hourly quota, so the next candidate is verified before each slot.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P14 | G1 | Steane round on the grid: B+C joint prep for L5 | exact min depth with proof status (CP-SAT: none at 6–12; light-cone bound 6) | Sonnet lane ST_BC (`work/lanes/ST_BC`, jerry, tom) | active |
| 2 | P15 | G1 | Layouts with three independently connected block regions (parallel small preps) | layouts.json with preps | Sonnet lane ST_LAY (`work/lanes/ST_LAY`, hippo, sunfish) | active |
| 3 | P17 | G1 | Exact block encoders: BFS over CSS states (X-stabilizer subspaces), every optimal circuit scored by exact danger; replaces seed sampling | encoders with min CX, min depth and min danger proven per class | Codex lane EXENC (`work/lanes/EXENC`, zebra) | active |
| 4 | P5 | G1 | Exact second-order full-circuit evaluator (fault pairs through the judge's engine), loss by fault pair, per-location sensitivity | agrees with v12's 12-seed MC mean within the third-order residual | Sonnet lane EVAL (`work/lanes/EVAL`, owl) | active |
| 5 | P16 | G1 | Integrate (`work/lanes/DR/merge.py`), score, submit the best verified candidate | official 3-seed mean below 7.6e-5 | main session | waiting on P14/P15 |
| 6 | P2 | G1 | Hourly submission of the best verified candidate (seed-0 re-draws, R-20261023-10) | each slot with a gain used | main session | active |

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us
  either way.
