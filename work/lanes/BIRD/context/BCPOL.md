# BCPOL

Status: RUNNING — contract searches, final validation and all-orders reference comparison. No submission, commit or push.

Pricing base: `../MAIN/v23h_c2c9`, second 5.24923143352901e-5, cubic 1.67287254874966e-5, total **6.92210398227867e-5**, exp(-A1) **0.54085957771236**. The canceled v24 base is excluded. Baseline rebuild reproduces these parts; baseline 1e6-shot judge PASS at 3.7 s on zebra.

Best completed three-seed mean: **`finalists/endpoint_5_s712_00138`**, **6.906951e-05**. Second 5.24316756593e-05; cubic 1.6477486555e-05; total 6.89091622142e-05; exp(-A1) 0.5422649935. Runtime **6.0 s per 1e6 on hippo**, versus v22 calibration 4.6 s (scaled limit 40 s).
Difference from v23h_c2c9: exact delta **-3.118776085e-07** (-0.4506%); delta A1 **-0.00259511526**. Contract endpoint 5; 5 X pivots, 88 prep+check CX, 202 total CX, R=45. The suffix and non-BC operation times are retained.

| Completed finalist | 2nd + cubic | exp(-A1) | ΔA1 | seed 0 / 1000 / 2000 | MC mean | seconds/1e6, host |
|---|---:|---:|---:|---|---:|---|
| `endpoint_5_s712_00138` | 6.8909162214e-05 | 0.542264993 | -0.002595115 | 6.917631e-05 / 6.82218e-05 / 6.98104e-05 | 6.906951e-05 | 6.0, hippo |
| `endpoint_5_s712_00601` | 6.8450176403e-05 | 0.544326378 | -0.006389342 | 6.890265e-05 / 6.86921e-05 / 7.047326e-05 | 6.9356e-05 | 6.3, jerry |
| `endpoint_4_s711_00035` | 6.8773241635e-05 | 0.542224508 | -0.002520453 | 7.113477e-05 / 6.776882e-05 / 7.098774e-05 | 6.996378e-05 | 6.7, hippo |

## Item 4 — partial-clean policies

All seven singleton policies are implemented with shared-signature SAT cuts, independent complete CSS/Stim targets, and exhaustive single-X plus actual-CX XX checks. The policy-9 search produced genuinely dirty witnesses; clean intermediates are not priced, avoiding BCFB’s contract. Six other singleton searches produced no priced witness in their recorded finite budgets; this is not UNSAT.

Explicit terminal identity-pair controls give a valid witness for every singleton class 9..15. All have c1 below 1e-12. They require one or two added round steps and lose in the cubic screen; the loss combines admitted correctable boundary errors with extra data waiting. These controls do not close the policies or establish an optimum. Full reference checks are recorded separately from screens.

## Item 5 — endpoint after B→C

All seven rank-5 endpoints were attempted from the 89-CX rank-6 seed. Five produced candidates; endpoints 6 and 7 produced no witness in the initial finite budgets. The original 89-CX seed is SAT under the new predicate and reproduces baseline loss. Correctable boundary errors are allowed; harmful accepted B classes remain forbidden.

Rank-5 winners have five initialization pivots and synthesize prep plus check together. The observed gains come from their full noisy schedule and fault correlations, not from CX count. Fixed-initialization SAT feedback now uses the validated boundary cache when the exterior fingerprint matches. Every new best is independently rescored and judge-checked before retention.

## Item 6 — C6

All seven accepted-sector identities were exhaustively proved over 128 X patterns: exactly S ∪ (S+e_i), with no harmful logical class. All seven zero-return-helper synthesis models were launched. Additional helper-X models permit the omitted cell to carry temporary coherence and then be measured; their Z-frame correction is propagated through already-performed same-step checks.

The first builder unnecessarily removed both readout-recoding CXs for every omission. The corrected builder removes only recoding touching the omitted cell and permits its terminal helper measurement at R. Old screens remain tied to their frozen circuits. Projected baseline recipes at positions 0, 4, 6 pass the independent ideal/predicate checks and have cubic losses 1.04167240741e-4, 9.09683488605e-5, 9.68653536748e-5. Positions 1, 2, 3, 5 fail the single-X predicate before full pricing. This closes only these projected recipes; fresh helper-X synthesis continues.

## Item 10 — boundary cache

Verified rank: **11 = 8 X + 3 Z** for the v23h_c2c9 boundary before step 45. The implemented cache stores degree-0/1/2 exterior response kernels over all 2048 classes and the pure exterior cubic scalar; prep distributions use exact categorical-channel Fourier polynomials. It reproduces full cubic arithmetic within 1.2e-17 on baseline and physical cancellation controls. Baseline compilation took 3.56 s; compatible scoring about 0.03–0.05 s. Frozen initialization times and an exterior-channel plus ideal-decoder fingerprint prevent invalid reuse. Other endpoints, schedules, or shared-record correlations require a new cache.

**This cache is exact through third order, not all orders.** The reviewer’s independently validated all-orders reference has now been found in MAIN/spec and is running on the baseline and close finalists. WALSH currently contains code but no validation report. An all-orders boundary-response cache remains under implementation.

## Verified versus inferred

Verified receipts: `validation.json`; the rank audit; complete CSS target and fault-predicate checks; cubic evaluator comparisons; frozen finalist `*.exact.log`, `*.speed.log`, `*.mc.log`, and `*.verified.json`. Full checks call unmodified EVAL/exact2.py --third with |c1|<1e-12 and the unmodified MAIN/spec/mc3.py (byte-identical lane copy on hosts where MAIN/spec is absent).

Not yet established: a global optimum; an all-orders cache; final close-candidate ranking when MC and cubic screens disagree. Screens without completed reference receipts are provisional. exp(-A1) is a predictor, not the final seed-0 acceptance gate. Paused searches record capacity interruptions and are not mislabeled UNSAT. Runtime passes refer to the measured host and v22 calibration; server runtime is inferred.

Only BCPOL files are written. No credentials read, submissions, git mutations, or agents. Other lanes and jobs are read-only.
