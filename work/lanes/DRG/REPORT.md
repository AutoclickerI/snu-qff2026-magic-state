# DRG lane report

## Verified results

The exact proxy evaluator was run on the prototype circuits from `work/lanes/DR/poc.py` with the `sched_zfirst.json` schedule:

| structure | qubits | CX | exact proxy |
|---|---:|---:|---:|
| X verified cats + Z Bell pairs (`build_hybrid`, `z_mode="pair"`) | 34 | 54 | 7.479463883712559e-5 |
| X verified cats + Z one-verifier cats (`z_mode="cat1"`) | 43 | 66 | 5.445282246757451e-5 |
| clean cats for X and Z (`build_clean`, `clean_z=True`) | 55 | 90 | 4.493980776112215e-5 |

These are exact `poc.proxy`/`proxy2.joint_loss` results, not estimates.

The existing grid-valid A1 superdense final round was independently re-evaluated with the exact `GModel.proxy` evaluator:

- data cells: `[0, 19, 7, 4, 3, 15, 8]`
- proxy: `1.0979897098975395e-4`
- round CX count: 27 (cycle model; full candidate has 115 CX)
- source: `res_A1_9b_1792752451.json#0`

## Full-circuit candidate

The best available full circuit is the existing ALAP A1 candidate:

- QASM: `work/lanes/DRG/v11_A1i_alap45.qasm` (copied from `work/submissions/v11_A1i_alap45.qasm`)
- metadata: `work/lanes/DRG/v11_A1i_alap45.json` (copied from `work/submissions/v11_A1i_alap45.json`)
- DRG copy of seed measurements: `work/lanes/DRG/v11_A1i_alap45_seeds.json`
- data qubits: `[0, 19, 7, 4, 3, 15, 8]`
- 115 two-qubit gates
- source: A1 double-cat pre-stage plus commuting ALAP seed 45

`fast_check` passed all four judge gates for all three seeds (100,000,000 shots each):

| seed | score | acceptance | passed |
|---:|---:|---:|:---:|
| 0 | 1.1940011244995666e-4 | 0.68458897 | true |
| 1000 | 1.2240502264909212e-4 | 0.68461243 | true |
| 2000 | 1.1879765554513874e-4 | 0.68460947 | true |
| 3-seed mean | 1.2020093021472917e-4 | — | all true |

## Grid obstruction and limit

I attempted CP-SAT placement of the prototype interaction graphs with all 36 cells and reuse permitted only for non-overlapping operation intervals. The X/Z cat interaction graphs are infeasible on the grid. The direct cause is graph topology: the verifier/tree constructions contain odd cycles (including triangles in the cat variants), while a rectangular nearest-neighbour grid is bipartite. The placement model therefore returns `INFEASIBLE` for the 34-, 43-, and 55-qubit variants.

No DRG-specific full circuit was produced: the available exact-proxy improvements require a new bipartite verifier/cat topology and a new detector proof before integration. No submission was made.
