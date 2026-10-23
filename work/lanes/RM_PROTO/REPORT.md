# RM_PROTO — reproduced paper and retained-output evaluation

Completed grid-free study. **Best tested retained-output variant: mean 1−F = 8.5189458302e-05 ± 6.1e-07 SEM, acceptance 0.64293977** under the judge's STANDARD noise at p=1e-3. It has 119 CX, 35 active qubits, and zero first-order loss. This remains above the leader's quoted 6.29e-5 even before routing; it is not a grid submission.

## 1. Circuit summary and artifacts

- **`rm_circuit.{qasm,stim,json}`**: canonical paper adaptation for RM_GRID, 89 CX, 19 active qubits, depth 59, serial reused flag ancillas. All four paper source groups are retained. Its measured mean is 1.2609125e-2, acceptance 0.5030749 (three 10-million-shot seeds). Data qubits in judge Steane order are **[4,2,3,0,5,1,6]**, corresponding to paper labels [5,3,4,1,6,2,7].
- **`paper_raw.*`**: original 82-CX physical circuit, with its physical software gauge frame documented below. It intentionally fails the judge's fixed-codespace check without that frame; it is a reproduction artifact, not a candidate.
- **`rm_optimized.*`**: best tested variant, exact copy of `va_ta0_PA.*`; the JSON records the provenance and scores.
- `rm_frame12.*`: superseded 94-CX coherent-frame prototype, retained as negative evidence. Its scores are distinct from the canonical 89-CX files.
- Stim files use the judge/xtim extended Stim syntax, including T and T_DAG.

