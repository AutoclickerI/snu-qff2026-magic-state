Status: RUNNING — P75 integration on v36a; all-orders acceptance floor0.5002. Prior delivery: [REPORT_v36a_delivery.md](REPORT_v36a_delivery.md).

# v36a all-orders noise ledger

Removal gains overlap and are not additive. The circuit, detector predicate and all outcomes are unchanged; only the selected noise is disabled.

Baseline: 1−F=4.146051958326e-05, acceptance=0.500832514460.

| Removed region | Loss after removal | Loss saved | Acceptance after removal |
|---|---:|---:|---:|
| round | 8.052245284182e-06 | 3.340827429907e-05 | 0.509207041 |
| BC_resource | 3.567110212804e-05 | 5.789417455219e-06 | 0.552603379 |
| waiting_data | 3.666187430232e-05 | 4.798645280935e-06 | 0.558643852 |
| prefix_ops | 3.908822594880e-05 | 2.372293634458e-06 | 0.593472448 |
| prefix_idles | 3.949183770823e-05 | 1.968681875025e-06 | 0.617333810 |
| A_preparation | 3.951163294455e-05 | 1.948886638704e-06 | 0.516020367 |
| readout | 3.990086170078e-05 | 1.559657882480e-06 | 0.517479886 |
| data_hops | 4.104733009013e-05 | 4.131894931308e-07 | 0.512200492 |
| A_decoder | 4.135284143816e-05 | 1.076781450929e-07 | 0.502201462 |

Definitions: `ledger/regions.json`. Full73-moment receipts are saved per removal. The top physical-pair classes are generated independently.

Top exact second-order physical-pair classes (no mixed idle gaps):

| Pair class | Contribution |
|---|---:|
| round x round | 3.054444444444e-05 |
| BC_resource x BC_resource | 2.902074074074e-06 |
| BC_resource x round | 5.955259259259e-07 |
| BC_resource x readout | 3.554962962963e-07 |
| prefix_ops x waiting_data | 2.679576268664e-07 |
| waiting_data x waiting_data | 1.549347142072e-07 |
| prefix_ops x prefix_ops | 1.033333333333e-07 |
| prefix_ops x round | 2.666666666667e-08 |
| round x waiting_data | 1.777777777778e-08 |

Within the round region (overlapping removal gains):

| Removed noise | Loss after removal | Gain |
|---|---:|---:|
| BC_check | 3.724704161051e-05 | 4.213477972748e-06 |
| BD_coupling | 2.767078586289e-05 | 1.378973372036e-05 |
| DA_coupling | 3.819132324059e-05 | 3.269196342664e-06 |
| final_data_idle | 1.384904650971e-05 | 2.761147307355e-05 |

## Verified finalists below v36a

| Stem | All orders | Acceptance | Judge | MC3 mean |
|---|---:|---:|---|---:|
| [v36/st2_both](v36/st2_both.qasm) | 4.127590181784e-05 | 0.500617287 | PASS, 2.4s, FAST | 4.1859340e-05 |

## Current integration findings

The all-orders ledger changes physical noise probabilities only. No gate, ideal operation, detector or accepted outcome is removed. The baseline exactly reproduces MAIN/v36a. Physical-pair classes use unchanged exact2's second-order contraction and sum to3.50015441929244e-5. No compressed idle gap crosses a region boundary in this baseline. Counterfactual removal gains overlap and are not additive.

Six isolated checked preparation resets can be delayed to immediately before their measurements. All-orders loss is unchanged within1e-16; acceptance rises0.500832514→0.504510812. The independent-segment pass-factor formula predicts the ratio1.007344366006368, exactly matching the evaluator. All73 normalized acceptance/decoder moments agree within6.7e-16; see prep_factorization.json.

On v36a, removing the initial checks42/43/45/46 and replacing initial39/40/41 measurements by resets, jointly with the six preparation delays, gives acceptance0.516922510 at loss4.14596131494e-5. These were re-evaluated jointly; their gains were not assumed to add. A moved record may have changed physical meaning: ST2's new c45 is an echo readout, so the new delivered circuit retains it when recovering acceptance.

The v35b two-echo mechanism ports successfully to v36a:4.12759018178e-5, acceptance0.500617287, judge PASS2.4s/1e6 and FAST. MC3 mean4.185934e-5. The C-copy exchange releases0.002410720 acceptance but costs1.0308924e-7 loss on this base; appending the same edge with an extra terminal tick loses badly,9.04916e-5. It remains a budget option, not a standalone fidelity win.

WAITPROT's machine-readable menu is frozen and refreshed by gadget name. Every new record is reallocated, slots are tested against v36a, and joint circuits are repriced. Some old windows now hit the new A encoder or prefix gates: q16→q10 at37/39 conflicts with q16's transfer/preparation, and the old q7 Z guard spanning27–31 crosses the now-earlier blue-check interaction. These exact placements are rejected; shorter valid windows are independently built and priced.

BCFB's delivered encoder paths are rebuilt on v36a's release constraints with explicit initial resets, with/without q16 verification where applicable. The current valid ports lose to the incumbent; this does not refute other timings, measured-state reuse, different flags, or delayed-round versions. FRESH's SX sign variants remain SLOW in its delivered report. Its newly delivered static general-atoms dispatch predictor is copied into this lane; it is an additional screen, and finalists still receive the measured XTIM gate.

The acceptance knapsack is a beam search using full-circuit cubic screens for proposal selection, followed by unchanged all-orders ranking of emitted candidates. It preserves multiple loss/acceptance tradeoffs and checks every full conjunction; it is not an exhaustive optimum over all possible gadgets. New ST2 and COMP29 deliveries are inspected and re-derived as they arrive.

All work stays in SEPBC. No credentials, submissions, commits, pushes or subagents. Host limits are enforced before launches; one broad pricing batch was moved from zebra to tom when zebra's total load exceeded64 cores. Completion is tracked by process exit, not output-file appearance.
