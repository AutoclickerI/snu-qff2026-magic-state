# Direct live output from the incumbent source

The complete, unchanged native source prefix is a valid seven-qubit Steane magic-state preparation in the noiseless model, but its live noisy output is much worse than the incumbent with its final verification instrument. The source-only circuit has **251 CX, 41 clocks, exact conditional loss 0.0007367620164877308 and acceptance 0.6593364932174665**. All six raw Steane stabilizers are +1 and the noiseless infidelity is zero.

This control retains every operation, deterministic detector and noise channel in `work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16`. It adds no resource preparation, extra wait, terminal verification or hypothetical perfect operation. The exact finite-p evaluation includes reset, gate, measurement and idle noise under the shared evaluator. Its reported kernel-omission bound is 3.36e-14. This is a full noisy native control, not a perfect-source estimate.

The result rejects simply deleting the current ending from this source; it does not establish that all direct-output sources must fail. The separate [seven-cat](../DIRECT_CAT_20261028/REPORT.md) and [Gao](../GAO_DIRECT_20261028/REPORT.md) controls test other source families under their stated abstract-connectivity scopes.

Run `.venv/bin/python work/lanes/DIRECT_NATIVE_20261028/evaluate.py` from the repository root. The complete result is [result.json](result.json); the QASM SHA-256 is `d828869d5031c0297adfe18c1d8c5bcdc92395a815ce4affe2f06ecb60ac9769`. No contest submission or production race was started.
