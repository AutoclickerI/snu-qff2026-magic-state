# SCHED lane report

The scheduler keeps each native operation's per-qubit order and gate fixed. It folds reset+h and h+measure into the judge's native RX/MX operations, assigns one barrier-separated layer per step, and prices each idle gap with the exact merged probability `0.75*(1-(1-4p/3)^x)`. The fixed quadratic coefficients come from `EVAL/exact2.py`'s `(s,d)` pair tables.

## Part 1: exact quadratic schedules

| Target | Baseline | Baseline 2nd | Baseline 3rd | Scheduled | Scheduled 2nd | Scheduled 3rd | First order | exp(-A1) | MC mean ± SEM | seed-0 |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| v12 | submitted `v12_L5lns12` | 1.121949e-4 | 1.14313e-4 | `v12_scheduled` | 1.104850e-4 | 1.12796e-4 | 1.39e-19 | 0.66934 | 1.130400e-4 ± 5.66e-7 | 1.137159e-4 |
| cand2 | `ST_BC/cand2` | 9.161934e-5 | 1.286e-4 | `cand2_scheduled` | 8.758413e-5 | 1.26105e-4 | 5.03e-19 | 0.50405 | 1.285260e-4 ± 7.36e-7 | 1.295218e-4 |

Baseline values: v12 3-seed MC mean `1.132707e-4`; cand2 `1.312041e-4`, with baseline `exp(-A1)` 0.69052 and 0.52772. Scheduled MC rows are in `v12_scheduled.mc.json` and `cand2_scheduled.mc.json`; each uses seeds 0, 1000 and 2000 with 1e8 shots. Both scheduled circuits pass `tprep.check` at 1e6 shots (format, class, correctness, acceptance); v12 acceptance 0.6687 and cand2 0.5049.

| Target / variant | seed 0 | seed 1000 | seed 2000 | mean ± SEM | seed-0 score |
|---|---:|---:|---:|---:|---:|
| v12 baseline | 1.146510e-4 | 1.132262e-4 | 1.119350e-4 | 1.132707e-4 ± 6.33e-7 | 1.146510e-4 |
| v12 scheduled | 1.137159e-4 | 1.134884e-4 | 1.119158e-4 | 1.130400e-4 ± 5.66e-7 | 1.137159e-4 |
| cand2 baseline | 1.295896e-4 | 1.326035e-4 | 1.314192e-4 | 1.312041e-4 ± 8.77e-7 | 1.295896e-4 |
| cand2 scheduled | 1.295218e-4 | 1.270898e-4 | 1.289664e-4 | 1.285260e-4 ± 7.36e-7 | 1.295218e-4 |

Five random feasible schedules per target match uncached exact2 second order to relative errors below `1.4e-15`; receipts are `modelcheck_v12.json` and `modelcheck_cand2.json`. Native `tprep.noise.schedule` reproduces every emitted layer.

## Part 2: full-circuit encoder selection

The exact enumeration produced 223 distinct A encoders (the existing `exact200.cpp`/`merge.py` flow). All 223 were scored at second order; the lowest-second-order shortlist was rescored through exact third order. The completed third-order ranking selected `enc_210` and `enc_202`:

| Encoder | danger | depth | CX | exact 2nd | exact 3rd | first order | exp(-A1) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `enc_210` (best) | 6.67e-4 | 6 | 12 | 9.161602e-5 | 1.285389e-4 | 5.03e-19 | 0.52775
| `enc_202` | 6.67e-4 | 6 | 11 | 9.161934e-5 | 1.286256e-4 | 5.03e-19 | 0.52772

The next third-order candidate `enc_204` is `1.304812e-4`; `enc_193` is `1.300217e-4` (lower second-order, but worse third-order than the selected pair). Candidates are `encoder_best_210.qasm/.json` and `encoder_best_202.qasm/.json`; both pass `tprep.check` at 1e6 shots (acceptance about 0.527). The encoder sweep's exact JSON receipts remain in `encoders/`.
