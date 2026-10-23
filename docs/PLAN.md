# Plan

## Status (2026-10-23 19:5x KST)
- Rank 1 with v8 (server 0.000123, 115 CX); Placeholder second at 0.000129 with 103 CX and improving fast.
- Best local: v10 = A1 layout + interleaved final cycle seeded from L1's CP-SAT orders + ALAP. Proxy
  1.0980e-4, seed-0 1.21115e-4 (key 0.000121), 3-seed mean 1.2208e-4, 115 CX. Armed for the 20:05 slot
  (`work/submit_when_ready.sh`, submits only if the sequential judge passes).
- About 80% of the remaining loss is data idle in the final readout cycle (FINDINGS). The next large
  lever is the readout paradigm (P3, P4), not more pre-cycle tuning.
- Next action: confirm v10 scored on the server (20:05 slot), then rank the next A1/v6-layout anneal
  batch (hippo) and the tom ALAP screen by 3-seed means and arm the 21:05 slot.
- Milestone: lanes report by 23:00 and the session's report is due 2026-10-23 23:59 KST (R-20261023-5).
  Contest deadline 2026-10-30 12:00 KST.

## Critical path
edit model or schedule (minutes) → proxy (0.2 s) → anneal or CP-SAT (2–30 min) → build full circuit
plus ALAP variants (1 s) → official seed-0 score via `fast_check` (10 s at 16–20 processes) → 3-seed mean
(30 s) → sequential judge and fault scan (2 min) → submit (hourly slot, ~2 min to score).
Bottleneck: the cycle-only proxy is the only fast ranker, and it ranks correctly only after ALAP and
only within the Bell-pair architecture. New architectures (direct readout, new layouts) need official
MC to rank, at 10–30 s per candidate. Fix: P5, a full-circuit evaluator. The second limit is the hourly
quota, so always have the next candidate verified before the slot.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P1 | G1 | A1 + interleaved cycle + ALAP: anneal from L1 bases, screen ALAP seeds, 3-seed means, submit the best | best true mean verified and submitted | main session (`work/lanes/me_layout`) | active |
| 2 | P2 | G1 | Submit hourly: the best verified candidate in every slot | every slot used until 2026-10-30 12:00 | main session | active |
| 3 | P3 | G1 | Direct single-step readout final round with hook protection (flags); tail floor 2.6e-5 vs 5.9e-5 for Bell pairs | a valid candidate beats the best Bell-pair true mean, or a mechanism shows why not | Codex L3 (`work/lanes/L3_direct_readout`) | active |
| 4 | P4 | G1 | Layout co-design (moves, roles, extras) with the schedule, solver-based | best layout for P1/P3 found or bounded | Codex L2 (`work/lanes/L2_layout_cpsat`) | active |
| 5 | P5 | G2 | Full-circuit fast evaluator, validated against multi-seed MC | ranks ALAP'd and new-architecture candidates like 3-seed means | Codex L4 (`work/lanes/L4_fullproxy`) | active |
| 6 | P6 | G1 | CP-SAT on the A1 layout and on new layouts from P4 | certified or improved proxy optimum | Codex L1 (`work/lanes/L1_cpsat_schedule`) | active |
| 7 | P7 | G1 | Pre-cycle and boundary changes beyond ALAP | gain measured in 3-seed means | Codex L5 (`work/lanes/L5_precycle`) | active |
| 8 | P8 | G4 | Fewer CX at equal score (drop the d1 move or extras where they do not pay) | a candidate with ≤ 113 CX at our best key | — | next |
| 9 | P9 | G2 | Tell the lanes that c1 = 0 is not required (CONSTRAINTS "Not constraints") | lanes screen on the official gates only | main session | next: when each lane next resumes |
