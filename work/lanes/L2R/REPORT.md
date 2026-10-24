# L2R — LAYOUT2 release-aware and prep-witness screen

All artifacts in this lane were made with the required thread caps. No submission
was made. The supplied incumbent is copied as [base.qasm](base.qasm) with its
data mapping in [base.json](base.json).

## Baseline ablation

The exact evaluator was run on `v15_l2m.qasm` with `pre_end=32`, `round_start=54`,
and A cells `13,26,20,22,21,23,14`. The complete receipts are
[ablate_only.txt](ablate_only.txt) and [ablate_wait.txt](ablate_wait.txt).

| Region kept noisy | 2nd | 3rd | total | exp(-A1) |
|---|---:|---:|---:|---:|
| all | 6.0952e-5 | 3.5383e-5 | 9.6335e-5 | 0.5011 |
| pre only | 1.7747e-6 | 6.3764e-7 | 2.4123e-6 | 0.7156 |
| wait only | 0 | 9.3813e-7 | 9.3813e-7 | 0.9165 |
| moves only | 0 | 2.0623e-8 | 2.0623e-8 | 0.9694 |
| A only | 0 | 2.4317e-8 | 2.4317e-8 | 0.9484 |
| prep only | 1.3337e-5 | 4.4216e-7 | 1.3779e-5 | 0.8681 |
| round only | 2.8133e-5 | -1.2233e-7 | 2.8011e-5 | 0.9573 |

| Data-wait scale | 2nd | 3rd | total | exp(-A1) |
|---:|---:|---:|---:|---:|
| 1.0 | 6.0952e-5 | 3.5383e-5 | 9.6335e-5 | 0.5011 |
| 0.5 | 6.0439e-5 | 2.1761e-5 | 8.2200e-5 | 0.5233 |
| 0.0 | 5.9924e-5 | 1.2146e-5 | 7.2070e-5 | 0.5468 |

The zero-wait counterfactual is an ablation only; it is not a judge-valid
circuit because the current layout's release constraints still require R=54.

## Synthesis attempts

The release-aware CP-SAT merger is [release_merge.py](release_merge.py). It
preserves per-cell job order and minimizes R before maximizing lateness. On the
given 68-CX BC witness it found `R=54`, but its alternate prep interleaving
raised the exact loss to 1.53380e-4. It is retained as a negative receipt in
[rel2_metrics.json](rel2_metrics.json). Moving cat preparation earlier caused
acceptance failures (`rel0`/`rel1`) and was discarded.

| Candidate | R | wait steps | CX | c1 | 2nd | 3rd | exp(-A1) | MC seeds 0/1000/2000 | MC mean | seed-0 acceptance | status | files |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---|
| base v15_l2m | 54 | 15 | 212 | 4.2188e-19 | 6.11575e-5 | 9.63348e-5 | 0.50112 | 1.013296e-4 / 1.011040e-4 / 1.000947e-4 | 1.008428e-4 | 0.5009 (1e6) | PASS | [base.qasm](base.qasm), [base_check.log](base_check.log) |
| rel2 release CP-SAT | 54 | 15 | 212 | 6.0668e-19 | 1.13784e-4 | 1.53380e-4 | 0.50971 | — | — | 0.5104 | PASS, rejected by exact | [rel2.qasm](rel2.qasm), [rel2_metrics.json](rel2_metrics.json) |
| rel2 + q5,q11,q18 | 54 | 15 | 212 | 6.0668e-19 | 1.12806e-4 | 1.52365e-4 | 0.50717 | — | — | 0.5076 | PASS, rejected by exact | [rel2_m5_11_18.qasm](rel2_m5_11_18.qasm), [rel2_m5_11_18_metrics.json](rel2_m5_11_18_metrics.json) |
| rel2 non-cat measure-init | 54 | 15 | 212 | 6.0668e-19 | 1.12668e-4 | 1.51556e-4 | 0.49795 | — | — | 0.4988 | FAIL acceptance | [rel2_noncat.qasm](rel2_noncat.qasm), [rel2_noncat_metrics.json](rel2_noncat_metrics.json) |
| rel0 early-cat schedule | 54 | 15 | 212 | 8.4619e-19 | 3.02023e-4 | 5.71787e-4 | 0.27874 | — | — | 0.2803 | FAIL acceptance | [rel0_metrics.json](rel0_metrics.json) |
| rel1 early-cat schedule + measure-init | 54 | 15 | 212 | 8.4619e-19 | 3.00507e-4 | 5.66522e-4 | 0.2714 | — | — | 0.2735 | FAIL acceptance | [rel1_mall_metrics.json](rel1_mall_metrics.json) |
| BC seed 0, incumbent merger | 54 | 15 | 212 | 4.2929e-19 | 6.26102e-5 | 9.83431e-5 | 0.50538 | 1.003867e-4 / 1.004573e-4 / 9.974423e-5 | **1.001961e-4** | 0.505694 (1e8), 0.505427 (1e6) | PASS; best MC | [bc0_m.qasm](bc0_m.qasm), [bc0_m.json](bc0_m.json), [bc0_m_metrics.json](bc0_m_metrics.json) |

The BC seed-0 candidate is the final lane result. Its exact total is within 3%
of the incumbent threshold, so it received all three 1e8-shot MC runs. Its mean
is 0.65% below the supplied 1.00843e-4 baseline mean, and its seed-0 official
value is 1.003867e-4. Every candidate sent to MC passed the 1e6-shot judge check;
the other candidates were rejected by exact score or acceptance before MC.

## Solver receipts

The BC witness used by the final candidate is the LAYOUT2 14-layer, 68-CX
fault-tolerant prep [r23_1_3_BC_d14_k68_s0.json](../LAYOUT2/r23_1_3_BC_d14_k68_s0.json).
The incumbent A encoder is the first filtered 13-CX, depth-8 witness in
[r23_1_3_A_filtered.json](../LAYOUT2/r23_1_3_A_filtered.json). The release
scheduler's receipt is embedded in `rel2.json` (`OPTIMAL`, 0.0602 s, R=54).
