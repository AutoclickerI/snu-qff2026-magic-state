# Detector lane report

At p = 10^-3, neither target has an undeclared independent deterministic parity. The full declared span remains best among the third-order finalists and the measured MC candidates. Dropping `c[3]` frees acceptance with a very small loss cost. For the present circuits, retain the full span to minimize loss; the `c[3]` variants provide acceptance headroom.

All files are under `work/lanes/DET/`. No submission was made. All emitted QASM files passed `tprep.check(..., shots=10**6, seed=0)` for format, class, correctness, and acceptance. Monte Carlo below uses `work/fast_check.check`, 10^8 shots per seed, seeds 0, 1000, 2000, 22 worker processes on hippo (23 including its parent), with BLAS/OpenMP threads capped at one. Zebra initially used eight workers plus the parent; a transient total-load spike to 50.27/64 was observed and the lane restarted with at most four workers. Completed checkpoints were retained.

## Deterministic parity space and judge semantics

| Target | Measurement records | Declared lines | Declared rank | Full deterministic rank | Missing independent parities | Quotient representatives checked |
|---|---:|---:|---:|---:|---:|---:|
| v12 | 22 | 23 | 20 | 20 | 0 | 4 |
| cand2 | 35 | 24 | 24 | 24 | 0 | 2048 |

The proof uses the judge’s own `tprep.exact.run` deferred-measurement state, retaining all 15 T/T† rotations. First, row-reduce the already verified detector parities. Then enumerate every coset of their span in the full measurement-record parity space and evaluate the exact Pauli expectation. Multiplication by a declared deterministic parity preserves the absolute expectation, so one representative per coset is sufficient. Every nontrivial coset representative has expectation **0**, far from the judge’s `abs(abs(expectation)-1) <= 1e-9` criterion. This proves completeness, not merely completeness of a Clifford surrogate. See [v12_space.json](v12_space.json), [cand2_space.json](cand2_space.json), and [audit.json](audit.json).

The QASM converter resolves classical bit names to measurement records and places each `DETECTOR` after its latest referenced measurement. A noiseless parity of either 0 or 1 is valid; the detector compares against that reference. `POSTSELECT(v)` compares the raw record parity to v, and can make an otherwise random detector conditionally deterministic. Both targets have no POSTSELECT and their actual auto frames are `X=(0,[])`, `Z=(0,[])`. No frame or postselection changes were made. Adding any parity within the existing deterministic span cannot change accepted shots. v12 has three duplicate `c[7]` declarations; [v12_dedup.qasm](v12_dedup.qasm) removes them while retaining rank 20.
The duplicate-free v12 is bit-identical to the original in score, SEM, and acceptance at all three 10^8-shot seeds. [emitted_audit.json](emitted_audit.json) independently confirms that all 20 emitted circuits declare exactly the intended subspaces; their quantum-operation text is unchanged.

Primary implementation sources: [QASM conversion](../../../upstream/snu-qff2026-problem/tprep/qasm.py), [exact determinism check](../../../upstream/snu-qff2026-problem/tprep/exact.py), [frame, postselection and scoring](../../../upstream/snu-qff2026-problem/tprep/check.py).

## Search and exact validation

The search reuses `exact2.Eval` fault signatures and `Engine` expectations. It accumulates joint detector-syndrome probability and logical-loss mass for every single fault and every unordered pair from distinct noise channels. A subspace then accepts a linear kernel in that joint syndrome space. This preserves the exact normalized first- and second-order coefficients, including single-loss normalization terms. The unchanged cases reproduce the supplied numbers. Ten independently rebound `exact2.run` evaluations agree with histogram rescoring to at most 3.4e-16 absolute.

Enumerated: each generator removal; every coordinate removal set of size 2, 3, or 4; every subspace supported on at most four generator coordinates; and every one-dimensional relaxed syndrome kernel that has nonzero mass through second order, at any Hamming weight. Unlisted syndrome sectors have zero effect at these orders. Multi-start greedy search extends promising kernels. All reported fronts enforce first-order loss < 1e-14; finalists actually remain around 5e-19. There are no missing independent parities to add. This is exhaustive for the stated neighborhoods, not a claim of global optimality over all subspaces at all fault orders.