Sources: supplied [arXiv:2609.12698](https://arxiv.org/abs/2609.12698), especially Appendices A–C; the exact 25-CX encoder is transcribed from [Daguerre–Kim, arXiv:2410.07327v3, Fig. 5](https://arxiv.org/pdf/2410.07327). The downloaded reference PDF and rendered encoder figure are in `paper/`. `build.py` contains every encoder and flag-gadget CX in execution order.

The encoder starts paper qubits 7,9,11,13,14 in |+⟩ and the other ten in |0⟩. A |+⟩ verifier controls seven CX onto **even labels 2,4,6,8,10,12,14** and is measured in X. Four reusable ancillas implement TA=(p14,p16,p17), TB=(p1,p2,p3), PA=(p8,p12), PB=(p10,p11), using the exact Table III geometry and Appendix B right-to-left gate order. These use 30+20 CX. The verifier, ten source syndromes and four flags give 15 deterministic source detectors. Odd paper labels receive T, even labels T†. Bulk qubits 8–15 are measured in X; their total parity is detector 16.

**Gauge-frame incompatibility:** the paper applies the physical software frame Z47^s1 Z45^s2 Z27^s3, with s1=u8⊕u9⊕u13⊕u14, s2=u9⊕u10⊕u11⊕u14, s3=u11⊕u12⊕u13⊕u14. The judge's FRAME declarations support only logical Paulis. Without physical gauge correction, 7/8 of noiseless branches lie outside its fixed +1 Steane codespace (exact infidelity 0.875). Postselecting all three random signs would give ideal acceptance 1/8 and cannot meet 0.5.

The canonical adaptation adds **CX(i→i+7), i=1…7**, before bulk readout. This coherently applies the required physical frame up to a Steane stabilizer and a logical Z. Declare FRAME_X=0 and **FRAME_Z=u8⊕…⊕u14**. On accepted even-bulk branches the latter also equals u15. These seven CX are real noisy gates under our judge; they are not hidden software corrections.

## 2. Reproduction against the paper

The paper model has exactly **150 independent noisy locations**: 30 preparations, 82 CX, 15 T/T†, 23 live measurements. It has no idle noise and ideal destructive output tomography. The software frame is represented by noiseless coherent gates, with bulk measurement flips placed before those gates so recorded-bit errors induce the correct physical frame. This placement matters.

`paper_eval.py` enumerates distinct faulty locations through weight three, including every Pauli component, using the exact rotation state. It separately postselects the three X-type or three Y-type destructive syndrome parities and combines their accepted weights and logical expectations **before** normalization; it does not substitute the judge's six-syndrome decoder.

| Quantity | Reproduced result | Paper |
|---|---:|---:|
| First-/second-order loss coefficients | 0 within 1e-12 roundoff | 0 |
| Cubic coefficient | 210.175037036965 | 2837363/13500 = 210.175037037037 |
| Acceptance from fault weights ≤3 | 0.868955329597 | 0.8689553 lower endpoint |
| Acceptance including adversarial higher-order mass | [0.8689553296, 0.8689733607] | [0.8689553, 0.8689734] |
| Conditional loss retaining weights ≤3 | 2.087903636e-07 | same low-order calculation |
| Finite-p upper bound, 99.9% joint confidence | **2.1813304353e-07** | ≤2.19e-7, rounded ≤2.2e-7 |
| Estimated finite-p infidelity | 2.1188661387e-07 | not the certificate |

For the independent finite-p certificate, `paper_high.py` sampled **1,000,000 fault-location subsets at each weight 4,5,6**, seed 20261024; positive-loss counts were 277,187,96. One-sided Clopper–Pearson bounds with Bonferroni allocation cover the three strata; all weight≥7 events receive unit loss (mass 2.59537e-10); the denominator floor is (1−p)^150. Evidence: `paper_orders.json`, `paper_high.json`. The headline result is reproduced, not merely quoted or obtained by substituting p into a fitted cubic.

## 3. Our-judge grid-free score and loss split

The canonical 89-CX adaptation's three 10-million-shot scores are 0.01261059484, 0.01258653178, 0.01263024879, mean **0.01260912514**, acceptance **0.5030749**. Its first-order loss is zero; second-order expansion is **0.01367511908**. Terminal last-output-gate plus idle-only loss is 0.001123901486, remaining-only 0.008424130787, mixed term 0.004127086808 at second order. Canonical output terminal idle counts in judge data order are **[10,21,13,20,1,1,4]**. This explains why the destructive paper result does not survive unchanged as a live-output score. Evidence: `rm_circuit_breakdown.json` and `rm7_serial_asap_both_score.json`.

The optimized variant uses a reduced source check set (one flagged TA check Z8Z9Z10Z15 plus PA's two checks), the original encoder and logical-X verifier, all 15 T/T† gates, the seven-CX coherent frame, and a final Steane round. Blocks A=|+L⟩ and B=|0L⟩ detect output X and Z errors; independent D=|+L⟩ verifies A's Z errors and C=|0L⟩ verifies B's X errors. The bulk/source cells are reset and reused. Ancilla preparation is scheduled as late as dependencies permit.

**Best circuit — 100 million shots per seed, exact xtim engine, unchanged STANDARD noise and decoder:**

| Seed | 1−F | SEM | Acceptance |
|---:|---:|---:|---:|
| 0 | 8.4828885431e-05 | 1.06e-06 | 0.64288243 |
| 1000 | 8.4251638611e-05 | 1.05e-06 | 0.64301420 |
| 2000 | 8.6487850864e-05 | 1.06e-06 | 0.64292267 |


Mean **8.5189458302e-05 ± 6.1e-07 SEM**; seed-0 three-significant-figure key **8.48e-05**. Acceptance mean **0.64293977**. Exact single-fault loss is zero (numerical residue -4.7e-19); second-order conditional expansion **7.2577559867e-05**. The Monte Carlo includes all fault orders; the difference from the expansion is material.

For the following split, **tail** includes the full noisy channels on the last two output-check CX gates and all data idle noise beginning there. It includes the partners' Pauli components; it is not just a hand-selected data marginal. **Rest** includes every other channel.

| Noise enabled | Second-order conditional expansion | All-order MC 1−F | MC acceptance |
|---|---:|---:|---:|
| Tail only | 2.5666666667e-05 | 2.5880387129e-05 ± 4.5e-07 | 0.99071161 |
| Rest only | 4.345868319e-05 | 5.2398811422e-05 ± 8.51e-07 | 0.64886968 |
| Mixed / ablation residual | 3.4522100109e-06 | 6.9102597505e-06 | — |
| All | 7.2577559867e-05 | 8.5189458302e-05 | 0.64293977 |

Tail/rest MC each uses 100 million shots, seed 0. The second-order split is additive. The all-order residual is full mean minus the two ablations and includes interactions and conditional-normalization effects; it is not a uniquely assigned causal contribution. Evidence: `va_ta0_PA_regions.json`. The tail's **2.5666667e-5 second-order loss matches the direct-readout floor in work/bounds.py**. Every output has consecutive final checks and exactly one terminal idle step.

## 4. Tail-optimised variants and decisions

All Monte Carlo means below use seeds 0/1000/2000; shot counts are explicit. First-order loss is zero except for `va_TA_TB` (1.6666667e-5 at p=1e-3). `results.json` also records exact screens, including source-check subsets with nonzero first order.

| Variant | CX | Mean 1−F | Acceptance | Shots/seed |
|---|---:|---:|---:|---:|
| `rm_frame12` | 94 | 0.032879368 | 0.465998 | 10,000,000 |
| `rm7_serial_barriers` | 89 | 0.025679869 | 0.473501 | 10,000,000 |
| `rm7_serial_asap` | 89 | 0.012609125 | 0.503075 | 10,000,000 |
| `rm7_serial_alap` | 89 | 0.018322844 | 0.512761 | 10,000,000 |
| `rm7_parallel_asap` | 89 | 0.0028391479 | 0.611533 | 10,000,000 |
| `rm7_parallel_alap` | 89 | 0.0033218689 | 0.621999 | 10,000,000 |
| `rm7_serial_dummy_alap` | 103 | 0.01831986 | 0.500259 | 10,000,000 |
| `rm7_parallel_dummy_alap` | 103 | 0.0050208471 | 0.596115 | 10,000,000 |
| `rm7_lateverify` | 91 | 0.0057905567 | 0.550385 | 10,000,000 |
| `rm7_lateverify_alap` | 91 | 0.0050957605 | 0.511216 | 10,000,000 |
| `rm7_parallel_asap_steane` | 137 | 0.00015099003 | 0.434245 | 10,000,000 |
| `rm7_parallel_steane_alap` | 137 | 0.00016667661 | 0.501566 | 10,000,000 |
| `va_TA_TB_PA_PB` | 153 | 0.00011495668 | 0.476557 | 10,000,000 |
| `va_TA_TB` | 133 | 9.8693721e-05 | 0.613514 | 10,000,000 |
| `va_PA` | 113 | 0.00012217402 | 0.664078 | 10,000,000 |
| `va_TA_PA` | 128 | 9.8273281e-05 | 0.586545 | 100,000,000 |
| `va_TA_PB` | 128 | 0.00011415532 | 0.575970 | 10,000,000 |
| `va_ta02_PA` | 123 | 9.3811374e-05 | 0.605328 | 100,000,000 |
| `va_ta0_PA` | 119 | 8.5189458e-05 | 0.642940 | 100,000,000 |


- Replaced the initial 12-CX coherent gauge frame by seven transversal CX; retained the 12-CX version as negative evidence.
- Tested serial barriers, ASAP and late scheduling; independent flag gadgets reduce source depth from 59 to 31. Late scheduling alone can improve acceptance while worsening loss.
- Tested explicit checked dummy partners in the final step. Serial late-scheduled result is score-neutral within noise; parallel reuse adds three steps and worsens loss. The idealized dummy floor does not account for this preparation/reuse cost.
- Tested moving and flagging the logical-X verifier at the end of source checks. It lengthens exposure and is worse in these schedules.
- Added a verified Steane round with direct one-step final readout. Verifying both ancilla blocks removes substantial source×round cross terms.
- Screened all 15 proper subsets of the four source groups and six reduced-TA variants. Dropping both pair groups gives first-order loss 1.6666667e-5 at p=1e-3. These candidates were also ranked by total loss, since zero first order is not a judge requirement; their best screened variant was Monte Carlo checked. The winning reduced source keeps PA and one flagged TA check. This changes the paper recipe and is explicitly an optimization, not part of the reproduction.
- Gauge readout timing follows the tested ASAP and late schedules; all eight bulk qubits are measured before their cells are reset and reused for output-round ancillas. Their timing, final check order, and output waiting steps are included in the actual STANDARD schedule.

No global-optimality or routing-feasibility claim is made. The surviving gap is mostly earlier faults and their interactions with the final round, not an avoidable multi-step terminal readout.

## 5. Judge-limit and correctness checks

`verify_limits.py` runs the judge's format, xtim class, exact correctness, and noiseless cross-engine checks with **only the adjacency predicate bypassed in process**. No judge source was edited.

| Check | Canonical rm_circuit | Optimized rm_optimized | Limit |
|---|---:|---:|---:|
| Active qubits | 19 | 35 | 36 |
| CX count | 89 | 119 | no separate CX cap |
| T/T† count | 15 | 15 | exact-engine processability |
| Rotation rank | 5 | 5 | 22 |
| Measure + reset | 53 | 91 | 1000 |
| Statements | 184 | 306 | 5000 |
| Bytes | 3236 | 11286 | 200000 |
| Noiseless fidelity | 1 | 1 | 1 |
| Deterministic detectors | 16/16 | 21/21 | all |
| STANDARD acceptance | 0.503075 | 0.642940 | ≥0.5 |

Both pass the non-grid format/class/correctness checks. **Chip adjacency is not satisfied and routing is unverified**, as requested for this lane. No submission or credentials access occurred. Evidence: `judge_limits.json`; canonical SHA-256 `5e9dc3ce1ae09cbb2b46b5038e4a20e60f68cfd16e6bf23932935930a70e03cd`; optimized SHA-256 `894ceb4d65151f12bacd874eb41bf48d9d38c3a121b627688c745ab44c53cc81`.

## Reproduction and provenance

Run from this directory with `/home/jihoon/competitions/quantumn/.venv/bin/python`, `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`:

1. `build.py` reconstructs the paper and canonical circuit; `paper_eval.py` and `paper_high.py` reproduce the paper metric.
2. `variants.py`, `alap.py`, `dummy.py`, `late_verify.py`, `subsets.py`, `verified_a.py`, `reduced_ta.py` generate the evaluated variants.
3. `score.py va_ta0_PA --mode mc --procs 4 --shots 100000000` reproduces the three-seed judge metric; `regions.py va_ta0_PA 100000000 6` reproduces the noise split.
4. `verify_limits.py rm_circuit va_ta0_PA va_ta02_PA va_TA_PA` reproduces limits and noiseless checks.

Only OS processes were used; no subagents or collaboration tools. Jerry jobs used capped threads and bounded worker pools; local compute stayed at at most two processes. When Jerry's observed load approached 75% of 64 cores, subsequent MC jobs were reduced to four workers; independent six-worker region scoring started only after load fell below 26.

**Cache containment correction:** local xtim checks initially created reference-cache files in repository-root `.xtim_cache`, outside the requested lane. The local run was stopped by exact PID; cache paths now point explicitly under RM_PROTO. `cache_audit.py` identified exact circuit keys and removed 30 lane-specific root cache entries, preserving unrelated entries. `cache_audit.json` records this correction. No source file outside this lane was changed. Generated caches are ignored by this lane's `.gitignore`.
