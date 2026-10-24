# TREP — verified grid candidate, 8.52% lower MC mean

**Primary delivery: [encoder19_alap.qasm](encoder19_alap.qasm) + [metadata](encoder19_alap.json).** The 1e8-shot mean at seeds 0/1000/2000 is **7.636083e-05**, versus v17a **8.347295e-05**. All four judge gates pass at 1e6 shots; seed-0 acceptance is 0.52782. The circuit uses 203 CX and native depth 49, with the round at native step 46. No submission, commit, push, or writes outside this lane were performed.

The first completion gate is met. All 16 supports were enumerated and their phase-axis protection checked. The winning circuit resynthesizes the current form; the other 15 forms were **not physically synthesized or priced**. Their full-fault behavior remains unverified. They are not claimed to lose.

## Corrections to the brief

- v17a’s metadata/barrier label is R=47, but `tprep.noise.schedule` places its actual round at **50**, with native depth **53**. Its pre-stage still ends at 32. Every R and release step below uses the judge’s native scheduler. The source QASM SHA-256 is `2b990de2563bf8a87343cdcb68c1012739b7726686ae0587b706fc3b4a053e1b`.
- In [R1’s pair log](../R1/v16_release_drop.pairs.log), 6.410e-6 is **prep×round**, and 5.875e-6 is **prep×prep**. Those refer to suffix-block preparation. The distinct pre×round entry is 2.265e-6.

## Enumeration and physical synthesis

Pulling back the 15 rotations gives mutually commuting axes. Their X action on the occupied orbit has **rank 5**; the full Pauli vectors have **rank 9**. Every extra Z factor is trivial on the occupied orbit. In the basis recorded in [enumeration.json](enumeration.json), the signed phase is exactly `parity(25 & y) mod 8` for all 32 assignments.

The degree-1/2/3 binary phase-signature matrix has rank 25 on the 31 nonzero axes. Its six-dimensional kernel is exactly the punctured affine functions. The complete 64-word coset has T-weight counts `1:1, 14:15, 15:16, 16:16, 17:15, 30:1`. The one-T support has one harmful phase-axis single; every 14-T support has seven harmful phase-axis pairs; every 15-T support has zero harmful singles and pairs. Each 15-T support also has explicit ±1 coefficients reproducing the exact ideal phase, so no extra Clifford phase correction is required. These statements are exhaustive calculations in [enumerate.py](enumerate.py), not full-fault guarantees for unsynthesized circuits.

Two CP-SAT models changed the physical network:

- [synth_init.py](synth_init.py) replaced the 12-CX pre-T Clifford resource by an 11-CX, five-layer state preparation, preserving its entire CSS stabilizer space. The fixed-initialization five-layer objective was solved optimally. Four-layer variants and the five-layer full-unitary model returned INFEASIBLE; these are limited to the encoded solver models.
- [synth_encoder.py](synth_encoder.py) replaced the complete 25-CX injection encoder by **19 CX in six occupied layers**. Backward Z constraints preserve the three Steane checks and logical Z; the initial logical phase has exactly one nonzero component on a |+> input, identifying the T site. The selected measured-zero inputs are cells 2, 9, 13, and the T site is cell 7. Unused preparations and an empty solver layer were removed by [emit_encoder.py](emit_encoder.py). The existing injection verification, double-cat check, final T-dagger layer, and v17a suffix are retained. The full pre-stage footprint stays at 15 cells and pre-CX count falls from 81 to 75.
- [schedule_prefix.py](schedule_prefix.py) keeps all per-wire dependencies and shifts every suffix operation by one common offset. It first minimizes the suffix start, then applies the stated scheduling objective. The ALAP prefix gives the best MC mean. Its native prefix overlaps suffix preparation; the final prefix T-dagger occurs at 45. Later release of some flag cells is accepted because the full-circuit loss is lower.

The new network is still form f00_0: its coordinate-basis map back to the original basis is `[1, 2, 4, 8, 21]`, and all 15 physical T-site occurrences match under that map ([classification](classification.json)). The actual parity network changed by six CX, so the gain is not attributed to coordinate renaming.

