# Structural redesign experiments — 27 October 2026

## Outcome

**No new legal circuit in this run beats MAIN/v37j. There is no SOTA claim and no new submission candidate.**

Three structural implementations were completed: a native joint encoder/phase network, full-block output
teleportation with an affine frame, and shared GHZ hook verification through existing precheck readouts.
The repository contains their generators, selected QASM/ordered-output metadata, failed controls, exact
prices, and official-check evidence. The incumbent remains the best legal circuit verified in this run.

All results below use the organizer's noise model at p = 0.001. Lower loss is better. The reported exact
loss is a deterministic all-orders numerical expectation, not a Monte Carlo draw or exact symbolic number.

| Circuit | Geometry | CX | Ticks | Expected loss | Acceptance | Decision |
|---|---|---:|---:|---:|---:|---|
| Incumbent MAIN/v37j | 6×6 grid | 412 | 49 | 3.5870950034704206e-5 | 0.5010179047299785 | Keep incumbent |
| Native joint encoder and phase network | 6×6 grid | 134 | 31 | 8.489600747077256e-5 | 0.6890119163514336 | Valid, 2.37× incumbent loss |
| Fresh B-block output teleportation | 6×6 grid | 412 | 49 | 3.672998861770659e-5 | 0.5005215715582058 | Valid, 2.395% worse |
| Shared GHZ flags and square ending | Unrestricted connectivity | 139 | 21 | 3.26709931735252e-5 | 0.6853018171181722 | Abstract mechanism only |
| Same architecture, completed native bridge control | 6×6 grid | 724 | 391 | 0.18268418215320847 | 0.0003347070706826457 | Fails acceptance |

All five pass the separate raw noiseless output check, including all six code stabilizers and the logical
target. That does not make the unrestricted circuit grid-valid or the native bridge circuit admissible.
The official acceptance threshold is 0.5; this repository uses 0.5002 as a selection margin. The
`grid_valid` field in the independent receipts describes adjacency only, not overall admissibility.

The five authoritative recomputations are [baseline](evidence/verified_baseline_v37j.json),
[compact prefix](evidence/verified_compact_rank5.json), [teleportation](evidence/verified_b_output_teleport.json),
[abstract flags](evidence/verified_joint_flags_abstract.json), and
[native flags](evidence/verified_joint_flags_native.json). Each contains QASM SHA-256, ordered output
qubits, dependency versions, source pins, and the full raw and noisy result.

## The leaderboard target