Finalists use `exact2.run(third=True)` and `exact2.third_order`. A local acceleration rejects only detector outcomes outside the exact joint spectrum before calling the same loss engine; baseline weight-three terms agree with the original implementation within 5.5e-20. See [acceleration_audit.json](acceleration_audit.json). `exp(-A1)` is an acceptance estimate; judge MC acceptance is listed separately. “Through third” means the sum of orders one, two and three.

## v12

The search retained 141,832 distinct first-order-safe subspaces. It represented 48,986 syndrome sectors through second order. Full counts and every single-generator result are in [v12_search.json](v12_search.json).

| Change | Exact second | Through third | First order | exp(-A1) |
|---|---:|---:|---:|---:|
| full declared span | 1.1219494707e-04 | 1.1431328313e-04 | 4.903e-19 | 0.690524522 |
| drop `c[3]` | 1.1219494707e-04 | 1.1432189970e-04 | 4.903e-19 | 0.698740069 |
| drop `c[7] XOR c[10]` | 1.1221772484e-04 | 1.1470159306e-04 | 4.903e-19 | 0.693930913 |
| drop `c[3]`, `c[7] XOR c[10]` | 1.1221772484e-04 | 1.1471021148e-04 | 4.903e-19 | 0.702186989 |
| drop `c[1]` | 1.1268035824e-04 | 1.1499710864e-04 | 4.903e-19 | 0.692183771 |
| drop `c[5]` | 1.1279439151e-04 | 1.1519381566e-04 | 4.903e-19 | 0.694725511 |
| drop `c[1]`, `c[3]`, `c[7] XOR c[10]` | 1.1270313602e-04 | 1.1540534718e-04 | 4.903e-19 | 0.703874262 |
| drop `c[5]`, `c[3]`, `c[7] XOR c[10]` | 1.1281939151e-04 | 1.1561014517e-04 | 4.903e-19 | 0.706458930 |
| drop `c[5]`, `c[1]`, `c[3]`, `c[7] XOR c[10]` | 1.1415910275e-04 | 1.1730524482e-04 | 4.903e-19 | 0.708487018 |

### Through-third-order Pareto front among finalists

| Change | Through third | exp(-A1) |
|---|---:|---:|
| full declared span | 1.1431328313e-04 | 0.690524522 |
| drop `c[3]` | 1.1432189970e-04 | 0.698740069 |
| drop `c[3]`, `c[7] XOR c[10]` | 1.1471021148e-04 | 0.702186989 |
| drop `c[1]`, `c[3]`, `c[7] XOR c[10]` | 1.1540534718e-04 | 0.703874262 |
| drop `c[5]`, `c[3]`, `c[7] XOR c[10]` | 1.1561014517e-04 | 0.706458930 |
| drop `c[5]`, `c[1]`, `c[3]`, `c[7] XOR c[10]` | 1.1730524482e-04 | 0.708487018 |

### Monte Carlo: 10^8 shots per seed

| Candidate | Seed 0 | Seed 1000 | Seed 2000 | 3-seed mean | Mean acceptance |
|---|---:|---:|---:|---:|---:|
| [v12_base](v12_base.qasm) | 1.1465095876e-04 | 1.1322617254e-04 | 1.1193501605e-04 | 1.1327071578e-04 | 0.690454670 |
| [v12_dedup](v12_dedup.qasm) | 1.1465095876e-04 | 1.1322617254e-04 | 1.1193501605e-04 | 1.1327071578e-04 | 0.690454670 |
| [v12_drop_c3](v12_drop_c3.qasm) | 1.1471994416e-04 | 1.1324042547e-04 | 1.1196471954e-04 | 1.1330836306e-04 | 0.698712420 |
| [v12_drop_c7c10](v12_drop_c7c10.qasm) | 1.1518031271e-04 | 1.1343110948e-04 | 1.1248571552e-04 | 1.1369904590e-04 | 0.693878257 |
| [v12_drop_c3_c7c10](v12_drop_c3_c7c10.qasm) | 1.1524309978e-04 | 1.1344335677e-04 | 1.1250216042e-04 | 1.1372953899e-04 | 0.702177250 |

