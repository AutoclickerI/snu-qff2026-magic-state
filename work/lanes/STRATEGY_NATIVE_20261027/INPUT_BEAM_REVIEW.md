# Bounded native input-beam experiment

## Outcome

The four requested beam searches completed without finding a witness. They do not improve on the existing native 24-CX, seven-CX-layer input module, and they do not establish that the broader logical-frame boundary is better. Stop this particular heuristic pending a stronger state-search proposal; increasing its budget alone is not presently justified.

The source was inspected without finding a correctness bug requiring modification. Exact algebra and the official raw-state oracle were independently exercised on two constructed controls. No edit to `input_beam.py` was made.

## Search budget and results

Both modes use exactly the same 14-cell native graph and reverse CNOT row operations. The clear mode has one target with all helpers zero. The logical-frame mode has all 128 targets in which helpers are zero or carry only the logical computational bit; X measurement plus one affine logical-Z frame removes the latter copies.

| Mode | Seed | Beam width | Depth bound | Wall-time cap | Actual search seconds | States recorded | Best nonzero rows at final frontier |
|---|---:|---:|---:|---:|---:|---:|---:|
| Clear helpers | 0 | 1,400 | 28 CX | 90 s | 6.6102 | 362,458 | 5 |
| Clear helpers | 1 | 1,800 | 28 CX | 90 s | 7.0422 | 443,701 | 5 |
| Logical-frame helpers | 0 | 1,400 | 28 CX | 90 s | 9.4461 | 413,942 | 6 |
| Logical-frame helpers | 1 | 1,800 | 28 CX | 90 s | 8.4472 | 512,929 | 5 |

All four hit the depth budget before the time cap; each JSON reports `budget_exhausted`. At most two single-threaded search processes ran concurrently. A valid product endpoint needs four independent nonzero rows, including the single magic-input row. Since a known 24-CX clear-helper witness exists, missing it at depth 28 demonstrates an incomplete heuristic search, not an infeasibility result.

Receipts: `beam_clear_0.json`, `beam_clear_1.json`, `beam_logical_frame_0.json`, `beam_logical_frame_1.json`, and the matching process logs. All processes exited successfully. Source SHA-256 during all four searches: `ebf738bb921e2fc913becc164ea6f5a4765130e2c7b15e687790456dbb00b223`.

## Official raw correctness checks

The controls use the unchanged `tprep.qasm.to_stim`, `tprep.exact.verify` and exact run oracle through the existing frame-aware raw checker. Both have ideal acceptance 1, zero raw infidelity and all six Steane stabilizer expectations +1.

| Constructed control | CX | CX layers | Native clocks | Raw result |
|---|---:|---:|---:|---|
| Original encoder plus two transversal transfer layers | 24 | 7 | 9 | Pass |
| Same, with logical-bit copy on helper q7 and X-measurement logical-Z frame | 32 | 11 | 14 | Pass |

The second construction is an existence control for the relaxed boundary. It does not come from the beam and is more expensive than the baseline. Starting with cleared helpers, its eight native CXs compute the XOR of data coordinates 0, 1 and 2 onto q7, uncompute the temporary helpers, then measure q7 in X and apply the corresponding declared logical-Z frame. The eight edges are retained in `beam_control_checks.json`.

The exact emitted circuits and ordered output metadata are in `candidates/input_control_clear_seed0_cx24.{qasm,json}` and `candidates/input_control_logical_frame_seed0_cx32.{qasm,json}`. The receipt is `beam_control_checks.json`.

## Interpretation

The relaxed helper interface is legal in principle, but this experiment supplies no evidence that it reduces native preparation cost. The graph-only greedy score strongly favors fewer nonzero rows and adjacent duplicate rows; it is not a complete state synthesizer and has not even recovered the existing feasible clear-helper control. This is evidence to improve or replace the heuristic, not evidence against CP-SAT or against measurement-aware state synthesis.

No full noisy score or fault-tolerance claim was made. The module has one T input and has not been assembled with all required noisy checks. New files are confined to the current `STRATEGY_NATIVE_20261027` lane; production and upstream source files were not changed.
