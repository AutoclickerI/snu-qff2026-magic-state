# Exact uniform-Pauli factors and channel coalescing

Analysis pin: `0ff9423a8e69c13998ab1baf7bf09c8e97558a60`.

## What the current evaluator repeats

`MAIN/sparse/sparse_walsh.py:factors_for` builds a channel's characteristic tensor by summing its individual nonidentity Pauli alternatives. A two-qubit depolarizing channel therefore needs fifteen full outer products per observable moment, even though the characteristic function has only two possible values. The calculation repeats for all 73 moments. This optimization changes the factor algebra; it is separate from the already adopted detector-basis search.

## Identity

Let a uniform channel choose a nonzero vector of F_2^d with total probability p, and identity with probability 1-p. Let S be the image of its full propagated signature map (kernel, residual detector, and observable bits). For a character y,

`chi(y) = 1` if `y` is orthogonal to every basis vector of S; otherwise `chi(y) = 1 - 2^d*p/(2^d-1)`.

This follows because a nontrivial character sums to zero over a finite binary vector space. The image may have lower rank than d: every image vector has the same number of preimages, and the formula is unchanged. A completely zero image has factor one and can be omitted from computation.

Two independent channels with the same full signature image have the same orthogonality predicate. Their product is represented by one predicate and the product of the two nontrivial eigenvalues. This merging is valid for every moment because the image key includes all observable signature bits, not only the current moment's projected sign.

## Guarded implementation

`channel_algebra.py` verifies that a candidate has 2^d-1 alternatives with exactly equal represented probabilities, and that the multiset of images including identity is uniform over a GF(2) subspace. Even a one-ULP probability difference uses the original implementation. A reduced binary basis supplies a canonical full-signature key for merging. No QASM instruction, noise probability, detector condition, or judge code is changed.

The final hardened implementation retains both characteristic levels explicitly: `trivial=p0+n*p_term`, `nontrivial=p0-p_term`. It never replaces an almost-normalized trivial level by one. A zero-signature channel becomes a retained scalar factor, and merging multiplies both levels. Thus no probability-equality or normalization approximation is introduced. Ordinary floating-point arithmetic and reordering remain subject to roundoff.

The equivalent algebra changes floating-point summation order. It preserves exact real-valued moments; it does not promise identical last bits. The sparse kernel's existing omission bound remains separate from roundoff.

## Measured v36g witness

The current v36g has 692 channel factors and 5,580 nonidentity Pauli summands. The analytical form drops 81 full-signature identity factors and merges another 173, leaving 438 character factors and 1,011 basis predicates. All factors in this circuit satisfy the guards; none needed fallback.

`benchmark_character.json` compares every one of the 73 original moments with the merged version. Maximum absolute difference is 7.66053886991358e-15. Original L is 3.836054467100275e-5; merged L is 3.836054467089148e-5. Acceptance differs by 7.66e-15. This is numerical agreement, not a new physical loss improvement.

Sequential accumulated component timings on the review host were:

| Stage | Original | Analytical and merged |
|---|---:|---:|
| Factor construction | 13.278 s | 1.702 s |
| Variable elimination | 13.266 s | 10.037 s |
| Common sparse-kernel construction | 2.656 s | 2.656 s |

Without merging, analytical factor construction took 2.460 s. These are interleaved component timings, not independent end-to-end runs. Common planning took 12.515 s during another audit workload. Do not promise a universal total speedup from this table. The structural counts and full moment comparison are the stronger evidence.

## Use

Keep `channel_algebra.py` and `character_eval.py` together. From the handoff or repository parent:

```bash
python character_eval.py \
  --evaluator-dir /path/to/quantumn/work/lanes/MAIN/sparse \
  --stem /path/to/quantumn/work/lanes/MAIN/v36g \
  --output /tmp/v36g_character.json --processes 4
```

The wrapper uses the current evaluator's prepare/compile_best/sparse_kernel/contract_selector functions and does not modify its files. `--processes 1` avoids POSIX fork. An optional `--profile-factor-construction` records a small ABBA factor microbenchmark. The required environment is the same as the original sparse evaluator.

`--basis-trials 0` evaluates the saved bases without additional hill climbing. It is verified on v36g and documents a separate planning-cost issue in `PLANNING_AND_RACE.md`. Leaving the option out preserves current upstream planning. The portable zero-trial run completed in 6.118 seconds with all 73 moments agreeing within 7.66e-15.

The acceptance-factor ABBA microbenchmark recorded CPU times of 0.27314/0.27277 seconds for four original builds and 0.03128/0.03677 seconds for four analytical builds. This supports the factor-construction gain independently of the broader scheduling/load caveat; it is not a claim about the official Monte Carlo sampler.

## Next implementation gate

Integrate the algebra at the compiler/factor boundary, retain the guard and original-factor fallback, and compare all moments on current v36f/v36g and representative actual edits. Include planning and construction in workload throughput. Keep physical source-channel metadata outside the merged representation for adjoint attribution; a merged factor is not permission to merge or remove physical gates.

The optimized factors can also make a planned finite boundary table cheaper. That is an independent extension; no boundary-cache speedup is claimed here.

## Final guard and provenance validation

`portable_hardened.json` and `portable_hardened_validation.json` rerun the final implementation on v36g. All 73 moments still agree within 7.66054e-15, with unchanged structural counts and loss difference 5.90e-19. `guard_validation.json` checks five independent synthetic cases, including a one-ULP unequal probability (which must fall back), an unnormalized factor, a nonunit zero-signature factor, and merged nonunit factors. Maximum difference from explicit summation is 1.11e-16.

The new receipt records the input JSON hash and ordered data-qubit list; hashes of `sparse_walsh.py`, `frontend.py`, `fastfill.py`, `basis_warm.json` and all `judge_subset` Python files; hashes of both extension files; Python/NumPy versions; and the planning budget. For reuse, combine the separately recorded QASM SHA256 with `semantic_context_sha256`; the latter describes the context rather than replacing the QASM identity.

Original timing receipts retain their observed values and now identify the archived `version1/` implementation hashes. The final guard change was revalidated for semantics, not used to claim an additional speedup.