The ordering above uses the three-seed mean; seed 0 is retained separately because it is the judge’s submission key. MC uncertainty per seed is about 1.1e-6 for v12 and 1.3e-6 for cand2. Small differences should not be described as proven improvements.

### Loss/acceptance Pareto front through second order

These are the nondominated points among all searched first-order-safe subspaces, using exact second-order loss and exp(-A1). The search JSON gives the exact generator vectors. For a non-coordinate change, `kernel span {hex masks}` specifies the admitted full-detector syndromes; detector generators are its GF(2) orthogonal complement. Bit j refers to `full_records[j]` / `independent_clbits[j]` in the parity-space JSON.

| Change | Detector rank | Exact second | exp(-A1) |
|---|---:|---:|---:|
| drop `c[3]` | 19 | 1.1219494707e-04 | 0.698740069 |
| drop `c[3]`, `c[7] XOR c[10]` | 18 | 1.1221772484e-04 | 0.702186989 |
| drop `c[1]`, `c[3]`, `c[7] XOR c[10]` | 17 | 1.1270313602e-04 | 0.703874262 |
| drop `c[5]`, `c[3]`, `c[7] XOR c[10]` | 17 | 1.1281939151e-04 | 0.706458930 |
| drop `c[5]`, `c[1]`, `c[3]`, `c[7] XOR c[10]` | 16 | 1.1415910275e-04 | 0.708487018 |
| kernel span {0x4, 0x100, 0x800, 0x48, 0x8} | 15 | 1.1814034254e-04 | 0.709337712 |
| kernel span {0x4, 0x100, 0x800, 0xa, 0x6} | 15 | 1.1835381020e-04 | 0.709858084 |
| kernel span {0x4, 0x100, 0x800, 0x18, 0x8} | 15 | 1.2056335458e-04 | 0.710377891 |
| drop `c[5]`, `c[1]`, `c[3]`, `c[18] XOR c[21]` | 16 | 1.9648909045e-04 | 0.710575223 |
| drop `c[5]`, `c[3]`, `c[7] XOR c[10]`, `c[18] XOR c[21]` | 16 | 2.0885187006e-04 | 0.712036426 |
| drop `c[5]`, `c[3]`, `c[7] XOR c[10]`, `c[17] XOR c[20]` | 16 | 2.4567711610e-04 | 0.712939226 |

### MC Pareto front among measured candidates

| Candidate | 3-seed mean | Mean acceptance |
|---|---:|---:|
| [v12_base](v12_base.qasm) | 1.1327071578e-04 | 0.690454670 |
| [v12_drop_c3](v12_drop_c3.qasm) | 1.1330836306e-04 | 0.698712420 |
| [v12_drop_c3_c7c10](v12_drop_c3_c7c10.qasm) | 1.1372953899e-04 | 0.702177250 |

## cand2

The search retained 259,967 distinct first-order-safe subspaces. It represented 75,605 syndrome sectors through second order. Full counts and every single-generator result are in [cand2_search.json](cand2_search.json).

