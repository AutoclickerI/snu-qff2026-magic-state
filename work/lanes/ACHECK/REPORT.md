# ACHECK

**Completed: [best.qasm](best.qasm) and [best.json](best.json), sourced from `verify_2_9_15`.** The 3-seed 1e8-shot mean is **7.34312063185213e-5**, 2.57% below v19’s 7.536742492e-5. Seed-0 acceptance is **0.53238408**. The circuit passes all four judge checks at 1e6 shots, retains 203 CX and native round step 45, and satisfies the first completion branch.

The winner retains the existing A encoder, reuses the already-postselected MX state of q1, replaces A’s q16 reset with a Z measurement and its detector, and adds deterministic MX checks immediately after RX initialization on q2, q9, and q15. The whole circuit is rescheduled ALAP with the native per-wire dependencies retained. Every extra measurement has an explicit detector; the existing output frame is unchanged.

All loss numbers are 1−F at p=0.001. Exact totals include the isolated cubic increment and are used only for |c1 p| < 1e-12. exp(−A1) is an acceptance **estimate**. Every circuit in the fixes table was run through unmodified `tprep.check(..., shots=10**6, seed=0)`; its verdict and actual acceptance are retained. No submission, commit, push, credential access, or sub-agent was used.

A’s loss decomposition, using the judge’s native schedule and channel provenance. Each ablation switches off just the named channels; differences overlap and must not be added. Pair terms below credit the full pair to a family whenever it participates (so within-A pairs appear in both families). The original 20-unit region contains 18 A encoder operations plus two data-hop initializations; this analysis separates those and includes A’s actual readout.

| A fault family | Pair loss involving family | Largest pair partners (loss) | Cubic loss removed | Loss removed through third order | Share of full v19 loss |
|---|---:|---|---:|---:|---:|
| Encoder CX | 1.294988e-05 | pre_idle: 3.208588e-06; data_idle: 2.467433e-06; BC_gate: 2.004444e-06; round_gate: 1.484444e-06 | 2.198407e-06 | 1.514828e-05 | 20.26% |
| Encoder initialization | 4.833333e-07 | A_CX: 4.666667e-07; pre_gate: 1.666667e-08 | 1.924382e-06 | 2.407716e-06 | 3.22% |
| A idle after initialization | 1.011514e-06 | A_CX: 9.754106e-07; pre_gate: 2.221481e-08; pre_idle: 1.388889e-08 | 2.591261e-06 | 3.602776e-06 | 4.82% |
| A readout, including shared C→A re-encoding | 6.482748e-07 | pre_idle: 2.911119e-07; BC_gate: 1.6e-07; pre_gate: 1.083333e-07; BC_idle: 8.882963e-08 | 1.072477e-06 | 1.720752e-06 | 2.30% |
| All four A families together | — | overlapping pairs and triples | 7.285299e-06 | 2.093622e-05 | 28.01% |

`pre_idle` includes data gaps ending at a prefix operation, especially the final T_DAG. `data_idle` denotes later data gaps owned by hops or the round. `A_readout` includes the joint two-qubit noise of C17→A16; it is not an attribution to A alone within that shared channel.

The leading pair is a Z/Y idle on data cell 10 at native steps 31–44 with a late A encoder fault (for example ZZ after CX 1→2 at step 44), contributing 3.0842914e-7 per listed Pauli pair. The analogous cell-0 idle at 30–43 pairs with the 8→14 / 14→15 branch. These form a logical Z from A’s weight-two Z class plus the missing data error. Leading positive weight-three sets include Z on A cell 9 during steps 40–44 with Z idles on data cells 3 and 0 (3.8094160e-8); pivot initialization plus two data idles also appears. Top triples are positive weight-three terms, **not** the normalized cubic contribution; the exact cubic term includes the pair-times-other-channel correction. Full labels, pair aggregation, and ablations: [mechanism.json](mechanism.json).

Fixes. Extra CX and occupied cells are relative to v19; a borrowed B/C flag cell and the internal A15 checker add no physical cells. “3rd” is the isolated cubic increment. Native round step and one-million-shot acceptance expose timing and acceptance costs.

