# Chamberland–Cross flag route (CC)

All paper quotations below are from [Chamberland & Cross, arXiv:1811.00566, saved text](paper/cc1811.00566.txt); page numbers are the PDF page numbers. Measurements below are from the supplied contest judge at `p=1e-3`, unless explicitly marked as paper results. No submission was made.

## Protocol extracted from the paper

* **Measured logical operator and eigenstate.** Section 3 states that the Steane code is `[[7,1,3]]` and that “the logical Hadamard operator is given by H = H^{⊗7}” (p. 4, §3). Equation (4) defines `|H> = cos(pi/8)|0> + sin(pi/8)|1>`; the surrounding text says it is the `+1` eigenstate of Hadamard (pp. 2–3). Equation (6) defines `|−H> = Y|H>` as the `−1` eigenstate (p. 3).
* **Relation to the contest state.** Equation (7) gives the paper's magic state exactly as `|A_{π/4}> = (|0> + exp(iπ/4)|1>)/sqrt(2) = exp(iπ/8) H S† |H>` (p. 3, Eq. (7)). Therefore the algebraic inverse is `|H> = exp(−iπ/8) S H |A_{π/4}>`. The contest encoder has the opposite physical phase convention; exact noiseless verification of the contest encoder inferred the equivalent implementation map `|T_L> -> |H_L>` as physical `H` then `S†`, and the inverse as `S` then `H`. This direction is **inferred from the contest encoder and exact judge correctness**, not asserted by the paper.
* **Controlled-H and the flag.** Figure 2(a) is the nondestructive H measurement: a `|+>` control applies controlled-H to the data and is measured in X. Figure 2(b) says the controlled-H gate is decomposed into `T`, `CZ`, and `T†` (p. 4, Fig. 2 caption); every `CZ` was routed as neighboring `CX` plus one-qubit Clifford gates. Section 3 says flag qubits can measure logical H with one extra ancilla and that if a fault spreads to a data error of weight greater than one, the flag detects it (p. 4). Figure 5(a)'s caption says: “If a single fault results in a data qubit error of weight greater than one, the circuit will flag (the `|0>` state will be measured as `−1`) and the `|H>` state preparation scheme will begin anew” (p. 5, Fig. 5 caption). The detection circuit is `|H>_nf -> H_m^{f1} -> EC` (Fig. 5(b), p. 5). The paper says the error-detection scheme uses 10 qubits (p. 4).
* **Repetition.** The Fig. 5 error-detection protocol has one flagged logical-H measurement `H_m^{f1}` followed by EC; a flagged/nontrivial result rejects that attempt. The separate correction protocol in Fig. 6(b) repeats `H_m^{f2}` three times; its caption says that a flag in the third measurement causes an extra EC round (p. 6, Fig. 6 caption). Figure 6(a) adds two flags to localize faults near the fourth controlled-H and requires the full six-bit syndrome rather than separate CSS syndromes (p. 6, Fig. 6 caption). Appendix A.3 explains why three measurements are required to disambiguate `+−` outcomes (p. 17, footnote 9). Thus “three repetitions” belongs to the correction variant, not the one-measurement error-detection variant used for the compact candidate.
* **Postselection and correction.** For Fig. 5, the flag is accepted only when its Z measurement is trivial (`+1`, raw bit 0); Appendix A.2 says a nontrivial H-measurement outcome is rejected and that an EC measurement that is nontrivial is rejected (pp. 14–15). The OpenQASM implementation expresses rejection as `// POSTSELECT(0)` on the logical-H X record and flag Z record. The literal implementation additionally postselects all six Steane syndrome records; that version fails the contest acceptance floor after grid routing. A retry loop is not represented in OpenQASM: judge postselection has the same conditional-state semantics.
* **Paper's reported logical-failure numbers.** Table 4 reports, for the level-1 error-detection `|H>` preparation, `Pr[accept] = (1−p)^75` and logical error probabilities `(p_x,p_y,p_z) = (9.95, 4.41, 7.87) p^2` (p. 26, Table 4; coefficients rounded there to three digits). The paper's conclusion summarizes this as accepting “around 80%” and having logical error rates “near 10−4” around physical `p = 3×10−3` (p. 10). These are **paper-model results**, not predictions under the contest's grid/idle noise.

## Circuits

`cc_hm_best.qasm/.json` is the best valid compact circuit: the contest's `|T_L>` encoder, the inferred `H,S†` map, one Fig. 5(a) flagged logical-H measurement, postselection on its two `+1` records, and the inverse `S,H` map. The final placement is `data_qubits = [20,21,15,28,26,33,27]`. It uses 73 neighboring CX gates, 161 noise channels, 14 distinct physical cells (7 data + 7 routing/helper cells), and judge execution end step 57 (Qiskit depth 59). The exact sampler reports rotation rank 5; the judge source sets `MAX_RANK = 22`, so this is below the cap. The placement screen tested 120 Sabre initial-layout/seed combinations; the reported candidate is the best exact second-order result.