The [official leaderboard](https://snuquantums.github.io/snu-qff2026/hackathon.html) was retrieved at
2026-10-27 07:43:30 UTC, or 16:43:30 KST. The sanitized public snapshot is
[leaderboard.json](evidence/leaderboard.json).

| Rank at retrieval | Team | Official sampled loss | CX | Sampled acceptance |
|---|---|---:|---:|---:|
| 1 | Placeholder | 3.0423837010265e-5 | 277 | 0.50059432 |
| 2 | 초정밀모델제어학회쨩 | 3.30430020090153e-5 | 412 | 0.5010138 |

The leader has 32.77% fewer CX and a 7.93% lower sampled score than the second-place entry in this snapshot.
The public data does not reveal the winning circuit or its exact expected loss. Its sampled score must
not be compared with our exact expectation as if the two were the same statistic. The first-place circuit
cannot be reverse-engineered from its gate count, score and acceptance alone.

## What was implemented and learned

### 1. Joint native encoder and phase synthesis

[PREFIX20261027](../PREFIX20261027/REPORT.md) jointly chooses the initial product basis, the encoder and
the 15 phase forms. It preserves the fifth binary coordinate used for fault detection. It searches
backwards from the required encoded output and flag state, allowing any valid five-dimensional product
endpoint instead of restoring a fixed intermediate encoder after each parity computation.

The best source uses 22 CX; 14 transfer CX and the fully preserved 98-CX T14 terminal/resource circuit
produce a complete 134-CX, 31-tick native circuit. All preparation and transfer operations are physically
present and noisy. The phase identity is checked over all 32 binary inputs, and the canonical artifact
rebuilds byte for byte.

The search included 122 initial phase-placement screens, 56 variants of 28 synthesized networks,
32 exposure-weighted variants, ten post-phase projectors and 26 final phase-placement variants. These
were screening budgets, not 246 independent full official evaluations. Selected full all-orders scores
and failed controls are retained in the lane.

The first short network had three harmful single-fault locations. Further network and schedule changes
removed those single-fault failures, but the best complete loss remains 8.4896e-5. Zero harmful singles
therefore did not preserve the incumbent's suppression of combined faults. The 67.5% CX reduction is a
size result, not a fidelity improvement.

### 2. Output teleportation and affine corrections

[FRAME20261027](../FRAME20261027/REPORT.md) reverses the final B-to-data transversal CX layer, measures
the old data in X, keeps B as quantum output, and applies the permitted affine logical Z frame.
Fresh initialization of three resource sources fixes the raw code-state failure of the naive rewrite.

The repaired full-block construction is correct and has no harmful single faults, but its full loss is
2.395% worse. All 126 nonempty proper subsets of partial output relocation fail raw code correctness.
Ten C-readout choices and ten source-herald variants do not yield an improved admissible result. A
28-case affine syndrome recovery screen produces seven zero-single-fault cases, all of which lose badly
when fully priced. The lane completed 28 noisy contractions in total.

The local frame-aware evaluator is part of the deliverable. Shared qtools rejects frame declarations;
its low-level zero-frame parser must not be used to price this candidate. The extension incorporates
frame records into the logical observables and their fault signatures, and the official raw check is
performed separately with the frame included.

### 3. Shared GHZ hook verification

[NATIVE20261027](../NATIVE20261027/REPORT.md) reconstructs encoded injection, both Steane prechecks,
two logical-axis GHZ checks and a square terminal arrangement. It copies three GHZ Z-parity checks into
each existing precheck block after that block has interacted with the data. These records detect hook
faults without adding separate flag qubits. The released blocks exchange final resource roles.

Against the reconstructed unverified GHZ control, the exact second-order coefficient falls from
43.4166666667 to 28.06. The full abstract loss improves from 4.67938718912e-5 to 3.26709931735e-5.
Higher orders remain material. This abstract result also does not beat the repository's already
documented DEEP abstract result of 2.7185e-5; the latter's circuit was not present in the checked snapshot.

The complete native control jointly chooses seven terminal squares, code labels, orientations and helper
positions, then implements earlier remote CX operations with exact bridges that restore unknown
intermediate states. The last two CX layers are local. The resulting 724 CX and 391 ticks make acceptance
collapse to 0.0003347. This completed bridge control is unusable because it fails acceptance. The result
does not exclude other placements, native preparation circuits, or implementations of shared GHZ flags.

### 4. Exact completion of deterministic record parities

[record_contract.py](record_contract.py) enumerates the small noiseless rotation-state Pauli stabilizer
space and solves for every deterministic affine parity of existing records. It keeps the full complex
Pauli phase when recovering each parity's reference bit. An independent four-example review checks Bell
parities, repeated magic-state readout, a negative reference, and a nonorthogonal rotation basis with
complex phases; see [the review](../FRAME20261027/record_contract_review.json).

For v37j, the declared detector rank is 71 and the complete affine rank is 76. The five missing parity
basis rows are c11; c286 XOR c292; c312; c330 XOR c331 XOR c333 XOR c336; and c348. Simply adding them gives
loss 3.5870215892519594e-5 but acceptance 0.4897193862927524, so it is invalid. This is not the different
detector trade from the interrupted conversation, which claimed higher acceptance; that earlier trade's
artifact was not recovered and is not claimed as a result of this run.

The first compact-prefix control has declared rank 36 and complete rank 36: no deterministic affine
record parity was omitted. Its three harmful single faults cannot be removed merely by adding another
deterministic parity of those existing records. That conclusion is about this control, not all compact
prefixes or nonlinear acceptance predicates.

Completeness is limited to unpostselected circuits with rotation rank at most eight, with the raw check
establishing that the supplied detector rows are valid. It is not a general POSTSELECT or Boolean decoder
synthesis algorithm.

### 5. Physical parity checks and counterfactual noise cuts

[parity_meters.py](parity_meters.py) generates real two-CX temporal parity meters on native neighbors,
using an available cell and no new tick. It screened 107 slots and fully priced 32. Its best meter only
changes an earlier prefix control from 1.78328e-4 to 1.75111e-4, so it is not competitive. The selected
witness and the complete result ledger are retained.

[counterfactual.py](counterfactual.py) diagnoses that earlier prefix by selectively removing noise
channels. With only source operations before tick 25 noisy, loss is about 9.03e-5; with only later
source operations noisy, loss is about 3.50e-5. Following idle noise stays attached to its source operation.
These are nonadditive counterfactuals, not an achievable savings estimate or a rigorous loss budget.

## Validation and numerical provenance

The baseline also completed a fresh official 100,000,000-shot seed-zero check using the pinned judge:

- sampled loss: **3.549216241018776e-5**;
- standard error: **7.22e-7**;
- sampled acceptance: **0.50095567**;
- format, simulator class, raw correctness and acceptance: passed;
- elapsed time: 257.6 seconds with two processes on this worker.

This is a fresh sample of the canonical baseline, not the selected leaderboard redraw. Its receipt is
[baseline_official.txt](evidence/baseline_official.txt). B-output teleportation passed a one-million-shot
official check; the final compact prefix passed its own one-million-shot check in
[best_validate.json](../PREFIX20261027/best_validate.json). Their exact expectations are already inferior,
so neither was promoted to another 100-million-shot run.

Source pins:

- repository parent: `020cd0364b8f75d167ca203fd9e615ea100c9bf8`;
- official judge: `76fe47c0324f1c1f8b72a7d55af200e88043b522`;
- unchanged qtools evaluator: `94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f`.

Earlier search receipts contain evaluator hash `64107f0e...`: the local source transfer had added a final
blank line to the evaluator files. All shared evaluator files were restored to their exact repository
bytes before the five independent final recomputations. There was no semantic evaluator change. The
authoritative `verified_*.json` receipts use the pinned `94d0bfed...` version. Original baseline and T14
input bytes were also restored, and the compact prefix was rebuilt and repriced after that restoration.

The sparse contraction diagnostics are small relative to every reported design gap. Frame diagnostics
are not claimed to be a rigorously propagated bound on normalized loss. The full expected values and
their input hashes, rather than low-order coefficients or single lucky samples, determine the verdict.

## Reproduce

Use the existing repository environment described in [RESOURCES](../../../docs/RESOURCES.md). A fresh
environment can use the pins in [requirements.txt](requirements.txt) plus the official source and wheel
locations/hashes in [dependency_sources.json](evidence/dependency_sources.json). These experiments used
Python 3.12, tprep 3.0.3 and xtim 3.1.3+qff2. Install the official judge editable from
`upstream/snu-qff2026-problem` at the pinned commit; do not edit its sources.

From the repository root:

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=work/tools:upstream/snu-qff2026-problem
.venv/bin/python work/lanes/REBUILD20261027/verify_results.py baseline_v37j
.venv/bin/python work/lanes/REBUILD20261027/verify_results.py compact_rank5
.venv/bin/python work/lanes/REBUILD20261027/verify_results.py b_output_teleport
.venv/bin/python work/lanes/REBUILD20261027/verify_results.py joint_flags_abstract
.venv/bin/python work/lanes/REBUILD20261027/verify_results.py joint_flags_native
.venv/bin/python work/lanes/PREFIX20261027/reproduce.py
.venv/bin/python work/lanes/FRAME20261027/review_record_contract.py
```

To repeat the full official baseline check:

```bash
.venv/bin/python work/fast_check.py work/lanes/MAIN/v37j.qasm work/lanes/MAIN/v37j.json 100000000 2
```

`verify_results.py` bypasses adjacency only for its explicitly labeled abstract case in a process-local
scope. It restores the original function and never puts that result in the shared grid-valid cache.
Other cases use ordinary adjacency checks or the explicit frame-aware extension.

The three lane manifests list selected generators, controls and witnesses. The integration manifest
`selected_files.json` covers the complete delivered file set and hashes. Existing baseline, T14 inputs
and qtools sources remain in the parent commit; the change adds experiment files only.

## Engineering conclusion

The tested bottleneck is suppression of combined faults in a physically prepared, native circuit.
Joint synthesis made the prefix much smaller but lost that suppression. Shared flags repaired a measured
fault-pair mechanism abstractly, while the completed bridge realization lost the benefit to routing and
idle noise. Output relocation proved correct but did not reduce loss. These are reproducible outcomes
that constrain the next design; none justifies replacing v37j.

Primary rules: [official problem at the pinned commit](https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/problem.md).