| Change | Exact second | Through third | First order | exp(-A1) |
|---|---:|---:|---:|---:|
| full declared span | 9.1619341734e-05 | 1.2862556369e-04 | 5.033e-19 | 0.527719162 |
| drop `c[3]` | 9.1619341734e-05 | 1.2867872987e-04 | 5.033e-19 | 0.534346319 |
| drop `c[1]` | 9.1947964154e-05 | 1.2980442772e-04 | 5.033e-19 | 0.528599428 |
| drop `c[11]` | 9.2403471163e-05 | 1.3070231703e-04 | 5.033e-19 | 0.530322427 |
| drop `c[7] XOR c[10]` | 9.2037305577e-05 | 1.3152231884e-04 | 5.033e-19 | 0.530322427 |
| drop `c[3]`, `c[7] XOR c[10]` | 9.2037305577e-05 | 1.3157548673e-04 | 5.033e-19 | 0.536982276 |
| drop `c[1]`, `c[3]`, `c[7] XOR c[10]` | 9.2370372441e-05 | 1.3279945883e-04 | 5.033e-19 | 0.537877993 |
| kernel span {0x40, 0x400, 0x102, 0x202} | 9.2564473202e-05 | 1.3301364615e-04 | 5.033e-19 | 0.537947327 |
| drop `c[13]` | 9.3220888795e-05 | 1.3320772798e-04 | 5.033e-19 | 0.528352805 |
| drop `c[9]` | 9.2974825422e-05 | 1.3444806175e-04 | 5.033e-19 | 0.528458487 |

### Through-third-order Pareto front among finalists

| Change | Through third | exp(-A1) |
|---|---:|---:|
| full declared span | 1.2862556369e-04 | 0.527719162 |
| drop `c[3]` | 1.2867872987e-04 | 0.534346319 |
| drop `c[3]`, `c[7] XOR c[10]` | 1.3157548673e-04 | 0.536982276 |
| drop `c[1]`, `c[3]`, `c[7] XOR c[10]` | 1.3279945883e-04 | 0.537877993 |
| kernel span {0x40, 0x400, 0x102, 0x202} | 1.3301364615e-04 | 0.537947327 |

### Monte Carlo: 10^8 shots per seed

| Candidate | Seed 0 | Seed 1000 | Seed 2000 | 3-seed mean | Mean acceptance |
|---|---:|---:|---:|---:|---:|
| [cand2_base](cand2_base.qasm) | 1.2958960010e-04 | 1.3260353560e-04 | 1.3141923779e-04 | 1.3120412450e-04 | 0.527905050 |
| [cand2_drop_c3](cand2_drop_c3.qasm) | 1.2962840953e-04 | 1.3283414681e-04 | 1.3179309453e-04 | 1.3141855029e-04 | 0.534564290 |
| [cand2_drop_c1](cand2_drop_c1.qasm) | 1.3077435779e-04 | 1.3370636735e-04 | 1.3258202134e-04 | 1.3235424883e-04 | 0.528820590 |
| [cand2_drop_c7c10](cand2_drop_c7c10.qasm) | 1.3273278502e-04 | 1.3571195494e-04 | 1.3438252544e-04 | 1.3427575514e-04 | 0.530549870 |
| [cand2_drop_c3_c7c10](cand2_drop_c3_c7c10.qasm) | 1.3274268994e-04 | 1.3597834591e-04 | 1.3480217697e-04 | 1.3450773761e-04 | 0.537242910 |

The ordering above uses the three-seed mean; seed 0 is retained separately because it is the judge’s submission key. MC uncertainty per seed is about 1.1e-6 for v12 and 1.3e-6 for cand2. Small differences should not be described as proven improvements.

### Loss/acceptance Pareto front through second order

These are the nondominated points among all searched first-order-safe subspaces, using exact second-order loss and exp(-A1). The search JSON gives the exact generator vectors. For a non-coordinate change, `kernel span {hex masks}` specifies the admitted full-detector syndromes; detector generators are its GF(2) orthogonal complement. Bit j refers to `full_records[j]` / `independent_clbits[j]` in the parity-space JSON.

