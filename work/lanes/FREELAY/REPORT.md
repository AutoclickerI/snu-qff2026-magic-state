# FREELAY — verified mean 7.536742492e-05

**Delivery: [joint_reuse2_alap.qasm](joint_reuse2_alap.qasm) and [metadata](joint_reuse2_alap.json).** Its three 1e8-shot MC scores have mean **7.536742492e-05**, a measured **1.30%** below the requested v18 bar 7.636e-5. Seed-0 acceptance is **0.53486914**. The full 1e6-shot judge passes format, class, correctness, and acceptance. This satisfies the first completion branch. It remains above the supplied leader score 5.727e-5.

The winner retains the L5 cell sets and clean 82-CX joint B+C preparation. It reuses the prefix MX states on cells 10 and 9, whose records are already postselected, for the first data hops from 4 and 8. Each hop uses the |+⟩ transfer order CX destination→source, then CX source→destination. Full-circuit CP-SAT timing puts the native round at 45, versus the supplied v18 reference at 46. The 11-CX A encoder wins over the tested 12-CX lower-danger encoder. No submission, commit, push, credential access, sub-agent, or write outside FREELAY was performed.

The separate-block target near 3.55e-5 was **not reached**. The successful delivery is a scheduling/reuse improvement in the joint-prep option, not a successful separate-encoder placement. The measured difference is modest relative to MC uncertainty (each winner seed has SEM about 1.04e-6); it is not an established true-mean optimum.

## Models

Times are native operations. [co_design.py](co_design.py) reserves complete live-state intervals, including destination resets and both source CX/measurement steps of a move. Prefix wire order is preserved and its end is free. Encoder wire dependencies precede moves, every final A/B partner is distinct, and B→C at R is immediately followed by B→data at R+1. Data moves use two CX; block moves use one CX plus measurement, with detector-frame XORs. The optional early-A branch frees A cells after readout. The optional GL(3,2) branch permits all 168 code-label automorphisms independently (joint B/C retain their paired labeling).

The 48 legal isometry/translation embeddings reduce to **six** labeled translation classes under whole-board D4 symmetry. [geometry.json](geometry.json) records every mapping; [geometry.py](geometry.py) exhaustively verifies it. Small-block templates are EXENC/L5’s 11-CX six-layer witness and 12-CX nine-layer witness; B and C use the dual 11-CX encoder. The standard grid-free 9-CX graph has zero direct seven-cell grid embeddings. This closes that fixed-cell graph only, not dynamically routed 9-CX encoders or all possible small encoders.

Initial occupancy searches used the stated integer exposure proxy. A four-build nonnegative calibration uses native prefix/data/block exposure features ([calibration.json](calibration.json)); data moves and teleports retain explicit exploratory priors because those four builds do not identify their coefficients. The first placement test exposed an identification failure: B/C exposure was constant in the calibration sample, received zero coefficient, and the optimizer introduced unpriced waits. All six `joint_cal` builds failed acceptance and their exact losses rose to 1.54–4.59e-4. These failed measurements are retained. `joint_safe` adds a lexicographic ALAP tie-break over preparation, prefix, and move times at the same primary proxy optimum. The fit is not validated for separate blocks. “OPTIMAL” below means optimal for the named bounded proxy model, never globally optimal infidelity. Placement-model horizons are R≤60. No UNKNOWN result is called UNSAT.

