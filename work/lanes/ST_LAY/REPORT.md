# ST_LAY report

Finding: three disjoint connected regions (A+hA, B+hB, C+hC) on the 6x6 grid are infeasible with helpers
taken from the 8 free cells alone.
- CP-SAT (lay3.py, 5 seeds x 500 s, 10-12 workers) returns UNKNOWN; the A+B-only relaxation is also UNKNOWN.
- Simulated annealing (sa.py, ~50 chains x 150 s) never gets below one split component; ignoring C (A+B only)
  also fails, while A+C and B+C succeed. So the A/B pair is the obstruction (consistent with, not proof of, infeasibility).
- Stripe layouts (5 vertical a-d-b-c columns) are proven INFEASIBLE by CP-SAT.

Workaround that works: use the final data cells d_i as helpers too (they are empty while blocks are prepared;
data arrive afterwards). Then three disjoint regions exist, but data must route around block cells.

| cand | hops | A | B | C |
|---|---|---|---|---|
| 0 | 14 | no encoder at depth<=9 | 9 layers, 38 CX | 4 layers, 12 CX |
| 1 | 18 | none | 9, 39 | 5, 10 |
| 2 | 22 | none | 9, 40 | 5, 12 |

All are worse than L5 (6 hops): B regions are large and snake-like, A has no depth<=9 encoder, data move far.
Prefix symmetry/translation maps were not explored (no time); EVAL/exact2 validation not run.
Files: lay3.py (CP-SAT), sa.py (annealer), build.py, prep.py, layouts.json (3 entries, A preps missing).