| Change | Detector rank | Exact second | exp(-A1) |
|---|---:|---:|---:|
| drop `c[3]` | 23 | 9.1619341734e-05 | 0.534346319 |
| drop `c[1]`, `c[3]` | 22 | 9.1947964154e-05 | 0.535237639 |
| drop `c[3]`, `c[7] XOR c[10]` | 22 | 9.2037305577e-05 | 0.536982276 |
| drop `c[1]`, `c[3]`, `c[7] XOR c[10]` | 21 | 9.2370372441e-05 | 0.537877993 |
| kernel span {0x40, 0x300, 0x400} | 21 | 9.2564473202e-05 | 0.537947327 |
| drop `c[1]`, `c[3]`, `c[9]`, `c[7] XOR c[10]` | 20 | 9.3734745018e-05 | 0.538631549 |
| drop `c[1]`, `c[3]`, `c[8]`, `c[7] XOR c[10]` | 20 | 9.4328989491e-05 | 0.538703371 |
| drop `c[3]`, `c[8]`, `c[9]`, `c[7] XOR c[10]` | 20 | 9.5887462829e-05 | 0.539527622 |
| drop `c[5]`, `c[3]`, `c[7] XOR c[10]` | 21 | 9.6811966438e-05 | 0.540716128 |
| drop `c[5]`, `c[3]`, `c[9]`, `c[7] XOR c[10]` | 20 | 9.8176339015e-05 | 0.541473661 |
| drop `c[5]`, `c[3]`, `c[8]`, `c[7] XOR c[10]` | 20 | 9.8770583488e-05 | 0.541545862 |
| drop `c[1]`, `c[5]`, `c[3]`, `c[7] XOR c[10]` | 20 | 1.0091894571e-04 | 0.541870887 |
| drop `c[5]`, `c[3]`, `c[7] XOR c[10]`, `c[11]` | 20 | 1.2006716911e-04 | 0.543383508 |
| drop `c[5]`, `c[3]`, `c[7] XOR c[10]`, `c[22] XOR c[23] XOR c[26] XOR c[27]` | 20 | 1.4438342127e-04 | 0.543679654 |
| drop `c[5]`, `c[3]`, `c[6]`, `c[7] XOR c[10]` | 20 | 1.7713331903e-04 | 0.546039925 |
| drop `c[5]`, `c[3]`, `c[6]`, `c[22] XOR c[23] XOR c[26] XOR c[27]` | 20 | 2.2513996558e-04 | 0.546337519 |
| drop `c[5]`, `c[3]`, `c[17] XOR c[18] XOR c[19] XOR c[20]` | 21 | 3.4118547780e-04 | 0.547146624 |
| drop `c[5]`, `c[3]`, `c[7] XOR c[10]`, `c[17] XOR c[18] XOR c[19] XOR c[20]` | 20 | 3.4929883314e-04 | 0.549845725 |
| drop `c[5]`, `c[3]`, `c[17] XOR c[18] XOR c[19] XOR c[20]`, `c[22] XOR c[23] XOR c[26] XOR c[27]` | 20 | 4.1796725263e-04 | 0.550145394 |
| drop `c[5]`, `c[3]`, `c[6]`, `c[17] XOR c[18] XOR c[19] XOR c[20]` | 20 | 4.2542545764e-04 | 0.552533734 |
| kernel span {0x40, 0x10000, 0xa00000} | 21 | 8.5902271207e-04 | 0.554363816 |
| kernel span {0x600000, 0xa00000} | 22 | 1.0776359712e-03 | 0.554664746 |
| kernel span {0x40, 0xa00000, 0xc00000} | 21 | 1.0776715267e-03 | 0.561630289 |
| kernel span {0x10000, 0xa00000, 0xc00000} | 21 | 1.9004678921e-03 | 0.564180347 |

### MC Pareto front among measured candidates

| Candidate | 3-seed mean | Mean acceptance |
|---|---:|---:|
| [cand2_base](cand2_base.qasm) | 1.3120412450e-04 | 0.527905050 |
| [cand2_drop_c3](cand2_drop_c3.qasm) | 1.3141855029e-04 | 0.534564290 |
| [cand2_drop_c3_c7c10](cand2_drop_c3_c7c10.qasm) | 1.3450773761e-04 | 0.537242910 |

## Artifact and verification inventory

