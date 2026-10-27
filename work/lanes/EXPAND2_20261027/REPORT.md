# Expanded native search and verified working candidate

This is a working checkpoint of the continuing search. **SOTA has not been established.**
The complete native incumbent patch in `release/` passes the official 100-million-shot
check and improves the deterministic expected loss of MAIN/v37j by 0.0128205%.
The larger improvements reported for new endings below are explicitly counterfactuals
with ideal resource preparation; they are not submission candidates.

## Complete, verified circuit

| Quantity | MAIN/v37j | Native incumbent patch |
|---|---:|---:|
| Expected loss, p=0.001 | 3.5870950034704206e-5 | **3.586635120011179e-5** |
| Exact acceptance | 0.5010179047299785 | **0.5003426997728605** |
| CX | 412 | 412 |
| Native ticks | 49 | 49 |
| T/TDG | 15 | 15 |
| Raw output | Correct before ideal decoding | Correct before ideal decoding |

The patch accepts one additional linear sector of the existing identity-detector
syndrome, recovering acceptance without changing the measured expected loss. It then
adds deterministic Z heralds on q13 at tick 34, q31 at tick 41, and q33 at tick 39.
These use existing idle slots. All three reads are included in the detector contract.
The gain is 4.598834592416253e-9, much smaller than one official run's sampling error.

The ordered outputs remain `[6,20,19,10,2,22,16]`. QASM SHA-256:
`30964aaefc6a2180dd130640abb280d61d1e2db889eaf81c1c98533689c3478c`.

Official pinned-judge check, 100,000,000 shots, seed 0, two worker processes:

- Sampled loss: **3.602063381796255e-5**, SEM **7.27e-7**.
- Sampled acceptance: **0.50040763**.
- Format/class/correctness/acceptance: **PASS**; 412 CX; 272.8 seconds.
- Receipt: `release/official_100m.txt`.

This sampled score is not a leaderboard improvement. The candidate has not replaced
the contest racer or been submitted. The small expected improvement alone does not
establish a throughput advantage over production v37j.

### Reproduce

From the repository root, with its `.venv` and the pinned qtools/judge dependencies:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .venv/bin/python work/lanes/EXPAND2_20261027/reproduce_working.py --price

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .venv/bin/python work/fast_check.py \
  work/lanes/EXPAND2_20261027/release/native_incumbent_patch.qasm \
  work/lanes/EXPAND2_20261027/release/native_incumbent_patch.json 100000000 2
