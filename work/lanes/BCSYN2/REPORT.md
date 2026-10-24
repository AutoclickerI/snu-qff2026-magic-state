# BCSYN2 — clean B+C synthesis and in-situ optimization

Completion gate met by **fb_s401_0035**: 3-seed 1e8-shot MC mean **7.19561100e-05**, versus v20 **7.282e-5** (-1.186%). Seed-0 acceptance 0.54714. The 1e6-shot judge check passes. [best.qasm](best.qasm), [best.json](best.json), [MC receipt](full/fb_s401_0035.mc.log).

3312 full-circuit prices recorded; 3312 pass the 1e6-shot judge check. The complete measured full-circuit table is [full_results.csv](full_results.csv) (circuit files kept for the finalists below only; the main session deleted the rest as regenerable), with loss-sorted structured receipts in [full_results.json](full_results.json). Every QASM has a JSON containing `data_qubits`.

Synthesis budgets below distinguish elapsed solver time, process CPU time, and requested limits. CPU totals are measured from `/proc/<pid>/stat` before any stop. A stopped search is neither UNSAT nor timeout. SAT at cap 74 or 78 follows from independently validated 73-CX and 78-CX witnesses; it does not assert that every long seed found them.

| Formulation | CX cap | depth | budget / measured time | status | witness CX | clean check | in-situ exact total |
|---|---:|---:|---|---|---:|---|---:|
| Reverse endpoint + shared signatures, CaDiCaL CEGAR, endpoint hints | 78 | 14 | 7205 s/seed requested; completed solver 0.0 s; stopped CPU 14753.8 s | SAT witness; 4 STOPPED_CAPACITY, 4 STOPPED_AFTER_MC_WIN | 73 | Stim + BC2 PASS | 8.60636240e-05 |
| Reverse endpoint + shared signatures, CaDiCaL CEGAR, endpoint hints | 74 | 14 | 7205 s/seed requested; completed solver 0.0 s; stopped CPU 14767.4 s | SAT witness; 4 STOPPED_CAPACITY, 4 STOPPED_AFTER_MC_WIN | 73 | Stim + BC2 PASS | 8.60636240e-05 |
| Reverse endpoint + shared signatures, CaDiCaL CEGAR, endpoint hints | 70 | 14 | 7205 s/seed requested; completed solver 0.0 s; stopped CPU 14815.4 s | 4 STOPPED_CAPACITY, 4 STOPPED_AFTER_MC_WIN | — | — | — |
| Reverse endpoint + shared signatures, CaDiCaL CEGAR, endpoint hints | 82 | 13 | 7205 s/seed requested; completed solver 0.0 s; stopped CPU 14830.9 s | 4 STOPPED_CAPACITY, 4 STOPPED_AFTER_MC_WIN | — | — | — |
| Reverse endpoint + shared signatures, CaDiCaL CEGAR, endpoint hints | 78 | 13 | 7205 s/seed requested; completed solver 0.0 s; stopped CPU 14812.6 s | 4 STOPPED_CAPACITY, 4 STOPPED_AFTER_MC_WIN | — | — | — |
| Assumption-based LNS, full clean cuts, known82 seed | 82 | 14 | measured run logs in `runs/lns*.log`; 5,194 witnesses (`runs/lns_witnesses.tar.xz`) / 2,965 distinct wire sequences | SAT | 73–82 | Stim + BC2 PASS | all representative prices in CSV |
| Exact-loss feedback SAT repair, MX init | 82 | 14 | `feedback_s*.log` and price receipts | SAT | 80–82 | Stim + BC2 PASS | 7.10055308e-05 |
| Helper X measurement, endpoint variables on free cells | 74/70/82/78 | 14/13 | 7205 s/seed requested; 8432.65 CPU s across four stopped instances | 4 STOPPED_AFTER_MC_WIN; no witness | — | — | — |
| Known helper-X extension (validation, q32) | 83 | 15 | deterministic construction | SAT | 83 | Stim + BC2 PASS | 9.27222064e-05 |

Final rankings use the MC mean only. Exact totals include the third-order increment and are used only when `abs(c1) < 1e-12`. Native R is measured after emitting the full QASM. MC entries are 1e8 shots at seeds 0, 1000, 2000. A dash means not measured. All listed full circuits below passed the 1e6-shot judge check.

