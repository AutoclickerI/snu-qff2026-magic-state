# Judge behaviour
Serves: G1, G2. Read before reasoning about scores, noise, validity or evaluators. Source code:
`upstream/snu-qff2026-problem/tprep/` (`check.py`, `noise.py`, `faults.py`).

- **Sampling.** `tprep.check` compiles the noisy circuit with xtim's exact engine and samples 1e6-shot
  chunks; chunk k uses seed + k. Each shot returns the expectations ⟨X_L⟩, ⟨Y_L⟩ of the final state given
  that shot's Pauli errors. MC noise comes only from which errors occur. `work/fast_check.py` runs the
  chunks in parallel and sums them in the judge's order, so it is bit-identical.
- **Decoding.** After the circuit, the judge measures the six stabilizers ideally. Any nonzero Z-type
  (X-type) syndrome flips the sign it applies, which corrects every weight-1 error. A same-type weight-2
  error is always miscorrected; an X on one qubit plus a Z on another is corrected. A Z-type logical
  flip costs 1 (both ⟨X_L⟩ and ⟨Y_L⟩), an X-type one costs ½ (⟨Y_L⟩ only).
- **Noise (STANDARD, p = 1e-3).** DEPOLARIZE1 after every 1-qubit gate (including `id`, `t`, `tdg`),
  DEPOLARIZE2 after every `cx`, flips on measurement and reset, DEPOLARIZE1 after measurement on a
  reused qubit, a noisy |0⟩ at first use unless it is a reset, and DEPOLARIZE1 per waiting step.
  `reset; h` and `h; measure` run natively as RX and MX (one step).
- **Idle.** Operations run ASAP in written order; `barrier` holds its qubits. A qubit idles between its
  operations and from its last operation to the end of the circuit, except before a reset and after a
  final measurement. So data qubits idle until the last measurement anywhere.
- **Gates checked.** `format`, `class`, `correctness`, `acceptance` (CONSTRAINTS rules 1–4). The judge
  does not run `fault_scan`; c1 is our diagnostic. c1 ≈ 3.7e-17 is roundoff (FINDINGS).
- **Board.** Key = 1-F at 3 s.f., then fewer 2q gates, then earlier submission; best entry per team.
- **Measure, then reuse without reset.** The judge charges X_ERROR(p) before `measure` (state and record flip together) and DEPOLARIZE1(p) after it, so a measured qubit reused at once is a known |m⟩ with 2p/3 harmful error, one step earlier than `reset` (X_ERROR p). Waiting before the reuse is charged; waiting before a reset is not. The X^m offset must land only where a detector can XOR the record in (never on the output), or correctness fails.
- **Frame and selection.** Affine logical frames (`FRAME_X`/`FRAME_Z` on record parities, both or neither) and `POSTSELECT` are legal; our circuits use none. A frame on a parity that is already a detector changes nothing on accepted shots. A nonlinear accept rule can be computed with legal gates (reviewer 7's 8-CX/7-T AND witness), at full noise cost.
- **No other levers in the code** (read 2026-10-23): noise follows problem.md §1.5 for every operation; the only free operations are `barrier` and the `h` folded into MX/RX; the sign-only correction equals the §2.2 lookup; comments cannot inject Stim text; MPP and every 2q gate but `cx` are rejected.
- **Spec freedoms checked 2026-10-24** (problem.md §1.2–2.2 and `tprep/{qasm,noise,check}.py`):
  - A block qubit can move in 1 CX: CX f→a (f fresh |+⟩), then measure a in Z, leaves X^m on A, which only flips A's
    Z readout. For B or C, CX x→f (f fresh |0⟩), then measure x in X, leaves Z^m, which only flips B's X readout.
    XOR m into those detectors. The data and output cannot move this way: the noiseless correctness check rejects
    any run that needs a correction, and only logical X_L/Z_L frames are allowed. The whole data block can be
    teleported into a |+_L⟩ block (FRAME_X).
  - A may couple to a data qubit before the final T_DAG layer: Z-type stabilizers commute with T^7 and with the
    cat's controlled X^7. B must come after it.
  - Measuring a fresh qubit prepares |0⟩ with 2p/3 error (in use). Measuring it in X prepares |±⟩ with 2p/3 error,
    but the Z^m offset must stay off the data (B and C qubits only).
  - The output's last step cannot be a read or reset. A final CX with a measured partner leaves D1(2p/5) on the output
    (TERM, our class floor); only CXs with unmeasured helpers go lower (BOUND's minimizer), and every tested helper
    ending lost (FINDINGS "Endings outside our terminal class"), which closes those builds, not the family.
  - POSTSELECT on a noiselessly random bit halves acceptance; a biased outcome (logical H_XY on \|+_L⟩: 0.854) is
    affordable but worth ≤ 1% (FINDINGS).
