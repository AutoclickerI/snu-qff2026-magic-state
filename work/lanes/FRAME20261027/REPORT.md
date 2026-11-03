# FRAME20261027: output teleportation and affine record contracts

## Outcome

No improvement over MAIN/v37j was found in this bounded lane. The best legal candidate is `cand/btele_fresh`, with loss **3.672998861770659e-5**, acceptance **0.5005215715582058**, **412 CX**, and **49 native ticks**. The reproduced MAIN/v37j baseline is 3.58709500347e-5 at acceptance 0.50101790473. The teleportation candidate is approximately 2.395% worse in loss and does not reduce CX count.

The candidate is useful as a validated architectural building block, not as a new submission. Its output is the former B verification block, its final old-data readout supplies an affine logical Z frame, and all six raw output code stabilizers are +1. The naive construction fails that raw condition; fresh initialization of three B/C resource sources repairs it.

All lane processes completed. No submission, remote write, commit, push, or shared qtools edit was performed by this lane. The root task owns official pinned-judge sampling and the eventual repository packaging.

## Construction and raw correctness

The seven-qubit arrays below use the code-coordinate order, not numerical order:

| Role | Physical qubits |
|---|---|
| Old data D | 6, 20, 19, 10, 2, 22, 16 |
| A verification block | 0, 14, 13, 9, 1, 21, 15 |
| New output B | 12, 26, 25, 11, 3, 28, 17 |
| C resource/check block | 18, 27, 24, 5, 4, 29, 23 |

`teleport_b.py` reverses the final transversal B-to-D CX layer to D-to-B. It replaces the seven final B X measurements with X measurements of D and moves the output metadata to B. Three Steane X-syndrome parities of the D records remain detectors. The logical correction is `FRAME_Z(0) c[400] ... c[406]`; `FRAME_X` is zero. The prior resource source measurements c352, c353, c361 become fresh RX preparations and disappear from detector expressions.

The resource sources are q26 and q28 at tick 31, and q29 at tick 30. Their old X measurement outcomes were random phase information that the original B readout detector expressions could absorb. Once B is retained as quantum output, those phases cannot simply be ignored. The naive construction gives zero expectation for raw X stabilizers and nondeterministic new detectors. Reinitializing these three sources produces a valid output.

For `btele_fresh`, the pinned official noiseless exact checker reports no errors, raw infidelity 0, rotation rank 5, and all six stabilizers equal to 0.9999999999999997. The lane-local fault analysis finds no harmful single-fault components. Its QASM SHA256 is `26e80bac7623146cd750628843340ce7c9c30ed24fd73aa87829325eb3a8fd50`.

The observed B/C resource before the final B-to-C layer is a correlated duplicated Steane-code support, rather than two separately available logical-zero blocks. Its physical cells form the path 12–18–24–25–26–27–28–29–23–17–11–5–4–3. The existing late transport reuses several of these cells, so replacing this resource with a compact standalone preparation requires a joint transport/resource redesign. This lane did not establish a cheaper native replacement.

## Bounded experiments

Every quoted noisy score below includes all independent noise channels at the pinned model's p=0.001. The evaluator contracts their probability distribution deterministically; these are not sampled rankings. Raw correctness was checked before scoring.

| Experiment | Scope | Best or representative loss | Acceptance | Result |
|---|---:|---:|---:|---|
| Fresh full-block teleport | 1 | 3.67299886177e-5 | 0.500521571558 | Raw valid; behind baseline |
| Partial output relocation | All 126 nonempty proper subsets | Not priced | — | Every subset fails raw code correctness |
| C readout, three syndrome checks | 1 | 5.81194224288e-5 | 0.501201380507 | Raw valid; worse |
| C readout, syndrome plus total parity | 1 | 4.10486107059e-5 | 0.500531460298 | Raw valid; worse |
| C readout, total parity only | 1 | 3.35906056825e-3 | 0.507415432153 | Raw valid; much worse |
| Drop one C readout check | All 7 choices | 4.10142020432e-5 | 0.501973781874 | Best choice is cdrop2; every choice worse |
| Herald fresh source preparations | 10 specified variants | 3.66287480521e-5 | 0.498020799609 | Lowest loss heralds all three; fails acceptance |
| Accept one extra D syndrome sector, affine frame | 28 raw/single-fault cases; 7 fully scored | 2.30220611841e-4 | 0.505738798855 | Best full score is recover_d6_p2; much worse |

The ten source-herald variants cover each source alone and all three together, followed by six specified trades against singleton resource flags. All ten are raw valid. None meets the baseline loss and acceptance simultaneously. Removing other resource flags recovers little acceptance because remaining checks still constrain those faults.