| Method / circuit | Extra CX / cells | R | c1 p | 2nd | 3rd | Exact total | exp(−A1), estimate | Judge 1e6 / acceptance |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| v19 control: [base](base.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.56468e-05 | 1.91053e-05 | 7.47521e-05 | 0.53476 | PASS / 0.534164 |
| MX reuse q1: [init_1](init_1.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.55468e-05 | 1.87935e-05 | 7.43402e-05 | 0.53443 | PASS / 0.53413 |
| MX reuse q2: [init_2](init_2.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.56468e-05 | 1.89768e-05 | 7.46236e-05 | 0.53459 | PASS / 0.534363 |
| MX reuse q1/q2: [init_1_2](init_1_2.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.55468e-05 | 1.86677e-05 | 7.42144e-05 | 0.53425 | PASS / 0.534769 |
| M-init q16: [init_16](init_16.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.56468e-05 | 1.87646e-05 | 7.44114e-05 | 0.53426 | PASS / 0.534281 |
| combined reuse/init: [reuse_1_2_16](reuse_1_2_16.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.55468e-05 | 1.83298e-05 | 7.38766e-05 | 0.53375 | PASS / 0.533147 |
| RX→H q9: [init_9](init_9.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.78859e-05 | 1.94588e-05 | 7.73447e-05 | 0.53409 | PASS / 0.533934 |
| RX→H q15: [init_15](init_15.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.93157e-05 | 1.90554e-05 | 7.83711e-05 | 0.5348 | PASS / 0.534477 |
| R→H q8: [reuse_8](reuse_8.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.66312e-05 | 1.92289e-05 | 7.58601e-05 | 0.53338 | PASS / 0.533064 |
| RX then MX: [pivot_9](pivot_9.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.55579e-05 | 1.89796e-05 | 7.45375e-05 | 0.53387 | PASS / 0.533802 |
| RX then MX: [pivot_15](pivot_15.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.48977e-05 | 1.94068e-05 | 7.43044e-05 | 0.53459 | PASS / 0.533784 |
| RX then MX: [pivot_9_15](pivot_9_15.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.48088e-05 | 1.92788e-05 | 7.40876e-05 | 0.5337 | PASS / 0.533209 |
| RX then MX: [pivot_1_2_9_15](pivot_1_2_9_15.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.47478e-05 | 1.91606e-05 | 7.39084e-05 | 0.53279 | PASS / 0.533015 |
| reuse + measured init: [combo_9_15](combo_9_15.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.47364e-05 | 1.84983e-05 | 7.32347e-05 | 0.53269 | PASS / 0.532971 |
| reuse + measured init: [combo_9_15_8](combo_9_15_8.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.47364e-05 | 1.84496e-05 | 7.3186e-05 | 0.53181 | PASS / 0.531436 |
| reuse + measured init: [combo_9_15_14](combo_9_15_14.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.49562e-05 | 1.85948e-05 | 7.3551e-05 | 0.53233 | PASS / 0.532506 |
| reuse + measured init: [combo_9_15_8_14](combo_9_15_8_14.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.49562e-05 | 1.85461e-05 | 7.35023e-05 | 0.53144 | PASS / 0.531248 |
| verified pivots + q16 M-init: [verify_9_15](verify_9_15.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.47364e-05 | 1.86232e-05 | 7.33596e-05 | 0.53287 | PASS / 0.532654 |
| verified pivots + q16 M-init: [verify_2_9_15](verify_2_9_15.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.47364e-05 | 1.84978e-05 | 7.32342e-05 | 0.53233 | PASS / 0.531087 |
| verified pivots + q16 M-init: [verify_1_2_9_15](verify_1_2_9_15.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.47478e-05 | 1.88168e-05 | 7.35645e-05 | 0.5323 | PASS / 0.532172 |
| in-situ encoder: [enc_214](enc_214.qasm) | +2 / +0 | 45 | 2.9236e-19 | 5.22968e-05 | 2.41842e-05 | 7.6481e-05 | 0.53127 | PASS / 0.531153 |
| in-situ encoder: [enc_000](enc_000.qasm) | +1 / +0 | 45 | 2.9236e-19 | 5.5085e-05 | 2.55632e-05 | 8.06481e-05 | 0.53109 | PASS / 0.53077 |
| borrowed-cell flag: [flag_00](flag_00.qasm) | +4 / +0 | 65 | 2.9236e-19 | 7.33309e-05 | 0.000168773 | 0.000242104 | 0.3809 | FAIL / 0.380054 |
| borrowed-cell flag: [flag_05](flag_05.qasm) | +3 / +0 | 53 | 2.9236e-19 | 5.9664e-05 | 4.08037e-05 | 0.000100468 | 0.47023 | FAIL / 0.470514 |
| borrowed-cell flag: [flag_15](flag_15.qasm) | +4 / +0 | 51 | 2.9236e-19 | 6.23773e-05 | 4.16197e-05 | 0.000103997 | 0.4887 | FAIL / 0.488549 |
| early A coupling: [early_008](early_008.qasm) | +0 / +0 | 45 | 4.2137e-19 | 6.34936e-05 | 1.93956e-05 | 8.28892e-05 | 0.53508 | PASS / 0.534835 |
| early A coupling: [early_032](early_032.qasm) | +0 / +0 | 45 | 3.2934e-19 | 5.80452e-05 | 1.89558e-05 | 7.7001e-05 | 0.53547 | PASS / 0.535794 |
| early A coupling: [early_064](early_064.qasm) | +0 / +0 | 45 | 3.1086e-19 | 5.68468e-05 | 1.90222e-05 | 7.5869e-05 | 0.53512 | PASS / 0.535179 |
| new layout + 3-cell cat: [layout2_alap](layout2_alap.qasm) | +3 / +3 | 51 | 4.0893e-19 | 6.50646e-05 | 3.27526e-05 | 9.78172e-05 | 0.50037 | FAIL / 0.499496 |
| in-situ encoder: [enc_510](enc_510.qasm) | +1 / +0 | 45 | 2.9236e-19 | 5.56435e-05 | 1.90667e-05 | 7.47102e-05 | 0.5348 | PASS / 0.534309 |
| in-situ encoder: [enc_502](enc_502.qasm) | +0 / +0 | 45 | 2.9236e-19 | 5.56468e-05 | 1.91053e-05 | 7.47521e-05 | 0.53476 | PASS / 0.533862 |
| in-situ encoder: [enc_512](enc_512.qasm) | +1 / +0 | 45 | 2.9236e-19 | 5.51274e-05 | 1.98368e-05 | 7.49642e-05 | 0.53558 | PASS / 0.535779 |
| A15 logical-X check: [internal_187](internal_187.qasm) | +3 / +0 | 49 | 2.9236e-19 | 5.65477e-05 | 3.33839e-05 | 8.99316e-05 | 0.50248 | PASS / 0.50225 |
| A15 logical-X check: [internal_072](internal_072.qasm) | +5 / +0 | 50 | 2.9236e-19 | 5.67581e-05 | 3.40955e-05 | 9.08536e-05 | 0.4954 | FAIL / 0.494884 |
| A15 logical-X check: [internal_076](internal_076.qasm) | +5 / +0 | 50 | 2.9236e-19 | 5.67712e-05 | 3.40948e-05 | 9.08659e-05 | 0.4954 | FAIL / 0.494961 |

All detailed scores, including additional encoder and init variants, are in [scores.json](scores.json). `init_8`, `init_8_16`, and `init_1_2_8_16` fail noiseless detector determinism: the reused hop leaves q8 in |+⟩, so its proposed Z measure-init is random. The corrected H-based q8 variant is `reuse_8`, which passes and loses. These failures were not patched by dropping detectors.

Finalists: 1e8 shots for each of seeds 0, 1000, 2000, using the judge’s unmodified chunk arithmetic through `fast_check.check`. Ranking uses only the three-seed mean and requires seed-0 acceptance ≥0.505 as the practical floor.

| Circuit | Seed 0 | Seed 1000 | Seed 2000 | Mean | Seed-0 acceptance | Files |
|---|---:|---:|---:|---:|---:|---|
| verify_2_9_15 | 7.485198e-05 | 7.239126e-05 | 7.305038e-05 | 7.343121e-05 | 0.5323841 | [QASM](verify_2_9_15.qasm), [JSON](verify_2_9_15.json), [MC](verify_2_9_15.mc.json) |
| v19 reference | 7.5448361e-5 | 7.4562589e-5 | 7.6091324e-5 | 7.536742492e-5 | 0.53486914 | [QASM](base.qasm), [JSON](base.json), [FREELAY receipt](../FREELAY/joint_reuse2_alap.score.json) |

Reference v19 mean supplied and reproduced in FREELAY: 7.536742492e-5, seeds 7.5448361e-5 / 7.4562589e-5 / 7.6091324e-5; seed-0 acceptance 0.53486914. Its identical QASM is retained as `base.qasm` and was separately checked at 1e6 here.

Search boundaries and validation: 521 distinct retained EXENC/FLAG/SCHED encoder paths were built in v19’s full timing model and screened at second order; 33 diverse candidates were checked through third order. Second-order screening is not a final performance rank. All 168 GL(3,2) maps per encoder were tested on the fixed A cell set; only the original physical embeddings survived adjacency. The seven logical-X support geometries are in [automorphism_audit.json](automorphism_audit.json). The common-neighbor support {14,9,16} uses A’s own cell 15; 190 algebraically admissible prefixes were built with its three-CX check before it joins A, choosing the best round/time-sum schedule among all six check orders. Their minimum native R is 49 (maximum 54), with full-circuit shortlist prices in the fixes table. This is not a proof against arbitrary new placements or other dynamic encoders.

The LAYOUT2 cat check was rebuilt with the 19-CX injection prefix and full ALAP scheduling. External flags borrow B/C cells before their preparation and thereby delay the round; their recorded acceptance fails. Early A was moved before final T_DAG where legal, with the native schedule verified; its increased unprotected data exposure outweighed the A idle saving. Logical-X checks on A remain valid in principle; these measurements close only the constructed schedules.

The lane-local [fast_exact.py](fast_exact.py) only rejects fault signatures that flip an identity detector projector; all accepted tables and all pair/triple sums use the original exact2 code. Baseline total agrees with the original evaluator. On four architecture families, 1,800 random single/pair/triple table queries agreed exactly with the unmodified dense engine ([validation](fast_validation.json)); both `combo_9_15_8` and the delivered `verify_2_9_15` were cross-checked with the unmodified exact2 CLI; all reported printed terms match. The requested unmodified `MAIN/spec/mc3.py` was copied verbatim into this lane for owl and rerun on `best`; it reproduces the three seed scores ([receipt](best.mc3.log)). Every emitted native operation is compared with `tprep.noise.schedule`, including folded MX/RX operations.

Runs used owl Docker quotas totaling at most 32 cores and zebra jobs with at most three workers, with OMP/BLAS/MKL threads fixed to one. MC jobs for `init_1_2`, `reuse_1_2_16`, and `combo_9_15_8` were stopped by explicit PID/container ID before a complete seed result, after selecting the verified-q2 implementation. Their means remain unmeasured, and no partial draw is used in ranking. `combo_9_15_8` has the slightly lower exact estimate 7.31860e-5, but direct q2 MX reuse made sampling much slower; the delivered reset-then-MX alternative has exact 7.32342e-5 and completed all three MC seeds. This is a screening decision, not a measured MC comparison between those two circuits. Artifacts and useful completed checks are retained. No claim of global optimality or of a statistically established true-mean improvement follows from three seeds alone.

Reproduction: with OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1, run the project `.venv/bin/python work/lanes/ACHECK/build_best.py`. The resulting `replay.qasm` is asserted byte-identical to `best.qasm`; `best.json` includes native prefix provenance, data_qubits, exact scores, all MC seeds, and the SHA-256. All lane processes were finished or explicitly stopped at handoff.