| Embedding class | Block option | Moves | Solver status | Proxy objective | Built? | Exact total | Receipt |
|---|---|---|---|---:|---|---:|---|
| all six (48 embeddings) | standard 9-CX graph | no intra-encoder routing | INFEASIBLE (embedding enumeration) | — | no | — | [geometry](geometry.json) |
| r0c0 | separate l5_11; fixed L5 endpoints | data ≤3/wire; block ≤3/wire | INFEASIBLE | — | no | — | [free2d_fixed_h3](free2d_fixed_h3.receipt.json) |
| r0c0 | separate l5_11 | data ≤2/wire; block ≤2/wire | TIMEOUT | — | no | — | [free2d_h2](free2d_h2.receipt.json) |
| r0c0 | separate l5_11 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r0c0_l5_11](free2d_r0c0_l5_11.receipt.json) |
| r0c0 | separate l5_12 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r0c0_l5_12](free2d_r0c0_l5_12.receipt.json) |
| r0c1 | separate l5_11 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r0c1_l5_11](free2d_r0c1_l5_11.receipt.json) |
| r0c1 | separate l5_12 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r0c1_l5_12](free2d_r0c1_l5_12.receipt.json) |
| r1c0 | separate l5_11 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r1c0_l5_11](free2d_r1c0_l5_11.receipt.json) |
| r1c0 | separate l5_12 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r1c0_l5_12](free2d_r1c0_l5_12.receipt.json) |
| r1c1 | separate l5_11 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r1c1_l5_11](free2d_r1c1_l5_11.receipt.json) |
| r1c1 | separate l5_12 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r1c1_l5_12](free2d_r1c1_l5_12.receipt.json) |
| r2c0 | separate l5_11 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r2c0_l5_11](free2d_r2c0_l5_11.receipt.json) |
| r2c0 | separate l5_12 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r2c0_l5_12](free2d_r2c0_l5_12.receipt.json) |
| r2c1 | separate l5_11 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r2c1_l5_11](free2d_r2c1_l5_11.receipt.json) |
| r2c1 | separate l5_12 | data ≤2/wire; block ≤1/wire | INFEASIBLE | — | no | — | [free2d_r2c1_l5_12](free2d_r2c1_l5_12.receipt.json) |
| r0c0 | joint82 + l5_11 | 6 data; 0 block | OPTIMAL | 5073.0 | yes | 7.8328000e-05 | [free_joint](free_joint.receipt.json) |
| r0c0 | separate l5_11 | data ≤2/wire; block ≤2/wire | TIMEOUT | — | no | — | [free_sep_calibrated](free_sep_calibrated.receipt.json) |
| r0c0 | joint82 + l5_11; GL(3,2) labels; ALAP tie | 6 data; 0 block | FEASIBLE | 5073 | yes | 7.8335000e-05 | [joint_auto](joint_auto.receipt.json) |
| r0c0 | joint82 + l5_11 | 6 data; 0 block | OPTIMAL | 486660.0 | yes | 1.7850500e-04 | [joint_cal_r0c0](joint_cal_r0c0.receipt.json) |
| r0c1 | joint82 + l5_11 | 9 data; 0 block | OPTIMAL | 538917.0 | yes | 2.4473600e-04 | [joint_cal_r0c1](joint_cal_r0c1.receipt.json) |
| r1c0 | joint82 + l5_11 | 6 data; 0 block | OPTIMAL | 486660.0 | yes | 1.6513800e-04 | [joint_cal_r1c0](joint_cal_r1c0.receipt.json) |
| r1c1 | joint82 + l5_11 | 9 data; 0 block | OPTIMAL | 538917.0 | yes | 4.5859800e-04 | [joint_cal_r1c1](joint_cal_r1c1.receipt.json) |
| r2c0 | joint82 + l5_11 | 7 data; 0 block | OPTIMAL | 526808.0 | yes | 1.5388100e-04 | [joint_cal_r2c0](joint_cal_r2c0.receipt.json) |
| r2c1 | joint82 + l5_11 | 10 data; 0 block | OPTIMAL | 545795.0 | yes | 1.7480100e-04 | [joint_cal_r2c1](joint_cal_r2c1.receipt.json) |
| r0c0 | joint82 + l5_11; ALAP tie | 6 data; 0 block | OPTIMAL | 486660 | yes | 7.8335000e-05 | [joint_safe_r0c0](joint_safe_r0c0.receipt.json) |
| r0c1 | joint82 + l5_11; ALAP tie | 9 data; 0 block | OPTIMAL | 538917 | yes | 8.9405900e-05 | [joint_safe_r0c1](joint_safe_r0c1.receipt.json) |
| r1c0 | joint82 + l5_11; ALAP tie | 6 data; 0 block | OPTIMAL | 486660 | yes | 7.8335000e-05 | [joint_safe_r1c0](joint_safe_r1c0.receipt.json) |
| r1c1 | joint82 + l5_11; ALAP tie | 9 data; 0 block | OPTIMAL | 538917 | yes | 8.9405900e-05 | [joint_safe_r1c1](joint_safe_r1c1.receipt.json) |
| r2c0 | joint82 + l5_11; ALAP tie | 7 data; 0 block | OPTIMAL | 526808 | yes | 8.1852600e-05 | [joint_safe_r2c0](joint_safe_r2c0.receipt.json) |
| r2c1 | joint82 + l5_11; ALAP tie | 10 data; 0 block | OPTIMAL | 545795 | yes | 8.7930600e-05 | [joint_safe_r2c1](joint_safe_r2c1.receipt.json) |
| r0c0 | separate l5_11; GL(3,2) labels; early A | data ≤2/wire; block ≤1/wire | TIMEOUT | — | no | — | [sep_auto_h1](sep_auto_h1.receipt.json) |
| r0c0 | separate l5_11; early A | data ≤2/wire; block ≤2/wire | TIMEOUT | — | no | — | [sep_early_a](sep_early_a.receipt.json) |
| r0c0 | separate l5_11 | data ≤2/wire; block ≤2/wire | TIMEOUT | — | no | — | [sep_r0c0](sep_r0c0.receipt.json) |
| r1c0 | separate l5_11 | data ≤2/wire; block ≤2/wire | TIMEOUT | — | no | — | [sep_r1c0](sep_r1c0.receipt.json) |
| r0c0, retained L5 | joint82 + 12-CX A; reuse=1; alap | 6 data; 0 block | OPTIMAL | -8872.0 | yes | 8.0554000e-05 | [joint_exactA_alap](joint_exactA_alap.json) |
| r0c0, retained L5 | joint82 + 11-CX A; reuse=2; alap | 6 data; 0 block | OPTIMAL | -8886.0 | yes | 7.4752100e-05 | [joint_reuse2_alap](joint_reuse2_alap.json) |
| r0c0, retained L5 | joint82 + 11-CX A; reuse=1; alap | 6 data; 0 block | OPTIMAL | -8916.0 | yes | 7.4686900e-05 | [joint_reuse_alap](joint_reuse_alap.json) |
| r0c0, retained L5 | joint82 + 11-CX A; reuse=1; idle | 6 data; 0 block | OPTIMAL | 1394.0 | yes | 7.8209500e-05 | [joint_reuse_idle](joint_reuse_idle.json) |

