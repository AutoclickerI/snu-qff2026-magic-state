# EARLY lane report

The release-aware run keeps the L5 geometry and schedules the joint B+C encoder by individual
cell dependencies.  A CP-SAT ALAP pass first minimizes the round start and then maximizes the
start time of every preparatory unit at that minimum, which prevents free-cell preparations from
creating an idle tail.  The prefix ends at step 32 (first free step 33).

The new B+C synthesis is a 14-layer, 73-CX witness.  Its SAT receipt is
[`sat6_d14_k82_late3_s0.receipt.json`](sat6_d14_k82_late3_s0.receipt.json): cells 4, 6, 13 and
19 are forbidden before layer 3, the real FT rule has 53 CEGAR fault constraints, and all bad
single-X faults are absent.  The scheduler is `early_merge.py`; it gives `R=48`, 15 data wait
steps (steps 33--47), and 198 total CX.

Every accepted row below passed format, class, correctness and acceptance at 1e6 shots.  `c1` is
the exact first-order diagnostic; values around 1e-19 are numerical zero.  Exact columns are from
`exact2.py --third` with 8 or 4 workers as recorded in the adjacent logs.

| candidate | R | data wait | CX | c1 | 2nd | 3rd | exact total | exp(-A1) | 1e6 seed-0 acceptance | MC seed 0 | MC seed 1000 | MC seed 2000 | MC mean | files |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| L5 late3 ALAP | 48 | 15 | 198 | 3.4047e-19 | 7.00083e-5 | 2.29609e-5 | 9.29692e-5 | 0.55681 | 0.557001 | 9.323137e-5 | 9.295966e-5 | 9.337501e-5 | 9.318868e-5 | [`l5_late3_alap.qasm`](l5_late3_alap.qasm), [`l5_late3_alap.json`](l5_late3_alap.json) |
| L5 late3 + m17 | 48 | 15 | 198 | 3.4047e-19 | 6.94638e-5 | 2.29457e-5 | 9.24095e-5 | 0.55589 | 0.555477 | 9.466855e-5 | 9.461350e-5 | 9.350368e-5 | 9.426191e-5 | [`l5_late3_alap_m17.qasm`](l5_late3_alap_m17.qasm), [`l5_late3_alap_m17.json`](l5_late3_alap_m17.json) |
| L5 late3 + m25 | 48 | 15 | 198 | 3.4047e-19 | 6.99416e-5 | 2.29488e-5 | 9.28904e-5 | 0.55589 | 0.555435 | 9.445762e-5 | 9.221530e-5 | 9.450749e-5 | 9.372680e-5 | [`l5_late3_alap_m25.qasm`](l5_late3_alap_m25.qasm), [`l5_late3_alap_m25.json`](l5_late3_alap_m25.json) |
| **L5 late3 + m27** | **48** | **15** | **198** | **3.4047e-19** | **6.96305e-5** | **2.29503e-5** | **9.25808e-5** | **0.55589** | **0.556335** | **9.244435e-5** | **9.299956e-5** | **9.281592e-5** | **9.275328e-5** | [`l5_late3_alap_m27.qasm`](l5_late3_alap_m27.qasm), [`l5_late3_alap_m27.json`](l5_late3_alap_m27.json) |

The m17, m25 and m27 suffixes are first-use measurement rewrites from `minit.py`; m27 measures
the first-use reset of q27 and is the best three-seed mean.  All 14 single-site rewrites and the
all-sites rewrite passed the 1e6-shot judge gate; the screen is in
[`minit_checks.txt`](minit_checks.txt).  Their seed-0 scores ranged from `8.18e-5` to `1.14e-4`,
with acceptance `0.5554--0.5563`; only the exact-third-order finalists were sent to 1e8-shot MC.

The same 1e8-shot run on the supplied baseline [`v14_bcm.qasm`](v14_bcm.qasm) gives
`1.025239e-4`, `1.043763e-4`, `1.042962e-4`, mean `1.037321e-4`, acceptance `0.544361`, and
207 CX.  Thus m27 improves the measured mean by 10.61% (and the seed-0 score by 9.83%) while
retaining acceptance above 0.5.  Its exact baseline comparison is the supplied v14 value
`1.018941632e-4` (2nd `7.333299e-5`, 3rd `2.856117e-5`, exp(-A1) `0.544084`).

The independent LAYOUT2 c5 witness was also checked: `R=55`, 22 wait steps, 212 CX, c1
`4.2929e-19`, 2nd `6.51499e-5`, 3rd `4.04374e-5`, total `1.05587e-4`, exp(-A1) `0.50822`,
and acceptance `0.5081`.  It is above the v14 exact total and was not sent to MC.  The first
release-aware schedule without the ALAP objective was rejected at acceptance `0.3767`; its
failure is preserved in `l5_early.exact.log`.

For the winning m27 circuit, `ablate.py --wait-scale` gives:

| wait scale | 2nd | 3rd | total | exp(-A1) |
|---:|---:|---:|---:|---:|
| 0 | 6.2150e-5 | 7.0647e-6 | 6.9214e-5 | 0.6036 |
| 0.5 | 6.5908e-5 | 1.3470e-5 | 7.9378e-5 | 0.5791 |
| 1 | 6.9630e-5 | 2.2950e-5 | 9.2581e-5 | 0.5559 |

The receipt is [`l5_late3_alap_m27.ablate32.log`](l5_late3_alap_m27.ablate32.log).  The remaining
data wait therefore costs about `2.34e-5` exact third-order loss relative to zero wait.
