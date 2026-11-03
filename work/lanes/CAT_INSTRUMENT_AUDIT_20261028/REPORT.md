# Native CAT7 terminal-instrument audit and repair

## Result

The original native CAT7 best had a **source-boundary initialization mismatch** in its compact A instrument. The A module was designed for an earlier source that left q15 in a known |0> state. In the CAT7 source, q15 instead ends in an X-basis measurement and remains in a random |±> state correlated with its record. Raw magic-state correctness and zero harmful accepted single faults did not expose the weaker terminal response.

Adding a physical **R15 at clock32**, then completing the resulting deterministic detector contract, repairs the tested fault response. The new row is `c[22] XOR c[23] XOR c[25] = 0`. The full circuit is raw-valid and c1=0; its exact conditional loss is **9.312204487476157e-5**, acceptance **.5651748131129868**, 190 CX and 41 clocks. At the cut after the last source T-dagger, it rejects all 21 single-qubit X/Y/Z faults and all 63 same-axis weight-two faults. This is a finite fault-response audit, not full channel equivalence. The exact loss remains above the 3.566732196898089e-5 native incumbent.

The corrected circuit is `cat7_r15_complete_45495c4fe525cb7d_d6_20_19_10_2_22_16.qasm` with matching JSON and `.receipt.json`. This audit supersedes any interpretation of the original CAT7 result as a full-strength terminal instrument. It does not invalidate its reported noisy score as a score of that weaker circuit.

## Cause and detector requirement

At the original cut32, q15's last source operation is MX at clock31 with record c21. The exact state oracle gives `<X15>=0` and `<X15 Z_record21>=1`: the physical cell is |±> correlated to the earlier cat measurement, not the fixed |0> input assumed by the old compact A module. The A module did not reset q15 before its first CX involving q15. `q15_audit.py` and `q15_audit.json` contain the literal-prefix evidence.

The root fixed-cut probe on the original circuit accepts an X on data q2 and three harmful XX pairs: (6,10), (20,16) and (19,22). All single Y/Z and other single X cases, and the other tested same-axis pairs, reject. Merely inserting R15 while keeping the original detector rows leaves exactly that same weak response and the same loss .0002657337995; the reset makes a new deterministic record relation available but does not itself add the check. The original 32-row detector contract is short one independent deterministic row after the reset. Re-deriving the full contract yields 33 rows and rejects every tested boundary fault listed above. `repair.py` preserves both controls, including exact-noise and fault-response receipts. Detector completion is a noiseless linear-record completeness statement, not a proof that all possible faulty accepted maps are equivalent.

## Terminal B/C and second source mismatch

This circuit does retain all seven final B→C uncopy interactions: six are at clock38; CX3→4 occurs at clock37 followed by M4 at38, with no intervening operation on those two cells before the B→data layer. It is therefore distinct from the earlier compact B/C pilot that accidentally omitted this layer.

At cut38, after the early q3→q4 uncopy, exact ideal-prefix queries give +1 for the three B zero-code Z stabilizers, logical Z_B, and all seven B/C pair relations (the early-uncomputed C4 is individually +Z). The three correlated B/C X generators have record-dependent signs rather than unconditional +1: generator 0 has sign `(-1)^(c31 XOR c32)`, generator 1 `(-1)^(c29 XOR c32)`, and generator 2 `(-1)^c29`. These are exact affine record relations from literal-prefix Pauli probes, recorded in `bc_records.json` and `bc_audit.json`; they explain why unconditional X expectations vanish and do not show an omitted B→C gate.

A second input difference exists at B q26: the old source supplied |+> before its guard MX, while the CAT7 source supplies |0>, making that MX random. Adding a physical RX26 immediately before the guard and completing the record contract was tested on two corrected circuits. For the best full-flag circuit it leaves exact loss unchanged to numerical precision while reducing acceptance from .5651748131 to .5640455938; the unflagged delay17 circuit likewise retains loss .0001006968667 while acceptance falls from .5928678903 to .5916833402. Thus the tested RX26 intervention is not a score improvement, although the input distinction is real. The separate source-state receipt is `work/lanes/CONTINUE_20261028/module_input_audit.json`.

## Corrected family

Every row below uses a real q15 reset at its source-specific release clock, a fully rederived deterministic record contract, all noisy operations and waits, raw correctness, c1=0, and rejection of all 21 single XYZ and all 63 same-axis weight-two cut faults. These are exact full-noise conditional losses; see `rerank.json` and the emitted QASM/specs.

| Source / B-factory timing | Exact loss | Acceptance |
|---|---:|---:|
| Unflagged, B delay16 | .0001135922094 | .5901344027 |
| Unflagged, B delay17 | .0001006968667 | .5928678903 |
| Unflagged, B delay18 | .0001141783327 | .5901344027 |
| Interleaved three flags per round, B delay21 | **.00009312204487** | .5651748131 |
| Three flags only in second round, B delay20 | .0001001906342 | .5710410108 |
| Noninterleaved three flags per round, B delay23 | .0001003420744 | .5500602743 |

The pair audit of the corrected best gives c2=69.97555556. Largest classified contributions are data-idle × data-idle 13.0556, data-idle × terminal cross-gate 11.5556, B/C idle × encoder gate 4.6, B/C gate × encoder gate 3.1244, and B/C idle × encoder idle 3.1111. They are second-order diagnostic terms, not an additive attribution of finite-p conditional loss. `pairs_repaired.json` is the full ledger. No submission, shared-tool edit or production promotion was made.