The binding cut for the fixed-label, one-teleport models is the encoder-to-round geometry: an independent placement-only relaxation already returns INFEASIBLE at r0c0 ([receipt](geometry_h1_l5_11.json)), while two teleports admit a geometric witness ([receipt](geometry_h2_l5_11.json)). The full one-teleport time models prove infeasibility in each of the six classes for both tested A templates. These statements do not include the later code-label-permutation branch. Timed two-teleport searches, including calibrated and early-A variants, are reported at their actual termination status; their timeouts do not establish a physical obstruction.

## Full circuits

R lists A coupling / last B→data CX, measured from `tprep.noise.schedule`. “3rd” is the third-order increment. Exact totals are used only for |c1|<1e-12. exp(-A1) is an acceptance **estimate**. Every listed circuit received `tprep.check(..., shots=10**6, seed=0)`; only full MC finalists receive a final performance rank. MC seeds are 0 / 1000 / 2000 at 1e8 shots each.

| Circuit | R native | CX | c1 | 2nd | 3rd | Exact total | exp(-A1), estimate | MC seeds | MC mean | Seed-0 acceptance, 1e8 | Judge 1e6 | Files |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---|
| joint_reuse2_alap | 45 / 46 | 203 | 2.9236000e-19 | 5.5646800e-05 | 1.9105300e-05 | 7.4752100e-05 | 5.3476000e-01 | 7.5448361e-05 / 7.4562589e-05 / 7.6091324e-05 | 7.5367425e-05 | 0.53486914 | PASS | [qasm](joint_reuse2_alap.qasm), [json](joint_reuse2_alap.json), [check](joint_reuse2_alap.check.log), [scores](joint_reuse2_alap.score.json) |
| joint_reuse_alap | 45 / 46 | 203 | 2.9236000e-19 | 5.5646800e-05 | 1.9040100e-05 | 7.4686900e-05 | 5.3494000e-01 | 7.6689710e-05 / 7.4834880e-05 / 7.7110280e-05 | 7.6211623e-05 | 0.53501000 | PASS | [qasm](joint_reuse_alap.qasm), [json](joint_reuse_alap.json), [check](joint_reuse_alap.check.log), [scores](joint_reuse_alap.score.json) |
| joint_reuse_idle | 45 / 46 | 203 | 2.3315000e-19 | 5.5815100e-05 | 2.2394400e-05 | 7.8209500e-05 | 5.6253000e-01 | — | — | — | PASS | [qasm](joint_reuse_idle.qasm), [json](joint_reuse_idle.json), [check](joint_reuse_idle.check.log), [scores](joint_reuse_idle.score.json) |
| free_joint | 46 / 47 | 201 | 2.9236000e-19 | 5.8288200e-05 | 2.0039700e-05 | 7.8328000e-05 | 5.3572000e-01 | — | — | — | PASS | [qasm](free_joint.qasm), [json](free_joint.json), [check](free_joint.check.log), [scores](free_joint.score.json) |
| joint_auto | 46 / 47 | 201 | 2.9236000e-19 | 5.8288200e-05 | 2.0046800e-05 | 7.8335000e-05 | 5.3570000e-01 | — | — | — | PASS | [qasm](joint_auto.qasm), [json](joint_auto.json), [check](joint_auto.check.log), [scores](joint_auto.score.json) |
| joint_safe_r0c0 | 46 / 47 | 201 | 2.9236000e-19 | 5.8288200e-05 | 2.0046800e-05 | 7.8335000e-05 | 5.3570000e-01 | — | — | — | PASS | [qasm](joint_safe_r0c0.qasm), [json](joint_safe_r0c0.json), [check](joint_safe_r0c0.check.log), [scores](joint_safe_r0c0.score.json) |
| joint_safe_r1c0 | 46 / 47 | 201 | 2.9236000e-19 | 5.8288200e-05 | 2.0046800e-05 | 7.8335000e-05 | 5.3570000e-01 | — | — | — | PASS | [qasm](joint_safe_r1c0.qasm), [json](joint_safe_r1c0.json), [check](joint_safe_r1c0.check.log), [scores](joint_safe_r1c0.score.json) |
| joint_exactA_alap | 45 / 46 | 204 | 2.9236000e-19 | 5.5085000e-05 | 2.5469000e-05 | 8.0554000e-05 | 5.3127000e-01 | — | — | — | PASS | [qasm](joint_exactA_alap.qasm), [json](joint_exactA_alap.json), [check](joint_exactA_alap.check.log), [scores](joint_exactA_alap.score.json) |
| joint_safe_r2c0 | 48 / 49 | 203 | 2.3315000e-19 | 5.8390900e-05 | 2.3461700e-05 | 8.1852600e-05 | 5.2629000e-01 | — | — | — | PASS | [qasm](joint_safe_r2c0.qasm), [json](joint_safe_r2c0.json), [check](joint_safe_r2c0.check.log), [scores](joint_safe_r2c0.score.json) |
| joint_safe_r2c1 | 49 / 50 | 209 | -5.9212000e-20 | 6.2498600e-05 | 2.5432100e-05 | 8.7930600e-05 | 5.1619000e-01 | — | — | — | PASS | [qasm](joint_safe_r2c1.qasm), [json](joint_safe_r2c1.json), [check](joint_safe_r2c1.check.log), [scores](joint_safe_r2c1.score.json) |
| joint_safe_r0c1 | 49 / 50 | 207 | 2.3315000e-19 | 6.2903400e-05 | 2.6502500e-05 | 8.9405900e-05 | 5.1945000e-01 | — | — | — | PASS | [qasm](joint_safe_r0c1.qasm), [json](joint_safe_r0c1.json), [check](joint_safe_r0c1.check.log), [scores](joint_safe_r0c1.score.json) |
| joint_safe_r1c1 | 49 / 50 | 207 | 2.3315000e-19 | 6.2903400e-05 | 2.6502500e-05 | 8.9405900e-05 | 5.1945000e-01 | — | — | — | PASS | [qasm](joint_safe_r1c1.qasm), [json](joint_safe_r1c1.json), [check](joint_safe_r1c1.check.log), [scores](joint_safe_r1c1.score.json) |
| joint_cal_r2c0 | 48 / 49 | 203 | -2.2565000e-17 | 1.0172500e-04 | 5.2156200e-05 | 1.5388100e-04 | 4.6232000e-01 | — | — | — | FAIL | [qasm](joint_cal_r2c0.qasm), [json](joint_cal_r2c0.json), [check](joint_cal_r2c0.check.log), [scores](joint_cal_r2c0.score.json) |
| joint_cal_r1c0 | 46 / 47 | 201 | 2.9236000e-19 | 1.0621700e-04 | 5.8920700e-05 | 1.6513800e-04 | 4.5702000e-01 | — | — | — | FAIL | [qasm](joint_cal_r1c0.qasm), [json](joint_cal_r1c0.json), [check](joint_cal_r1c0.check.log), [scores](joint_cal_r1c0.score.json) |
| joint_cal_r2c1 | 49 / 50 | 209 | -4.0708000e-20 | 1.0307900e-04 | 7.1722100e-05 | 1.7480100e-04 | 4.3733000e-01 | — | — | — | FAIL | [qasm](joint_cal_r2c1.qasm), [json](joint_cal_r2c1.json), [check](joint_cal_r2c1.check.log), [scores](joint_cal_r2c1.score.json) |
| joint_cal_r0c0 | 46 / 47 | 201 | 2.9236000e-19 | 1.1754200e-04 | 6.0963300e-05 | 1.7850500e-04 | 4.5264000e-01 | — | — | — | FAIL | [qasm](joint_cal_r0c0.qasm), [json](joint_cal_r0c0.json), [check](joint_cal_r0c0.check.log), [scores](joint_cal_r0c0.score.json) |
| joint_cal_r0c1 | 49 / 50 | 207 | 2.3315000e-19 | 1.6018800e-04 | 8.4547700e-05 | 2.4473600e-04 | 4.2564000e-01 | — | — | — | FAIL | [qasm](joint_cal_r0c1.qasm), [json](joint_cal_r0c1.json), [check](joint_cal_r0c1.check.log), [scores](joint_cal_r0c1.score.json) |
| joint_cal_r1c1 | 49 / 50 | 207 | 2.3315000e-19 | 3.4485400e-04 | 1.1374400e-04 | 4.5859800e-04 | 3.9176000e-01 | — | — | — | FAIL | [qasm](joint_cal_r1c1.qasm), [json](joint_cal_r1c1.json), [check](joint_cal_r1c1.check.log), [scores](joint_cal_r1c1.score.json) |