```

The reproducer checks the original v37j QASM hash, rebuilds the actual detector row
operations and heralds, checks the resulting QASM hash, and runs the independent raw
state check. `release/reproduction.json` is its completed receipt.
The lane-local analytic-kernel evaluator independently gives loss
3.5866351199224215e-5 and acceptance 0.5003426997728606, agreeing with the pinned
dense-kernel contraction within 9e-16. Receipt: `release/independent_kernel_result.json`.

## Implemented search mechanisms

`acceptance_search.py` groups single faults by deterministic detector sector, computes
exact conditional single/pair risks, and tests linear accepted subspaces using complete
all-orders pricing. It screened 60 single directions, fully priced 20 individual directions
and six combinations. The six-direction combination reaches A=0.5131627317 at
L=3.5985331875e-5; the selected one-direction relaxation preserves the original loss at
A=0.5046945780. These are acceptance tradeoffs, not new logical error correction.

`idle_heralds.py` screened 206 measurement/slot choices. Eighteen passed raw validity and
zero-single-loss checks; all 18 received full prices. `combine_heralds.py` priced 24
combinations of the useful reads. The selected full circuit is the release above.

`short_tail.py` tested removing the final B reads and the last A decoder CX, replacing
the A readout with one-tick-earlier product measurements. All 64 tested product bases
passed raw correctness, but only a subset retained zero harmful single faults. Twelve
full prices rejected the family: the best tested zero-single variant costs approximately
6.91946e-4 at A=0.5393. The lost phase-check information overwhelms the saved idle tick.

`rank6.py`, `phase_support.py`, and `phase_sweep.py` implement 31-T and explicit 23-T
rank-six phase-polynomial networks. The 31-T native witness passed an official 1M run
but had harmful singles and loss approximately 2.49e-4. Thirty-four phase placements
on the 23-T network could not remove its six-component minimum single-fault class;
the best of five full prices was 1.5606572e-4. Neither is competitive.

## Evaluator extension and its limits

`analytic_price.py` derives sparse Walsh kernels by conjugating Pauli moments through
commuting pi/8 rotations and solving their binary X-support equations. It feeds the
unchanged, pinned qtools all-orders noise contraction. It does not change the judge.
All 73 baseline kernels agree with the independent dense construction with normalized
L1 difference at most 1.47e-15; the compact-prefix control agrees within 1.35e-15.

The extension is limited to the asserted commuting-rotation, zero-reference,
zero-frame/no-POSTSELECT family. It removes the old arbitrary 20-T construction limit
only when the resulting analytic kernel is tractable. A memory guard rejects nullity
above 18; 29/31-T cases with millions of selector terms still require a factored kernel
or official sampling. It is not a general exact evaluator for every legal circuit.

## New terminal/resource work

The independent END2 and NATIVE2 lanes provide the exact corrected six-square resource,
native geometry, a preserved source boundary, and complete assembly tools. Root added
native backward beams, constructive parity-tree resource synthesis, first-order-safe
pruning, and release-weighted searches across all 64 local square orientations.

The parity-tree construction returns independently verified native state-preparation
witnesses, including first-order-safe ones. Their depth is currently too large: the best
first-order-safe orientation in the 192-witness screen had 103 CX, 41 standalone layers,
and a conservative source-compatible round at 74. That is not a competitive full circuit.
No resource witness is presented as SOTA merely because its noiseless state is correct.

A four-square alternative has also passed the ideal-resource raw-state checks. The
preserved 251-CX source followed by that ending has counterfactual loss
2.89602322487e-5 and acceptance 0.604349903. Its A resource admits a native 13-CX
measurement-assisted preparation, verified with the resulting record corrections.
The remaining BC resource and the complete noisy assembly are still under construction.
This counterfactual is not an achieved full-circuit score.

The new source contraction tools make the tradeoff explicit:

| Native source | CX | Source ticks | Loss with ideal instantaneous new resource | Acceptance |
|---|---:|---:|---:|---:|
| NATIVE2 preserved source | 251 | 41 | 2.74984614967e-5 | 0.603735894 |
| Cancel 61 commuting CX pairs, original clock | 129 | 41 | 2.94302854623e-5 | 0.570416485 |
| Same cancellation, ASAP/JIT | 129 | 41 | 3.14458237265e-5 | 0.581023842 |
| Additional 24 raw/first-order-safe CX removals | 105 | 41 | 3.18080728877e-5 | 0.604381778 |
| Also remove 20 final spectator reads | 105 | 40 | 5.68900087989e-5 | 0.628153620 |

Every row has correct raw output and zero harmful single contribution within numerical
tolerance. Fewer gates and zero single-fault loss do not guarantee lower full loss.
The 105-CX source releases many factory cells much earlier, but that freedom must be
valued in a complete native assembly. All ideal-resource diagnostics are labeled in
their JSON and intentionally excluded from submission candidates.

## Provenance and outstanding objective

Baseline QASM SHA-256 is
`ac2d9dfbfb4967baacf85a25f2a1eaac35dd7039abe2069dc858cd5a5f4ca5cd`.
Pinned qtools version is
`94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f`.
The official judge checkout is pinned at
`76fe47c0324f1c1f8b72a7d55af200e88043b522`.

Main advanced during this work to 0b702a7954b753e1834b27023bbb7ad813f59fc2, adding only
an independent v37j re-draw submission and receipt. Its source circuit/evaluator did
not change. This lane preserves that work and does not modify main or shared qtools.

The remaining objective is a complete legal native circuit with materially better
full noisy loss, followed by the official score needed to establish the leaderboard
claim. The verified patch above completes a small working improvement; it does not
complete the user's SOTA objective.
