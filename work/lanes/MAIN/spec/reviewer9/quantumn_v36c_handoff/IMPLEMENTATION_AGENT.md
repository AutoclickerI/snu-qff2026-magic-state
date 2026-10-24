# Implementation brief

## Objective and evidence standard

Improve the true expected decoded loss of the current incumbent while preserving the official accepted-output contract and absolute noisy acceptance of at least 0.5. Also integrate demonstrated evaluator savings that make the search cheaper. Keep physical improvements and evaluator improvements as separate deliverables.

This handoff is pinned to quantumn `42afa8ff01c3999444336f5bb2fe473c1475d6f4`, with v36c L=4.1151559437773416e-5 and A=0.5027278379249299. Rebase conclusions if the live repository has advanced. Read the live repository's instructions; this review does not override them.

The final delta through `e31cec14e20f5d9fec9da759ef0d61cd4a5358ab` was reviewed separately: it only adds the v36b_r580 reorder and its receipt. See `LATEST_UPDATE.md`; it does not change the analysis inputs or expected-loss baseline.

No new complete winning physical circuit is supplied. One evaluator optimization is implemented; the strongest physical candidate has exact phase identities, limited-noise certificates, and routed fragments. Other tasks have explicit feasibility gates. The ten task IDs and scopes in `TASKS.json` are authoritative for this brief.

## Start two work streams

### M02: integrate the saved detector basis

Use `audit/review10/search/evaluate_basis.py` as the concrete reference. Preserve the pinned evaluator as a comparison. Integrate the saved 32 XORs and semantic/cost checks; do not run the 1,500-proposal search on every candidate.

The safe transformation acts only among zero-reference identity projector rows after the existing canonicalization. Keep all active kernel rows, observables, probabilities, and kernel weights fixed. Check full GF(2) rank. Reuse across candidates is allowed after the semantic checks; exact QASM hash equality is not required. Revert to original coordinates if the proposal is incompatible or planning costs are worse.

Validate all 73 moments within 1e-12 on twenty real neighboring edits, including model building and planning in throughput measurements. The v36c witness reduces width 11 to 9 and peak bucket size by four. Do not promise that every neighboring graph will benefit.

### M01: construct and price one complete rank-four fourteen-T seed

The historical `TREP/enumerate.py` contains fourteen-T supports, but `TREP2/forms.py` only builds T==15 and assumes rank five. Their old negative conclusions do not price this rank-four family.

Use either the historical f14_1 construction or a correctly mapped current-coordinate support. For the historical seed:

- Physical data sites in the fragment are `[0, 20, 7, 4, 3, 15, 8]`.
- Their binary coordinate rows are `[2, 31, 4, 21, 14, 19, 8]`, of rank four.
- The target parity coordinate is 25.
- The support is `[2, 4, 6, 8, 10, 12, 14, 17, 19, 21, 23, 27, 29, 31]`.
- All fourteen signs may be TDG, with zero added virtual Clifford phase on the occupied subspace.
- The routed fragment uses cells `[0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 13, 14, 15, 19, 20]`; non-data input rows are zero.

The current extracted coordinate target is 31. The numbers 25 and 31 label different bases. They are not conflicting target states.

The phase identity is `-sum_{a in H\{0,t}} parity(a.y) == parity(t.y) (mod 8)`, with H a four-dimensional binary subspace containing t. Prove the chosen encoder prepares the right occupied subspace and preserves the required accepted-output instrument. Then jointly synthesize encoder, parity network, helper preparation, outgoing measurements, detector records, and release times. Appending the fragment to unchanged rank-five scaffolding may erase the benefit.

The fifth independent phase coordinate is unnecessary for this phase polynomial. Removing the corresponding |+> preparation, measurement, or q6 cell still requires a proof about the full Clifford exterior and accepted-output contract. Do not blindly delete c54 or any other record. Do not assume a proof on occupied phase states proves a full operator identity on arbitrary physical inputs.

The supplied fragments achieved 18 CX / 15 ticks at minimum CX, or 24 CX / 10 ticks at minimum depth. The matched protected-family router search found 28 CX / 26 ticks at minimum CX and 32 CX / 15 ticks at minimum depth. These are finite search witnesses, not optimality certificates. All fragment CXs are grid-adjacent, input rows are restored, and phase equality was replayed on all 32 assignments.

Fourteen-T phase-axis noise is worse than protected fifteen-T noise: about 7.79335e-7 versus 1.29759e-9 in the explicitly isolated model. The question is whether reduced physical preparation/routing/lifetime cost more than compensates in the complete noisy circuit. That isolated difference is not an additive loss estimate.

First gate: legal native schedule, exact accepted ideal T_L before the judge's final correction, and official class/processability. Second gate: full-noise A,N,L, including every changed reset, wait, measurement, and detector. Promote only a complete circuit that beats the incumbent with A>=0.5. The suggested 0.5% gain is an investment preference, not a rule excluding smaller exact gains.

