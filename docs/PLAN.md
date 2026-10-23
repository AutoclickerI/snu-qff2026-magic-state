# Plan

## Status (2026-10-23 22:55 KST)
- Board 21:08: Placeholder 8.475e-5 (147 CX, acc 0.603), us 1.194e-4 (v11; true mean 1.219e-4).
- Floors (FINDINGS): any circuit ≥ 2.55e-5 (1.16e-5 if every gate were noiseless except the final
  wait); the final round is ≈98% of v11's loss. Grid-free direct-readout rounds with clean cats beat
  our Bell round on the exact proxy (4.5–5.5e-5 vs 1.098e-4) but need 36–48 ancillas; the grid has 29.
- Old lanes L1–L5 are stopped (Jihoon, 21:15). Running: BP push (Claude), DRG embedding (Codex),
  bound AUDIT (Codex).

## Critical path
edit (minutes) → proxy (0.2 s) → anneal on hippo (~1 min per 24 chains) → full circuit + ALAP variants
(1 s) → official seed-0 score (10 s at 20 processes) → 3-seed mean (30 s) → sequential judge (2 min) →
submit (hourly, ~2 min to score). Bottleneck: the cycle-only proxy ranks only Bell-pair circuits with
ALAP applied, so new architectures need official MC to rank (10–30 s per candidate). Fix: P5. Second
limit: the hourly quota, so the next candidate is verified before each slot.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P2 | G1 | Submit the best verified candidate each hourly slot (best seed-0 re-draw of the best true mean, R-20261023-10) | every slot with a gain is used until 2026-10-30 12:00 | main session (`work/submit_when_ready.sh`) | waiting for a candidate below 1.19e-4 |
| 2 | P10 | G1 | Grid-valid direct-readout final round (clean cats, Z-before-X), then full circuit | round proxy < 6e-5 on the grid, then official 3-seed mean below 8.5e-5 | Codex DRG (`work/lanes/DRG`) | active |
| 3 | P11 | G1 | Bell-pair round pushed toward its 5.86e-5 floor | official 3-seed mean below v11's 1.219e-4 | Claude BP (`work/lanes/BP_push`) | active |
| 4 | P12 | G3 | Independent audit of the lower bound and any rule detours | report with proof and tested detours | Codex AUDIT (`work/lanes/AUDIT`) | active |
| 5 | P13 | G2 | Search tools for the direct-readout class (`work/lanes/DR`: relaxed floors, prototypes) | DRG uses them | main session | done for now |

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us
  either way.