## Forms and prefix pricing

T supports use decimal five-bit coordinates. Release is the first step after the last prefix operation on cells **[1,6,13,2,9,14]**, in that order. Depth is the last prefix native step plus one; an interleaved prefix can extend until just before the round. Pre loss means only prefix noise enabled on the full circuit, through third order. All grid-free rows use separate standard 9-CX A/B/C encoders and R=33; they are diagnostic circuits and fail physical adjacency.

| Form / implementation | T support | Protection | Pre CX | Depth | Releases [1,6,13,2,9,14] | Pre-region exact loss | Grid-free total, R=33 |
|---|---|---|---:|---:|---|---:|---:|
| f00_0 / 19 CX, ALAP | 1,2,4,7,8,11,13,14,16,19,21,22,26,28,31 | Phase 0 singles/0 pairs; full c1≈0; judge pass | 75 | 46 | [42, 32, 31, 41, 32, 39] | 5.330743e-06 | 3.571751e-05 |
| f00_0 / 19 CX, compact | 1,2,4,7,8,11,13,14,16,19,21,22,26,28,31 | Phase 0 singles/0 pairs; full c1≈0; judge pass | 75 | 30 | [30, 30, 17, 30, 30, 30] | 1.327553e-06 | 3.821616e-05 |
| f00_0 / 11 CX resource | 1,2,4,7,8,11,13,14,16,19,21,22,26,28,31 | Phase 0 singles/0 pairs; full c1≈0; judge pass | 80 | 32 | [32, 32, 19, 32, 32, 32] | 1.277770e-06 | 3.628364e-05 |
| f02_0 | 1,3,4,6,8,10,13,15,16,18,21,23,27,28,30 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f04_0 | 1,2,5,6,8,11,12,15,16,19,20,23,26,29,30 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f06_0 | 1,3,5,7,8,10,12,14,16,18,20,22,27,29,31 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f09_0 | 2,3,4,5,10,11,12,13,16,17,22,23,24,30,31 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f11_0 | 4,5,6,7,12,13,14,15,16,17,18,19,24,26,27 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f13_0 | 2,3,6,7,10,11,14,15,16,17,20,21,24,28,29 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f15_0 | 16,17,18,19,20,21,22,23,24,26,27,28,29,30,31 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f17_0 | 2,3,4,5,8,9,14,15,18,19,20,21,24,30,31 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f19_0 | 4,5,6,7,8,9,10,11,20,21,22,23,24,26,27 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f21_0 | 2,3,6,7,8,9,12,13,18,19,22,23,24,28,29 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f23_0 | 8,9,10,11,12,13,14,15,24,26,27,28,29,30,31 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f24_0 | 1,2,4,7,9,10,12,15,17,18,20,23,26,28,31 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f26_0 | 1,3,4,6,9,11,12,14,17,19,20,22,27,28,30 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f28_0 | 1,2,5,6,9,10,13,14,17,18,21,22,26,29,30 | Phase 0/0; full circuit untested | — | — | — | — | — |
| f30_0 | 1,3,5,7,9,11,13,15,17,19,21,23,27,29,31 | Phase 0/0; full circuit untested | — | — | — | — | — |

The compact variants use the existing [ablate.py](../MAIN/ablate.py) time regions. For the interleaved ALAP circuit, [price.py](price.py) uses saved prefix-operation provenance, otherwise a time cutoff would wrongly include the suffix blocks. Noise before a prefix operation, including its preceding idle gap, belongs to that prefix; data waits before suffix operations belong to the suffix. For the ALAP grid-free R=33 diagnostic, the same prefix network is rescheduled ALAP with all prefix operations finishing by 32. It is not the R=46 clock schedule transplanted unchanged. The existing sep33 reference is about 3.55e-5.

## Full grid circuits

Each MC seed uses 1e8 shots. `c1` is the first-order loss printed by exact2, including p=1e-3. All reported third-order totals satisfy |c1|<1e-12. The acceptance estimate does not rank candidates.

