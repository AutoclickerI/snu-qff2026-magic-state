# LNS

**Status: running. A fully MC-ranked delivery exists; the complete move-set certificate is still open.**

Delivery alias: `best.qasm/.json` = **bc_port_ed4839a8a8**. Ranking uses completed 1e8-shot means at seeds 0/1000/2000; acceptance is a gate.

Best completed MC mean: **6.895644e-05**, `bc_port_ed4839a8a8`; seed-0 acceptance **0.53259**.

Best exact screen: **bc_port_229898d242**, **6.75808350118e-05**, delta from v22h_c2c9 **-3.72512177e-06 (-5.224%)**.
Second 5.16277975475e-05; cubic 1.59530374643e-05; exp(-A1) 0.53902294; c1 p 2.92e-19; R [44, 44], 204 CX.
This exact screen is not promoted by predicted acceptance or score alone. Its MC status is shown below.

| Finalist | Seed 0 | Seed 1000 | Seed 2000 | Mean | Seed-0 acc | Check |
|---|---:|---:|---:|---:|---:|---|
| bc_port_ed4839a8a8 | 6.852339e-05 | 6.904925e-05 | 6.929668e-05 | 6.895644e-05 | 0.53259 | PASS |
| bc_follow1_25345cb641 | 6.953067e-05 | 7.028041e-05 | 6.90633e-05 | 6.962479e-05 | 0.53926 | PASS |
| iter3_0cc1febf8e | 7.026273e-05 | 6.997225e-05 | 7.035348e-05 | 7.019615e-05 | 0.53577 | PASS |
| bc_w_fast | 7.007544e-05 | 7.156851e-05 | 7.130104e-05 | 7.098166e-05 | 0.53421 | PASS |
| fast_compound2_774000b526 | 7.023561e-05 | 6.95945e-05 | 7.347679e-05 | 7.11023e-05 | 0.52559 | PASS |
| fast_follow2_36fc263c49 | 6.945745e-05 | 7.067343e-05 | 7.318427e-05 | 7.110505e-05 | 0.52017 | PASS |
| fast_compounds_d2fa7dd5be | 7.05832e-05 | 7.300042e-05 | 7.092891e-05 | 7.150418e-05 | 0.52888 | PASS |
| reset_h | 7.168144e-05 | 7.18449e-05 | 7.161891e-05 | 7.171509e-05 | 0.53222 | PASS |
| reset_w | 7.146481e-05 | 7.206699e-05 | 7.362855e-05 | 7.238678e-05 | 0.53397 | PASS |
| choices_6123b801f1 | pending | pending | pending | pending | pending | PASS |

| Move family | Evaluations | Invalid screens | Better than parent | Best exact delta vs starting bar |
|---|---:|---:|---:|---:|
| timing | 5813 | 0 | 210 | -3.62027342e-06 |
| commute | 798 | 0 | 64 | -2.77637731e-06 |
| init | 1358 | 332 | 240 | -3.72512177e-06 |
| phase | 113 | 18 | 14 | -2.77347212e-06 |
| readout | 4004 | 602 | 39 | -3.58263499e-06 |
| hop | 315 | 48 | 31 | -2.7843873e-06 |
| triple | 166 | 0 | 139 | -2.01360827e-06 |

Counts are completed evaluations, including earlier controls/repeated recipes; build failures and interrupted work are not certificates. Full descriptions, hashes, objective parts and errors are in the lane JSONL logs. Physical-equivalence qualifications are below.

## Delivery and interpretation

The MC table above and the delivery alias are authoritative current facts. The alias is promoted only after a passing judge check and all three 1e8-shot MC seeds. Earlier sampled candidates remain in the table as measured finalists, not current recommendations. Differences comparable to a per-seed SEM of about 1e-6 are statistically unresolved even though the required observed mean defines rank.

The current normal-speed BCSYN2+LNS delivery is **bc_port_ed4839a8a8**: **6.895644e-5 mean**, from **6.852339e-5 / 6.904925e-5 / 6.929668e-5**, seed-0 acceptance **0.53259**. Unmodified exact2 gives **6.85320e-5**; the full-precision pruned receipt is **6.853195009309e-5**. Native R=45, 204 CX. It starts from MAIN/v23h_c2c9, which combines BCSYN2's fb_s401_0035 prep with HOPS and ACHECK, then adds the verified LNS pre-stage watches/checks, commuting swaps, q10 measured initialization, and readout 14→8. The BC preparation is BCSYN2's contribution; the port and additional moves are this lane's work.

The original h/w bases were both explored. The q8-reuse family is slower to sample: iter3_0cc1febf8e completed at **7.019615e-5 mean**, acceptance **0.53577**. The latest lower exact screens have not yet completed required MC and do not replace the delivery on predictions alone. In particular the BCSYN2+q8-reuse screen **bc_port_229898d242** is **6.758083501181e-5** exact, exp(-A1) **0.53902294**, R44/204CX.

## Kept mechanisms