| Full circuit | R (native) | CX | c1 | 2nd | 3rd increment | exact total | exp(-A1) | MC 0 / 1000 / 2000 | MC mean | seed-0 acceptance | files |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| fb_s401_0035 | 45 | 203 | 2.92358730e-19 | 5.25812032e-05 | 1.84243276e-05 | 7.10055308e-05 | 0.547017 | 7.13339600e-05 / 7.16020000e-05 / 7.29323800e-05 | 7.19561100e-05 | 0.54714 | [QASM](full/fb_s401_0035.qasm), [JSON](full/fb_s401_0035.json) |
| fb_s401_0009 | 45 | 203 | 2.92358730e-19 | 5.33345217e-05 | 1.83406846e-05 | 7.16752063e-05 | 0.546944 | 7.30954600e-05 / 7.19878500e-05 / 7.22950600e-05 | 7.24594500e-05 | 0.54702 | [QASM](full/fb_s401_0009.qasm), [JSON](full/fb_s401_0009.json) |
| v20 | 45 | 203 | 2.92358730e-19 | 5.44088166e-05 | 1.86914100e-05 | 7.31002267e-05 | 0.539917 | 7.26094900e-05 / 7.20588000e-05 / 7.37834700e-05 | 7.28172500e-05 | 0.54001 | [QASM](full/v20.qasm), [JSON](full/v20.json) |
| p2134_mx | 45 | 202 | 2.92358730e-19 | 5.35276330e-05 | 1.83695554e-05 | 7.18971884e-05 | 0.547166 | 7.21667100e-05 / 7.40122300e-05 / 7.29003600e-05 | 7.30264300e-05 | 0.54727 | [QASM](full/p2134_mx.qasm), [JSON](full/p2134_mx.json) |
| fb_s401_0026 | 45 | 203 | 2.92358730e-19 | 5.26256328e-05 | 1.84091270e-05 | 7.10347598e-05 | 0.547017 | 7.42625600e-05 / 7.26658100e-05 / 7.26429300e-05 | 7.31904300e-05 | 0.54718 | [QASM](full/fb_s401_0026.qasm), [JSON](full/fb_s401_0026.json) |
| lns_1497_mx | 45 | 201 | 2.92358730e-19 | 5.36888166e-05 | 1.83915667e-05 | 7.20803833e-05 | 0.547090 | 7.33178000e-05 / 7.31138600e-05 / 7.46218000e-05 | 7.36844900e-05 | 0.54714 | [QASM](full/lns_1497_mx.qasm), [JSON](full/lns_1497_mx.json) |
| mx_6_5_26_17_12_11 | 45 | 203 | 2.92358730e-19 | 5.42088166e-05 | 1.84034615e-05 | 7.26122782e-05 | 0.540637 | 7.35107600e-05 / 7.50878900e-05 / 7.32052700e-05 | 7.39346400e-05 | 0.54074 | [QASM](full/mx_6_5_26_17_12_11.qasm), [JSON](full/mx_6_5_26_17_12_11.json) |
| replay82 | 45 | 203 | 2.92358730e-19 | 5.44088166e-05 | 1.86914100e-05 | 7.31002267e-05 | 0.539917 | — | — | — | [QASM](full/replay82.qasm), [JSON](full/replay82.json) |
| cancel_3 | 45 | 199 | 2.92358730e-19 | 5.47037984e-05 | 1.90359043e-05 | 7.37397026e-05 | 0.537987 | — | — | — | [QASM](full/cancel_3.qasm), [JSON](full/cancel_3.json) |
| lns_0000_release_alap | 46 | 194 | 2.92358730e-19 | 6.37834820e-05 | 2.22801420e-05 | 8.60636240e-05 | 0.536796 | — | — | — | [QASM](full/lns_0000_release_alap.qasm), [JSON](full/lns_0000_release_alap.json) |
| lns_0000 | 46 | 194 | 2.92358730e-19 | 6.46071841e-05 | 2.35787754e-05 | 8.81859595e-05 | 0.525716 | — | — | — | [QASM](full/lns_0000.qasm), [JSON](full/lns_0000.json) |
| helper_x_known | 47 | 204 | 2.92358730e-19 | 6.35113969e-05 | 2.92108095e-05 | 9.27222064e-05 | 0.515579 | — | — | — | [QASM](full/helper_x_known.qasm), [JSON](full/helper_x_known.json) |

The completion branch used is the verified MC improvement; individual long seeds were stopped early after that gate passed. Their stopped CPU times are reported rather than being mislabeled as two-hour timeouts. The winning mean is a measured three-seed result; the roughly 1e-6 SEM of each seed does not support a claim of statistical certainty from three seeds alone. All clean-prep aliases and their in-situ prices are mapped in [synthesis_all.csv](synthesis_all.csv).

The full stabilizer target is checked deterministically in Stim: three X generators, three Z generators and logical Z for each block. This repairs the prior verifier, which sampled only six X checks and could not certify the complete target. Every single-X location and every actual-CX XX fault is checked with the unmodified BC2 `clean` predicate, including C logical parity.

Solver improvement: the model shares eight backwards syndrome/parity bits at every time/cell. A counterexample adds four clean clauses using those shared signatures, rather than rebuilding a separate propagation network. Endpoint generator bases are fixed (independent GL(3,2) changes diversify code-equivalent bases); arbitrary forward basis variables are removed. Incremental CaDiCaL retains learned clauses; local repair uses assumptions to free consecutive or disjoint layer sets. Nine fixed networks cross-check SAT against independent Stim and BC2: [model_validation.json](model_validation.json).

The full-circuit builder preserves v20 native operation times outside B+C, with an explicitly recorded variant that advances terminal measurements freeing B/C cells and places the new prep ALAP. Initialization detectors are replaced by actual ownership, not by a pre-stage index list. MX records are propagated as Pauli-frame signs into the existing detectors. The never-used helper footprint is exactly 18, 24, 30–35; [v20_footprint.json](v20_footprint.json) records the native schedule. Helper X outcomes induce Z corrections derived from the six generator columns and folded into B readout detectors; the known q32 extension passes the full judge but loses on loss.

Bulk evaluation uses exact decoder Fourier moments. For each fault class, signed moments are summed over output-Pauli characters. Pair products subtract same-channel coincidences; triple products subtract the three pair coincidences and add twice the all-same-channel term. This is algebraic aggregation of exact2, not a fitted proxy. Seven circuits agree with unaggregated exact2 arithmetic within 4.5e-18 in loss: [moments_validation.json](moments_validation.json). Finalists additionally have unmodified `EVAL/exact2.py --third` CLI receipts.

Limits: no global optimality proof. Fewer CX did not reliably reduce in-situ loss: direct cancellation to 78 CX loses, and the 73-CX network initially delays the round to R=46. MC means, not exact-screen minima or single seeds, decide the ranking. The long-run solver records distinguish interrupted capacity stops from genuine timeouts. No submission, git commit/push, credential access, or changes to other lanes/jobs were made.
