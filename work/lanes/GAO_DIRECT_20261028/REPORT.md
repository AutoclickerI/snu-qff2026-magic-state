# Gao source-only live-output control

The source-only Gao constructions are raw-correct but perform poorly under full noise even **before** routing. The original 16-CX correction form has L=0.002952264839382273 and A=0.8208444628; the two sparse quotient forms are worse. This is a concrete negative control against the hypothesis that the previously used square tail alone explains the complete abstract result. The square tail performs material error detection on residual errors from the source in these implementations.

## Scope and construction

`direct.py` starts from the explicit physical source portion of `gao_abstract_parallel` or the `GAO_QUOTIENT_20261028` correction constructions. It **removes every A/B/C preparation and terminal operation**, rather than merely stopping at a late fixed time of a circuit with overlapping resources. It retains the generic physical qRM source encoder, source verifier, all four flagged/grouped checks, 15 T/T-dagger operations, coherent bulk correction, all eight bulk X reads, and all physical reset, gate, read, and idle noise. The full deterministic affine source-record space is recomputed from the new circuit. The seven-CX candidate includes its required logical Z frame in the raw check and every fault calculation.

The seven physical face T/T-dagger gates are commuted to the final source clock: they act on controls of the face→bulk CX gates and on different wires from the bulk measurements. A bounded commutation-DAG scheduler then assigns times, while preserving all noncommuting dependencies and placing these seven phases on the last clock. T gates on the bulk remain before bulk measurement. The resulting output is live, not destructively measured, and no ideal or noisy square tail is present.

All circuits below deliberately relax two-qubit adjacency; they are abstract diagnostics, not native candidates. All pass the exact noiseless output oracle with the six output code stabilizers +1 and corrected logical T infidelity zero. Records and raw oracles are included in individual `.qasm`, `.json` and `.price.json` receipts.

| Source correction | CX / clocks | Exact loss | Acceptance | Accepted harmful single-fault contribution at p=.001 | Harmful singles |
|---|---:|---:|---:|---:|---:|
| Original 16-CX coherent correction | 105 / 17 | 0.0029522648394 | 0.8208444628 | 0.0026 | 23 |
| 7-CX correction + logical Z frame | 96 / 15 | 0.0036405641443 | 0.8370635490 | 0.0034 | 26 |
| 10-CX coherent correction | 99 / 15 | 0.0045133382493 | 0.8328185840 | 0.0043333333 | 25 |

The single-fault contribution is a diagnostic coefficient evaluated at p=.001, not an independent finite-p ranking. Exact full-noise expectations above determine comparison. These schedules differ and are bounded local proposals, not global optimization or a family-wide no-go.

## Concrete fault witness

For the original source-only circuit, the single Z component of the physical `DEPOLARIZE1` channel on q6 after CX(1,6) at clock 4 produces **no source-record flips**, is accepted, and contributes 0.0003333333333 to the first-order expected loss. Z(q4) after CX(1,4) at clock 5 is another accepted no-record-flip example. Full fault lists are in `original.singles.json`, `frame.singles.json`, and `coherent.singles.json`. These witnesses are sufficient to show that the explicitly tested source and detector contract do not provide single-fault protection for live output, even though raw ideal state verification passes.

The earlier complete abstract square-tail benchmark near 4.38e-5 included the real noisy terminal resource and checks. The different schedules and corrections mean the comparison should not be read as an additive cost decomposition or as a proof that every possible terminal helps; it does establish that direct removal of the tail is not sufficient for this physical source.
