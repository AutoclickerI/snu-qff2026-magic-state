# FLOOR — independent lower-bound audit
Verdict: **BOUND CONFIRMED under the inspected STANDARD judge as written; no admissible counterexample found.**
True conditional expected loss >= **2.1892512824770077772e-5**, hence the requested **2.18925128e-5**.
A board draw near 2e-5 is not excluded; neither is a mean near 2.25e-5. Attainability of either is unproved.
Independence: source audit, own spectral derivation and ten tail tests saved in `INDEPENDENT.md` before reviewer 18/CONTRACT were read.
## Judge ground truth (source root: upstream/snu-qff2026-problem/)
| Item | Charge / enforcement |
|---|---|
| CX | D2(p): II 1-p; each other Pauli p/15; adjacent pairs only (`tprep/noise.py:117`, `qasm.py:194`). |
| 1q Clifford, Pauli, T/Tdg, id | D1(p): I 1-p, X/Y/Z p/3, after each gate (`noise.py:115`). |
| Initial/reset | First use X_ERROR(p) unless reset; R X_ERROR(p), native RX Z_ERROR(p); never-used wires ideal zero (`noise.py:104–114`). |
| Measurement | X_ERROR(p) before M, Z_ERROR(p) before MX; D1(p) after **every** measurement, even discarded (`noise.py:108–112`). |
| Native X | Eligible H,M / H,M,H -> MX; R,H -> RX; folded H has no own noise/time (`qasm.py:102–145`). |
| Idle | ASAP converted native operations; gaps and terminal waiting through last occupied step; none before first use, before reset, after terminal M (`noise.py:54–88`). |
| Barrier / TICK | Barrier synchronizes named wires without duration; trailing barrier ignored; Stim TICK ignored (`qasm.py:247–253`, `noise.py:57`). |
| Decode | Six ideal stabilizer measurements; separate Hamming X/Z correction; final syndromes never reject (`check.py:18–22,273–311`). |
| DETECTOR | Ideally deterministic XOR, possibly conditional on POSTSELECT; compare with ideal reference, including reference 1 (`exact.py:verify`). |
| POSTSELECT / acceptance | Explicit XOR=0/1; ideal accepted probability >1e-12; noisy measured acceptance >=0.5 (`exact.py`, `check.py:54`). |
| FRAME_X/Z | Free affine logical Pauli signs; both declarations or automatic inference; no physical correction gates (`check.py:224–265`). |
| Records | Latest classical write; ideal decode records inaccessible (`qasm.py:198–240`, `check.py:146–149`). |
| Correctness | Accepted raw state must be framed T_L before decoding; code-space/target tolerance 1e-9 (`exact.py:verify`). |
| Other free/legal features | Declarations and ideal judge tail; folded H only. Physical conditionals, participant noise and MPP rejected (`qasm.py`, `parse.py`). |
## Loopholes, smallest decisive tests, and outcomes
Each test sought a sub-bound complete two-layer price or violated source assumption; either would earn expansion to a full counterexample.
| Loophole | Test and result; closure |
|---|---|
| Early last operation / no final idle | Saved native schedules include final measurement tick; earlier output accumulates idle. `groundtruth.json`; **certified exclusion**. |
| Barrier/native-H timing | Converted RX/MX and barriers across folds tested; last actual native tick used throughout; **certified exclusion**. |
| Final M/R/never-used output | Public tprep.check and raw verify reject M, MX, R, RX, unused-output and postselected M; raw loss >=0.5; **certified exclusion** by separability. |
| Free logical frames / S / Pauli gates | WHOLEEND exact tail prices: each physical one-layer ending 1.16252525335e-5, raw correct; free frame changes no tick. **Certified exclusion** by branchwise Pauli covariance. |
| Only charge final layer | One idle layer 1.16252525335e-5; one helper-CX layer 7.44545573927e-6. Saved in `counterexamples/`; **proxy rejection**: compulsory penultimate noise omitted, not a two-layer counterexample. |
| Final inverse helper CX pair | `inverse_two_CX.qasm`: L=2.96656211430e-5, A=1; **measured failure**. |
| Measured penultimate helper | `measured_helper.qasm`: L=2.27556841923e-5, A=0.9893233123; **measured failure**. |
| Add final fresh/early helper | Fresh RX helper L=7.06801159764e-5; early RX helper L=4.81339157185e-5; each A=0.9893233123. **Measured failure**: reset/idle errors propagate. |
| Best seven-helper scaffold | `seven_tiles.qasm`: L=2.19209639186e-5, A=0.9787606162, both final ticks fully charged; raw correctness/class PASS; **measured failure** (2.84511e-8 above bound). |
| Output-output / crossed output-helper / equal-axis helpers | Independent all-21-pair spectra: floors 3.33328885924e-4 / >=1.33315550814e-4 / >=1.33315550814e-4; **certified exclusion**. |
| Opposite-axis helper pair | Isolated floor exactly zero; exact positive residual after extracting B_X(r)B_Z(r), retained in arbitrary input; **certified exclusion** of escape, not exclusion of this contact. |
| M/reset/first-use penultimate endpoints | Full matrix-basis preparation and reused-measurement checks; factors exist despite idle exemptions; **certified exclusion**. |
| Gauge, overwrite, arbitrary record selection/feed-forward | Latest-write/forbidden conditional probes plus seven organizer frame/POSTSELECT tests PASS. Branchwise instrument factors; **certified exclusion**. |
| Non-code input, coherent logical bias, syndrome coherences | All 16,384 assignments x 64 sectors checked independently without symmetry; full-spectrum bound covers arbitrary density matrices; **certified exclusion**. |
## Proof audit, assumption by assumption
| Assumption / reduction | Enforcement and audit |
|---|---|
| Correct noise convention, independent locations | `noise_blocks` emits separate D1/D2/error channels; q=2p/5, r=4p/15 checked against primary code. |
| Global final step and disjoint gates | `schedule` per-wire free times; H_i exists only for a CX **at global T**. Earlier last CX belongs to idle/local case. |
| Terminal output entangled, not measured/reset | Raw target check; separable-output fidelity <=1/2, far outside 1e-9 tolerance. No exact-target assumption beyond this exclusion is needed. |
| Terminal output-output CX | Retain full D2, optimize arbitrary state; larger floor verified for all 21 pairs. |
| Penultimate DD / D_i-H_j / equal-axis HH | Whole projected channels, not a selected bad fault. Independent all-pair spectra verify exclusions. |
| Opposite-axis HH | Rational residual nonnegative, normalized, exact convolution; all correlated residual noise remains in the conditional state. |
| Own D_i-H_i | D2 covariant under either final CX orientation; trace gives D1(4p/5) twice. Complete operator-basis identities tested. |
| Outside endpoint measured at T | Both X/Z bases and both results: no-flip D1(q0), q0=3/7496; flip branch fully depolarizing; common D1(q) exists branchwise. |
| Helper measured-partner reduction | Project to propagated output axis **before** extracting B(r); direct extraction from unprojected helper D1 is not asserted. |
| Outside endpoint unmeasured | No later interaction can reach a measured record at T; partial-trace invariance removes its error even on entangled inputs. |
| Idle/local/reused-M | D1(p) supplies D1(q), or helper-axis flip 2p/3; post-M D1 is always emitted. |
| Reset/fresh endpoint | Exact preparation-state factorization, not factorization on arbitrary entangled input. Both commuting/anticommuting helper bases tested. |
| Final arbitrary 1q U, including T | D1 covariance; DD D2 covariance; crossed channel is isotropic on output in each helper-axis branch. |
| Conditional acceptance and frames | Common factors preserve each record probability and commute with logical Paulis; no assumption that deleting noise improves postselected fidelity. |
| Spectral reduction | Decoder observable has 64 two-dimensional syndrome blocks. Arbitrary logical orientation and all syndrome sectors optimized. |
| Certificate completeness/rounding | Regenerated exact 264-orbit rational certificate with python -I; independent exhaustive 4^7 check and dense spectra. Exact rational comparison certifies requested rounded-down decimal. |
| CONTRACT audit | Every listed case agrees with primary code and matrix identities. Its w-corollary is only about the all-X factorization's conditional residual state. |
## Verification receipts and limits
`experiments/groundtruth.json`: scheduler/noise probes and public raw checks; `tail_results.json`: ten exact all-orders prices, zero kernel omission.
`experiments/full_assignment_audit.json`: 1,048,576 sector inequalities, unique XXXXXXX / zero-syndrome optimum, max certificate difference 1.89e-15.
`experiments/instrument_audit.json`: complete two-qubit matrix basis; largest identity discrepancy 1.12e-16; binary residual checked with Fractions.
`logs/organizer_record_tests.log`: seven upstream tests PASS, covering record frames, random POSTSELECT, conditional detectors, overwritten bits and accepted-only correctness.
`reviewer18_copy/`: isolated regenerated exact certificate and dense verification (34,560 eigenvalues; max discrepancy <1e-14).
`experiments/requested_bound_certificate.json`: positive exact squared-norm margin for L >=2.18925128e-5. `source_hashes.json` pins audited sources.
Verified: local organizer semantics, raw correctness of saved tails, exact-channel certificate and independent numerical checks. Inferred by proved factorization: universal applicability to admitted circuits.
Unverified: attaining the relaxation with a noisy preparation at A>=0.5; remote/server code identity; future organizer changes; any individual finite-shot board score.
Budgets closed: raw/schedule 20 cases/2 min (<2 s); initial spectra 232 cases/10 min (<1 s); tails 10/10 min (<10 s); certificate/exhaustive/dense/instruments 10 min (<5 s); scaffold 1/5 min.
Decision: one-layer prices are scoped counterexamples only; calling them full counterexamples would omit precisely the compulsory noise being audited. Details/budgets in `EXPERIMENTS.md`.
Fixed encoders, grid layouts and barrier grammar apply only to saved probes and expire after those tests; the proof relaxes geometry, prefix, acceptance amount and arbitrary incoming states.
No tom compute (observed load 60.86/64); at most two local workers. No submissions, commits, pushes, subagents, external writes, or signals to other jobs.