## Verification and limits

- Every generated QASM has sibling metadata with `data_qubits`. The emitter checks every native unit against its requested layer after removing empty global layers; the retained-joint scheduler checks exact native timing equality. [manifest.json](manifest.json) records delivered hashes and native depths.
- Prefix operation provenance is preserved through rescheduling. Native MX folding is retained with `h; measure; h` when the measured physical cell is reused. Full judge correctness checks detector determinism and the actual output state.
- The separate-block emitter implements teleport frames, but a successful separate-block full circuit was not established by the completed searches. Those frame paths remain unverified by a full judge build unless a separate candidate appears in the table above.
- The 15 alternative phase-polynomial prefix forms, additional encoder families, more routing depth, and a general interleaving of encoder CXs with moves remain open. The model moves each wire only after its last encoder CX, and treats each prefix wire as busy from first to last prefix operation; it does not reuse gaps between prefix resets. Early A is tested after that data wire’s prefix operations, rather than commuting it through its final T-dagger.
- All CPU work used zebra (≤8 lane cores) or sunfish (≤24), with BLAS/OpenMP fixed to one and explicit CP-SAT workers. Subprocess exits, not output-file creation, controlled sequencing. No active FREELAY job is intentionally left running at handoff.

Reproduction: use the environment `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1` and the project `.venv/bin/python`. `joint_schedule.py --out joint_reuse2_alap --reuse 2 --mode alap` builds the delivery; `evaluate.py joint_reuse2_alap 8 --mc` runs the complete verification. The first finalist also uses the requested unchanged `MAIN/spec/mc3.py`; the second evaluator calls the same `fast_check.check` chunk implementation and seeds, saving full-precision receipts.
