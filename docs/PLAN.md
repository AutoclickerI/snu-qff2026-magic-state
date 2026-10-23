# Plan

## Status (2026-10-23 23:30 KST)
- Board: Placeholder 7.604e-5 (161 CX, acc 0.590); us 1.127e-4 (v12 = L5-lane pre-stage gains on the v11 family, true mean 1.142e-4).
- New final round (FINDINGS "Steane-type final round"): 3.20e-5 grid-free, data side at the floor. First grid circuit 6.05e-4
  because of the A-encoder × data-exposure cross term; fixes in progress (low-danger A, blocks prepared during the pre-stage tail,
  parallel block preps). Layout L5 (no helpers, 6 hops) needs a joint B+C prep that CP-SAT has not solved.

## Critical path
edit (minutes) → exact score `lanes/EVAL/exact2.py` (2 s, 2nd order; `--third` 30 s) → official seed-0 MC
(10 s at 20 processes) and 3-seed mean (30 s) for the finalists → sequential judge (2 min) → submit (hourly,
~2 min to score). Bottleneck now: no valid grid Steane-round circuit yet (P14–P17); the hourly quota limits
only submissions, so the next candidate is verified before each slot.

## Ranked work
| Rank | Id | Serves | Work | Done when | Who | State |
|---|---|---|---|---|---|---|
| 1 | P14 | G1 | Steane round on the grid: B+C joint prep for L5 that keeps C an independent check of B (first full L5 circuit: c1 7.7e-4 from correlated B/C faults) | merged circuit with c1 = 0 and fewer than 10 layers, or a proof that none exists | Sonnet lane ST_BC (`work/lanes/ST_BC`, jerry, tom) | active |
| 2 | P15 | G1 | Co-place pre-stage and round: every symmetry/translation of the pre-stage footprint (~48), blocks staged in cells free during the pre-stage with one-hop moves, optional block D on the released pre-stage ancilla cells; minimise round start R | per placement: feasible, R with and without D, exact score of the winners (c1 = 0) | Sonnet lane ST_LAY (`work/lanes/ST_LAY`, hippo, sunfish) | active |
| 3 | P17 | G1 | Exact block encoders (`work/lanes/EXENC/exenc.py`): A on L5 done (FINDINGS); run on B, C (and A) of every ST_LAY layout | preps for each candidate layout | main session | next |
| 4 | P18 | G1 | Block D (\|+_L⟩) checking A's Z errors before A couples: grid-free gain, 35-cell layout feasibility, full circuit | proxy with/without D, layout or infeasibility proof, exact score | Sonnet lane ST_AV (`work/lanes/ST_AV`, owl) | active |
| 5 | P16 | G1 | Integrate (`work/lanes/DR/merge.py`), score, submit the best verified candidate | official 3-seed mean below 7.6e-5 | main session | parked: P14/P15 |
| 6 | P2 | G1 | Hourly submission of the best verified candidate (seed-0 re-draws, R-20261023-10) | each slot with a gain used | main session | active |

## Open questions
- Organizers might rescore with other seeds; P §2.3 says seed 0 is official. True-mean gains protect us
  either way.