## Then build exact diagnostic extensions

**M03 — full factor environments.** Retain selected full adjoint gradient tensors before scalar reduction. For a single changed factor, `Z' = Z + <E_i,F'_i-F_i>` is exact only when the kernel, coordinates, and all other factors are unchanged. Hash semantic boundaries; textual QASM locality is not enough. Multi-factor replacements need a joint environment. Check twenty edits and one retiming edit that must invalidate reuse. A proposed investment gate is twofold end-to-end throughput, not merely a cheaper contraction kernel.

**M04 — finite-p mixed counterfactuals.** Use the existing adjoint with five editable channels made perfect in turn. For each unnormalized moment, `Z_-ij = Z-g_i-g_j+H_ij`, with `H_ij = g_j(base)-g_j(i-perfect)`. Compute A and N separately, then form L. Validate twelve pairs with direct full contraction. This is a channel-removal diagnostic; it does not authorize deleting physical gates or summing gains from larger bundles. Continue only if the ranking reveals an actionable synthesis target.

## Gate the six broader tasks

| Task | First result required before scaling |
|---|---|
| M05 | Exact sector A,N and four logical-Pauli costs, then a realizable affine acceptance/frame policy. The three shipped no-frame coarsenings are losing controls. |
| M06 | Match v36c, then a legal >20-T small-rank control using a factorized magic-sign kernel. Keep the official propagated-rank guard and runtime restrictions. |
| M07 | Exhibit a genuinely larger feasible accepted, frame-corrected instrument family, including positivity and trace constraints; do not merely count unconstrained Choi directions. |
| M08 | Compute a clear incoming-boundary syndrome table, screen all 2,825 subspaces, then price a few rank-2 to rank-5 physical extractors. |
| M09 | Reproduce all branches/byproducts of the existing star-to-triangle witness, then price one specific verifier resource including preparation, measurement, local Clifford, and latency. |
| M10 | Correct semantic noise coupling and independent-pilot control variates on known-answer pairs; demonstrate variance per CPU improvement before using unknown candidates. |

For M07 preserve the complete exterior-relevant accepted and frame-corrected map, including earlier classical records and correlations. Do not impose equality of every raw B/C branch if measurement, acceptance, and correction are being jointly redesigned; that would eliminate the intended freedom. Conversely, tracing out C alone proves no new freedom. An arbitrary-input replacement requires the relevant composite Choi contract; a fixed preparation can use the corresponding classical-quantum input contract.

For M09 retaining all correctable branches is a useful preference, not an official requirement. Legal postselection is allowed if the full absolute acceptance and loss remain acceptable. Physical X byproducts propagated through T may demand an unsupported conditional Clifford; endpoint graph equivalence is insufficient.

For M10 set tau to the accurately known baseline loss. With candidate `Y=I_acc,c*(loss_c-tau)` and baseline `X=I_acc,b*(loss_b-tau)`, a fixed independently trained beta gives an unbiased estimate of `N_c-tau*A_c` from `Y-beta*X`. It is not an unbiased ratio estimate of L. Preserve each circuit's measurement and fault marginals, include baseline numerical uncertainty, and check acceptance separately. A pilot coefficient can increase variance.

## Do not repeat stale work as a new result

P75 already covers N-L0*A and interacting real-edit combinations. The ordinary adjoint exists. P77, P73, and P78 cover terminal redesign, B preparation flags, and sampled-score racing respectively. Coordinate these new tasks with those lanes.

Common GL(3,2) Schmidt basis changes give the same B/C resource state. Fano labeling, plain no-A/no-B architectures, and simplistic last-idle Pauli replacement have existing negative evidence. The current factorization census found no nontrivial independent acceptance-only component. Moment-sharing analysis predicts only about 6.17% bucket-work savings, not a large universal multiplier.

The current implementation's T<=20, rank-five phase generator, zero-frame fast path, A0 approximately one, fixed blocks, and full terminal extraction are not all official requirements. The actual judge still imposes grid locality, its gate set, no conditional quantum gates, exact accepted ideal output, A>=0.5, processability including MAX_RANK=22, size limits, and server time limits. See the report for the full matrix.

Do not set a true-expected-loss target below 1e-5 under the unchanged STANDARD model without first locating a concrete error in the retained-output bound. The rerun certificate gives L>=1.162e-5. A selected finite-shot score can be below an expectation bound.

## Required result record

For each proposed physical promotion save source and judge pins, QASM SHA256, data-qubit ordering, native counts/depth, ideal/class checks, absolute A, unnormalized N, L, approximation bounds, and runtime. Compare against the same current baseline. For evaluator work compare all moments and total workload throughput. Keep failed candidates with their reason; the package provides examples.

No remote launch, competition submission, or repository push was performed for this review. Those operational actions are outside the local handoff.