| Circuit | 10^6-shot check | Acceptance |
|---|---|---:|
| [cand2_base](cand2_base.qasm) ([metadata](cand2_base.json)) | PASS all four gates | 0.527671 |
| [cand2_drop_c1](cand2_drop_c1.qasm) ([metadata](cand2_drop_c1.json)) | PASS all four gates | 0.528577 |
| [cand2_drop_c3](cand2_drop_c3.qasm) ([metadata](cand2_drop_c3.json)) | PASS all four gates | 0.534250 |
| [cand2_drop_c3_c7c10](cand2_drop_c3_c7c10.qasm) ([metadata](cand2_drop_c3_c7c10.json)) | PASS all four gates | 0.536986 |
| [cand2_drop_c7c10](cand2_drop_c7c10.qasm) ([metadata](cand2_drop_c7c10.json)) | PASS all four gates | 0.530375 |
| [cand2_screen_04](cand2_screen_04.qasm) ([metadata](cand2_screen_04.json)) | PASS all four gates | 0.530370 |
| [cand2_screen_05](cand2_screen_05.qasm) ([metadata](cand2_screen_05.json)) | PASS all four gates | 0.528519 |
| [cand2_screen_06](cand2_screen_06.qasm) ([metadata](cand2_screen_06.json)) | PASS all four gates | 0.528333 |
| [cand2_screen_07](cand2_screen_07.qasm) ([metadata](cand2_screen_07.json)) | PASS all four gates | 0.537908 |
| [cand2_screen_08](cand2_screen_08.qasm) ([metadata](cand2_screen_08.json)) | PASS all four gates | 0.537987 |
| [v12_base](v12_base.qasm) ([metadata](v12_base.json)) | PASS all four gates | 0.690309 |
| [v12_dedup](v12_dedup.qasm) ([metadata](v12_dedup.json)) | PASS all four gates | 0.690309 |
| [v12_drop_c3](v12_drop_c3.qasm) ([metadata](v12_drop_c3.json)) | PASS all four gates | 0.698653 |
| [v12_drop_c3_c7c10](v12_drop_c3_c7c10.qasm) ([metadata](v12_drop_c3_c7c10.json)) | PASS all four gates | 0.702162 |
| [v12_drop_c7c10](v12_drop_c7c10.qasm) ([metadata](v12_drop_c7c10.json)) | PASS all four gates | 0.693779 |
| [v12_screen_03](v12_screen_03.qasm) ([metadata](v12_screen_03.json)) | PASS all four gates | 0.694538 |
| [v12_screen_04](v12_screen_04.qasm) ([metadata](v12_screen_04.json)) | PASS all four gates | 0.691993 |
| [v12_screen_05](v12_screen_05.qasm) ([metadata](v12_screen_05.json)) | PASS all four gates | 0.703882 |
| [v12_screen_06](v12_screen_06.qasm) ([metadata](v12_screen_06.json)) | PASS all four gates | 0.706472 |
| [v12_screen_07](v12_screen_07.qasm) ([metadata](v12_screen_07.json)) | PASS all four gates | 0.708515 |

Checked: source hashes, full noiseless parity-space completeness with T rotations, empty frames, baseline exact coefficients, cached rescoring against direct `exact2`, final third-order terms, unchanged quantum operations, all emitted circuit gates at 10^6 shots, and the listed three-seed 10^8-shot MC results. Inferred: acceptance headroom may help another circuit variant; that must be re-evaluated after changing quantum operations. Unverified: global optimality outside the enumerated neighborhoods, and all higher-order coefficients beyond the MC measurements.

Reproduction: run `analyze.py`, `search.py`, `audit.py`, `accelerate.py`, `third_screen.py`, `validate.py <candidate stems>` / `validate.py mc <candidate stems>`, then `report.py`, using the repository venv, cwd `work/lanes/DET/`, `PYTHONDONTWRITEBYTECODE=1`, and all three BLAS/OpenMP thread variables set to 1. `validate.py mc` is configured for hippo’s 22 workers. The original exact evaluator and judge were not modified.
