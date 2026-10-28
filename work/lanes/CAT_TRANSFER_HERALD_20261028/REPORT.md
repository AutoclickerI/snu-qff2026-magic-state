# CAT7 source-transfer heralds

The combined physical transfer herald improves the corrected CAT7 parent, but does not approach the native incumbent. It uses six MZ measurements of known-zero transfer wires and replaces the first-cat root reset/preparation with a physical H, all at the existing clock 14. The complete native circuit has exact L=**8.977878556875212e-5**, A=**0.5618977639**, 190 CX and 41 clocks. This is **3.59% below** the corrected CAT7 parent's L=9.312204487476157e-5, but **2.52 times** the incumbent L=3.5667321969e-5. This is not a SOTA result.

## Construction and record checks

The specified parent finishes the two-CX one-way state transfers from A to D at clocks 12–13. Its clock-14 first-cat initialization is **RX(q8)**, not RX(q14), and R on q7, q9, q13, q14, q15 and q21. The intended root substitution was therefore applied to q8. The measured controls replace the six R operations with real MZ operations in the same clock. Their new record IDs are c56–c61, for those six sites in that order. The root control replaces RX(q8) with an actual H(q8); this is a physical one-qubit gate with its actual judge noise, not a free gate or noise exemption. The measured q wires continue into cat preparation on their post-measurement states.

`herald.py` makes three complete physical variants and recomputes all noiseless deterministic affine detector relations from scratch, including existing source, cat, resource, and terminal records. It separately extracts each source boundary through clock 14, recomputes its own deterministic rows, and runs the pinned exact raw oracle there before checking the complete output. Every boundary and complete circuit has the six output Steane stabilizers +1 and zero noiseless target infidelity within numerical tolerance. All three have zero harmful accepted single-fault contributions. Full finite-p prices include actual preparation, measurement, H, CX and idle channels; the same 190 CX and 41 clocks are retained.

| Variant | Exact L | Acceptance | Boundary and full raw | Harmful singles |
|---|---:|---:|---|---:|
| Corrected parent | 9.312204487476157e-5 | 0.5651748131 | Pass | 0 |
| Six MZ heralds | 9.008916580633220e-5 | 0.5618746413 | Pass | 0 |
| Physical H on q8 instead of RX | 9.272204174567453e-5 | 0.5651977534 | Pass | 0 |
| Both changes | **8.977878556875212e-5** | **0.5618977639** | Pass | 0 |

The full result uses 39 deterministic rows in each six-measurement variant; the boundary uses seven. `meas_full.price.json`, `root_full.price.json`, and `both_full.price.json` give the exact finite-p receipts. `*_boundary.qasm` and `*_full.qasm` retain the respective recomputed contracts and explicit measurement operations. No source, judge, evaluator, race, or submission file was modified. The improvements are evidence for this specific source/ancilla joint herald, not a broader optimality or general architecture claim.