- q8 MX reuse removes the reset at old native step 24, the sole operation in that layer. Native R moves 45→44 with 203 CX. Both pair and cubic losses fall. The normal-speed branch retains that reset because reset-free sampling is much slower.
- Six B+C pivots use MX initialization, with random Z-frame records propagated through the Clifford suffix and XORed into detectors. Every variant passes exact2's actual noiseless-correctness gate before being scored.
- Commuting pre-stage CX swaps (9→10 with 9→15; later 1→0 with 1→7; 9→3 with 9→15) alter the exposure to propagated faults. Each retained swap has an exact full-circuit receipt; gate count is not the ranking objective.
- X watches before early resets, plus MX checks immediately after selected RX preparations, reduce the cubic term. Measured initialization of q10/q19 and readout edge 14→8 combine with these checks in the current delivery.
- `cubic_lns_best` changes 32 operation times, retains native R=44 and depth 47, and advances the 16→22 transfer by seven steps. Exact parts: **5.298088067412e-5 + 1.596764238901e-5 = 6.894852306313e-5**, exp(-A1) **0.51611202**. Its independent pruned exact2 confirmation and timing diff are saved. Judge/MC checks remain pending for this screen.
- A built data-15 path 15→21→22 finishes before data 8 enters 21. On the current normal-speed delivery it gives **7.012217965511e-5**, a 1.03227e-8 exact gain (`fast_follow2_36fc263c49`). Its MC is running. This is a measured alternative route, not a global route certificate.

## Third-order evidence

`choices_6123b801f1.attribution.json` includes region pair sums and thresholded triples after q8 reuse. The largest retained positive triple is Z-idle on data cells 10, 3 and 0 (1.13019773e-7), followed by A9 Z idle with data 3/0 (4.06067654e-8). Positive weight-three sums exclude the negative pair-times-other-channel normalization; they are not the complete cubic increment. Original MAIN port metadata omitted prefix indices, so `analyze.py` reconstructs them from HOPS operation identities. This diagnostic labeling does not affect scores, and new operations can have incomplete region attribution.

## Evaluator verification

- `moments_validation.json`: BCSYN2's exact Fourier contraction matches TREP2 pruned exact2 on both supplied bases within 3.9e-18. A lane-local copy is in `inputs/moments.py`; only its root-path resolution differs. All newly retained best screens receive an independent pruned exact2 confirmation.
- Unmodified `EVAL/exact2.py --third` agrees to every printed digit for iter3_0cc1febf8e and fast_compounds_d2fa7dd5be (`*.reference.log`). Both have c1 p = 2.9236e-19.
- `temporal.py` compiles fixed-order pair/cubic contractions once, with a zero-noise spectator exposing all possible idle boundaries. Five independent emitted schedules validate each compiled model; the saved winner is evaluated independently again. The low branch tested 2,997 unique proposals and improved to cubic_lns_best. The normal-speed branch tested 3,033 unique proposals with no gain (`cubic_fast.*`).
- The fixed-order LP timing repair matches five CP-SAT integer-optimum references and their step-change costs (`retime_lp_vs_cpsat.json`). CP-SAT remains for commuting-order and synchronized-round models.

## Scope and certificates

The exhaustive directed readout scan evaluated **all 1,953 matchings** on reset_h. Best: **14→8, 17→16, 19→25**, exact **7.043276005278e-5**, `matchings_0e63052f92`. This closes only the ten grid edges, disjoint endpoints, one CX layer and fixed readout schedule in `matchings.py`; it does not close arbitrary readout networks or modified later bases.

The iterative neighborhood covers feasible single-native-unit placements; legal commuting-CX swaps with minimum-deviation repair; implemented reset/measure/RX/MX-reuse and watch/check choices; final-Tdag masks; detector/frame variants; destination-basis and chain timing choices; and round placements R−3 through R+1. `iter*.coverage.json` gives each completed pass's bounds and counts. A sampled search, timeout, build failure or interrupted pass is not a local-optimum proof. General routes, different footprints, and arbitrary readout networks remain open.

## Interpretation and operational limits

A pure T/Tdag shift inside one single-wire idle interval is exactly the same channel under isotropic depolarization when every other native operation and occupied layer is fixed: D_b D_1 U_T D_a = D_(a+b+1) U_T. `phase_idle_identity.json` checks 992 splits to 4.45e-16. The ~2.7e-10 exact2 differences for isolated T-q4 shifts are truncation/resummed-channel grouping effects, not true ensemble gains. These analytically equivalent placements are excluded from new single-unit scans; HOPS phase relocations through CXs remain included.

Runtime is measured, server consequences inferred: the first q8-reuse 1e6-shot check took about 83 s on zebra; the later finalist took about 132 CPU-s on Jerry. A sequential 1e8-shot evaluation could exceed the external one-hour submission limit. Server hardware/runtime is unverified, so no server-time pass/fail is asserted. The superseded initial reuse MC was stopped with no completed seeds; its interruption receipt is explicit. The retained finalist's full MC continues.

Malformed early bit-allocation proposals and native-MX folding errors failed before scoring, were corrected, and affected proposals were regenerated. Capacity-related stops and restarts preserve completed rows and are logged. No submission, commit, push, credentials access, sub-agent, or other-lane modification was performed. Source, candidates and receipts are under LNS.