| Circuit | R | CX | c1 | 2nd | 3rd | Exact total | exp(-A1) | MC 0 / 1000 / 2000 | MC mean | Seed-0 acceptance | Files |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| v17a | 50 | 209 | 3.182600e-19 | 5.707720e-05 | 2.537690e-05 | 8.245410e-05 | 0.54287 | 8.393188e-05 / 8.355687e-05 / 8.293009e-05 | 8.347295e-05 | 0.543 | [qasm](inputs/v17a.qasm), [json](inputs/v17a.json) |
| init_state_d5_s1 | 49 | 208 | 3.182600e-19 | 5.707720e-05 | 2.533400e-05 | 8.241120e-05 | 0.54576 | 8.417347e-05 / 8.228549e-05 / 8.439325e-05 | 8.361740e-05 | 0.54596 | [qasm](init_state_d5_s1.qasm), [json](init_state_d5_s1.json) |
| encoder19 | 47 | 203 | 2.516500e-19 | 5.707720e-05 | 2.581080e-05 | 8.288810e-05 | 0.5525 | 8.395208e-05 / 8.440232e-05 / 8.548979e-05 | 8.461473e-05 | 0.55258 | [qasm](encoder19.qasm), [json](encoder19.json) |
| init_state_d5_s1_idle | 48 | 208 | 3.182600e-19 | 5.663540e-05 | 2.375490e-05 | 8.039030e-05 | 0.54917 | 8.280370e-05 / 8.306007e-05 / 8.101909e-05 | 8.229429e-05 | 0.54937 | [qasm](init_state_d5_s1_idle.qasm), [json](init_state_d5_s1_idle.json) |
| encoder19_idle | 46 | 203 | 2.849600e-19 | 5.661330e-05 | 2.409910e-05 | 8.071240e-05 | 0.55612 | 8.168320e-05 / 8.255842e-05 / 8.135326e-05 | 8.186496e-05 | 0.55642 | [qasm](encoder19_idle.qasm), [json](encoder19_idle.json) |
| encoder19_alap | 46 | 203 | 2.923600e-19 | 5.622620e-05 | 1.983790e-05 | 7.606400e-05 | 0.52776 | 7.742218e-05 / 7.508943e-05 / 7.657090e-05 | 7.636083e-05 | 0.52782 | [qasm](encoder19_alap.qasm), [json](encoder19_alap.json) |

Ranked by MC: **encoder19_alap**, encoder19_idle, init_state_d5_s1_idle, v17a, init_state_d5_s1, encoder19. The two unscheduled synthesis variants lose on the required mean despite reducing gates/depth. The ASAP variant has only a second-order screen (5.73086e-5), so it is not assigned a final rank. An early emission experiment, init_state_d5_s0, used barrier counts instead of native times; it is retained as a negative implementation receipt, not a delivery.

## Verification and remaining limits

- [encoder19_alap.check.json](encoder19_alap.check.json), [encoder19_idle.check.json](encoder19_idle.check.json), and [init_state_d5_s1_idle.check.json](init_state_d5_s1_idle.check.json) contain explicit format, class, correctness, and acceptance verdicts at 1e6 shots. All pass, and every physical T-axis single and pair was checked again on the synthesized circuits.
- Full-fault exact screens and three-seed results are in each candidate’s `.exact.log` and `.mc.log`. The MC command is the requested `mc3.py`; [results.json](results.json) collects the measured numbers. Individual MC SEMs are about 1.0–1.1e-6. The reported gain is the observed three-seed mean difference, not an official submission result.
- Every QASM has a sibling JSON with `data_qubits`. Grid-free artifacts are marked `grid_free: true`; only the full-grid candidates above are deliveries. Remote calculations used at most 20 lane cores on jerry and 8 on hippo, with all three BLAS/OpenMP variables set to 1. No other lane’s files or jobs were changed.
- This does not establish an optimum over all 16 forms, all encoders, or all schedules. The 15 alternative physical forms remain open because the successful-circuit completion branch was reached.
