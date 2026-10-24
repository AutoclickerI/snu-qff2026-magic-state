# Implementation agent instructions

Your first objective is a verified expected-loss improvement over the independently reproduced v36a control, subject to official validity, acceptance, and runtime.

## Evidence hierarchy

Use all-orders expected L and A for physical ranking. Keep the exact numerical model's cutoff and floating-point limitations visible. Use official correctness and short sampling for validation. Preserve separate columns for official seed-0 score, multiseed estimates, and true expectation. Do not infer an expectation gain from a selected seed-0 draw.

A new incumbent invalidates old edit prices. Record source commit, exact QASM hash, ordered output qubits, evaluator/judge versions, A, N=A*L, L, CX/depth, errors and runtime. A parser or evaluator failure is not a bad physical candidate.

## Priority

1. Identify the actual running search entry point. Only fix the public legacy defects if they affect the live engine.
2. Integrate the completed 538-channel adjoint ledger into the current integration lane. Top individual effects are seven final data idles, then seven B-to-data CX channels. Those are hypothetical noise interventions, not executable deletions.
3. Evaluate a small complete edit menu on the current control using R_lambda=N-lambda*A, lambda=L_control. Measure pair interactions rather than assuming additive loss/acceptance prices.
4. Preserve annotation equivalence while testing runtime. Do not infer speedup from the single recorded times.
5. Gate speculative hardware synthesis with branch-aware optimistic analyses.

## Critical invariants

- Official p=0.001 acceptance floor is 0.5. Current internal verification margin is 0.5002.
- Circuit must be exact on accepted noiseless branches before the judge's final correction.
- The judge's final syndrome correction does not postselect.
- All added native gates, first-use preparations, measurements, resets, and live-qubit idle time are noisy.
- Only the specifically folded H-measure-H / reset-H native constructs have free folding; generic H is not free.
- Affine FRAME_X/Z declarations are legal; conditional quantum operations are not.
- The universal expected-loss certificate is >=1.162e-5 under the inspected judge. The 7.44545e-6 last-tick relaxation is not an achievable whole-circuit witness.
- A per-channel noiseless counterfactual is diagnostic, and marginal gains must not be added.

## Do not repeat closed or already active work as a discovery

Flag-conditioned A encoding, physical acceptance budgeting, known check removal, waiting protection, SX runtime work, terminal 1-3 CX B flag searches, C-copy trades, and joint-record policy work are already represented in the repository. The ten tasks in TASKS.json state the actual additional change or coverage check.

## Search fixes to inspect

- First 48 moves per family: later moves have zero proposal probability.
- Generator exception after valid yields: clears all preceding moves.
- Diversity candidates appended after filling survivor capacity: truncation removes them.
- Fixed creg c[256]: current v36a uses c[278], so the valid input becomes invalid.
- Fixed output/round-role assumptions silently exclude legal architectures.
- Legacy c1 rejection and second-order acceptance proxy must not be mistaken for current contest requirements.

## New physical proposals remain hypotheses

The earlier B-support census is a backward channel-adjoint support calculation. It crosses resets and measurements. A short support is not evidence of an independent useful flag. Carry classical record dressing and test independence before synthesis.

Weighted fault-pair synthesis is an objective/contract refinement of existing CEGAR, not a new solver brand. Price the full noisy exterior.

Backward terminal-instrument synthesis must retain prior-record correlations and charge every added physical operation. Its relaxed bound only supports pruning when the relaxed feasible set contains every real boundary state.