`cc_ec_flags.qasm/.json` adds six routed single-ancilla Steane syndrome measurements but postselects only the two Fig. 5(a) flag/H records so it remains acceptance-valid. It has 172 CX, 16 touched cells, and end step 125. `cc_ec.qasm/.json` is the literal postselected version with all eight records required to be zero.

All emitted two-qubit operations are `cx` on grid neighbors. Controlled-H was decomposed into `h,s,sdg,t,tdg,x,cx` only; no unsupported gate or custom conditional operation is present. The compact QASM contains 8 `t` and 7 `tdg` instructions (15 non-Clifford gates total), and the EC variants have the same non-Clifford count.

## Judge results

### Compact candidate (`cc_hm_best`)

`tprep.check(..., shots=10**6, seed=0)`:

```text
format PASS; class PASS; correctness PASS
acceptance PASS (0.7754, floor 0.5)
score 1-F = 0.0250759 ± 0.00016; 2q+ gates = 73
```

`exact2.py --third` reports the exact judge message `c1 != 0: the third-order term is implemented for c1 = 0 only; skipped`. Its full output gives rotation rank 5, first-order loss `1.3265e-2`, second-order `1-F = 2.53091e-2`, and `A1 = 0.272949` (`exp(-A1)=0.76113`). Because the first-order term is nonzero, there is no exact third-order number from this tool; this is an evaluator limitation, not a judge rejection.

The required 10^8-shot checks, run with `fast_check.check(..., procs=8)`, are:

| seed | 1-F | SEM | acceptance |
|---:|---:|---:|---:|
| 0 | 0.0248939146372 | 1.64e-5 | 0.77568194 |
| 1000 | 0.0248645698136 | 1.64e-5 | 0.77569671 |
| 2000 | 0.0248588224152 | 1.64e-5 | 0.77562242 |
| **three-seed mean** | **0.0248724356220** | — | — |

Every seed passed the judge gates; the seed-0 result is recorded in `mc_seed0.log`, and the other seeds in `mc_seed1000.log` and `mc_seed2000.log`.

### Literal EC variants

* `cc_ec_flags`: `tprep.check` at 10^6 shots passes format/class/correctness/acceptance with `1-F = 0.0944049 ± 0.0003`, acceptance `0.7135`, and 172 CX. `exact2.py` gives second-order `1-F = 0.115767`, first-order `4.7758e-2`, and again skips `--third` because `c1 != 0`.
* `cc_ec`: requiring all six syndrome records as well as the flag/H records gives the exact judge result `acceptance: FAIL (0.4668, floor 0.5)` at 10^5 shots (the exact judge message). Its second-order `1-F` is `0.0886991`, with first-order `2.9787e-2`; `--third` is skipped for the same explicit `c1 != 0` reason. It is not a valid submission under the contest acceptance rule.

## Comparison and verdict

| circuit | exact 2nd-order 1-F | MC 3-seed mean | acceptance | CX | touched cells | end step |
|---|---:|---:|---:|---:|---:|---:|
| CC compact full/pre-stage | `2.53091e-2` | `2.48724e-2` | `0.7756` | 73 | 14 | 57 |
| current v12 full | `1.12195e-4` (3rd `1.14313e-4`) | `1.1327e-4` | PASS | 115 | 16 | 41 |
| v11 cultivation pre-stage (lines 1–204) | `1.46e-5` (reported in `PRE/REPORT.md`) | — | `0.74` | — | 15 (reported) | 32 |

**(a) Full circuit:** CC is decisively worse than v12: its true-mean loss is about 219× larger (`2.487e-2` versus `1.133e-4`) despite 42 fewer CX gates. The mechanism is the nonzero first-order term from the physical `T/T†` controlled-H decomposition plus long routed/idle windows; the paper's `O(p^2)` coefficient assumes its complete fault-tolerant EC/error-detection construction and its own noise model, which the grid implementation does not reproduce.

**(b) Pre-stage:** CC is not a useful cultivation replacement. It touches one fewer cell than the reported v11 pre-stage and uses fewer CX in this placement, but ends at step 57 instead of 32 and has `c1 p = 1.3265e-2` versus the cultivation pre-stage's measured `1.46e-5` loss. Its 3-seed mean is roughly 1,700× higher. The compact Fig. 5(a) component is therefore useful only as a negative result: the complete paper protocol cannot be made acceptance-valid and competitive on this 6×6 judge with this footprint/routing.