The recovery family accepts the old-data syndrome set {0,v}, for each of the seven nonzero three-bit syndromes v. It retains two independent parity checks and tries all four whole-block Pauli frame corrections on the extra sector. All 28 variants are raw valid. The seven logical-Z corrections have no harmful single faults, but their full losses range from 2.30220611841e-4 to 2.56792449635e-4. The remaining 21 corrections have harmful single faults and were not fully scored. This is a concrete example where a zero single-fault coefficient is insufficient for ranking.

Overall, the lane completed 28 noisy contractions, 126 raw checks of mixed output subsets, and the 28-case recovery raw/single-fault sweep. These are finite families around MAIN/v37j and the repaired B-output construction. They do not rule out other teleportation resources, nonlinear acceptance rules, different prefixes, or different native layouts.

## Evaluator method and limits

`frame_tools.py` provides a lane-local affine-frame extension without changing qtools. It multiplies each pulled-back decoded X observable by the record Pauli for the Z frame, and each decoded Y observable by the record Pauli for the XOR of X and Z frames. It adds the corresponding record-flip parities to the fault signatures and applies constant frame signs. The existing sparse-Walsh channel contraction then computes acceptance and the decoded target moment.

The extension supports the existing H/CX/T/reset/measurement frontend, zero-reference deterministic detectors, affine whole-block logical frames, and no POSTSELECT. It is not a general implementation of every official allowed gate. The public qtools pricing entry point rejects framed circuits. Its low-level zero-frame parser does not incorporate frame declarations, so framed circuits must use the frame-aware evaluator. The official raw check is separate and includes the logical frame.

The saved `kernel_omission_sum` is the sum of contraction kernel omission diagnostics, typically below 4.5e-13 here. It is not asserted to be a rigorously propagated bound on the final normalized loss. Reported digits are deterministic evaluator outputs, subject to floating-point and contraction tolerances. This uncertainty is far smaller than the observed gaps but should not be confused with exact symbolic arithmetic.

## Independent review of record_contract.py

The root lane's exact completion calculation is mathematically consistent for its stated unpostselected circuit subset. Let B span the X supports of the pulled-back rotations. The rotation state is supported on computational basis vectors in span(B). A Pauli therefore acts within that support through its physical X mask and the dual Z coordinates `w_j = parity(B_j & z)`. Any Pauli with an X mask outside span(B) has zero expectation. Exhaustively enumerating the 4^rank(B) Pauli coordinates inside the support finds every unsigned Pauli stabilizer of the rotation state. Quotienting record columns by this stabilizer subspace and taking the binary kernel finds every deterministic affine parity of the records.

Ignoring signs while finding the binary relation space is safe because the code subsequently multiplies the original record Paulis, including their complex phases, and evaluates each resulting relation to recover its reference bit. The Z coordinates must use the dual pairing above; they are not simply coordinates of z in B. The implementation handles that distinction correctly, including a nonorthogonal B.

`review_record_contract.py` independently checked four small examples. Three use the pinned official exact simulator: a Bell record parity, a repeated X readout of a magic state, and a deterministic negative reference produced by four T rotations. The fourth uses a direct four-amplitude matrix calculation with nonorthogonal rotation basis [3,1], complex Pauli phases, and two negative-reference relations. The inferred affine relation closure matched every enumerated record parity in all four examples. Results are saved in `record_contract_review.json`.

This is completeness of deterministic **affine parities** of the unpostselected noiseless records, at rotation rank at most eight. It is not completeness of all Boolean acceptance predicates or of record relations conditional on arbitrary POSTSELECT. `complete(m,dets)` assumes that supplied detector rows are valid; the audit wrapper establishes that via the separate raw checker. The completion does not itself prove correct raw output. No defect was found, and no root-lane source was changed.

## Reproduction and selected artifacts

Run from the repository root with the pinned `.venv` and one CPU per process:

```bash
PYTHONPATH=work/tools:upstream/snu-qff2026-problem OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/FRAME20261027/teleport_b.py
PYTHONPATH=work/tools:upstream/snu-qff2026-problem OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/FRAME20261027/recover_syndrome.py
PYTHONPATH=work/tools:upstream/snu-qff2026-problem OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/FRAME20261027/review_record_contract.py
```

The other generator entry points are `mixed_output.py`, `c_contracts.py`, and `resource_herald.py`. The best candidate is the QASM/JSON pair `cand/btele_fresh`, accompanied by its full pricing and single-fault results. `all_priced_results.json` collects all 28 noisy results. The mixed-output and recovery summary JSON files preserve every tested case, including invalid and unpriced cases. `selected_files_manifest.json` records the selected source, report, evidence, and candidate hashes for handoff.
