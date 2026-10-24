# Search and evaluator review at 42afa8f

Review pin: `42afa8ff01c3999444336f5bb2fe473c1475d6f4`, repository `AutoclickerI/quantumn`.
This is an internal audit note for the root reviewer. No repository changes or remote jobs were performed.

## What is already adopted

Do not present the following as fresh missed methods:

- `docs/PLAN.md:26`: P75 already uses `N - L0*A`, measured physical-edit pair interactions, and all-orders repricing of combinations.
- `docs/PLAN.md:29`: P77 already owns backward terminal-instrument synthesis and a FRAME/POSTSELECT frontend extension where needed.
- `docs/PLAN.md:32`: P73 already owns the earlier B flag, with an ideal meter screen, and second A flags.
- `docs/reference/circuit.md:26-28` and `work/lanes/MAIN/sparse/adjoint_ablation.py`: the first all-channel adjoint is integrated. The current tree contains `v36b_adjoint_72.json`.
- `docs/FINDINGS.md:63` explicitly says live `pop35_*` preserves register size and fills survivors first. The old `population.py` bugs still exist, but should not be promoted as evidence that the active search is broken.
- `docs/PLAN.md:36`: chunk racing for official Monte Carlo re-draws is already active P78.

The public source still has a coverage gap. The recursive Git tree at this pin returned 8,801 entries and `truncated:false`. `work/lanes/ST2` has the 24 old entries, with no `pop35_*`, `knapsack_select.py`, or `ledger.py`. Direct directory fetches of `FRESH`, `SEPBC`, `IDEAS`, `DRAW`, `TERM`, and `BCPOL` returned NOT_FOUND. The documentation can establish current plans/results, but unavailable implementation cannot be audited as if it were the legacy file.

## New measured result: optimize the detector coordinates used by the tensor evaluator

The current sparse evaluator canonicalizes reduced projectors, then chooses a min-fill elimination order in that one coordinate system (`sparse_walsh.py:39-71, 214-216`). It never searches the remaining invertible detector basis. This is separate from reducing the number of record occurrences in submitted DETECTOR annotations.

On v36c there are 72 detector rows. Four have nontrivial reduced ideal projectors (indices 7, 17, 18, 19); the other 68 reduce to identity. Change only the identity-projector rows by elementary invertible row XORs. For their noise syndrome d, acceptance is the condition d=0. For any invertible U, `Ud=0 iff d=0`. The corresponding Fourier variables are related by the bijection `y -> U^(-T)y`; the normalized sum, all observables, and the ideal kernel are unchanged. Only the scopes and contraction work change. Every original independent noise channel and its probability stays intact.

### Actual experiment

`basis_width_probe.py` used seed 80353 and 1,500 greedy random elementary XOR proposals. It accepted 32 row operations in 19.624 s. `basis_width_probe.json` records every operation and both elimination orders.

| Quantity | Original | After detector-coordinate search |
|---|---:|---:|
| Independent noise channels | 552 | 552 |
| Kernel bits | 19 | 19 |
| Conditioned elimination width | 11 | 9 |
| Min-fill work-entry proxy | 5,636 | 1,911 |
| Largest actual bucket, entries | 4,698,112 | 1,174,528 |
| Basis rank | 72 | 72 |
| Noisy acceptance | 0.5027278379249299 | 0.5027278379249299 |
| Expected loss | 4.1151559437773416e-5 | 4.1151559437773416e-5 |

`basis_validate.py` evaluated all 73 moments in both coordinate systems, using the same current evaluator implementation and four worker processes. Maximum absolute moment difference was **1.6653345369377348e-16**. No new sparse cutoff is introduced: the same kernel states/weights are used. This establishes a genuine compute improvement for this circuit, not a physical-loss improvement.

Timing was measured in ABBA order. Background load varied, so the pooled wall-clock ratio is not a controlled universal speedup:

| Run | Wall seconds | Sum of child CPU seconds |
|---|---:|---:|
| Original A1 | 21.7588 | 85.8592 |
| Optimized B1 | 8.5520 | 33.7483 |
| Optimized B2 | 9.4209 | 36.5070 |
| Original A2 | 43.9536 | 117.0714 |

The first pair is about 2.54x faster in both wall and child CPU time. The rigorous structural result is a 4x smaller largest bucket and 66.1% less min-fill work proxy. Report timings as observed ranges with the contention caveat, not a guaranteed 3.66x wall speedup.

### Integration recommendation and gate

Cache the basis search by a canonical compiled-model signature. Reuse and cheaply repair the incumbent's basis for nearby candidates; do not pay the 19.6-s search cost on every 8-s evaluation. Include original basis as a candidate. Evaluate the actual selector-weighted bucket work, because the current unweighted min-fill proxy is not exact elapsed time. Use the old basis whenever a new basis fails the cost or timing gate. First benchmark 20 nearby v36c edits, require all 73 moments to match within 1e-12, and measure end-to-end throughput including planning. Stop expanding this optimization if cache amortization does not improve that workload.

## Further fresh candidate 1: exact finite-p pair interventions via the existing adjoint

Let Z be an unnormalized moment, A, or N=A*L. Existing independent-channel scales lambda make Z multiaffine. With `g_i = partial_i Z` and `H_ij = partial_i partial_j Z`, the exact two-channel-perfect intervention is:

`Z_minus_ij = Z - g_i - g_j + H_ij`.

No physical-p expansion is involved. The existing first adjoint can obtain the needed mixed derivative without implementing a new Hessian engine:

`H_ij = g_j(base) - g_j(channel_i_perfect)`.

Make channel i's factor identically one, run the existing adjoint again, and subtract the other channels' gradients. A handful of selected i gives their interactions with all 552 channels in a handful of reverse passes. This is distinct from P75's interactions between actual circuit edits: it identifies which joint noise mechanisms remain after all orders and conditioning, before proposing edits. It is also distinct from summing single-channel removal gains, which is invalid.

First gate: select five channels corresponding to editable waits, A-flag-blind errors, and B-resource faults; compute pair interventions and check 12 diverse pairs by direct contraction. Rank pairs by exact conditional loss `N_minus_ij/A_minus_ij`, not by a raw Hessian alone. Use the pair map to formulate actual two-region edit proposals. Stop if the useful pairs are all irreducible terminal noise or do not alter the proposed physical search. No physical improvement is yet demonstrated.

Implementation hook: `adjoint_ablation.py:31-84, 106-151`. With the new detector basis, the same graph simplification can accelerate these passes.

## Further fresh candidate 2: retain full factor environments for exact local replacement pricing

The reverse pass already computes arrays `grads[i]` and immediately collapses them to one scalar at `adjoint_ablation.py:82-83`. Keep these environments for selected local factors. If the ideal kernel, observable convention, and all other independent factors are unchanged, multilinearity gives:

`Z_new = Z_old + <environment_i, factor_i_new - factor_i_old>`.

This prices an arbitrary replacement of that factor exactly, not just scaling its total error probability. For a small physical edit changing several factors, contract the unchanged exterior once to a boundary tensor and price the changed region against it. This generalizes the existing B/C-only boundary cache (PLAN P62) to waiting-data checks, local timing choices and init/readout alternatives.

A real gate rewrite can alter many pulled-back fault signatures or the ideal kernel. It must not use the one-factor identity merely because the QASM diff is small. Compare complete compiled kernels and signatures; invalidate the exterior when its coordinates or factors change. First gate: test 20 actual near-incumbent mutations and identify the unchanged exterior mechanically, then compare all 73 moments with full recomputation. Require at least 2x throughput including hashing/model build; stop if most changes have wide boundaries. No speed measurement or circuit-loss gain for this cache has been made yet.

## Further candidate 3: finish the legal frontend by reusing the full judge-backed model

The sparse prototype rejects partial barriers, FRAME/POSTSELECT, nonzero detector references, non-diagonal kernels and >20 rotation-sign bits (`sparse_walsh.py:73-105`). Its native walk supports only R/RX/M/MX/CX/H/T/T_DAG/I and raises on other gates (`frontend.py:225-247`), narrower than the official gate set.

P77 already plans an affine extension, so do not call that plan new. A concrete implementation shortcut is public `work/lanes/EVAL/model.py:82-102`: it already uses the official converter, declaration parser, conditional detector treatment, exact correctness verification, and frame detection. Its Clifford walk consumes the official CLIFFORD set; lines179-217 already construct postselection projectors and frame-dressed output observables. Reuse this model with all-orders noise rather than implement another partial parser. Preserve absolute A, not the engine's normalized A/A0, and retain the sparse kernel's explicit domain checks until each is extended.

First cases should be current legal SX, signed-frame and POSTSELECT variants for which official exact correctness is known. This remains an enabling task, not proof that any extra legal gate or reference lowers physical loss.

## A rejected overclaim: 73-way moment fusion is not automatically a large speedup

`kernel_reuse_probe.py` found only 1,726 distinct channel sign patterns across 40,296 channel-by-moment instances; there is genuine leaf reuse. Kernel support consists of 17 distinct sets: nine singleton groups plus eight groups of eight Y moments. However, a structural shared-DAG probe with the actual elimination order reduced total bucket-entry work only from 912,396,856 to 856,098,344 (6.17% less work; a 1.0658 ratio). Thus “share the 73 contractions” should not be advertised as a 73x or even 2x speedup. Optimize detector coordinates first. Leaf/kernels caching may be an incremental improvement after that, subject to a real memory/throughput benchmark.

## Reproduction and provenance

- `source_provenance.json` records 14 Git blob identities; all 14 local source copies match.
- Official-style frontend dependencies under `source/work/lanes/MAIN/sparse/judge_subset/` were copied from the prior independently pinned v36a handoff; no dependency behavior was changed.
- The benchmark input was initially materialized with one extra terminal newline. `benchmark_input/v36c.qasm` preserves exactly the evaluated bytes (SHA256 `41aa437394f055b549380eccaa445a26fe077b3bc6759092119178a9c7e33de0`). The exact pinned source is separately preserved with SHA256 `49ea05888f6f56f87eee49665f8275e3f0c30e199c67db7958f5318cc07bd3f8`; the sole difference is that terminal newline. `basis_validate.py` uses the preserved benchmark input for reproducibility.
- Executed Python: `/workspace/scratch/a4b592a94a64/audit/review6_validation/venv/bin/python` (NumPy2.3.5 in the existing validated environment).
- No source branch, submission, external message, or remote compute state was mutated.
