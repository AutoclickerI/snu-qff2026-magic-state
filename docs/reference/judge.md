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
