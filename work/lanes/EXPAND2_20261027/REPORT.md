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

## Continued assembly, readout, and scheduling work

The continuing search produced complete native 48- and 47-tick circuits. Their
official raw outputs and exhaustive single-Pauli audits pass. Exact all-orders
prices now distinguish actual timing achievements from performance gains:

| Complete native construction | CX | Ticks | c2 | Exact loss | Exact acceptance |
|---|---:|---:|---:|---:|---:|
| First 48-tick, early B schedule | 376 | 48 | 39.2 | 4.62502747419e-5 | 0.472779781363 |
| B waiting-rejection optimized, strong A | 375 | 48 | 35.03 | 4.06936374726e-5 | 0.506398489982 |
| Same, with both plus-state spare guards | 386 | 48 | 33.17 | 3.80823788643e-5 | 0.503853819645 |
| Earlier source and B, alternate 9-CX A, both spare guards | 378 | 47 | 34.2311111 | 3.89104079039e-5 | 0.510125086243 |
| B phase pulse before final verification, both spare guards | 385 | 48 | 32.6177778 | 3.77389420079e-5 | 0.497201343145 |

The first and last rows fail acceptance. The eligible shorter circuits remain
worse than the incumbent. The real clock saving does not outweigh the source
protection and late fault-pair costs. Exact receipts are in NATIVE2; no circuit
in this table is promoted as SOTA.

### What the full circuit exposed

An ordinary encoded-plus A resource followed by seven Z reads loses an important
check present in v37j. The incumbent applies CX8→7 and CX9→8 after the relevant
data interactions, then reads q9 in X. This measures the encoded X representative
on physical qubits {7,8,9}, while the other reads retain three Z-syndrome checks.
Restoring that check reduced one complete candidate's expected loss from
1.01935788786e-4 to 4.39235744267e-5. Both numbers refer to the then-completed
detector policy and remain above the incumbent.

`logical_readout.py` enumerated 3,372 valid native two-layer decoders, representing
nine distinct measured X subspaces. Twenty-seven physical representatives were
assembled and audited with a fixed 10-CX A preparation. The best second-order
coefficient was 38.0555556, using the original logical-X subspace. Adding a second
X check did not improve that fixed-preparation family. The generator, choices,
and result ledger distinguish this finite search from a global readout bound.

`relaxed_a.py` tested all seven nonempty subsets of the three initially zero A
inputs, preparing a larger X space and removing resulting state-identity gates.
All seven were raw-correct. Three had zero single-fault contribution but
second-order coefficients of 120.599444 or more; the other four had harmful
single faults. Weaker A checks did not improve this family.

`park_data.py` reinstates native identity interactions with independently
heralded plus-state helpers q0 and q1 in otherwise idle data slots. For the
10-CX A preparation, both helpers reduced the second-order coefficient from
38.0555556 to 35.7422222 without extending the 49-tick circuit. The extra gates
are useful because the full conditional noise channel differs from idle noise.
This is a measured scheduling effect, not an assertion that fewer gates always
improve performance.

`original_a_resource.py` isolates the incumbent's 11-CX A preparation and its
two-CX readout from the separate parking operations. With the preserved source
and B factory, its coefficient is 33.5022222; adding q0/q1 parking gives
32.0422222 at 400 CX and 49 ticks. These initial experiments used the historical
record-exclusion policy described below and are labeled as such, rather than as
baseline-equivalent controls.

### Acceptance contract correction

Completing every noiseless affine detector initially added two independent
checks beyond the incumbent's intended contract. Simply excluding the two
associated records did **not** restore the original detector subspace, because
the original circuit uses them in relative checks. That intermediate policy is
a distinct experiment and must not be called baseline-equivalent.

NATIVE2 subsequently derived two permitted physical fault directions separately
from each actual circuit, projected the completed detector rows orthogonally to
those directions, and checked the reconstructed 412-CX circuit against the
original canonical detector row space. The resulting spaces match exactly at
rank 71, with the same physical operation multiset. The control receipt is
`../NATIVE2_20261027/record_contract_modes_control.json`. Retimed modules preserve
original record identifiers so the physical directions are resolved at their
actual new times.

### Source scheduling

`commuting_schedule.py` uses CP-SAT with exact commuting-operation relations,
native resource constraints, and explicit source releases. The preserved
251-CX source remains 41 ticks in the completed search; its retimed ideal-resource
diagnostic is worse, at 2.99206583656e-5. The 129-CX cancellation variant reaches
39 ticks but its diagnostic worsens to 3.38039951164e-5. These are bounded search
outcomes. The later 48-tick full circuit instead uses a small set of targeted
source contractions to unblock the verified B factory, retaining its MZ heralds.

The remaining work is joint optimization of the source releases, A preparation,
measured phase representative, and the final readout schedule. A zero single-fault
coefficient alone is insufficient: accepted correctable resource errors can pair
with a later data error or false check to produce the dominant logical loss.

### Native Clifford phase experiments

`frontend_axis.py` extends the lane-local Clifford frontend with native SX/SXdg.
It preserves the pinned noise scheduler and all-orders contraction. An independent
Stim inverse-tableau oracle checks 11,279 fault pullbacks and 1,440 signed
observables, including randomized H/S/Sdg/SX/SXdg/CX words. All agree; the receipt
is `axis_frontend_verification.json`. Shared qtools and judge files are unchanged.

`axis_echo.py` first put real noisy transversal Clifford pulses on data at40 and
their inverses at47, replacing existing idle channels. All five variants passed
raw and full single-fault checks, but every pair coefficient was worse: H44.83556,
S/Sdg40.86111, SX/SXdg35.35778, versus35.03. These are finite failed controls.

`between_checks.py` creates a distinct instrument with A taps44, B taps46, and
readout47. Clifford pulses at45 and47 then rotate the second checked syndrome
relative to the first. Again all five variants are raw/F1 valid. The no-pulse
coefficient is42.69667; SX/SXdg tie it, S/Sdg increase it to52.23778, and H to
536.89889. No full prices were needed to select these inferior controls.

`b_phase_probe.py` instead applies transversal S to the encoded-zero B resource.
It preserves the ideal resource and can make some incoming bit residues visible
to the final phase readout. With B ready45, a pulse in the post-verification gap
only changes c2 from45.03333 to44.51111. Moving the final B-to-C verification to45
and placing the pulse at44 gives34.47778, compared with35.0 for the exact same
schedule without the pulse. Adding both plus-spare guards gives32.61778. Its
full price is included above and fails acceptance; a low pair coefficient alone
does not make it an eligible improvement. `phase_screen.py` supplies the complete
raw/F1/pair gate for further independently certified resource phase symmetries.

## Provenance and outstanding objective

Baseline QASM SHA-256 is
`ac2d9dfbfb4967baacf85a25f2a1eaac35dd7039abe2069dc858cd5a5f4ca5cd`.
Pinned qtools version is
`94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f`.
The official judge checkout is pinned at
`76fe47c0324f1c1f8b72a7d55af200e88043b522`.

Main advanced during this work through 048e820600c7d30f9f1dee92cf0957b80e2e939a,
adding two independent v37j re-draw submissions and receipts. Its source circuit
and evaluator did not change. Commit 3a0b74f9527e874b9d83e9b5403134ef194ba334
preserves both updates in the private research branch. This lane does not modify
main or shared qtools.

The remaining objective is a complete legal native circuit with materially better
full noisy loss, followed by the official score needed to establish the leaderboard
claim. The verified patch above completes a small working improvement; it does not
complete the user's SOTA objective.
