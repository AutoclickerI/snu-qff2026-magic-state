# MBP

**Status: No eligible physical improvement found. Grid-free pricing is complete for the listed recipes; the broad grid-embedding question remains unresolved.**

Ranking is by infidelity only. The hard acceptance gate is 0.5; 0.505 is the practical floor. No submission, commit or push was performed. All lane writes are under this directory.

Noise and score semantics come from the organizers' [noise implementation](../../../upstream/snu-qff2026-problem/tprep/noise.py) and [judge](../../../upstream/snu-qff2026-problem/tprep/check.py). Numerical expansion uses the repository's [exact evaluator](../EVAL/exact2.py).

The supplied physical bar is `../MAIN/v22h_c2c9`: 203 CX, R45, c1=2.9236e-19, second=5.43199e-5, third=1.69860e-5, total=7.13060e-5, exp(-A1)=0.53384. These are from the existing [exact receipt](../MAIN/v22h_c2c9.exact.txt); the supplied seed-0 re-draw mean is approximately 7.23e-5 and is not a new MBP measurement.

**Matched R45 result:** [redundant 1+3-cat MB-B+C](matched_cat13_BC.qasm) has exact total **5.1130377e-5** and three-seed MC mean **5.1351965e-5**, versus the [unitary reference](matched_ref.qasm) at exact **5.1207368e-5**, MC **5.2076372e-5**. The observed mean is 1.39% lower, about one combined standard error; this is noise-competitive, not a resolved true gain. Both are explicitly grid-free diagnostics. The promising two-member-cat graph fails stationary embedding; the embeddable reused three-helper variant misses the practical acceptance floor.

The requested contexts contain **2,116 recipe/order evaluations**: 1,058 at sep33 and 1,058 using the exact v22h pre-stage at R45. The table also preserves pilot and diagnostic runs. All completed prices pass noiseless correctness; acceptance failures are retained and excluded from eligibility.

## Scope and verification

- Grid-free prices relax adjacency and use dedicated virtual preparation helpers. They preserve the judge noise, all exact noiseless correctness conditions, and the 1e6-shot seed-0 check. Their format PASS is **under these explicit relaxations**, so it is not a physical eligibility claim.
- `sep` uses the exact sep33 prefix and R33. **`v22h` is the matched R45 sweep:** all 129 pre-stage operations at v22h_c2c9's native times, with all 18 pre-stage detectors. Separate unitary reference blocks replace grid data hops and the 82-CX joint B+C for this grid-free comparison.
- `v22` is the preserved pilot sweep, not the exact-current control: five pre-stage operations were one step later and four early M-init detectors were omitted by the legacy builder. Every R45 recipe was rerun as `v22h` after the [prefix audit](prefix_comparison.json). The pilot's internal comparisons remain measured, but final conclusions use the matched context. The per-wire gate DAG is identical, so the placement models' free-timing feasible spaces are unchanged.
- Every measured row below passed Stim detector determinism (T/T_DAG removed for the known valid X_L Clifford surrogate) and the full non-Clifford exact correctness check in `tprep.check(..., shots=1e6, seed=0)`. Acceptance failures remain visible.
- Exact evaluation uses `exact2.run` or its algebraically pruned equivalent in `fast_pairs.py`, plus TREP2's pruned `exact2.third_order`. [Pair validation](pair_validation.json) agrees on loss to floating-point precision; [unchanged third-order validation](exact_validation.json) agrees exactly on the MB frame circuit. Third order is omitted unless |c1|<1e-12. exp(-A1) is an estimate, not the acceptance gate.
- Repeated exact quantum tables are memoized within a single model. Both the [reference](cache_validation.json) and [matched MB circuit](cache_mb_validation.json) reproduce uncached third order exactly; 86–88 thousand table requests require only 6,756 distinct tables. This changes computation time, not the noise model or score.
- Three independent checks use all six orders. Four-check sweeps use all 24 orders. The additional pair-product redundancy sweep covers masks 3, 5 and 6 on B+C. Hybrid orders that remove already prepared rows can coincide. Coupling orders within a four-body measurement are explicit in `perm`; they are not exhaustively enumerated.
- [recipes.csv](recipes.csv) records QASM hashes and regeneration parameters; [regeneration verification](regeneration.receipt.json) checks exact reconstruction before bulk removal. Retained finalists include QASM, judge metadata, and numerical receipts.

## Best measured order per grid-free structure

| Prefix | MB blocks | Structure | Variants | Best order | 2nd | 3rd | Total | exp(-A1) | 1e6 acceptance |
|---|---|---|---:|---|---:|---:|---:|---:|---:|
| sep | none | direct | 1 | 012 | 3.338849e-05 | 2.096233e-06 | 3.548473e-05 | 0.67283 | 0.671797 |
| sep | A | cat | 6 | 210 | 6.529728e-05 | 4.246477e-06 | 6.954376e-05 | 0.65014 | 0.649892 |
| sep | A | cat13 | 6 | 201 | 3.741e-05 | 5.14215e-06 | 4.255215e-05 | 0.64694 | 0.646514 |
| sep | A | cat13red | 24 | 210 | 3.782706e-05 | 5.060456e-06 | 4.288752e-05 | 0.63435 | 0.634678 |
| sep | A | cat3 | 7 | 021 | 7.460397e-05 | 5.320145e-06 | 7.992411e-05 | 0.64267 | 0.642013 |
| sep | A | cat4 | 6 | 210 | 8.713815e-05 | 7.447106e-06 | 9.458525e-05 | 0.63159 | 0.630852 |
| sep | A | catred | 24 | 2301 | 7.179303e-05 | 3.797538e-06 | 7.559057e-05 | 0.64072 | 0.639931 |
| sep | A | direct | 7 | 201 | 3.666407e-05 | 4.570257e-06 | 4.123433e-05 | 0.65046 | 0.649773 |
| sep | A | flag | 6 | 201 | 3.156626e-05 | 4.901199e-06 | 3.646745e-05 | 0.62847 | 0.628184 |
| sep | A | hybrid1 | 6 | 021 | 3.623118e-05 | 5.219473e-06 | 4.145065e-05 | 0.64667 | 0.646630 |
| sep | A | hybrid2 | 6 | 012 | 3.555542e-05 | 4.546212e-06 | 4.010164e-05 | 0.65025 | 0.649437 |
| sep | A | hybrid2t | 1 | 012 | 4.468109e-05 | 4.889171e-06 | 4.957027e-05 | 0.64767 | 0.647493 |
| sep | A | redundant | 24 | 210 | 3.640161e-05 | 4.175094e-06 | 4.057671e-05 | 0.64343 | 0.642674 |
| sep | A | seq | 6 | 201 | 3.772744e-05 | 1.007361e-05 | 4.780105e-05 | 0.62019 | 0.620517 |
| sep | AB | cat | 6 | 210 | 8.099177e-05 | 5.80095e-06 | 8.679272e-05 | 0.62821 | 0.627695 |
| sep | AB | direct | 6 | 210 | 3.835599e-05 | 5.93658e-06 | 4.429256e-05 | 0.62883 | 0.628785 |
| sep | AB | flag | 6 | 201 | 3.146848e-05 | 7.057197e-06 | 3.852567e-05 | 0.58703 | 0.587276 |
| sep | AB | hybrid1 | 6 | 021 | 3.811181e-05 | 7.003455e-06 | 4.511526e-05 | 0.62152 | 0.620340 |
| sep | AB | hybrid2 | 6 | 012 | 3.638526e-05 | 5.821339e-06 | 4.22066e-05 | 0.62843 | 0.628192 |
| sep | AB | hybrid2t | 1 | 012 | 4.794706e-05 | 6.420592e-06 | 5.436765e-05 | 0.62346 | 0.622791 |
| sep | AB | redundant | 24 | 210 | 3.635317e-05 | 4.449945e-06 | 4.080311e-05 | 0.61531 | 0.614402 |
| sep | AB | seq | 6 | 210 | 4.022916e-05 | 1.541138e-05 | 5.564054e-05 | 0.57168 | 0.571155 |
| sep | ABC | cat | 6 | 210 | 0.0001022485 | 7.552053e-06 | 0.0001098005 | 0.60702 | 0.606861 |
| sep | ABC | direct | 6 | 210 | 4.003415e-05 | 7.456187e-06 | 4.749034e-05 | 0.60793 | 0.607781 |
| sep | ABC | flag | 6 | 201 | 3.146848e-05 | 9.329556e-06 | 4.079803e-05 | 0.54833 | 0.548658 |
| sep | ABC | flag,redundant,redundant | 6 | 201 | 3.158848e-05 | 5.505e-06 | 3.709348e-05 | 0.57474 | 0.574503 |
| sep | ABC | hybrid1 | 6 | 021 | 4.006354e-05 | 8.949399e-06 | 4.901294e-05 | 0.59735 | 0.597152 |
| sep | ABC | hybrid2 | 6 | 012 | 3.723288e-05 | 7.204151e-06 | 4.443703e-05 | 0.60734 | 0.606994 |
| sep | ABC | hybrid2t | 1 | 012 | 5.200191e-05 | 8.151473e-06 | 6.015338e-05 | 0.60015 | 0.599893 |
| sep | ABC | redundant | 24 | 210 | 3.647362e-05 | 4.832653e-06 | 4.130627e-05 | 0.58842 | 0.587847 |
| sep | ABC | seq | 6 | 210 | 4.226023e-05 | 2.159576e-05 | 6.385598e-05 | 0.52696 | 0.527082 |
| sep | AC | cat | 6 | 210 | 8.099177e-05 | 5.752577e-06 | 8.674435e-05 | 0.62821 | 0.627535 |
| sep | AC | direct | 6 | 210 | 3.835599e-05 | 5.898449e-06 | 4.425443e-05 | 0.62883 | 0.628010 |
| sep | AC | flag | 6 | 201 | 3.146848e-05 | 7.019393e-06 | 3.848787e-05 | 0.58703 | 0.586965 |
| sep | AC | hybrid1 | 6 | 021 | 3.811181e-05 | 6.953901e-06 | 4.506571e-05 | 0.62152 | 0.620836 |
| sep | AC | hybrid2 | 6 | 012 | 3.638526e-05 | 5.782987e-06 | 4.216825e-05 | 0.62843 | 0.627557 |
| sep | AC | hybrid2t | 1 | 012 | 4.794706e-05 | 6.375278e-06 | 5.432233e-05 | 0.62346 | 0.622650 |
| sep | AC | redundant | 24 | 210 | 3.635317e-05 | 4.406516e-06 | 4.075969e-05 | 0.61531 | 0.614643 |
| sep | AC | seq | 6 | 210 | 4.022916e-05 | 1.531582e-05 | 5.554498e-05 | 0.57168 | 0.571474 |
| sep | B | cat | 6 | 102 | 3.460829e-05 | 3.087298e-06 | 3.769558e-05 | 0.65095 | 0.650683 |
| sep | B | cat13 | 6 | 120 | 3.459688e-05 | 3.111554e-06 | 3.770843e-05 | 0.64694 | 0.646121 |
| sep | B | cat13red | 24 | 3201 | 3.313285e-05 | 2.162603e-06 | 3.529545e-05 | 0.63258 | 0.631949 |
| sep | B | cat3 | 6 | 102 | 3.51106e-05 | 3.480421e-06 | 3.859102e-05 | 0.64267 | 0.642268 |
| sep | B | cat3red | 24 | 0213 | 3.332174e-05 | 2.187634e-06 | 3.550937e-05 | 0.63171 | 0.630981 |
| sep | B | cat3reusered | 24 | 0213 | 3.369768e-05 | 2.996903e-06 | 3.669459e-05 | 0.57826 | 0.577909 |
| sep | B | cat3spinered | 24 | 3102 | 3.352947e-05 | 3.039875e-06 | 3.656935e-05 | 0.57948 | 0.579313 |
| sep | B | cat4 | 6 | 120 | 3.553937e-05 | 3.815333e-06 | 3.93547e-05 | 0.63159 | 0.631238 |
| sep | B | catred | 24 | 0132 | 3.338603e-05 | 2.117226e-06 | 3.550326e-05 | 0.64212 | 0.641418 |
| sep | B | direct | 6 | 120 | 3.434728e-05 | 2.929891e-06 | 3.727717e-05 | 0.65046 | 0.649622 |
| sep | B | flag | 6 | 120 | 3.486109e-05 | 3.342711e-06 | 3.82038e-05 | 0.62847 | 0.628103 |
| sep | B | hybrid1 | 6 | 012 | 3.446663e-05 | 3.087919e-06 | 3.755455e-05 | 0.64666 | 0.645947 |
| sep | B | hybrid2 | 6 | 012 | 3.408073e-05 | 2.873675e-06 | 3.695441e-05 | 0.65025 | 0.649772 |
| sep | B | hybrid2t | 1 | 012 | 3.428423e-05 | 2.999093e-06 | 3.728332e-05 | 0.64767 | 0.646569 |
| sep | B | redundant | 24 | 201 | 3.333226e-05 | 2.295201e-06 | 3.562746e-05 | 0.64343 | 0.642628 |
| sep | B | seq | 6 | 102 | 3.448726e-05 | 4.036858e-06 | 3.852412e-05 | 0.62081 | 0.620278 |
| sep | BC | cat | 6 | 210 | 4.22111e-05 | 4.147433e-06 | 4.635854e-05 | 0.62821 | 0.628714 |
| sep | BC | cat13 | 6 | 120 | 3.600082e-05 | 4.327638e-06 | 4.032846e-05 | 0.62204 | 0.621555 |
| sep | BC | cat13red | 24 | 3201 | 3.305943e-05 | 2.547309e-06 | 3.560674e-05 | 0.59474 | 0.593402 |
| sep | BC | cat13red mask=3 | 24 | 0123 | 3.40106e-05 | 2.748257e-06 | 3.675885e-05 | 0.61176 | 0.611725 |
| sep | BC | cat13red mask=5 | 24 | 0123 | 3.298838e-05 | 2.913191e-06 | 3.590157e-05 | 0.61257 | 0.613087 |
| sep | BC | cat13red mask=6 | 24 | 3120 | 3.457895e-05 | 3.335823e-06 | 3.791478e-05 | 0.59530 | 0.595745 |
| sep | BC | cat3 | 6 | 102 | 4.609715e-05 | 5.271411e-06 | 5.136856e-05 | 0.61387 | 0.613684 |
| sep | BC | cat3red | 24 | 3102 | 4.273048e-05 | 2.977165e-06 | 4.570764e-05 | 0.58581 | 0.586283 |
| sep | BC | cat3reusered | 24 | 3102 | 4.326062e-05 | 6.967155e-06 | 5.022778e-05 | 0.49908 | 0.499935 |
| sep | BC | cat3spinered | 25 | 1302 | 4.647934e-05 | 6.769247e-06 | 5.324859e-05 | 0.49908 | 0.499939 |
| sep | BC | cat4 | 6 | 120 | 4.667024e-05 | 6.227057e-06 | 5.28973e-05 | 0.59288 | 0.592884 |
| sep | BC | catred | 24 | 3210 | 3.964491e-05 | 2.438388e-06 | 4.20833e-05 | 0.61014 | 0.609650 |
| sep | BC | direct | 6 | 120 | 3.550162e-05 | 3.901658e-06 | 3.940328e-05 | 0.62883 | 0.628351 |
| sep | BC | flag | 6 | 120 | 3.643146e-05 | 4.733801e-06 | 4.116527e-05 | 0.58703 | 0.587086 |
| sep | BC | hybrid1 | 6 | 012 | 3.562476e-05 | 4.234725e-06 | 3.985949e-05 | 0.62152 | 0.620751 |
| sep | BC | hybrid2 | 6 | 012 | 3.479075e-05 | 3.757483e-06 | 3.854823e-05 | 0.62843 | 0.627870 |
| sep | BC | hybrid2t | 1 | 012 | 3.596886e-05 | 4.075987e-06 | 4.004484e-05 | 0.62346 | 0.622569 |
| sep | BC | redundant | 24 | 201 | 3.343602e-05 | 2.601405e-06 | 3.603743e-05 | 0.61530 | 0.614889 |
| sep | BC | redundant mask=3 | 24 | 0123 | 3.402707e-05 | 2.668634e-06 | 3.669571e-05 | 0.62772 | 0.627356 |
| sep | BC | redundant mask=5 | 24 | 0123 | 3.325433e-05 | 2.80563e-06 | 3.605996e-05 | 0.62772 | 0.626500 |
| sep | BC | redundant mask=6 | 24 | 2310 | 3.450654e-05 | 3.027671e-06 | 3.753421e-05 | 0.62231 | 0.621440 |
| sep | BC | seq | 6 | 102 | 3.577269e-05 | 6.708041e-06 | 4.248073e-05 | 0.57281 | 0.572816 |
| sep | C | cat | 6 | 102 | 3.460829e-05 | 3.036813e-06 | 3.76451e-05 | 0.65095 | 0.650830 |
| sep | C | cat13 | 6 | 120 | 3.459688e-05 | 3.063874e-06 | 3.766075e-05 | 0.64694 | 0.646071 |
| sep | C | cat13red | 24 | 3201 | 3.313285e-05 | 2.095363e-06 | 3.522821e-05 | 0.63258 | 0.631815 |
| sep | C | cat3 | 6 | 102 | 3.51106e-05 | 3.407817e-06 | 3.851841e-05 | 0.64267 | 0.642301 |
| sep | C | cat3red | 24 | 0213 | 3.332174e-05 | 2.096793e-06 | 3.541853e-05 | 0.63171 | 0.631766 |
| sep | C | cat3reusered | 24 | 0213 | 3.369768e-05 | 2.800398e-06 | 3.649808e-05 | 0.57826 | 0.577862 |
| sep | C | cat3spinered | 24 | 3102 | 3.352947e-05 | 2.847667e-06 | 3.637714e-05 | 0.57948 | 0.578679 |
| sep | C | cat4 | 6 | 120 | 3.553937e-05 | 3.71127e-06 | 3.925064e-05 | 0.63159 | 0.631319 |
| sep | C | catred | 24 | 1302 | 3.338603e-05 | 2.054659e-06 | 3.544069e-05 | 0.64148 | 0.640699 |
| sep | C | direct | 6 | 120 | 3.434728e-05 | 2.891814e-06 | 3.723909e-05 | 0.65046 | 0.649952 |
| sep | C | flag | 6 | 120 | 3.486109e-05 | 3.304962e-06 | 3.816605e-05 | 0.62847 | 0.627962 |
| sep | C | hybrid1 | 6 | 012 | 3.446663e-05 | 3.038374e-06 | 3.7505e-05 | 0.64666 | 0.645689 |
| sep | C | hybrid2 | 6 | 012 | 3.408073e-05 | 2.835323e-06 | 3.691605e-05 | 0.65025 | 0.649007 |
| sep | C | hybrid2t | 1 | 012 | 3.428423e-05 | 2.953779e-06 | 3.723801e-05 | 0.64767 | 0.647335 |
| sep | C | redundant | 24 | 201 | 3.333226e-05 | 2.251713e-06 | 3.558397e-05 | 0.64343 | 0.642890 |
| sep | C | seq | 6 | 102 | 3.448726e-05 | 3.942794e-06 | 3.843005e-05 | 0.62081 | 0.620537 |
| v22 | none | direct | 1 | 012 | 3.858427e-05 | 1.240382e-05 | 5.098808e-05 | 0.60239 | 0.601428 |
| v22 | A | cat | 6 | 210 | 8.490774e-05 | 1.885746e-05 | 0.0001037652 | 0.58207 | 0.581825 |
| v22 | A | cat13 | 6 | 201 | 4.223177e-05 | 2.086116e-05 | 6.309293e-05 | 0.57921 | 0.579379 |
| v22 | A | cat13red | 24 | 201 | 4.234042e-05 | 1.929884e-05 | 6.163926e-05 | 0.56794 | 0.567731 |
| v22 | A | cat3 | 6 | 021 | 9.855967e-05 | 2.173181e-05 | 0.0001202915 | 0.57539 | 0.575106 |
| v22 | A | cat4 | 6 | 210 | 0.0001120516 | 2.684776e-05 | 0.0001388993 | 0.56547 | 0.565026 |
| v22 | A | catred | 24 | 2301 | 9.260544e-05 | 1.66563e-05 | 0.0001092617 | 0.57364 | 0.573479 |
| v22 | A | direct | 6 | 201 | 4.144974e-05 | 1.945505e-05 | 6.090479e-05 | 0.58236 | 0.582173 |
| v22 | A | flag | 6 | 201 | 3.377584e-05 | 2.06488e-05 | 5.442464e-05 | 0.56268 | 0.561823 |
| v22 | A | hybrid1 | 6 | 021 | 4.1806e-05 | 2.125479e-05 | 6.306079e-05 | 0.57897 | 0.578635 |
| v22 | A | hybrid2 | 6 | 012 | 4.063856e-05 | 1.969098e-05 | 6.032955e-05 | 0.58218 | 0.582251 |
| v22 | A | hybrid2t | 1 | 012 | 5.484709e-05 | 2.062305e-05 | 7.547014e-05 | 0.57987 | 0.578815 |
| v22 | A | redundant | 24 | 201 | 4.097785e-05 | 1.768538e-05 | 5.866323e-05 | 0.57606 | 0.576067 |
| v22 | A | seq | 6 | 201 | 4.249942e-05 | 3.246473e-05 | 7.496414e-05 | 0.55531 | 0.555640 |
| v22 | AB | cat | 6 | 210 | 0.0001006022 | 2.286313e-05 | 0.0001234654 | 0.56244 | 0.561558 |
| v22 | AB | direct | 6 | 201 | 4.324743e-05 | 2.30584e-05 | 6.630583e-05 | 0.56300 | 0.562704 |
| v22 | AB | flag | 6 | 201 | 3.367806e-05 | 2.613573e-05 | 5.98138e-05 | 0.52558 | 0.525172 |
| v22 | AB | hybrid1 | 6 | 021 | 4.368663e-05 | 2.542186e-05 | 6.910849e-05 | 0.55646 | 0.556683 |
| v22 | AB | hybrid2 | 6 | 012 | 4.14684e-05 | 2.295983e-05 | 6.442823e-05 | 0.56264 | 0.562397 |
| v22 | AB | hybrid2t | 1 | 012 | 5.811305e-05 | 2.439868e-05 | 8.251173e-05 | 0.55819 | 0.558113 |
| v22 | AB | redundant | 6 | 201 | 4.090727e-05 | 1.834065e-05 | 5.924792e-05 | 0.55089 | 0.550757 |
| v22 | AB | seq | 6 | 201 | 4.535581e-05 | 4.405062e-05 | 8.940643e-05 | 0.51186 | 0.511582 |
| v22 | ABC | cat | 6 | 210 | 0.0001218589 | 2.707915e-05 | 0.0001489381 | 0.54347 | 0.543058 |
| v22 | ABC | direct | 6 | 210 | 4.505104e-05 | 2.678847e-05 | 7.183952e-05 | 0.54428 | 0.544311 |
| v22 | ABC | flag | 6 | 201 | 3.367806e-05 | 3.174039e-05 | 6.541845e-05 | 0.49093 | 0.491251 |
| v22 | ABC | flag,redundant,redundant | 6 | 201 | 3.379806e-05 | 2.199893e-05 | 5.579699e-05 | 0.51457 | 0.514198 |
| v22 | ABC | hybrid1 | 6 | 021 | 4.563837e-05 | 2.975169e-05 | 7.539006e-05 | 0.53482 | 0.535462 |
| v22 | ABC | hybrid2 | 6 | 012 | 4.231602e-05 | 2.633625e-05 | 6.865227e-05 | 0.54376 | 0.543833 |
| v22 | ABC | hybrid2t | 2 | 012 | 6.21679e-05 | 2.837407e-05 | 9.054197e-05 | 0.53732 | 0.537277 |
| v22 | ABC | redundant | 24 | 201 | 4.099669e-05 | 1.910495e-05 | 6.010165e-05 | 0.52681 | 0.526660 |
| v22 | ABC | seq | 6 | 210 | 4.751045e-05 | 5.640565e-05 | 0.0001039161 | 0.47183 | 0.471160 |
| v22 | AC | cat | 6 | 210 | 0.0001006022 | 2.281475e-05 | 0.000123417 | 0.56244 | 0.562096 |
| v22 | AC | direct | 6 | 201 | 4.324743e-05 | 2.302023e-05 | 6.626766e-05 | 0.56300 | 0.562252 |
| v22 | AC | flag | 6 | 201 | 3.367806e-05 | 2.609793e-05 | 5.977599e-05 | 0.52558 | 0.525846 |
| v22 | AC | hybrid1 | 6 | 021 | 4.368663e-05 | 2.537231e-05 | 6.905894e-05 | 0.55646 | 0.555914 |
| v22 | AC | hybrid2 | 6 | 012 | 4.14684e-05 | 2.292148e-05 | 6.438988e-05 | 0.56264 | 0.562037 |
| v22 | AC | hybrid2t | 1 | 012 | 5.811305e-05 | 2.435337e-05 | 8.246642e-05 | 0.55819 | 0.558037 |
| v22 | AC | redundant | 6 | 201 | 4.090727e-05 | 1.829716e-05 | 5.920443e-05 | 0.55089 | 0.550360 |
| v22 | AC | seq | 6 | 201 | 4.535581e-05 | 4.395491e-05 | 8.931071e-05 | 0.51186 | 0.511404 |
| v22 | B | cat | 6 | 102 | 3.980406e-05 | 1.535593e-05 | 5.516e-05 | 0.58280 | 0.581564 |
| v22 | B | cat13 | 6 | 012 | 3.980587e-05 | 1.553874e-05 | 5.534461e-05 | 0.57979 | 0.578944 |
| v22 | B | cat13red | 24 | 3201 | 3.832862e-05 | 1.23738e-05 | 5.070243e-05 | 0.56635 | 0.565723 |
| v22 | B | cat3 | 6 | 102 | 4.030637e-05 | 1.645792e-05 | 5.67643e-05 | 0.57539 | 0.575529 |
| v22 | B | cat3red | 24 | 0213 | 3.851751e-05 | 1.225313e-05 | 5.077065e-05 | 0.56558 | 0.565080 |
| v22 | B | cat3reusered | 24 | 0213 | 3.888707e-05 | 1.418153e-05 | 5.30686e-05 | 0.51776 | 0.517157 |
| v22 | B | cat3spinered | 24 | 0213 | 3.884713e-05 | 1.411117e-05 | 5.29583e-05 | 0.51885 | 0.518022 |
| v22 | B | cat4 | 6 | 120 | 4.073514e-05 | 1.750186e-05 | 5.823701e-05 | 0.56547 | 0.564911 |
| v22 | B | catred | 24 | 0132 | 3.858181e-05 | 1.225041e-05 | 5.083222e-05 | 0.57490 | 0.574371 |
| v22 | B | direct | 6 | 012 | 3.955615e-05 | 1.50015e-05 | 5.455765e-05 | 0.58295 | 0.582397 |
| v22 | B | flag | 6 | 120 | 4.005604e-05 | 1.630548e-05 | 5.636152e-05 | 0.56268 | 0.561308 |
| v22 | B | hybrid1 | 6 | 012 | 3.966158e-05 | 1.51364e-05 | 5.479798e-05 | 0.57897 | 0.578707 |
| v22 | B | hybrid2 | 6 | 012 | 3.927651e-05 | 1.469813e-05 | 5.397463e-05 | 0.58218 | 0.582531 |
| v22 | B | hybrid2t | 1 | 012 | 3.947918e-05 | 1.499926e-05 | 5.447844e-05 | 0.57987 | 0.579028 |
| v22 | B | redundant | 24 | 201 | 3.852803e-05 | 1.285706e-05 | 5.138509e-05 | 0.57606 | 0.575483 |
| v22 | B | seq | 6 | 102 | 3.967665e-05 | 1.804674e-05 | 5.772338e-05 | 0.55586 | 0.555383 |
| v22 | BC | cat | 6 | 210 | 4.740688e-05 | 1.862621e-05 | 6.603308e-05 | 0.56244 | 0.562223 |
| v22 | BC | cat13 | 6 | 012 | 4.121414e-05 | 1.886757e-05 | 6.008171e-05 | 0.55804 | 0.557912 |
| v22 | BC | cat13red | 24 | 3201 | 3.82552e-05 | 1.266277e-05 | 5.091797e-05 | 0.53247 | 0.532287 |
| v22 | BC | cat13red mask=3 | 24 | 0123 | 3.920637e-05 | 1.404671e-05 | 5.325308e-05 | 0.54771 | 0.547295 |
| v22 | BC | cat13red mask=5 | 24 | 0123 | 3.818415e-05 | 1.453279e-05 | 5.271694e-05 | 0.54844 | 0.547785 |
| v22 | BC | cat13red mask=6 | 24 | 3120 | 3.97739e-05 | 1.46954e-05 | 5.44693e-05 | 0.53298 | 0.532485 |
| v22 | BC | cat3 | 6 | 102 | 5.129292e-05 | 2.094605e-05 | 7.223897e-05 | 0.54960 | 0.549744 |
| v22 | BC | cat3red | 24 | 3102 | 4.792625e-05 | 1.304922e-05 | 6.097548e-05 | 0.52448 | 0.524716 |
| v22 | BC | cat3reusered | 24 | 3102 | 4.845001e-05 | 1.952486e-05 | 6.797487e-05 | 0.44686 | 0.446171 |
| v22 | BC | cat3spinered | 25 | 0213 | 5.193416e-05 | 1.855571e-05 | 7.048986e-05 | 0.44686 | 0.446549 |
| v22 | BC | cat4 | 6 | 120 | 5.186602e-05 | 2.329655e-05 | 7.516257e-05 | 0.53081 | 0.530866 |
| v22 | BC | catred | 24 | 3210 | 4.484068e-05 | 1.286063e-05 | 5.770132e-05 | 0.54626 | 0.545629 |
| v22 | BC | direct | 6 | 012 | 4.07147e-05 | 1.773172e-05 | 5.844643e-05 | 0.56413 | 0.563850 |
| v22 | BC | flag | 6 | 120 | 4.162641e-05 | 2.035432e-05 | 6.198074e-05 | 0.52558 | 0.525185 |
| v22 | BC | hybrid1 | 6 | 012 | 4.081971e-05 | 1.802596e-05 | 5.884568e-05 | 0.55645 | 0.556217 |
| v22 | BC | hybrid2 | 6 | 012 | 3.998652e-05 | 1.709868e-05 | 5.708521e-05 | 0.56264 | 0.561805 |
| v22 | BC | hybrid2t | 2 | 012 | 4.116381e-05 | 1.777025e-05 | 5.893405e-05 | 0.55819 | 0.557755 |
| v22 | BC | redundant | 24 | 201 | 3.86318e-05 | 1.341827e-05 | 5.205006e-05 | 0.55089 | 0.551068 |
| v22 | BC | redundant mask=3 | 24 | 0123 | 3.922285e-05 | 1.396911e-05 | 5.319196e-05 | 0.56200 | 0.561674 |
| v22 | BC | redundant mask=5 | 24 | 0123 | 3.845011e-05 | 1.438703e-05 | 5.283713e-05 | 0.56200 | 0.561503 |
| v22 | BC | redundant mask=6 | 24 | 1203 | 3.984021e-05 | 1.432314e-05 | 5.416335e-05 | 0.55864 | 0.557979 |
| v22 | BC | seq | 6 | 102 | 4.096208e-05 | 2.443093e-05 | 6.539301e-05 | 0.51289 | 0.512515 |
| v22 | C | cat | 6 | 102 | 3.980406e-05 | 1.530545e-05 | 5.510951e-05 | 0.58280 | 0.582574 |
| v22 | C | cat13 | 6 | 012 | 3.980587e-05 | 1.549235e-05 | 5.529822e-05 | 0.57979 | 0.578817 |
| v22 | C | cat13red | 24 | 3201 | 3.832862e-05 | 1.230656e-05 | 5.063519e-05 | 0.56635 | 0.566214 |
| v22 | C | cat3 | 6 | 102 | 4.030637e-05 | 1.638532e-05 | 5.669169e-05 | 0.57539 | 0.574681 |
| v22 | C | cat3red | 24 | 0213 | 3.851751e-05 | 1.216229e-05 | 5.067981e-05 | 0.56558 | 0.566016 |
| v22 | C | cat3reusered | 24 | 0213 | 3.888707e-05 | 1.398503e-05 | 5.28721e-05 | 0.51776 | 0.517798 |
| v22 | C | cat3spinered | 24 | 0213 | 3.884713e-05 | 1.391855e-05 | 5.276568e-05 | 0.51885 | 0.518877 |
| v22 | C | cat4 | 6 | 120 | 4.073514e-05 | 1.73978e-05 | 5.813294e-05 | 0.56547 | 0.564604 |
| v22 | C | catred | 24 | 0132 | 3.858181e-05 | 1.218815e-05 | 5.076996e-05 | 0.57490 | 0.574436 |
| v22 | C | direct | 6 | 012 | 3.955615e-05 | 1.496472e-05 | 5.452087e-05 | 0.58295 | 0.582531 |
| v22 | C | flag | 6 | 120 | 4.005604e-05 | 1.626773e-05 | 5.632377e-05 | 0.56268 | 0.562554 |
| v22 | C | hybrid1 | 6 | 012 | 3.966158e-05 | 1.508685e-05 | 5.474843e-05 | 0.57897 | 0.578570 |
| v22 | C | hybrid2 | 6 | 012 | 3.927651e-05 | 1.465977e-05 | 5.393628e-05 | 0.58218 | 0.582498 |
| v22 | C | hybrid2t | 1 | 012 | 3.947918e-05 | 1.495394e-05 | 5.443312e-05 | 0.57987 | 0.579107 |
| v22 | C | redundant | 24 | 201 | 3.852803e-05 | 1.281357e-05 | 5.13416e-05 | 0.57606 | 0.574845 |
| v22 | C | seq | 6 | 102 | 3.967665e-05 | 1.795267e-05 | 5.762932e-05 | 0.55586 | 0.555830 |
| v22h | none | direct | 2 | 012 | 3.864948e-05 | 1.255789e-05 | 5.120737e-05 | 0.60321 | 0.602356 |
| v22h | A | cat | 6 | 210 | 8.490909e-05 | 1.904722e-05 | 0.0001039563 | 0.58286 | 0.583203 |
| v22h | A | cat13 | 6 | 201 | 4.223199e-05 | 2.108835e-05 | 6.332034e-05 | 0.57999 | 0.579560 |
| v22h | A | cat13red | 24 | 201 | 4.234062e-05 | 1.955181e-05 | 6.189243e-05 | 0.56871 | 0.567476 |
| v22h | A | cat3 | 6 | 021 | 9.856134e-05 | 2.193835e-05 | 0.0001204997 | 0.57617 | 0.576381 |
| v22h | A | cat4 | 6 | 210 | 0.0001120533 | 2.711335e-05 | 0.0001391667 | 0.56624 | 0.566491 |
| v22h | A | catred | 24 | 2301 | 9.260676e-05 | 1.685438e-05 | 0.0001094611 | 0.57442 | 0.574130 |
| v22h | A | direct | 6 | 201 | 4.144996e-05 | 1.966455e-05 | 6.111451e-05 | 0.58315 | 0.582617 |
| v22h | A | flag | 6 | 201 | 3.377585e-05 | 2.086278e-05 | 5.463864e-05 | 0.56344 | 0.562023 |
| v22h | A | hybrid1 | 6 | 021 | 4.189347e-05 | 2.149121e-05 | 6.338468e-05 | 0.57976 | 0.579833 |
| v22h | A | hybrid2 | 6 | 012 | 4.07041e-05 | 1.990181e-05 | 6.060591e-05 | 0.58297 | 0.582448 |
| v22h | A | hybrid2t | 1 | 012 | 5.484719e-05 | 2.083351e-05 | 7.56807e-05 | 0.58066 | 0.579800 |
| v22h | A | redundant | 24 | 201 | 4.097804e-05 | 1.790676e-05 | 5.88848e-05 | 0.57684 | 0.576613 |
| v22h | A | seq | 6 | 201 | 4.249942e-05 | 3.276483e-05 | 7.526425e-05 | 0.55606 | 0.555610 |
| v22h | AB | cat | 6 | 210 | 0.0001006036 | 2.312173e-05 | 0.0001237253 | 0.56320 | 0.563471 |
| v22h | AB | direct | 6 | 201 | 4.324765e-05 | 2.33273e-05 | 6.657496e-05 | 0.56376 | 0.563635 |
| v22h | AB | flag | 6 | 201 | 3.367808e-05 | 2.644353e-05 | 6.012161e-05 | 0.52629 | 0.526116 |
| v22h | AB | hybrid1 | 6 | 021 | 4.37741e-05 | 2.572633e-05 | 6.950042e-05 | 0.55721 | 0.556244 |
| v22h | AB | hybrid2 | 6 | 012 | 4.153394e-05 | 2.322709e-05 | 6.476103e-05 | 0.56340 | 0.563339 |
| v22h | AB | hybrid2t | 1 | 012 | 5.811315e-05 | 2.46739e-05 | 8.278705e-05 | 0.55895 | 0.558678 |
| v22h | AB | redundant | 24 | 201 | 4.090746e-05 | 1.857203e-05 | 5.947949e-05 | 0.55163 | 0.551045 |
| v22h | AB | seq | 6 | 201 | 4.535581e-05 | 4.449315e-05 | 8.984896e-05 | 0.51256 | 0.512851 |
| v22h | ABC | cat | 6 | 210 | 0.0001218603 | 2.740669e-05 | 0.000149267 | 0.54420 | 0.544561 |
| v22h | ABC | direct | 6 | 210 | 4.505127e-05 | 2.712437e-05 | 7.217564e-05 | 0.54502 | 0.544599 |
| v22h | ABC | flag | 6 | 201 | 3.367808e-05 | 3.214203e-05 | 6.582011e-05 | 0.49159 | 0.491836 |
| v22h | ABC | flag,redundant,redundant | 6 | 201 | 3.379808e-05 | 2.223288e-05 | 5.603095e-05 | 0.51527 | 0.515316 |
| v22h | ABC | hybrid1 | 6 | 021 | 4.572584e-05 | 3.012421e-05 | 7.585005e-05 | 0.53554 | 0.536905 |
| v22h | ABC | hybrid2 | 6 | 012 | 4.238155e-05 | 2.665994e-05 | 6.904149e-05 | 0.54450 | 0.544683 |
| v22h | ABC | hybrid2t | 1 | 012 | 6.2168e-05 | 2.871404e-05 | 9.088204e-05 | 0.53805 | 0.537673 |
| v22h | ABC | redundant | 24 | 201 | 4.099689e-05 | 1.934636e-05 | 6.034324e-05 | 0.52752 | 0.527533 |
| v22h | ABC | seq | 6 | 210 | 4.751045e-05 | 5.703175e-05 | 0.0001045422 | 0.47247 | 0.472581 |
| v22h | AC | cat | 6 | 210 | 0.0001006036 | 2.307336e-05 | 0.0001236769 | 0.56320 | 0.563098 |
| v22h | AC | direct | 6 | 201 | 4.324765e-05 | 2.328913e-05 | 6.653678e-05 | 0.56376 | 0.563334 |
| v22h | AC | flag | 6 | 201 | 3.367808e-05 | 2.640573e-05 | 6.00838e-05 | 0.52629 | 0.525978 |
| v22h | AC | hybrid1 | 6 | 021 | 4.37741e-05 | 2.567677e-05 | 6.945087e-05 | 0.55721 | 0.557436 |
| v22h | AC | hybrid2 | 6 | 012 | 4.153394e-05 | 2.318874e-05 | 6.472268e-05 | 0.56340 | 0.563366 |
| v22h | AC | hybrid2t | 1 | 012 | 5.811315e-05 | 2.462858e-05 | 8.274173e-05 | 0.55895 | 0.558816 |
| v22h | AC | redundant | 24 | 201 | 4.090746e-05 | 1.852854e-05 | 5.9436e-05 | 0.55163 | 0.552156 |
| v22h | AC | seq | 6 | 201 | 4.535581e-05 | 4.439743e-05 | 8.975324e-05 | 0.51256 | 0.513754 |
| v22h | B | cat | 6 | 102 | 3.986928e-05 | 1.556991e-05 | 5.543919e-05 | 0.58359 | 0.583534 |
| v22h | B | cat13 | 6 | 012 | 3.987108e-05 | 1.57546e-05 | 5.562568e-05 | 0.58058 | 0.579821 |
| v22h | B | cat13red | 24 | 3201 | 3.839384e-05 | 1.252442e-05 | 5.091826e-05 | 0.56712 | 0.566117 |
| v22h | B | cat3 | 6 | 102 | 4.037159e-05 | 1.6692e-05 | 5.706359e-05 | 0.57617 | 0.575381 |
| v22h | B | cat3red | 24 | 0213 | 3.858273e-05 | 1.240019e-05 | 5.098291e-05 | 0.56635 | 0.565972 |
| v22h | B | cat3reusered | 24 | 0213 | 3.895218e-05 | 1.435693e-05 | 5.330911e-05 | 0.51846 | 0.518583 |
| v22h | B | cat3spinered | 24 | 0213 | 3.891224e-05 | 1.428613e-05 | 5.319837e-05 | 0.51956 | 0.518702 |
| v22h | B | cat4 | 6 | 120 | 4.080036e-05 | 1.775411e-05 | 5.855447e-05 | 0.56624 | 0.566046 |
| v22h | B | catred | 24 | 0132 | 3.864702e-05 | 1.239944e-05 | 5.104647e-05 | 0.57567 | 0.575161 |
| v22h | B | direct | 6 | 012 | 3.962137e-05 | 1.520695e-05 | 5.482832e-05 | 0.58374 | 0.583753 |
| v22h | B | flag | 6 | 120 | 4.012125e-05 | 1.653653e-05 | 5.665778e-05 | 0.56344 | 0.562978 |
| v22h | B | hybrid1 | 6 | 012 | 3.972679e-05 | 1.534347e-05 | 5.507026e-05 | 0.57976 | 0.579689 |
| v22h | B | hybrid2 | 6 | 012 | 3.934172e-05 | 1.489608e-05 | 5.42378e-05 | 0.58297 | 0.582863 |
| v22h | B | hybrid2t | 1 | 012 | 3.954439e-05 | 1.520348e-05 | 5.474787e-05 | 0.58066 | 0.580946 |
| v22h | B | redundant | 24 | 201 | 3.859325e-05 | 1.301842e-05 | 5.161167e-05 | 0.57684 | 0.574850 |
| v22h | B | seq | 6 | 102 | 3.974176e-05 | 1.831491e-05 | 5.805667e-05 | 0.55662 | 0.555568 |
| v22h | BC | cat | 6 | 210 | 4.747209e-05 | 1.889496e-05 | 6.636705e-05 | 0.56320 | 0.562384 |
| v22h | BC | cat13 | 6 | 012 | 4.127935e-05 | 1.914524e-05 | 6.042459e-05 | 0.55880 | 0.558911 |
| v22h | BC | cat13red | 25 | 3201 | 3.832042e-05 | 1.280996e-05 | 5.113038e-05 | 0.53319 | 0.532852 |
| v22h | BC | cat13red mask=3 | 24 | 0123 | 3.927159e-05 | 1.422023e-05 | 5.349182e-05 | 0.54846 | 0.548641 |
| v22h | BC | cat13red mask=5 | 24 | 0123 | 3.824936e-05 | 1.472776e-05 | 5.297713e-05 | 0.54919 | 0.548958 |
| v22h | BC | cat13red mask=6 | 24 | 3120 | 3.983912e-05 | 1.488609e-05 | 5.472521e-05 | 0.53370 | 0.533435 |
| v22h | BC | cat3 | 6 | 102 | 5.135813e-05 | 2.126026e-05 | 7.261839e-05 | 0.55034 | 0.550761 |
| v22h | BC | cat3red | 24 | 3102 | 4.799147e-05 | 1.319708e-05 | 6.118855e-05 | 0.52519 | 0.524898 |
| v22h | BC | cat3reusered | 24 | 3102 | 4.851512e-05 | 1.975166e-05 | 6.826678e-05 | 0.44747 | 0.447344 |
| v22h | BC | cat3spinered | 24 | 0213 | 5.199927e-05 | 1.875186e-05 | 7.075113e-05 | 0.44747 | 0.447684 |
| v22h | BC | cat4 | 6 | 120 | 5.193123e-05 | 2.364693e-05 | 7.557816e-05 | 0.53153 | 0.532108 |
| v22h | BC | catred | 24 | 3210 | 4.49059e-05 | 1.301648e-05 | 5.792237e-05 | 0.54700 | 0.547174 |
| v22h | BC | direct | 6 | 012 | 4.077992e-05 | 1.798858e-05 | 5.876849e-05 | 0.56489 | 0.563926 |
| v22h | BC | flag | 6 | 120 | 4.169163e-05 | 2.06624e-05 | 6.235403e-05 | 0.52629 | 0.526485 |
| v22h | BC | hybrid1 | 6 | 012 | 4.088493e-05 | 1.828605e-05 | 5.917098e-05 | 0.55721 | 0.556473 |
| v22h | BC | hybrid2 | 6 | 012 | 4.005174e-05 | 1.734052e-05 | 5.739225e-05 | 0.56340 | 0.563603 |
| v22h | BC | hybrid2t | 1 | 012 | 4.122902e-05 | 1.802462e-05 | 5.925364e-05 | 0.55895 | 0.558206 |
| v22h | BC | redundant | 24 | 201 | 3.869701e-05 | 1.358696e-05 | 5.228397e-05 | 0.55163 | 0.550802 |
| v22h | BC | redundant mask=3 | 24 | 0123 | 3.928806e-05 | 1.414619e-05 | 5.343425e-05 | 0.56276 | 0.562819 |
| v22h | BC | redundant mask=5 | 24 | 0123 | 3.851532e-05 | 1.458164e-05 | 5.309696e-05 | 0.56276 | 0.562424 |
| v22h | BC | redundant mask=6 | 24 | 1203 | 3.990543e-05 | 1.451417e-05 | 5.441959e-05 | 0.55940 | 0.559667 |
| v22h | BC | seq | 6 | 102 | 4.102719e-05 | 2.48135e-05 | 6.584069e-05 | 0.51358 | 0.512825 |
| v22h | C | cat | 6 | 102 | 3.986928e-05 | 1.551943e-05 | 5.538871e-05 | 0.58359 | 0.583605 |
| v22h | C | cat13 | 6 | 012 | 3.987108e-05 | 1.570821e-05 | 5.557929e-05 | 0.58058 | 0.579894 |
| v22h | C | cat13red | 24 | 3201 | 3.839384e-05 | 1.245718e-05 | 5.085102e-05 | 0.56712 | 0.566468 |
| v22h | C | cat3 | 6 | 102 | 4.037159e-05 | 1.66194e-05 | 5.699098e-05 | 0.57617 | 0.576450 |
| v22h | C | cat3red | 24 | 0213 | 3.858273e-05 | 1.230935e-05 | 5.089207e-05 | 0.56635 | 0.566606 |
| v22h | C | cat3reusered | 24 | 0213 | 3.895218e-05 | 1.416042e-05 | 5.31126e-05 | 0.51846 | 0.517829 |
| v22h | C | cat3spinered | 24 | 0213 | 3.891224e-05 | 1.409352e-05 | 5.300576e-05 | 0.51956 | 0.518834 |
| v22h | C | cat4 | 6 | 120 | 4.080036e-05 | 1.765005e-05 | 5.845041e-05 | 0.56624 | 0.565726 |
| v22h | C | catred | 24 | 0132 | 3.864702e-05 | 1.233718e-05 | 5.098421e-05 | 0.57567 | 0.574825 |
| v22h | C | direct | 6 | 012 | 3.962137e-05 | 1.517017e-05 | 5.479153e-05 | 0.58374 | 0.584273 |
| v22h | C | flag | 6 | 120 | 4.012125e-05 | 1.649878e-05 | 5.662003e-05 | 0.56344 | 0.562622 |
| v22h | C | hybrid1 | 6 | 012 | 3.972679e-05 | 1.529392e-05 | 5.502072e-05 | 0.57976 | 0.579304 |
| v22h | C | hybrid2 | 6 | 012 | 3.934172e-05 | 1.485772e-05 | 5.419945e-05 | 0.58297 | 0.582427 |
| v22h | C | hybrid2t | 1 | 012 | 3.954439e-05 | 1.515816e-05 | 5.470256e-05 | 0.58066 | 0.580335 |
| v22h | C | redundant | 24 | 201 | 3.859325e-05 | 1.297493e-05 | 5.156818e-05 | 0.57684 | 0.577088 |
| v22h | C | seq | 6 | 102 | 3.974176e-05 | 1.822085e-05 | 5.796261e-05 | 0.55662 | 0.555957 |

## Three-seed MC comparisons

Each seed uses 1e8 shots, at seeds 0, 1000 and 2000. These are grid-free diagnostics unless explicitly marked physical. They cannot qualify as on-grid submissions.

| Circuit | MC 0 | MC 1000 | MC 2000 | Mean | Seed-0 acceptance | Evidence |
|---|---:|---:|---:|---:|---:|---|
| matched_cat13_BC | 5.09091781e-05 | 5.26758645e-05 | 5.04708531e-05 | 5.13519652e-05 | 0.5331062 | [matched_cat13_BC.mc.json](matched_cat13_BC.mc.json) |
| matched_ref | 5.10343269e-05 | 5.19927983e-05 | 5.32019894e-05 | 5.20763716e-05 | 0.6030255 | [matched_ref.mc.json](matched_ref.mc.json) |
| runs/v22_BC_cat13red_201 | 5.08348504e-05 | 5.19832332e-05 | 5.3833342e-05 | 5.22171419e-05 | 0.5354594 | [v22_BC_cat13red_201.mc.json](runs/v22_BC_cat13red_201.mc.json) |
| runs/v22_BC_cat13red_3201 | 5.11776455e-05 | 5.1174189e-05 | 5.27600313e-05 | 5.17039553e-05 | 0.5324590 | [v22_BC_cat13red_3201.mc.json](runs/v22_BC_cat13red_3201.mc.json) |
| runs/v22_ref | 5.26349344e-05 | 5.15915191e-05 | 5.22443898e-05 | 5.21569477e-05 | 0.6021666 | [v22_ref.mc.json](runs/v22_ref.mc.json) |
| tree2_BC_v22 | 5.97740134e-05 | 6.13191297e-05 | 6.00488579e-05 | 6.0380667e-05 | 0.5581021 | [tree2_BC_v22.mc.json](tree2_BC_v22.mc.json) |

## Placement models

`grid.py` reserves complete lifetimes with NoOverlap2D: prefix, data transfers, preparation block qubits and reusable ancillas. It includes optional block teleports, independent code automorphisms, and movement between sequential stabilizer measurements. CP-SAT proposes compact feasible circuits; only exact loss may select a built candidate. INFEASIBLE is confined to the stated graph, hop, horizon, embedding and relabeling bounds. UNKNOWN and interrupted searches are not impossibility proofs.

| Model | Status | Evidence |
|---|---|---|
| grid_c0_hop | INTERRUPTED | [grid_c0_hop.receipt.json](grid_c0_hop.receipt.json) |
| grid_cat13_r0c0 | INFEASIBLE | [grid_cat13_r0c0.receipt.json](grid_cat13_r0c0.receipt.json) |
| grid_cat3 | INFEASIBLE | [grid_cat3.receipt.json](grid_cat3.receipt.json) |
| grid_cat_r0c0 | INFEASIBLE | [grid_cat_r0c0.receipt.json](grid_cat_r0c0.receipt.json) |
| grid_h2 | INFEASIBLE | [grid_h2.receipt.json](grid_h2.receipt.json) |
| grid_h2t | INFEASIBLE | [grid_h2t.receipt.json](grid_h2t.receipt.json) |
| grid_h2t_auto | INTERRUPTED | [grid_h2t_auto.receipt.json](grid_h2t_auto.receipt.json) |
| grid_spine | UNKNOWN | [grid_spine.receipt.json](grid_spine.receipt.json) |
| grid_stage_bc | UNKNOWN | [grid_stage_bc.receipt.json](grid_stage_bc.receipt.json) |
| grid_tree_fixed | UNKNOWN | [grid_tree_fixed.receipt.json](grid_tree_fixed.receipt.json) |
| grid_tree_r0c1 | UNKNOWN | [grid_tree_r0c1.receipt.json](grid_tree_r0c1.receipt.json) |
| grid_tree_r1c0 | UNKNOWN | [grid_tree_r1c0.receipt.json](grid_tree_r1c0.receipt.json) |
| grid_tree_r1c1 | UNKNOWN | [grid_tree_r1c1.receipt.json](grid_tree_r1c1.receipt.json) |
| grid_tree_r2c0 | UNKNOWN | [grid_tree_r2c0.receipt.json](grid_tree_r2c0.receipt.json) |
| grid_tree_r2c1 | UNKNOWN | [grid_tree_r2c1.receipt.json](grid_tree_r2c1.receipt.json) |
| grid_tree_tables | UNKNOWN | [grid_tree_tables.receipt.json](grid_tree_tables.receipt.json) |
| grid_u_c0_h80 | INTERRUPTED | [grid_u_c0_h80.receipt.json](grid_u_c0_h80.receipt.json) |
| grid_u_c0_hop | INFEASIBLE | [grid_u_c0_hop.receipt.json](grid_u_c0_hop.receipt.json) |
| grid_u_cat3 | INFEASIBLE | [grid_u_cat3.receipt.json](grid_u_cat3.receipt.json) |
| grid_u_h2t2_auto | INTERRUPTED | [grid_u_h2t2_auto.receipt.json](grid_u_h2t2_auto.receipt.json) |
| ['direct'], round=False | INFEASIBLE | [geometry_00.json](geometry_00.json) |
| ['h1'], round=False | INFEASIBLE | [geometry_01.json](geometry_01.json) |
| ['h2'], round=False | INFEASIBLE | [geometry_02.json](geometry_02.json) |
| ['cat22'], round=False | INFEASIBLE | [geometry_03.json](geometry_03.json) |
| ['cat2'], round=False | OPTIMAL | [geometry_04.json](geometry_04.json) |
| ['cat3'], round=False | OPTIMAL | [geometry_05.json](geometry_05.json) |
| ['cat4'], round=False | OPTIMAL | [geometry_06.json](geometry_06.json) |
| ['free', 'cat2', 'cat2'], round=True | OPTIMAL | [geometry_07.json](geometry_07.json) |
| ['unitary', 'cat2', 'cat2'], round=True | INFEASIBLE | [geometry_08.json](geometry_08.json) |
| ['cat2', 'free', 'free'], round=True | OPTIMAL | [geometry_09.json](geometry_09.json) |
| ['free', 'cat3', 'cat3'], round=True | OPTIMAL | [geometry_10.json](geometry_10.json) |
| ['unitary', 'cat3', 'cat3'], round=True | INFEASIBLE | [geometry_11.json](geometry_11.json) |
| ['cat3', 'cat3', 'cat3'], round=True | UNKNOWN | [geometry_12.json](geometry_12.json) |
| ['unitary', 'cat4', 'cat4'], round=True | INFEASIBLE | [geometry_13.json](geometry_13.json) |
| ['cat2red'], round=False | INFEASIBLE | [geometry_14.json](geometry_14.json) |
| ['cat3red'], round=False | OPTIMAL | [geometry_15.json](geometry_15.json) |
| ['cat2pairred'], round=False | INFEASIBLE | [geometry_16.json](geometry_16.json) |

## Mechanisms and current conclusions

- The preparation frame is entirely classical. A's Z-check detector XORs its preparation result. B's final X-check detector XORs both B and C preparation results, since C's Z frame propagates backward through B→C. C's Z-readout checks have no preparation-frame terms. No conditional gate is used.
- An error absorbed into a measured preparation frame is harmless. An erroneous preparation record, or a phase error after the corresponding check, can instead cancel the final detector syndrome of a data Z error. Redundancy checks reject many of those record errors. They do not detect the X-hook errors that commute with the preparation X checks.
- Bare MB-A is worse than the separate unitary reference. Its target-ancilla Z faults propagate into multi-qubit Z on A, and interact with pre-round data Z faults. Flag brackets substantially reduce this cost; cats can introduce harmful preparation faults before any data coupling.
- MB-B and MB-C have nearly equal single-block costs. A fourth redundant stabilizer suppresses much of the cost associated with preparation records masking the data syndrome. B+C costs are not additive: joint experiments measure additional cross terms.
- Direct three-generator stars, and the original partial star encoders plus remaining bare measurements, fail the standalone grid embedding model. A 2+2 split at every two-member cat also fails. Allowing 1+3 cat splits makes a single block embeddable; this does not prove that an entire round fits.
- The five-CX partial tree `0→4, 1→5, 0→6, 1→6, 6→2` prepares the first two stabilizers from pivots 0 and 1; one measurement prepares the third. Unlike the original star hybrids, its support graph embeds. Its A version has an expensive initial phase fault: this is measured in `tree2_ABC_v22`, and keeps the unitary-A / MB-B+C version as the stronger grid candidate.
- Redundant four-check two-member cats are also INFEASIBLE for one stationary block, even allowing helper reuse and 1+3 splits ([geometry_14.json](geometry_14.json)). Three-member cats can reuse one path of three helper cells, but the two-block preparation adds long exposure and has matching weight-two X-hook pairs in B and C. Each such reset-fault pair contributes 5e-7 at second order. The physical bridge diagnostic verifies all detectors but fails acceptance by orders of magnitude; it is not a competitive placement.
- Both redundancy types were checked geometrically: a four-record dependency and a three-record dependency ([geometry_16.json](geometry_16.json)). Their two code-automorphism classes cover the 35 four-stabilizer sets: 7 and 28 respectively ([certificate](algebra_geometry_certificate.json)). The fixed-cell two-member-cat obstruction covers both classes; moving block qubits between checks is outside it.
- The explicit reused three-helper B+C recipe has seed-0 1e6 acceptance 0.498116–0.500172 over all 24 orders at R33, and 0.446484–0.447463 at R45. Every tested order misses the practical 0.505 floor before physical routing. The [hook-pair receipt](hook_pair.json) measures eight accepted fault pairs, conditional loss 0.5 each, contributing 4e-6 in total at second order.
- Tree-hybrid A exposes a specific dangerous phase hook: the initial Z fault on its shared parity wire becomes a two-qubit Z pattern. With the pre-round data Z idle at logical index 3, one measured pair alone contributes 5.28033e-6 in `tree2_ABC_v22`. This explains why the same partial tree is much less attractive for A than for B/C.
- On `v22_BC_redundant_201`, total=5.205006e-5. No preparation-ancilla noise: 5.142945e-5; no pre-round data idles: 3.468781e-5. The reductions overlap and must not be added. [Region-pair and ablation receipt](runs/v22_BC_redundant_201.analysis.json).
- A layout failure only closes that model. Other partial encoders, cat trees, internal gate orders, and wider movement models are not globally ruled out.

## Verified versus inferred / unfinished

Measured: every numerical circuit row, every retained MC mean, exact/accelerated evaluator agreement, Stim detector determinism, actual non-Clifford judge correctness, and the stated bounded solver statuses. Algebraically checked: the 28 generator bases, 35 redundant-check sets, and all 48 prefix embeddings grouped into six D4 classes.

Inference: the noise-competitive MB constructions could help if their preparation fits with sufficiently little exposure. No eligible full-grid winner was constructed. The only newly built physical diagnostic fails acceptance. Searches with block motion and independent code relabeling timed out without incumbents; their broad feasibility remains unresolved. Consequently no physical finalist qualified for the requested MAIN/spec/mc3.py ranking. The MC table is explicitly a grid-free comparison, not a substitute for that missing physical result.

## Every measured variant

The full machine-readable table is [results.csv](results.csv). `GF PASS/FAIL` refers to the explicitly relaxed grid-free judge. No 1e6-shot score is used for ranking. Regeneration: `.venv/bin/python work/lanes/MBP/mbp.py <name> --blocks <blocks> --kind <structure> --R <R> --pre <prefix> --order <order> --perm <perm> --procs N`.

| Variant / file stem | Structure | CX | R | c1 | 2nd | 3rd | Exact total | exp(-A1) | Check / MC |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| [matched_cat13_BC](matched_cat13_BC.qasm) · [JSON](matched_cat13_BC.json) · [receipt](matched_cat13_BC.result.json) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.832042e-05 | 1.280996e-05 | 5.113038e-05 | 0.53319 | GF PASS; acc 0.532852; MC mean 5.135197e-05 |
| [matched_ref](matched_ref.qasm) · [JSON](matched_ref.json) · [receipt](matched_ref.result.json) |  direct | 123 | 45 | 2.923587e-19 | 3.864948e-05 | 1.255789e-05 | 5.120737e-05 | 0.60321 | GF PASS; acc 0.602356; MC mean 5.207637e-05 |
| [physical_hybrid2t](physical_hybrid2t.qasm) · [JSON](physical_hybrid2t.json) · [receipt](physical_hybrid2t.result.json) |  routed_BC_hybrid2t | 498 | 391 | 1.543588e-18 | 0.003674718 | 0.2812367 | 0.2849114 | 0.00021 | FAIL; acc 0.001769; MC not run |
| `runs/sep_ABC_cat_012` (regenerate) | ABC cat | 147 | 33 | 3.182639e-19 | 0.0001402843 | 7.80114e-06 | 0.0001480854 | 0.60931 | GF PASS; acc 0.609646; MC not run |
| `runs/sep_ABC_cat_021` (regenerate) | ABC cat | 147 | 33 | 3.182639e-19 | 0.0001357448 | 7.721411e-06 | 0.0001434662 | 0.60931 | GF PASS; acc 0.609647; MC not run |
| `runs/sep_ABC_cat_102` (regenerate) | ABC cat | 147 | 33 | 3.182639e-19 | 0.0001329456 | 7.636503e-06 | 0.0001405821 | 0.60931 | GF PASS; acc 0.608864; MC not run |
| `runs/sep_ABC_cat_120` (regenerate) | ABC cat | 147 | 33 | 3.182639e-19 | 0.0001181686 | 8.032572e-06 | 0.0001262012 | 0.60339 | GF PASS; acc 0.603321; MC not run |
| `runs/sep_ABC_cat_201` (regenerate) | ABC cat | 147 | 33 | 3.182639e-19 | 0.0001153442 | 8.541137e-06 | 0.0001238853 | 0.60039 | GF PASS; acc 0.599750; MC not run |
| `runs/sep_ABC_cat_210` (regenerate) | ABC cat | 147 | 33 | 3.182639e-19 | 0.0001022485 | 7.552053e-06 | 0.0001098005 | 0.60702 | GF PASS; acc 0.606861; MC not run |
| `runs/sep_ABC_direct_012` (regenerate) | ABC direct | 138 | 33 | 3.182639e-19 | 4.278291e-05 | 7.586327e-06 | 5.036924e-05 | 0.60976 | GF PASS; acc 0.609702; MC not run |
| `runs/sep_ABC_direct_021` (regenerate) | ABC direct | 138 | 33 | 3.182639e-19 | 4.28577e-05 | 8.451532e-06 | 5.130923e-05 | 0.60250 | GF PASS; acc 0.602566; MC not run |
| `runs/sep_ABC_direct_102` (regenerate) | ABC direct | 138 | 33 | 3.182639e-19 | 5.036397e-05 | 8.875187e-06 | 5.923916e-05 | 0.59892 | GF PASS; acc 0.598674; MC not run |
| `runs/sep_ABC_direct_120` (regenerate) | ABC direct | 138 | 33 | 3.182639e-19 | 4.107542e-05 | 7.541051e-06 | 4.861647e-05 | 0.60792 | GF PASS; acc 0.607455; MC not run |
| `runs/sep_ABC_direct_201` (regenerate) | ABC direct | 138 | 33 | 3.182639e-19 | 4.043723e-05 | 7.556175e-06 | 4.799341e-05 | 0.60792 | GF PASS; acc 0.607457; MC not run |
| `runs/sep_ABC_direct_210` (regenerate) | ABC direct | 138 | 33 | 3.182639e-19 | 4.003415e-05 | 7.456187e-06 | 4.749034e-05 | 0.60793 | GF PASS; acc 0.607781; MC not run |
| `runs/sep_ABC_flag_012` (regenerate) | ABC flag | 156 | 33 | 3.182639e-19 | 3.179986e-05 | 9.296093e-06 | 4.109595e-05 | 0.54998 | GF PASS; acc 0.549614; MC not run |
| `runs/sep_ABC_flag_021` (regenerate) | ABC flag | 156 | 33 | 3.182639e-19 | 3.155252e-05 | 1.020789e-05 | 4.17604e-05 | 0.54182 | GF PASS; acc 0.542134; MC not run |
| `runs/sep_ABC_flag_102` (regenerate) | ABC flag | 156 | 33 | 3.182639e-19 | 3.248749e-05 | 1.064232e-05 | 4.31298e-05 | 0.53700 | GF PASS; acc 0.536911; MC not run |
| `runs/sep_ABC_flag_120` (regenerate) | ABC flag | 156 | 33 | 3.182639e-19 | 3.218233e-05 | 9.315965e-06 | 4.149829e-05 | 0.54833 | GF PASS; acc 0.548675; MC not run |
| `runs/sep_ABC_flag_201` (regenerate) | ABC flag | 156 | 33 | 3.182639e-19 | 3.146848e-05 | 9.329556e-06 | 4.079803e-05 | 0.54833 | GF PASS; acc 0.548658; MC not run |
| `runs/sep_ABC_flag_210` (regenerate) | ABC flag | 156 | 33 | 3.182639e-19 | 3.173134e-05 | 9.24311e-06 | 4.097445e-05 | 0.54833 | GF PASS; acc 0.548441; MC not run |
| `runs/sep_ABC_flag_redundant_012` (regenerate) | ABC flag,redundant,redundant | 152 | 33 | 3.182639e-19 | 3.191097e-05 | 5.524758e-06 | 3.743573e-05 | 0.57647 | GF PASS; acc 0.576288; MC not run |
| `runs/sep_ABC_flag_redundant_021` (regenerate) | ABC flag,redundant,redundant | 152 | 33 | 3.182639e-19 | 3.166363e-05 | 5.839565e-06 | 3.750319e-05 | 0.56904 | GF PASS; acc 0.568669; MC not run |
| `runs/sep_ABC_flag_redundant_102` (regenerate) | ABC flag,redundant,redundant | 152 | 33 | 3.182639e-19 | 3.279638e-05 | 6.135024e-06 | 3.89314e-05 | 0.56509 | GF PASS; acc 0.564508; MC not run |
| `runs/sep_ABC_flag_redundant_120` (regenerate) | ABC flag,redundant,redundant | 152 | 33 | 3.182639e-19 | 3.232011e-05 | 5.522358e-06 | 3.784246e-05 | 0.57474 | GF PASS; acc 0.574667; MC not run |
| `runs/sep_ABC_flag_redundant_201` (regenerate) | ABC flag,redundant,redundant | 152 | 33 | 3.182639e-19 | 3.158848e-05 | 5.505e-06 | 3.709348e-05 | 0.57474 | GF PASS; acc 0.574503; MC not run |
| `runs/sep_ABC_flag_redundant_210` (regenerate) | ABC flag,redundant,redundant | 152 | 33 | 3.182639e-19 | 3.186912e-05 | 5.499529e-06 | 3.736865e-05 | 0.57474 | GF PASS; acc 0.574128; MC not run |
| `runs/sep_ABC_hybrid1_012` (regenerate) | ABC hybrid1 | 135 | 33 | 3.182639e-19 | 4.03715e-05 | 9.007852e-06 | 4.937935e-05 | 0.59735 | GF PASS; acc 0.596951; MC not run |
| `runs/sep_ABC_hybrid1_021` (regenerate) | ABC hybrid1 | 135 | 33 | 3.182639e-19 | 4.006354e-05 | 8.949399e-06 | 4.901294e-05 | 0.59735 | GF PASS; acc 0.597152; MC not run |
| `runs/sep_ABC_hybrid1_102` (regenerate) | ABC hybrid1 | 135 | 33 | 3.182639e-19 | 4.03715e-05 | 9.007852e-06 | 4.937935e-05 | 0.59735 | GF PASS; acc 0.596951; MC not run |
| `runs/sep_ABC_hybrid1_120` (regenerate) | ABC hybrid1 | 135 | 33 | 3.182639e-19 | 4.03715e-05 | 9.007852e-06 | 4.937935e-05 | 0.59735 | GF PASS; acc 0.596951; MC not run |
| `runs/sep_ABC_hybrid1_201` (regenerate) | ABC hybrid1 | 135 | 33 | 3.182639e-19 | 4.006354e-05 | 8.949399e-06 | 4.901294e-05 | 0.59735 | GF PASS; acc 0.597152; MC not run |
| `runs/sep_ABC_hybrid1_210` (regenerate) | ABC hybrid1 | 135 | 33 | 3.182639e-19 | 4.006354e-05 | 8.949399e-06 | 4.901294e-05 | 0.59735 | GF PASS; acc 0.597152; MC not run |
| `runs/sep_ABC_hybrid2_012` (regenerate) | ABC hybrid2 | 132 | 33 | 3.182639e-19 | 3.723288e-05 | 7.204151e-06 | 4.443703e-05 | 0.60734 | GF PASS; acc 0.606994; MC not run |
| `runs/sep_ABC_hybrid2_021` (regenerate) | ABC hybrid2 | 132 | 33 | 3.182639e-19 | 3.723288e-05 | 7.204151e-06 | 4.443703e-05 | 0.60734 | GF PASS; acc 0.606994; MC not run |
| `runs/sep_ABC_hybrid2_102` (regenerate) | ABC hybrid2 | 132 | 33 | 3.182639e-19 | 3.723288e-05 | 7.204151e-06 | 4.443703e-05 | 0.60734 | GF PASS; acc 0.606994; MC not run |
| `runs/sep_ABC_hybrid2_120` (regenerate) | ABC hybrid2 | 132 | 33 | 3.182639e-19 | 3.723288e-05 | 7.204151e-06 | 4.443703e-05 | 0.60734 | GF PASS; acc 0.606994; MC not run |
| `runs/sep_ABC_hybrid2_201` (regenerate) | ABC hybrid2 | 132 | 33 | 3.182639e-19 | 3.723288e-05 | 7.204151e-06 | 4.443703e-05 | 0.60734 | GF PASS; acc 0.606994; MC not run |
| `runs/sep_ABC_hybrid2_210` (regenerate) | ABC hybrid2 | 132 | 33 | 3.182639e-19 | 3.723288e-05 | 7.204151e-06 | 4.443703e-05 | 0.60734 | GF PASS; acc 0.606994; MC not run |
| `runs/sep_ABC_hybrid2t_012` (regenerate) | ABC hybrid2t | 129 | 33 | 3.182639e-19 | 5.200191e-05 | 8.151473e-06 | 6.015338e-05 | 0.60015 | GF PASS; acc 0.599893; MC not run |
| `runs/sep_ABC_redundant_012` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.693191e-05 | 4.912865e-06 | 4.184478e-05 | 0.59018 | GF PASS; acc 0.590034; MC not run |
| `runs/sep_ABC_redundant_0132` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.951974e-05 | 6.153781e-06 | 4.567352e-05 | 0.57960 | GF PASS; acc 0.578624; MC not run |
| `runs/sep_ABC_redundant_021` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.689113e-05 | 5.208515e-06 | 4.209964e-05 | 0.58315 | GF PASS; acc 0.582396; MC not run |
| `runs/sep_ABC_redundant_0231` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 4.077193e-05 | 5.56658e-06 | 4.633851e-05 | 0.58130 | GF PASS; acc 0.580857; MC not run |
| `runs/sep_ABC_redundant_0312` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.953102e-05 | 5.661977e-06 | 4.5193e-05 | 0.58645 | GF PASS; acc 0.586354; MC not run |
| `runs/sep_ABC_redundant_0321` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.963632e-05 | 6.204429e-06 | 4.584075e-05 | 0.57775 | GF PASS; acc 0.577022; MC not run |
| `runs/sep_ABC_redundant_102` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 4.058169e-05 | 5.493144e-06 | 4.607483e-05 | 0.57968 | GF PASS; acc 0.579509; MC not run |
| `runs/sep_ABC_redundant_1032` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.9679e-05 | 6.161976e-06 | 4.584098e-05 | 0.57960 | GF PASS; acc 0.578726; MC not run |
| `runs/sep_ABC_redundant_120` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.662455e-05 | 4.845995e-06 | 4.147054e-05 | 0.58841 | GF PASS; acc 0.588057; MC not run |
| `runs/sep_ABC_redundant_1230` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.671845e-05 | 4.860203e-06 | 4.157866e-05 | 0.58841 | GF PASS; acc 0.588220; MC not run |
| `runs/sep_ABC_redundant_1302` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.898907e-05 | 5.738886e-06 | 4.472795e-05 | 0.58482 | GF PASS; acc 0.584103; MC not run |
| `runs/sep_ABC_redundant_1320` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.854711e-05 | 5.83937e-06 | 4.438648e-05 | 0.57784 | GF PASS; acc 0.577892; MC not run |
| `runs/sep_ABC_redundant_201` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.650944e-05 | 4.852433e-06 | 4.136187e-05 | 0.58841 | GF PASS; acc 0.587750; MC not run |
| `runs/sep_ABC_redundant_2031` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 4.052307e-05 | 5.388909e-06 | 4.591198e-05 | 0.58304 | GF PASS; acc 0.582431; MC not run |
| `runs/sep_ABC_redundant_210` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.647362e-05 | 4.832653e-06 | 4.130627e-05 | 0.58842 | GF PASS; acc 0.587847; MC not run |
| `runs/sep_ABC_redundant_2130` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.656752e-05 | 4.846381e-06 | 4.14139e-05 | 0.58841 | GF PASS; acc 0.588528; MC not run |
| `runs/sep_ABC_redundant_2301` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.73139e-05 | 4.942794e-06 | 4.225669e-05 | 0.59007 | GF PASS; acc 0.589732; MC not run |
| `runs/sep_ABC_redundant_2310` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.98863e-05 | 5.148712e-06 | 4.503501e-05 | 0.58478 | GF PASS; acc 0.584268; MC not run |
| `runs/sep_ABC_redundant_3012` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.890932e-05 | 5.117762e-06 | 4.402709e-05 | 0.59530 | GF PASS; acc 0.594740; MC not run |
| `runs/sep_ABC_redundant_3021` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.894862e-05 | 5.766857e-06 | 4.471548e-05 | 0.58295 | GF PASS; acc 0.582712; MC not run |
| `runs/sep_ABC_redundant_3102` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 5.037176e-05 | 6.306301e-06 | 5.667806e-05 | 0.57775 | GF PASS; acc 0.577580; MC not run |
| `runs/sep_ABC_redundant_3120` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.858931e-05 | 5.333872e-06 | 4.392318e-05 | 0.58644 | GF PASS; acc 0.586088; MC not run |
| `runs/sep_ABC_redundant_3201` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.838394e-05 | 5.665191e-06 | 4.404913e-05 | 0.57945 | GF PASS; acc 0.578918; MC not run |
| `runs/sep_ABC_redundant_3210` (regenerate) | ABC redundant | 150 | 33 | 3.182639e-19 | 3.834627e-05 | 5.638933e-06 | 4.39852e-05 | 0.57946 | GF PASS; acc 0.578998; MC not run |
| `runs/sep_ABC_seq_012` (regenerate) | ABC seq | 138 | 33 | 3.182639e-19 | 5.31326e-05 | 2.301211e-05 | 7.614471e-05 | 0.52852 | GF PASS; acc 0.528154; MC not run |
| `runs/sep_ABC_seq_021` (regenerate) | ABC seq | 138 | 33 | 3.182639e-19 | 4.949048e-05 | 2.249398e-05 | 7.198446e-05 | 0.52853 | GF PASS; acc 0.528560; MC not run |
| `runs/sep_ABC_seq_102` (regenerate) | ABC seq | 138 | 33 | 3.182639e-19 | 5.277118e-05 | 2.258964e-05 | 7.536082e-05 | 0.52853 | GF PASS; acc 0.529566; MC not run |
| `runs/sep_ABC_seq_120` (regenerate) | ABC seq | 138 | 33 | 3.182639e-19 | 4.705468e-05 | 2.215172e-05 | 6.92064e-05 | 0.52695 | GF PASS; acc 0.527314; MC not run |
| `runs/sep_ABC_seq_201` (regenerate) | ABC seq | 138 | 33 | 3.182639e-19 | 4.361799e-05 | 2.20734e-05 | 6.569139e-05 | 0.52695 | GF PASS; acc 0.526814; MC not run |
| `runs/sep_ABC_seq_210` (regenerate) | ABC seq | 138 | 33 | 3.182639e-19 | 4.226023e-05 | 2.159576e-05 | 6.385598e-05 | 0.52696 | GF PASS; acc 0.527082; MC not run |
| `runs/sep_AB_cat_012` (regenerate) | AB cat | 141 | 33 | 3.182639e-19 | 0.0001018807 | 5.956589e-06 | 0.0001078372 | 0.62979 | GF PASS; acc 0.629573; MC not run |
| `runs/sep_AB_cat_021` (regenerate) | AB cat | 141 | 33 | 3.182639e-19 | 9.94723e-05 | 5.908978e-06 | 0.0001053813 | 0.62979 | GF PASS; acc 0.629579; MC not run |
| `runs/sep_AB_cat_102` (regenerate) | AB cat | 141 | 33 | 3.182639e-19 | 9.825342e-05 | 5.857014e-06 | 0.0001041104 | 0.62979 | GF PASS; acc 0.629136; MC not run |
| `runs/sep_AB_cat_120` (regenerate) | AB cat | 141 | 33 | 3.182639e-19 | 9.037796e-05 | 6.090011e-06 | 9.646797e-05 | 0.62570 | GF PASS; acc 0.624769; MC not run |
| `runs/sep_AB_cat_201` (regenerate) | AB cat | 141 | 33 | 3.182639e-19 | 8.828038e-05 | 6.391978e-06 | 9.467236e-05 | 0.62363 | GF PASS; acc 0.623503; MC not run |
| `runs/sep_AB_cat_210` (regenerate) | AB cat | 141 | 33 | 3.182639e-19 | 8.099177e-05 | 5.80095e-06 | 8.679272e-05 | 0.62821 | GF PASS; acc 0.627695; MC not run |
| `runs/sep_AB_direct_012` (regenerate) | AB direct | 135 | 33 | 3.182639e-19 | 4.010661e-05 | 5.993092e-06 | 4.60997e-05 | 0.63010 | GF PASS; acc 0.630011; MC not run |
| `runs/sep_AB_direct_021` (regenerate) | AB direct | 135 | 33 | 3.182639e-19 | 4.004418e-05 | 6.580147e-06 | 4.662433e-05 | 0.62509 | GF PASS; acc 0.624718; MC not run |
| `runs/sep_AB_direct_102` (regenerate) | AB direct | 135 | 33 | 3.182639e-19 | 4.573756e-05 | 6.871017e-06 | 5.260858e-05 | 0.62260 | GF PASS; acc 0.621430; MC not run |
| `runs/sep_AB_direct_120` (regenerate) | AB direct | 135 | 33 | 3.182639e-19 | 3.916211e-05 | 5.991769e-06 | 4.515388e-05 | 0.62883 | GF PASS; acc 0.628135; MC not run |
| `runs/sep_AB_direct_201` (regenerate) | AB direct | 135 | 33 | 3.182639e-19 | 3.846176e-05 | 5.993518e-06 | 4.445528e-05 | 0.62883 | GF PASS; acc 0.628125; MC not run |
| `runs/sep_AB_direct_210` (regenerate) | AB direct | 135 | 33 | 3.182639e-19 | 3.835599e-05 | 5.93658e-06 | 4.429256e-05 | 0.62883 | GF PASS; acc 0.628785; MC not run |
| `runs/sep_AB_flag_012` (regenerate) | AB flag | 147 | 33 | 3.182639e-19 | 3.179986e-05 | 7.020921e-06 | 3.882078e-05 | 0.58821 | GF PASS; acc 0.588299; MC not run |
| `runs/sep_AB_flag_021` (regenerate) | AB flag | 147 | 33 | 3.182639e-19 | 3.155252e-05 | 7.606539e-06 | 3.915905e-05 | 0.58238 | GF PASS; acc 0.581813; MC not run |
| `runs/sep_AB_flag_102` (regenerate) | AB flag | 147 | 33 | 3.182639e-19 | 3.248749e-05 | 7.905838e-06 | 4.039332e-05 | 0.57892 | GF PASS; acc 0.578920; MC not run |
| `runs/sep_AB_flag_120` (regenerate) | AB flag | 147 | 33 | 3.182639e-19 | 3.218233e-05 | 7.058466e-06 | 3.924079e-05 | 0.58703 | GF PASS; acc 0.587283; MC not run |
| `runs/sep_AB_flag_201` (regenerate) | AB flag | 147 | 33 | 3.182639e-19 | 3.146848e-05 | 7.057197e-06 | 3.852567e-05 | 0.58703 | GF PASS; acc 0.587276; MC not run |
| `runs/sep_AB_flag_210` (regenerate) | AB flag | 147 | 33 | 3.182639e-19 | 3.173134e-05 | 7.010581e-06 | 3.874192e-05 | 0.58703 | GF PASS; acc 0.586725; MC not run |
| `runs/sep_AB_hybrid1_012` (regenerate) | AB hybrid1 | 133 | 33 | 3.182639e-19 | 3.841517e-05 | 7.037372e-06 | 4.545254e-05 | 0.62152 | GF PASS; acc 0.621223; MC not run |
| `runs/sep_AB_hybrid1_021` (regenerate) | AB hybrid1 | 133 | 33 | 3.182639e-19 | 3.811181e-05 | 7.003455e-06 | 4.511526e-05 | 0.62152 | GF PASS; acc 0.620340; MC not run |
| `runs/sep_AB_hybrid1_102` (regenerate) | AB hybrid1 | 133 | 33 | 3.182639e-19 | 3.841517e-05 | 7.037372e-06 | 4.545254e-05 | 0.62152 | GF PASS; acc 0.621223; MC not run |
| `runs/sep_AB_hybrid1_120` (regenerate) | AB hybrid1 | 133 | 33 | 3.182639e-19 | 3.841517e-05 | 7.037372e-06 | 4.545254e-05 | 0.62152 | GF PASS; acc 0.621223; MC not run |
| `runs/sep_AB_hybrid1_201` (regenerate) | AB hybrid1 | 133 | 33 | 3.182639e-19 | 3.811181e-05 | 7.003455e-06 | 4.511526e-05 | 0.62152 | GF PASS; acc 0.620340; MC not run |
| `runs/sep_AB_hybrid1_210` (regenerate) | AB hybrid1 | 133 | 33 | 3.182639e-19 | 3.811181e-05 | 7.003455e-06 | 4.511526e-05 | 0.62152 | GF PASS; acc 0.620340; MC not run |
| `runs/sep_AB_hybrid2_012` (regenerate) | AB hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.821339e-06 | 4.22066e-05 | 0.62843 | GF PASS; acc 0.628192; MC not run |
| `runs/sep_AB_hybrid2_021` (regenerate) | AB hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.821339e-06 | 4.22066e-05 | 0.62843 | GF PASS; acc 0.628192; MC not run |
| `runs/sep_AB_hybrid2_102` (regenerate) | AB hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.821339e-06 | 4.22066e-05 | 0.62843 | GF PASS; acc 0.628192; MC not run |
| `runs/sep_AB_hybrid2_120` (regenerate) | AB hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.821339e-06 | 4.22066e-05 | 0.62843 | GF PASS; acc 0.628192; MC not run |
| `runs/sep_AB_hybrid2_201` (regenerate) | AB hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.821339e-06 | 4.22066e-05 | 0.62843 | GF PASS; acc 0.628192; MC not run |
| `runs/sep_AB_hybrid2_210` (regenerate) | AB hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.821339e-06 | 4.22066e-05 | 0.62843 | GF PASS; acc 0.628192; MC not run |
| `runs/sep_AB_hybrid2t_012` (regenerate) | AB hybrid2t | 129 | 33 | 3.182639e-19 | 4.794706e-05 | 6.420592e-06 | 5.436765e-05 | 0.62346 | GF PASS; acc 0.622791; MC not run |
| `runs/sep_AB_redundant_012` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.678708e-05 | 4.493552e-06 | 4.128063e-05 | 0.61654 | GF PASS; acc 0.616200; MC not run |
| `runs/sep_AB_redundant_0132` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.866329e-05 | 5.358008e-06 | 4.40213e-05 | 0.60914 | GF PASS; acc 0.608294; MC not run |
| `runs/sep_AB_redundant_021` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.682606e-05 | 4.757895e-06 | 4.158395e-05 | 0.61163 | GF PASS; acc 0.610401; MC not run |
| `runs/sep_AB_redundant_0231` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 4.002668e-05 | 4.972387e-06 | 4.499907e-05 | 0.61034 | GF PASS; acc 0.609678; MC not run |
| `runs/sep_AB_redundant_0312` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.869602e-05 | 4.978529e-06 | 4.367455e-05 | 0.61394 | GF PASS; acc 0.613299; MC not run |
| `runs/sep_AB_redundant_0321` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.886819e-05 | 5.39862e-06 | 4.426681e-05 | 0.60785 | GF PASS; acc 0.607899; MC not run |
| `runs/sep_AB_redundant_102` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 4.024924e-05 | 4.95581e-06 | 4.520505e-05 | 0.60920 | GF PASS; acc 0.608763; MC not run |
| `runs/sep_AB_redundant_1032` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.88005e-05 | 5.364118e-06 | 4.416462e-05 | 0.60915 | GF PASS; acc 0.608919; MC not run |
| `runs/sep_AB_redundant_120` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.65041e-05 | 4.461802e-06 | 4.09659e-05 | 0.61530 | GF PASS; acc 0.614095; MC not run |
| `runs/sep_AB_redundant_1230` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.659801e-05 | 4.472334e-06 | 4.107034e-05 | 0.61530 | GF PASS; acc 0.614944; MC not run |
| `runs/sep_AB_redundant_1302` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.824284e-05 | 5.046815e-06 | 4.328965e-05 | 0.61280 | GF PASS; acc 0.612208; MC not run |
| `runs/sep_AB_redundant_1320` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.820542e-05 | 5.192698e-06 | 4.339812e-05 | 0.60791 | GF PASS; acc 0.606804; MC not run |
| `runs/sep_AB_redundant_201` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.642001e-05 | 4.467229e-06 | 4.088724e-05 | 0.61530 | GF PASS; acc 0.614102; MC not run |
| `runs/sep_AB_redundant_2031` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.973587e-05 | 4.835583e-06 | 4.457145e-05 | 0.61155 | GF PASS; acc 0.610980; MC not run |
| `runs/sep_AB_redundant_210` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.635317e-05 | 4.449945e-06 | 4.080311e-05 | 0.61531 | GF PASS; acc 0.614402; MC not run |
| `runs/sep_AB_redundant_2130` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.644707e-05 | 4.459934e-06 | 4.090701e-05 | 0.61530 | GF PASS; acc 0.614285; MC not run |
| `runs/sep_AB_redundant_2301` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.700314e-05 | 4.495828e-06 | 4.149897e-05 | 0.61646 | GF PASS; acc 0.616468; MC not run |
| `runs/sep_AB_redundant_2310` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.931551e-05 | 4.670588e-06 | 4.39861e-05 | 0.61277 | GF PASS; acc 0.611958; MC not run |
| `runs/sep_AB_redundant_3012` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.818455e-05 | 4.552275e-06 | 4.273682e-05 | 0.62010 | GF PASS; acc 0.618745; MC not run |
| `runs/sep_AB_redundant_3021` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.829057e-05 | 5.073027e-06 | 4.33636e-05 | 0.61149 | GF PASS; acc 0.610855; MC not run |
| `runs/sep_AB_redundant_3102` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 4.781698e-05 | 5.428992e-06 | 5.324598e-05 | 0.60785 | GF PASS; acc 0.606795; MC not run |
| `runs/sep_AB_redundant_3120` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.822513e-05 | 4.782213e-06 | 4.300734e-05 | 0.61393 | GF PASS; acc 0.614310; MC not run |
| `runs/sep_AB_redundant_3201` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.801549e-05 | 5.049357e-06 | 4.306485e-05 | 0.60904 | GF PASS; acc 0.608096; MC not run |
| `runs/sep_AB_redundant_3210` (regenerate) | AB redundant | 143 | 33 | 3.182639e-19 | 3.806179e-05 | 5.038918e-06 | 4.310071e-05 | 0.60905 | GF PASS; acc 0.608298; MC not run |
| `runs/sep_AB_seq_012` (regenerate) | AB seq | 135 | 33 | 3.182639e-19 | 4.688637e-05 | 1.62488e-05 | 6.313517e-05 | 0.57281 | GF PASS; acc 0.572160; MC not run |
| `runs/sep_AB_seq_021` (regenerate) | AB seq | 135 | 33 | 3.182639e-19 | 4.425712e-05 | 1.592172e-05 | 6.017884e-05 | 0.57281 | GF PASS; acc 0.572708; MC not run |
| `runs/sep_AB_seq_102` (regenerate) | AB seq | 135 | 33 | 3.182639e-19 | 4.757524e-05 | 1.602155e-05 | 6.359678e-05 | 0.57281 | GF PASS; acc 0.572184; MC not run |
| `runs/sep_AB_seq_120` (regenerate) | AB seq | 135 | 33 | 3.182639e-19 | 4.399631e-05 | 1.578723e-05 | 5.978354e-05 | 0.57167 | GF PASS; acc 0.571035; MC not run |
| `runs/sep_AB_seq_201` (regenerate) | AB seq | 135 | 33 | 3.182639e-19 | 4.058383e-05 | 1.567354e-05 | 5.625736e-05 | 0.57167 | GF PASS; acc 0.571655; MC not run |
| `runs/sep_AB_seq_210` (regenerate) | AB seq | 135 | 33 | 3.182639e-19 | 4.022916e-05 | 1.541138e-05 | 5.564054e-05 | 0.57168 | GF PASS; acc 0.571155; MC not run |
| `runs/sep_AC_cat_012` (regenerate) | AC cat | 141 | 33 | 3.182639e-19 | 0.0001018807 | 5.906186e-06 | 0.0001077868 | 0.62979 | GF PASS; acc 0.628872; MC not run |
| `runs/sep_AC_cat_021` (regenerate) | AC cat | 141 | 33 | 3.182639e-19 | 9.94723e-05 | 5.858498e-06 | 0.0001053308 | 0.62979 | GF PASS; acc 0.628857; MC not run |
| `runs/sep_AC_cat_102` (regenerate) | AC cat | 141 | 33 | 3.182639e-19 | 9.825342e-05 | 5.806529e-06 | 0.00010406 | 0.62979 | GF PASS; acc 0.629375; MC not run |
| `runs/sep_AC_cat_120` (regenerate) | AC cat | 141 | 33 | 3.182639e-19 | 9.037796e-05 | 6.037738e-06 | 9.64157e-05 | 0.62570 | GF PASS; acc 0.625219; MC not run |
| `runs/sep_AC_cat_201` (regenerate) | AC cat | 141 | 33 | 3.182639e-19 | 8.828038e-05 | 6.3393e-06 | 9.461968e-05 | 0.62363 | GF PASS; acc 0.622828; MC not run |
| `runs/sep_AC_cat_210` (regenerate) | AC cat | 141 | 33 | 3.182639e-19 | 8.099177e-05 | 5.752577e-06 | 8.674435e-05 | 0.62821 | GF PASS; acc 0.627535; MC not run |
| `runs/sep_AC_direct_012` (regenerate) | AC direct | 135 | 33 | 3.182639e-19 | 4.010661e-05 | 5.956305e-06 | 4.606292e-05 | 0.63010 | GF PASS; acc 0.629533; MC not run |
| `runs/sep_AC_direct_021` (regenerate) | AC direct | 135 | 33 | 3.182639e-19 | 4.004418e-05 | 6.538749e-06 | 4.658293e-05 | 0.62509 | GF PASS; acc 0.624639; MC not run |
| `runs/sep_AC_direct_102` (regenerate) | AC direct | 135 | 33 | 3.182639e-19 | 4.573756e-05 | 6.82665e-06 | 5.256421e-05 | 0.62260 | GF PASS; acc 0.622163; MC not run |
| `runs/sep_AC_direct_120` (regenerate) | AC direct | 135 | 33 | 3.182639e-19 | 3.916211e-05 | 5.953692e-06 | 4.51158e-05 | 0.62883 | GF PASS; acc 0.627633; MC not run |
| `runs/sep_AC_direct_201` (regenerate) | AC direct | 135 | 33 | 3.182639e-19 | 3.846176e-05 | 5.95534e-06 | 4.44171e-05 | 0.62883 | GF PASS; acc 0.627625; MC not run |
| `runs/sep_AC_direct_210` (regenerate) | AC direct | 135 | 33 | 3.182639e-19 | 3.835599e-05 | 5.898449e-06 | 4.425443e-05 | 0.62883 | GF PASS; acc 0.628010; MC not run |
| `runs/sep_AC_flag_012` (regenerate) | AC flag | 147 | 33 | 3.182639e-19 | 3.179986e-05 | 6.984474e-06 | 3.878434e-05 | 0.58821 | GF PASS; acc 0.587556; MC not run |
| `runs/sep_AC_flag_021` (regenerate) | AC flag | 147 | 33 | 3.182639e-19 | 3.155252e-05 | 7.566659e-06 | 3.911917e-05 | 0.58238 | GF PASS; acc 0.582240; MC not run |
| `runs/sep_AC_flag_102` (regenerate) | AC flag | 147 | 33 | 3.182639e-19 | 3.248749e-05 | 7.864899e-06 | 4.035239e-05 | 0.57892 | GF PASS; acc 0.578915; MC not run |
| `runs/sep_AC_flag_120` (regenerate) | AC flag | 147 | 33 | 3.182639e-19 | 3.218233e-05 | 7.020717e-06 | 3.920305e-05 | 0.58703 | GF PASS; acc 0.586971; MC not run |
| `runs/sep_AC_flag_201` (regenerate) | AC flag | 147 | 33 | 3.182639e-19 | 3.146848e-05 | 7.019393e-06 | 3.848787e-05 | 0.58703 | GF PASS; acc 0.586965; MC not run |
| `runs/sep_AC_flag_210` (regenerate) | AC flag | 147 | 33 | 3.182639e-19 | 3.173134e-05 | 6.972801e-06 | 3.870414e-05 | 0.58703 | GF PASS; acc 0.586740; MC not run |
| `runs/sep_AC_hybrid1_012` (regenerate) | AC hybrid1 | 133 | 33 | 3.182639e-19 | 3.841517e-05 | 6.987827e-06 | 4.5403e-05 | 0.62152 | GF PASS; acc 0.621207; MC not run |
| `runs/sep_AC_hybrid1_021` (regenerate) | AC hybrid1 | 133 | 33 | 3.182639e-19 | 3.811181e-05 | 6.953901e-06 | 4.506571e-05 | 0.62152 | GF PASS; acc 0.620836; MC not run |
| `runs/sep_AC_hybrid1_102` (regenerate) | AC hybrid1 | 133 | 33 | 3.182639e-19 | 3.841517e-05 | 6.987827e-06 | 4.5403e-05 | 0.62152 | GF PASS; acc 0.621207; MC not run |
| `runs/sep_AC_hybrid1_120` (regenerate) | AC hybrid1 | 133 | 33 | 3.182639e-19 | 3.841517e-05 | 6.987827e-06 | 4.5403e-05 | 0.62152 | GF PASS; acc 0.621207; MC not run |
| `runs/sep_AC_hybrid1_201` (regenerate) | AC hybrid1 | 133 | 33 | 3.182639e-19 | 3.811181e-05 | 6.953901e-06 | 4.506571e-05 | 0.62152 | GF PASS; acc 0.620836; MC not run |
| `runs/sep_AC_hybrid1_210` (regenerate) | AC hybrid1 | 133 | 33 | 3.182639e-19 | 3.811181e-05 | 6.953901e-06 | 4.506571e-05 | 0.62152 | GF PASS; acc 0.620836; MC not run |
| `runs/sep_AC_hybrid2_012` (regenerate) | AC hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.782987e-06 | 4.216825e-05 | 0.62843 | GF PASS; acc 0.627557; MC not run |
| `runs/sep_AC_hybrid2_021` (regenerate) | AC hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.782987e-06 | 4.216825e-05 | 0.62843 | GF PASS; acc 0.627557; MC not run |
| `runs/sep_AC_hybrid2_102` (regenerate) | AC hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.782987e-06 | 4.216825e-05 | 0.62843 | GF PASS; acc 0.627557; MC not run |
| `runs/sep_AC_hybrid2_120` (regenerate) | AC hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.782987e-06 | 4.216825e-05 | 0.62843 | GF PASS; acc 0.627557; MC not run |
| `runs/sep_AC_hybrid2_201` (regenerate) | AC hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.782987e-06 | 4.216825e-05 | 0.62843 | GF PASS; acc 0.627557; MC not run |
| `runs/sep_AC_hybrid2_210` (regenerate) | AC hybrid2 | 131 | 33 | 3.182639e-19 | 3.638526e-05 | 5.782987e-06 | 4.216825e-05 | 0.62843 | GF PASS; acc 0.627557; MC not run |
| `runs/sep_AC_hybrid2t_012` (regenerate) | AC hybrid2t | 129 | 33 | 3.182639e-19 | 4.794706e-05 | 6.375278e-06 | 5.432233e-05 | 0.62346 | GF PASS; acc 0.622650; MC not run |
| `runs/sep_AC_redundant_012` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.678708e-05 | 4.45126e-06 | 4.123834e-05 | 0.61654 | GF PASS; acc 0.616088; MC not run |
| `runs/sep_AC_redundant_0132` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.866329e-05 | 5.308974e-06 | 4.397226e-05 | 0.60914 | GF PASS; acc 0.609031; MC not run |
| `runs/sep_AC_redundant_021` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.682606e-05 | 4.711075e-06 | 4.153713e-05 | 0.61163 | GF PASS; acc 0.611634; MC not run |
| `runs/sep_AC_redundant_0231` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 4.002668e-05 | 4.923914e-06 | 4.49506e-05 | 0.61034 | GF PASS; acc 0.609608; MC not run |
| `runs/sep_AC_redundant_0312` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.869602e-05 | 4.933731e-06 | 4.362975e-05 | 0.61394 | GF PASS; acc 0.613472; MC not run |
| `runs/sep_AC_redundant_0321` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.886819e-05 | 5.348195e-06 | 4.421639e-05 | 0.60785 | GF PASS; acc 0.607007; MC not run |
| `runs/sep_AC_redundant_102` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 4.024924e-05 | 4.906103e-06 | 4.515534e-05 | 0.60920 | GF PASS; acc 0.608775; MC not run |
| `runs/sep_AC_redundant_1032` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.88005e-05 | 5.315036e-06 | 4.411554e-05 | 0.60915 | GF PASS; acc 0.608259; MC not run |
| `runs/sep_AC_redundant_120` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.65041e-05 | 4.418392e-06 | 4.092249e-05 | 0.61530 | GF PASS; acc 0.615191; MC not run |
| `runs/sep_AC_redundant_1230` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.659801e-05 | 4.428955e-06 | 4.102696e-05 | 0.61530 | GF PASS; acc 0.614502; MC not run |
| `runs/sep_AC_redundant_1302` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.824284e-05 | 5.001128e-06 | 4.324396e-05 | 0.61280 | GF PASS; acc 0.612740; MC not run |
| `runs/sep_AC_redundant_1320` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.820542e-05 | 5.142425e-06 | 4.334784e-05 | 0.60791 | GF PASS; acc 0.608208; MC not run |
| `runs/sep_AC_redundant_201` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.642001e-05 | 4.423741e-06 | 4.084376e-05 | 0.61530 | GF PASS; acc 0.614744; MC not run |
| `runs/sep_AC_redundant_2031` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.973587e-05 | 4.788155e-06 | 4.452402e-05 | 0.61155 | GF PASS; acc 0.611093; MC not run |
| `runs/sep_AC_redundant_210` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.635317e-05 | 4.406516e-06 | 4.075969e-05 | 0.61531 | GF PASS; acc 0.614643; MC not run |
| `runs/sep_AC_redundant_2130` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.644707e-05 | 4.416536e-06 | 4.086361e-05 | 0.61530 | GF PASS; acc 0.614738; MC not run |
| `runs/sep_AC_redundant_2301` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.700314e-05 | 4.453298e-06 | 4.145643e-05 | 0.61646 | GF PASS; acc 0.615893; MC not run |
| `runs/sep_AC_redundant_2310` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.931551e-05 | 4.624287e-06 | 4.39398e-05 | 0.61277 | GF PASS; acc 0.612613; MC not run |
| `runs/sep_AC_redundant_3012` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.818455e-05 | 4.51308e-06 | 4.269763e-05 | 0.62010 | GF PASS; acc 0.619170; MC not run |
| `runs/sep_AC_redundant_3021` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.829057e-05 | 5.025977e-06 | 4.331655e-05 | 0.61149 | GF PASS; acc 0.611009; MC not run |
| `runs/sep_AC_redundant_3102` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 4.781698e-05 | 5.377131e-06 | 5.319412e-05 | 0.60785 | GF PASS; acc 0.607331; MC not run |
| `runs/sep_AC_redundant_3120` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.822513e-05 | 4.737278e-06 | 4.296241e-05 | 0.61393 | GF PASS; acc 0.613573; MC not run |
| `runs/sep_AC_redundant_3201` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.801549e-05 | 4.99988e-06 | 4.301537e-05 | 0.60904 | GF PASS; acc 0.608457; MC not run |
| `runs/sep_AC_redundant_3210` (regenerate) | AC redundant | 143 | 33 | 3.182639e-19 | 3.806179e-05 | 4.989448e-06 | 4.305124e-05 | 0.60905 | GF PASS; acc 0.608967; MC not run |
| `runs/sep_AC_seq_012` (regenerate) | AC seq | 135 | 33 | 3.182639e-19 | 4.688637e-05 | 1.615522e-05 | 6.304159e-05 | 0.57281 | GF PASS; acc 0.572875; MC not run |
| `runs/sep_AC_seq_021` (regenerate) | AC seq | 135 | 33 | 3.182639e-19 | 4.425712e-05 | 1.582794e-05 | 6.008506e-05 | 0.57281 | GF PASS; acc 0.572571; MC not run |
| `runs/sep_AC_seq_102` (regenerate) | AC seq | 135 | 33 | 3.182639e-19 | 4.757524e-05 | 1.592748e-05 | 6.350272e-05 | 0.57281 | GF PASS; acc 0.572222; MC not run |
| `runs/sep_AC_seq_120` (regenerate) | AC seq | 135 | 33 | 3.182639e-19 | 4.399631e-05 | 1.569189e-05 | 5.968819e-05 | 0.57167 | GF PASS; acc 0.571104; MC not run |
| `runs/sep_AC_seq_201` (regenerate) | AC seq | 135 | 33 | 3.182639e-19 | 4.058383e-05 | 1.557782e-05 | 5.616165e-05 | 0.57167 | GF PASS; acc 0.571450; MC not run |
| `runs/sep_AC_seq_210` (regenerate) | AC seq | 135 | 33 | 3.182639e-19 | 4.022916e-05 | 1.531582e-05 | 5.554498e-05 | 0.57168 | GF PASS; acc 0.571474; MC not run |
| `runs/sep_A_cat13_012` (regenerate) | A cat13 | 135 | 33 | 3.182639e-19 | 3.835964e-05 | 5.098499e-06 | 4.345814e-05 | 0.64759 | GF PASS; acc 0.646570; MC not run |
| `runs/sep_A_cat13_021` (regenerate) | A cat13 | 135 | 33 | 3.182639e-19 | 3.815096e-05 | 5.45682e-06 | 4.360778e-05 | 0.64501 | GF PASS; acc 0.644238; MC not run |
| `runs/sep_A_cat13_102` (regenerate) | A cat13 | 135 | 33 | 3.182639e-19 | 4.264299e-05 | 5.670147e-06 | 4.831313e-05 | 0.64372 | GF PASS; acc 0.643823; MC not run |
| `runs/sep_A_cat13_120` (regenerate) | A cat13 | 135 | 33 | 3.182639e-19 | 3.819091e-05 | 5.152745e-06 | 4.334365e-05 | 0.64694 | GF PASS; acc 0.646483; MC not run |
| `runs/sep_A_cat13_201` (regenerate) | A cat13 | 135 | 33 | 3.182639e-19 | 3.741e-05 | 5.14215e-06 | 4.255215e-05 | 0.64694 | GF PASS; acc 0.646514; MC not run |
| `runs/sep_A_cat13_210` (regenerate) | A cat13 | 135 | 33 | 3.182639e-19 | 3.76105e-05 | 5.129055e-06 | 4.273956e-05 | 0.64694 | GF PASS; acc 0.646832; MC not run |
| `runs/sep_A_cat13red_012` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.809327e-05 | 5.043691e-06 | 4.313696e-05 | 0.63499 | GF PASS; acc 0.634614; MC not run |
| `runs/sep_A_cat13red_0132` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.872722e-05 | 5.155374e-06 | 4.388259e-05 | 0.63410 | GF PASS; acc 0.633029; MC not run |
| `runs/sep_A_cat13red_021` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.821148e-05 | 5.340262e-06 | 4.355174e-05 | 0.63246 | GF PASS; acc 0.632300; MC not run |
| `runs/sep_A_cat13red_0231` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.864445e-05 | 5.502329e-06 | 4.414678e-05 | 0.63136 | GF PASS; acc 0.631570; MC not run |
| `runs/sep_A_cat13red_0312` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.908321e-05 | 5.33923e-06 | 4.442244e-05 | 0.63321 | GF PASS; acc 0.632957; MC not run |
| `runs/sep_A_cat13red_0321` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.900033e-05 | 5.328766e-06 | 4.43291e-05 | 0.63321 | GF PASS; acc 0.633017; MC not run |
| `runs/sep_A_cat13red_102` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 4.253042e-05 | 5.502856e-06 | 4.803328e-05 | 0.63120 | GF PASS; acc 0.630919; MC not run |
| `runs/sep_A_cat13red_1032` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.877237e-05 | 5.145912e-06 | 4.391828e-05 | 0.63410 | GF PASS; acc 0.634162; MC not run |
| `runs/sep_A_cat13red_120` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.797809e-05 | 5.072195e-06 | 4.305028e-05 | 0.63435 | GF PASS; acc 0.633875; MC not run |
| `runs/sep_A_cat13red_1230` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.80719e-05 | 5.092292e-06 | 4.316419e-05 | 0.63351 | GF PASS; acc 0.633453; MC not run |
| `runs/sep_A_cat13red_1302` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.906593e-05 | 5.379576e-06 | 4.444551e-05 | 0.63179 | GF PASS; acc 0.631559; MC not run |
| `runs/sep_A_cat13red_1320` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.880345e-05 | 5.188652e-06 | 4.39921e-05 | 0.63304 | GF PASS; acc 0.633070; MC not run |
| `runs/sep_A_cat13red_201` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.785317e-05 | 5.066845e-06 | 4.292001e-05 | 0.63435 | GF PASS; acc 0.633878; MC not run |
| `runs/sep_A_cat13red_2031` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.822848e-05 | 5.217646e-06 | 4.344612e-05 | 0.63325 | GF PASS; acc 0.632431; MC not run |
| `runs/sep_A_cat13red_210` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.782706e-05 | 5.060456e-06 | 4.288752e-05 | 0.63435 | GF PASS; acc 0.634678; MC not run |
| `runs/sep_A_cat13red_2130` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.792088e-05 | 5.079474e-06 | 4.300035e-05 | 0.63351 | GF PASS; acc 0.632855; MC not run |
| `runs/sep_A_cat13red_2301` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.817061e-05 | 5.206078e-06 | 4.337669e-05 | 0.63283 | GF PASS; acc 0.631939; MC not run |
| `runs/sep_A_cat13red_2310` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.816202e-05 | 5.196918e-06 | 4.335893e-05 | 0.63283 | GF PASS; acc 0.631703; MC not run |
| `runs/sep_A_cat13red_3012` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.90473e-05 | 5.305413e-06 | 4.435271e-05 | 0.63322 | GF PASS; acc 0.632584; MC not run |
| `runs/sep_A_cat13red_3021` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.920804e-05 | 5.625315e-06 | 4.483335e-05 | 0.63069 | GF PASS; acc 0.630047; MC not run |
| `runs/sep_A_cat13red_3102` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 4.379849e-05 | 5.78862e-06 | 4.958711e-05 | 0.62944 | GF PASS; acc 0.629521; MC not run |
| `runs/sep_A_cat13red_3120` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.894744e-05 | 5.350673e-06 | 4.429811e-05 | 0.63258 | GF PASS; acc 0.632143; MC not run |
| `runs/sep_A_cat13red_3201` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.873861e-05 | 5.339705e-06 | 4.407832e-05 | 0.63258 | GF PASS; acc 0.632155; MC not run |
| `runs/sep_A_cat13red_3210` (regenerate) | A cat13red | 140 | 33 | 3.182639e-19 | 3.873002e-05 | 5.33217e-06 | 4.406219e-05 | 0.63258 | GF PASS; acc 0.632348; MC not run |
| `runs/sep_A_cat3_012` (regenerate) | A cat3 | 138 | 33 | 3.182639e-19 | 7.477921e-05 | 5.334675e-06 | 8.011389e-05 | 0.64267 | GF PASS; acc 0.642010; MC not run |
| `runs/sep_A_cat3_021` (regenerate) | A cat3 | 138 | 33 | 3.182639e-19 | 7.460397e-05 | 5.320145e-06 | 7.992411e-05 | 0.64267 | GF PASS; acc 0.642013; MC not run |
| `runs/sep_A_cat3_102` (regenerate) | A cat3 | 138 | 33 | 3.182639e-19 | 7.473045e-05 | 5.297642e-06 | 8.002809e-05 | 0.64267 | GF PASS; acc 0.642041; MC not run |
| `runs/sep_A_cat3_120` (regenerate) | A cat3 | 138 | 33 | 3.182639e-19 | 7.470934e-05 | 5.596673e-06 | 8.030601e-05 | 0.64011 | GF PASS; acc 0.639620; MC not run |
| `runs/sep_A_cat3_201` (regenerate) | A cat3 | 138 | 33 | 3.182639e-19 | 7.458508e-05 | 5.617472e-06 | 8.020255e-05 | 0.64011 | GF PASS; acc 0.639612; MC not run |
| `runs/sep_A_cat3_210` (regenerate) | A cat3 | 138 | 33 | 3.182639e-19 | 7.446983e-05 | 5.579431e-06 | 8.004926e-05 | 0.64011 | GF PASS; acc 0.639619; MC not run |
| `runs/sep_A_cat4_012` (regenerate) | A cat4 | 141 | 33 | 3.182639e-19 | 8.982816e-05 | 7.665832e-06 | 9.749399e-05 | 0.63159 | GF PASS; acc 0.631625; MC not run |
| `runs/sep_A_cat4_021` (regenerate) | A cat4 | 141 | 33 | 3.182639e-19 | 8.861138e-05 | 7.59624e-06 | 9.620762e-05 | 0.63159 | GF PASS; acc 0.631615; MC not run |
| `runs/sep_A_cat4_102` (regenerate) | A cat4 | 141 | 33 | 3.182639e-19 | 8.975793e-05 | 7.628784e-06 | 9.738671e-05 | 0.63159 | GF PASS; acc 0.631640; MC not run |
| `runs/sep_A_cat4_120` (regenerate) | A cat4 | 141 | 33 | 3.182639e-19 | 8.841807e-05 | 7.524488e-06 | 9.594255e-05 | 0.63159 | GF PASS; acc 0.630859; MC not run |
| `runs/sep_A_cat4_201` (regenerate) | A cat4 | 141 | 33 | 3.182639e-19 | 8.727549e-05 | 7.482179e-06 | 9.475767e-05 | 0.63159 | GF PASS; acc 0.630867; MC not run |
| `runs/sep_A_cat4_210` (regenerate) | A cat4 | 141 | 33 | 3.182639e-19 | 8.713815e-05 | 7.447106e-06 | 9.458525e-05 | 0.63159 | GF PASS; acc 0.630852; MC not run |
| `runs/sep_A_cat_012` (regenerate) | A cat | 135 | 33 | 3.182639e-19 | 7.122149e-05 | 4.295875e-06 | 7.551736e-05 | 0.65095 | GF PASS; acc 0.650106; MC not run |
| `runs/sep_A_cat_021` (regenerate) | A cat | 135 | 33 | 3.182639e-19 | 7.091313e-05 | 4.275888e-06 | 7.518902e-05 | 0.65095 | GF PASS; acc 0.650107; MC not run |
| `runs/sep_A_cat_102` (regenerate) | A cat | 135 | 33 | 3.182639e-19 | 7.130572e-05 | 4.269419e-06 | 7.557514e-05 | 0.65095 | GF PASS; acc 0.650448; MC not run |
| `runs/sep_A_cat_120` (regenerate) | A cat | 135 | 33 | 3.182639e-19 | 7.069174e-05 | 4.407118e-06 | 7.509886e-05 | 0.64884 | GF PASS; acc 0.648444; MC not run |
| `runs/sep_A_cat_201` (regenerate) | A cat | 135 | 33 | 3.182639e-19 | 6.800103e-05 | 4.531386e-06 | 7.253241e-05 | 0.64776 | GF PASS; acc 0.646947; MC not run |
| `runs/sep_A_cat_210` (regenerate) | A cat | 135 | 33 | 3.182639e-19 | 6.529728e-05 | 4.246477e-06 | 6.954376e-05 | 0.65014 | GF PASS; acc 0.649892; MC not run |
| `runs/sep_A_catred_012` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 8.110543e-05 | 3.644162e-06 | 8.474959e-05 | 0.64212 | GF PASS; acc 0.641907; MC not run |
| `runs/sep_A_catred_0132` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 8.273657e-05 | 3.653192e-06 | 8.638976e-05 | 0.64212 | GF PASS; acc 0.641197; MC not run |
| `runs/sep_A_catred_021` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 8.111992e-05 | 3.631336e-06 | 8.475126e-05 | 0.64212 | GF PASS; acc 0.642321; MC not run |
| `runs/sep_A_catred_0231` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.638165e-05 | 4.045862e-06 | 8.042751e-05 | 0.63875 | GF PASS; acc 0.638796; MC not run |
| `runs/sep_A_catred_0312` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.697661e-05 | 3.896031e-06 | 8.087264e-05 | 0.64067 | GF PASS; acc 0.640304; MC not run |
| `runs/sep_A_catred_0321` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.697661e-05 | 3.889297e-06 | 8.086591e-05 | 0.64067 | GF PASS; acc 0.640309; MC not run |
| `runs/sep_A_catred_102` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.980196e-05 | 3.727664e-06 | 8.352963e-05 | 0.64148 | GF PASS; acc 0.641454; MC not run |
| `runs/sep_A_catred_1032` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 8.156644e-05 | 3.736673e-06 | 8.530311e-05 | 0.64148 | GF PASS; acc 0.641228; MC not run |
| `runs/sep_A_catred_120` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.935951e-05 | 3.837378e-06 | 8.319688e-05 | 0.63961 | GF PASS; acc 0.639372; MC not run |
| `runs/sep_A_catred_1230` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.665749e-05 | 3.708241e-06 | 8.036573e-05 | 0.64195 | GF PASS; acc 0.641359; MC not run |
| `runs/sep_A_catred_1302` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 8.147524e-05 | 3.751277e-06 | 8.522652e-05 | 0.64148 | GF PASS; acc 0.640731; MC not run |
| `runs/sep_A_catred_1320` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 8.265936e-05 | 3.959168e-06 | 8.661852e-05 | 0.63875 | GF PASS; acc 0.638470; MC not run |
| `runs/sep_A_catred_201` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.830961e-05 | 3.813916e-06 | 8.212353e-05 | 0.63918 | GF PASS; acc 0.638416; MC not run |
| `runs/sep_A_catred_2031` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 8.122935e-05 | 4.290278e-06 | 8.551963e-05 | 0.63519 | GF PASS; acc 0.635050; MC not run |
| `runs/sep_A_catred_210` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.429651e-05 | 3.743572e-06 | 7.804008e-05 | 0.64088 | GF PASS; acc 0.640381; MC not run |
| `runs/sep_A_catred_2130` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.666087e-05 | 3.694878e-06 | 8.035575e-05 | 0.64195 | GF PASS; acc 0.641344; MC not run |
| `runs/sep_A_catred_2301` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.179303e-05 | 3.797538e-06 | 7.559057e-05 | 0.64072 | GF PASS; acc 0.639931; MC not run |
| `runs/sep_A_catred_2310` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.515924e-05 | 3.996383e-06 | 7.915562e-05 | 0.63880 | GF PASS; acc 0.638411; MC not run |
| `runs/sep_A_catred_3012` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.905481e-05 | 3.770136e-06 | 8.282495e-05 | 0.64131 | GF PASS; acc 0.640767; MC not run |
| `runs/sep_A_catred_3021` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.905481e-05 | 3.759479e-06 | 8.281429e-05 | 0.64131 | GF PASS; acc 0.640771; MC not run |
| `runs/sep_A_catred_3102` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.920283e-05 | 3.882794e-06 | 8.308562e-05 | 0.64024 | GF PASS; acc 0.640539; MC not run |
| `runs/sep_A_catred_3120` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.880748e-05 | 3.953963e-06 | 8.276144e-05 | 0.63944 | GF PASS; acc 0.638946; MC not run |
| `runs/sep_A_catred_3201` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.783031e-05 | 4.018748e-06 | 8.184906e-05 | 0.63816 | GF PASS; acc 0.638093; MC not run |
| `runs/sep_A_catred_3210` (regenerate) | A catred | 140 | 33 | 3.182639e-19 | 7.324372e-05 | 3.86016e-06 | 7.710387e-05 | 0.64072 | GF PASS; acc 0.639758; MC not run |
| `runs/sep_A_direct_012` (regenerate) | A direct | 132 | 33 | 3.182639e-19 | 3.761698e-05 | 4.537546e-06 | 4.215452e-05 | 0.65111 | GF PASS; acc 0.650685; MC not run |
| `runs/sep_A_direct_021` (regenerate) | A direct | 132 | 33 | 3.182639e-19 | 3.740844e-05 | 4.867734e-06 | 4.227618e-05 | 0.64852 | GF PASS; acc 0.647994; MC not run |
| `runs/sep_A_direct_102` (regenerate) | A direct | 132 | 33 | 3.182639e-19 | 4.15867e-05 | 5.071201e-06 | 4.665791e-05 | 0.64723 | GF PASS; acc 0.646551; MC not run |
| `runs/sep_A_direct_120` (regenerate) | A direct | 132 | 33 | 3.182639e-19 | 3.744436e-05 | 4.580604e-06 | 4.202496e-05 | 0.65046 | GF PASS; acc 0.649777; MC not run |
| `runs/sep_A_direct_201` (regenerate) | A direct | 132 | 33 | 3.182639e-19 | 3.666407e-05 | 4.570257e-06 | 4.123433e-05 | 0.65046 | GF PASS; acc 0.649773; MC not run |
| `runs/sep_A_direct_210` (regenerate) | A direct | 132 | 33 | 3.182639e-19 | 3.686449e-05 | 4.557026e-06 | 4.142151e-05 | 0.65046 | GF PASS; acc 0.649971; MC not run |
| `runs/sep_A_flag_012` (regenerate) | A flag | 138 | 33 | 3.182639e-19 | 3.189764e-05 | 4.865357e-06 | 3.6763e-05 | 0.62910 | GF PASS; acc 0.629132; MC not run |
| `runs/sep_A_flag_021` (regenerate) | A flag | 138 | 33 | 3.182639e-19 | 3.165029e-05 | 5.139577e-06 | 3.678987e-05 | 0.62597 | GF PASS; acc 0.625397; MC not run |
| `runs/sep_A_flag_102` (regenerate) | A flag | 138 | 33 | 3.182639e-19 | 3.258527e-05 | 5.316651e-06 | 3.790192e-05 | 0.62411 | GF PASS; acc 0.623716; MC not run |
| `runs/sep_A_flag_120` (regenerate) | A flag | 138 | 33 | 3.182639e-19 | 3.228011e-05 | 4.918616e-06 | 3.719872e-05 | 0.62847 | GF PASS; acc 0.628189; MC not run |
| `runs/sep_A_flag_201` (regenerate) | A flag | 138 | 33 | 3.182639e-19 | 3.156626e-05 | 4.901199e-06 | 3.646745e-05 | 0.62847 | GF PASS; acc 0.628184; MC not run |
| `runs/sep_A_flag_210` (regenerate) | A flag | 138 | 33 | 3.182639e-19 | 3.182912e-05 | 4.896184e-06 | 3.67253e-05 | 0.62847 | GF PASS; acc 0.628152; MC not run |
| `runs/sep_A_hybrid1_012` (regenerate) | A hybrid1 | 131 | 33 | 3.182639e-19 | 3.653884e-05 | 5.227091e-06 | 4.176593e-05 | 0.64666 | GF PASS; acc 0.646507; MC not run |
| `runs/sep_A_hybrid1_021` (regenerate) | A hybrid1 | 131 | 33 | 3.182639e-19 | 3.623118e-05 | 5.219473e-06 | 4.145065e-05 | 0.64667 | GF PASS; acc 0.646630; MC not run |
| `runs/sep_A_hybrid1_102` (regenerate) | A hybrid1 | 131 | 33 | 3.182639e-19 | 3.653884e-05 | 5.227091e-06 | 4.176593e-05 | 0.64666 | GF PASS; acc 0.646507; MC not run |
| `runs/sep_A_hybrid1_120` (regenerate) | A hybrid1 | 131 | 33 | 3.182639e-19 | 3.653884e-05 | 5.227091e-06 | 4.176593e-05 | 0.64666 | GF PASS; acc 0.646507; MC not run |
| `runs/sep_A_hybrid1_201` (regenerate) | A hybrid1 | 131 | 33 | 3.182639e-19 | 3.623118e-05 | 5.219473e-06 | 4.145065e-05 | 0.64667 | GF PASS; acc 0.646630; MC not run |
| `runs/sep_A_hybrid1_210` (regenerate) | A hybrid1 | 131 | 33 | 3.182639e-19 | 3.623118e-05 | 5.219473e-06 | 4.145065e-05 | 0.64667 | GF PASS; acc 0.646630; MC not run |
| `runs/sep_A_hybrid2_012` (regenerate) | A hybrid2 | 130 | 33 | 3.182639e-19 | 3.555542e-05 | 4.546212e-06 | 4.010164e-05 | 0.65025 | GF PASS; acc 0.649437; MC not run |
| `runs/sep_A_hybrid2_021` (regenerate) | A hybrid2 | 130 | 33 | 3.182639e-19 | 3.555542e-05 | 4.546212e-06 | 4.010164e-05 | 0.65025 | GF PASS; acc 0.649437; MC not run |
| `runs/sep_A_hybrid2_102` (regenerate) | A hybrid2 | 130 | 33 | 3.182639e-19 | 3.555542e-05 | 4.546212e-06 | 4.010164e-05 | 0.65025 | GF PASS; acc 0.649437; MC not run |
| `runs/sep_A_hybrid2_120` (regenerate) | A hybrid2 | 130 | 33 | 3.182639e-19 | 3.555542e-05 | 4.546212e-06 | 4.010164e-05 | 0.65025 | GF PASS; acc 0.649437; MC not run |
| `runs/sep_A_hybrid2_201` (regenerate) | A hybrid2 | 130 | 33 | 3.182639e-19 | 3.555542e-05 | 4.546212e-06 | 4.010164e-05 | 0.65025 | GF PASS; acc 0.649437; MC not run |
| `runs/sep_A_hybrid2_210` (regenerate) | A hybrid2 | 130 | 33 | 3.182639e-19 | 3.555542e-05 | 4.546212e-06 | 4.010164e-05 | 0.65025 | GF PASS; acc 0.649437; MC not run |
| `runs/sep_A_hybrid2t_012` (regenerate) | A hybrid2t | 129 | 33 | 3.182639e-19 | 4.468109e-05 | 4.889171e-06 | 4.957027e-05 | 0.64767 | GF PASS; acc 0.647493; MC not run |
| `runs/sep_A_redundant_012` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.679781e-05 | 4.182568e-06 | 4.098037e-05 | 0.64407 | GF PASS; acc 0.643454; MC not run |
| `runs/sep_A_redundant_0132` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.797128e-05 | 4.738244e-06 | 4.270952e-05 | 0.64020 | GF PASS; acc 0.639081; MC not run |
| `runs/sep_A_redundant_021` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.691655e-05 | 4.429621e-06 | 4.134617e-05 | 0.64150 | GF PASS; acc 0.640795; MC not run |
| `runs/sep_A_redundant_0231` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.95681e-05 | 4.525262e-06 | 4.409336e-05 | 0.64082 | GF PASS; acc 0.639981; MC not run |
| `runs/sep_A_redundant_0312` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.80388e-05 | 4.447775e-06 | 4.248657e-05 | 0.64271 | GF PASS; acc 0.642216; MC not run |
| `runs/sep_A_redundant_0321` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.827784e-05 | 4.788843e-06 | 4.306668e-05 | 0.63951 | GF PASS; acc 0.639300; MC not run |
| `runs/sep_A_redundant_102` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 4.021679e-05 | 4.559161e-06 | 4.477595e-05 | 0.64023 | GF PASS; acc 0.639746; MC not run |
| `runs/sep_A_redundant_1032` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.808645e-05 | 4.744906e-06 | 4.283135e-05 | 0.64020 | GF PASS; acc 0.639613; MC not run |
| `runs/sep_A_redundant_120` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.655255e-05 | 4.185062e-06 | 4.073761e-05 | 0.64343 | GF PASS; acc 0.643293; MC not run |
| `runs/sep_A_redundant_1230` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.664645e-05 | 4.193818e-06 | 4.084027e-05 | 0.64342 | GF PASS; acc 0.643024; MC not run |
| `runs/sep_A_redundant_1302` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.766105e-05 | 4.499229e-06 | 4.216028e-05 | 0.64211 | GF PASS; acc 0.641515; MC not run |
| `runs/sep_A_redundant_1320` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.80415e-05 | 4.715206e-06 | 4.275671e-05 | 0.63955 | GF PASS; acc 0.638870; MC not run |
| `runs/sep_A_redundant_201` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.649059e-05 | 4.19033e-06 | 4.068092e-05 | 0.64343 | GF PASS; acc 0.642850; MC not run |
| `runs/sep_A_redundant_2031` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.923977e-05 | 4.43141e-06 | 4.367118e-05 | 0.64146 | GF PASS; acc 0.640090; MC not run |
| `runs/sep_A_redundant_210` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.640161e-05 | 4.175094e-06 | 4.057671e-05 | 0.64343 | GF PASS; acc 0.642674; MC not run |
| `runs/sep_A_redundant_2130` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.649552e-05 | 4.183251e-06 | 4.067877e-05 | 0.64343 | GF PASS; acc 0.643123; MC not run |
| `runs/sep_A_redundant_2301` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.686127e-05 | 4.166175e-06 | 4.102744e-05 | 0.64403 | GF PASS; acc 0.643774; MC not run |
| `runs/sep_A_redundant_2310` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.904472e-05 | 4.333508e-06 | 4.337823e-05 | 0.64210 | GF PASS; acc 0.641383; MC not run |
| `runs/sep_A_redundant_3012` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.763755e-05 | 4.112324e-06 | 4.174987e-05 | 0.64593 | GF PASS; acc 0.645241; MC not run |
| `runs/sep_A_redundant_3021` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.781029e-05 | 4.537648e-06 | 4.234794e-05 | 0.64143 | GF PASS; acc 0.641023; MC not run |
| `runs/sep_A_redundant_3102` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 4.598402e-05 | 4.76573e-06 | 5.074975e-05 | 0.63951 | GF PASS; acc 0.639145; MC not run |
| `runs/sep_A_redundant_3120` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.805206e-05 | 4.375312e-06 | 4.242737e-05 | 0.64270 | GF PASS; acc 0.641935; MC not run |
| `runs/sep_A_redundant_3201` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.782927e-05 | 4.606664e-06 | 4.243593e-05 | 0.64014 | GF PASS; acc 0.639978; MC not run |
| `runs/sep_A_redundant_3210` (regenerate) | A redundant | 136 | 33 | 3.182639e-19 | 3.796843e-05 | 4.610655e-06 | 4.257908e-05 | 0.64014 | GF PASS; acc 0.639630; MC not run |
| `runs/sep_A_seq_012` (regenerate) | A seq | 132 | 33 | 3.182639e-19 | 4.08268e-05 | 1.026181e-05 | 5.108861e-05 | 0.62081 | GF PASS; acc 0.620989; MC not run |
| `runs/sep_A_seq_021` (regenerate) | A seq | 132 | 33 | 3.182639e-19 | 3.920154e-05 | 1.010138e-05 | 4.930292e-05 | 0.62081 | GF PASS; acc 0.620857; MC not run |
| `runs/sep_A_seq_102` (regenerate) | A seq | 132 | 33 | 3.182639e-19 | 4.256596e-05 | 1.025284e-05 | 5.28188e-05 | 0.62081 | GF PASS; acc 0.619896; MC not run |
| `runs/sep_A_seq_120` (regenerate) | A seq | 132 | 33 | 3.182639e-19 | 4.113349e-05 | 1.018865e-05 | 5.132214e-05 | 0.62019 | GF PASS; acc 0.620014; MC not run |
| `runs/sep_A_seq_201` (regenerate) | A seq | 132 | 33 | 3.182639e-19 | 3.772744e-05 | 1.007361e-05 | 4.780105e-05 | 0.62019 | GF PASS; acc 0.620517; MC not run |
| `runs/sep_A_seq_210` (regenerate) | A seq | 132 | 33 | 3.182639e-19 | 3.838477e-05 | 1.000865e-05 | 4.839341e-05 | 0.62020 | GF PASS; acc 0.619708; MC not run |
| `runs/sep_BC_cat13_012` (regenerate) | BC cat13 | 141 | 33 | 3.182639e-19 | 3.601836e-05 | 4.453687e-06 | 4.047205e-05 | 0.62329 | GF PASS; acc 0.623162; MC not run |
| `runs/sep_BC_cat13_021` (regenerate) | BC cat13 | 141 | 33 | 3.182639e-19 | 3.667531e-05 | 4.691475e-06 | 4.136679e-05 | 0.61833 | GF PASS; acc 0.618107; MC not run |
| `runs/sep_BC_cat13_102` (regenerate) | BC cat13 | 141 | 33 | 3.182639e-19 | 3.618749e-05 | 4.73768e-06 | 4.092517e-05 | 0.61588 | GF PASS; acc 0.615838; MC not run |
| `runs/sep_BC_cat13_120` (regenerate) | BC cat13 | 141 | 33 | 3.182639e-19 | 3.600082e-05 | 4.327638e-06 | 4.032846e-05 | 0.62204 | GF PASS; acc 0.621555; MC not run |
| `runs/sep_BC_cat13_201` (regenerate) | BC cat13 | 141 | 33 | 3.182639e-19 | 3.650701e-05 | 4.342651e-06 | 4.084966e-05 | 0.62204 | GF PASS; acc 0.621556; MC not run |
| `runs/sep_BC_cat13_210` (regenerate) | BC cat13 | 141 | 33 | 3.182639e-19 | 3.646233e-05 | 4.283868e-06 | 4.07462e-05 | 0.62204 | GF PASS; acc 0.621928; MC not run |
| `runs/sep_BC_cat13red_012` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.316118e-05 | 2.664722e-06 | 3.58259e-05 | 0.59928 | GF PASS; acc 0.599087; MC not run |
| `runs/sep_BC_cat13red_0132` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.296609e-05 | 2.646561e-06 | 3.561265e-05 | 0.59760 | GF PASS; acc 0.597298; MC not run |
| `runs/sep_BC_cat13red_021` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.316118e-05 | 2.702313e-06 | 3.586349e-05 | 0.59451 | GF PASS; acc 0.594914; MC not run |
| `runs/sep_BC_cat13red_0231` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.312574e-05 | 2.645241e-06 | 3.577098e-05 | 0.59245 | GF PASS; acc 0.592759; MC not run |
| `runs/sep_BC_cat13red_0312` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.305054e-05 | 2.584538e-06 | 3.563508e-05 | 0.59592 | GF PASS; acc 0.595079; MC not run |
| `runs/sep_BC_cat13red_0321` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.305054e-05 | 2.580516e-06 | 3.563105e-05 | 0.59593 | GF PASS; acc 0.595800; MC not run |
| `runs/sep_BC_cat13red_102` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.335895e-05 | 2.782111e-06 | 3.614106e-05 | 0.59214 | GF PASS; acc 0.592338; MC not run |
| `runs/sep_BC_cat13red_1032` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.297498e-05 | 2.64027e-06 | 3.561525e-05 | 0.59760 | GF PASS; acc 0.596808; MC not run |
| `runs/sep_BC_cat13red_120` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.342731e-05 | 2.624267e-06 | 3.605158e-05 | 0.59807 | GF PASS; acc 0.597520; MC not run |
| `runs/sep_BC_cat13red_1230` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.351596e-05 | 2.632481e-06 | 3.614844e-05 | 0.59648 | GF PASS; acc 0.596664; MC not run |
| `runs/sep_BC_cat13red_1302` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.297498e-05 | 2.724153e-06 | 3.569914e-05 | 0.59325 | GF PASS; acc 0.592805; MC not run |
| `runs/sep_BC_cat13red_1320` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.312574e-05 | 2.619309e-06 | 3.574505e-05 | 0.59561 | GF PASS; acc 0.595874; MC not run |
| `runs/sep_BC_cat13red_201` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.317006e-05 | 2.630713e-06 | 3.580078e-05 | 0.59807 | GF PASS; acc 0.597891; MC not run |
| `runs/sep_BC_cat13red_2031` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.313463e-05 | 2.569433e-06 | 3.570406e-05 | 0.59600 | GF PASS; acc 0.595164; MC not run |
| `runs/sep_BC_cat13red_210` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.342731e-05 | 2.626652e-06 | 3.605396e-05 | 0.59807 | GF PASS; acc 0.597368; MC not run |
| `runs/sep_BC_cat13red_2130` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.351596e-05 | 2.635511e-06 | 3.615147e-05 | 0.59648 | GF PASS; acc 0.596131; MC not run |
| `runs/sep_BC_cat13red_2301` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.329427e-05 | 2.577927e-06 | 3.58722e-05 | 0.59521 | GF PASS; acc 0.594879; MC not run |
| `runs/sep_BC_cat13red_2310` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.344503e-05 | 2.575232e-06 | 3.602026e-05 | 0.59521 | GF PASS; acc 0.595307; MC not run |
| `runs/sep_BC_cat13red_3012` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.305054e-05 | 2.596545e-06 | 3.564708e-05 | 0.59593 | GF PASS; acc 0.595587; MC not run |
| `runs/sep_BC_cat13red_3021` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.305054e-05 | 2.644575e-06 | 3.569511e-05 | 0.59119 | GF PASS; acc 0.591485; MC not run |
| `runs/sep_BC_cat13red_3102` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.317721e-05 | 2.701186e-06 | 3.587839e-05 | 0.58884 | GF PASS; acc 0.588562; MC not run |
| `runs/sep_BC_cat13red_3120` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.313907e-05 | 2.546435e-06 | 3.568551e-05 | 0.59474 | GF PASS; acc 0.593398; MC not run |
| `runs/sep_BC_cat13red_3201` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.305943e-05 | 2.547309e-06 | 3.560674e-05 | 0.59474 | GF PASS; acc 0.593402; MC not run |
| `runs/sep_BC_cat13red_3210` (regenerate) | BC cat13red | 151 | 33 | 3.182639e-19 | 3.321018e-05 | 2.542956e-06 | 3.575314e-05 | 0.59474 | GF PASS; acc 0.594663; MC not run |
| `runs/sep_BC_cat13red_m3_0123` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.40106e-05 | 2.748257e-06 | 3.675885e-05 | 0.61176 | GF PASS; acc 0.611725; MC not run |
| `runs/sep_BC_cat13red_m3_0132` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.416153e-05 | 3.115796e-06 | 3.727733e-05 | 0.59531 | GF PASS; acc 0.595298; MC not run |
| `runs/sep_BC_cat13red_m3_0213` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.433925e-05 | 2.847981e-06 | 3.718723e-05 | 0.60447 | GF PASS; acc 0.604650; MC not run |
| `runs/sep_BC_cat13red_m3_0231` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.463649e-05 | 3.092481e-06 | 3.772898e-05 | 0.59206 | GF PASS; acc 0.592502; MC not run |
| `runs/sep_BC_cat13red_m3_0312` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.424598e-05 | 3.070364e-06 | 3.731634e-05 | 0.59135 | GF PASS; acc 0.591289; MC not run |
| `runs/sep_BC_cat13red_m3_0321` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.441463e-05 | 3.047478e-06 | 3.746211e-05 | 0.59136 | GF PASS; acc 0.591338; MC not run |
| `runs/sep_BC_cat13red_m3_1023` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.420838e-05 | 2.851295e-06 | 3.705967e-05 | 0.60447 | GF PASS; acc 0.604349; MC not run |
| `runs/sep_BC_cat13red_m3_1032` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.465883e-05 | 3.203172e-06 | 3.786201e-05 | 0.59176 | GF PASS; acc 0.591907; MC not run |
| `runs/sep_BC_cat13red_m3_1203` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.435258e-05 | 2.841659e-06 | 3.719424e-05 | 0.60810 | GF PASS; acc 0.607508; MC not run |
| `runs/sep_BC_cat13red_m3_1230` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.435258e-05 | 2.843838e-06 | 3.719642e-05 | 0.60729 | GF PASS; acc 0.607205; MC not run |
| `runs/sep_BC_cat13red_m3_1302` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.435931e-05 | 3.187963e-06 | 3.754727e-05 | 0.59216 | GF PASS; acc 0.591120; MC not run |
| `runs/sep_BC_cat13red_m3_1320` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.452983e-05 | 3.097883e-06 | 3.762771e-05 | 0.59372 | GF PASS; acc 0.593709; MC not run |
| `runs/sep_BC_cat13red_m3_2013` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.492088e-05 | 2.993158e-06 | 3.791404e-05 | 0.60810 | GF PASS; acc 0.607766; MC not run |
| `runs/sep_BC_cat13red_m3_2031` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.536912e-05 | 3.213884e-06 | 3.8583e-05 | 0.59324 | GF PASS; acc 0.592772; MC not run |
| `runs/sep_BC_cat13red_m3_2103` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.506088e-05 | 3.036846e-06 | 3.809773e-05 | 0.60447 | GF PASS; acc 0.604507; MC not run |
| `runs/sep_BC_cat13red_m3_2130` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.484977e-05 | 3.026531e-06 | 3.78763e-05 | 0.60487 | GF PASS; acc 0.604455; MC not run |
| `runs/sep_BC_cat13red_m3_2301` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.485848e-05 | 2.992248e-06 | 3.785073e-05 | 0.60399 | GF PASS; acc 0.603508; MC not run |
| `runs/sep_BC_cat13red_m3_2310` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.518654e-05 | 3.126757e-06 | 3.83133e-05 | 0.59601 | GF PASS; acc 0.595292; MC not run |
| `runs/sep_BC_cat13red_m3_3012` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.415709e-05 | 2.923071e-06 | 3.708016e-05 | 0.59967 | GF PASS; acc 0.599702; MC not run |
| `runs/sep_BC_cat13red_m3_3021` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.441463e-05 | 3.052381e-06 | 3.746701e-05 | 0.59136 | GF PASS; acc 0.590626; MC not run |
| `runs/sep_BC_cat13red_m3_3102` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.433264e-05 | 3.126378e-06 | 3.745902e-05 | 0.58822 | GF PASS; acc 0.587799; MC not run |
| `runs/sep_BC_cat13red_m3_3120` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.452538e-05 | 2.955649e-06 | 3.748103e-05 | 0.59411 | GF PASS; acc 0.593803; MC not run |
| `runs/sep_BC_cat13red_m3_3201` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.471181e-05 | 3.047538e-06 | 3.775935e-05 | 0.59530 | GF PASS; acc 0.594745; MC not run |
| `runs/sep_BC_cat13red_m3_3210` (regenerate) | BC cat13red mask=3 | 151 | 33 | 3.182639e-19 | 3.485368e-05 | 3.039354e-06 | 3.789303e-05 | 0.59531 | GF PASS; acc 0.595074; MC not run |
| `runs/sep_BC_cat13red_m5_0123` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.298838e-05 | 2.913191e-06 | 3.590157e-05 | 0.61257 | GF PASS; acc 0.613087; MC not run |
| `runs/sep_BC_cat13red_m5_0132` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.385892e-05 | 3.40865e-06 | 3.726757e-05 | 0.59325 | GF PASS; acc 0.592921; MC not run |
| `runs/sep_BC_cat13red_m5_0213` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.322838e-05 | 2.992866e-06 | 3.622124e-05 | 0.60528 | GF PASS; acc 0.604167; MC not run |
| `runs/sep_BC_cat13red_m5_0231` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.343205e-05 | 3.236901e-06 | 3.666895e-05 | 0.59372 | GF PASS; acc 0.594054; MC not run |
| `runs/sep_BC_cat13red_m5_0312` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.366781e-05 | 3.249277e-06 | 3.691709e-05 | 0.59491 | GF PASS; acc 0.594800; MC not run |
| `runs/sep_BC_cat13red_m5_0321` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.347931e-05 | 3.22386e-06 | 3.670317e-05 | 0.59372 | GF PASS; acc 0.594178; MC not run |
| `runs/sep_BC_cat13red_m5_1023` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.336615e-05 | 3.263738e-06 | 3.662989e-05 | 0.60528 | GF PASS; acc 0.604973; MC not run |
| `runs/sep_BC_cat13red_m5_1032` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.412743e-05 | 3.570221e-06 | 3.769765e-05 | 0.59325 | GF PASS; acc 0.592629; MC not run |
| `runs/sep_BC_cat13red_m5_1203` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.316393e-05 | 3.07282e-06 | 3.623675e-05 | 0.60891 | GF PASS; acc 0.608723; MC not run |
| `runs/sep_BC_cat13red_m5_1230` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.316393e-05 | 3.07588e-06 | 3.623981e-05 | 0.60891 | GF PASS; acc 0.608737; MC not run |
| `runs/sep_BC_cat13red_m5_1302` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.412743e-05 | 3.571792e-06 | 3.769922e-05 | 0.59325 | GF PASS; acc 0.592466; MC not run |
| `runs/sep_BC_cat13red_m5_1320` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.354352e-05 | 3.448296e-06 | 3.699181e-05 | 0.59363 | GF PASS; acc 0.592847; MC not run |
| `runs/sep_BC_cat13red_m5_2013` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.341726e-05 | 2.962271e-06 | 3.637953e-05 | 0.60527 | GF PASS; acc 0.604910; MC not run |
| `runs/sep_BC_cat13red_m5_2031` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.387605e-05 | 3.141887e-06 | 3.701794e-05 | 0.59847 | GF PASS; acc 0.597951; MC not run |
| `runs/sep_BC_cat13red_m5_2103` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.346171e-05 | 3.032715e-06 | 3.649442e-05 | 0.60527 | GF PASS; acc 0.604866; MC not run |
| `runs/sep_BC_cat13red_m5_2130` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.346171e-05 | 3.036452e-06 | 3.649816e-05 | 0.60527 | GF PASS; acc 0.604891; MC not run |
| `runs/sep_BC_cat13red_m5_2301` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.334316e-05 | 2.998471e-06 | 3.634163e-05 | 0.60448 | GF PASS; acc 0.603213; MC not run |
| `runs/sep_BC_cat13red_m5_2310` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.352456e-05 | 3.164316e-06 | 3.668887e-05 | 0.59570 | GF PASS; acc 0.595783; MC not run |
| `runs/sep_BC_cat13red_m5_3012` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.304609e-05 | 3.094406e-06 | 3.61405e-05 | 0.60087 | GF PASS; acc 0.600649; MC not run |
| `runs/sep_BC_cat13red_m5_3021` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.347931e-05 | 3.225822e-06 | 3.670513e-05 | 0.59372 | GF PASS; acc 0.592750; MC not run |
| `runs/sep_BC_cat13red_m5_3102` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.325054e-05 | 3.446862e-06 | 3.66974e-05 | 0.59058 | GF PASS; acc 0.590334; MC not run |
| `runs/sep_BC_cat13red_m5_3120` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.313018e-05 | 3.219375e-06 | 3.634956e-05 | 0.59530 | GF PASS; acc 0.595761; MC not run |
| `runs/sep_BC_cat13red_m5_3201` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.317054e-05 | 3.080515e-06 | 3.625105e-05 | 0.59411 | GF PASS; acc 0.593366; MC not run |
| `runs/sep_BC_cat13red_m5_3210` (regenerate) | BC cat13red mask=5 | 151 | 33 | 3.182639e-19 | 3.317463e-05 | 3.10622e-06 | 3.628085e-05 | 0.59411 | GF PASS; acc 0.593580; MC not run |
| `runs/sep_BC_cat13red_m6_0123` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.494281e-05 | 3.422795e-06 | 3.83656e-05 | 0.61257 | GF PASS; acc 0.612195; MC not run |
| `runs/sep_BC_cat13red_m6_0132` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.727816e-05 | 4.334172e-06 | 4.161233e-05 | 0.58426 | GF PASS; acc 0.584381; MC not run |
| `runs/sep_BC_cat13red_m6_0213` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.542011e-05 | 3.670809e-06 | 3.909092e-05 | 0.60527 | GF PASS; acc 0.605148; MC not run |
| `runs/sep_BC_cat13red_m6_0231` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.542011e-05 | 3.669704e-06 | 3.908981e-05 | 0.60527 | GF PASS; acc 0.605152; MC not run |
| `runs/sep_BC_cat13red_m6_0312` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.555964e-05 | 3.938042e-06 | 3.949768e-05 | 0.59483 | GF PASS; acc 0.595495; MC not run |
| `runs/sep_BC_cat13red_m6_0321` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.573659e-05 | 4.140586e-06 | 3.987717e-05 | 0.58698 | GF PASS; acc 0.586080; MC not run |
| `runs/sep_BC_cat13red_m6_1023` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.497638e-05 | 3.383695e-06 | 3.836007e-05 | 0.60527 | GF PASS; acc 0.605603; MC not run |
| `runs/sep_BC_cat13red_m6_1032` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.642207e-05 | 4.094741e-06 | 4.051681e-05 | 0.58309 | GF PASS; acc 0.583011; MC not run |
| `runs/sep_BC_cat13red_m6_1203` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.489415e-05 | 3.208436e-06 | 3.810259e-05 | 0.60891 | GF PASS; acc 0.608245; MC not run |
| `runs/sep_BC_cat13red_m6_1230` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.501158e-05 | 3.347503e-06 | 3.835908e-05 | 0.59967 | GF PASS; acc 0.599473; MC not run |
| `runs/sep_BC_cat13red_m6_1302` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.575214e-05 | 3.813489e-06 | 3.956563e-05 | 0.58472 | GF PASS; acc 0.585425; MC not run |
| `runs/sep_BC_cat13red_m6_1320` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.567682e-05 | 3.580396e-06 | 3.925722e-05 | 0.58705 | GF PASS; acc 0.587069; MC not run |
| `runs/sep_BC_cat13red_m6_2013` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.522082e-05 | 3.384854e-06 | 3.860567e-05 | 0.60527 | GF PASS; acc 0.605237; MC not run |
| `runs/sep_BC_cat13red_m6_2031` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.522082e-05 | 3.383404e-06 | 3.860422e-05 | 0.60527 | GF PASS; acc 0.605245; MC not run |
| `runs/sep_BC_cat13red_m6_2103` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.514971e-05 | 3.252662e-06 | 3.840237e-05 | 0.60527 | GF PASS; acc 0.604918; MC not run |
| `runs/sep_BC_cat13red_m6_2130` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.537768e-05 | 3.36799e-06 | 3.874567e-05 | 0.59847 | GF PASS; acc 0.597951; MC not run |
| `runs/sep_BC_cat13red_m6_2301` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.486678e-05 | 3.449709e-06 | 3.831649e-05 | 0.59808 | GF PASS; acc 0.598362; MC not run |
| `runs/sep_BC_cat13red_m6_2310` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.475602e-05 | 3.235085e-06 | 3.799111e-05 | 0.60448 | GF PASS; acc 0.603204; MC not run |
| `runs/sep_BC_cat13red_m6_3012` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.480959e-05 | 3.613727e-06 | 3.842332e-05 | 0.59649 | GF PASS; acc 0.596145; MC not run |
| `runs/sep_BC_cat13red_m6_3021` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.49869e-05 | 3.807236e-06 | 3.879413e-05 | 0.58862 | GF PASS; acc 0.588016; MC not run |
| `runs/sep_BC_cat13red_m6_3102` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.490983e-05 | 3.655755e-06 | 3.856558e-05 | 0.59058 | GF PASS; acc 0.590361; MC not run |
| `runs/sep_BC_cat13red_m6_3120` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.457895e-05 | 3.335823e-06 | 3.791478e-05 | 0.59530 | GF PASS; acc 0.595745; MC not run |
| `runs/sep_BC_cat13red_m6_3201` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.460129e-05 | 3.480543e-06 | 3.808184e-05 | 0.58979 | GF PASS; acc 0.589897; MC not run |
| `runs/sep_BC_cat13red_m6_3210` (regenerate) | BC cat13red mask=6 | 151 | 33 | 3.182639e-19 | 3.466772e-05 | 3.389767e-06 | 3.805749e-05 | 0.58979 | GF PASS; acc 0.589888; MC not run |
| `runs/sep_BC_cat3_012` (regenerate) | BC cat3 | 147 | 33 | 3.182639e-19 | 4.677223e-05 | 5.384371e-06 | 5.21566e-05 | 0.61387 | GF PASS; acc 0.613661; MC not run |
| `runs/sep_BC_cat3_021` (regenerate) | BC cat3 | 147 | 33 | 3.182639e-19 | 4.702112e-05 | 5.353402e-06 | 5.237452e-05 | 0.61387 | GF PASS; acc 0.613646; MC not run |
| `runs/sep_BC_cat3_102` (regenerate) | BC cat3 | 147 | 33 | 3.182639e-19 | 4.609715e-05 | 5.271411e-06 | 5.136856e-05 | 0.61387 | GF PASS; acc 0.613684; MC not run |
| `runs/sep_BC_cat3_120` (regenerate) | BC cat3 | 147 | 33 | 3.182639e-19 | 4.655901e-05 | 5.428469e-06 | 5.198748e-05 | 0.60898 | GF PASS; acc 0.609714; MC not run |
| `runs/sep_BC_cat3_201` (regenerate) | BC cat3 | 147 | 33 | 3.182639e-19 | 4.737632e-05 | 5.489058e-06 | 5.286537e-05 | 0.60898 | GF PASS; acc 0.609738; MC not run |
| `runs/sep_BC_cat3_210` (regenerate) | BC cat3 | 147 | 33 | 3.182639e-19 | 4.687889e-05 | 5.395243e-06 | 5.227414e-05 | 0.60898 | GF PASS; acc 0.609728; MC not run |
| `runs/sep_BC_cat3red_0123` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.511892e-05 | 2.84656e-06 | 4.796548e-05 | 0.59311 | GF PASS; acc 0.593165; MC not run |
| `runs/sep_BC_cat3red_0132` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.557789e-05 | 2.940592e-06 | 4.851848e-05 | 0.58925 | GF PASS; acc 0.589522; MC not run |
| `runs/sep_BC_cat3red_0213` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.511892e-05 | 2.844793e-06 | 4.796372e-05 | 0.59311 | GF PASS; acc 0.593160; MC not run |
| `runs/sep_BC_cat3red_0231` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.435267e-05 | 3.204605e-06 | 4.755728e-05 | 0.57991 | GF PASS; acc 0.579974; MC not run |
| `runs/sep_BC_cat3red_0312` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.297878e-05 | 3.125263e-06 | 4.610404e-05 | 0.58309 | GF PASS; acc 0.582128; MC not run |
| `runs/sep_BC_cat3red_0321` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.297878e-05 | 3.128446e-06 | 4.610722e-05 | 0.58309 | GF PASS; acc 0.582146; MC not run |
| `runs/sep_BC_cat3red_1023` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.444212e-05 | 2.85679e-06 | 4.729891e-05 | 0.59192 | GF PASS; acc 0.591280; MC not run |
| `runs/sep_BC_cat3red_1032` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.490109e-05 | 2.94793e-06 | 4.784902e-05 | 0.58807 | GF PASS; acc 0.587558; MC not run |
| `runs/sep_BC_cat3red_1203` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.454879e-05 | 2.975491e-06 | 4.752428e-05 | 0.58721 | GF PASS; acc 0.587339; MC not run |
| `runs/sep_BC_cat3red_1230` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.454879e-05 | 2.980031e-06 | 4.752882e-05 | 0.58721 | GF PASS; acc 0.587338; MC not run |
| `runs/sep_BC_cat3red_1302` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.424648e-05 | 2.863572e-06 | 4.711005e-05 | 0.59161 | GF PASS; acc 0.592189; MC not run |
| `runs/sep_BC_cat3red_1320` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.501193e-05 | 3.087021e-06 | 4.809895e-05 | 0.58378 | GF PASS; acc 0.583371; MC not run |
| `runs/sep_BC_cat3red_2013` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.444212e-05 | 2.878086e-06 | 4.732021e-05 | 0.59192 | GF PASS; acc 0.591227; MC not run |
| `runs/sep_BC_cat3red_2031` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.435267e-05 | 3.339447e-06 | 4.769212e-05 | 0.57530 | GF PASS; acc 0.575340; MC not run |
| `runs/sep_BC_cat3red_2103` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.454879e-05 | 2.98008e-06 | 4.752887e-05 | 0.58721 | GF PASS; acc 0.587327; MC not run |
| `runs/sep_BC_cat3red_2130` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.454879e-05 | 2.985304e-06 | 4.753409e-05 | 0.58721 | GF PASS; acc 0.587335; MC not run |
| `runs/sep_BC_cat3red_2301` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.433525e-05 | 3.117078e-06 | 4.745233e-05 | 0.58339 | GF PASS; acc 0.583115; MC not run |
| `runs/sep_BC_cat3red_2310` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.42466e-05 | 3.209683e-06 | 4.745628e-05 | 0.57798 | GF PASS; acc 0.577803; MC not run |
| `runs/sep_BC_cat3red_3012` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.289024e-05 | 2.916919e-06 | 4.580716e-05 | 0.59130 | GF PASS; acc 0.591171; MC not run |
| `runs/sep_BC_cat3red_3021` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.289024e-05 | 2.920058e-06 | 4.58103e-05 | 0.59130 | GF PASS; acc 0.591153; MC not run |
| `runs/sep_BC_cat3red_3102` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.273048e-05 | 2.977165e-06 | 4.570764e-05 | 0.58581 | GF PASS; acc 0.586283; MC not run |
| `runs/sep_BC_cat3red_3120` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.281913e-05 | 3.105605e-06 | 4.592474e-05 | 0.58153 | GF PASS; acc 0.581420; MC not run |
| `runs/sep_BC_cat3red_3201` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.297889e-05 | 3.020467e-06 | 4.599936e-05 | 0.58698 | GF PASS; acc 0.587168; MC not run |
| `runs/sep_BC_cat3red_3210` (regenerate) | BC cat3red | 159 | 33 | 3.182639e-19 | 4.289024e-05 | 3.10336e-06 | 4.59936e-05 | 0.58153 | GF PASS; acc 0.581420; MC not run |
| `runs/sep_BC_cat3reusered_0123` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.394021e-05 | 6.80493e-06 | 5.074514e-05 | 0.49697 | GF FAIL; acc 0.497500; MC not run |
| `runs/sep_BC_cat3reusered_0132` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.350062e-05 | 6.953143e-06 | 5.045376e-05 | 0.49802 | GF FAIL; acc 0.498157; MC not run |
| `runs/sep_BC_cat3reusered_0213` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.394021e-05 | 6.844746e-06 | 5.078495e-05 | 0.49697 | GF FAIL; acc 0.498126; MC not run |
| `runs/sep_BC_cat3reusered_0231` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.396048e-05 | 6.949175e-06 | 5.090965e-05 | 0.49802 | GF FAIL; acc 0.497407; MC not run |
| `runs/sep_BC_cat3reusered_0312` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.430091e-05 | 7.161524e-06 | 5.146243e-05 | 0.49909 | GF FAIL; acc 0.499328; MC not run |
| `runs/sep_BC_cat3reusered_0321` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.483105e-05 | 7.098654e-06 | 5.19297e-05 | 0.49909 | GF FAIL; acc 0.499083; MC not run |
| `runs/sep_BC_cat3reusered_1023` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.394021e-05 | 6.945316e-06 | 5.088552e-05 | 0.49698 | GF FAIL; acc 0.497032; MC not run |
| `runs/sep_BC_cat3reusered_1032` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.350062e-05 | 7.087585e-06 | 5.058821e-05 | 0.49803 | GF FAIL; acc 0.498156; MC not run |
| `runs/sep_BC_cat3reusered_1203` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.550169e-05 | 7.108677e-06 | 5.261037e-05 | 0.49699 | GF FAIL; acc 0.497195; MC not run |
| `runs/sep_BC_cat3reusered_1230` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.603254e-05 | 7.123269e-06 | 5.315581e-05 | 0.49697 | GF FAIL; acc 0.496937; MC not run |
| `runs/sep_BC_cat3reusered_1302` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.350062e-05 | 7.090769e-06 | 5.059139e-05 | 0.49802 | GF FAIL; acc 0.497524; MC not run |
| `runs/sep_BC_cat3reusered_1320` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.42969e-05 | 6.933669e-06 | 5.123057e-05 | 0.49802 | GF FAIL; acc 0.497793; MC not run |
| `runs/sep_BC_cat3reusered_2013` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.394021e-05 | 7.247332e-06 | 5.118754e-05 | 0.49698 | GF FAIL; acc 0.496861; MC not run |
| `runs/sep_BC_cat3reusered_2031` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.396048e-05 | 7.348494e-06 | 5.130897e-05 | 0.49803 | GF FAIL; acc 0.497322; MC not run |
| `runs/sep_BC_cat3reusered_2103` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.550169e-05 | 7.370902e-06 | 5.287259e-05 | 0.49699 | GF FAIL; acc 0.497203; MC not run |
| `runs/sep_BC_cat3reusered_2130` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.603254e-05 | 7.386349e-06 | 5.341889e-05 | 0.49697 | GF FAIL; acc 0.496912; MC not run |
| `runs/sep_BC_cat3reusered_2301` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.500147e-05 | 7.36402e-06 | 5.236549e-05 | 0.49802 | GF FAIL; acc 0.497984; MC not run |
| `runs/sep_BC_cat3reusered_2310` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.52676e-05 | 7.266753e-06 | 5.253435e-05 | 0.49802 | GF FAIL; acc 0.497885; MC not run |
| `runs/sep_BC_cat3reusered_3012` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.430091e-05 | 7.177594e-06 | 5.14785e-05 | 0.49907 | GF FAIL; acc 0.499097; MC not run |
| `runs/sep_BC_cat3reusered_3021` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.483105e-05 | 7.115896e-06 | 5.194695e-05 | 0.49907 | GF FAIL; acc 0.499651; MC not run |
| `runs/sep_BC_cat3reusered_3102` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.326062e-05 | 6.967155e-06 | 5.022778e-05 | 0.49908 | GF FAIL; acc 0.499935; MC not run |
| `runs/sep_BC_cat3reusered_3120` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.40569e-05 | 6.804913e-06 | 5.086181e-05 | 0.49909 | GF FAIL; acc 0.498930; MC not run |
| `runs/sep_BC_cat3reusered_3201` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.483105e-05 | 6.959063e-06 | 5.179011e-05 | 0.49908 | GF FAIL; acc 0.499863; MC not run |
| `runs/sep_BC_cat3reusered_3210` (regenerate) | BC cat3reusered | 159 | 33 | 3.182639e-19 | 4.509718e-05 | 6.85807e-06 | 5.195525e-05 | 0.49909 | GF FAIL; acc 0.498753; MC not run |
| `runs/sep_BC_cat3spinered_0123` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.674477e-05 | 6.801159e-06 | 5.354593e-05 | 0.49908 | GF FAIL; acc 0.498767; MC not run |
| `runs/sep_BC_cat3spinered_0132` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.647934e-05 | 6.978921e-06 | 5.345827e-05 | 0.49908 | GF FAIL; acc 0.499354; MC not run |
| `runs/sep_BC_cat3spinered_0213` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.674477e-05 | 6.516905e-06 | 5.326167e-05 | 0.49908 | GF FAIL; acc 0.499926; MC not run |
| `runs/sep_BC_cat3spinered_0231` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.701464e-05 | 6.631866e-06 | 5.36465e-05 | 0.49908 | GF PASS; acc 0.500150; MC not run |
| `runs/sep_BC_cat3spinered_0312` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.748478e-05 | 7.003483e-06 | 5.448826e-05 | 0.49908 | GF FAIL; acc 0.499250; MC not run |
| `runs/sep_BC_cat3spinered_0321` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.802007e-05 | 6.94063e-06 | 5.49607e-05 | 0.49908 | GF FAIL; acc 0.498116; MC not run |
| `runs/sep_BC_cat3spinered_1023` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.674477e-05 | 6.809925e-06 | 5.355469e-05 | 0.49908 | GF FAIL; acc 0.499352; MC not run |
| `runs/sep_BC_cat3spinered_1032` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.647934e-05 | 6.983888e-06 | 5.346323e-05 | 0.49908 | GF FAIL; acc 0.498758; MC not run |
| `runs/sep_BC_cat3spinered_1203` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.825292e-05 | 6.563177e-06 | 5.48161e-05 | 0.49908 | GF FAIL; acc 0.499259; MC not run |
| `runs/sep_BC_cat3spinered_1230` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.878821e-05 | 6.574903e-06 | 5.536312e-05 | 0.49908 | GF FAIL; acc 0.498134; MC not run |
| `runs/sep_BC_cat3spinered_1302` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.647934e-05 | 6.769247e-06 | 5.324859e-05 | 0.49908 | GF FAIL; acc 0.499939; MC not run |
| `runs/sep_BC_cat3spinered_1320` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.728006e-05 | 6.607316e-06 | 5.388738e-05 | 0.49908 | GF PASS; acc 0.500165; MC not run |
| `runs/sep_BC_cat3spinered_2013` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.674921e-05 | 6.538883e-06 | 5.32881e-05 | 0.49908 | GF PASS; acc 0.500172; MC not run |
| `runs/sep_BC_cat3spinered_2031` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.701019e-05 | 6.650832e-06 | 5.366103e-05 | 0.49908 | GF FAIL; acc 0.499968; MC not run |
| `runs/sep_BC_cat3spinered_2103` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.825736e-05 | 6.576156e-06 | 5.483352e-05 | 0.49908 | GF FAIL; acc 0.498148; MC not run |
| `runs/sep_BC_cat3spinered_2130` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.878377e-05 | 6.58908e-06 | 5.537285e-05 | 0.49908 | GF FAIL; acc 0.499240; MC not run |
| `runs/sep_BC_cat3spinered_2301` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.801563e-05 | 6.870765e-06 | 5.488639e-05 | 0.49908 | GF FAIL; acc 0.498768; MC not run |
| `runs/sep_BC_cat3spinered_2310` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.828105e-05 | 6.771435e-06 | 5.505249e-05 | 0.49908 | GF FAIL; acc 0.499323; MC not run |
| `runs/sep_BC_cat3spinered_3012` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.748922e-05 | 7.016515e-06 | 5.450574e-05 | 0.49908 | GF FAIL; acc 0.498150; MC not run |
| `runs/sep_BC_cat3spinered_3021` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.801563e-05 | 6.954754e-06 | 5.497038e-05 | 0.49908 | GF FAIL; acc 0.499220; MC not run |
| `runs/sep_BC_cat3spinered_3102` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.648379e-05 | 6.777437e-06 | 5.326123e-05 | 0.49908 | GF PASS; acc 0.500126; MC not run |
| `runs/sep_BC_cat3spinered_3120` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.727562e-05 | 6.612494e-06 | 5.388811e-05 | 0.49908 | GF FAIL; acc 0.499920; MC not run |
| `runs/sep_BC_cat3spinered_3201` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.801563e-05 | 6.865798e-06 | 5.488143e-05 | 0.49908 | GF FAIL; acc 0.499319; MC not run |
| `runs/sep_BC_cat3spinered_3210` (regenerate) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.828105e-05 | 6.762669e-06 | 5.504372e-05 | 0.49908 | GF FAIL; acc 0.498739; MC not run |
| `runs/sep_BC_cat4_012` (regenerate) | BC cat4 | 153 | 33 | 3.182639e-19 | 4.723842e-05 | 6.500154e-06 | 5.373857e-05 | 0.59288 | GF PASS; acc 0.593273; MC not run |
| `runs/sep_BC_cat4_021` (regenerate) | BC cat4 | 153 | 33 | 3.182639e-19 | 4.784251e-05 | 6.442684e-06 | 5.428519e-05 | 0.59288 | GF PASS; acc 0.593291; MC not run |
| `runs/sep_BC_cat4_102` (regenerate) | BC cat4 | 153 | 33 | 3.182639e-19 | 4.656346e-05 | 6.381974e-06 | 5.294543e-05 | 0.59288 | GF PASS; acc 0.593310; MC not run |
| `runs/sep_BC_cat4_120` (regenerate) | BC cat4 | 153 | 33 | 3.182639e-19 | 4.667024e-05 | 6.227057e-06 | 5.28973e-05 | 0.59288 | GF PASS; acc 0.592884; MC not run |
| `runs/sep_BC_cat4_201` (regenerate) | BC cat4 | 153 | 33 | 3.182639e-19 | 4.784263e-05 | 6.266435e-06 | 5.410906e-05 | 0.59288 | GF PASS; acc 0.592922; MC not run |
| `runs/sep_BC_cat4_210` (regenerate) | BC cat4 | 153 | 33 | 3.182639e-19 | 4.734509e-05 | 6.169221e-06 | 5.351431e-05 | 0.59288 | GF PASS; acc 0.592896; MC not run |
| `runs/sep_BC_cat_012` (regenerate) | BC cat | 141 | 33 | 3.182639e-19 | 4.424749e-05 | 4.332794e-06 | 4.858028e-05 | 0.62979 | GF PASS; acc 0.629265; MC not run |
| `runs/sep_BC_cat_021` (regenerate) | BC cat | 141 | 33 | 3.182639e-19 | 4.454971e-05 | 4.299491e-06 | 4.88492e-05 | 0.62979 | GF PASS; acc 0.629275; MC not run |
| `runs/sep_BC_cat_102` (regenerate) | BC cat | 141 | 33 | 3.182639e-19 | 4.357252e-05 | 4.209249e-06 | 4.778177e-05 | 0.62979 | GF PASS; acc 0.628890; MC not run |
| `runs/sep_BC_cat_120` (regenerate) | BC cat | 141 | 33 | 3.182639e-19 | 4.470467e-05 | 4.310634e-06 | 4.901531e-05 | 0.62570 | GF PASS; acc 0.625117; MC not run |
| `runs/sep_BC_cat_201` (regenerate) | BC cat | 141 | 33 | 3.182639e-19 | 4.424138e-05 | 4.461856e-06 | 4.870324e-05 | 0.62363 | GF PASS; acc 0.623482; MC not run |
| `runs/sep_BC_cat_210` (regenerate) | BC cat | 141 | 33 | 3.182639e-19 | 4.22111e-05 | 4.147433e-06 | 4.635854e-05 | 0.62821 | GF PASS; acc 0.628714; MC not run |
| `runs/sep_BC_catred_012` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.324734e-05 | 2.310957e-06 | 4.55583e-05 | 0.61281 | GF PASS; acc 0.612734; MC not run |
| `runs/sep_BC_catred_0132` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.351217e-05 | 2.282972e-06 | 4.579514e-05 | 0.61281 | GF PASS; acc 0.613246; MC not run |
| `runs/sep_BC_catred_021` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.324897e-05 | 2.304698e-06 | 4.555367e-05 | 0.61281 | GF PASS; acc 0.612455; MC not run |
| `runs/sep_BC_catred_0231` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.024281e-05 | 2.492338e-06 | 4.273514e-05 | 0.60640 | GF PASS; acc 0.605996; MC not run |
| `runs/sep_BC_catred_0312` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.061638e-05 | 2.429374e-06 | 4.304575e-05 | 0.61005 | GF PASS; acc 0.610549; MC not run |
| `runs/sep_BC_catred_0321` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.061638e-05 | 2.432291e-06 | 4.304867e-05 | 0.61005 | GF PASS; acc 0.610540; MC not run |
| `runs/sep_BC_catred_102` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.257054e-05 | 2.32382e-06 | 4.489436e-05 | 0.61158 | GF PASS; acc 0.611466; MC not run |
| `runs/sep_BC_catred_1032` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.283537e-05 | 2.294302e-06 | 4.512967e-05 | 0.61158 | GF PASS; acc 0.611204; MC not run |
| `runs/sep_BC_catred_120` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.342319e-05 | 2.444084e-06 | 4.586728e-05 | 0.60802 | GF PASS; acc 0.607819; MC not run |
| `runs/sep_BC_catred_1230` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.223421e-05 | 2.384148e-06 | 4.461836e-05 | 0.61249 | GF PASS; acc 0.612033; MC not run |
| `runs/sep_BC_catred_1302` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.283537e-05 | 2.295954e-06 | 4.513132e-05 | 0.61158 | GF PASS; acc 0.611443; MC not run |
| `runs/sep_BC_catred_1320` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.443996e-05 | 2.476898e-06 | 4.691686e-05 | 0.60640 | GF PASS; acc 0.606103; MC not run |
| `runs/sep_BC_catred_201` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.245217e-05 | 2.448585e-06 | 4.490075e-05 | 0.60721 | GF PASS; acc 0.607125; MC not run |
| `runs/sep_BC_catred_2031` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.172281e-05 | 2.659563e-06 | 4.438237e-05 | 0.59966 | GF PASS; acc 0.599065; MC not run |
| `runs/sep_BC_catred_210` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.098052e-05 | 2.39914e-06 | 4.337966e-05 | 0.61046 | GF PASS; acc 0.609948; MC not run |
| `runs/sep_BC_catred_2130` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.223584e-05 | 2.38346e-06 | 4.46193e-05 | 0.61249 | GF PASS; acc 0.611521; MC not run |
| `runs/sep_BC_catred_2301` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 3.969392e-05 | 2.463344e-06 | 4.215726e-05 | 0.61014 | GF PASS; acc 0.610226; MC not run |
| `runs/sep_BC_catred_2310` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.028269e-05 | 2.491183e-06 | 4.277387e-05 | 0.60649 | GF PASS; acc 0.606834; MC not run |
| `runs/sep_BC_catred_3012` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.163895e-05 | 2.374769e-06 | 4.401372e-05 | 0.61126 | GF PASS; acc 0.611056; MC not run |
| `runs/sep_BC_catred_3021` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.163895e-05 | 2.378103e-06 | 4.401706e-05 | 0.61126 | GF PASS; acc 0.611042; MC not run |
| `runs/sep_BC_catred_3102` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.091252e-05 | 2.3499e-06 | 4.326242e-05 | 0.60923 | GF PASS; acc 0.609495; MC not run |
| `runs/sep_BC_catred_3120` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.170713e-05 | 2.476606e-06 | 4.418374e-05 | 0.60770 | GF PASS; acc 0.607245; MC not run |
| `runs/sep_BC_catred_3201` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 4.194358e-05 | 2.570429e-06 | 4.451401e-05 | 0.60528 | GF PASS; acc 0.604564; MC not run |
| `runs/sep_BC_catred_3210` (regenerate) | BC catred | 151 | 33 | 3.182639e-19 | 3.964491e-05 | 2.438388e-06 | 4.20833e-05 | 0.61014 | GF PASS; acc 0.609650; MC not run |
| `runs/sep_BC_direct_012` (regenerate) | BC direct | 135 | 33 | 3.182639e-19 | 3.551893e-05 | 4.030243e-06 | 3.954917e-05 | 0.63010 | GF PASS; acc 0.629655; MC not run |
| `runs/sep_BC_direct_021` (regenerate) | BC direct | 135 | 33 | 3.182639e-19 | 3.61754e-05 | 4.265113e-06 | 4.044052e-05 | 0.62509 | GF PASS; acc 0.624088; MC not run |
| `runs/sep_BC_direct_102` (regenerate) | BC direct | 135 | 33 | 3.182639e-19 | 3.568805e-05 | 4.304767e-06 | 3.999282e-05 | 0.62260 | GF PASS; acc 0.622013; MC not run |
| `runs/sep_BC_direct_120` (regenerate) | BC direct | 135 | 33 | 3.182639e-19 | 3.550162e-05 | 3.901658e-06 | 3.940328e-05 | 0.62883 | GF PASS; acc 0.628351; MC not run |
| `runs/sep_BC_direct_201` (regenerate) | BC direct | 135 | 33 | 3.182639e-19 | 3.600734e-05 | 3.917438e-06 | 3.992478e-05 | 0.62883 | GF PASS; acc 0.628345; MC not run |
| `runs/sep_BC_direct_210` (regenerate) | BC direct | 135 | 33 | 3.182639e-19 | 3.59629e-05 | 3.858006e-06 | 3.98209e-05 | 0.62883 | GF PASS; acc 0.628021; MC not run |
| `runs/sep_BC_flag_012` (regenerate) | BC flag | 147 | 33 | 3.182639e-19 | 3.64928e-05 | 4.854073e-06 | 4.134687e-05 | 0.58821 | GF PASS; acc 0.587933; MC not run |
| `runs/sep_BC_flag_021` (regenerate) | BC flag | 147 | 33 | 3.182639e-19 | 3.723675e-05 | 5.134776e-06 | 4.237153e-05 | 0.58238 | GF PASS; acc 0.582291; MC not run |
| `runs/sep_BC_flag_102` (regenerate) | BC flag | 147 | 33 | 3.182639e-19 | 3.642181e-05 | 5.196638e-06 | 4.161845e-05 | 0.57892 | GF PASS; acc 0.578497; MC not run |
| `runs/sep_BC_flag_120` (regenerate) | BC flag | 147 | 33 | 3.182639e-19 | 3.643146e-05 | 4.733801e-06 | 4.116527e-05 | 0.58703 | GF PASS; acc 0.587086; MC not run |
| `runs/sep_BC_flag_201` (regenerate) | BC flag | 147 | 33 | 3.182639e-19 | 3.697174e-05 | 4.754085e-06 | 4.172582e-05 | 0.58703 | GF PASS; acc 0.587045; MC not run |
| `runs/sep_BC_flag_210` (regenerate) | BC flag | 147 | 33 | 3.182639e-19 | 3.685659e-05 | 4.695081e-06 | 4.155168e-05 | 0.58703 | GF PASS; acc 0.586848; MC not run |
| `runs/sep_BC_hybrid1_012` (regenerate) | BC hybrid1 | 133 | 33 | 3.182639e-19 | 3.562476e-05 | 4.234725e-06 | 3.985949e-05 | 0.62152 | GF PASS; acc 0.620751; MC not run |
| `runs/sep_BC_hybrid1_021` (regenerate) | BC hybrid1 | 133 | 33 | 3.182639e-19 | 3.59264e-05 | 4.196469e-06 | 4.012286e-05 | 0.62152 | GF PASS; acc 0.620409; MC not run |
| `runs/sep_BC_hybrid1_102` (regenerate) | BC hybrid1 | 133 | 33 | 3.182639e-19 | 3.562476e-05 | 4.234725e-06 | 3.985949e-05 | 0.62152 | GF PASS; acc 0.620751; MC not run |
| `runs/sep_BC_hybrid1_120` (regenerate) | BC hybrid1 | 133 | 33 | 3.182639e-19 | 3.562476e-05 | 4.234725e-06 | 3.985949e-05 | 0.62152 | GF PASS; acc 0.620751; MC not run |
| `runs/sep_BC_hybrid1_201` (regenerate) | BC hybrid1 | 133 | 33 | 3.182639e-19 | 3.59264e-05 | 4.196469e-06 | 4.012286e-05 | 0.62152 | GF PASS; acc 0.620409; MC not run |
| `runs/sep_BC_hybrid1_210` (regenerate) | BC hybrid1 | 133 | 33 | 3.182639e-19 | 3.59264e-05 | 4.196469e-06 | 4.012286e-05 | 0.62152 | GF PASS; acc 0.620409; MC not run |
| `runs/sep_BC_hybrid2_012` (regenerate) | BC hybrid2 | 131 | 33 | 3.182639e-19 | 3.479075e-05 | 3.757483e-06 | 3.854823e-05 | 0.62843 | GF PASS; acc 0.627870; MC not run |
| `runs/sep_BC_hybrid2_021` (regenerate) | BC hybrid2 | 131 | 33 | 3.182639e-19 | 3.479075e-05 | 3.757483e-06 | 3.854823e-05 | 0.62843 | GF PASS; acc 0.627870; MC not run |
| `runs/sep_BC_hybrid2_102` (regenerate) | BC hybrid2 | 131 | 33 | 3.182639e-19 | 3.479075e-05 | 3.757483e-06 | 3.854823e-05 | 0.62843 | GF PASS; acc 0.627870; MC not run |
| `runs/sep_BC_hybrid2_120` (regenerate) | BC hybrid2 | 131 | 33 | 3.182639e-19 | 3.479075e-05 | 3.757483e-06 | 3.854823e-05 | 0.62843 | GF PASS; acc 0.627870; MC not run |
| `runs/sep_BC_hybrid2_201` (regenerate) | BC hybrid2 | 131 | 33 | 3.182639e-19 | 3.479075e-05 | 3.757483e-06 | 3.854823e-05 | 0.62843 | GF PASS; acc 0.627870; MC not run |
| `runs/sep_BC_hybrid2_210` (regenerate) | BC hybrid2 | 131 | 33 | 3.182639e-19 | 3.479075e-05 | 3.757483e-06 | 3.854823e-05 | 0.62843 | GF PASS; acc 0.627870; MC not run |
| `runs/sep_BC_hybrid2t_012` (regenerate) | BC hybrid2t | 129 | 33 | 3.182639e-19 | 3.596886e-05 | 4.075987e-06 | 4.004484e-05 | 0.62346 | GF PASS; acc 0.622569; MC not run |
| `runs/sep_BC_redundant_012` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.342713e-05 | 2.633931e-06 | 3.606106e-05 | 0.61654 | GF PASS; acc 0.616064; MC not run |
| `runs/sep_BC_redundant_0132` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.37629e-05 | 3.00406e-06 | 3.676696e-05 | 0.60914 | GF PASS; acc 0.608793; MC not run |
| `runs/sep_BC_redundant_021` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.342713e-05 | 2.663021e-06 | 3.609015e-05 | 0.61163 | GF PASS; acc 0.610296; MC not run |
| `runs/sep_BC_redundant_0231` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.369063e-05 | 2.807101e-06 | 3.649773e-05 | 0.61034 | GF PASS; acc 0.609807; MC not run |
| `runs/sep_BC_redundant_0312` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.384734e-05 | 2.908472e-06 | 3.675582e-05 | 0.61394 | GF PASS; acc 0.613989; MC not run |
| `runs/sep_BC_redundant_0321` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.402382e-05 | 3.018176e-06 | 3.7042e-05 | 0.60785 | GF PASS; acc 0.607519; MC not run |
| `runs/sep_BC_redundant_102` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.362491e-05 | 2.741856e-06 | 3.636677e-05 | 0.60920 | GF PASS; acc 0.608817; MC not run |
| `runs/sep_BC_redundant_1032` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.377179e-05 | 3.005913e-06 | 3.67777e-05 | 0.60915 | GF PASS; acc 0.607706; MC not run |
| `runs/sep_BC_redundant_120` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.369327e-05 | 2.600613e-06 | 3.629388e-05 | 0.61530 | GF PASS; acc 0.614089; MC not run |
| `runs/sep_BC_redundant_1230` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.378192e-05 | 2.600365e-06 | 3.638228e-05 | 0.61530 | GF PASS; acc 0.614620; MC not run |
| `runs/sep_BC_redundant_1302` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.368361e-05 | 2.907063e-06 | 3.659067e-05 | 0.61280 | GF PASS; acc 0.612537; MC not run |
| `runs/sep_BC_redundant_1320` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.374607e-05 | 2.830399e-06 | 3.657647e-05 | 0.60791 | GF PASS; acc 0.607429; MC not run |
| `runs/sep_BC_redundant_201` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.343602e-05 | 2.601405e-06 | 3.603743e-05 | 0.61530 | GF PASS; acc 0.614889; MC not run |
| `runs/sep_BC_redundant_2031` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.369952e-05 | 2.76783e-06 | 3.646735e-05 | 0.61155 | GF PASS; acc 0.611223; MC not run |
| `runs/sep_BC_redundant_210` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.369327e-05 | 2.601985e-06 | 3.629525e-05 | 0.61531 | GF PASS; acc 0.615026; MC not run |
| `runs/sep_BC_redundant_2130` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.378192e-05 | 2.602075e-06 | 3.638399e-05 | 0.61530 | GF PASS; acc 0.615048; MC not run |
| `runs/sep_BC_redundant_2301` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.364864e-05 | 2.658983e-06 | 3.630763e-05 | 0.61646 | GF PASS; acc 0.615300; MC not run |
| `runs/sep_BC_redundant_2310` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.383321e-05 | 2.677511e-06 | 3.651072e-05 | 0.61277 | GF PASS; acc 0.612322; MC not run |
| `runs/sep_BC_redundant_3012` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.375916e-05 | 2.795525e-06 | 3.655469e-05 | 0.62010 | GF PASS; acc 0.619539; MC not run |
| `runs/sep_BC_redundant_3021` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.393576e-05 | 2.914848e-06 | 3.685061e-05 | 0.61149 | GF PASS; acc 0.610950; MC not run |
| `runs/sep_BC_redundant_3102` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.428542e-05 | 3.022642e-06 | 3.730806e-05 | 0.60785 | GF PASS; acc 0.607196; MC not run |
| `runs/sep_BC_redundant_3120` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.37594e-05 | 2.746191e-06 | 3.650559e-05 | 0.61393 | GF PASS; acc 0.613589; MC not run |
| `runs/sep_BC_redundant_3201` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.385647e-05 | 2.800245e-06 | 3.665671e-05 | 0.60904 | GF PASS; acc 0.608216; MC not run |
| `runs/sep_BC_redundant_3210` (regenerate) | BC redundant | 143 | 33 | 3.182639e-19 | 3.391881e-05 | 2.78005e-06 | 3.669886e-05 | 0.60905 | GF PASS; acc 0.608833; MC not run |
| `runs/sep_BC_redundant_m3_0123` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.402707e-05 | 2.668634e-06 | 3.669571e-05 | 0.62772 | GF PASS; acc 0.627356; MC not run |
| `runs/sep_BC_redundant_m3_0132` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.435472e-05 | 3.079977e-06 | 3.74347e-05 | 0.61738 | GF PASS; acc 0.616891; MC not run |
| `runs/sep_BC_redundant_m3_0213` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.435549e-05 | 2.737823e-06 | 3.709331e-05 | 0.62272 | GF PASS; acc 0.621845; MC not run |
| `runs/sep_BC_redundant_m3_0231` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.482921e-05 | 3.148423e-06 | 3.797763e-05 | 0.61116 | GF PASS; acc 0.610349; MC not run |
| `runs/sep_BC_redundant_m3_0312` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.452734e-05 | 3.190794e-06 | 3.771814e-05 | 0.61288 | GF PASS; acc 0.611833; MC not run |
| `runs/sep_BC_redundant_m3_0321` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.469576e-05 | 3.13871e-06 | 3.783447e-05 | 0.61166 | GF PASS; acc 0.611717; MC not run |
| `runs/sep_BC_redundant_m3_1023` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.422485e-05 | 2.764748e-06 | 3.69896e-05 | 0.62024 | GF PASS; acc 0.619685; MC not run |
| `runs/sep_BC_redundant_m3_1032` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.485202e-05 | 3.18153e-06 | 3.803355e-05 | 0.61125 | GF PASS; acc 0.611151; MC not run |
| `runs/sep_BC_redundant_m3_1203` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.436882e-05 | 2.765241e-06 | 3.713406e-05 | 0.62397 | GF PASS; acc 0.623597; MC not run |
| `runs/sep_BC_redundant_m3_1230` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.436882e-05 | 2.766514e-06 | 3.713534e-05 | 0.62397 | GF PASS; acc 0.623606; MC not run |
| `runs/sep_BC_redundant_m3_1302` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.45525e-05 | 3.143557e-06 | 3.769605e-05 | 0.61492 | GF PASS; acc 0.613809; MC not run |
| `runs/sep_BC_redundant_m3_1320` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.454607e-05 | 2.973247e-06 | 3.751931e-05 | 0.61409 | GF PASS; acc 0.614168; MC not run |
| `runs/sep_BC_redundant_m3_2013` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.493688e-05 | 2.896816e-06 | 3.78337e-05 | 0.62647 | GF PASS; acc 0.626571; MC not run |
| `runs/sep_BC_redundant_m3_2031` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.55616e-05 | 3.2755e-06 | 3.88371e-05 | 0.61239 | GF PASS; acc 0.612336; MC not run |
| `runs/sep_BC_redundant_m3_2103` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.507688e-05 | 2.955039e-06 | 3.803192e-05 | 0.62024 | GF PASS; acc 0.619653; MC not run |
| `runs/sep_BC_redundant_m3_2130` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.486577e-05 | 2.925156e-06 | 3.779093e-05 | 0.62398 | GF PASS; acc 0.623395; MC not run |
| `runs/sep_BC_redundant_m3_2301` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.49629e-05 | 3.030205e-06 | 3.79931e-05 | 0.62224 | GF PASS; acc 0.621548; MC not run |
| `runs/sep_BC_redundant_m3_2310` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.520231e-05 | 3.13598e-06 | 3.833829e-05 | 0.61402 | GF PASS; acc 0.613462; MC not run |
| `runs/sep_BC_redundant_m3_3012` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.435028e-05 | 3.015376e-06 | 3.736565e-05 | 0.62026 | GF PASS; acc 0.619759; MC not run |
| `runs/sep_BC_redundant_m3_3021` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.469576e-05 | 3.138551e-06 | 3.783431e-05 | 0.61165 | GF PASS; acc 0.611099; MC not run |
| `runs/sep_BC_redundant_m3_3102` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.467028e-05 | 3.289472e-06 | 3.795975e-05 | 0.60720 | GF PASS; acc 0.607565; MC not run |
| `runs/sep_BC_redundant_m3_3120` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.454162e-05 | 2.978675e-06 | 3.75203e-05 | 0.61328 | GF PASS; acc 0.613607; MC not run |
| `runs/sep_BC_redundant_m3_3201` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.481623e-05 | 3.056298e-06 | 3.787253e-05 | 0.61327 | GF PASS; acc 0.612658; MC not run |
| `runs/sep_BC_redundant_m3_3210` (regenerate) | BC redundant mask=3 | 143 | 33 | 3.182639e-19 | 3.486968e-05 | 3.03577e-06 | 3.790545e-05 | 0.61328 | GF PASS; acc 0.612914; MC not run |
| `runs/sep_BC_redundant_m5_0123` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.325433e-05 | 2.80563e-06 | 3.605996e-05 | 0.62772 | GF PASS; acc 0.626500; MC not run |
| `runs/sep_BC_redundant_m5_0132` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.559789e-05 | 3.681699e-06 | 3.927959e-05 | 0.60392 | GF PASS; acc 0.602669; MC not run |
| `runs/sep_BC_redundant_m5_0213` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.349433e-05 | 2.871932e-06 | 3.636626e-05 | 0.62024 | GF PASS; acc 0.620513; MC not run |
| `runs/sep_BC_redundant_m5_0231` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.387472e-05 | 3.185553e-06 | 3.706027e-05 | 0.61246 | GF PASS; acc 0.611610; MC not run |
| `runs/sep_BC_redundant_m5_0312` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.446462e-05 | 3.278015e-06 | 3.774263e-05 | 0.61533 | GF PASS; acc 0.614753; MC not run |
| `runs/sep_BC_redundant_m5_0321` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.486296e-05 | 3.466754e-06 | 3.832972e-05 | 0.60923 | GF PASS; acc 0.608031; MC not run |
| `runs/sep_BC_redundant_m5_1023` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.363211e-05 | 3.150064e-06 | 3.678217e-05 | 0.62025 | GF PASS; acc 0.620136; MC not run |
| `runs/sep_BC_redundant_m5_1032` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.599887e-05 | 3.866049e-06 | 3.986492e-05 | 0.60393 | GF PASS; acc 0.603452; MC not run |
| `runs/sep_BC_redundant_m5_1203` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.342989e-05 | 2.963803e-06 | 3.639369e-05 | 0.62397 | GF PASS; acc 0.623257; MC not run |
| `runs/sep_BC_redundant_m5_1230` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.342989e-05 | 2.964981e-06 | 3.639487e-05 | 0.62397 | GF PASS; acc 0.623224; MC not run |
| `runs/sep_BC_redundant_m5_1302` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.464716e-05 | 3.579953e-06 | 3.822712e-05 | 0.61119 | GF PASS; acc 0.610795; MC not run |
| `runs/sep_BC_redundant_m5_1320` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.47407e-05 | 3.560908e-06 | 3.830161e-05 | 0.60430 | GF PASS; acc 0.603799; MC not run |
| `runs/sep_BC_redundant_m5_2013` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.368322e-05 | 2.841435e-06 | 3.652466e-05 | 0.62024 | GF PASS; acc 0.620319; MC not run |
| `runs/sep_BC_redundant_m5_2031` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.431872e-05 | 3.087249e-06 | 3.740597e-05 | 0.61736 | GF PASS; acc 0.616925; MC not run |
| `runs/sep_BC_redundant_m5_2103` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.372766e-05 | 2.917631e-06 | 3.66453e-05 | 0.62024 | GF PASS; acc 0.619885; MC not run |
| `runs/sep_BC_redundant_m5_2130` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.372766e-05 | 2.919178e-06 | 3.664684e-05 | 0.62024 | GF PASS; acc 0.619882; MC not run |
| `runs/sep_BC_redundant_m5_2301` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.369753e-05 | 2.922895e-06 | 3.662043e-05 | 0.62231 | GF PASS; acc 0.621445; MC not run |
| `runs/sep_BC_redundant_m5_2310` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.379051e-05 | 3.029634e-06 | 3.682014e-05 | 0.61286 | GF PASS; acc 0.611569; MC not run |
| `runs/sep_BC_redundant_m5_3012` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.375472e-05 | 3.109852e-06 | 3.686457e-05 | 0.62026 | GF PASS; acc 0.619759; MC not run |
| `runs/sep_BC_redundant_m5_3021` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.415342e-05 | 3.286638e-06 | 3.744006e-05 | 0.61410 | GF PASS; acc 0.613246; MC not run |
| `runs/sep_BC_redundant_m5_3102` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.395916e-05 | 3.438912e-06 | 3.739808e-05 | 0.60963 | GF PASS; acc 0.609225; MC not run |
| `runs/sep_BC_redundant_m5_3120` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.375051e-05 | 3.154976e-06 | 3.690549e-05 | 0.61328 | GF PASS; acc 0.613007; MC not run |
| `runs/sep_BC_redundant_m5_3201` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.396758e-05 | 3.120223e-06 | 3.70878e-05 | 0.60961 | GF PASS; acc 0.608807; MC not run |
| `runs/sep_BC_redundant_m5_3210` (regenerate) | BC redundant mask=5 | 143 | 33 | 3.182639e-19 | 3.388325e-05 | 3.103536e-06 | 3.698679e-05 | 0.60840 | GF PASS; acc 0.607864; MC not run |
| `runs/sep_BC_redundant_m6_0123` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.469285e-05 | 3.210035e-06 | 3.790289e-05 | 0.62772 | GF PASS; acc 0.627533; MC not run |
| `runs/sep_BC_redundant_m6_0132` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.729346e-05 | 4.169902e-06 | 4.146336e-05 | 0.60434 | GF PASS; acc 0.604144; MC not run |
| `runs/sep_BC_redundant_m6_0213` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.516992e-05 | 3.445874e-06 | 3.86158e-05 | 0.62025 | GF PASS; acc 0.619263; MC not run |
| `runs/sep_BC_redundant_m6_0231` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.516992e-05 | 3.445513e-06 | 3.861543e-05 | 0.62025 | GF PASS; acc 0.619273; MC not run |
| `runs/sep_BC_redundant_m6_0312` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.557517e-05 | 3.776222e-06 | 3.935139e-05 | 0.61280 | GF PASS; acc 0.612643; MC not run |
| `runs/sep_BC_redundant_m6_0321` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.58403e-05 | 3.955564e-06 | 3.979587e-05 | 0.60471 | GF PASS; acc 0.604637; MC not run |
| `runs/sep_BC_redundant_m6_1023` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.472642e-05 | 3.147524e-06 | 3.787395e-05 | 0.62024 | GF PASS; acc 0.619937; MC not run |
| `runs/sep_BC_redundant_m6_1032` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.64376e-05 | 3.922373e-06 | 4.035997e-05 | 0.60312 | GF PASS; acc 0.602728; MC not run |
| `runs/sep_BC_redundant_m6_1203` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.464444e-05 | 2.981331e-06 | 3.762577e-05 | 0.62396 | GF PASS; acc 0.623636; MC not run |
| `runs/sep_BC_redundant_m6_1230` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.47621e-05 | 3.120481e-06 | 3.788258e-05 | 0.62108 | GF PASS; acc 0.620991; MC not run |
| `runs/sep_BC_redundant_m6_1302` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.576814e-05 | 3.665513e-06 | 3.943366e-05 | 0.60600 | GF PASS; acc 0.605704; MC not run |
| `runs/sep_BC_redundant_m6_1320` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.578171e-05 | 3.455759e-06 | 3.923747e-05 | 0.60963 | GF PASS; acc 0.608608; MC not run |
| `runs/sep_BC_redundant_m6_2013` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.497087e-05 | 3.15453e-06 | 3.81254e-05 | 0.62024 | GF PASS; acc 0.619286; MC not run |
| `runs/sep_BC_redundant_m6_2031` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.497087e-05 | 3.154008e-06 | 3.812488e-05 | 0.62024 | GF PASS; acc 0.619273; MC not run |
| `runs/sep_BC_redundant_m6_2103` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.489999e-05 | 3.015916e-06 | 3.791591e-05 | 0.62024 | GF PASS; acc 0.619155; MC not run |
| `runs/sep_BC_redundant_m6_2130` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.51282e-05 | 3.15748e-06 | 3.828568e-05 | 0.61736 | GF PASS; acc 0.616928; MC not run |
| `runs/sep_BC_redundant_m6_2301` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.461706e-05 | 3.176873e-06 | 3.779393e-05 | 0.61778 | GF PASS; acc 0.617088; MC not run |
| `runs/sep_BC_redundant_m6_2310` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.450654e-05 | 3.027671e-06 | 3.753421e-05 | 0.62231 | GF PASS; acc 0.621440; MC not run |
| `runs/sep_BC_redundant_m6_3012` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.482559e-05 | 3.445126e-06 | 3.827072e-05 | 0.61451 | GF PASS; acc 0.613806; MC not run |
| `runs/sep_BC_redundant_m6_3021` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.509108e-05 | 3.616046e-06 | 3.870712e-05 | 0.60639 | GF PASS; acc 0.606422; MC not run |
| `runs/sep_BC_redundant_m6_3102` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.492583e-05 | 3.521065e-06 | 3.84469e-05 | 0.61085 | GF PASS; acc 0.609917; MC not run |
| `runs/sep_BC_redundant_m6_3120` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.468384e-05 | 3.210551e-06 | 3.78944e-05 | 0.61573 | GF PASS; acc 0.615551; MC not run |
| `runs/sep_BC_redundant_m6_3201` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.479425e-05 | 3.308233e-06 | 3.810248e-05 | 0.60881 | GF PASS; acc 0.607891; MC not run |
| `runs/sep_BC_redundant_m6_3210` (regenerate) | BC redundant mask=6 | 143 | 33 | 3.182639e-19 | 3.486091e-05 | 3.241804e-06 | 3.810272e-05 | 0.61003 | GF PASS; acc 0.609934; MC not run |
| `runs/sep_BC_seq_012` (regenerate) | BC seq | 135 | 33 | 3.182639e-19 | 3.781023e-05 | 7.121011e-06 | 4.493125e-05 | 0.57281 | GF PASS; acc 0.572481; MC not run |
| `runs/sep_BC_seq_021` (regenerate) | BC seq | 135 | 33 | 3.182639e-19 | 3.881708e-05 | 7.001117e-06 | 4.581819e-05 | 0.57281 | GF PASS; acc 0.572826; MC not run |
| `runs/sep_BC_seq_102` (regenerate) | BC seq | 135 | 33 | 3.182639e-19 | 3.577269e-05 | 6.708041e-06 | 4.248073e-05 | 0.57281 | GF PASS; acc 0.572816; MC not run |
| `runs/sep_BC_seq_120` (regenerate) | BC seq | 135 | 33 | 3.182639e-19 | 3.753395e-05 | 6.462473e-06 | 4.399643e-05 | 0.57167 | GF PASS; acc 0.571401; MC not run |
| `runs/sep_BC_seq_201` (regenerate) | BC seq | 135 | 33 | 3.182639e-19 | 3.900268e-05 | 6.485451e-06 | 4.548813e-05 | 0.57167 | GF PASS; acc 0.572135; MC not run |
| `runs/sep_BC_seq_210` (regenerate) | BC seq | 135 | 33 | 3.182639e-19 | 3.957898e-05 | 6.292344e-06 | 4.587132e-05 | 0.57168 | GF PASS; acc 0.570741; MC not run |
| `runs/sep_B_cat13_012` (regenerate) | B cat13 | 135 | 33 | 3.182639e-19 | 3.461009e-05 | 3.178741e-06 | 3.778884e-05 | 0.64759 | GF PASS; acc 0.647104; MC not run |
| `runs/sep_B_cat13_021` (regenerate) | B cat13 | 135 | 33 | 3.182639e-19 | 3.494301e-05 | 3.284794e-06 | 3.822781e-05 | 0.64501 | GF PASS; acc 0.644721; MC not run |
| `runs/sep_B_cat13_102` (regenerate) | B cat13 | 135 | 33 | 3.182639e-19 | 3.455021e-05 | 3.291898e-06 | 3.784211e-05 | 0.64372 | GF PASS; acc 0.642348; MC not run |
| `runs/sep_B_cat13_120` (regenerate) | B cat13 | 135 | 33 | 3.182639e-19 | 3.459688e-05 | 3.111554e-06 | 3.770843e-05 | 0.64694 | GF PASS; acc 0.646121; MC not run |
| `runs/sep_B_cat13_201` (regenerate) | B cat13 | 135 | 33 | 3.182639e-19 | 3.485886e-05 | 3.120054e-06 | 3.797892e-05 | 0.64694 | GF PASS; acc 0.646126; MC not run |
| `runs/sep_B_cat13_210` (regenerate) | B cat13 | 135 | 33 | 3.182639e-19 | 3.483208e-05 | 3.088652e-06 | 3.792073e-05 | 0.64694 | GF PASS; acc 0.646328; MC not run |
| `runs/sep_B_cat13red_012` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.319706e-05 | 2.263458e-06 | 3.546051e-05 | 0.63499 | GF PASS; acc 0.634814; MC not run |
| `runs/sep_B_cat13red_0132` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.309507e-05 | 2.243572e-06 | 3.533864e-05 | 0.63410 | GF PASS; acc 0.633450; MC not run |
| `runs/sep_B_cat13red_021` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.319706e-05 | 2.272075e-06 | 3.546913e-05 | 0.63246 | GF PASS; acc 0.632063; MC not run |
| `runs/sep_B_cat13red_0231` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.317489e-05 | 2.227162e-06 | 3.540206e-05 | 0.63136 | GF PASS; acc 0.630804; MC not run |
| `runs/sep_B_cat13red_0312` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.313063e-05 | 2.187902e-06 | 3.531853e-05 | 0.63321 | GF PASS; acc 0.632643; MC not run |
| `runs/sep_B_cat13red_0321` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.313063e-05 | 2.185914e-06 | 3.531654e-05 | 0.63321 | GF PASS; acc 0.632950; MC not run |
| `runs/sep_B_cat13red_102` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.322372e-05 | 2.302885e-06 | 3.552661e-05 | 0.63120 | GF PASS; acc 0.629954; MC not run |
| `runs/sep_B_cat13red_1032` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.309952e-05 | 2.243468e-06 | 3.534298e-05 | 0.63410 | GF PASS; acc 0.633039; MC not run |
| `runs/sep_B_cat13red_120` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.332346e-05 | 2.248928e-06 | 3.557239e-05 | 0.63435 | GF PASS; acc 0.634040; MC not run |
| `runs/sep_B_cat13red_1230` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.336778e-05 | 2.2524e-06 | 3.562018e-05 | 0.63351 | GF PASS; acc 0.633484; MC not run |
| `runs/sep_B_cat13red_1302` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.309952e-05 | 2.271642e-06 | 3.537116e-05 | 0.63179 | GF PASS; acc 0.631517; MC not run |
| `runs/sep_B_cat13red_1320` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.316823e-05 | 2.231227e-06 | 3.539945e-05 | 0.63304 | GF PASS; acc 0.632608; MC not run |
| `runs/sep_B_cat13red_201` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.319928e-05 | 2.249042e-06 | 3.544832e-05 | 0.63435 | GF PASS; acc 0.633057; MC not run |
| `runs/sep_B_cat13red_2031` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.317712e-05 | 2.203131e-06 | 3.538025e-05 | 0.63325 | GF PASS; acc 0.632170; MC not run |
| `runs/sep_B_cat13red_210` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.332346e-05 | 2.250062e-06 | 3.557352e-05 | 0.63435 | GF PASS; acc 0.633677; MC not run |
| `runs/sep_B_cat13red_2130` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.336778e-05 | 2.253839e-06 | 3.562162e-05 | 0.63351 | GF PASS; acc 0.632860; MC not run |
| `runs/sep_B_cat13red_2301` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.325694e-05 | 2.202787e-06 | 3.545973e-05 | 0.63283 | GF PASS; acc 0.631757; MC not run |
| `runs/sep_B_cat13red_2310` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.332787e-05 | 2.203694e-06 | 3.553157e-05 | 0.63283 | GF PASS; acc 0.632226; MC not run |
| `runs/sep_B_cat13red_3012` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.313063e-05 | 2.184363e-06 | 3.531499e-05 | 0.63322 | GF PASS; acc 0.632679; MC not run |
| `runs/sep_B_cat13red_3021` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.313063e-05 | 2.198333e-06 | 3.532896e-05 | 0.63069 | GF PASS; acc 0.631086; MC not run |
| `runs/sep_B_cat13red_3102` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.312174e-05 | 2.215296e-06 | 3.533703e-05 | 0.62944 | GF PASS; acc 0.628864; MC not run |
| `runs/sep_B_cat13red_3120` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.316823e-05 | 2.164245e-06 | 3.533247e-05 | 0.63258 | GF PASS; acc 0.631927; MC not run |
| `runs/sep_B_cat13red_3201` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.313285e-05 | 2.162603e-06 | 3.529545e-05 | 0.63258 | GF PASS; acc 0.631949; MC not run |
| `runs/sep_B_cat13red_3210` (regenerate) | B cat13red | 140 | 33 | 3.182639e-19 | 3.320378e-05 | 2.16267e-06 | 3.536645e-05 | 0.63258 | GF PASS; acc 0.632175; MC not run |
| `runs/sep_B_cat3_012` (regenerate) | B cat3 | 138 | 33 | 3.182639e-19 | 3.544814e-05 | 3.547206e-06 | 3.899534e-05 | 0.64267 | GF PASS; acc 0.642265; MC not run |
| `runs/sep_B_cat3_021` (regenerate) | B cat3 | 138 | 33 | 3.182639e-19 | 3.557258e-05 | 3.531995e-06 | 3.910458e-05 | 0.64267 | GF PASS; acc 0.642263; MC not run |
| `runs/sep_B_cat3_102` (regenerate) | B cat3 | 138 | 33 | 3.182639e-19 | 3.51106e-05 | 3.480421e-06 | 3.859102e-05 | 0.64267 | GF PASS; acc 0.642268; MC not run |
| `runs/sep_B_cat3_120` (regenerate) | B cat3 | 138 | 33 | 3.182639e-19 | 3.534153e-05 | 3.516425e-06 | 3.885796e-05 | 0.64011 | GF PASS; acc 0.639760; MC not run |
| `runs/sep_B_cat3_201` (regenerate) | B cat3 | 138 | 33 | 3.182639e-19 | 3.575018e-05 | 3.558564e-06 | 3.930875e-05 | 0.64011 | GF PASS; acc 0.639741; MC not run |
| `runs/sep_B_cat3_210` (regenerate) | B cat3 | 138 | 33 | 3.182639e-19 | 3.550147e-05 | 3.500036e-06 | 3.900151e-05 | 0.64011 | GF PASS; acc 0.639751; MC not run |
| `runs/sep_B_cat3red_0123` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.332174e-05 | 2.188626e-06 | 3.551036e-05 | 0.63171 | GF PASS; acc 0.630980; MC not run |
| `runs/sep_B_cat3red_0132` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.335723e-05 | 2.20846e-06 | 3.556569e-05 | 0.62966 | GF PASS; acc 0.629262; MC not run |
| `runs/sep_B_cat3red_0213` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.332174e-05 | 2.187634e-06 | 3.550937e-05 | 0.63171 | GF PASS; acc 0.630981; MC not run |
| `runs/sep_B_cat3red_0231` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.340811e-05 | 2.295657e-06 | 3.570377e-05 | 0.62465 | GF PASS; acc 0.624258; MC not run |
| `runs/sep_B_cat3red_0312` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.345697e-05 | 2.301726e-06 | 3.575869e-05 | 0.62635 | GF PASS; acc 0.625842; MC not run |
| `runs/sep_B_cat3red_0321` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.345697e-05 | 2.303421e-06 | 3.576039e-05 | 0.62635 | GF PASS; acc 0.625839; MC not run |
| `runs/sep_B_cat3red_1023` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.332174e-05 | 2.193457e-06 | 3.55152e-05 | 0.63108 | GF PASS; acc 0.630874; MC not run |
| `runs/sep_B_cat3red_1032` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.335723e-05 | 2.212627e-06 | 3.556986e-05 | 0.62903 | GF PASS; acc 0.628184; MC not run |
| `runs/sep_B_cat3red_1203` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.337507e-05 | 2.210103e-06 | 3.558518e-05 | 0.62856 | GF PASS; acc 0.627707; MC not run |
| `runs/sep_B_cat3red_1230` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.337507e-05 | 2.207609e-06 | 3.558268e-05 | 0.62856 | GF PASS; acc 0.627695; MC not run |
| `runs/sep_B_cat3red_1302` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.335723e-05 | 2.199843e-06 | 3.555708e-05 | 0.63091 | GF PASS; acc 0.629958; MC not run |
| `runs/sep_B_cat3red_1320` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.340156e-05 | 2.241568e-06 | 3.564313e-05 | 0.62673 | GF PASS; acc 0.626050; MC not run |
| `runs/sep_B_cat3red_2013` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.332174e-05 | 2.194257e-06 | 3.5516e-05 | 0.63108 | GF PASS; acc 0.630756; MC not run |
| `runs/sep_B_cat3red_2031` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.340811e-05 | 2.313772e-06 | 3.572188e-05 | 0.62216 | GF PASS; acc 0.621838; MC not run |
| `runs/sep_B_cat3red_2103` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.337507e-05 | 2.211978e-06 | 3.558705e-05 | 0.62856 | GF PASS; acc 0.627708; MC not run |
| `runs/sep_B_cat3red_2130` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.337507e-05 | 2.209826e-06 | 3.55849e-05 | 0.62856 | GF PASS; acc 0.627691; MC not run |
| `runs/sep_B_cat3red_2301` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.33994e-05 | 2.257806e-06 | 3.56572e-05 | 0.62652 | GF PASS; acc 0.626019; MC not run |
| `runs/sep_B_cat3red_2310` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.335507e-05 | 2.264251e-06 | 3.561932e-05 | 0.62361 | GF PASS; acc 0.622886; MC not run |
| `runs/sep_B_cat3red_3012` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.34127e-05 | 2.246119e-06 | 3.565882e-05 | 0.63075 | GF PASS; acc 0.630141; MC not run |
| `runs/sep_B_cat3red_3021` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.34127e-05 | 2.247791e-06 | 3.566049e-05 | 0.63075 | GF PASS; acc 0.630147; MC not run |
| `runs/sep_B_cat3red_3102` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.333282e-05 | 2.241204e-06 | 3.557402e-05 | 0.62781 | GF PASS; acc 0.626218; MC not run |
| `runs/sep_B_cat3red_3120` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.337715e-05 | 2.273636e-06 | 3.565078e-05 | 0.62552 | GF PASS; acc 0.625151; MC not run |
| `runs/sep_B_cat3red_3201` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.345703e-05 | 2.267114e-06 | 3.572414e-05 | 0.62844 | GF PASS; acc 0.628344; MC not run |
| `runs/sep_B_cat3red_3210` (regenerate) | B cat3red | 144 | 33 | 3.182639e-19 | 3.34127e-05 | 2.271809e-06 | 3.568451e-05 | 0.62552 | GF PASS; acc 0.625151; MC not run |
| `runs/sep_B_cat3reusered_0123` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.369768e-05 | 3.037172e-06 | 3.673486e-05 | 0.57826 | GF PASS; acc 0.577848; MC not run |
| `runs/sep_B_cat3reusered_0132` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.360011e-05 | 3.134453e-06 | 3.673457e-05 | 0.57887 | GF PASS; acc 0.579353; MC not run |
| `runs/sep_B_cat3reusered_0213` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.369768e-05 | 2.996903e-06 | 3.669459e-05 | 0.57826 | GF PASS; acc 0.577909; MC not run |
| `runs/sep_B_cat3reusered_0231` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.382782e-05 | 3.062334e-06 | 3.689015e-05 | 0.57887 | GF PASS; acc 0.578319; MC not run |
| `runs/sep_B_cat3reusered_0312` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.411803e-05 | 3.256873e-06 | 3.737491e-05 | 0.57948 | GF PASS; acc 0.579247; MC not run |
| `runs/sep_B_cat3reusered_0321` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.438311e-05 | 3.221539e-06 | 3.760464e-05 | 0.57948 | GF PASS; acc 0.579033; MC not run |
| `runs/sep_B_cat3reusered_1023` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.369768e-05 | 3.039194e-06 | 3.673688e-05 | 0.57826 | GF PASS; acc 0.578209; MC not run |
| `runs/sep_B_cat3reusered_1032` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.360011e-05 | 3.136313e-06 | 3.673643e-05 | 0.57887 | GF PASS; acc 0.578569; MC not run |
| `runs/sep_B_cat3reusered_1203` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.447843e-05 | 3.018938e-06 | 3.749736e-05 | 0.57826 | GF PASS; acc 0.578158; MC not run |
| `runs/sep_B_cat3reusered_1230` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.474385e-05 | 3.022135e-06 | 3.776599e-05 | 0.57826 | GF PASS; acc 0.577798; MC not run |
| `runs/sep_B_cat3reusered_1302` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.360011e-05 | 3.124594e-06 | 3.672471e-05 | 0.57886 | GF PASS; acc 0.578076; MC not run |
| `runs/sep_B_cat3reusered_1320` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.399825e-05 | 3.037727e-06 | 3.703598e-05 | 0.57887 | GF PASS; acc 0.578157; MC not run |
| `runs/sep_B_cat3reusered_2013` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.369768e-05 | 3.001665e-06 | 3.669935e-05 | 0.57826 | GF PASS; acc 0.577803; MC not run |
| `runs/sep_B_cat3reusered_2031` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.382782e-05 | 3.066526e-06 | 3.689435e-05 | 0.57887 | GF PASS; acc 0.578068; MC not run |
| `runs/sep_B_cat3reusered_2103` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.447843e-05 | 3.021666e-06 | 3.750009e-05 | 0.57826 | GF PASS; acc 0.578167; MC not run |
| `runs/sep_B_cat3reusered_2130` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.474385e-05 | 3.024739e-06 | 3.776859e-05 | 0.57826 | GF PASS; acc 0.577784; MC not run |
| `runs/sep_B_cat3reusered_2301` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.434831e-05 | 3.05783e-06 | 3.740614e-05 | 0.57886 | GF PASS; acc 0.578910; MC not run |
| `runs/sep_B_cat3reusered_2310` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.448138e-05 | 3.005762e-06 | 3.748714e-05 | 0.57887 | GF PASS; acc 0.578159; MC not run |
| `runs/sep_B_cat3reusered_3012` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.411803e-05 | 3.234826e-06 | 3.735286e-05 | 0.57947 | GF PASS; acc 0.578995; MC not run |
| `runs/sep_B_cat3reusered_3021` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.438311e-05 | 3.199525e-06 | 3.758263e-05 | 0.57947 | GF PASS; acc 0.579196; MC not run |
| `runs/sep_B_cat3reusered_3102` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.359789e-05 | 3.11116e-06 | 3.670905e-05 | 0.57948 | GF PASS; acc 0.579498; MC not run |
| `runs/sep_B_cat3reusered_3120` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.399603e-05 | 3.024157e-06 | 3.702019e-05 | 0.57948 | GF PASS; acc 0.579738; MC not run |
| `runs/sep_B_cat3reusered_3201` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.438311e-05 | 3.039146e-06 | 3.742225e-05 | 0.57948 | GF PASS; acc 0.579301; MC not run |
| `runs/sep_B_cat3reusered_3210` (regenerate) | B cat3reusered | 144 | 33 | 3.182639e-19 | 3.451617e-05 | 2.986947e-06 | 3.750312e-05 | 0.57948 | GF PASS; acc 0.579029; MC not run |
| `runs/sep_B_cat3spinered_0123` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.365996e-05 | 2.982597e-06 | 3.664256e-05 | 0.57948 | GF PASS; acc 0.579318; MC not run |
| `runs/sep_B_cat3spinered_0132` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.352725e-05 | 3.07368e-06 | 3.660093e-05 | 0.57948 | GF PASS; acc 0.578896; MC not run |
| `runs/sep_B_cat3spinered_0213` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.365774e-05 | 2.942476e-06 | 3.660022e-05 | 0.57948 | GF PASS; acc 0.579060; MC not run |
| `runs/sep_B_cat3spinered_0231` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.379046e-05 | 2.996066e-06 | 3.678652e-05 | 0.57948 | GF PASS; acc 0.579336; MC not run |
| `runs/sep_B_cat3spinered_0312` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.402997e-05 | 3.181969e-06 | 3.721194e-05 | 0.57948 | GF PASS; acc 0.579257; MC not run |
| `runs/sep_B_cat3spinered_0321` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.429317e-05 | 3.14386e-06 | 3.743703e-05 | 0.57948 | GF PASS; acc 0.578276; MC not run |
| `runs/sep_B_cat3spinered_1023` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.365996e-05 | 2.984253e-06 | 3.664422e-05 | 0.57948 | GF PASS; acc 0.578933; MC not run |
| `runs/sep_B_cat3spinered_1032` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.352725e-05 | 3.074702e-06 | 3.660195e-05 | 0.57948 | GF PASS; acc 0.579319; MC not run |
| `runs/sep_B_cat3spinered_1203` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.441404e-05 | 2.964863e-06 | 3.73789e-05 | 0.57948 | GF PASS; acc 0.579288; MC not run |
| `runs/sep_B_cat3spinered_1230` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.467724e-05 | 2.968428e-06 | 3.764567e-05 | 0.57948 | GF PASS; acc 0.578305; MC not run |
| `runs/sep_B_cat3spinered_1302` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.352947e-05 | 3.063124e-06 | 3.65926e-05 | 0.57948 | GF PASS; acc 0.579078; MC not run |
| `runs/sep_B_cat3spinered_1320` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.392317e-05 | 2.976312e-06 | 3.689948e-05 | 0.57948 | GF PASS; acc 0.579329; MC not run |
| `runs/sep_B_cat3spinered_2013` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.36533e-05 | 2.947076e-06 | 3.660037e-05 | 0.57948 | GF PASS; acc 0.579314; MC not run |
| `runs/sep_B_cat3spinered_2031` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.378601e-05 | 3.000294e-06 | 3.67863e-05 | 0.57948 | GF PASS; acc 0.579075; MC not run |
| `runs/sep_B_cat3spinered_2103` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.441182e-05 | 2.967786e-06 | 3.73796e-05 | 0.57948 | GF PASS; acc 0.578314; MC not run |
| `runs/sep_B_cat3spinered_2130` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.467502e-05 | 2.971734e-06 | 3.764675e-05 | 0.57948 | GF PASS; acc 0.579285; MC not run |
| `runs/sep_B_cat3spinered_2301` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.429095e-05 | 2.991356e-06 | 3.728231e-05 | 0.57948 | GF PASS; acc 0.579330; MC not run |
| `runs/sep_B_cat3spinered_2310` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.442366e-05 | 2.942047e-06 | 3.736571e-05 | 0.57948 | GF PASS; acc 0.578925; MC not run |
| `runs/sep_B_cat3spinered_3012` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.402775e-05 | 3.159815e-06 | 3.718756e-05 | 0.57948 | GF PASS; acc 0.578282; MC not run |
| `runs/sep_B_cat3spinered_3021` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.429095e-05 | 3.122019e-06 | 3.741297e-05 | 0.57948 | GF PASS; acc 0.579268; MC not run |
| `runs/sep_B_cat3spinered_3102` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.352947e-05 | 3.039875e-06 | 3.656935e-05 | 0.57948 | GF PASS; acc 0.579313; MC not run |
| `runs/sep_B_cat3spinered_3120` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.392317e-05 | 2.952689e-06 | 3.687586e-05 | 0.57948 | GF PASS; acc 0.579049; MC not run |
| `runs/sep_B_cat3spinered_3201` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.429095e-05 | 2.965118e-06 | 3.725607e-05 | 0.57948 | GF PASS; acc 0.578918; MC not run |
| `runs/sep_B_cat3spinered_3210` (regenerate) | B cat3spinered | 144 | 33 | 3.182639e-19 | 3.442366e-05 | 2.915213e-06 | 3.733887e-05 | 0.57948 | GF PASS; acc 0.579311; MC not run |
| `runs/sep_B_cat4_012` (regenerate) | B cat4 | 141 | 33 | 3.182639e-19 | 3.582346e-05 | 3.971716e-06 | 3.979517e-05 | 0.63159 | GF PASS; acc 0.631158; MC not run |
| `runs/sep_B_cat4_021` (regenerate) | B cat4 | 141 | 33 | 3.182639e-19 | 3.61255e-05 | 3.940091e-06 | 4.006559e-05 | 0.63159 | GF PASS; acc 0.631163; MC not run |
| `runs/sep_B_cat4_102` (regenerate) | B cat4 | 141 | 33 | 3.182639e-19 | 3.548598e-05 | 3.904718e-06 | 3.939069e-05 | 0.63159 | GF PASS; acc 0.631151; MC not run |
| `runs/sep_B_cat4_120` (regenerate) | B cat4 | 141 | 33 | 3.182639e-19 | 3.553937e-05 | 3.815333e-06 | 3.93547e-05 | 0.63159 | GF PASS; acc 0.631238; MC not run |
| `runs/sep_B_cat4_201` (regenerate) | B cat4 | 141 | 33 | 3.182639e-19 | 3.612556e-05 | 3.840333e-06 | 3.996589e-05 | 0.63159 | GF PASS; acc 0.631229; MC not run |
| `runs/sep_B_cat4_210` (regenerate) | B cat4 | 141 | 33 | 3.182639e-19 | 3.587679e-05 | 3.782551e-06 | 3.965934e-05 | 0.63159 | GF PASS; acc 0.631226; MC not run |
| `runs/sep_B_cat_012` (regenerate) | B cat | 135 | 33 | 3.182639e-19 | 3.494577e-05 | 3.154896e-06 | 3.810066e-05 | 0.65095 | GF PASS; acc 0.650637; MC not run |
| `runs/sep_B_cat_021` (regenerate) | B cat | 135 | 33 | 3.182639e-19 | 3.511243e-05 | 3.13777e-06 | 3.82502e-05 | 0.65095 | GF PASS; acc 0.650645; MC not run |
| `runs/sep_B_cat_102` (regenerate) | B cat | 135 | 33 | 3.182639e-19 | 3.460829e-05 | 3.087298e-06 | 3.769558e-05 | 0.65095 | GF PASS; acc 0.650683; MC not run |
| `runs/sep_B_cat_120` (regenerate) | B cat | 135 | 33 | 3.182639e-19 | 3.499436e-05 | 3.108654e-06 | 3.810302e-05 | 0.64884 | GF PASS; acc 0.648079; MC not run |
| `runs/sep_B_cat_201` (regenerate) | B cat | 135 | 33 | 3.182639e-19 | 3.542272e-05 | 3.18652e-06 | 3.860924e-05 | 0.64776 | GF PASS; acc 0.647627; MC not run |
| `runs/sep_B_cat_210` (regenerate) | B cat | 135 | 33 | 3.182639e-19 | 3.501869e-05 | 3.053354e-06 | 3.807204e-05 | 0.65014 | GF PASS; acc 0.649815; MC not run |
| `runs/sep_B_catred_012` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.345252e-05 | 2.133969e-06 | 3.558649e-05 | 0.64212 | GF PASS; acc 0.641415; MC not run |
| `runs/sep_B_catred_0132` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.338603e-05 | 2.117226e-06 | 3.550326e-05 | 0.64212 | GF PASS; acc 0.641418; MC not run |
| `runs/sep_B_catred_021` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.345255e-05 | 2.132033e-06 | 3.558459e-05 | 0.64212 | GF PASS; acc 0.641914; MC not run |
| `runs/sep_B_catred_0231` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.347232e-05 | 2.214717e-06 | 3.568703e-05 | 0.63875 | GF PASS; acc 0.638814; MC not run |
| `runs/sep_B_catred_0312` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.348577e-05 | 2.197271e-06 | 3.568304e-05 | 0.64067 | GF PASS; acc 0.640111; MC not run |
| `runs/sep_B_catred_0321` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.348577e-05 | 2.19891e-06 | 3.568468e-05 | 0.64067 | GF PASS; acc 0.640106; MC not run |
| `runs/sep_B_catred_102` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.345252e-05 | 2.138338e-06 | 3.559086e-05 | 0.64148 | GF PASS; acc 0.640876; MC not run |
| `runs/sep_B_catred_1032` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.338603e-05 | 2.120865e-06 | 3.55069e-05 | 0.64148 | GF PASS; acc 0.640406; MC not run |
| `runs/sep_B_catred_120` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.359448e-05 | 2.184326e-06 | 3.577881e-05 | 0.63961 | GF PASS; acc 0.639476; MC not run |
| `runs/sep_B_catred_1230` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.361658e-05 | 2.169841e-06 | 3.578642e-05 | 0.64195 | GF PASS; acc 0.640983; MC not run |
| `runs/sep_B_catred_1302` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.338603e-05 | 2.117364e-06 | 3.55034e-05 | 0.64148 | GF PASS; acc 0.641030; MC not run |
| `runs/sep_B_catred_1320` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.356334e-05 | 2.186892e-06 | 3.575023e-05 | 0.63875 | GF PASS; acc 0.637802; MC not run |
| `runs/sep_B_catred_201` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.345255e-05 | 2.183076e-06 | 3.563563e-05 | 0.63918 | GF PASS; acc 0.638621; MC not run |
| `runs/sep_B_catred_2031` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.349454e-05 | 2.268343e-06 | 3.576288e-05 | 0.63519 | GF PASS; acc 0.634453; MC not run |
| `runs/sep_B_catred_210` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.355006e-05 | 2.177132e-06 | 3.57272e-05 | 0.64088 | GF PASS; acc 0.640213; MC not run |
| `runs/sep_B_catred_2130` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.361661e-05 | 2.170811e-06 | 3.578742e-05 | 0.64195 | GF PASS; acc 0.641187; MC not run |
| `runs/sep_B_catred_2301` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.350787e-05 | 2.211982e-06 | 3.571985e-05 | 0.64072 | GF PASS; acc 0.639860; MC not run |
| `runs/sep_B_catred_2310` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.353004e-05 | 2.211199e-06 | 3.574123e-05 | 0.63880 | GF PASS; acc 0.638234; MC not run |
| `runs/sep_B_catred_3012` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.34415e-05 | 2.163304e-06 | 3.560481e-05 | 0.64131 | GF PASS; acc 0.640865; MC not run |
| `runs/sep_B_catred_3021` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.34415e-05 | 2.165148e-06 | 3.560665e-05 | 0.64131 | GF PASS; acc 0.640864; MC not run |
| `runs/sep_B_catred_3102` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.336162e-05 | 2.148432e-06 | 3.551005e-05 | 0.64024 | GF PASS; acc 0.639544; MC not run |
| `runs/sep_B_catred_3120` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.353892e-05 | 2.208772e-06 | 3.57477e-05 | 0.63944 | GF PASS; acc 0.638351; MC not run |
| `runs/sep_B_catred_3201` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.35743e-05 | 2.237308e-06 | 3.581161e-05 | 0.63816 | GF PASS; acc 0.637738; MC not run |
| `runs/sep_B_catred_3210` (regenerate) | B catred | 140 | 33 | 3.182639e-19 | 3.353004e-05 | 2.198428e-06 | 3.572846e-05 | 0.64072 | GF PASS; acc 0.640246; MC not run |
| `runs/sep_B_direct_012` (regenerate) | B direct | 132 | 33 | 3.182639e-19 | 3.436038e-05 | 2.997704e-06 | 3.735808e-05 | 0.65111 | GF PASS; acc 0.650766; MC not run |
| `runs/sep_B_direct_021` (regenerate) | B direct | 132 | 33 | 3.182639e-19 | 3.469306e-05 | 3.103622e-06 | 3.779668e-05 | 0.64852 | GF PASS; acc 0.647872; MC not run |
| `runs/sep_B_direct_102` (regenerate) | B direct | 132 | 33 | 3.182639e-19 | 3.43005e-05 | 3.110047e-06 | 3.741054e-05 | 0.64723 | GF PASS; acc 0.646400; MC not run |
| `runs/sep_B_direct_120` (regenerate) | B direct | 132 | 33 | 3.182639e-19 | 3.434728e-05 | 2.929891e-06 | 3.727717e-05 | 0.65046 | GF PASS; acc 0.649622; MC not run |
| `runs/sep_B_direct_201` (regenerate) | B direct | 132 | 33 | 3.182639e-19 | 3.460903e-05 | 2.938681e-06 | 3.754771e-05 | 0.65046 | GF PASS; acc 0.649614; MC not run |
| `runs/sep_B_direct_210` (regenerate) | B direct | 132 | 33 | 3.182639e-19 | 3.458236e-05 | 2.907039e-06 | 3.74894e-05 | 0.65046 | GF PASS; acc 0.650129; MC not run |
| `runs/sep_B_flag_012` (regenerate) | B flag | 138 | 33 | 3.182639e-19 | 3.489176e-05 | 3.404582e-06 | 3.829634e-05 | 0.62910 | GF PASS; acc 0.628245; MC not run |
| `runs/sep_B_flag_021` (regenerate) | B flag | 138 | 33 | 3.182639e-19 | 3.526373e-05 | 3.536039e-06 | 3.879977e-05 | 0.62597 | GF PASS; acc 0.624653; MC not run |
| `runs/sep_B_flag_102` (regenerate) | B flag | 138 | 33 | 3.182639e-19 | 3.485626e-05 | 3.558788e-06 | 3.841505e-05 | 0.62411 | GF PASS; acc 0.623825; MC not run |
| `runs/sep_B_flag_120` (regenerate) | B flag | 138 | 33 | 3.182639e-19 | 3.486109e-05 | 3.342711e-06 | 3.82038e-05 | 0.62847 | GF PASS; acc 0.628103; MC not run |
| `runs/sep_B_flag_201` (regenerate) | B flag | 138 | 33 | 3.182639e-19 | 3.513123e-05 | 3.354452e-06 | 3.848568e-05 | 0.62847 | GF PASS; acc 0.628118; MC not run |
| `runs/sep_B_flag_210` (regenerate) | B flag | 138 | 33 | 3.182639e-19 | 3.507366e-05 | 3.323059e-06 | 3.839671e-05 | 0.62847 | GF PASS; acc 0.628132; MC not run |
| `runs/sep_B_hybrid1_012` (regenerate) | B hybrid1 | 131 | 33 | 3.182639e-19 | 3.446663e-05 | 3.087919e-06 | 3.755455e-05 | 0.64666 | GF PASS; acc 0.645947; MC not run |
| `runs/sep_B_hybrid1_021` (regenerate) | B hybrid1 | 131 | 33 | 3.182639e-19 | 3.462189e-05 | 3.067611e-06 | 3.76895e-05 | 0.64667 | GF PASS; acc 0.646140; MC not run |
| `runs/sep_B_hybrid1_102` (regenerate) | B hybrid1 | 131 | 33 | 3.182639e-19 | 3.446663e-05 | 3.087919e-06 | 3.755455e-05 | 0.64666 | GF PASS; acc 0.645947; MC not run |
| `runs/sep_B_hybrid1_120` (regenerate) | B hybrid1 | 131 | 33 | 3.182639e-19 | 3.446663e-05 | 3.087919e-06 | 3.755455e-05 | 0.64666 | GF PASS; acc 0.645947; MC not run |
| `runs/sep_B_hybrid1_201` (regenerate) | B hybrid1 | 131 | 33 | 3.182639e-19 | 3.462189e-05 | 3.067611e-06 | 3.76895e-05 | 0.64667 | GF PASS; acc 0.646140; MC not run |
| `runs/sep_B_hybrid1_210` (regenerate) | B hybrid1 | 131 | 33 | 3.182639e-19 | 3.462189e-05 | 3.067611e-06 | 3.76895e-05 | 0.64667 | GF PASS; acc 0.646140; MC not run |
| `runs/sep_B_hybrid2_012` (regenerate) | B hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.873675e-06 | 3.695441e-05 | 0.65025 | GF PASS; acc 0.649772; MC not run |
| `runs/sep_B_hybrid2_021` (regenerate) | B hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.873675e-06 | 3.695441e-05 | 0.65025 | GF PASS; acc 0.649772; MC not run |
| `runs/sep_B_hybrid2_102` (regenerate) | B hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.873675e-06 | 3.695441e-05 | 0.65025 | GF PASS; acc 0.649772; MC not run |
| `runs/sep_B_hybrid2_120` (regenerate) | B hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.873675e-06 | 3.695441e-05 | 0.65025 | GF PASS; acc 0.649772; MC not run |
| `runs/sep_B_hybrid2_201` (regenerate) | B hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.873675e-06 | 3.695441e-05 | 0.65025 | GF PASS; acc 0.649772; MC not run |
| `runs/sep_B_hybrid2_210` (regenerate) | B hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.873675e-06 | 3.695441e-05 | 0.65025 | GF PASS; acc 0.649772; MC not run |
| `runs/sep_B_hybrid2t_012` (regenerate) | B hybrid2t | 129 | 33 | 3.182639e-19 | 3.428423e-05 | 2.999093e-06 | 3.728332e-05 | 0.64767 | GF PASS; acc 0.646569; MC not run |
| `runs/sep_B_redundant_012` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.333004e-05 | 2.31148e-06 | 3.564152e-05 | 0.64407 | GF PASS; acc 0.643128; MC not run |
| `runs/sep_B_redundant_0132` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.349347e-05 | 2.466017e-06 | 3.595949e-05 | 0.64020 | GF PASS; acc 0.639306; MC not run |
| `runs/sep_B_redundant_021` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.333004e-05 | 2.319165e-06 | 3.56492e-05 | 0.64150 | GF PASS; acc 0.641161; MC not run |
| `runs/sep_B_redundant_0231` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.339623e-05 | 2.380621e-06 | 3.577685e-05 | 0.64082 | GF PASS; acc 0.639577; MC not run |
| `runs/sep_B_redundant_0312` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.352903e-05 | 2.429156e-06 | 3.595819e-05 | 0.64271 | GF PASS; acc 0.642383; MC not run |
| `runs/sep_B_redundant_0321` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.361727e-05 | 2.462547e-06 | 3.607982e-05 | 0.63951 | GF PASS; acc 0.638588; MC not run |
| `runs/sep_B_redundant_102` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.33567e-05 | 2.34972e-06 | 3.570642e-05 | 0.64023 | GF PASS; acc 0.639689; MC not run |
| `runs/sep_B_redundant_1032` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.349792e-05 | 2.465864e-06 | 3.596378e-05 | 0.64020 | GF PASS; acc 0.639944; MC not run |
| `runs/sep_B_redundant_120` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.345644e-05 | 2.295456e-06 | 3.575189e-05 | 0.64343 | GF PASS; acc 0.642655; MC not run |
| `runs/sep_B_redundant_1230` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.350076e-05 | 2.294819e-06 | 3.579558e-05 | 0.64342 | GF PASS; acc 0.643104; MC not run |
| `runs/sep_B_redundant_1302` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.345383e-05 | 2.432592e-06 | 3.588642e-05 | 0.64211 | GF PASS; acc 0.641642; MC not run |
| `runs/sep_B_redundant_1320` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.347839e-05 | 2.381353e-06 | 3.585974e-05 | 0.63955 | GF PASS; acc 0.638233; MC not run |
| `runs/sep_B_redundant_201` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.333226e-05 | 2.295201e-06 | 3.562746e-05 | 0.64343 | GF PASS; acc 0.642628; MC not run |
| `runs/sep_B_redundant_2031` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.339845e-05 | 2.359937e-06 | 3.575839e-05 | 0.64146 | GF PASS; acc 0.640367; MC not run |
| `runs/sep_B_redundant_210` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.345644e-05 | 2.295834e-06 | 3.575227e-05 | 0.64343 | GF PASS; acc 0.643103; MC not run |
| `runs/sep_B_redundant_2130` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.350076e-05 | 2.295348e-06 | 3.579611e-05 | 0.64343 | GF PASS; acc 0.642872; MC not run |
| `runs/sep_B_redundant_2301` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.343412e-05 | 2.320549e-06 | 3.575467e-05 | 0.64403 | GF PASS; acc 0.642905; MC not run |
| `runs/sep_B_redundant_2310` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.346085e-05 | 2.318546e-06 | 3.57794e-05 | 0.64210 | GF PASS; acc 0.641263; MC not run |
| `runs/sep_B_redundant_3012` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.348494e-05 | 2.385602e-06 | 3.587054e-05 | 0.64593 | GF PASS; acc 0.645393; MC not run |
| `runs/sep_B_redundant_3021` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.357324e-05 | 2.428858e-06 | 3.60021e-05 | 0.64143 | GF PASS; acc 0.641044; MC not run |
| `runs/sep_B_redundant_3102` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.347605e-05 | 2.461423e-06 | 3.593747e-05 | 0.63951 | GF PASS; acc 0.638852; MC not run |
| `runs/sep_B_redundant_3120` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.347839e-05 | 2.351143e-06 | 3.582953e-05 | 0.64270 | GF PASS; acc 0.641788; MC not run |
| `runs/sep_B_redundant_3201` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.353137e-05 | 2.364083e-06 | 3.589545e-05 | 0.64014 | GF PASS; acc 0.639731; MC not run |
| `runs/sep_B_redundant_3210` (regenerate) | B redundant | 136 | 33 | 3.182639e-19 | 3.35581e-05 | 2.35453e-06 | 3.591263e-05 | 0.64014 | GF PASS; acc 0.639211; MC not run |
| `runs/sep_B_seq_012` (regenerate) | B seq | 132 | 33 | 3.182639e-19 | 3.550603e-05 | 4.256132e-06 | 3.976216e-05 | 0.62081 | GF PASS; acc 0.619925; MC not run |
| `runs/sep_B_seq_021` (regenerate) | B seq | 132 | 33 | 3.182639e-19 | 3.60139e-05 | 4.181054e-06 | 4.019495e-05 | 0.62081 | GF PASS; acc 0.620351; MC not run |
| `runs/sep_B_seq_102` (regenerate) | B seq | 132 | 33 | 3.182639e-19 | 3.448726e-05 | 4.036858e-06 | 3.852412e-05 | 0.62081 | GF PASS; acc 0.620278; MC not run |
| `runs/sep_B_seq_120` (regenerate) | B seq | 132 | 33 | 3.182639e-19 | 3.536345e-05 | 3.884667e-06 | 3.924811e-05 | 0.62019 | GF PASS; acc 0.620530; MC not run |
| `runs/sep_B_seq_201` (regenerate) | B seq | 132 | 33 | 3.182639e-19 | 3.61067e-05 | 3.900404e-06 | 4.00071e-05 | 0.62019 | GF PASS; acc 0.619534; MC not run |
| `runs/sep_B_seq_210` (regenerate) | B seq | 132 | 33 | 3.182639e-19 | 3.63904e-05 | 3.790564e-06 | 4.018097e-05 | 0.62020 | GF PASS; acc 0.619443; MC not run |
| `runs/sep_C_cat13_012` (regenerate) | C cat13 | 135 | 33 | 3.182639e-19 | 3.461009e-05 | 3.132353e-06 | 3.774245e-05 | 0.64759 | GF PASS; acc 0.646381; MC not run |
| `runs/sep_C_cat13_021` (regenerate) | C cat13 | 135 | 33 | 3.182639e-19 | 3.494301e-05 | 3.233791e-06 | 3.81768e-05 | 0.64501 | GF PASS; acc 0.644265; MC not run |
| `runs/sep_C_cat13_102` (regenerate) | C cat13 | 135 | 33 | 3.182639e-19 | 3.455021e-05 | 3.237923e-06 | 3.778814e-05 | 0.64372 | GF PASS; acc 0.643007; MC not run |
| `runs/sep_C_cat13_120` (regenerate) | C cat13 | 135 | 33 | 3.182639e-19 | 3.459688e-05 | 3.063874e-06 | 3.766075e-05 | 0.64694 | GF PASS; acc 0.646071; MC not run |
| `runs/sep_C_cat13_201` (regenerate) | C cat13 | 135 | 33 | 3.182639e-19 | 3.485886e-05 | 3.072275e-06 | 3.793114e-05 | 0.64694 | GF PASS; acc 0.646040; MC not run |
| `runs/sep_C_cat13_210` (regenerate) | C cat13 | 135 | 33 | 3.182639e-19 | 3.483208e-05 | 3.040919e-06 | 3.7873e-05 | 0.64694 | GF PASS; acc 0.646672; MC not run |
| `runs/sep_C_cat13red_012` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.319706e-05 | 2.20484e-06 | 3.54019e-05 | 0.63499 | GF PASS; acc 0.634833; MC not run |
| `runs/sep_C_cat13red_0132` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.309507e-05 | 2.182399e-06 | 3.527747e-05 | 0.63410 | GF PASS; acc 0.633504; MC not run |
| `runs/sep_C_cat13red_021` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.319706e-05 | 2.208934e-06 | 3.540599e-05 | 0.63246 | GF PASS; acc 0.631519; MC not run |
| `runs/sep_C_cat13red_0231` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.317489e-05 | 2.16029e-06 | 3.533518e-05 | 0.63136 | GF PASS; acc 0.630824; MC not run |
| `runs/sep_C_cat13red_0312` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.313063e-05 | 2.121891e-06 | 3.525252e-05 | 0.63321 | GF PASS; acc 0.631862; MC not run |
| `runs/sep_C_cat13red_0321` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.313063e-05 | 2.119883e-06 | 3.525051e-05 | 0.63321 | GF PASS; acc 0.632144; MC not run |
| `runs/sep_C_cat13red_102` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.322372e-05 | 2.23685e-06 | 3.546057e-05 | 0.63120 | GF PASS; acc 0.630345; MC not run |
| `runs/sep_C_cat13red_1032` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.309952e-05 | 2.182285e-06 | 3.52818e-05 | 0.63410 | GF PASS; acc 0.633536; MC not run |
| `runs/sep_C_cat13red_120` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.332346e-05 | 2.189185e-06 | 3.551264e-05 | 0.63435 | GF PASS; acc 0.634006; MC not run |
| `runs/sep_C_cat13red_1230` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.336778e-05 | 2.19269e-06 | 3.556047e-05 | 0.63351 | GF PASS; acc 0.633109; MC not run |
| `runs/sep_C_cat13red_1302` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.309952e-05 | 2.207111e-06 | 3.530663e-05 | 0.63179 | GF PASS; acc 0.630930; MC not run |
| `runs/sep_C_cat13red_1320` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.316823e-05 | 2.168933e-06 | 3.533716e-05 | 0.63304 | GF PASS; acc 0.632672; MC not run |
| `runs/sep_C_cat13red_201` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.319928e-05 | 2.189225e-06 | 3.53885e-05 | 0.63435 | GF PASS; acc 0.634211; MC not run |
| `runs/sep_C_cat13red_2031` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.317712e-05 | 2.139581e-06 | 3.53167e-05 | 0.63325 | GF PASS; acc 0.633239; MC not run |
| `runs/sep_C_cat13red_210` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.332346e-05 | 2.1903e-06 | 3.551376e-05 | 0.63435 | GF PASS; acc 0.633848; MC not run |
| `runs/sep_C_cat13red_2130` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.336778e-05 | 2.194109e-06 | 3.556189e-05 | 0.63351 | GF PASS; acc 0.632982; MC not run |
| `runs/sep_C_cat13red_2301` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.325694e-05 | 2.139269e-06 | 3.539621e-05 | 0.63283 | GF PASS; acc 0.632041; MC not run |
| `runs/sep_C_cat13red_2310` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.332787e-05 | 2.140216e-06 | 3.546809e-05 | 0.63283 | GF PASS; acc 0.632090; MC not run |
| `runs/sep_C_cat13red_3012` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.313063e-05 | 2.118338e-06 | 3.524897e-05 | 0.63322 | GF PASS; acc 0.632889; MC not run |
| `runs/sep_C_cat13red_3021` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.313063e-05 | 2.127782e-06 | 3.525841e-05 | 0.63069 | GF PASS; acc 0.630321; MC not run |
| `runs/sep_C_cat13red_3102` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.312174e-05 | 2.14184e-06 | 3.526358e-05 | 0.62944 | GF PASS; acc 0.628463; MC not run |
| `runs/sep_C_cat13red_3120` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.316823e-05 | 2.097064e-06 | 3.526529e-05 | 0.63258 | GF PASS; acc 0.631765; MC not run |
| `runs/sep_C_cat13red_3201` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.313285e-05 | 2.095363e-06 | 3.522821e-05 | 0.63258 | GF PASS; acc 0.631815; MC not run |
| `runs/sep_C_cat13red_3210` (regenerate) | C cat13red | 140 | 33 | 3.182639e-19 | 3.320378e-05 | 2.095469e-06 | 3.529925e-05 | 0.63258 | GF PASS; acc 0.632349; MC not run |
| `runs/sep_C_cat3_012` (regenerate) | C cat3 | 138 | 33 | 3.182639e-19 | 3.544814e-05 | 3.474683e-06 | 3.892282e-05 | 0.64267 | GF PASS; acc 0.642304; MC not run |
| `runs/sep_C_cat3_021` (regenerate) | C cat3 | 138 | 33 | 3.182639e-19 | 3.557258e-05 | 3.459471e-06 | 3.903205e-05 | 0.64267 | GF PASS; acc 0.642298; MC not run |
| `runs/sep_C_cat3_102` (regenerate) | C cat3 | 138 | 33 | 3.182639e-19 | 3.51106e-05 | 3.407817e-06 | 3.851841e-05 | 0.64267 | GF PASS; acc 0.642301; MC not run |
| `runs/sep_C_cat3_120` (regenerate) | C cat3 | 138 | 33 | 3.182639e-19 | 3.534153e-05 | 3.439182e-06 | 3.878071e-05 | 0.64011 | GF PASS; acc 0.639083; MC not run |
| `runs/sep_C_cat3_201` (regenerate) | C cat3 | 138 | 33 | 3.182639e-19 | 3.575018e-05 | 3.481365e-06 | 3.923155e-05 | 0.64011 | GF PASS; acc 0.639062; MC not run |
| `runs/sep_C_cat3_210` (regenerate) | C cat3 | 138 | 33 | 3.182639e-19 | 3.550147e-05 | 3.422792e-06 | 3.892426e-05 | 0.64011 | GF PASS; acc 0.639079; MC not run |
| `runs/sep_C_cat3red_0123` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.332174e-05 | 2.097785e-06 | 3.541952e-05 | 0.63171 | GF PASS; acc 0.631759; MC not run |
| `runs/sep_C_cat3red_0132` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.335723e-05 | 2.115314e-06 | 3.547255e-05 | 0.62966 | GF PASS; acc 0.629051; MC not run |
| `runs/sep_C_cat3red_0213` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.332174e-05 | 2.096793e-06 | 3.541853e-05 | 0.63171 | GF PASS; acc 0.631766; MC not run |
| `runs/sep_C_cat3red_0231` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.340811e-05 | 2.194638e-06 | 3.560275e-05 | 0.62465 | GF PASS; acc 0.624494; MC not run |
| `runs/sep_C_cat3red_0312` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.345697e-05 | 2.206281e-06 | 3.566325e-05 | 0.62635 | GF PASS; acc 0.625143; MC not run |
| `runs/sep_C_cat3red_0321` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.345697e-05 | 2.207977e-06 | 3.566495e-05 | 0.62635 | GF PASS; acc 0.625146; MC not run |
| `runs/sep_C_cat3red_1023` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.332174e-05 | 2.102136e-06 | 3.542387e-05 | 0.63108 | GF PASS; acc 0.630588; MC not run |
| `runs/sep_C_cat3red_1032` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.335723e-05 | 2.119001e-06 | 3.547624e-05 | 0.62903 | GF PASS; acc 0.628796; MC not run |
| `runs/sep_C_cat3red_1203` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.337507e-05 | 2.114258e-06 | 3.548933e-05 | 0.62856 | GF PASS; acc 0.628180; MC not run |
| `runs/sep_C_cat3red_1230` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.337507e-05 | 2.111784e-06 | 3.548686e-05 | 0.62856 | GF PASS; acc 0.628166; MC not run |
| `runs/sep_C_cat3red_1302` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.335723e-05 | 2.11003e-06 | 3.546726e-05 | 0.63091 | GF PASS; acc 0.630346; MC not run |
| `runs/sep_C_cat3red_1320` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.340156e-05 | 2.144606e-06 | 3.554617e-05 | 0.62673 | GF PASS; acc 0.626517; MC not run |
| `runs/sep_C_cat3red_2013` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.332174e-05 | 2.102915e-06 | 3.542465e-05 | 0.63108 | GF PASS; acc 0.630213; MC not run |
| `runs/sep_C_cat3red_2031` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.340811e-05 | 2.208216e-06 | 3.561632e-05 | 0.62216 | GF PASS; acc 0.622354; MC not run |
| `runs/sep_C_cat3red_2103` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.337507e-05 | 2.116133e-06 | 3.54912e-05 | 0.62856 | GF PASS; acc 0.628185; MC not run |
| `runs/sep_C_cat3red_2130` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.337507e-05 | 2.114001e-06 | 3.548907e-05 | 0.62856 | GF PASS; acc 0.628164; MC not run |
| `runs/sep_C_cat3red_2301` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.33994e-05 | 2.160127e-06 | 3.555952e-05 | 0.62652 | GF PASS; acc 0.626271; MC not run |
| `runs/sep_C_cat3red_2310` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.335507e-05 | 2.162001e-06 | 3.551707e-05 | 0.62361 | GF PASS; acc 0.623058; MC not run |
| `runs/sep_C_cat3red_3012` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.34127e-05 | 2.15854e-06 | 3.557124e-05 | 0.63075 | GF PASS; acc 0.630269; MC not run |
| `runs/sep_C_cat3red_3021` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.34127e-05 | 2.160211e-06 | 3.557291e-05 | 0.63075 | GF PASS; acc 0.630268; MC not run |
| `runs/sep_C_cat3red_3102` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.333282e-05 | 2.149033e-06 | 3.548185e-05 | 0.62781 | GF PASS; acc 0.627304; MC not run |
| `runs/sep_C_cat3red_3120` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.337715e-05 | 2.17809e-06 | 3.555524e-05 | 0.62552 | GF PASS; acc 0.625075; MC not run |
| `runs/sep_C_cat3red_3201` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.345703e-05 | 2.176143e-06 | 3.563317e-05 | 0.62844 | GF PASS; acc 0.627473; MC not run |
| `runs/sep_C_cat3red_3210` (regenerate) | C cat3red | 144 | 33 | 3.182639e-19 | 3.34127e-05 | 2.176262e-06 | 3.558896e-05 | 0.62552 | GF PASS; acc 0.625066; MC not run |
| `runs/sep_C_cat3reusered_0123` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.369768e-05 | 2.840799e-06 | 3.653848e-05 | 0.57826 | GF PASS; acc 0.578115; MC not run |
| `runs/sep_C_cat3reusered_0132` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.360011e-05 | 2.939801e-06 | 3.653991e-05 | 0.57887 | GF PASS; acc 0.577485; MC not run |
| `runs/sep_C_cat3reusered_0213` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.369768e-05 | 2.800398e-06 | 3.649808e-05 | 0.57826 | GF PASS; acc 0.577862; MC not run |
| `runs/sep_C_cat3reusered_0231` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.382782e-05 | 2.867485e-06 | 3.66953e-05 | 0.57887 | GF PASS; acc 0.577957; MC not run |
| `runs/sep_C_cat3reusered_0312` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.411803e-05 | 3.06421e-06 | 3.718224e-05 | 0.57948 | GF PASS; acc 0.579780; MC not run |
| `runs/sep_C_cat3reusered_0321` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.438311e-05 | 3.028809e-06 | 3.741191e-05 | 0.57948 | GF PASS; acc 0.578738; MC not run |
| `runs/sep_C_cat3reusered_1023` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.369768e-05 | 2.842763e-06 | 3.654045e-05 | 0.57826 | GF PASS; acc 0.577226; MC not run |
| `runs/sep_C_cat3reusered_1032` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.360011e-05 | 2.941606e-06 | 3.654172e-05 | 0.57887 | GF PASS; acc 0.579034; MC not run |
| `runs/sep_C_cat3reusered_1203` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.447843e-05 | 2.822711e-06 | 3.730114e-05 | 0.57826 | GF PASS; acc 0.578404; MC not run |
| `runs/sep_C_cat3reusered_1230` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.474385e-05 | 2.826131e-06 | 3.756998e-05 | 0.57826 | GF PASS; acc 0.577659; MC not run |
| `runs/sep_C_cat3reusered_1302` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.360011e-05 | 2.930039e-06 | 3.653015e-05 | 0.57886 | GF PASS; acc 0.578499; MC not run |
| `runs/sep_C_cat3reusered_1320` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.399825e-05 | 2.843113e-06 | 3.684136e-05 | 0.57887 | GF PASS; acc 0.578362; MC not run |
| `runs/sep_C_cat3reusered_2013` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.369768e-05 | 2.804971e-06 | 3.650265e-05 | 0.57826 | GF PASS; acc 0.577861; MC not run |
| `runs/sep_C_cat3reusered_2031` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.382782e-05 | 2.87149e-06 | 3.669931e-05 | 0.57887 | GF PASS; acc 0.578356; MC not run |
| `runs/sep_C_cat3reusered_2103` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.447843e-05 | 2.825308e-06 | 3.730373e-05 | 0.57826 | GF PASS; acc 0.578401; MC not run |
| `runs/sep_C_cat3reusered_2130` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.474385e-05 | 2.828603e-06 | 3.757245e-05 | 0.57826 | GF PASS; acc 0.577661; MC not run |
| `runs/sep_C_cat3reusered_2301` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.434831e-05 | 2.863013e-06 | 3.721133e-05 | 0.57886 | GF PASS; acc 0.579003; MC not run |
| `runs/sep_C_cat3reusered_2310` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.448138e-05 | 2.810952e-06 | 3.729233e-05 | 0.57887 | GF PASS; acc 0.579100; MC not run |
| `runs/sep_C_cat3reusered_3012` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.411803e-05 | 3.042056e-06 | 3.716009e-05 | 0.57947 | GF PASS; acc 0.579165; MC not run |
| `runs/sep_C_cat3reusered_3021` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.438311e-05 | 3.006687e-06 | 3.738979e-05 | 0.57947 | GF PASS; acc 0.579367; MC not run |
| `runs/sep_C_cat3reusered_3102` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.359789e-05 | 2.918006e-06 | 3.65159e-05 | 0.57948 | GF PASS; acc 0.579557; MC not run |
| `runs/sep_C_cat3reusered_3120` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.399603e-05 | 2.830945e-06 | 3.682697e-05 | 0.57948 | GF PASS; acc 0.578811; MC not run |
| `runs/sep_C_cat3reusered_3201` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.438311e-05 | 2.84586e-06 | 3.722897e-05 | 0.57948 | GF PASS; acc 0.579183; MC not run |
| `runs/sep_C_cat3reusered_3210` (regenerate) | C cat3reusered | 144 | 33 | 3.182639e-19 | 3.451617e-05 | 2.793669e-06 | 3.730984e-05 | 0.57948 | GF PASS; acc 0.578880; MC not run |
| `runs/sep_C_cat3spinered_0123` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.365996e-05 | 2.79012e-06 | 3.645008e-05 | 0.57948 | GF PASS; acc 0.579347; MC not run |
| `runs/sep_C_cat3spinered_0132` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.352725e-05 | 2.881467e-06 | 3.640872e-05 | 0.57948 | GF PASS; acc 0.578550; MC not run |
| `runs/sep_C_cat3spinered_0213` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.365774e-05 | 2.749858e-06 | 3.64076e-05 | 0.57948 | GF PASS; acc 0.578888; MC not run |
| `runs/sep_C_cat3spinered_0231` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.379046e-05 | 2.803644e-06 | 3.65941e-05 | 0.57948 | GF PASS; acc 0.578667; MC not run |
| `runs/sep_C_cat3spinered_0312` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.402997e-05 | 2.990228e-06 | 3.70202e-05 | 0.57948 | GF PASS; acc 0.579499; MC not run |
| `runs/sep_C_cat3spinered_0321` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.429317e-05 | 2.952064e-06 | 3.724524e-05 | 0.57948 | GF PASS; acc 0.579834; MC not run |
| `runs/sep_C_cat3spinered_1023` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.365996e-05 | 2.791709e-06 | 3.645167e-05 | 0.57948 | GF PASS; acc 0.578550; MC not run |
| `runs/sep_C_cat3spinered_1032` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.352725e-05 | 2.882425e-06 | 3.640968e-05 | 0.57948 | GF PASS; acc 0.579336; MC not run |
| `runs/sep_C_cat3spinered_1203` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.441404e-05 | 2.772483e-06 | 3.718652e-05 | 0.57948 | GF PASS; acc 0.579522; MC not run |
| `runs/sep_C_cat3spinered_1230` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.467724e-05 | 2.776244e-06 | 3.745349e-05 | 0.57948 | GF PASS; acc 0.579852; MC not run |
| `runs/sep_C_cat3spinered_1302` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.352947e-05 | 2.870927e-06 | 3.64004e-05 | 0.57948 | GF PASS; acc 0.578935; MC not run |
| `runs/sep_C_cat3spinered_1320` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.392317e-05 | 2.784044e-06 | 3.670721e-05 | 0.57948 | GF PASS; acc 0.578668; MC not run |
| `runs/sep_C_cat3spinered_2013` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.36533e-05 | 2.754316e-06 | 3.640761e-05 | 0.57948 | GF PASS; acc 0.578698; MC not run |
| `runs/sep_C_cat3spinered_2031` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.378601e-05 | 2.80773e-06 | 3.659374e-05 | 0.57948 | GF PASS; acc 0.578913; MC not run |
| `runs/sep_C_cat3spinered_2103` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.441182e-05 | 2.77533e-06 | 3.718715e-05 | 0.57948 | GF PASS; acc 0.579856; MC not run |
| `runs/sep_C_cat3spinered_2130` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.467502e-05 | 2.779473e-06 | 3.745449e-05 | 0.57948 | GF PASS; acc 0.579520; MC not run |
| `runs/sep_C_cat3spinered_2301` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.429095e-05 | 2.798949e-06 | 3.70899e-05 | 0.57948 | GF PASS; acc 0.579322; MC not run |
| `runs/sep_C_cat3spinered_2310` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.442366e-05 | 2.749638e-06 | 3.71733e-05 | 0.57948 | GF PASS; acc 0.578532; MC not run |
| `runs/sep_C_cat3spinered_3012` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.402775e-05 | 2.967986e-06 | 3.699573e-05 | 0.57948 | GF PASS; acc 0.579841; MC not run |
| `runs/sep_C_cat3spinered_3021` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.429095e-05 | 2.930133e-06 | 3.722108e-05 | 0.57948 | GF PASS; acc 0.579493; MC not run |
| `runs/sep_C_cat3spinered_3102` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.352947e-05 | 2.847667e-06 | 3.637714e-05 | 0.57948 | GF PASS; acc 0.578679; MC not run |
| `runs/sep_C_cat3spinered_3120` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.392317e-05 | 2.760411e-06 | 3.668358e-05 | 0.57948 | GF PASS; acc 0.578910; MC not run |
| `runs/sep_C_cat3spinered_3201` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.429095e-05 | 2.772776e-06 | 3.706373e-05 | 0.57948 | GF PASS; acc 0.578536; MC not run |
| `runs/sep_C_cat3spinered_3210` (regenerate) | C cat3spinered | 144 | 33 | 3.182639e-19 | 3.442366e-05 | 2.722872e-06 | 3.714653e-05 | 0.57948 | GF PASS; acc 0.579311; MC not run |
| `runs/sep_C_cat4_012` (regenerate) | C cat4 | 141 | 33 | 3.182639e-19 | 3.582346e-05 | 3.867811e-06 | 3.969127e-05 | 0.63159 | GF PASS; acc 0.630800; MC not run |
| `runs/sep_C_cat4_021` (regenerate) | C cat4 | 141 | 33 | 3.182639e-19 | 3.61255e-05 | 3.836153e-06 | 3.996165e-05 | 0.63159 | GF PASS; acc 0.630791; MC not run |
| `runs/sep_C_cat4_102` (regenerate) | C cat4 | 141 | 33 | 3.182639e-19 | 3.548598e-05 | 3.800733e-06 | 3.928671e-05 | 0.63159 | GF PASS; acc 0.630801; MC not run |
| `runs/sep_C_cat4_120` (regenerate) | C cat4 | 141 | 33 | 3.182639e-19 | 3.553937e-05 | 3.71127e-06 | 3.925064e-05 | 0.63159 | GF PASS; acc 0.631319; MC not run |
| `runs/sep_C_cat4_201` (regenerate) | C cat4 | 141 | 33 | 3.182639e-19 | 3.612556e-05 | 3.736281e-06 | 3.986184e-05 | 0.63159 | GF PASS; acc 0.631374; MC not run |
| `runs/sep_C_cat4_210` (regenerate) | C cat4 | 141 | 33 | 3.182639e-19 | 3.587679e-05 | 3.678454e-06 | 3.955524e-05 | 0.63159 | GF PASS; acc 0.631348; MC not run |
| `runs/sep_C_cat_012` (regenerate) | C cat | 135 | 33 | 3.182639e-19 | 3.494577e-05 | 3.104493e-06 | 3.805026e-05 | 0.65095 | GF PASS; acc 0.649744; MC not run |
| `runs/sep_C_cat_021` (regenerate) | C cat | 135 | 33 | 3.182639e-19 | 3.511243e-05 | 3.087289e-06 | 3.819972e-05 | 0.65095 | GF PASS; acc 0.649757; MC not run |
| `runs/sep_C_cat_102` (regenerate) | C cat | 135 | 33 | 3.182639e-19 | 3.460829e-05 | 3.036813e-06 | 3.76451e-05 | 0.65095 | GF PASS; acc 0.650830; MC not run |
| `runs/sep_C_cat_120` (regenerate) | C cat | 135 | 33 | 3.182639e-19 | 3.499436e-05 | 3.056382e-06 | 3.805074e-05 | 0.64884 | GF PASS; acc 0.648618; MC not run |
| `runs/sep_C_cat_201` (regenerate) | C cat | 135 | 33 | 3.182639e-19 | 3.542272e-05 | 3.133843e-06 | 3.855656e-05 | 0.64776 | GF PASS; acc 0.647790; MC not run |
| `runs/sep_C_cat_210` (regenerate) | C cat | 135 | 33 | 3.182639e-19 | 3.501869e-05 | 3.004982e-06 | 3.802367e-05 | 0.65014 | GF PASS; acc 0.649594; MC not run |
| `runs/sep_C_catred_012` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.345252e-05 | 2.072066e-06 | 3.552459e-05 | 0.64212 | GF PASS; acc 0.641576; MC not run |
| `runs/sep_C_catred_0132` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.338603e-05 | 2.054966e-06 | 3.5441e-05 | 0.64212 | GF PASS; acc 0.641076; MC not run |
| `runs/sep_C_catred_021` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.345255e-05 | 2.070128e-06 | 3.552268e-05 | 0.64212 | GF PASS; acc 0.640879; MC not run |
| `runs/sep_C_catred_0231` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.347232e-05 | 2.151026e-06 | 3.562334e-05 | 0.63875 | GF PASS; acc 0.637754; MC not run |
| `runs/sep_C_catred_0312` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.348577e-05 | 2.136757e-06 | 3.562253e-05 | 0.64067 | GF PASS; acc 0.639648; MC not run |
| `runs/sep_C_catred_0321` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.348577e-05 | 2.138396e-06 | 3.562416e-05 | 0.64067 | GF PASS; acc 0.639671; MC not run |
| `runs/sep_C_catred_102` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.345252e-05 | 2.075952e-06 | 3.552848e-05 | 0.64148 | GF PASS; acc 0.640406; MC not run |
| `runs/sep_C_catred_1032` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.338603e-05 | 2.058124e-06 | 3.544416e-05 | 0.64148 | GF PASS; acc 0.640736; MC not run |
| `runs/sep_C_catred_120` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.359448e-05 | 2.121177e-06 | 3.571566e-05 | 0.63961 | GF PASS; acc 0.639169; MC not run |
| `runs/sep_C_catred_1230` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.361658e-05 | 2.110811e-06 | 3.572739e-05 | 0.64195 | GF PASS; acc 0.641478; MC not run |
| `runs/sep_C_catred_1302` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.338603e-05 | 2.054659e-06 | 3.544069e-05 | 0.64148 | GF PASS; acc 0.640699; MC not run |
| `runs/sep_C_catred_1320` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.356334e-05 | 2.120833e-06 | 3.568417e-05 | 0.63875 | GF PASS; acc 0.638442; MC not run |
| `runs/sep_C_catred_201` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.345255e-05 | 2.119877e-06 | 3.557243e-05 | 0.63918 | GF PASS; acc 0.638695; MC not run |
| `runs/sep_C_catred_2031` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.349454e-05 | 2.200224e-06 | 3.569476e-05 | 0.63519 | GF PASS; acc 0.635063; MC not run |
| `runs/sep_C_catred_210` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.355006e-05 | 2.117581e-06 | 3.566765e-05 | 0.64088 | GF PASS; acc 0.640219; MC not run |
| `runs/sep_C_catred_2130` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.361661e-05 | 2.111778e-06 | 3.572839e-05 | 0.64195 | GF PASS; acc 0.640925; MC not run |
| `runs/sep_C_catred_2301` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.350787e-05 | 2.154648e-06 | 3.566252e-05 | 0.64072 | GF PASS; acc 0.640275; MC not run |
| `runs/sep_C_catred_2310` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.353004e-05 | 2.150088e-06 | 3.568012e-05 | 0.63880 | GF PASS; acc 0.638159; MC not run |
| `runs/sep_C_catred_3012` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.34415e-05 | 2.102836e-06 | 3.554434e-05 | 0.64131 | GF PASS; acc 0.640763; MC not run |
| `runs/sep_C_catred_3021` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.34415e-05 | 2.10468e-06 | 3.554618e-05 | 0.64131 | GF PASS; acc 0.640747; MC not run |
| `runs/sep_C_catred_3102` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.336162e-05 | 2.087146e-06 | 3.544877e-05 | 0.64024 | GF PASS; acc 0.640401; MC not run |
| `runs/sep_C_catred_3120` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.353892e-05 | 2.147908e-06 | 3.568683e-05 | 0.63944 | GF PASS; acc 0.638851; MC not run |
| `runs/sep_C_catred_3201` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.35743e-05 | 2.174128e-06 | 3.574843e-05 | 0.63816 | GF PASS; acc 0.637076; MC not run |
| `runs/sep_C_catred_3210` (regenerate) | C catred | 140 | 33 | 3.182639e-19 | 3.353004e-05 | 2.141164e-06 | 3.56712e-05 | 0.64072 | GF PASS; acc 0.640021; MC not run |
| `runs/sep_C_direct_012` (regenerate) | C direct | 132 | 33 | 3.182639e-19 | 3.436038e-05 | 2.960917e-06 | 3.732129e-05 | 0.65111 | GF PASS; acc 0.650563; MC not run |
| `runs/sep_C_direct_021` (regenerate) | C direct | 132 | 33 | 3.182639e-19 | 3.469306e-05 | 3.062224e-06 | 3.775528e-05 | 0.64852 | GF PASS; acc 0.647139; MC not run |
| `runs/sep_C_direct_102` (regenerate) | C direct | 132 | 33 | 3.182639e-19 | 3.43005e-05 | 3.06568e-06 | 3.736618e-05 | 0.64723 | GF PASS; acc 0.646938; MC not run |
| `runs/sep_C_direct_120` (regenerate) | C direct | 132 | 33 | 3.182639e-19 | 3.434728e-05 | 2.891814e-06 | 3.723909e-05 | 0.65046 | GF PASS; acc 0.649952; MC not run |
| `runs/sep_C_direct_201` (regenerate) | C direct | 132 | 33 | 3.182639e-19 | 3.460903e-05 | 2.900504e-06 | 3.750953e-05 | 0.65046 | GF PASS; acc 0.649965; MC not run |
| `runs/sep_C_direct_210` (regenerate) | C direct | 132 | 33 | 3.182639e-19 | 3.458236e-05 | 2.868908e-06 | 3.745127e-05 | 0.65046 | GF PASS; acc 0.649427; MC not run |
| `runs/sep_C_flag_012` (regenerate) | C flag | 138 | 33 | 3.182639e-19 | 3.489176e-05 | 3.368135e-06 | 3.825989e-05 | 0.62910 | GF PASS; acc 0.628636; MC not run |
| `runs/sep_C_flag_021` (regenerate) | C flag | 138 | 33 | 3.182639e-19 | 3.526373e-05 | 3.496159e-06 | 3.875989e-05 | 0.62597 | GF PASS; acc 0.625528; MC not run |
| `runs/sep_C_flag_102` (regenerate) | C flag | 138 | 33 | 3.182639e-19 | 3.485626e-05 | 3.517849e-06 | 3.837411e-05 | 0.62411 | GF PASS; acc 0.622995; MC not run |
| `runs/sep_C_flag_120` (regenerate) | C flag | 138 | 33 | 3.182639e-19 | 3.486109e-05 | 3.304962e-06 | 3.816605e-05 | 0.62847 | GF PASS; acc 0.627962; MC not run |
| `runs/sep_C_flag_201` (regenerate) | C flag | 138 | 33 | 3.182639e-19 | 3.513123e-05 | 3.316648e-06 | 3.844787e-05 | 0.62847 | GF PASS; acc 0.627990; MC not run |
| `runs/sep_C_flag_210` (regenerate) | C flag | 138 | 33 | 3.182639e-19 | 3.507366e-05 | 3.285278e-06 | 3.835893e-05 | 0.62847 | GF PASS; acc 0.627794; MC not run |
| `runs/sep_C_hybrid1_012` (regenerate) | C hybrid1 | 131 | 33 | 3.182639e-19 | 3.446663e-05 | 3.038374e-06 | 3.7505e-05 | 0.64666 | GF PASS; acc 0.645689; MC not run |
| `runs/sep_C_hybrid1_021` (regenerate) | C hybrid1 | 131 | 33 | 3.182639e-19 | 3.462189e-05 | 3.018056e-06 | 3.763995e-05 | 0.64667 | GF PASS; acc 0.646116; MC not run |
| `runs/sep_C_hybrid1_102` (regenerate) | C hybrid1 | 131 | 33 | 3.182639e-19 | 3.446663e-05 | 3.038374e-06 | 3.7505e-05 | 0.64666 | GF PASS; acc 0.645689; MC not run |
| `runs/sep_C_hybrid1_120` (regenerate) | C hybrid1 | 131 | 33 | 3.182639e-19 | 3.446663e-05 | 3.038374e-06 | 3.7505e-05 | 0.64666 | GF PASS; acc 0.645689; MC not run |
| `runs/sep_C_hybrid1_201` (regenerate) | C hybrid1 | 131 | 33 | 3.182639e-19 | 3.462189e-05 | 3.018056e-06 | 3.763995e-05 | 0.64667 | GF PASS; acc 0.646116; MC not run |
| `runs/sep_C_hybrid1_210` (regenerate) | C hybrid1 | 131 | 33 | 3.182639e-19 | 3.462189e-05 | 3.018056e-06 | 3.763995e-05 | 0.64667 | GF PASS; acc 0.646116; MC not run |
| `runs/sep_C_hybrid2_012` (regenerate) | C hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.835323e-06 | 3.691605e-05 | 0.65025 | GF PASS; acc 0.649007; MC not run |
| `runs/sep_C_hybrid2_021` (regenerate) | C hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.835323e-06 | 3.691605e-05 | 0.65025 | GF PASS; acc 0.649007; MC not run |
| `runs/sep_C_hybrid2_102` (regenerate) | C hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.835323e-06 | 3.691605e-05 | 0.65025 | GF PASS; acc 0.649007; MC not run |
| `runs/sep_C_hybrid2_120` (regenerate) | C hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.835323e-06 | 3.691605e-05 | 0.65025 | GF PASS; acc 0.649007; MC not run |
| `runs/sep_C_hybrid2_201` (regenerate) | C hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.835323e-06 | 3.691605e-05 | 0.65025 | GF PASS; acc 0.649007; MC not run |
| `runs/sep_C_hybrid2_210` (regenerate) | C hybrid2 | 130 | 33 | 3.182639e-19 | 3.408073e-05 | 2.835323e-06 | 3.691605e-05 | 0.65025 | GF PASS; acc 0.649007; MC not run |
| `runs/sep_C_hybrid2t_012` (regenerate) | C hybrid2t | 129 | 33 | 3.182639e-19 | 3.428423e-05 | 2.953779e-06 | 3.723801e-05 | 0.64767 | GF PASS; acc 0.647335; MC not run |
| `runs/sep_C_redundant_012` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.333004e-05 | 2.269188e-06 | 3.559922e-05 | 0.64407 | GF PASS; acc 0.643682; MC not run |
| `runs/sep_C_redundant_0132` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.349347e-05 | 2.416983e-06 | 3.591046e-05 | 0.64020 | GF PASS; acc 0.639743; MC not run |
| `runs/sep_C_redundant_021` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.333004e-05 | 2.272345e-06 | 3.560238e-05 | 0.64150 | GF PASS; acc 0.640667; MC not run |
| `runs/sep_C_redundant_0231` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.339623e-05 | 2.332147e-06 | 3.572838e-05 | 0.64082 | GF PASS; acc 0.639945; MC not run |
| `runs/sep_C_redundant_0312` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.352903e-05 | 2.384358e-06 | 3.591339e-05 | 0.64271 | GF PASS; acc 0.641605; MC not run |
| `runs/sep_C_redundant_0321` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.361727e-05 | 2.412122e-06 | 3.602939e-05 | 0.63951 | GF PASS; acc 0.638995; MC not run |
| `runs/sep_C_redundant_102` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.33567e-05 | 2.300014e-06 | 3.565672e-05 | 0.64023 | GF PASS; acc 0.639880; MC not run |
| `runs/sep_C_redundant_1032` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.349792e-05 | 2.416781e-06 | 3.59147e-05 | 0.64020 | GF PASS; acc 0.639602; MC not run |
| `runs/sep_C_redundant_120` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.345644e-05 | 2.252047e-06 | 3.570848e-05 | 0.64343 | GF PASS; acc 0.643464; MC not run |
| `runs/sep_C_redundant_1230` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.350076e-05 | 2.25144e-06 | 3.57522e-05 | 0.64342 | GF PASS; acc 0.642527; MC not run |
| `runs/sep_C_redundant_1302` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.345383e-05 | 2.386905e-06 | 3.584073e-05 | 0.64211 | GF PASS; acc 0.641096; MC not run |
| `runs/sep_C_redundant_1320` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.347839e-05 | 2.331081e-06 | 3.580947e-05 | 0.63955 | GF PASS; acc 0.639438; MC not run |
| `runs/sep_C_redundant_201` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.333226e-05 | 2.251713e-06 | 3.558397e-05 | 0.64343 | GF PASS; acc 0.642890; MC not run |
| `runs/sep_C_redundant_2031` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.339845e-05 | 2.312508e-06 | 3.571096e-05 | 0.64146 | GF PASS; acc 0.641076; MC not run |
| `runs/sep_C_redundant_210` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.345644e-05 | 2.252405e-06 | 3.570884e-05 | 0.64343 | GF PASS; acc 0.642831; MC not run |
| `runs/sep_C_redundant_2130` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.350076e-05 | 2.25195e-06 | 3.575271e-05 | 0.64343 | GF PASS; acc 0.642998; MC not run |
| `runs/sep_C_redundant_2301` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.343412e-05 | 2.278018e-06 | 3.571214e-05 | 0.64403 | GF PASS; acc 0.643570; MC not run |
| `runs/sep_C_redundant_2310` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.346085e-05 | 2.272245e-06 | 3.57331e-05 | 0.64210 | GF PASS; acc 0.641184; MC not run |
| `runs/sep_C_redundant_3012` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.348494e-05 | 2.346407e-06 | 3.583135e-05 | 0.64593 | GF PASS; acc 0.645701; MC not run |
| `runs/sep_C_redundant_3021` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.357324e-05 | 2.381808e-06 | 3.595505e-05 | 0.64143 | GF PASS; acc 0.641246; MC not run |
| `runs/sep_C_redundant_3102` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.347605e-05 | 2.409562e-06 | 3.588561e-05 | 0.63951 | GF PASS; acc 0.638698; MC not run |
| `runs/sep_C_redundant_3120` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.347839e-05 | 2.306208e-06 | 3.57846e-05 | 0.64270 | GF PASS; acc 0.641601; MC not run |
| `runs/sep_C_redundant_3201` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.353137e-05 | 2.314605e-06 | 3.584598e-05 | 0.64014 | GF PASS; acc 0.640363; MC not run |
| `runs/sep_C_redundant_3210` (regenerate) | C redundant | 136 | 33 | 3.182639e-19 | 3.35581e-05 | 2.30506e-06 | 3.586316e-05 | 0.64014 | GF PASS; acc 0.639553; MC not run |
| `runs/sep_C_seq_012` (regenerate) | C seq | 132 | 33 | 3.182639e-19 | 3.550603e-05 | 4.162559e-06 | 3.966859e-05 | 0.62081 | GF PASS; acc 0.620064; MC not run |
| `runs/sep_C_seq_021` (regenerate) | C seq | 132 | 33 | 3.182639e-19 | 3.60139e-05 | 4.087269e-06 | 4.010116e-05 | 0.62081 | GF PASS; acc 0.619292; MC not run |
| `runs/sep_C_seq_102` (regenerate) | C seq | 132 | 33 | 3.182639e-19 | 3.448726e-05 | 3.942794e-06 | 3.843005e-05 | 0.62081 | GF PASS; acc 0.620537; MC not run |
| `runs/sep_C_seq_120` (regenerate) | C seq | 132 | 33 | 3.182639e-19 | 3.536345e-05 | 3.789321e-06 | 3.915277e-05 | 0.62019 | GF PASS; acc 0.619204; MC not run |
| `runs/sep_C_seq_201` (regenerate) | C seq | 132 | 33 | 3.182639e-19 | 3.61067e-05 | 3.804686e-06 | 3.991138e-05 | 0.62019 | GF PASS; acc 0.619387; MC not run |
| `runs/sep_C_seq_210` (regenerate) | C seq | 132 | 33 | 3.182639e-19 | 3.63904e-05 | 3.695009e-06 | 4.008541e-05 | 0.62020 | GF PASS; acc 0.619526; MC not run |
| [runs/sep_ref](runs/sep_ref.qasm) · [JSON](runs/sep_ref.json) · [receipt](runs/sep_ref.result.json) |  direct | 129 | 33 | 3.182639e-19 | 3.338849e-05 | 2.096233e-06 | 3.548473e-05 | 0.67283 | GF PASS; acc 0.671797; MC not run |
| `runs/v22_ABC_cat_012` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.000162337 | 2.684516e-05 | 0.0001891822 | 0.54552 | GF PASS; acc 0.545422; MC not run |
| `runs/v22_ABC_cat_021` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.0001577312 | 2.668213e-05 | 0.0001844134 | 0.54552 | GF PASS; acc 0.545389; MC not run |
| `runs/v22_ABC_cat_102` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.0001551281 | 2.680533e-05 | 0.0001819334 | 0.54552 | GF PASS; acc 0.545204; MC not run |
| `runs/v22_ABC_cat_120` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.000140959 | 2.814102e-05 | 0.0001691 | 0.54022 | GF PASS; acc 0.540394; MC not run |
| `runs/v22_ABC_cat_201` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.000136401 | 2.90261e-05 | 0.0001654271 | 0.53753 | GF PASS; acc 0.537599; MC not run |
| `runs/v22_ABC_cat_210` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.0001218589 | 2.707915e-05 | 0.0001489381 | 0.54347 | GF PASS; acc 0.543058; MC not run |
| `runs/v22_ABC_direct_012` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 4.781169e-05 | 2.662881e-05 | 7.444051e-05 | 0.54592 | GF PASS; acc 0.545069; MC not run |
| `runs/v22_ABC_direct_021` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 4.782032e-05 | 2.852883e-05 | 7.634915e-05 | 0.53942 | GF PASS; acc 0.539388; MC not run |
| `runs/v22_ABC_direct_102` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 5.725509e-05 | 2.974242e-05 | 8.69975e-05 | 0.53621 | GF PASS; acc 0.536315; MC not run |
| `runs/v22_ABC_direct_120` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 4.619708e-05 | 2.698637e-05 | 7.318346e-05 | 0.54428 | GF PASS; acc 0.544455; MC not run |
| `runs/v22_ABC_direct_201` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 4.52229e-05 | 2.68028e-05 | 7.20257e-05 | 0.54428 | GF PASS; acc 0.544538; MC not run |
| `runs/v22_ABC_direct_210` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 4.505104e-05 | 2.678847e-05 | 7.183952e-05 | 0.54428 | GF PASS; acc 0.544311; MC not run |
| `runs/v22_ABC_flag_012` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.406997e-05 | 3.141041e-05 | 6.548038e-05 | 0.49241 | GF FAIL; acc 0.493068; MC not run |
| `runs/v22_ABC_flag_021` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.376197e-05 | 3.341502e-05 | 6.717699e-05 | 0.48511 | GF FAIL; acc 0.485164; MC not run |
| `runs/v22_ABC_flag_102` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.489768e-05 | 3.466883e-05 | 6.956651e-05 | 0.48079 | GF FAIL; acc 0.481164; MC not run |
| `runs/v22_ABC_flag_120` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.455158e-05 | 3.189703e-05 | 6.644861e-05 | 0.49093 | GF FAIL; acc 0.491222; MC not run |
| `runs/v22_ABC_flag_201` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.367806e-05 | 3.174039e-05 | 6.541845e-05 | 0.49093 | GF FAIL; acc 0.491251; MC not run |
| `runs/v22_ABC_flag_210` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.400698e-05 | 3.174478e-05 | 6.575176e-05 | 0.49093 | GF FAIL; acc 0.490563; MC not run |
| `runs/v22_ABC_flag_redundant_012` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.418109e-05 | 2.205123e-05 | 5.623232e-05 | 0.51612 | GF PASS; acc 0.516397; MC not run |
| `runs/v22_ABC_flag_redundant_021` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.387308e-05 | 2.283334e-05 | 5.670642e-05 | 0.50948 | GF PASS; acc 0.509575; MC not run |
| `runs/v22_ABC_flag_redundant_102` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.520657e-05 | 2.360482e-05 | 5.881139e-05 | 0.50594 | GF PASS; acc 0.505838; MC not run |
| `runs/v22_ABC_flag_redundant_120` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.468936e-05 | 2.20992e-05 | 5.678856e-05 | 0.51457 | GF PASS; acc 0.514050; MC not run |
| `runs/v22_ABC_flag_redundant_201` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.379806e-05 | 2.199893e-05 | 5.579699e-05 | 0.51457 | GF PASS; acc 0.514198; MC not run |
| `runs/v22_ABC_flag_redundant_210` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.414476e-05 | 2.203051e-05 | 5.617526e-05 | 0.51457 | GF PASS; acc 0.514742; MC not run |
| `runs/v22_ABC_hybrid1_012` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.601249e-05 | 2.992741e-05 | 7.593991e-05 | 0.53481 | GF PASS; acc 0.535433; MC not run |
| `runs/v22_ABC_hybrid1_021` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.563837e-05 | 2.975169e-05 | 7.539006e-05 | 0.53482 | GF PASS; acc 0.535462; MC not run |
| `runs/v22_ABC_hybrid1_102` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.601249e-05 | 2.992741e-05 | 7.593991e-05 | 0.53481 | GF PASS; acc 0.535433; MC not run |
| `runs/v22_ABC_hybrid1_120` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.601249e-05 | 2.992741e-05 | 7.593991e-05 | 0.53481 | GF PASS; acc 0.535433; MC not run |
| `runs/v22_ABC_hybrid1_201` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.563837e-05 | 2.975169e-05 | 7.539006e-05 | 0.53482 | GF PASS; acc 0.535462; MC not run |
| `runs/v22_ABC_hybrid1_210` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.563837e-05 | 2.975169e-05 | 7.539006e-05 | 0.53482 | GF PASS; acc 0.535462; MC not run |
| `runs/v22_ABC_hybrid2_012` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.231602e-05 | 2.633625e-05 | 6.865227e-05 | 0.54376 | GF PASS; acc 0.543833; MC not run |
| `runs/v22_ABC_hybrid2_021` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.231602e-05 | 2.633625e-05 | 6.865227e-05 | 0.54376 | GF PASS; acc 0.543833; MC not run |
| `runs/v22_ABC_hybrid2_102` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.231602e-05 | 2.633625e-05 | 6.865227e-05 | 0.54376 | GF PASS; acc 0.543833; MC not run |
| `runs/v22_ABC_hybrid2_120` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.231602e-05 | 2.633625e-05 | 6.865227e-05 | 0.54376 | GF PASS; acc 0.543833; MC not run |
| `runs/v22_ABC_hybrid2_201` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.231602e-05 | 2.633625e-05 | 6.865227e-05 | 0.54376 | GF PASS; acc 0.543833; MC not run |
| `runs/v22_ABC_hybrid2_210` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.231602e-05 | 2.633625e-05 | 6.865227e-05 | 0.54376 | GF PASS; acc 0.543833; MC not run |
| `runs/v22_ABC_hybrid2t_012` (regenerate) | ABC hybrid2t | 123 | 45 | 2.923587e-19 | 6.21679e-05 | 2.837407e-05 | 9.054197e-05 | 0.53732 | GF PASS; acc 0.537277; MC not run |
| `runs/v22_ABC_redundant_012` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.126385e-05 | 1.932635e-05 | 6.05902e-05 | 0.52840 | GF PASS; acc 0.527570; MC not run |
| `runs/v22_ABC_redundant_0132` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.402154e-05 | 2.216735e-05 | 6.618889e-05 | 0.51892 | GF PASS; acc 0.518257; MC not run |
| `runs/v22_ABC_redundant_021` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.122176e-05 | 1.99122e-05 | 6.113396e-05 | 0.52211 | GF PASS; acc 0.522713; MC not run |
| `runs/v22_ABC_redundant_0231` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.566236e-05 | 2.066884e-05 | 6.633119e-05 | 0.52045 | GF PASS; acc 0.520368; MC not run |
| `runs/v22_ABC_redundant_0312` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.409408e-05 | 2.0938e-05 | 6.503208e-05 | 0.52506 | GF PASS; acc 0.525283; MC not run |
| `runs/v22_ABC_redundant_0321` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.417044e-05 | 2.203355e-05 | 6.6204e-05 | 0.51727 | GF PASS; acc 0.516812; MC not run |
| `runs/v22_ABC_redundant_102` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.66175e-05 | 2.05922e-05 | 6.72097e-05 | 0.51900 | GF PASS; acc 0.518481; MC not run |
| `runs/v22_ABC_redundant_1032` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.433589e-05 | 2.215595e-05 | 6.649184e-05 | 0.51893 | GF PASS; acc 0.518580; MC not run |
| `runs/v22_ABC_redundant_120` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.126712e-05 | 1.915199e-05 | 6.041912e-05 | 0.52681 | GF PASS; acc 0.527177; MC not run |
| `runs/v22_ABC_redundant_1230` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.138855e-05 | 1.915363e-05 | 6.054218e-05 | 0.52681 | GF PASS; acc 0.526314; MC not run |
| `runs/v22_ABC_redundant_1302` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.365853e-05 | 2.134181e-05 | 6.500034e-05 | 0.52360 | GF PASS; acc 0.523176; MC not run |
| `runs/v22_ABC_redundant_1320` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.339754e-05 | 2.139988e-05 | 6.479742e-05 | 0.51735 | GF PASS; acc 0.516921; MC not run |
| `runs/v22_ABC_redundant_201` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.099669e-05 | 1.910495e-05 | 6.010165e-05 | 0.52681 | GF PASS; acc 0.526660; MC not run |
| `runs/v22_ABC_redundant_2031` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.557012e-05 | 2.018385e-05 | 6.575397e-05 | 0.52200 | GF PASS; acc 0.521619; MC not run |
| `runs/v22_ABC_redundant_210` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.111619e-05 | 1.910602e-05 | 6.022221e-05 | 0.52682 | GF PASS; acc 0.526899; MC not run |
| `runs/v22_ABC_redundant_2130` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.123761e-05 | 1.910712e-05 | 6.034474e-05 | 0.52681 | GF PASS; acc 0.526374; MC not run |
| `runs/v22_ABC_redundant_2301` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.191738e-05 | 1.927639e-05 | 6.119377e-05 | 0.52829 | GF PASS; acc 0.528447; MC not run |
| `runs/v22_ABC_redundant_2310` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.511614e-05 | 1.969632e-05 | 6.481246e-05 | 0.52356 | GF PASS; acc 0.522619; MC not run |
| `runs/v22_ABC_redundant_3012` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.347368e-05 | 1.982566e-05 | 6.329934e-05 | 0.53298 | GF PASS; acc 0.532650; MC not run |
| `runs/v22_ABC_redundant_3021` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.34842e-05 | 2.120613e-05 | 6.469033e-05 | 0.52193 | GF PASS; acc 0.521017; MC not run |
| `runs/v22_ABC_redundant_3102` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 5.758938e-05 | 2.231635e-05 | 7.990573e-05 | 0.51727 | GF PASS; acc 0.517343; MC not run |
| `runs/v22_ABC_redundant_3120` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.350104e-05 | 2.028476e-05 | 6.37858e-05 | 0.52505 | GF PASS; acc 0.524969; MC not run |
| `runs/v22_ABC_redundant_3201` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.307288e-05 | 2.087186e-05 | 6.394474e-05 | 0.51880 | GF PASS; acc 0.518773; MC not run |
| `runs/v22_ABC_redundant_3210` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.321751e-05 | 2.086702e-05 | 6.408453e-05 | 0.51881 | GF PASS; acc 0.518251; MC not run |
| `runs/v22_ABC_seq_012` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 5.832583e-05 | 5.781351e-05 | 0.0001161393 | 0.47322 | GF FAIL; acc 0.474316; MC not run |
| `runs/v22_ABC_seq_021` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 5.443941e-05 | 5.684496e-05 | 0.0001112844 | 0.47324 | GF FAIL; acc 0.474446; MC not run |
| `runs/v22_ABC_seq_102` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 5.860334e-05 | 5.820128e-05 | 0.0001168046 | 0.47324 | GF FAIL; acc 0.473291; MC not run |
| `runs/v22_ABC_seq_120` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 5.279196e-05 | 5.817866e-05 | 0.0001109706 | 0.47182 | GF FAIL; acc 0.471546; MC not run |
| `runs/v22_ABC_seq_201` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 4.838997e-05 | 5.64381e-05 | 0.0001048281 | 0.47182 | GF FAIL; acc 0.472096; MC not run |
| `runs/v22_ABC_seq_210` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 4.751045e-05 | 5.640565e-05 | 0.0001039161 | 0.47183 | GF FAIL; acc 0.471160; MC not run |
| `runs/v22_AB_cat_012` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001239334 | 2.272773e-05 | 0.0001466611 | 0.56385 | GF PASS; acc 0.563361; MC not run |
| `runs/v22_AB_cat_021` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001214587 | 2.26183e-05 | 0.000144077 | 0.56385 | GF PASS; acc 0.563377; MC not run |
| `runs/v22_AB_cat_102` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001204359 | 2.269816e-05 | 0.0001431341 | 0.56385 | GF PASS; acc 0.564305; MC not run |
| `runs/v22_AB_cat_120` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001131683 | 2.358305e-05 | 0.0001367513 | 0.56019 | GF PASS; acc 0.559670; MC not run |
| `runs/v22_AB_cat_201` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001093372 | 2.415829e-05 | 0.0001334955 | 0.55834 | GF PASS; acc 0.558376; MC not run |
| `runs/v22_AB_cat_210` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001006022 | 2.286313e-05 | 0.0001234654 | 0.56244 | GF PASS; acc 0.561558; MC not run |
| `runs/v22_AB_direct_012` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 4.513539e-05 | 2.292515e-05 | 6.806054e-05 | 0.56413 | GF PASS; acc 0.563681; MC not run |
| `runs/v22_AB_direct_021` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 4.50068e-05 | 2.429754e-05 | 6.930434e-05 | 0.55965 | GF PASS; acc 0.559370; MC not run |
| `runs/v22_AB_direct_102` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 5.262868e-05 | 2.518078e-05 | 7.780945e-05 | 0.55742 | GF PASS; acc 0.557231; MC not run |
| `runs/v22_AB_direct_120` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 4.428378e-05 | 2.320324e-05 | 6.748702e-05 | 0.56300 | GF PASS; acc 0.562709; MC not run |
| `runs/v22_AB_direct_201` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 4.324743e-05 | 2.30584e-05 | 6.630583e-05 | 0.56300 | GF PASS; acc 0.562704; MC not run |
| `runs/v22_AB_direct_210` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 4.337288e-05 | 2.30643e-05 | 6.643718e-05 | 0.56300 | GF PASS; acc 0.562774; MC not run |
| `runs/v22_AB_flag_012` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.406997e-05 | 2.590617e-05 | 5.997614e-05 | 0.52664 | GF PASS; acc 0.526676; MC not run |
| `runs/v22_AB_flag_021` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.376197e-05 | 2.727311e-05 | 6.103507e-05 | 0.52142 | GF PASS; acc 0.521517; MC not run |
| `runs/v22_AB_flag_102` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.489768e-05 | 2.814724e-05 | 6.304492e-05 | 0.51832 | GF PASS; acc 0.517736; MC not run |
| `runs/v22_AB_flag_120` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.455158e-05 | 2.626163e-05 | 6.081321e-05 | 0.52558 | GF PASS; acc 0.525184; MC not run |
| `runs/v22_AB_flag_201` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.367806e-05 | 2.613573e-05 | 5.98138e-05 | 0.52558 | GF PASS; acc 0.525172; MC not run |
| `runs/v22_AB_flag_210` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.400698e-05 | 2.615417e-05 | 6.016115e-05 | 0.52558 | GF PASS; acc 0.525318; MC not run |
| `runs/v22_AB_hybrid1_012` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.405616e-05 | 2.552632e-05 | 6.958248e-05 | 0.55645 | GF PASS; acc 0.556020; MC not run |
| `runs/v22_AB_hybrid1_021` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.368663e-05 | 2.542186e-05 | 6.910849e-05 | 0.55646 | GF PASS; acc 0.556683; MC not run |
| `runs/v22_AB_hybrid1_102` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.405616e-05 | 2.552632e-05 | 6.958248e-05 | 0.55645 | GF PASS; acc 0.556020; MC not run |
| `runs/v22_AB_hybrid1_120` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.405616e-05 | 2.552632e-05 | 6.958248e-05 | 0.55645 | GF PASS; acc 0.556020; MC not run |
| `runs/v22_AB_hybrid1_201` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.368663e-05 | 2.542186e-05 | 6.910849e-05 | 0.55646 | GF PASS; acc 0.556683; MC not run |
| `runs/v22_AB_hybrid1_210` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.368663e-05 | 2.542186e-05 | 6.910849e-05 | 0.55646 | GF PASS; acc 0.556683; MC not run |
| `runs/v22_AB_hybrid2_012` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.295983e-05 | 6.442823e-05 | 0.56264 | GF PASS; acc 0.562397; MC not run |
| `runs/v22_AB_hybrid2_021` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.295983e-05 | 6.442823e-05 | 0.56264 | GF PASS; acc 0.562397; MC not run |
| `runs/v22_AB_hybrid2_102` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.295983e-05 | 6.442823e-05 | 0.56264 | GF PASS; acc 0.562397; MC not run |
| `runs/v22_AB_hybrid2_120` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.295983e-05 | 6.442823e-05 | 0.56264 | GF PASS; acc 0.562397; MC not run |
| `runs/v22_AB_hybrid2_201` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.295983e-05 | 6.442823e-05 | 0.56264 | GF PASS; acc 0.562397; MC not run |
| `runs/v22_AB_hybrid2_210` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.295983e-05 | 6.442823e-05 | 0.56264 | GF PASS; acc 0.562397; MC not run |
| `runs/v22_AB_hybrid2t_012` (regenerate) | AB hybrid2t | 123 | 45 | 2.923587e-19 | 5.811305e-05 | 2.439868e-05 | 8.251173e-05 | 0.55819 | GF PASS; acc 0.558113; MC not run |
| `runs/v22_AB_redundant_012` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.111902e-05 | 1.846529e-05 | 5.958431e-05 | 0.55199 | GF PASS; acc 0.551201; MC not run |
| `runs/v22_AB_redundant_021` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.11567e-05 | 1.901766e-05 | 6.017436e-05 | 0.54761 | GF PASS; acc 0.547757; MC not run |
| `runs/v22_AB_redundant_102` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.628505e-05 | 1.953504e-05 | 6.58201e-05 | 0.54543 | GF PASS; acc 0.545356; MC not run |
| `runs/v22_AB_redundant_120` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.114668e-05 | 1.838634e-05 | 5.953301e-05 | 0.55089 | GF PASS; acc 0.549602; MC not run |
| `runs/v22_AB_redundant_201` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.090727e-05 | 1.834065e-05 | 5.924792e-05 | 0.55089 | GF PASS; acc 0.550757; MC not run |
| `runs/v22_AB_redundant_210` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.099574e-05 | 1.834529e-05 | 5.934103e-05 | 0.55089 | GF PASS; acc 0.550233; MC not run |
| `runs/v22_AB_seq_012` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 5.207959e-05 | 4.507255e-05 | 9.715215e-05 | 0.51288 | GF PASS; acc 0.512718; MC not run |
| `runs/v22_AB_seq_021` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 4.920605e-05 | 4.434061e-05 | 9.354666e-05 | 0.51289 | GF PASS; acc 0.513357; MC not run |
| `runs/v22_AB_seq_102` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 5.34074e-05 | 4.537468e-05 | 9.878208e-05 | 0.51289 | GF PASS; acc 0.513018; MC not run |
| `runs/v22_AB_seq_120` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 4.973358e-05 | 4.539978e-05 | 9.513336e-05 | 0.51186 | GF PASS; acc 0.512436; MC not run |
| `runs/v22_AB_seq_201` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 4.535581e-05 | 4.405062e-05 | 8.940643e-05 | 0.51186 | GF PASS; acc 0.511582; MC not run |
| `runs/v22_AB_seq_210` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 4.547939e-05 | 4.41558e-05 | 8.963518e-05 | 0.51187 | GF PASS; acc 0.512417; MC not run |
| `runs/v22_AC_cat_012` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001239334 | 2.267733e-05 | 0.0001466107 | 0.56385 | GF PASS; acc 0.563718; MC not run |
| `runs/v22_AC_cat_021` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001214587 | 2.256782e-05 | 0.0001440265 | 0.56385 | GF PASS; acc 0.563696; MC not run |
| `runs/v22_AC_cat_102` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001204359 | 2.264768e-05 | 0.0001430836 | 0.56385 | GF PASS; acc 0.563196; MC not run |
| `runs/v22_AC_cat_120` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001131683 | 2.353078e-05 | 0.0001366991 | 0.56019 | GF PASS; acc 0.560250; MC not run |
| `runs/v22_AC_cat_201` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001093372 | 2.410561e-05 | 0.0001334428 | 0.55834 | GF PASS; acc 0.557787; MC not run |
| `runs/v22_AC_cat_210` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001006022 | 2.281475e-05 | 0.000123417 | 0.56244 | GF PASS; acc 0.562096; MC not run |
| `runs/v22_AC_direct_012` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 4.513539e-05 | 2.288836e-05 | 6.802376e-05 | 0.56413 | GF PASS; acc 0.564504; MC not run |
| `runs/v22_AC_direct_021` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 4.50068e-05 | 2.425614e-05 | 6.926295e-05 | 0.55965 | GF PASS; acc 0.559959; MC not run |
| `runs/v22_AC_direct_102` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 5.262868e-05 | 2.513641e-05 | 7.776508e-05 | 0.55742 | GF PASS; acc 0.556858; MC not run |
| `runs/v22_AC_direct_120` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 4.428378e-05 | 2.316517e-05 | 6.744894e-05 | 0.56300 | GF PASS; acc 0.562231; MC not run |
| `runs/v22_AC_direct_201` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 4.324743e-05 | 2.302023e-05 | 6.626766e-05 | 0.56300 | GF PASS; acc 0.562252; MC not run |
| `runs/v22_AC_direct_210` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 4.337288e-05 | 2.302617e-05 | 6.639905e-05 | 0.56300 | GF PASS; acc 0.562118; MC not run |
| `runs/v22_AC_flag_012` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.406997e-05 | 2.586972e-05 | 5.993969e-05 | 0.52664 | GF PASS; acc 0.526507; MC not run |
| `runs/v22_AC_flag_021` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.376197e-05 | 2.723323e-05 | 6.099519e-05 | 0.52142 | GF PASS; acc 0.521311; MC not run |
| `runs/v22_AC_flag_102` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.489768e-05 | 2.81063e-05 | 6.300398e-05 | 0.51832 | GF PASS; acc 0.518096; MC not run |
| `runs/v22_AC_flag_120` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.455158e-05 | 2.622389e-05 | 6.077546e-05 | 0.52558 | GF PASS; acc 0.525816; MC not run |
| `runs/v22_AC_flag_201` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.367806e-05 | 2.609793e-05 | 5.977599e-05 | 0.52558 | GF PASS; acc 0.525846; MC not run |
| `runs/v22_AC_flag_210` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.400698e-05 | 2.611639e-05 | 6.012337e-05 | 0.52558 | GF PASS; acc 0.525884; MC not run |
| `runs/v22_AC_hybrid1_012` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.405616e-05 | 2.547677e-05 | 6.953293e-05 | 0.55645 | GF PASS; acc 0.556159; MC not run |
| `runs/v22_AC_hybrid1_021` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.368663e-05 | 2.537231e-05 | 6.905894e-05 | 0.55646 | GF PASS; acc 0.555914; MC not run |
| `runs/v22_AC_hybrid1_102` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.405616e-05 | 2.547677e-05 | 6.953293e-05 | 0.55645 | GF PASS; acc 0.556159; MC not run |
| `runs/v22_AC_hybrid1_120` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.405616e-05 | 2.547677e-05 | 6.953293e-05 | 0.55645 | GF PASS; acc 0.556159; MC not run |
| `runs/v22_AC_hybrid1_201` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.368663e-05 | 2.537231e-05 | 6.905894e-05 | 0.55646 | GF PASS; acc 0.555914; MC not run |
| `runs/v22_AC_hybrid1_210` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.368663e-05 | 2.537231e-05 | 6.905894e-05 | 0.55646 | GF PASS; acc 0.555914; MC not run |
| `runs/v22_AC_hybrid2_012` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.292148e-05 | 6.438988e-05 | 0.56264 | GF PASS; acc 0.562037; MC not run |
| `runs/v22_AC_hybrid2_021` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.292148e-05 | 6.438988e-05 | 0.56264 | GF PASS; acc 0.562037; MC not run |
| `runs/v22_AC_hybrid2_102` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.292148e-05 | 6.438988e-05 | 0.56264 | GF PASS; acc 0.562037; MC not run |
| `runs/v22_AC_hybrid2_120` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.292148e-05 | 6.438988e-05 | 0.56264 | GF PASS; acc 0.562037; MC not run |
| `runs/v22_AC_hybrid2_201` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.292148e-05 | 6.438988e-05 | 0.56264 | GF PASS; acc 0.562037; MC not run |
| `runs/v22_AC_hybrid2_210` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.14684e-05 | 2.292148e-05 | 6.438988e-05 | 0.56264 | GF PASS; acc 0.562037; MC not run |
| `runs/v22_AC_hybrid2t_012` (regenerate) | AC hybrid2t | 123 | 45 | 2.923587e-19 | 5.811305e-05 | 2.435337e-05 | 8.246642e-05 | 0.55819 | GF PASS; acc 0.558037; MC not run |
| `runs/v22_AC_redundant_012` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.111902e-05 | 1.8423e-05 | 5.954201e-05 | 0.55199 | GF PASS; acc 0.551113; MC not run |
| `runs/v22_AC_redundant_021` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.11567e-05 | 1.897084e-05 | 6.012754e-05 | 0.54761 | GF PASS; acc 0.547425; MC not run |
| `runs/v22_AC_redundant_102` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.628505e-05 | 1.948534e-05 | 6.577039e-05 | 0.54543 | GF PASS; acc 0.544969; MC not run |
| `runs/v22_AC_redundant_120` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.114668e-05 | 1.834293e-05 | 5.94896e-05 | 0.55089 | GF PASS; acc 0.550839; MC not run |
| `runs/v22_AC_redundant_201` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.090727e-05 | 1.829716e-05 | 5.920443e-05 | 0.55089 | GF PASS; acc 0.550360; MC not run |
| `runs/v22_AC_redundant_210` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.099574e-05 | 1.830186e-05 | 5.929761e-05 | 0.55089 | GF PASS; acc 0.549950; MC not run |
| `runs/v22_AC_seq_012` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 5.207959e-05 | 4.497898e-05 | 9.705857e-05 | 0.51288 | GF PASS; acc 0.513169; MC not run |
| `runs/v22_AC_seq_021` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 4.920605e-05 | 4.424683e-05 | 9.345288e-05 | 0.51289 | GF PASS; acc 0.513003; MC not run |
| `runs/v22_AC_seq_102` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 5.34074e-05 | 4.528062e-05 | 9.868802e-05 | 0.51289 | GF PASS; acc 0.512885; MC not run |
| `runs/v22_AC_seq_120` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 4.973358e-05 | 4.530443e-05 | 9.503802e-05 | 0.51186 | GF PASS; acc 0.511572; MC not run |
| `runs/v22_AC_seq_201` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 4.535581e-05 | 4.395491e-05 | 8.931071e-05 | 0.51186 | GF PASS; acc 0.511404; MC not run |
| `runs/v22_AC_seq_210` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 4.547939e-05 | 4.406024e-05 | 8.953963e-05 | 0.51187 | GF PASS; acc 0.511627; MC not run |
| `runs/v22_A_cat13_012` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.34246e-05 | 2.074641e-05 | 6.4171e-05 | 0.57979 | GF PASS; acc 0.578917; MC not run |
| `runs/v22_A_cat13_021` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.314968e-05 | 2.165817e-05 | 6.480785e-05 | 0.57748 | GF PASS; acc 0.576988; MC not run |
| `runs/v22_A_cat13_102` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.957042e-05 | 2.226962e-05 | 7.184004e-05 | 0.57633 | GF PASS; acc 0.576207; MC not run |
| `runs/v22_A_cat13_120` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.334882e-05 | 2.096408e-05 | 6.43129e-05 | 0.57921 | GF PASS; acc 0.579341; MC not run |
| `runs/v22_A_cat13_201` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.223177e-05 | 2.086116e-05 | 6.309293e-05 | 0.57921 | GF PASS; acc 0.579379; MC not run |
| `runs/v22_A_cat13_210` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.266357e-05 | 2.08879e-05 | 6.355147e-05 | 0.57921 | GF PASS; acc 0.578937; MC not run |
| `runs/v22_A_cat13red_012` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.242521e-05 | 1.929368e-05 | 6.171889e-05 | 0.56851 | GF PASS; acc 0.567991; MC not run |
| `runs/v22_A_cat13red_0132` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.317538e-05 | 1.941019e-05 | 6.258558e-05 | 0.56772 | GF PASS; acc 0.567393; MC not run |
| `runs/v22_A_cat13red_021` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.254212e-05 | 1.99028e-05 | 6.244492e-05 | 0.56625 | GF PASS; acc 0.565199; MC not run |
| `runs/v22_A_cat13red_0231` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.300865e-05 | 2.007406e-05 | 6.308271e-05 | 0.56527 | GF PASS; acc 0.565245; MC not run |
| `runs/v22_A_cat13red_0312` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.353742e-05 | 1.960365e-05 | 6.314107e-05 | 0.56692 | GF PASS; acc 0.566633; MC not run |
| `runs/v22_A_cat13red_0321` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.345454e-05 | 1.958414e-05 | 6.303868e-05 | 0.56692 | GF PASS; acc 0.566360; MC not run |
| `runs/v22_A_cat13red_102` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.856623e-05 | 2.031038e-05 | 6.887661e-05 | 0.56512 | GF PASS; acc 0.565212; MC not run |
| `runs/v22_A_cat13red_1032` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.337586e-05 | 1.941273e-05 | 6.278858e-05 | 0.56772 | GF PASS; acc 0.567315; MC not run |
| `runs/v22_A_cat13red_120` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.262066e-05 | 1.935333e-05 | 6.197399e-05 | 0.56794 | GF PASS; acc 0.566964; MC not run |
| `runs/v22_A_cat13red_1230` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.2742e-05 | 1.937143e-05 | 6.211343e-05 | 0.56718 | GF PASS; acc 0.566809; MC not run |
| `runs/v22_A_cat13red_1302` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.370795e-05 | 1.993886e-05 | 6.364681e-05 | 0.56565 | GF PASS; acc 0.565023; MC not run |
| `runs/v22_A_cat13red_1320` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.360079e-05 | 1.945883e-05 | 6.305961e-05 | 0.56677 | GF PASS; acc 0.566712; MC not run |
| `runs/v22_A_cat13red_201` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.234042e-05 | 1.929884e-05 | 6.163926e-05 | 0.56794 | GF PASS; acc 0.567731; MC not run |
| `runs/v22_A_cat13red_2031` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.274929e-05 | 1.945748e-05 | 6.220677e-05 | 0.56695 | GF PASS; acc 0.566154; MC not run |
| `runs/v22_A_cat13red_210` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.246964e-05 | 1.932148e-05 | 6.179111e-05 | 0.56794 | GF PASS; acc 0.568161; MC not run |
| `runs/v22_A_cat13red_2130` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.259097e-05 | 1.933837e-05 | 6.192934e-05 | 0.56718 | GF PASS; acc 0.566823; MC not run |
| `runs/v22_A_cat13red_2301` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.269143e-05 | 1.941892e-05 | 6.211035e-05 | 0.56658 | GF PASS; acc 0.566078; MC not run |
| `runs/v22_A_cat13red_2310` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.283815e-05 | 1.942767e-05 | 6.226583e-05 | 0.56658 | GF PASS; acc 0.566279; MC not run |
| `runs/v22_A_cat13red_3012` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.350151e-05 | 1.954412e-05 | 6.304563e-05 | 0.56692 | GF PASS; acc 0.566661; MC not run |
| `runs/v22_A_cat13red_3021` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.366224e-05 | 2.020038e-05 | 6.386263e-05 | 0.56466 | GF PASS; acc 0.564390; MC not run |
| `runs/v22_A_cat13red_3102` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.997034e-05 | 2.059391e-05 | 7.056425e-05 | 0.56354 | GF PASS; acc 0.563230; MC not run |
| `runs/v22_A_cat13red_3120` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.372334e-05 | 1.963164e-05 | 6.335498e-05 | 0.56635 | GF PASS; acc 0.565398; MC not run |
| `runs/v22_A_cat13red_3201` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.334814e-05 | 1.957407e-05 | 6.292221e-05 | 0.56635 | GF PASS; acc 0.565382; MC not run |
| `runs/v22_A_cat13red_3210` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.349487e-05 | 1.958542e-05 | 6.308029e-05 | 0.56636 | GF PASS; acc 0.566388; MC not run |
| `runs/v22_A_cat3_012` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.877359e-05 | 2.175122e-05 | 0.0001205248 | 0.57539 | GF PASS; acc 0.575111; MC not run |
| `runs/v22_A_cat3_021` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.855967e-05 | 2.173181e-05 | 0.0001202915 | 0.57539 | GF PASS; acc 0.575106; MC not run |
| `runs/v22_A_cat3_102` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.885458e-05 | 2.172705e-05 | 0.0001205816 | 0.57539 | GF PASS; acc 0.575096; MC not run |
| `runs/v22_A_cat3_120` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.883347e-05 | 2.256614e-05 | 0.0001213996 | 0.57310 | GF PASS; acc 0.572582; MC not run |
| `runs/v22_A_cat3_201` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.854078e-05 | 2.256023e-05 | 0.000121101 | 0.57310 | GF PASS; acc 0.572583; MC not run |
| `runs/v22_A_cat3_210` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.854424e-05 | 2.253894e-05 | 0.0001210832 | 0.57310 | GF PASS; acc 0.572578; MC not run |
| `runs/v22_A_cat4_012` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001147443 | 2.722287e-05 | 0.0001419672 | 0.56547 | GF PASS; acc 0.565804; MC not run |
| `runs/v22_A_cat4_021` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001134061 | 2.706566e-05 | 0.0001404717 | 0.56547 | GF PASS; acc 0.565811; MC not run |
| `runs/v22_A_cat4_102` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001148038 | 2.72002e-05 | 0.000142004 | 0.56547 | GF PASS; acc 0.565821; MC not run |
| `runs/v22_A_cat4_120` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001134639 | 2.702549e-05 | 0.0001404894 | 0.56547 | GF PASS; acc 0.565042; MC not run |
| `runs/v22_A_cat4_201` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001120702 | 2.686566e-05 | 0.0001389358 | 0.56547 | GF PASS; acc 0.565083; MC not run |
| `runs/v22_A_cat4_210` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001120516 | 2.684776e-05 | 0.0001388993 | 0.56547 | GF PASS; acc 0.565026; MC not run |
| `runs/v22_A_cat_012` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 9.327422e-05 | 1.88134e-05 | 0.0001120876 | 0.58280 | GF PASS; acc 0.582365; MC not run |
| `runs/v22_A_cat_021` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 9.289955e-05 | 1.87575e-05 | 0.000111657 | 0.58280 | GF PASS; acc 0.582362; MC not run |
| `runs/v22_A_cat_102` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 9.34882e-05 | 1.880214e-05 | 0.0001122903 | 0.58280 | GF PASS; acc 0.582463; MC not run |
| `runs/v22_A_cat_120` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 9.348207e-05 | 1.930938e-05 | 0.0001127915 | 0.58091 | GF PASS; acc 0.580847; MC not run |
| `runs/v22_A_cat_201` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 8.905784e-05 | 1.959973e-05 | 0.0001086576 | 0.57995 | GF PASS; acc 0.580172; MC not run |
| `runs/v22_A_cat_210` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 8.490774e-05 | 1.885746e-05 | 0.0001037652 | 0.58207 | GF PASS; acc 0.581825; MC not run |
| `runs/v22_A_catred_012` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001070704 | 1.613704e-05 | 0.0001232075 | 0.57490 | GF PASS; acc 0.574949; MC not run |
| `runs/v22_A_catred_0132` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001089236 | 1.607077e-05 | 0.0001249944 | 0.57490 | GF PASS; acc 0.574374; MC not run |
| `runs/v22_A_catred_021` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.000107087 | 1.610637e-05 | 0.0001231934 | 0.57490 | GF PASS; acc 0.574131; MC not run |
| `runs/v22_A_catred_0231` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.785876e-05 | 1.712644e-05 | 0.0001149852 | 0.57188 | GF PASS; acc 0.570657; MC not run |
| `runs/v22_A_catred_0312` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.93399e-05 | 1.671744e-05 | 0.0001160573 | 0.57360 | GF PASS; acc 0.572762; MC not run |
| `runs/v22_A_catred_0321` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.93399e-05 | 1.670549e-05 | 0.0001160454 | 0.57360 | GF PASS; acc 0.572763; MC not run |
| `runs/v22_A_catred_102` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001049933 | 1.634568e-05 | 0.000121339 | 0.57432 | GF PASS; acc 0.573544; MC not run |
| `runs/v22_A_catred_1032` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001069798 | 1.627611e-05 | 0.0001232559 | 0.57432 | GF PASS; acc 0.574583; MC not run |
| `runs/v22_A_catred_120` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001051725 | 1.672838e-05 | 0.0001219009 | 0.57264 | GF PASS; acc 0.572433; MC not run |
| `runs/v22_A_catred_1230` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.000100853 | 1.640767e-05 | 0.0001172607 | 0.57475 | GF PASS; acc 0.574369; MC not run |
| `runs/v22_A_catred_1302` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001068334 | 1.627516e-05 | 0.0001231086 | 0.57432 | GF PASS; acc 0.574127; MC not run |
| `runs/v22_A_catred_1320` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001090822 | 1.692712e-05 | 0.0001260093 | 0.57188 | GF PASS; acc 0.571732; MC not run |
| `runs/v22_A_catred_201` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001033481 | 1.666032e-05 | 0.0001200084 | 0.57226 | GF PASS; acc 0.571963; MC not run |
| `runs/v22_A_catred_2031` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001048775 | 1.775116e-05 | 0.0001226286 | 0.56869 | GF PASS; acc 0.568010; MC not run |
| `runs/v22_A_catred_210` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.700907e-05 | 1.653267e-05 | 0.0001135417 | 0.57379 | GF PASS; acc 0.573588; MC not run |
| `runs/v22_A_catred_2130` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001008585 | 1.638563e-05 | 0.0001172441 | 0.57474 | GF PASS; acc 0.574547; MC not run |
| `runs/v22_A_catred_2301` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.260544e-05 | 1.66563e-05 | 0.0001092617 | 0.57364 | GF PASS; acc 0.573479; MC not run |
| `runs/v22_A_catred_2310` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.644276e-05 | 1.703517e-05 | 0.0001134779 | 0.57192 | GF PASS; acc 0.571643; MC not run |
| `runs/v22_A_catred_3012` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001025701 | 1.63639e-05 | 0.000118934 | 0.57417 | GF PASS; acc 0.573429; MC not run |
| `runs/v22_A_catred_3021` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001025701 | 1.634419e-05 | 0.0001189143 | 0.57417 | GF PASS; acc 0.573432; MC not run |
| `runs/v22_A_catred_3102` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001023132 | 1.657612e-05 | 0.0001188893 | 0.57321 | GF PASS; acc 0.573052; MC not run |
| `runs/v22_A_catred_3120` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001025395 | 1.692495e-05 | 0.0001194644 | 0.57249 | GF PASS; acc 0.572527; MC not run |
| `runs/v22_A_catred_3201` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.000100859 | 1.715109e-05 | 0.00011801 | 0.57135 | GF PASS; acc 0.571067; MC not run |
| `runs/v22_A_catred_3210` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.386213e-05 | 1.672402e-05 | 0.0001105862 | 0.57364 | GF PASS; acc 0.573719; MC not run |
| `runs/v22_A_direct_012` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.264576e-05 | 1.936065e-05 | 6.20064e-05 | 0.58295 | GF PASS; acc 0.583553; MC not run |
| `runs/v22_A_direct_021` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.237106e-05 | 2.022684e-05 | 6.25979e-05 | 0.58063 | GF PASS; acc 0.579990; MC not run |
| `runs/v22_A_direct_102` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.847782e-05 | 2.08255e-05 | 6.930332e-05 | 0.57947 | GF PASS; acc 0.578658; MC not run |
| `runs/v22_A_direct_120` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.256603e-05 | 1.955963e-05 | 6.212566e-05 | 0.58236 | GF PASS; acc 0.582176; MC not run |
| `runs/v22_A_direct_201` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.144974e-05 | 1.945505e-05 | 6.090479e-05 | 0.58236 | GF PASS; acc 0.582173; MC not run |
| `runs/v22_A_direct_210` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.188138e-05 | 1.948172e-05 | 6.136311e-05 | 0.58236 | GF PASS; acc 0.582661; MC not run |
| `runs/v22_A_flag_012` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.416775e-05 | 2.052289e-05 | 5.469064e-05 | 0.56325 | GF PASS; acc 0.562931; MC not run |
| `runs/v22_A_flag_021` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.385975e-05 | 2.126693e-05 | 5.512668e-05 | 0.56045 | GF PASS; acc 0.560411; MC not run |
| `runs/v22_A_flag_102` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.499546e-05 | 2.177429e-05 | 5.676975e-05 | 0.55879 | GF PASS; acc 0.558638; MC not run |
| `runs/v22_A_flag_120` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.464936e-05 | 2.074524e-05 | 5.53946e-05 | 0.56268 | GF PASS; acc 0.561813; MC not run |
| `runs/v22_A_flag_201` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.377584e-05 | 2.06488e-05 | 5.442464e-05 | 0.56268 | GF PASS; acc 0.561823; MC not run |
| `runs/v22_A_flag_210` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.410476e-05 | 2.068305e-05 | 5.478781e-05 | 0.56268 | GF PASS; acc 0.562457; MC not run |
| `runs/v22_A_hybrid1_012` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.217983e-05 | 2.128607e-05 | 6.34659e-05 | 0.57897 | GF PASS; acc 0.578914; MC not run |
| `runs/v22_A_hybrid1_021` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.1806e-05 | 2.125479e-05 | 6.306079e-05 | 0.57897 | GF PASS; acc 0.578635; MC not run |
| `runs/v22_A_hybrid1_102` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.217983e-05 | 2.128607e-05 | 6.34659e-05 | 0.57897 | GF PASS; acc 0.578914; MC not run |
| `runs/v22_A_hybrid1_120` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.217983e-05 | 2.128607e-05 | 6.34659e-05 | 0.57897 | GF PASS; acc 0.578914; MC not run |
| `runs/v22_A_hybrid1_201` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.1806e-05 | 2.125479e-05 | 6.306079e-05 | 0.57897 | GF PASS; acc 0.578635; MC not run |
| `runs/v22_A_hybrid1_210` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.1806e-05 | 2.125479e-05 | 6.306079e-05 | 0.57897 | GF PASS; acc 0.578635; MC not run |
| `runs/v22_A_hybrid2_012` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.063856e-05 | 1.969098e-05 | 6.032955e-05 | 0.58218 | GF PASS; acc 0.582251; MC not run |
| `runs/v22_A_hybrid2_021` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.063856e-05 | 1.969098e-05 | 6.032955e-05 | 0.58218 | GF PASS; acc 0.582251; MC not run |
| `runs/v22_A_hybrid2_102` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.063856e-05 | 1.969098e-05 | 6.032955e-05 | 0.58218 | GF PASS; acc 0.582251; MC not run |
| `runs/v22_A_hybrid2_120` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.063856e-05 | 1.969098e-05 | 6.032955e-05 | 0.58218 | GF PASS; acc 0.582251; MC not run |
| `runs/v22_A_hybrid2_201` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.063856e-05 | 1.969098e-05 | 6.032955e-05 | 0.58218 | GF PASS; acc 0.582251; MC not run |
| `runs/v22_A_hybrid2_210` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.063856e-05 | 1.969098e-05 | 6.032955e-05 | 0.58218 | GF PASS; acc 0.582251; MC not run |
| `runs/v22_A_hybrid2t_012` (regenerate) | A hybrid2t | 123 | 45 | 2.923587e-19 | 5.484709e-05 | 2.062305e-05 | 7.547014e-05 | 0.57987 | GF PASS; acc 0.578815; MC not run |
| `runs/v22_A_redundant_012` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.112974e-05 | 1.771332e-05 | 5.884306e-05 | 0.57664 | GF PASS; acc 0.576218; MC not run |
| `runs/v22_A_redundant_0132` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.247307e-05 | 1.916632e-05 | 6.16394e-05 | 0.57318 | GF PASS; acc 0.573640; MC not run |
| `runs/v22_A_redundant_021` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.124718e-05 | 1.824624e-05 | 5.949342e-05 | 0.57435 | GF PASS; acc 0.574176; MC not run |
| `runs/v22_A_redundant_0231` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.445853e-05 | 1.852435e-05 | 6.298287e-05 | 0.57374 | GF PASS; acc 0.573437; MC not run |
| `runs/v22_A_redundant_0312` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.260186e-05 | 1.840974e-05 | 6.10116e-05 | 0.57543 | GF PASS; acc 0.574543; MC not run |
| `runs/v22_A_redundant_0321` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.281196e-05 | 1.917239e-05 | 6.198435e-05 | 0.57258 | GF PASS; acc 0.572280; MC not run |
| `runs/v22_A_redundant_102` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.625261e-05 | 1.861894e-05 | 6.487154e-05 | 0.57321 | GF PASS; acc 0.573225; MC not run |
| `runs/v22_A_redundant_1032` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.274333e-05 | 1.915409e-05 | 6.189742e-05 | 0.57318 | GF PASS; acc 0.573264; MC not run |
| `runs/v22_A_redundant_120` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.119512e-05 | 1.772885e-05 | 5.892397e-05 | 0.57606 | GF PASS; acc 0.575872; MC not run |
| `runs/v22_A_redundant_1230` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.131655e-05 | 1.773268e-05 | 5.904922e-05 | 0.57606 | GF PASS; acc 0.575121; MC not run |
| `runs/v22_A_redundant_1302` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.233052e-05 | 1.863849e-05 | 6.0969e-05 | 0.57489 | GF PASS; acc 0.573818; MC not run |
| `runs/v22_A_redundant_1320` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.289193e-05 | 1.899129e-05 | 6.188322e-05 | 0.57260 | GF PASS; acc 0.572102; MC not run |
| `runs/v22_A_redundant_201` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.097785e-05 | 1.768538e-05 | 5.866323e-05 | 0.57606 | GF PASS; acc 0.576067; MC not run |
| `runs/v22_A_redundant_2031` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.428682e-05 | 1.824002e-05 | 6.252684e-05 | 0.57431 | GF PASS; acc 0.574079; MC not run |
| `runs/v22_A_redundant_210` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.104419e-05 | 1.769313e-05 | 5.873731e-05 | 0.57607 | GF PASS; acc 0.575742; MC not run |
| `runs/v22_A_redundant_2130` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.116561e-05 | 1.76963e-05 | 5.886191e-05 | 0.57606 | GF PASS; acc 0.575099; MC not run |
| `runs/v22_A_redundant_2301` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.146475e-05 | 1.763609e-05 | 5.910085e-05 | 0.57660 | GF PASS; acc 0.576098; MC not run |
| `runs/v22_A_redundant_2310` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.427457e-05 | 1.798781e-05 | 6.226237e-05 | 0.57488 | GF PASS; acc 0.574648; MC not run |
| `runs/v22_A_redundant_3012` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.220191e-05 | 1.763901e-05 | 5.984092e-05 | 0.57830 | GF PASS; acc 0.578074; MC not run |
| `runs/v22_A_redundant_3021` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.234588e-05 | 1.865334e-05 | 6.099921e-05 | 0.57428 | GF PASS; acc 0.573840; MC not run |
| `runs/v22_A_redundant_3102` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 5.320163e-05 | 1.917533e-05 | 7.237697e-05 | 0.57258 | GF PASS; acc 0.571569; MC not run |
| `runs/v22_A_redundant_3120` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.296379e-05 | 1.817677e-05 | 6.114056e-05 | 0.57543 | GF PASS; acc 0.574667; MC not run |
| `runs/v22_A_redundant_3201` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.251821e-05 | 1.866494e-05 | 6.118315e-05 | 0.57314 | GF PASS; acc 0.572014; MC not run |
| `runs/v22_A_redundant_3210` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.283967e-05 | 1.867418e-05 | 6.151384e-05 | 0.57314 | GF PASS; acc 0.572402; MC not run |
| `runs/v22_A_seq_012` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.602003e-05 | 3.310938e-05 | 7.912941e-05 | 0.55586 | GF PASS; acc 0.555972; MC not run |
| `runs/v22_A_seq_021` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.415047e-05 | 3.258979e-05 | 7.674025e-05 | 0.55586 | GF PASS; acc 0.555497; MC not run |
| `runs/v22_A_seq_102` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.839813e-05 | 3.334882e-05 | 8.174695e-05 | 0.55586 | GF PASS; acc 0.555743; MC not run |
| `runs/v22_A_seq_120` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.687077e-05 | 3.33882e-05 | 8.025897e-05 | 0.55531 | GF PASS; acc 0.555405; MC not run |
| `runs/v22_A_seq_201` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.249942e-05 | 3.246473e-05 | 7.496414e-05 | 0.55531 | GF PASS; acc 0.555640; MC not run |
| `runs/v22_A_seq_210` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.363499e-05 | 3.268912e-05 | 7.632411e-05 | 0.55531 | GF PASS; acc 0.554697; MC not run |
| `runs/v22_BC_cat13_012` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.121414e-05 | 1.886757e-05 | 6.008171e-05 | 0.55804 | GF PASS; acc 0.557912; MC not run |
| `runs/v22_BC_cat13_021` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.187109e-05 | 1.934262e-05 | 6.121371e-05 | 0.55360 | GF PASS; acc 0.553492; MC not run |
| `runs/v22_BC_cat13_102` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.138326e-05 | 1.975774e-05 | 6.1141e-05 | 0.55140 | GF PASS; acc 0.551356; MC not run |
| `runs/v22_BC_cat13_120` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.11966e-05 | 1.891654e-05 | 6.011314e-05 | 0.55692 | GF PASS; acc 0.556987; MC not run |
| `runs/v22_BC_cat13_201` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.170279e-05 | 1.87922e-05 | 6.049499e-05 | 0.55692 | GF PASS; acc 0.556930; MC not run |
| `runs/v22_BC_cat13_210` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.165811e-05 | 1.879886e-05 | 6.045697e-05 | 0.55692 | GF PASS; acc 0.556367; MC not run |
| `runs/v22_BC_cat13red_012` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.835695e-05 | 1.334835e-05 | 5.17053e-05 | 0.53654 | GF PASS; acc 0.536484; MC not run |
| `runs/v22_BC_cat13red_0132` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.816187e-05 | 1.320819e-05 | 5.137006e-05 | 0.53504 | GF PASS; acc 0.534496; MC not run |
| `runs/v22_BC_cat13red_021` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.835612e-05 | 1.336316e-05 | 5.171928e-05 | 0.53228 | GF PASS; acc 0.532167; MC not run |
| `runs/v22_BC_cat13red_0231` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.832069e-05 | 1.305155e-05 | 5.137223e-05 | 0.53043 | GF PASS; acc 0.529438; MC not run |
| `runs/v22_BC_cat13red_0312` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.824631e-05 | 1.278383e-05 | 5.103014e-05 | 0.53354 | GF PASS; acc 0.532931; MC not run |
| `runs/v22_BC_cat13red_0321` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.824631e-05 | 1.276787e-05 | 5.101418e-05 | 0.53354 | GF PASS; acc 0.533996; MC not run |
| `runs/v22_BC_cat13red_102` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.85539e-05 | 1.355171e-05 | 5.210562e-05 | 0.53015 | GF PASS; acc 0.529332; MC not run |
| `runs/v22_BC_cat13red_1032` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.817076e-05 | 1.320189e-05 | 5.137265e-05 | 0.53504 | GF PASS; acc 0.534307; MC not run |
| `runs/v22_BC_cat13red_120` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.862308e-05 | 1.321359e-05 | 5.183668e-05 | 0.53545 | GF PASS; acc 0.535327; MC not run |
| `runs/v22_BC_cat13red_1230` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.871174e-05 | 1.323522e-05 | 5.194696e-05 | 0.53403 | GF PASS; acc 0.533076; MC not run |
| `runs/v22_BC_cat13red_1302` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.817076e-05 | 1.338703e-05 | 5.155779e-05 | 0.53114 | GF PASS; acc 0.530571; MC not run |
| `runs/v22_BC_cat13red_1320` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.832151e-05 | 1.31091e-05 | 5.143062e-05 | 0.53326 | GF PASS; acc 0.533398; MC not run |
| [runs/v22_BC_cat13red_201](runs/v22_BC_cat13red_201.qasm) · [JSON](runs/v22_BC_cat13red_201.json) · [receipt](runs/v22_BC_cat13red_201.result.json) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.836584e-05 | 1.321755e-05 | 5.158339e-05 | 0.53546 | GF PASS; acc 0.534756; MC mean 5.221714e-05 |
| `runs/v22_BC_cat13red_2031` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.83304e-05 | 1.290171e-05 | 5.123211e-05 | 0.53360 | GF PASS; acc 0.533182; MC not run |
| `runs/v22_BC_cat13red_210` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.862308e-05 | 1.321598e-05 | 5.183906e-05 | 0.53546 | GF PASS; acc 0.534828; MC not run |
| `runs/v22_BC_cat13red_2130` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.871174e-05 | 1.323825e-05 | 5.194999e-05 | 0.53404 | GF PASS; acc 0.533603; MC not run |
| `runs/v22_BC_cat13red_2301` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.849005e-05 | 1.292027e-05 | 5.141032e-05 | 0.53290 | GF PASS; acc 0.532736; MC not run |
| `runs/v22_BC_cat13red_2310` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.86408e-05 | 1.291894e-05 | 5.155975e-05 | 0.53290 | GF PASS; acc 0.532267; MC not run |
| `runs/v22_BC_cat13red_3012` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.824631e-05 | 1.279584e-05 | 5.104215e-05 | 0.53354 | GF PASS; acc 0.533238; MC not run |
| `runs/v22_BC_cat13red_3021` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.824631e-05 | 1.283192e-05 | 5.107824e-05 | 0.52930 | GF PASS; acc 0.528856; MC not run |
| `runs/v22_BC_cat13red_3102` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.837298e-05 | 1.300271e-05 | 5.137569e-05 | 0.52719 | GF PASS; acc 0.526494; MC not run |
| `runs/v22_BC_cat13red_3120` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.833485e-05 | 1.267466e-05 | 5.100951e-05 | 0.53247 | GF PASS; acc 0.532336; MC not run |
| [runs/v22_BC_cat13red_3201](runs/v22_BC_cat13red_3201.qasm) · [JSON](runs/v22_BC_cat13red_3201.json) · [receipt](runs/v22_BC_cat13red_3201.result.json) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.82552e-05 | 1.266277e-05 | 5.091797e-05 | 0.53247 | GF PASS; acc 0.532287; MC mean 5.170396e-05 |
| `runs/v22_BC_cat13red_3210` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.840596e-05 | 1.265979e-05 | 5.106575e-05 | 0.53247 | GF PASS; acc 0.532316; MC not run |
| `runs/v22_BC_cat13red_m3_0123` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.920637e-05 | 1.404671e-05 | 5.325308e-05 | 0.54771 | GF PASS; acc 0.547295; MC not run |
| `runs/v22_BC_cat13red_m3_0132` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.935731e-05 | 1.491712e-05 | 5.427442e-05 | 0.53299 | GF PASS; acc 0.532693; MC not run |
| `runs/v22_BC_cat13red_m3_0213` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.953502e-05 | 1.426533e-05 | 5.380035e-05 | 0.54119 | GF PASS; acc 0.540827; MC not run |
| `runs/v22_BC_cat13red_m3_0231` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.983144e-05 | 1.472748e-05 | 5.455892e-05 | 0.53008 | GF PASS; acc 0.530476; MC not run |
| `runs/v22_BC_cat13red_m3_0312` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.944092e-05 | 1.447934e-05 | 5.392027e-05 | 0.52945 | GF PASS; acc 0.529671; MC not run |
| `runs/v22_BC_cat13red_m3_0321` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.960958e-05 | 1.45025e-05 | 5.411207e-05 | 0.52945 | GF PASS; acc 0.529322; MC not run |
| `runs/v22_BC_cat13red_m3_1023` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.940415e-05 | 1.423713e-05 | 5.364128e-05 | 0.54119 | GF PASS; acc 0.540420; MC not run |
| `runs/v22_BC_cat13red_m3_1032` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.985378e-05 | 1.509123e-05 | 5.494501e-05 | 0.52981 | GF PASS; acc 0.529923; MC not run |
| `runs/v22_BC_cat13red_m3_1203` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.954836e-05 | 1.434627e-05 | 5.389463e-05 | 0.54444 | GF PASS; acc 0.544542; MC not run |
| `runs/v22_BC_cat13red_m3_1230` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.954836e-05 | 1.435628e-05 | 5.390463e-05 | 0.54372 | GF PASS; acc 0.543971; MC not run |
| `runs/v22_BC_cat13red_m3_1302` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.955426e-05 | 1.508323e-05 | 5.463749e-05 | 0.53017 | GF PASS; acc 0.529712; MC not run |
| `runs/v22_BC_cat13red_m3_1320` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.972478e-05 | 1.496173e-05 | 5.46865e-05 | 0.53157 | GF PASS; acc 0.531262; MC not run |
| `runs/v22_BC_cat13red_m3_2013` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.011665e-05 | 1.491395e-05 | 5.50306e-05 | 0.54444 | GF PASS; acc 0.543950; MC not run |
| `runs/v22_BC_cat13red_m3_2031` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.056489e-05 | 1.519334e-05 | 5.575823e-05 | 0.53113 | GF PASS; acc 0.531543; MC not run |
| `runs/v22_BC_cat13red_m3_2103` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.025665e-05 | 1.496425e-05 | 5.522091e-05 | 0.54119 | GF PASS; acc 0.540940; MC not run |
| `runs/v22_BC_cat13red_m3_2130` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.004554e-05 | 1.496118e-05 | 5.500672e-05 | 0.54155 | GF PASS; acc 0.541773; MC not run |
| `runs/v22_BC_cat13red_m3_2301` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.005425e-05 | 1.47323e-05 | 5.478655e-05 | 0.54076 | GF PASS; acc 0.540962; MC not run |
| `runs/v22_BC_cat13red_m3_2310` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.038232e-05 | 1.503023e-05 | 5.541255e-05 | 0.53361 | GF PASS; acc 0.533620; MC not run |
| `runs/v22_BC_cat13red_m3_3012` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.935286e-05 | 1.425663e-05 | 5.360949e-05 | 0.53689 | GF PASS; acc 0.536642; MC not run |
| `runs/v22_BC_cat13red_m3_3021` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.960958e-05 | 1.45074e-05 | 5.411697e-05 | 0.52945 | GF PASS; acc 0.529238; MC not run |
| `runs/v22_BC_cat13red_m3_3102` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.952759e-05 | 1.464173e-05 | 5.416932e-05 | 0.52665 | GF PASS; acc 0.525979; MC not run |
| `runs/v22_BC_cat13red_m3_3120` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.972033e-05 | 1.434408e-05 | 5.406442e-05 | 0.53192 | GF PASS; acc 0.531364; MC not run |
| `runs/v22_BC_cat13red_m3_3201` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.990676e-05 | 1.470424e-05 | 5.461101e-05 | 0.53299 | GF PASS; acc 0.533213; MC not run |
| `runs/v22_BC_cat13red_m3_3210` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.004863e-05 | 1.469745e-05 | 5.474608e-05 | 0.53299 | GF PASS; acc 0.532377; MC not run |
| `runs/v22_BC_cat13red_m5_0123` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.818415e-05 | 1.453279e-05 | 5.271694e-05 | 0.54844 | GF PASS; acc 0.547785; MC not run |
| `runs/v22_BC_cat13red_m5_0132` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.905387e-05 | 1.559912e-05 | 5.4653e-05 | 0.53115 | GF PASS; acc 0.530847; MC not run |
| `runs/v22_BC_cat13red_m5_0213` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.842415e-05 | 1.461531e-05 | 5.303946e-05 | 0.54191 | GF PASS; acc 0.541492; MC not run |
| `runs/v22_BC_cat13red_m5_0231` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.8627e-05 | 1.51222e-05 | 5.37492e-05 | 0.53157 | GF PASS; acc 0.532011; MC not run |
| `runs/v22_BC_cat13red_m5_0312` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.886276e-05 | 1.502122e-05 | 5.388398e-05 | 0.53263 | GF PASS; acc 0.532795; MC not run |
| `runs/v22_BC_cat13red_m5_0321` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.867426e-05 | 1.486777e-05 | 5.354203e-05 | 0.53157 | GF PASS; acc 0.531475; MC not run |
| `runs/v22_BC_cat13red_m5_1023` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.856193e-05 | 1.557085e-05 | 5.413278e-05 | 0.54191 | GF PASS; acc 0.541680; MC not run |
| `runs/v22_BC_cat13red_m5_1032` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.932238e-05 | 1.616272e-05 | 5.54851e-05 | 0.53115 | GF PASS; acc 0.530296; MC not run |
| `runs/v22_BC_cat13red_m5_1203` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.835971e-05 | 1.50178e-05 | 5.337751e-05 | 0.54516 | GF PASS; acc 0.544457; MC not run |
| `runs/v22_BC_cat13red_m5_1230` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.835971e-05 | 1.502086e-05 | 5.338057e-05 | 0.54516 | GF PASS; acc 0.544495; MC not run |
| `runs/v22_BC_cat13red_m5_1302` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.932238e-05 | 1.616429e-05 | 5.548667e-05 | 0.53115 | GF PASS; acc 0.531256; MC not run |
| `runs/v22_BC_cat13red_m5_1320` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.873847e-05 | 1.586595e-05 | 5.460441e-05 | 0.53149 | GF PASS; acc 0.530221; MC not run |
| `runs/v22_BC_cat13red_m5_2013` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.861304e-05 | 1.450948e-05 | 5.312252e-05 | 0.54190 | GF PASS; acc 0.541677; MC not run |
| `runs/v22_BC_cat13red_m5_2031` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.907183e-05 | 1.48787e-05 | 5.395053e-05 | 0.53582 | GF PASS; acc 0.535779; MC not run |
| `runs/v22_BC_cat13red_m5_2103` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.865748e-05 | 1.476853e-05 | 5.342602e-05 | 0.54190 | GF PASS; acc 0.542016; MC not run |
| `runs/v22_BC_cat13red_m5_2130` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.865748e-05 | 1.477227e-05 | 5.342975e-05 | 0.54190 | GF PASS; acc 0.541998; MC not run |
| `runs/v22_BC_cat13red_m5_2301` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.853894e-05 | 1.465775e-05 | 5.319668e-05 | 0.54119 | GF PASS; acc 0.541390; MC not run |
| `runs/v22_BC_cat13red_m5_2310` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.872033e-05 | 1.510032e-05 | 5.382065e-05 | 0.53333 | GF PASS; acc 0.533553; MC not run |
| `runs/v22_BC_cat13red_m5_3012` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.824187e-05 | 1.479063e-05 | 5.303249e-05 | 0.53796 | GF PASS; acc 0.537806; MC not run |
| `runs/v22_BC_cat13red_m5_3021` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.867426e-05 | 1.486973e-05 | 5.354399e-05 | 0.53157 | GF PASS; acc 0.531191; MC not run |
| `runs/v22_BC_cat13red_m5_3102` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.844549e-05 | 1.575132e-05 | 5.419681e-05 | 0.52875 | GF PASS; acc 0.528819; MC not run |
| `runs/v22_BC_cat13red_m5_3120` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.832513e-05 | 1.515946e-05 | 5.34846e-05 | 0.53298 | GF PASS; acc 0.532478; MC not run |
| `runs/v22_BC_cat13red_m5_3201` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.836549e-05 | 1.457663e-05 | 5.294211e-05 | 0.53192 | GF PASS; acc 0.531563; MC not run |
| `runs/v22_BC_cat13red_m5_3210` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.836958e-05 | 1.4717e-05 | 5.308658e-05 | 0.53192 | GF PASS; acc 0.531796; MC not run |
| `runs/v22_BC_cat13red_m6_0123` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.013858e-05 | 1.49861e-05 | 5.512468e-05 | 0.54844 | GF PASS; acc 0.548167; MC not run |
| `runs/v22_BC_cat13red_m6_0132` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.247218e-05 | 1.670622e-05 | 5.91784e-05 | 0.52311 | GF PASS; acc 0.523369; MC not run |
| `runs/v22_BC_cat13red_m6_0213` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.061589e-05 | 1.54648e-05 | 5.608068e-05 | 0.54191 | GF PASS; acc 0.542373; MC not run |
| `runs/v22_BC_cat13red_m6_0231` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.061589e-05 | 1.546369e-05 | 5.607958e-05 | 0.54191 | GF PASS; acc 0.542383; MC not run |
| `runs/v22_BC_cat13red_m6_0312` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.075459e-05 | 1.598124e-05 | 5.673582e-05 | 0.53256 | GF PASS; acc 0.532748; MC not run |
| `runs/v22_BC_cat13red_m6_0321` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.093061e-05 | 1.632312e-05 | 5.725373e-05 | 0.52554 | GF PASS; acc 0.524702; MC not run |
| `runs/v22_BC_cat13red_m6_1023` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.017215e-05 | 1.477815e-05 | 5.49503e-05 | 0.54191 | GF PASS; acc 0.541584; MC not run |
| `runs/v22_BC_cat13red_m6_1032` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.161609e-05 | 1.614163e-05 | 5.775772e-05 | 0.52206 | GF PASS; acc 0.522207; MC not run |
| `runs/v22_BC_cat13red_m6_1203` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.008993e-05 | 1.448056e-05 | 5.457049e-05 | 0.54516 | GF PASS; acc 0.544319; MC not run |
| `runs/v22_BC_cat13red_m6_1230` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.020735e-05 | 1.487056e-05 | 5.507791e-05 | 0.53689 | GF PASS; acc 0.536850; MC not run |
| `runs/v22_BC_cat13red_m6_1302` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.094616e-05 | 1.555346e-05 | 5.649962e-05 | 0.52352 | GF PASS; acc 0.523774; MC not run |
| `runs/v22_BC_cat13red_m6_1320` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.087084e-05 | 1.512974e-05 | 5.600058e-05 | 0.52561 | GF PASS; acc 0.525553; MC not run |
| `runs/v22_BC_cat13red_m6_2013` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.04166e-05 | 1.478045e-05 | 5.519704e-05 | 0.54190 | GF PASS; acc 0.541592; MC not run |
| `runs/v22_BC_cat13red_m6_2031` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.04166e-05 | 1.4779e-05 | 5.519559e-05 | 0.54190 | GF PASS; acc 0.541606; MC not run |
| `runs/v22_BC_cat13red_m6_2103` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.034548e-05 | 1.452504e-05 | 5.487052e-05 | 0.54190 | GF PASS; acc 0.541343; MC not run |
| `runs/v22_BC_cat13red_m6_2130` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.057346e-05 | 1.489132e-05 | 5.546478e-05 | 0.53582 | GF PASS; acc 0.535770; MC not run |
| `runs/v22_BC_cat13red_m6_2301` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.006255e-05 | 1.508684e-05 | 5.514939e-05 | 0.53547 | GF PASS; acc 0.534924; MC not run |
| `runs/v22_BC_cat13red_m6_2310` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 3.99518e-05 | 1.46624e-05 | 5.461419e-05 | 0.54119 | GF PASS; acc 0.541427; MC not run |
| `runs/v22_BC_cat13red_m6_3012` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.000454e-05 | 1.527175e-05 | 5.527629e-05 | 0.53405 | GF PASS; acc 0.534142; MC not run |
| `runs/v22_BC_cat13red_m6_3021` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.018092e-05 | 1.560498e-05 | 5.57859e-05 | 0.52701 | GF PASS; acc 0.526602; MC not run |
| `runs/v22_BC_cat13red_m6_3102` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.010478e-05 | 1.530134e-05 | 5.540612e-05 | 0.52875 | GF PASS; acc 0.528793; MC not run |
| `runs/v22_BC_cat13red_m6_3120` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 3.97739e-05 | 1.46954e-05 | 5.44693e-05 | 0.53298 | GF PASS; acc 0.532485; MC not run |
| `runs/v22_BC_cat13red_m6_3201` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 3.979531e-05 | 1.487207e-05 | 5.466739e-05 | 0.52806 | GF PASS; acc 0.527485; MC not run |
| `runs/v22_BC_cat13red_m6_3210` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 3.986174e-05 | 1.473341e-05 | 5.459515e-05 | 0.52806 | GF PASS; acc 0.527779; MC not run |
| `runs/v22_BC_cat3_012` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.1968e-05 | 2.091778e-05 | 7.288578e-05 | 0.54960 | GF PASS; acc 0.549768; MC not run |
| `runs/v22_BC_cat3_021` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.221689e-05 | 2.083735e-05 | 7.305424e-05 | 0.54960 | GF PASS; acc 0.549750; MC not run |
| `runs/v22_BC_cat3_102` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.129292e-05 | 2.094605e-05 | 7.223897e-05 | 0.54960 | GF PASS; acc 0.549744; MC not run |
| `runs/v22_BC_cat3_120` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.175479e-05 | 2.143145e-05 | 7.318624e-05 | 0.54522 | GF PASS; acc 0.545476; MC not run |
| `runs/v22_BC_cat3_201` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.257209e-05 | 2.131329e-05 | 7.388538e-05 | 0.54522 | GF PASS; acc 0.545527; MC not run |
| `runs/v22_BC_cat3_210` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.207467e-05 | 2.134698e-05 | 7.342164e-05 | 0.54522 | GF PASS; acc 0.545502; MC not run |
| `runs/v22_BC_cat3red_0123` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 5.03147e-05 | 1.267413e-05 | 6.298883e-05 | 0.53102 | GF PASS; acc 0.530931; MC not run |
| `runs/v22_BC_cat3red_0132` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 5.077366e-05 | 1.283456e-05 | 6.360822e-05 | 0.52756 | GF PASS; acc 0.527071; MC not run |
| `runs/v22_BC_cat3red_0213` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 5.03147e-05 | 1.266277e-05 | 6.297747e-05 | 0.53102 | GF PASS; acc 0.530906; MC not run |
| `runs/v22_BC_cat3red_0231` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.954845e-05 | 1.325271e-05 | 6.280115e-05 | 0.51920 | GF PASS; acc 0.519795; MC not run |
| `runs/v22_BC_cat3red_0312` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.817455e-05 | 1.324047e-05 | 6.141502e-05 | 0.52204 | GF PASS; acc 0.521747; MC not run |
| `runs/v22_BC_cat3red_0321` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.817455e-05 | 1.324365e-05 | 6.14182e-05 | 0.52204 | GF PASS; acc 0.521773; MC not run |
| `runs/v22_BC_cat3red_1023` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.96379e-05 | 1.268436e-05 | 6.232226e-05 | 0.52995 | GF PASS; acc 0.529739; MC not run |
| `runs/v22_BC_cat3red_1032` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 5.009686e-05 | 1.284189e-05 | 6.293876e-05 | 0.52651 | GF PASS; acc 0.526339; MC not run |
| `runs/v22_BC_cat3red_1203` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.974457e-05 | 1.279459e-05 | 6.253916e-05 | 0.52573 | GF PASS; acc 0.525707; MC not run |
| `runs/v22_BC_cat3red_1230` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.974457e-05 | 1.279913e-05 | 6.25437e-05 | 0.52573 | GF PASS; acc 0.525701; MC not run |
| `runs/v22_BC_cat3red_1302` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.944225e-05 | 1.276372e-05 | 6.220597e-05 | 0.52967 | GF PASS; acc 0.529641; MC not run |
| `runs/v22_BC_cat3red_1320` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 5.020771e-05 | 1.306819e-05 | 6.327589e-05 | 0.52267 | GF PASS; acc 0.521778; MC not run |
| `runs/v22_BC_cat3red_2013` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.96379e-05 | 1.269607e-05 | 6.233397e-05 | 0.52995 | GF PASS; acc 0.529329; MC not run |
| `runs/v22_BC_cat3red_2031` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.954845e-05 | 1.338755e-05 | 6.2936e-05 | 0.51507 | GF PASS; acc 0.515140; MC not run |
| `runs/v22_BC_cat3red_2103` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.974457e-05 | 1.279918e-05 | 6.254375e-05 | 0.52573 | GF PASS; acc 0.525731; MC not run |
| `runs/v22_BC_cat3red_2130` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.974457e-05 | 1.280441e-05 | 6.254897e-05 | 0.52573 | GF PASS; acc 0.525728; MC not run |
| `runs/v22_BC_cat3red_2301` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.953102e-05 | 1.309309e-05 | 6.262412e-05 | 0.52232 | GF PASS; acc 0.521778; MC not run |
| `runs/v22_BC_cat3red_2310` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.944237e-05 | 1.320424e-05 | 6.264662e-05 | 0.51747 | GF PASS; acc 0.517720; MC not run |
| `runs/v22_BC_cat3red_3012` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.808602e-05 | 1.295555e-05 | 6.104157e-05 | 0.52939 | GF PASS; acc 0.529175; MC not run |
| `runs/v22_BC_cat3red_3021` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.808602e-05 | 1.295869e-05 | 6.104471e-05 | 0.52939 | GF PASS; acc 0.529153; MC not run |
| `runs/v22_BC_cat3red_3102` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.792625e-05 | 1.304922e-05 | 6.097548e-05 | 0.52448 | GF PASS; acc 0.524716; MC not run |
| `runs/v22_BC_cat3red_3120` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.801491e-05 | 1.325868e-05 | 6.127359e-05 | 0.52065 | GF PASS; acc 0.520408; MC not run |
| `runs/v22_BC_cat3red_3201` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.817467e-05 | 1.314361e-05 | 6.131827e-05 | 0.52553 | GF PASS; acc 0.525756; MC not run |
| `runs/v22_BC_cat3red_3210` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.808602e-05 | 1.324504e-05 | 6.133106e-05 | 0.52065 | GF PASS; acc 0.520401; MC not run |
| `runs/v22_BC_cat3reusered_0123` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.912959e-05 | 1.901221e-05 | 6.814181e-05 | 0.44498 | GF FAIL; acc 0.444531; MC not run |
| `runs/v22_BC_cat3reusered_0132` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.869001e-05 | 1.934386e-05 | 6.803387e-05 | 0.44592 | GF FAIL; acc 0.445356; MC not run |
| `runs/v22_BC_cat3reusered_0213` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.912959e-05 | 1.891096e-05 | 6.804056e-05 | 0.44498 | GF FAIL; acc 0.445106; MC not run |
| `runs/v22_BC_cat3reusered_0231` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.914987e-05 | 1.905214e-05 | 6.820201e-05 | 0.44592 | GF FAIL; acc 0.446330; MC not run |
| `runs/v22_BC_cat3reusered_0312` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.94903e-05 | 1.950136e-05 | 6.899166e-05 | 0.44687 | GF FAIL; acc 0.446320; MC not run |
| `runs/v22_BC_cat3reusered_0321` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.002044e-05 | 1.928121e-05 | 6.930165e-05 | 0.44687 | GF FAIL; acc 0.446918; MC not run |
| `runs/v22_BC_cat3reusered_1023` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.912959e-05 | 1.91526e-05 | 6.828219e-05 | 0.44499 | GF FAIL; acc 0.445464; MC not run |
| `runs/v22_BC_cat3reusered_1032` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.869001e-05 | 1.94783e-05 | 6.816831e-05 | 0.44593 | GF FAIL; acc 0.445570; MC not run |
| `runs/v22_BC_cat3reusered_1203` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.069108e-05 | 1.919114e-05 | 6.988222e-05 | 0.44500 | GF FAIL; acc 0.445400; MC not run |
| `runs/v22_BC_cat3reusered_1230` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.122193e-05 | 1.92858e-05 | 7.050773e-05 | 0.44498 | GF FAIL; acc 0.445681; MC not run |
| `runs/v22_BC_cat3reusered_1302` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.869001e-05 | 1.957325e-05 | 6.826326e-05 | 0.44592 | GF FAIL; acc 0.446304; MC not run |
| `runs/v22_BC_cat3reusered_1320` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.948628e-05 | 1.937819e-05 | 6.886447e-05 | 0.44592 | GF FAIL; acc 0.445542; MC not run |
| `runs/v22_BC_cat3reusered_2013` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.912959e-05 | 1.931355e-05 | 6.844314e-05 | 0.44499 | GF FAIL; acc 0.445459; MC not run |
| `runs/v22_BC_cat3reusered_2031` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.914987e-05 | 1.945146e-05 | 6.860132e-05 | 0.44593 | GF FAIL; acc 0.446666; MC not run |
| `runs/v22_BC_cat3reusered_2103` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.069108e-05 | 1.945337e-05 | 7.014445e-05 | 0.44500 | GF FAIL; acc 0.445444; MC not run |
| `runs/v22_BC_cat3reusered_2130` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.122193e-05 | 1.954888e-05 | 7.077081e-05 | 0.44498 | GF FAIL; acc 0.445705; MC not run |
| `runs/v22_BC_cat3reusered_2301` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.019086e-05 | 1.953223e-05 | 6.972309e-05 | 0.44592 | GF FAIL; acc 0.445351; MC not run |
| `runs/v22_BC_cat3reusered_2310` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.045699e-05 | 1.955428e-05 | 7.001127e-05 | 0.44592 | GF FAIL; acc 0.445133; MC not run |
| `runs/v22_BC_cat3reusered_3012` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.94903e-05 | 1.951743e-05 | 6.900773e-05 | 0.44686 | GF FAIL; acc 0.446425; MC not run |
| `runs/v22_BC_cat3reusered_3021` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.002044e-05 | 1.929846e-05 | 6.931889e-05 | 0.44686 | GF FAIL; acc 0.446603; MC not run |
| `runs/v22_BC_cat3reusered_3102` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.845001e-05 | 1.952486e-05 | 6.797487e-05 | 0.44686 | GF FAIL; acc 0.446171; MC not run |
| `runs/v22_BC_cat3reusered_3120` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.924628e-05 | 1.932466e-05 | 6.857094e-05 | 0.44687 | GF FAIL; acc 0.445936; MC not run |
| `runs/v22_BC_cat3reusered_3201` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.002044e-05 | 1.919202e-05 | 6.921246e-05 | 0.44686 | GF FAIL; acc 0.447530; MC not run |
| `runs/v22_BC_cat3reusered_3210` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.028657e-05 | 1.921035e-05 | 6.949692e-05 | 0.44687 | GF FAIL; acc 0.446524; MC not run |
| `runs/v22_BC_cat3spinered_0123` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.193416e-05 | 1.897447e-05 | 7.090863e-05 | 0.44686 | GF FAIL; acc 0.447463; MC not run |
| `runs/v22_BC_cat3spinered_0132` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.166873e-05 | 1.927023e-05 | 7.093896e-05 | 0.44686 | GF FAIL; acc 0.447038; MC not run |
| `runs/v22_BC_cat3spinered_0213` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.193416e-05 | 1.855571e-05 | 7.048986e-05 | 0.44686 | GF FAIL; acc 0.446549; MC not run |
| `runs/v22_BC_cat3spinered_0231` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.220403e-05 | 1.863126e-05 | 7.083529e-05 | 0.44686 | GF FAIL; acc 0.446684; MC not run |
| `runs/v22_BC_cat3spinered_0312` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.267417e-05 | 1.917445e-05 | 7.184861e-05 | 0.44686 | GF FAIL; acc 0.447091; MC not run |
| `runs/v22_BC_cat3spinered_0321` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.320946e-05 | 1.895418e-05 | 7.216364e-05 | 0.44686 | GF FAIL; acc 0.446525; MC not run |
| `runs/v22_BC_cat3spinered_1023` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.193416e-05 | 1.898324e-05 | 7.091739e-05 | 0.44686 | GF FAIL; acc 0.447081; MC not run |
| `runs/v22_BC_cat3spinered_1032` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.166873e-05 | 1.92752e-05 | 7.094393e-05 | 0.44686 | GF FAIL; acc 0.447397; MC not run |
| `runs/v22_BC_cat3spinered_1203` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.344231e-05 | 1.861753e-05 | 7.205984e-05 | 0.44686 | GF FAIL; acc 0.447123; MC not run |
| `runs/v22_BC_cat3spinered_1230` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.39776e-05 | 1.87093e-05 | 7.26869e-05 | 0.44686 | GF FAIL; acc 0.446484; MC not run |
| `runs/v22_BC_cat3spinered_1302` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.166873e-05 | 1.914967e-05 | 7.08184e-05 | 0.44686 | GF FAIL; acc 0.446535; MC not run |
| `runs/v22_BC_cat3spinered_1320` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.246945e-05 | 1.894979e-05 | 7.141924e-05 | 0.44686 | GF FAIL; acc 0.446651; MC not run |
| `runs/v22_BC_cat3spinered_2013` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.19386e-05 | 1.857767e-05 | 7.051627e-05 | 0.44686 | GF FAIL; acc 0.446660; MC not run |
| `runs/v22_BC_cat3spinered_2031` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.219958e-05 | 1.865024e-05 | 7.084982e-05 | 0.44686 | GF FAIL; acc 0.446524; MC not run |
| `runs/v22_BC_cat3spinered_2103` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.344675e-05 | 1.863049e-05 | 7.207724e-05 | 0.44686 | GF FAIL; acc 0.446540; MC not run |
| `runs/v22_BC_cat3spinered_2130` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.397316e-05 | 1.87235e-05 | 7.269666e-05 | 0.44686 | GF FAIL; acc 0.447152; MC not run |
| `runs/v22_BC_cat3spinered_2301` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.320502e-05 | 1.893335e-05 | 7.213836e-05 | 0.44686 | GF FAIL; acc 0.447424; MC not run |
| `runs/v22_BC_cat3spinered_2310` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.347044e-05 | 1.895348e-05 | 7.242392e-05 | 0.44686 | GF FAIL; acc 0.447078; MC not run |
| `runs/v22_BC_cat3spinered_3012` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.267861e-05 | 1.918746e-05 | 7.186607e-05 | 0.44686 | GF FAIL; acc 0.446494; MC not run |
| `runs/v22_BC_cat3spinered_3021` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.320502e-05 | 1.896832e-05 | 7.217334e-05 | 0.44686 | GF FAIL; acc 0.447111; MC not run |
| `runs/v22_BC_cat3spinered_3102` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.167318e-05 | 1.915784e-05 | 7.083102e-05 | 0.44686 | GF FAIL; acc 0.446645; MC not run |
| `runs/v22_BC_cat3spinered_3120` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.246501e-05 | 1.895498e-05 | 7.141999e-05 | 0.44686 | GF FAIL; acc 0.446504; MC not run |
| `runs/v22_BC_cat3spinered_3201` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.320502e-05 | 1.892838e-05 | 7.21334e-05 | 0.44686 | GF FAIL; acc 0.447090; MC not run |
| `runs/v22_BC_cat3spinered_3210` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.347044e-05 | 1.894472e-05 | 7.241516e-05 | 0.44686 | GF FAIL; acc 0.447462; MC not run |
| `runs/v22_BC_cat4_012` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.24342e-05 | 2.340721e-05 | 7.58414e-05 | 0.53081 | GF PASS; acc 0.530710; MC not run |
| `runs/v22_BC_cat4_021` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.303828e-05 | 2.324337e-05 | 7.628165e-05 | 0.53081 | GF PASS; acc 0.530702; MC not run |
| `runs/v22_BC_cat4_102` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.175923e-05 | 2.343023e-05 | 7.518946e-05 | 0.53081 | GF PASS; acc 0.530752; MC not run |
| `runs/v22_BC_cat4_120` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.186602e-05 | 2.329655e-05 | 7.516257e-05 | 0.53081 | GF PASS; acc 0.530866; MC not run |
| `runs/v22_BC_cat4_201` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.30384e-05 | 2.310029e-05 | 7.613869e-05 | 0.53081 | GF PASS; acc 0.530923; MC not run |
| `runs/v22_BC_cat4_210` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.254086e-05 | 2.31306e-05 | 7.567146e-05 | 0.53081 | GF PASS; acc 0.530904; MC not run |
| `runs/v22_BC_cat_012` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.944326e-05 | 1.84404e-05 | 6.788366e-05 | 0.56385 | GF PASS; acc 0.564299; MC not run |
| `runs/v22_BC_cat_021` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.974548e-05 | 1.83536e-05 | 6.809908e-05 | 0.56385 | GF PASS; acc 0.564307; MC not run |
| `runs/v22_BC_cat_102` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.87683e-05 | 1.845819e-05 | 6.722649e-05 | 0.56385 | GF PASS; acc 0.564032; MC not run |
| `runs/v22_BC_cat_120` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.990045e-05 | 1.902489e-05 | 6.892534e-05 | 0.56019 | GF PASS; acc 0.559763; MC not run |
| `runs/v22_BC_cat_201` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.943716e-05 | 1.924377e-05 | 6.868093e-05 | 0.55834 | GF PASS; acc 0.557855; MC not run |
| `runs/v22_BC_cat_210` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.740688e-05 | 1.862621e-05 | 6.603308e-05 | 0.56244 | GF PASS; acc 0.562223; MC not run |
| `runs/v22_BC_catred_012` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.844311e-05 | 1.234327e-05 | 6.078639e-05 | 0.54866 | GF PASS; acc 0.548148; MC not run |
| `runs/v22_BC_catred_0132` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.870794e-05 | 1.223933e-05 | 6.094728e-05 | 0.54865 | GF PASS; acc 0.548426; MC not run |
| `runs/v22_BC_catred_021` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.844474e-05 | 1.232742e-05 | 6.077217e-05 | 0.54866 | GF PASS; acc 0.548490; MC not run |
| `runs/v22_BC_catred_0231` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.543858e-05 | 1.274923e-05 | 5.818781e-05 | 0.54292 | GF PASS; acc 0.541876; MC not run |
| `runs/v22_BC_catred_0312` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.581215e-05 | 1.260682e-05 | 5.841897e-05 | 0.54618 | GF PASS; acc 0.546504; MC not run |
| `runs/v22_BC_catred_0321` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.581215e-05 | 1.260973e-05 | 5.842188e-05 | 0.54618 | GF PASS; acc 0.546506; MC not run |
| `runs/v22_BC_catred_102` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.776631e-05 | 1.235614e-05 | 6.012245e-05 | 0.54756 | GF PASS; acc 0.547343; MC not run |
| `runs/v22_BC_catred_1032` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.803114e-05 | 1.225066e-05 | 6.02818e-05 | 0.54756 | GF PASS; acc 0.546448; MC not run |
| `runs/v22_BC_catred_120` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.861897e-05 | 1.268106e-05 | 6.130003e-05 | 0.54437 | GF PASS; acc 0.543710; MC not run |
| `runs/v22_BC_catred_1230` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.742999e-05 | 1.262662e-05 | 6.005661e-05 | 0.54837 | GF PASS; acc 0.547722; MC not run |
| `runs/v22_BC_catred_1302` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.803114e-05 | 1.22586e-05 | 6.028974e-05 | 0.54755 | GF PASS; acc 0.547128; MC not run |
| `runs/v22_BC_catred_1320` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.963574e-05 | 1.273928e-05 | 6.237501e-05 | 0.54291 | GF PASS; acc 0.542785; MC not run |
| `runs/v22_BC_catred_201` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.764794e-05 | 1.268306e-05 | 6.0331e-05 | 0.54364 | GF PASS; acc 0.543982; MC not run |
| `runs/v22_BC_catred_2031` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.691858e-05 | 1.312836e-05 | 6.004694e-05 | 0.53688 | GF PASS; acc 0.536529; MC not run |
| `runs/v22_BC_catred_210` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.61763e-05 | 1.263591e-05 | 5.881221e-05 | 0.54655 | GF PASS; acc 0.546111; MC not run |
| `runs/v22_BC_catred_2130` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.743162e-05 | 1.262593e-05 | 6.005755e-05 | 0.54837 | GF PASS; acc 0.547620; MC not run |
| `runs/v22_BC_catred_2301` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.488969e-05 | 1.286516e-05 | 5.775485e-05 | 0.54626 | GF PASS; acc 0.545556; MC not run |
| `runs/v22_BC_catred_2310` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.547846e-05 | 1.291305e-05 | 5.839152e-05 | 0.54299 | GF PASS; acc 0.542931; MC not run |
| `runs/v22_BC_catred_3012` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.683473e-05 | 1.247574e-05 | 5.931047e-05 | 0.54727 | GF PASS; acc 0.547100; MC not run |
| `runs/v22_BC_catred_3021` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.683473e-05 | 1.247908e-05 | 5.93138e-05 | 0.54727 | GF PASS; acc 0.547070; MC not run |
| `runs/v22_BC_catred_3102` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.61083e-05 | 1.24843e-05 | 5.859259e-05 | 0.54545 | GF PASS; acc 0.545056; MC not run |
| `runs/v22_BC_catred_3120` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.690291e-05 | 1.291079e-05 | 5.981369e-05 | 0.54408 | GF PASS; acc 0.543626; MC not run |
| `runs/v22_BC_catred_3201` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.713935e-05 | 1.305381e-05 | 6.019316e-05 | 0.54191 | GF PASS; acc 0.542077; MC not run |
| `runs/v22_BC_catred_3210` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.484068e-05 | 1.286063e-05 | 5.770132e-05 | 0.54626 | GF PASS; acc 0.545629; MC not run |
| `runs/v22_BC_direct_012` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.07147e-05 | 1.773172e-05 | 5.844643e-05 | 0.56413 | GF PASS; acc 0.563850; MC not run |
| `runs/v22_BC_direct_021` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.137118e-05 | 1.820369e-05 | 5.957487e-05 | 0.55965 | GF PASS; acc 0.559939; MC not run |
| `runs/v22_BC_direct_102` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.088383e-05 | 1.861192e-05 | 5.949574e-05 | 0.55742 | GF PASS; acc 0.557087; MC not run |
| `runs/v22_BC_direct_120` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.06974e-05 | 1.77781e-05 | 5.847549e-05 | 0.56300 | GF PASS; acc 0.563099; MC not run |
| `runs/v22_BC_direct_201` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.120312e-05 | 1.765462e-05 | 5.885773e-05 | 0.56300 | GF PASS; acc 0.563120; MC not run |
| `runs/v22_BC_direct_210` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.115867e-05 | 1.766058e-05 | 5.881925e-05 | 0.56300 | GF PASS; acc 0.562117; MC not run |
| `runs/v22_BC_flag_012` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.168775e-05 | 2.030279e-05 | 6.199054e-05 | 0.52664 | GF PASS; acc 0.526073; MC not run |
| `runs/v22_BC_flag_021` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.243077e-05 | 2.089894e-05 | 6.332971e-05 | 0.52142 | GF PASS; acc 0.521315; MC not run |
| `runs/v22_BC_flag_102` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.161583e-05 | 2.141003e-05 | 6.302586e-05 | 0.51832 | GF PASS; acc 0.517943; MC not run |
| `runs/v22_BC_flag_120` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.162641e-05 | 2.035432e-05 | 6.198074e-05 | 0.52558 | GF PASS; acc 0.525185; MC not run |
| `runs/v22_BC_flag_201` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.216669e-05 | 2.024147e-05 | 6.240816e-05 | 0.52558 | GF PASS; acc 0.525140; MC not run |
| `runs/v22_BC_flag_210` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.205154e-05 | 2.024733e-05 | 6.229887e-05 | 0.52558 | GF PASS; acc 0.525485; MC not run |
| `runs/v22_BC_hybrid1_012` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.081971e-05 | 1.802596e-05 | 5.884568e-05 | 0.55645 | GF PASS; acc 0.556217; MC not run |
| `runs/v22_BC_hybrid1_021` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.112134e-05 | 1.791786e-05 | 5.90392e-05 | 0.55646 | GF PASS; acc 0.556771; MC not run |
| `runs/v22_BC_hybrid1_102` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.081971e-05 | 1.802596e-05 | 5.884568e-05 | 0.55645 | GF PASS; acc 0.556217; MC not run |
| `runs/v22_BC_hybrid1_120` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.081971e-05 | 1.802596e-05 | 5.884568e-05 | 0.55645 | GF PASS; acc 0.556217; MC not run |
| `runs/v22_BC_hybrid1_201` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.112134e-05 | 1.791786e-05 | 5.90392e-05 | 0.55646 | GF PASS; acc 0.556771; MC not run |
| `runs/v22_BC_hybrid1_210` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.112134e-05 | 1.791786e-05 | 5.90392e-05 | 0.55646 | GF PASS; acc 0.556771; MC not run |
| `runs/v22_BC_hybrid2_012` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 3.998652e-05 | 1.709868e-05 | 5.708521e-05 | 0.56264 | GF PASS; acc 0.561805; MC not run |
| `runs/v22_BC_hybrid2_021` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 3.998652e-05 | 1.709868e-05 | 5.708521e-05 | 0.56264 | GF PASS; acc 0.561805; MC not run |
| `runs/v22_BC_hybrid2_102` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 3.998652e-05 | 1.709868e-05 | 5.708521e-05 | 0.56264 | GF PASS; acc 0.561805; MC not run |
| `runs/v22_BC_hybrid2_120` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 3.998652e-05 | 1.709868e-05 | 5.708521e-05 | 0.56264 | GF PASS; acc 0.561805; MC not run |
| `runs/v22_BC_hybrid2_201` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 3.998652e-05 | 1.709868e-05 | 5.708521e-05 | 0.56264 | GF PASS; acc 0.561805; MC not run |
| `runs/v22_BC_hybrid2_210` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 3.998652e-05 | 1.709868e-05 | 5.708521e-05 | 0.56264 | GF PASS; acc 0.561805; MC not run |
| `runs/v22_BC_hybrid2t_012` (regenerate) | BC hybrid2t | 123 | 45 | 2.923587e-19 | 4.116381e-05 | 1.777025e-05 | 5.893405e-05 | 0.55819 | GF PASS; acc 0.557755; MC not run |
| `runs/v22_BC_redundant_012` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.862291e-05 | 1.354758e-05 | 5.217049e-05 | 0.55199 | GF PASS; acc 0.551030; MC not run |
| `runs/v22_BC_redundant_0132` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.895785e-05 | 1.445631e-05 | 5.341416e-05 | 0.54538 | GF PASS; acc 0.545031; MC not run |
| `runs/v22_BC_redundant_021` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.862208e-05 | 1.355385e-05 | 5.217593e-05 | 0.54761 | GF PASS; acc 0.547594; MC not run |
| `runs/v22_BC_redundant_0231` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.888558e-05 | 1.388195e-05 | 5.276753e-05 | 0.54645 | GF PASS; acc 0.545699; MC not run |
| `runs/v22_BC_redundant_0312` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.904229e-05 | 1.418922e-05 | 5.323151e-05 | 0.54967 | GF PASS; acc 0.549413; MC not run |
| `runs/v22_BC_redundant_0321` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.921784e-05 | 1.434738e-05 | 5.356523e-05 | 0.54422 | GF PASS; acc 0.543793; MC not run |
| `runs/v22_BC_redundant_102` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.881986e-05 | 1.374144e-05 | 5.25613e-05 | 0.54543 | GF PASS; acc 0.544566; MC not run |
| `runs/v22_BC_redundant_1032` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.896674e-05 | 1.445815e-05 | 5.342489e-05 | 0.54538 | GF PASS; acc 0.544782; MC not run |
| `runs/v22_BC_redundant_120` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.888904e-05 | 1.341996e-05 | 5.2309e-05 | 0.55089 | GF PASS; acc 0.550252; MC not run |
| `runs/v22_BC_redundant_1230` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.897769e-05 | 1.343313e-05 | 5.241082e-05 | 0.55088 | GF PASS; acc 0.549966; MC not run |
| `runs/v22_BC_redundant_1302` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.887938e-05 | 1.42907e-05 | 5.317008e-05 | 0.54864 | GF PASS; acc 0.548944; MC not run |
| `runs/v22_BC_redundant_1320` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.894102e-05 | 1.406228e-05 | 5.300329e-05 | 0.54428 | GF PASS; acc 0.544047; MC not run |
| [runs/v22_BC_redundant_201](runs/v22_BC_redundant_201.qasm) · [JSON](runs/v22_BC_redundant_201.json) · [receipt](runs/v22_BC_redundant_201.result.json) | BC redundant | 137 | 45 | 2.923587e-19 | 3.86318e-05 | 1.341827e-05 | 5.205006e-05 | 0.55089 | GF PASS; acc 0.551068; MC not run |
| `runs/v22_BC_redundant_2031` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.889529e-05 | 1.376875e-05 | 5.266404e-05 | 0.54753 | GF PASS; acc 0.547120; MC not run |
| `runs/v22_BC_redundant_210` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.888904e-05 | 1.342133e-05 | 5.231037e-05 | 0.55089 | GF PASS; acc 0.550771; MC not run |
| `runs/v22_BC_redundant_2130` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.897769e-05 | 1.343484e-05 | 5.241253e-05 | 0.55089 | GF PASS; acc 0.550437; MC not run |
| `runs/v22_BC_redundant_2301` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.884442e-05 | 1.359348e-05 | 5.24379e-05 | 0.55192 | GF PASS; acc 0.550751; MC not run |
| `runs/v22_BC_redundant_2310` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.902898e-05 | 1.3632e-05 | 5.266098e-05 | 0.54862 | GF PASS; acc 0.548268; MC not run |
| `runs/v22_BC_redundant_3012` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.895494e-05 | 1.400137e-05 | 5.295631e-05 | 0.55518 | GF PASS; acc 0.554671; MC not run |
| `runs/v22_BC_redundant_3021` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.913071e-05 | 1.416947e-05 | 5.330018e-05 | 0.54748 | GF PASS; acc 0.546850; MC not run |
| `runs/v22_BC_redundant_3102` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.947944e-05 | 1.451734e-05 | 5.399678e-05 | 0.54422 | GF PASS; acc 0.544081; MC not run |
| `runs/v22_BC_redundant_3120` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.895435e-05 | 1.390243e-05 | 5.285678e-05 | 0.54966 | GF PASS; acc 0.548378; MC not run |
| `runs/v22_BC_redundant_3201` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.905049e-05 | 1.390953e-05 | 5.296002e-05 | 0.54529 | GF PASS; acc 0.545221; MC not run |
| `runs/v22_BC_redundant_3210` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.911283e-05 | 1.39092e-05 | 5.302203e-05 | 0.54530 | GF PASS; acc 0.545231; MC not run |
| `runs/v22_BC_redundant_m3_0123` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.922285e-05 | 1.396911e-05 | 5.319196e-05 | 0.56200 | GF PASS; acc 0.561674; MC not run |
| `runs/v22_BC_redundant_m3_0132` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.955049e-05 | 1.503616e-05 | 5.458665e-05 | 0.55275 | GF PASS; acc 0.552462; MC not run |
| `runs/v22_BC_redundant_m3_0213` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.955126e-05 | 1.415698e-05 | 5.370824e-05 | 0.55753 | GF PASS; acc 0.556405; MC not run |
| `runs/v22_BC_redundant_m3_0231` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.002416e-05 | 1.522347e-05 | 5.524763e-05 | 0.54719 | GF PASS; acc 0.547429; MC not run |
| `runs/v22_BC_redundant_m3_0312` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.972229e-05 | 1.521147e-05 | 5.493376e-05 | 0.54872 | GF PASS; acc 0.548469; MC not run |
| `runs/v22_BC_redundant_m3_0321` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.989071e-05 | 1.511025e-05 | 5.500096e-05 | 0.54763 | GF PASS; acc 0.546595; MC not run |
| `runs/v22_BC_redundant_m3_1023` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.942063e-05 | 1.415261e-05 | 5.357323e-05 | 0.55531 | GF PASS; acc 0.554324; MC not run |
| `runs/v22_BC_redundant_m3_1032` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.004697e-05 | 1.522444e-05 | 5.527141e-05 | 0.54726 | GF PASS; acc 0.546829; MC not run |
| `runs/v22_BC_redundant_m3_1203` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.95646e-05 | 1.427166e-05 | 5.383626e-05 | 0.55865 | GF PASS; acc 0.558132; MC not run |
| `runs/v22_BC_redundant_m3_1230` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.95646e-05 | 1.428076e-05 | 5.384536e-05 | 0.55864 | GF PASS; acc 0.558381; MC not run |
| `runs/v22_BC_redundant_m3_1302` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.974827e-05 | 1.519519e-05 | 5.494346e-05 | 0.55055 | GF PASS; acc 0.549508; MC not run |
| `runs/v22_BC_redundant_m3_1320` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.974184e-05 | 1.484044e-05 | 5.458228e-05 | 0.54980 | GF PASS; acc 0.549572; MC not run |
| `runs/v22_BC_redundant_m3_2013` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.013266e-05 | 1.48192e-05 | 5.495186e-05 | 0.56089 | GF PASS; acc 0.560925; MC not run |
| `runs/v22_BC_redundant_m3_2031` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.075737e-05 | 1.569483e-05 | 5.645221e-05 | 0.54828 | GF PASS; acc 0.548079; MC not run |
| `runs/v22_BC_redundant_m3_2103` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.027266e-05 | 1.488404e-05 | 5.51567e-05 | 0.55531 | GF PASS; acc 0.554938; MC not run |
| `runs/v22_BC_redundant_m3_2130` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.006155e-05 | 1.48614e-05 | 5.492294e-05 | 0.55865 | GF PASS; acc 0.557913; MC not run |
| `runs/v22_BC_redundant_m3_2301` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.015867e-05 | 1.513398e-05 | 5.529266e-05 | 0.55710 | GF PASS; acc 0.557088; MC not run |
| `runs/v22_BC_redundant_m3_2310` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.039808e-05 | 1.542146e-05 | 5.581955e-05 | 0.54974 | GF PASS; acc 0.548634; MC not run |
| `runs/v22_BC_redundant_m3_3012` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.954605e-05 | 1.488443e-05 | 5.443048e-05 | 0.55533 | GF PASS; acc 0.554826; MC not run |
| `runs/v22_BC_redundant_m3_3021` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.989071e-05 | 1.511009e-05 | 5.50008e-05 | 0.54762 | GF PASS; acc 0.547008; MC not run |
| `runs/v22_BC_redundant_m3_3102` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.98643e-05 | 1.552807e-05 | 5.539237e-05 | 0.54364 | GF PASS; acc 0.543713; MC not run |
| `runs/v22_BC_redundant_m3_3120` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.973657e-05 | 1.484435e-05 | 5.458092e-05 | 0.54908 | GF PASS; acc 0.548577; MC not run |
| `runs/v22_BC_redundant_m3_3201` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.001118e-05 | 1.50767e-05 | 5.508788e-05 | 0.54908 | GF PASS; acc 0.549299; MC not run |
| `runs/v22_BC_redundant_m3_3210` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.006463e-05 | 1.507606e-05 | 5.514069e-05 | 0.54908 | GF PASS; acc 0.548783; MC not run |
| `runs/v22_BC_redundant_m5_0123` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.845011e-05 | 1.438703e-05 | 5.283713e-05 | 0.56200 | GF PASS; acc 0.561503; MC not run |
| `runs/v22_BC_redundant_m5_0132` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 4.079192e-05 | 1.658237e-05 | 5.737429e-05 | 0.54071 | GF PASS; acc 0.540573; MC not run |
| `runs/v22_BC_redundant_m5_0213` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.869011e-05 | 1.445618e-05 | 5.314628e-05 | 0.55530 | GF PASS; acc 0.555112; MC not run |
| `runs/v22_BC_redundant_m5_0231` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.906967e-05 | 1.518571e-05 | 5.425538e-05 | 0.54834 | GF PASS; acc 0.548061; MC not run |
| `runs/v22_BC_redundant_m5_0312` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.965957e-05 | 1.548381e-05 | 5.514338e-05 | 0.55092 | GF PASS; acc 0.550013; MC not run |
| `runs/v22_BC_redundant_m5_0321` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 4.005698e-05 | 1.577675e-05 | 5.583374e-05 | 0.54546 | GF PASS; acc 0.546204; MC not run |
| `runs/v22_BC_redundant_m5_1023` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.882788e-05 | 1.541848e-05 | 5.424636e-05 | 0.55531 | GF PASS; acc 0.554917; MC not run |
| `runs/v22_BC_redundant_m5_1032` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 4.119289e-05 | 1.716886e-05 | 5.836176e-05 | 0.54072 | GF PASS; acc 0.540526; MC not run |
| `runs/v22_BC_redundant_m5_1203` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.862566e-05 | 1.487033e-05 | 5.349599e-05 | 0.55865 | GF PASS; acc 0.558094; MC not run |
| `runs/v22_BC_redundant_m5_1230` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.862566e-05 | 1.487151e-05 | 5.349717e-05 | 0.55865 | GF PASS; acc 0.558065; MC not run |
| `runs/v22_BC_redundant_m5_1302` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.984211e-05 | 1.652922e-05 | 5.637133e-05 | 0.54721 | GF PASS; acc 0.546356; MC not run |
| `runs/v22_BC_redundant_m5_1320` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.993472e-05 | 1.645299e-05 | 5.638771e-05 | 0.54105 | GF PASS; acc 0.540924; MC not run |
| `runs/v22_BC_redundant_m5_2013` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.8879e-05 | 1.435045e-05 | 5.322945e-05 | 0.55530 | GF PASS; acc 0.555280; MC not run |
| `runs/v22_BC_redundant_m5_2031` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.95145e-05 | 1.493896e-05 | 5.445346e-05 | 0.55273 | GF PASS; acc 0.552124; MC not run |
| `runs/v22_BC_redundant_m5_2103` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.892344e-05 | 1.4615e-05 | 5.353844e-05 | 0.55531 | GF PASS; acc 0.554826; MC not run |
| `runs/v22_BC_redundant_m5_2130` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.892344e-05 | 1.461654e-05 | 5.353998e-05 | 0.55531 | GF PASS; acc 0.554817; MC not run |
| `runs/v22_BC_redundant_m5_2301` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.889331e-05 | 1.46207e-05 | 5.351401e-05 | 0.55716 | GF PASS; acc 0.556395; MC not run |
| `runs/v22_BC_redundant_m5_2310` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.898629e-05 | 1.492744e-05 | 5.391373e-05 | 0.54870 | GF PASS; acc 0.548466; MC not run |
| `runs/v22_BC_redundant_m5_3012` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.895049e-05 | 1.516377e-05 | 5.411426e-05 | 0.55533 | GF PASS; acc 0.554799; MC not run |
| `runs/v22_BC_redundant_m5_3021` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.934837e-05 | 1.544533e-05 | 5.47937e-05 | 0.54982 | GF PASS; acc 0.549574; MC not run |
| `runs/v22_BC_redundant_m5_3102` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.915411e-05 | 1.610046e-05 | 5.525458e-05 | 0.54581 | GF PASS; acc 0.545711; MC not run |
| `runs/v22_BC_redundant_m5_3120` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.894546e-05 | 1.538038e-05 | 5.432584e-05 | 0.54908 | GF PASS; acc 0.549035; MC not run |
| `runs/v22_BC_redundant_m5_3201` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.91616e-05 | 1.505764e-05 | 5.421924e-05 | 0.54580 | GF PASS; acc 0.545098; MC not run |
| `runs/v22_BC_redundant_m5_3210` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.907727e-05 | 1.507893e-05 | 5.415621e-05 | 0.54472 | GF PASS; acc 0.544717; MC not run |
| `runs/v22_BC_redundant_m6_0123` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.988863e-05 | 1.484282e-05 | 5.473145e-05 | 0.56201 | GF PASS; acc 0.561785; MC not run |
| `runs/v22_BC_redundant_m6_0132` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.248748e-05 | 1.713822e-05 | 5.96257e-05 | 0.54108 | GF PASS; acc 0.541238; MC not run |
| `runs/v22_BC_redundant_m6_0213` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.03657e-05 | 1.530914e-05 | 5.567484e-05 | 0.55531 | GF PASS; acc 0.554743; MC not run |
| `runs/v22_BC_redundant_m6_0231` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.03657e-05 | 1.530878e-05 | 5.567447e-05 | 0.55531 | GF PASS; acc 0.554748; MC not run |
| `runs/v22_BC_redundant_m6_0312` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.077012e-05 | 1.622645e-05 | 5.699657e-05 | 0.54865 | GF PASS; acc 0.549048; MC not run |
| `runs/v22_BC_redundant_m6_0321` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.103432e-05 | 1.653067e-05 | 5.756499e-05 | 0.54142 | GF PASS; acc 0.541296; MC not run |
| `runs/v22_BC_redundant_m6_1023` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.99222e-05 | 1.461146e-05 | 5.453366e-05 | 0.55530 | GF PASS; acc 0.554776; MC not run |
| `runs/v22_BC_redundant_m6_1032` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.163162e-05 | 1.656573e-05 | 5.819736e-05 | 0.53999 | GF PASS; acc 0.540057; MC not run |
| `runs/v22_BC_redundant_m6_1203` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.984021e-05 | 1.432314e-05 | 5.416335e-05 | 0.55864 | GF PASS; acc 0.557979; MC not run |
| `runs/v22_BC_redundant_m6_1230` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.995787e-05 | 1.490324e-05 | 5.486111e-05 | 0.55606 | GF PASS; acc 0.555832; MC not run |
| `runs/v22_BC_redundant_m6_1302` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.096216e-05 | 1.609692e-05 | 5.705909e-05 | 0.54257 | GF PASS; acc 0.542269; MC not run |
| `runs/v22_BC_redundant_m6_1320` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.097573e-05 | 1.577771e-05 | 5.675345e-05 | 0.54582 | GF PASS; acc 0.545900; MC not run |
| `runs/v22_BC_redundant_m6_2013` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.016664e-05 | 1.46196e-05 | 5.478625e-05 | 0.55531 | GF PASS; acc 0.554254; MC not run |
| `runs/v22_BC_redundant_m6_2031` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.016664e-05 | 1.461908e-05 | 5.478572e-05 | 0.55531 | GF PASS; acc 0.554270; MC not run |
| `runs/v22_BC_redundant_m6_2103` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.009577e-05 | 1.435797e-05 | 5.445374e-05 | 0.55530 | GF PASS; acc 0.554789; MC not run |
| `runs/v22_BC_redundant_m6_2130` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.032397e-05 | 1.494051e-05 | 5.526448e-05 | 0.55273 | GF PASS; acc 0.552110; MC not run |
| `runs/v22_BC_redundant_m6_2301` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.981284e-05 | 1.488369e-05 | 5.469653e-05 | 0.55310 | GF PASS; acc 0.552041; MC not run |
| `runs/v22_BC_redundant_m6_2310` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.970231e-05 | 1.461984e-05 | 5.432215e-05 | 0.55716 | GF PASS; acc 0.556363; MC not run |
| `runs/v22_BC_redundant_m6_3012` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.002054e-05 | 1.551059e-05 | 5.553113e-05 | 0.55018 | GF PASS; acc 0.549773; MC not run |
| `runs/v22_BC_redundant_m6_3021` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.02851e-05 | 1.580677e-05 | 5.609187e-05 | 0.54292 | GF PASS; acc 0.542873; MC not run |
| `runs/v22_BC_redundant_m6_3102` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.012078e-05 | 1.576363e-05 | 5.588441e-05 | 0.54691 | GF PASS; acc 0.546650; MC not run |
| `runs/v22_BC_redundant_m6_3120` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.987879e-05 | 1.515359e-05 | 5.503238e-05 | 0.55127 | GF PASS; acc 0.551355; MC not run |
| `runs/v22_BC_redundant_m6_3201` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.998827e-05 | 1.51738e-05 | 5.516207e-05 | 0.54508 | GF PASS; acc 0.545075; MC not run |
| `runs/v22_BC_redundant_m6_3210` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.005493e-05 | 1.515463e-05 | 5.520956e-05 | 0.54617 | GF PASS; acc 0.545595; MC not run |
| `runs/v22_BC_seq_012` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.299962e-05 | 2.441622e-05 | 6.741584e-05 | 0.51288 | GF PASS; acc 0.513373; MC not run |
| `runs/v22_BC_seq_021` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.400646e-05 | 2.399224e-05 | 6.79987e-05 | 0.51289 | GF PASS; acc 0.512858; MC not run |
| `runs/v22_BC_seq_102` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.096208e-05 | 2.443093e-05 | 6.539301e-05 | 0.51289 | GF PASS; acc 0.512515; MC not run |
| `runs/v22_BC_seq_120` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.272334e-05 | 2.419127e-05 | 6.691461e-05 | 0.51186 | GF PASS; acc 0.512323; MC not run |
| `runs/v22_BC_seq_201` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.419207e-05 | 2.36579e-05 | 6.784996e-05 | 0.51186 | GF PASS; acc 0.512159; MC not run |
| `runs/v22_BC_seq_210` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.476836e-05 | 2.369133e-05 | 6.845969e-05 | 0.51187 | GF PASS; acc 0.512489; MC not run |
| `runs/v22_B_cat13_012` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 3.980587e-05 | 1.553874e-05 | 5.534461e-05 | 0.57979 | GF PASS; acc 0.578944; MC not run |
| `runs/v22_B_cat13_021` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 4.013879e-05 | 1.576335e-05 | 5.590214e-05 | 0.57748 | GF PASS; acc 0.577513; MC not run |
| `runs/v22_B_cat13_102` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 3.974599e-05 | 1.595471e-05 | 5.57007e-05 | 0.57633 | GF PASS; acc 0.576373; MC not run |
| `runs/v22_B_cat13_120` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 3.979265e-05 | 1.55591e-05 | 5.535175e-05 | 0.57921 | GF PASS; acc 0.578310; MC not run |
| `runs/v22_B_cat13_201` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 4.005464e-05 | 1.54978e-05 | 5.555244e-05 | 0.57921 | GF PASS; acc 0.578326; MC not run |
| `runs/v22_B_cat13_210` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 4.002785e-05 | 1.549917e-05 | 5.552703e-05 | 0.57921 | GF PASS; acc 0.578822; MC not run |
| `runs/v22_B_cat13red_012` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.839283e-05 | 1.275868e-05 | 5.115151e-05 | 0.56851 | GF PASS; acc 0.567303; MC not run |
| `runs/v22_B_cat13red_0132` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.829085e-05 | 1.267783e-05 | 5.096867e-05 | 0.56772 | GF PASS; acc 0.566964; MC not run |
| `runs/v22_B_cat13red_021` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.839201e-05 | 1.27553e-05 | 5.114731e-05 | 0.56625 | GF PASS; acc 0.564960; MC not run |
| `runs/v22_B_cat13red_0231` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.836984e-05 | 1.258313e-05 | 5.095297e-05 | 0.56527 | GF PASS; acc 0.565084; MC not run |
| `runs/v22_B_cat13red_0312` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.83264e-05 | 1.2441e-05 | 5.07674e-05 | 0.56692 | GF PASS; acc 0.566167; MC not run |
| `runs/v22_B_cat13red_0321` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.83264e-05 | 1.243304e-05 | 5.075944e-05 | 0.56692 | GF PASS; acc 0.566688; MC not run |
| `runs/v22_B_cat13red_102` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.841867e-05 | 1.284069e-05 | 5.125936e-05 | 0.56512 | GF PASS; acc 0.565012; MC not run |
| `runs/v22_B_cat13red_1032` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.829529e-05 | 1.267772e-05 | 5.097301e-05 | 0.56772 | GF PASS; acc 0.566312; MC not run |
| `runs/v22_B_cat13red_120` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.851923e-05 | 1.269703e-05 | 5.121626e-05 | 0.56794 | GF PASS; acc 0.566885; MC not run |
| `runs/v22_B_cat13red_1230` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.856356e-05 | 1.270721e-05 | 5.127077e-05 | 0.56718 | GF PASS; acc 0.566042; MC not run |
| `runs/v22_B_cat13red_1302` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.829529e-05 | 1.275652e-05 | 5.105181e-05 | 0.56565 | GF PASS; acc 0.565388; MC not run |
| `runs/v22_B_cat13red_1320` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.8364e-05 | 1.262959e-05 | 5.099359e-05 | 0.56677 | GF PASS; acc 0.567085; MC not run |
| `runs/v22_B_cat13red_201` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.839505e-05 | 1.269588e-05 | 5.109094e-05 | 0.56794 | GF PASS; acc 0.566955; MC not run |
| `runs/v22_B_cat13red_2031` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.837289e-05 | 1.25227e-05 | 5.089559e-05 | 0.56695 | GF PASS; acc 0.566781; MC not run |
| `runs/v22_B_cat13red_210` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.851923e-05 | 1.269816e-05 | 5.121739e-05 | 0.56794 | GF PASS; acc 0.568011; MC not run |
| `runs/v22_B_cat13red_2130` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.856356e-05 | 1.270865e-05 | 5.12722e-05 | 0.56718 | GF PASS; acc 0.566877; MC not run |
| `runs/v22_B_cat13red_2301` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.845271e-05 | 1.252739e-05 | 5.098011e-05 | 0.56658 | GF PASS; acc 0.565624; MC not run |
| `runs/v22_B_cat13red_2310` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.852365e-05 | 1.252899e-05 | 5.105264e-05 | 0.56658 | GF PASS; acc 0.565874; MC not run |
| `runs/v22_B_cat13red_3012` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.83264e-05 | 1.243746e-05 | 5.076386e-05 | 0.56692 | GF PASS; acc 0.566164; MC not run |
| `runs/v22_B_cat13red_3021` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.83264e-05 | 1.244546e-05 | 5.077186e-05 | 0.56466 | GF PASS; acc 0.564422; MC not run |
| `runs/v22_B_cat13red_3102` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.831751e-05 | 1.251971e-05 | 5.083722e-05 | 0.56354 | GF PASS; acc 0.563292; MC not run |
| `runs/v22_B_cat13red_3120` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.8364e-05 | 1.238184e-05 | 5.074584e-05 | 0.56635 | GF PASS; acc 0.565738; MC not run |
| `runs/v22_B_cat13red_3201` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.832862e-05 | 1.23738e-05 | 5.070243e-05 | 0.56635 | GF PASS; acc 0.565723; MC not run |
| `runs/v22_B_cat13red_3210` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.839956e-05 | 1.237457e-05 | 5.077412e-05 | 0.56636 | GF PASS; acc 0.565667; MC not run |
| `runs/v22_B_cat3_012` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.064391e-05 | 1.645409e-05 | 5.709801e-05 | 0.57539 | GF PASS; acc 0.575481; MC not run |
| `runs/v22_B_cat3_021` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.076836e-05 | 1.641415e-05 | 5.718251e-05 | 0.57539 | GF PASS; acc 0.575448; MC not run |
| `runs/v22_B_cat3_102` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.030637e-05 | 1.645792e-05 | 5.67643e-05 | 0.57539 | GF PASS; acc 0.575529; MC not run |
| `runs/v22_B_cat3_120` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.053731e-05 | 1.66581e-05 | 5.71954e-05 | 0.57310 | GF PASS; acc 0.572767; MC not run |
| `runs/v22_B_cat3_201` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.094596e-05 | 1.661086e-05 | 5.755682e-05 | 0.57310 | GF PASS; acc 0.572765; MC not run |
| `runs/v22_B_cat3_210` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.069725e-05 | 1.661608e-05 | 5.731333e-05 | 0.57310 | GF PASS; acc 0.572770; MC not run |
| `runs/v22_B_cat3red_0123` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.851751e-05 | 1.225892e-05 | 5.077643e-05 | 0.56558 | GF PASS; acc 0.565073; MC not run |
| `runs/v22_B_cat3red_0132` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.855301e-05 | 1.231119e-05 | 5.08642e-05 | 0.56374 | GF PASS; acc 0.563774; MC not run |
| `runs/v22_B_cat3red_0213` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.851751e-05 | 1.225313e-05 | 5.077065e-05 | 0.56558 | GF PASS; acc 0.565080; MC not run |
| `runs/v22_B_cat3red_0231` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.860388e-05 | 1.24759e-05 | 5.107979e-05 | 0.55925 | GF PASS; acc 0.558978; MC not run |
| `runs/v22_B_cat3red_0312` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.865274e-05 | 1.251461e-05 | 5.116735e-05 | 0.56078 | GF PASS; acc 0.559774; MC not run |
| `runs/v22_B_cat3red_0321` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.865274e-05 | 1.25163e-05 | 5.116905e-05 | 0.56078 | GF PASS; acc 0.559755; MC not run |
| `runs/v22_B_cat3red_1023` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.851751e-05 | 1.226375e-05 | 5.078127e-05 | 0.56501 | GF PASS; acc 0.564094; MC not run |
| `runs/v22_B_cat3red_1032` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.855301e-05 | 1.231536e-05 | 5.086837e-05 | 0.56317 | GF PASS; acc 0.562468; MC not run |
| `runs/v22_B_cat3red_1203` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.857085e-05 | 1.227616e-05 | 5.084701e-05 | 0.56276 | GF PASS; acc 0.562719; MC not run |
| `runs/v22_B_cat3red_1230` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.857085e-05 | 1.227367e-05 | 5.084451e-05 | 0.56276 | GF PASS; acc 0.562707; MC not run |
| `runs/v22_B_cat3red_1302` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.855301e-05 | 1.230572e-05 | 5.085873e-05 | 0.56486 | GF PASS; acc 0.563911; MC not run |
| `runs/v22_B_cat3red_1320` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.859734e-05 | 1.238795e-05 | 5.098529e-05 | 0.56111 | GF PASS; acc 0.560691; MC not run |
| `runs/v22_B_cat3red_2013` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.851751e-05 | 1.225976e-05 | 5.077727e-05 | 0.56501 | GF PASS; acc 0.563774; MC not run |
| `runs/v22_B_cat3red_2031` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.860388e-05 | 1.249402e-05 | 5.10979e-05 | 0.55702 | GF PASS; acc 0.556599; MC not run |
| `runs/v22_B_cat3red_2103` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.857085e-05 | 1.227804e-05 | 5.084888e-05 | 0.56276 | GF PASS; acc 0.562721; MC not run |
| `runs/v22_B_cat3red_2130` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.857085e-05 | 1.227588e-05 | 5.084673e-05 | 0.56276 | GF PASS; acc 0.562700; MC not run |
| `runs/v22_B_cat3red_2301` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.859517e-05 | 1.240201e-05 | 5.099718e-05 | 0.56093 | GF PASS; acc 0.560866; MC not run |
| `runs/v22_B_cat3red_2310` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.855085e-05 | 1.241772e-05 | 5.096857e-05 | 0.55832 | GF PASS; acc 0.557453; MC not run |
| `runs/v22_B_cat3red_3012` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.860848e-05 | 1.242072e-05 | 5.102919e-05 | 0.56471 | GF PASS; acc 0.563308; MC not run |
| `runs/v22_B_cat3red_3021` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.860848e-05 | 1.242239e-05 | 5.103086e-05 | 0.56471 | GF PASS; acc 0.563295; MC not run |
| `runs/v22_B_cat3red_3102` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.852859e-05 | 1.243251e-05 | 5.096111e-05 | 0.56209 | GF PASS; acc 0.561603; MC not run |
| `runs/v22_B_cat3red_3120` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.857292e-05 | 1.250545e-05 | 5.107838e-05 | 0.56003 | GF PASS; acc 0.559318; MC not run |
| `runs/v22_B_cat3red_3201` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.86528e-05 | 1.248396e-05 | 5.113676e-05 | 0.56265 | GF PASS; acc 0.561860; MC not run |
| `runs/v22_B_cat3red_3210` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.860848e-05 | 1.249793e-05 | 5.110641e-05 | 0.56003 | GF PASS; acc 0.559305; MC not run |
| `runs/v22_B_cat3reusered_0123` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.888707e-05 | 1.429233e-05 | 5.31794e-05 | 0.51776 | GF PASS; acc 0.516997; MC not run |
| `runs/v22_B_cat3reusered_0132` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.87895e-05 | 1.448068e-05 | 5.327019e-05 | 0.51831 | GF PASS; acc 0.518292; MC not run |
| `runs/v22_B_cat3reusered_0213` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.888707e-05 | 1.418153e-05 | 5.30686e-05 | 0.51776 | GF PASS; acc 0.517157; MC not run |
| `runs/v22_B_cat3reusered_0231` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.901721e-05 | 1.426505e-05 | 5.328225e-05 | 0.51831 | GF PASS; acc 0.516875; MC not run |
| `runs/v22_B_cat3reusered_0312` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.930742e-05 | 1.457738e-05 | 5.388481e-05 | 0.51886 | GF PASS; acc 0.517979; MC not run |
| `runs/v22_B_cat3reusered_0321` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.957249e-05 | 1.446341e-05 | 5.40359e-05 | 0.51886 | GF PASS; acc 0.519215; MC not run |
| `runs/v22_B_cat3reusered_1023` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.888707e-05 | 1.429435e-05 | 5.318143e-05 | 0.51776 | GF PASS; acc 0.517431; MC not run |
| `runs/v22_B_cat3reusered_1032` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.87895e-05 | 1.448254e-05 | 5.327205e-05 | 0.51831 | GF PASS; acc 0.517433; MC not run |
| `runs/v22_B_cat3reusered_1203` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.966781e-05 | 1.421169e-05 | 5.38795e-05 | 0.51777 | GF PASS; acc 0.517826; MC not run |
| `runs/v22_B_cat3reusered_1230` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.993324e-05 | 1.425492e-05 | 5.418816e-05 | 0.51776 | GF PASS; acc 0.516917; MC not run |
| `runs/v22_B_cat3reusered_1302` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.87895e-05 | 1.451671e-05 | 5.330621e-05 | 0.51830 | GF PASS; acc 0.518471; MC not run |
| `runs/v22_B_cat3reusered_1320` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.918764e-05 | 1.441086e-05 | 5.35985e-05 | 0.51831 | GF PASS; acc 0.517739; MC not run |
| `runs/v22_B_cat3reusered_2013` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.888707e-05 | 1.418629e-05 | 5.307336e-05 | 0.51776 | GF PASS; acc 0.517681; MC not run |
| `runs/v22_B_cat3reusered_2031` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.901721e-05 | 1.426924e-05 | 5.328644e-05 | 0.51831 | GF PASS; acc 0.517353; MC not run |
| `runs/v22_B_cat3reusered_2103` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.966781e-05 | 1.421442e-05 | 5.388223e-05 | 0.51777 | GF PASS; acc 0.517812; MC not run |
| `runs/v22_B_cat3reusered_2130` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.993324e-05 | 1.425753e-05 | 5.419076e-05 | 0.51776 | GF PASS; acc 0.516970; MC not run |
| `runs/v22_B_cat3reusered_2301` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.95377e-05 | 1.429317e-05 | 5.383087e-05 | 0.51830 | GF PASS; acc 0.518176; MC not run |
| `runs/v22_B_cat3reusered_2310` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.967077e-05 | 1.430076e-05 | 5.397152e-05 | 0.51831 | GF PASS; acc 0.517471; MC not run |
| `runs/v22_B_cat3reusered_3012` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.930742e-05 | 1.455534e-05 | 5.386276e-05 | 0.51885 | GF PASS; acc 0.519259; MC not run |
| `runs/v22_B_cat3reusered_3021` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.957249e-05 | 1.44414e-05 | 5.401389e-05 | 0.51885 | GF PASS; acc 0.518050; MC not run |
| `runs/v22_B_cat3reusered_3102` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.878728e-05 | 1.454061e-05 | 5.332788e-05 | 0.51885 | GF PASS; acc 0.518302; MC not run |
| `runs/v22_B_cat3reusered_3120` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.918542e-05 | 1.443462e-05 | 5.362004e-05 | 0.51886 | GF PASS; acc 0.518856; MC not run |
| `runs/v22_B_cat3reusered_3201` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.957249e-05 | 1.430622e-05 | 5.387871e-05 | 0.51885 | GF PASS; acc 0.518863; MC not run |
| `runs/v22_B_cat3reusered_3210` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.970556e-05 | 1.431368e-05 | 5.401924e-05 | 0.51886 | GF PASS; acc 0.518786; MC not run |
| `runs/v22_B_cat3spinered_0123` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.884935e-05 | 1.421939e-05 | 5.306874e-05 | 0.51885 | GF PASS; acc 0.519603; MC not run |
| `runs/v22_B_cat3spinered_0132` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.871664e-05 | 1.436947e-05 | 5.308611e-05 | 0.51885 | GF PASS; acc 0.518152; MC not run |
| `runs/v22_B_cat3spinered_0213` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.884713e-05 | 1.411117e-05 | 5.29583e-05 | 0.51885 | GF PASS; acc 0.518022; MC not run |
| `runs/v22_B_cat3spinered_0231` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.897984e-05 | 1.414506e-05 | 5.31249e-05 | 0.51885 | GF PASS; acc 0.518789; MC not run |
| `runs/v22_B_cat3spinered_0312` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.921936e-05 | 1.441679e-05 | 5.363614e-05 | 0.51885 | GF PASS; acc 0.518182; MC not run |
| `runs/v22_B_cat3spinered_0321` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.948256e-05 | 1.430001e-05 | 5.378257e-05 | 0.51885 | GF PASS; acc 0.518290; MC not run |
| `runs/v22_B_cat3spinered_1023` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.884935e-05 | 1.422104e-05 | 5.30704e-05 | 0.51885 | GF PASS; acc 0.518161; MC not run |
| `runs/v22_B_cat3spinered_1032` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.871664e-05 | 1.437049e-05 | 5.308713e-05 | 0.51885 | GF PASS; acc 0.519561; MC not run |
| `runs/v22_B_cat3spinered_1203` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.960343e-05 | 1.414139e-05 | 5.374482e-05 | 0.51885 | GF PASS; acc 0.518164; MC not run |
| `runs/v22_B_cat3spinered_1230` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.986663e-05 | 1.4185e-05 | 5.405163e-05 | 0.51885 | GF PASS; acc 0.518306; MC not run |
| `runs/v22_B_cat3spinered_1302` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.871886e-05 | 1.440322e-05 | 5.312208e-05 | 0.51885 | GF PASS; acc 0.518050; MC not run |
| `runs/v22_B_cat3spinered_1320` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.911256e-05 | 1.429748e-05 | 5.341003e-05 | 0.51885 | GF PASS; acc 0.518774; MC not run |
| `runs/v22_B_cat3spinered_2013` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.884269e-05 | 1.41158e-05 | 5.295848e-05 | 0.51885 | GF PASS; acc 0.518790; MC not run |
| `runs/v22_B_cat3spinered_2031` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.89754e-05 | 1.414932e-05 | 5.312472e-05 | 0.51885 | GF PASS; acc 0.518059; MC not run |
| `runs/v22_B_cat3spinered_2103` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.960121e-05 | 1.414434e-05 | 5.374555e-05 | 0.51885 | GF PASS; acc 0.518262; MC not run |
| `runs/v22_B_cat3spinered_2130` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.986441e-05 | 1.418833e-05 | 5.405274e-05 | 0.51885 | GF PASS; acc 0.518188; MC not run |
| `runs/v22_B_cat3spinered_2301` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.948034e-05 | 1.417188e-05 | 5.365222e-05 | 0.51885 | GF PASS; acc 0.519582; MC not run |
| `runs/v22_B_cat3spinered_2310` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.961305e-05 | 1.418231e-05 | 5.379536e-05 | 0.51885 | GF PASS; acc 0.518142; MC not run |
| `runs/v22_B_cat3spinered_3012` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.921713e-05 | 1.439464e-05 | 5.361178e-05 | 0.51885 | GF PASS; acc 0.518280; MC not run |
| `runs/v22_B_cat3spinered_3021` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.948034e-05 | 1.427817e-05 | 5.375851e-05 | 0.51885 | GF PASS; acc 0.518188; MC not run |
| `runs/v22_B_cat3spinered_3102` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.871886e-05 | 1.437997e-05 | 5.309884e-05 | 0.51885 | GF PASS; acc 0.518759; MC not run |
| `runs/v22_B_cat3spinered_3120` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.911256e-05 | 1.427385e-05 | 5.338641e-05 | 0.51885 | GF PASS; acc 0.518068; MC not run |
| `runs/v22_B_cat3spinered_3201` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.948034e-05 | 1.414565e-05 | 5.362598e-05 | 0.51885 | GF PASS; acc 0.518170; MC not run |
| `runs/v22_B_cat3spinered_3210` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.961305e-05 | 1.415547e-05 | 5.376852e-05 | 0.51885 | GF PASS; acc 0.519599; MC not run |
| `runs/v22_B_cat4_012` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.101923e-05 | 1.757703e-05 | 5.859626e-05 | 0.56547 | GF PASS; acc 0.565765; MC not run |
| `runs/v22_B_cat4_021` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.132128e-05 | 1.749222e-05 | 5.881349e-05 | 0.56547 | GF PASS; acc 0.565775; MC not run |
| `runs/v22_B_cat4_102` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.068175e-05 | 1.758063e-05 | 5.826238e-05 | 0.56547 | GF PASS; acc 0.565763; MC not run |
| `runs/v22_B_cat4_120` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.073514e-05 | 1.750186e-05 | 5.823701e-05 | 0.56547 | GF PASS; acc 0.564911; MC not run |
| `runs/v22_B_cat4_201` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.132134e-05 | 1.740905e-05 | 5.873038e-05 | 0.56547 | GF PASS; acc 0.564947; MC not run |
| `runs/v22_B_cat4_210` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.107257e-05 | 1.741503e-05 | 5.848759e-05 | 0.56547 | GF PASS; acc 0.564926; MC not run |
| `runs/v22_B_cat_012` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 4.014154e-05 | 1.535287e-05 | 5.549441e-05 | 0.58280 | GF PASS; acc 0.583219; MC not run |
| `runs/v22_B_cat_021` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 4.030821e-05 | 1.530677e-05 | 5.561498e-05 | 0.58280 | GF PASS; acc 0.583165; MC not run |
| `runs/v22_B_cat_102` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 3.980406e-05 | 1.535593e-05 | 5.516e-05 | 0.58280 | GF PASS; acc 0.581564; MC not run |
| `runs/v22_B_cat_120` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 4.019014e-05 | 1.560726e-05 | 5.579739e-05 | 0.58091 | GF PASS; acc 0.580450; MC not run |
| `runs/v22_B_cat_201` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 4.061849e-05 | 1.572093e-05 | 5.633942e-05 | 0.57995 | GF PASS; acc 0.579426; MC not run |
| `runs/v22_B_cat_210` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 4.021446e-05 | 1.543967e-05 | 5.565413e-05 | 0.58207 | GF PASS; acc 0.580998; MC not run |
| `runs/v22_B_catred_012` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.86483e-05 | 1.230557e-05 | 5.095387e-05 | 0.57490 | GF PASS; acc 0.574324; MC not run |
| `runs/v22_B_catred_0132` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.858181e-05 | 1.225041e-05 | 5.083222e-05 | 0.57490 | GF PASS; acc 0.574371; MC not run |
| `runs/v22_B_catred_021` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.864833e-05 | 1.229884e-05 | 5.094717e-05 | 0.57490 | GF PASS; acc 0.573845; MC not run |
| `runs/v22_B_catred_0231` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.866809e-05 | 1.249776e-05 | 5.116585e-05 | 0.57188 | GF PASS; acc 0.571789; MC not run |
| `runs/v22_B_catred_0312` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.868154e-05 | 1.244061e-05 | 5.112215e-05 | 0.57360 | GF PASS; acc 0.573517; MC not run |
| `runs/v22_B_catred_0321` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.868154e-05 | 1.244225e-05 | 5.112379e-05 | 0.57360 | GF PASS; acc 0.573549; MC not run |
| `runs/v22_B_catred_102` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.86483e-05 | 1.230994e-05 | 5.095824e-05 | 0.57432 | GF PASS; acc 0.574208; MC not run |
| `runs/v22_B_catred_1032` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.858181e-05 | 1.225405e-05 | 5.083586e-05 | 0.57432 | GF PASS; acc 0.573395; MC not run |
| `runs/v22_B_catred_120` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.879025e-05 | 1.245826e-05 | 5.124852e-05 | 0.57264 | GF PASS; acc 0.572122; MC not run |
| `runs/v22_B_catred_1230` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.881236e-05 | 1.244627e-05 | 5.125863e-05 | 0.57475 | GF PASS; acc 0.574686; MC not run |
| `runs/v22_B_catred_1302` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.858181e-05 | 1.22537e-05 | 5.083551e-05 | 0.57432 | GF PASS; acc 0.573512; MC not run |
| `runs/v22_B_catred_1320` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.875911e-05 | 1.24731e-05 | 5.123222e-05 | 0.57188 | GF PASS; acc 0.571053; MC not run |
| `runs/v22_B_catred_201` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.864833e-05 | 1.245546e-05 | 5.110379e-05 | 0.57226 | GF PASS; acc 0.571871; MC not run |
| `runs/v22_B_catred_2031` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.869031e-05 | 1.265727e-05 | 5.134758e-05 | 0.56869 | GF PASS; acc 0.567819; MC not run |
| `runs/v22_B_catred_210` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.874584e-05 | 1.245047e-05 | 5.119631e-05 | 0.57379 | GF PASS; acc 0.573117; MC not run |
| `runs/v22_B_catred_2130` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.881239e-05 | 1.244724e-05 | 5.125963e-05 | 0.57474 | GF PASS; acc 0.574105; MC not run |
| `runs/v22_B_catred_2301` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.870365e-05 | 1.256735e-05 | 5.1271e-05 | 0.57364 | GF PASS; acc 0.573189; MC not run |
| `runs/v22_B_catred_2310` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.872581e-05 | 1.257654e-05 | 5.130235e-05 | 0.57192 | GF PASS; acc 0.572031; MC not run |
| `runs/v22_B_catred_3012` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.863728e-05 | 1.236836e-05 | 5.100563e-05 | 0.57417 | GF PASS; acc 0.573464; MC not run |
| `runs/v22_B_catred_3021` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.863728e-05 | 1.23702e-05 | 5.100747e-05 | 0.57417 | GF PASS; acc 0.573458; MC not run |
| `runs/v22_B_catred_3102` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.855739e-05 | 1.237019e-05 | 5.092759e-05 | 0.57321 | GF PASS; acc 0.572792; MC not run |
| `runs/v22_B_catred_3120` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.87347e-05 | 1.258041e-05 | 5.131511e-05 | 0.57249 | GF PASS; acc 0.571639; MC not run |
| `runs/v22_B_catred_3201` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.877008e-05 | 1.263338e-05 | 5.140346e-05 | 0.57135 | GF PASS; acc 0.570718; MC not run |
| `runs/v22_B_catred_3210` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.872581e-05 | 1.256377e-05 | 5.128958e-05 | 0.57364 | GF PASS; acc 0.572713; MC not run |
| `runs/v22_B_direct_012` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.955615e-05 | 1.50015e-05 | 5.455765e-05 | 0.58295 | GF PASS; acc 0.582397; MC not run |
| `runs/v22_B_direct_021` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.988884e-05 | 1.522589e-05 | 5.511473e-05 | 0.58063 | GF PASS; acc 0.579969; MC not run |
| `runs/v22_B_direct_102` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.949627e-05 | 1.541641e-05 | 5.491268e-05 | 0.57947 | GF PASS; acc 0.578756; MC not run |
| `runs/v22_B_direct_120` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.954306e-05 | 1.50212e-05 | 5.456426e-05 | 0.58236 | GF PASS; acc 0.582219; MC not run |
| `runs/v22_B_direct_201` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.98048e-05 | 1.496024e-05 | 5.476504e-05 | 0.58236 | GF PASS; acc 0.582192; MC not run |
| `runs/v22_B_direct_210` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.977814e-05 | 1.496135e-05 | 5.473949e-05 | 0.58236 | GF PASS; acc 0.581698; MC not run |
| `runs/v22_B_flag_012` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.008671e-05 | 1.628145e-05 | 5.636816e-05 | 0.56325 | GF PASS; acc 0.562293; MC not run |
| `runs/v22_B_flag_021` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.045775e-05 | 1.656995e-05 | 5.70277e-05 | 0.56045 | GF PASS; acc 0.560262; MC not run |
| `runs/v22_B_flag_102` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.005028e-05 | 1.681731e-05 | 5.686759e-05 | 0.55879 | GF PASS; acc 0.558335; MC not run |
| `runs/v22_B_flag_120` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.005604e-05 | 1.630548e-05 | 5.636152e-05 | 0.56268 | GF PASS; acc 0.561308; MC not run |
| `runs/v22_B_flag_201` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.032618e-05 | 1.625065e-05 | 5.657683e-05 | 0.56268 | GF PASS; acc 0.561266; MC not run |
| `runs/v22_B_flag_210` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.02686e-05 | 1.625169e-05 | 5.652029e-05 | 0.56268 | GF PASS; acc 0.562866; MC not run |
| `runs/v22_B_hybrid1_012` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.966158e-05 | 1.51364e-05 | 5.479798e-05 | 0.57897 | GF PASS; acc 0.578707; MC not run |
| `runs/v22_B_hybrid1_021` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.981684e-05 | 1.508109e-05 | 5.489793e-05 | 0.57897 | GF PASS; acc 0.578629; MC not run |
| `runs/v22_B_hybrid1_102` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.966158e-05 | 1.51364e-05 | 5.479798e-05 | 0.57897 | GF PASS; acc 0.578707; MC not run |
| `runs/v22_B_hybrid1_120` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.966158e-05 | 1.51364e-05 | 5.479798e-05 | 0.57897 | GF PASS; acc 0.578707; MC not run |
| `runs/v22_B_hybrid1_201` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.981684e-05 | 1.508109e-05 | 5.489793e-05 | 0.57897 | GF PASS; acc 0.578629; MC not run |
| `runs/v22_B_hybrid1_210` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.981684e-05 | 1.508109e-05 | 5.489793e-05 | 0.57897 | GF PASS; acc 0.578629; MC not run |
| `runs/v22_B_hybrid2_012` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.469813e-05 | 5.397463e-05 | 0.58218 | GF PASS; acc 0.582531; MC not run |
| `runs/v22_B_hybrid2_021` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.469813e-05 | 5.397463e-05 | 0.58218 | GF PASS; acc 0.582531; MC not run |
| `runs/v22_B_hybrid2_102` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.469813e-05 | 5.397463e-05 | 0.58218 | GF PASS; acc 0.582531; MC not run |
| `runs/v22_B_hybrid2_120` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.469813e-05 | 5.397463e-05 | 0.58218 | GF PASS; acc 0.582531; MC not run |
| `runs/v22_B_hybrid2_201` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.469813e-05 | 5.397463e-05 | 0.58218 | GF PASS; acc 0.582531; MC not run |
| `runs/v22_B_hybrid2_210` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.469813e-05 | 5.397463e-05 | 0.58218 | GF PASS; acc 0.582531; MC not run |
| `runs/v22_B_hybrid2t_012` (regenerate) | B hybrid2t | 123 | 45 | 2.923587e-19 | 3.947918e-05 | 1.499926e-05 | 5.447844e-05 | 0.57987 | GF PASS; acc 0.579028; MC not run |
| `runs/v22_B_redundant_012` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.852581e-05 | 1.292171e-05 | 5.144752e-05 | 0.57664 | GF PASS; acc 0.576179; MC not run |
| `runs/v22_B_redundant_0132` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.868842e-05 | 1.334498e-05 | 5.20334e-05 | 0.57318 | GF PASS; acc 0.572061; MC not run |
| `runs/v22_B_redundant_021` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.852498e-05 | 1.291738e-05 | 5.144237e-05 | 0.57435 | GF PASS; acc 0.574186; MC not run |
| `runs/v22_B_redundant_0231` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.859118e-05 | 1.30708e-05 | 5.166198e-05 | 0.57374 | GF PASS; acc 0.572954; MC not run |
| `runs/v22_B_redundant_0312` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.872398e-05 | 1.322238e-05 | 5.194636e-05 | 0.57543 | GF PASS; acc 0.574818; MC not run |
| `runs/v22_B_redundant_0321` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.881129e-05 | 1.327932e-05 | 5.209061e-05 | 0.57258 | GF PASS; acc 0.572610; MC not run |
| `runs/v22_B_redundant_102` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.855165e-05 | 1.300252e-05 | 5.155417e-05 | 0.57321 | GF PASS; acc 0.573081; MC not run |
| `runs/v22_B_redundant_1032` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.869287e-05 | 1.334482e-05 | 5.203769e-05 | 0.57318 | GF PASS; acc 0.572704; MC not run |
| `runs/v22_B_redundant_120` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.865221e-05 | 1.285857e-05 | 5.151078e-05 | 0.57606 | GF PASS; acc 0.575568; MC not run |
| `runs/v22_B_redundant_1230` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.869654e-05 | 1.286464e-05 | 5.156117e-05 | 0.57606 | GF PASS; acc 0.575790; MC not run |
| `runs/v22_B_redundant_1302` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.86496e-05 | 1.327785e-05 | 5.192745e-05 | 0.57489 | GF PASS; acc 0.574468; MC not run |
| `runs/v22_B_redundant_1320` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.867334e-05 | 1.315015e-05 | 5.182349e-05 | 0.57260 | GF PASS; acc 0.572717; MC not run |
| `runs/v22_B_redundant_201` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.852803e-05 | 1.285706e-05 | 5.138509e-05 | 0.57606 | GF PASS; acc 0.575483; MC not run |
| `runs/v22_B_redundant_2031` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.859423e-05 | 1.301377e-05 | 5.1608e-05 | 0.57431 | GF PASS; acc 0.573786; MC not run |
| `runs/v22_B_redundant_210` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.865221e-05 | 1.285894e-05 | 5.151115e-05 | 0.57607 | GF PASS; acc 0.575711; MC not run |
| `runs/v22_B_redundant_2130` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.869654e-05 | 1.286517e-05 | 5.15617e-05 | 0.57606 | GF PASS; acc 0.574996; MC not run |
| `runs/v22_B_redundant_2301` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.86299e-05 | 1.294123e-05 | 5.157113e-05 | 0.57660 | GF PASS; acc 0.575617; MC not run |
| `runs/v22_B_redundant_2310` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.865663e-05 | 1.294917e-05 | 5.16058e-05 | 0.57488 | GF PASS; acc 0.574457; MC not run |
| `runs/v22_B_redundant_3012` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.868072e-05 | 1.314197e-05 | 5.182269e-05 | 0.57830 | GF PASS; acc 0.577708; MC not run |
| `runs/v22_B_redundant_3021` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.876819e-05 | 1.320902e-05 | 5.197721e-05 | 0.57428 | GF PASS; acc 0.572867; MC not run |
| `runs/v22_B_redundant_3102` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.867007e-05 | 1.336114e-05 | 5.203121e-05 | 0.57258 | GF PASS; acc 0.572756; MC not run |
| `runs/v22_B_redundant_3120` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.867334e-05 | 1.308214e-05 | 5.175548e-05 | 0.57543 | GF PASS; acc 0.573484; MC not run |
| `runs/v22_B_redundant_3201` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.872539e-05 | 1.307091e-05 | 5.17963e-05 | 0.57314 | GF PASS; acc 0.572154; MC not run |
| `runs/v22_B_redundant_3210` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.875212e-05 | 1.30713e-05 | 5.182342e-05 | 0.57314 | GF PASS; acc 0.572671; MC not run |
| `runs/v22_B_seq_012` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 4.069542e-05 | 1.805211e-05 | 5.874753e-05 | 0.55586 | GF PASS; acc 0.554865; MC not run |
| `runs/v22_B_seq_021` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 4.120328e-05 | 1.782491e-05 | 5.90282e-05 | 0.55586 | GF PASS; acc 0.554503; MC not run |
| `runs/v22_B_seq_102` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 3.967665e-05 | 1.804674e-05 | 5.772338e-05 | 0.55586 | GF PASS; acc 0.555383; MC not run |
| `runs/v22_B_seq_120` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 4.055283e-05 | 1.789747e-05 | 5.84503e-05 | 0.55531 | GF PASS; acc 0.554605; MC not run |
| `runs/v22_B_seq_201` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 4.129608e-05 | 1.763491e-05 | 5.893099e-05 | 0.55531 | GF PASS; acc 0.554740; MC not run |
| `runs/v22_B_seq_210` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 4.157979e-05 | 1.763839e-05 | 5.921818e-05 | 0.55531 | GF PASS; acc 0.554751; MC not run |
| `runs/v22_C_cat13_012` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 3.980587e-05 | 1.549235e-05 | 5.529822e-05 | 0.57979 | GF PASS; acc 0.578817; MC not run |
| `runs/v22_C_cat13_021` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 4.013879e-05 | 1.571235e-05 | 5.585114e-05 | 0.57748 | GF PASS; acc 0.576932; MC not run |
| `runs/v22_C_cat13_102` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 3.974599e-05 | 1.590074e-05 | 5.564673e-05 | 0.57633 | GF PASS; acc 0.575783; MC not run |
| `runs/v22_C_cat13_120` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 3.979265e-05 | 1.551142e-05 | 5.530407e-05 | 0.57921 | GF PASS; acc 0.578504; MC not run |
| `runs/v22_C_cat13_201` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 4.005464e-05 | 1.545002e-05 | 5.550466e-05 | 0.57921 | GF PASS; acc 0.578540; MC not run |
| `runs/v22_C_cat13_210` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 4.002785e-05 | 1.545144e-05 | 5.54793e-05 | 0.57921 | GF PASS; acc 0.578476; MC not run |
| `runs/v22_C_cat13red_012` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.839283e-05 | 1.270006e-05 | 5.109289e-05 | 0.56851 | GF PASS; acc 0.568335; MC not run |
| `runs/v22_C_cat13red_0132` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.829085e-05 | 1.261665e-05 | 5.09075e-05 | 0.56772 | GF PASS; acc 0.567124; MC not run |
| `runs/v22_C_cat13red_021` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.839201e-05 | 1.269216e-05 | 5.108417e-05 | 0.56625 | GF PASS; acc 0.566173; MC not run |
| `runs/v22_C_cat13red_0231` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.836984e-05 | 1.251625e-05 | 5.08861e-05 | 0.56527 | GF PASS; acc 0.564287; MC not run |
| `runs/v22_C_cat13red_0312` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.83264e-05 | 1.237499e-05 | 5.070139e-05 | 0.56692 | GF PASS; acc 0.566681; MC not run |
| `runs/v22_C_cat13red_0321` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.83264e-05 | 1.236701e-05 | 5.069341e-05 | 0.56692 | GF PASS; acc 0.565918; MC not run |
| `runs/v22_C_cat13red_102` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.841867e-05 | 1.277465e-05 | 5.119333e-05 | 0.56512 | GF PASS; acc 0.565261; MC not run |
| `runs/v22_C_cat13red_1032` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.829529e-05 | 1.261654e-05 | 5.091183e-05 | 0.56772 | GF PASS; acc 0.567564; MC not run |
| `runs/v22_C_cat13red_120` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.851923e-05 | 1.263728e-05 | 5.115651e-05 | 0.56794 | GF PASS; acc 0.567642; MC not run |
| `runs/v22_C_cat13red_1230` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.856356e-05 | 1.26475e-05 | 5.121105e-05 | 0.56718 | GF PASS; acc 0.566923; MC not run |
| `runs/v22_C_cat13red_1302` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.829529e-05 | 1.269199e-05 | 5.098728e-05 | 0.56565 | GF PASS; acc 0.565429; MC not run |
| `runs/v22_C_cat13red_1320` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.8364e-05 | 1.256729e-05 | 5.09313e-05 | 0.56677 | GF PASS; acc 0.566269; MC not run |
| `runs/v22_C_cat13red_201` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.839505e-05 | 1.263607e-05 | 5.103112e-05 | 0.56794 | GF PASS; acc 0.567331; MC not run |
| `runs/v22_C_cat13red_2031` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.837289e-05 | 1.245915e-05 | 5.083204e-05 | 0.56695 | GF PASS; acc 0.566266; MC not run |
| `runs/v22_C_cat13red_210` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.851923e-05 | 1.26384e-05 | 5.115763e-05 | 0.56794 | GF PASS; acc 0.567529; MC not run |
| `runs/v22_C_cat13red_2130` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.856356e-05 | 1.264892e-05 | 5.121247e-05 | 0.56718 | GF PASS; acc 0.566927; MC not run |
| `runs/v22_C_cat13red_2301` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.845271e-05 | 1.246387e-05 | 5.091659e-05 | 0.56658 | GF PASS; acc 0.566176; MC not run |
| `runs/v22_C_cat13red_2310` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.852365e-05 | 1.246552e-05 | 5.098916e-05 | 0.56658 | GF PASS; acc 0.566358; MC not run |
| `runs/v22_C_cat13red_3012` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.83264e-05 | 1.237144e-05 | 5.069784e-05 | 0.56692 | GF PASS; acc 0.566545; MC not run |
| `runs/v22_C_cat13red_3021` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.83264e-05 | 1.237491e-05 | 5.070131e-05 | 0.56466 | GF PASS; acc 0.564010; MC not run |
| `runs/v22_C_cat13red_3102` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.831751e-05 | 1.244625e-05 | 5.076377e-05 | 0.56354 | GF PASS; acc 0.563360; MC not run |
| `runs/v22_C_cat13red_3120` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.8364e-05 | 1.231466e-05 | 5.067866e-05 | 0.56635 | GF PASS; acc 0.566187; MC not run |
| `runs/v22_C_cat13red_3201` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.832862e-05 | 1.230656e-05 | 5.063519e-05 | 0.56635 | GF PASS; acc 0.566214; MC not run |
| `runs/v22_C_cat13red_3210` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.839956e-05 | 1.230736e-05 | 5.070692e-05 | 0.56636 | GF PASS; acc 0.565765; MC not run |
| `runs/v22_C_cat3_012` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.064391e-05 | 1.638157e-05 | 5.702548e-05 | 0.57539 | GF PASS; acc 0.574682; MC not run |
| `runs/v22_C_cat3_021` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.076836e-05 | 1.634163e-05 | 5.710998e-05 | 0.57539 | GF PASS; acc 0.574695; MC not run |
| `runs/v22_C_cat3_102` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.030637e-05 | 1.638532e-05 | 5.669169e-05 | 0.57539 | GF PASS; acc 0.574681; MC not run |
| `runs/v22_C_cat3_120` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.053731e-05 | 1.658085e-05 | 5.711816e-05 | 0.57310 | GF PASS; acc 0.572262; MC not run |
| `runs/v22_C_cat3_201` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.094596e-05 | 1.653366e-05 | 5.747962e-05 | 0.57310 | GF PASS; acc 0.572296; MC not run |
| `runs/v22_C_cat3_210` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.069725e-05 | 1.653884e-05 | 5.723609e-05 | 0.57310 | GF PASS; acc 0.572284; MC not run |
| `runs/v22_C_cat3red_0123` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.851751e-05 | 1.216808e-05 | 5.068559e-05 | 0.56558 | GF PASS; acc 0.565982; MC not run |
| `runs/v22_C_cat3red_0132` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.855301e-05 | 1.221805e-05 | 5.077106e-05 | 0.56374 | GF PASS; acc 0.563369; MC not run |
| `runs/v22_C_cat3red_0213` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.851751e-05 | 1.216229e-05 | 5.067981e-05 | 0.56558 | GF PASS; acc 0.566016; MC not run |
| `runs/v22_C_cat3red_0231` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.860388e-05 | 1.237488e-05 | 5.097877e-05 | 0.55925 | GF PASS; acc 0.559678; MC not run |
| `runs/v22_C_cat3red_0312` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.865274e-05 | 1.241916e-05 | 5.107191e-05 | 0.56078 | GF PASS; acc 0.560442; MC not run |
| `runs/v22_C_cat3red_0321` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.865274e-05 | 1.242086e-05 | 5.10736e-05 | 0.56078 | GF PASS; acc 0.560479; MC not run |
| `runs/v22_C_cat3red_1023` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.851751e-05 | 1.217243e-05 | 5.068994e-05 | 0.56501 | GF PASS; acc 0.564039; MC not run |
| `runs/v22_C_cat3red_1032` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.855301e-05 | 1.222174e-05 | 5.077475e-05 | 0.56317 | GF PASS; acc 0.562933; MC not run |
| `runs/v22_C_cat3red_1203` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.857085e-05 | 1.218032e-05 | 5.075116e-05 | 0.56276 | GF PASS; acc 0.561435; MC not run |
| `runs/v22_C_cat3red_1230` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.857085e-05 | 1.217784e-05 | 5.074869e-05 | 0.56276 | GF PASS; acc 0.561458; MC not run |
| `runs/v22_C_cat3red_1302` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.855301e-05 | 1.221591e-05 | 5.076892e-05 | 0.56486 | GF PASS; acc 0.564006; MC not run |
| `runs/v22_C_cat3red_1320` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.859734e-05 | 1.229099e-05 | 5.088833e-05 | 0.56111 | GF PASS; acc 0.560609; MC not run |
| `runs/v22_C_cat3red_2013` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.851751e-05 | 1.216841e-05 | 5.068593e-05 | 0.56501 | GF PASS; acc 0.564023; MC not run |
| `runs/v22_C_cat3red_2031` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.860388e-05 | 1.238846e-05 | 5.099234e-05 | 0.55702 | GF PASS; acc 0.556302; MC not run |
| `runs/v22_C_cat3red_2103` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.857085e-05 | 1.218219e-05 | 5.075304e-05 | 0.56276 | GF PASS; acc 0.561435; MC not run |
| `runs/v22_C_cat3red_2130` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.857085e-05 | 1.218006e-05 | 5.075091e-05 | 0.56276 | GF PASS; acc 0.561457; MC not run |
| `runs/v22_C_cat3red_2301` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.859517e-05 | 1.230433e-05 | 5.08995e-05 | 0.56093 | GF PASS; acc 0.560239; MC not run |
| `runs/v22_C_cat3red_2310` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.855085e-05 | 1.231547e-05 | 5.086632e-05 | 0.55832 | GF PASS; acc 0.557883; MC not run |
| `runs/v22_C_cat3red_3012` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.860848e-05 | 1.233314e-05 | 5.094161e-05 | 0.56471 | GF PASS; acc 0.564373; MC not run |
| `runs/v22_C_cat3red_3021` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.860848e-05 | 1.233481e-05 | 5.094329e-05 | 0.56471 | GF PASS; acc 0.564377; MC not run |
| `runs/v22_C_cat3red_3102` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.852859e-05 | 1.234034e-05 | 5.086894e-05 | 0.56209 | GF PASS; acc 0.561493; MC not run |
| `runs/v22_C_cat3red_3120` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.857292e-05 | 1.240991e-05 | 5.098283e-05 | 0.56003 | GF PASS; acc 0.559584; MC not run |
| `runs/v22_C_cat3red_3201` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.86528e-05 | 1.239299e-05 | 5.104579e-05 | 0.56265 | GF PASS; acc 0.562039; MC not run |
| `runs/v22_C_cat3red_3210` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.860848e-05 | 1.240238e-05 | 5.101086e-05 | 0.56003 | GF PASS; acc 0.559589; MC not run |
| `runs/v22_C_cat3reusered_0123` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.888707e-05 | 1.409596e-05 | 5.298303e-05 | 0.51776 | GF PASS; acc 0.517459; MC not run |
| `runs/v22_C_cat3reusered_0132` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.87895e-05 | 1.428603e-05 | 5.307553e-05 | 0.51831 | GF PASS; acc 0.518122; MC not run |
| `runs/v22_C_cat3reusered_0213` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.888707e-05 | 1.398503e-05 | 5.28721e-05 | 0.51776 | GF PASS; acc 0.517798; MC not run |
| `runs/v22_C_cat3reusered_0231` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.901721e-05 | 1.40702e-05 | 5.30874e-05 | 0.51831 | GF PASS; acc 0.517971; MC not run |
| `runs/v22_C_cat3reusered_0312` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.930742e-05 | 1.438472e-05 | 5.369214e-05 | 0.51886 | GF PASS; acc 0.518446; MC not run |
| `runs/v22_C_cat3reusered_0321` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.957249e-05 | 1.427068e-05 | 5.384317e-05 | 0.51886 | GF PASS; acc 0.518597; MC not run |
| `runs/v22_C_cat3reusered_1023` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.888707e-05 | 1.409792e-05 | 5.298499e-05 | 0.51776 | GF PASS; acc 0.517281; MC not run |
| `runs/v22_C_cat3reusered_1032` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.87895e-05 | 1.428784e-05 | 5.307734e-05 | 0.51831 | GF PASS; acc 0.518512; MC not run |
| `runs/v22_C_cat3reusered_1203` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.966781e-05 | 1.401546e-05 | 5.368328e-05 | 0.51777 | GF PASS; acc 0.517630; MC not run |
| `runs/v22_C_cat3reusered_1230` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.993324e-05 | 1.405892e-05 | 5.399216e-05 | 0.51776 | GF PASS; acc 0.516982; MC not run |
| `runs/v22_C_cat3reusered_1302` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.87895e-05 | 1.432215e-05 | 5.311165e-05 | 0.51830 | GF PASS; acc 0.518027; MC not run |
| `runs/v22_C_cat3reusered_1320` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.918764e-05 | 1.421624e-05 | 5.340388e-05 | 0.51831 | GF PASS; acc 0.518062; MC not run |
| `runs/v22_C_cat3reusered_2013` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.888707e-05 | 1.39896e-05 | 5.287667e-05 | 0.51776 | GF PASS; acc 0.517289; MC not run |
| `runs/v22_C_cat3reusered_2031` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.901721e-05 | 1.40742e-05 | 5.309141e-05 | 0.51831 | GF PASS; acc 0.518325; MC not run |
| `runs/v22_C_cat3reusered_2103` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.966781e-05 | 1.401806e-05 | 5.368587e-05 | 0.51777 | GF PASS; acc 0.517594; MC not run |
| `runs/v22_C_cat3reusered_2130` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.993324e-05 | 1.406139e-05 | 5.399463e-05 | 0.51776 | GF PASS; acc 0.517017; MC not run |
| `runs/v22_C_cat3reusered_2301` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.95377e-05 | 1.409835e-05 | 5.363605e-05 | 0.51830 | GF PASS; acc 0.518108; MC not run |
| `runs/v22_C_cat3reusered_2310` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.967077e-05 | 1.410595e-05 | 5.377671e-05 | 0.51831 | GF PASS; acc 0.517656; MC not run |
| `runs/v22_C_cat3reusered_3012` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.930742e-05 | 1.436257e-05 | 5.366999e-05 | 0.51885 | GF PASS; acc 0.519362; MC not run |
| `runs/v22_C_cat3reusered_3021` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.957249e-05 | 1.424856e-05 | 5.382105e-05 | 0.51885 | GF PASS; acc 0.518408; MC not run |
| `runs/v22_C_cat3reusered_3102` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.878728e-05 | 1.434745e-05 | 5.313473e-05 | 0.51885 | GF PASS; acc 0.518923; MC not run |
| `runs/v22_C_cat3reusered_3120` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.918542e-05 | 1.424141e-05 | 5.342682e-05 | 0.51886 | GF PASS; acc 0.517809; MC not run |
| `runs/v22_C_cat3reusered_3201` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.957249e-05 | 1.411293e-05 | 5.368542e-05 | 0.51885 | GF PASS; acc 0.518573; MC not run |
| `runs/v22_C_cat3reusered_3210` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.970556e-05 | 1.41204e-05 | 5.382596e-05 | 0.51886 | GF PASS; acc 0.519042; MC not run |
| `runs/v22_C_cat3spinered_0123` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.884935e-05 | 1.402691e-05 | 5.287626e-05 | 0.51885 | GF PASS; acc 0.518627; MC not run |
| `runs/v22_C_cat3spinered_0132` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.871664e-05 | 1.417726e-05 | 5.28939e-05 | 0.51885 | GF PASS; acc 0.518421; MC not run |
| `runs/v22_C_cat3spinered_0213` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.884713e-05 | 1.391855e-05 | 5.276568e-05 | 0.51885 | GF PASS; acc 0.518877; MC not run |
| `runs/v22_C_cat3spinered_0231` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.897984e-05 | 1.395264e-05 | 5.293248e-05 | 0.51885 | GF PASS; acc 0.518545; MC not run |
| `runs/v22_C_cat3spinered_0312` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.921936e-05 | 1.422505e-05 | 5.34444e-05 | 0.51885 | GF PASS; acc 0.519467; MC not run |
| `runs/v22_C_cat3spinered_0321` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.948256e-05 | 1.410821e-05 | 5.359077e-05 | 0.51885 | GF PASS; acc 0.518508; MC not run |
| `runs/v22_C_cat3spinered_1023` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.884935e-05 | 1.40285e-05 | 5.287785e-05 | 0.51885 | GF PASS; acc 0.518412; MC not run |
| `runs/v22_C_cat3spinered_1032` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.871664e-05 | 1.417821e-05 | 5.289485e-05 | 0.51885 | GF PASS; acc 0.518598; MC not run |
| `runs/v22_C_cat3spinered_1203` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.960343e-05 | 1.394901e-05 | 5.355244e-05 | 0.51885 | GF PASS; acc 0.519478; MC not run |
| `runs/v22_C_cat3spinered_1230` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.986663e-05 | 1.399282e-05 | 5.385945e-05 | 0.51885 | GF PASS; acc 0.518473; MC not run |
| `runs/v22_C_cat3spinered_1302` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.871886e-05 | 1.421102e-05 | 5.292989e-05 | 0.51885 | GF PASS; acc 0.518904; MC not run |
| `runs/v22_C_cat3spinered_1320` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.911256e-05 | 1.410521e-05 | 5.321776e-05 | 0.51885 | GF PASS; acc 0.518542; MC not run |
| `runs/v22_C_cat3spinered_2013` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.884269e-05 | 1.392304e-05 | 5.276572e-05 | 0.51885 | GF PASS; acc 0.518523; MC not run |
| `runs/v22_C_cat3spinered_2031` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.89754e-05 | 1.395675e-05 | 5.293215e-05 | 0.51885 | GF PASS; acc 0.518889; MC not run |
| `runs/v22_C_cat3spinered_2103` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.960121e-05 | 1.395189e-05 | 5.355309e-05 | 0.51885 | GF PASS; acc 0.518474; MC not run |
| `runs/v22_C_cat3spinered_2130` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.986441e-05 | 1.399607e-05 | 5.386048e-05 | 0.51885 | GF PASS; acc 0.519465; MC not run |
| `runs/v22_C_cat3spinered_2301` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.948034e-05 | 1.397948e-05 | 5.345981e-05 | 0.51885 | GF PASS; acc 0.518633; MC not run |
| `runs/v22_C_cat3spinered_2310` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.961305e-05 | 1.39899e-05 | 5.360295e-05 | 0.51885 | GF PASS; acc 0.518420; MC not run |
| `runs/v22_C_cat3spinered_3012` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.921713e-05 | 1.420281e-05 | 5.341995e-05 | 0.51885 | GF PASS; acc 0.518511; MC not run |
| `runs/v22_C_cat3spinered_3021` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.948034e-05 | 1.408629e-05 | 5.356662e-05 | 0.51885 | GF PASS; acc 0.519490; MC not run |
| `runs/v22_C_cat3spinered_3102` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.871886e-05 | 1.418776e-05 | 5.290663e-05 | 0.51885 | GF PASS; acc 0.518523; MC not run |
| `runs/v22_C_cat3spinered_3120` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.911256e-05 | 1.408157e-05 | 5.319413e-05 | 0.51885 | GF PASS; acc 0.518837; MC not run |
| `runs/v22_C_cat3spinered_3201` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.948034e-05 | 1.39533e-05 | 5.343364e-05 | 0.51885 | GF PASS; acc 0.518438; MC not run |
| `runs/v22_C_cat3spinered_3210` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.961305e-05 | 1.396313e-05 | 5.357618e-05 | 0.51885 | GF PASS; acc 0.518647; MC not run |
| `runs/v22_C_cat4_012` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.101923e-05 | 1.747312e-05 | 5.849235e-05 | 0.56547 | GF PASS; acc 0.565506; MC not run |
| `runs/v22_C_cat4_021` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.132128e-05 | 1.738828e-05 | 5.870955e-05 | 0.56547 | GF PASS; acc 0.565505; MC not run |
| `runs/v22_C_cat4_102` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.068175e-05 | 1.747665e-05 | 5.81584e-05 | 0.56547 | GF PASS; acc 0.565505; MC not run |
| `runs/v22_C_cat4_120` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.073514e-05 | 1.73978e-05 | 5.813294e-05 | 0.56547 | GF PASS; acc 0.564604; MC not run |
| `runs/v22_C_cat4_201` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.132134e-05 | 1.730499e-05 | 5.862633e-05 | 0.56547 | GF PASS; acc 0.564631; MC not run |
| `runs/v22_C_cat4_210` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.107257e-05 | 1.731093e-05 | 5.838349e-05 | 0.56547 | GF PASS; acc 0.564607; MC not run |
| `runs/v22_C_cat_012` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 4.014154e-05 | 1.530246e-05 | 5.544401e-05 | 0.58280 | GF PASS; acc 0.582709; MC not run |
| `runs/v22_C_cat_021` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 4.030821e-05 | 1.525629e-05 | 5.55645e-05 | 0.58280 | GF PASS; acc 0.582679; MC not run |
| `runs/v22_C_cat_102` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 3.980406e-05 | 1.530545e-05 | 5.510951e-05 | 0.58280 | GF PASS; acc 0.582574; MC not run |
| `runs/v22_C_cat_120` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 4.019014e-05 | 1.555499e-05 | 5.574512e-05 | 0.58091 | GF PASS; acc 0.580812; MC not run |
| `runs/v22_C_cat_201` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 4.061849e-05 | 1.566825e-05 | 5.628674e-05 | 0.57995 | GF PASS; acc 0.580062; MC not run |
| `runs/v22_C_cat_210` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 4.021446e-05 | 1.53913e-05 | 5.560576e-05 | 0.58207 | GF PASS; acc 0.581564; MC not run |
| `runs/v22_C_catred_012` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.86483e-05 | 1.224367e-05 | 5.089196e-05 | 0.57490 | GF PASS; acc 0.574588; MC not run |
| `runs/v22_C_catred_0132` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.858181e-05 | 1.218815e-05 | 5.076996e-05 | 0.57490 | GF PASS; acc 0.574436; MC not run |
| `runs/v22_C_catred_021` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.864833e-05 | 1.223693e-05 | 5.088526e-05 | 0.57490 | GF PASS; acc 0.574806; MC not run |
| `runs/v22_C_catred_0231` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.866809e-05 | 1.243407e-05 | 5.110216e-05 | 0.57188 | GF PASS; acc 0.571510; MC not run |
| `runs/v22_C_catred_0312` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.868154e-05 | 1.238009e-05 | 5.106164e-05 | 0.57360 | GF PASS; acc 0.572842; MC not run |
| `runs/v22_C_catred_0321` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.868154e-05 | 1.238173e-05 | 5.106328e-05 | 0.57360 | GF PASS; acc 0.572837; MC not run |
| `runs/v22_C_catred_102` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.86483e-05 | 1.224755e-05 | 5.089585e-05 | 0.57432 | GF PASS; acc 0.573967; MC not run |
| `runs/v22_C_catred_1032` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.858181e-05 | 1.219131e-05 | 5.077312e-05 | 0.57432 | GF PASS; acc 0.573920; MC not run |
| `runs/v22_C_catred_120` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.879025e-05 | 1.239512e-05 | 5.118537e-05 | 0.57264 | GF PASS; acc 0.572100; MC not run |
| `runs/v22_C_catred_1230` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.881236e-05 | 1.238724e-05 | 5.11996e-05 | 0.57475 | GF PASS; acc 0.574350; MC not run |
| `runs/v22_C_catred_1302` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.858181e-05 | 1.219099e-05 | 5.07728e-05 | 0.57432 | GF PASS; acc 0.573912; MC not run |
| `runs/v22_C_catred_1320` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.875911e-05 | 1.240704e-05 | 5.116616e-05 | 0.57188 | GF PASS; acc 0.571532; MC not run |
| `runs/v22_C_catred_201` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.864833e-05 | 1.239226e-05 | 5.104059e-05 | 0.57226 | GF PASS; acc 0.571638; MC not run |
| `runs/v22_C_catred_2031` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.869031e-05 | 1.258915e-05 | 5.127946e-05 | 0.56869 | GF PASS; acc 0.567589; MC not run |
| `runs/v22_C_catred_210` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.874584e-05 | 1.239092e-05 | 5.113676e-05 | 0.57379 | GF PASS; acc 0.572347; MC not run |
| `runs/v22_C_catred_2130` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.881239e-05 | 1.238821e-05 | 5.12006e-05 | 0.57474 | GF PASS; acc 0.574821; MC not run |
| `runs/v22_C_catred_2301` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.870365e-05 | 1.251002e-05 | 5.121367e-05 | 0.57364 | GF PASS; acc 0.573145; MC not run |
| `runs/v22_C_catred_2310` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.872581e-05 | 1.251543e-05 | 5.124124e-05 | 0.57192 | GF PASS; acc 0.571574; MC not run |
| `runs/v22_C_catred_3012` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.863728e-05 | 1.230789e-05 | 5.094516e-05 | 0.57417 | GF PASS; acc 0.573856; MC not run |
| `runs/v22_C_catred_3021` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.863728e-05 | 1.230973e-05 | 5.094701e-05 | 0.57417 | GF PASS; acc 0.573824; MC not run |
| `runs/v22_C_catred_3102` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.855739e-05 | 1.230891e-05 | 5.08663e-05 | 0.57321 | GF PASS; acc 0.573026; MC not run |
| `runs/v22_C_catred_3120` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.87347e-05 | 1.251955e-05 | 5.125425e-05 | 0.57249 | GF PASS; acc 0.571857; MC not run |
| `runs/v22_C_catred_3201` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.877008e-05 | 1.25702e-05 | 5.134028e-05 | 0.57135 | GF PASS; acc 0.571696; MC not run |
| `runs/v22_C_catred_3210` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.872581e-05 | 1.250651e-05 | 5.123232e-05 | 0.57364 | GF PASS; acc 0.573341; MC not run |
| `runs/v22_C_direct_012` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.955615e-05 | 1.496472e-05 | 5.452087e-05 | 0.58295 | GF PASS; acc 0.582531; MC not run |
| `runs/v22_C_direct_021` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.988884e-05 | 1.51845e-05 | 5.507333e-05 | 0.58063 | GF PASS; acc 0.580306; MC not run |
| `runs/v22_C_direct_102` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.949627e-05 | 1.537204e-05 | 5.486831e-05 | 0.57947 | GF PASS; acc 0.579155; MC not run |
| `runs/v22_C_direct_120` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.954306e-05 | 1.498313e-05 | 5.452618e-05 | 0.58236 | GF PASS; acc 0.582098; MC not run |
| `runs/v22_C_direct_201` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.98048e-05 | 1.492206e-05 | 5.472686e-05 | 0.58236 | GF PASS; acc 0.582138; MC not run |
| `runs/v22_C_direct_210` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.977814e-05 | 1.492322e-05 | 5.470135e-05 | 0.58236 | GF PASS; acc 0.581526; MC not run |
| `runs/v22_C_flag_012` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.008671e-05 | 1.6245e-05 | 5.633171e-05 | 0.56325 | GF PASS; acc 0.562748; MC not run |
| `runs/v22_C_flag_021` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.045775e-05 | 1.653007e-05 | 5.698782e-05 | 0.56045 | GF PASS; acc 0.559846; MC not run |
| `runs/v22_C_flag_102` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.005028e-05 | 1.677637e-05 | 5.682665e-05 | 0.55879 | GF PASS; acc 0.558175; MC not run |
| `runs/v22_C_flag_120` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.005604e-05 | 1.626773e-05 | 5.632377e-05 | 0.56268 | GF PASS; acc 0.562554; MC not run |
| `runs/v22_C_flag_201` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.032618e-05 | 1.621285e-05 | 5.653903e-05 | 0.56268 | GF PASS; acc 0.562578; MC not run |
| `runs/v22_C_flag_210` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.02686e-05 | 1.621391e-05 | 5.648251e-05 | 0.56268 | GF PASS; acc 0.562762; MC not run |
| `runs/v22_C_hybrid1_012` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.966158e-05 | 1.508685e-05 | 5.474843e-05 | 0.57897 | GF PASS; acc 0.578570; MC not run |
| `runs/v22_C_hybrid1_021` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.981684e-05 | 1.503154e-05 | 5.484837e-05 | 0.57897 | GF PASS; acc 0.578488; MC not run |
| `runs/v22_C_hybrid1_102` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.966158e-05 | 1.508685e-05 | 5.474843e-05 | 0.57897 | GF PASS; acc 0.578570; MC not run |
| `runs/v22_C_hybrid1_120` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.966158e-05 | 1.508685e-05 | 5.474843e-05 | 0.57897 | GF PASS; acc 0.578570; MC not run |
| `runs/v22_C_hybrid1_201` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.981684e-05 | 1.503154e-05 | 5.484837e-05 | 0.57897 | GF PASS; acc 0.578488; MC not run |
| `runs/v22_C_hybrid1_210` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.981684e-05 | 1.503154e-05 | 5.484837e-05 | 0.57897 | GF PASS; acc 0.578488; MC not run |
| `runs/v22_C_hybrid2_012` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.465977e-05 | 5.393628e-05 | 0.58218 | GF PASS; acc 0.582498; MC not run |
| `runs/v22_C_hybrid2_021` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.465977e-05 | 5.393628e-05 | 0.58218 | GF PASS; acc 0.582498; MC not run |
| `runs/v22_C_hybrid2_102` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.465977e-05 | 5.393628e-05 | 0.58218 | GF PASS; acc 0.582498; MC not run |
| `runs/v22_C_hybrid2_120` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.465977e-05 | 5.393628e-05 | 0.58218 | GF PASS; acc 0.582498; MC not run |
| `runs/v22_C_hybrid2_201` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.465977e-05 | 5.393628e-05 | 0.58218 | GF PASS; acc 0.582498; MC not run |
| `runs/v22_C_hybrid2_210` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.927651e-05 | 1.465977e-05 | 5.393628e-05 | 0.58218 | GF PASS; acc 0.582498; MC not run |
| `runs/v22_C_hybrid2t_012` (regenerate) | C hybrid2t | 123 | 45 | 2.923587e-19 | 3.947918e-05 | 1.495394e-05 | 5.443312e-05 | 0.57987 | GF PASS; acc 0.579107; MC not run |
| `runs/v22_C_redundant_012` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.852581e-05 | 1.287942e-05 | 5.140523e-05 | 0.57664 | GF PASS; acc 0.576506; MC not run |
| `runs/v22_C_redundant_0132` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.868842e-05 | 1.329594e-05 | 5.198437e-05 | 0.57318 | GF PASS; acc 0.572895; MC not run |
| `runs/v22_C_redundant_021` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.852498e-05 | 1.287056e-05 | 5.139555e-05 | 0.57435 | GF PASS; acc 0.573817; MC not run |
| `runs/v22_C_redundant_0231` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.859118e-05 | 1.302233e-05 | 5.16135e-05 | 0.57374 | GF PASS; acc 0.573211; MC not run |
| `runs/v22_C_redundant_0312` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.872398e-05 | 1.317758e-05 | 5.190156e-05 | 0.57543 | GF PASS; acc 0.575549; MC not run |
| `runs/v22_C_redundant_0321` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.881129e-05 | 1.322889e-05 | 5.204018e-05 | 0.57258 | GF PASS; acc 0.571782; MC not run |
| `runs/v22_C_redundant_102` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.855165e-05 | 1.295281e-05 | 5.150446e-05 | 0.57321 | GF PASS; acc 0.572866; MC not run |
| `runs/v22_C_redundant_1032` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.869287e-05 | 1.329574e-05 | 5.198861e-05 | 0.57318 | GF PASS; acc 0.573269; MC not run |
| `runs/v22_C_redundant_120` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.865221e-05 | 1.281516e-05 | 5.146737e-05 | 0.57606 | GF PASS; acc 0.575945; MC not run |
| `runs/v22_C_redundant_1230` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.869654e-05 | 1.282126e-05 | 5.151779e-05 | 0.57606 | GF PASS; acc 0.574769; MC not run |
| `runs/v22_C_redundant_1302` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.86496e-05 | 1.323216e-05 | 5.188177e-05 | 0.57489 | GF PASS; acc 0.574307; MC not run |
| `runs/v22_C_redundant_1320` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.867334e-05 | 1.309988e-05 | 5.177322e-05 | 0.57260 | GF PASS; acc 0.571166; MC not run |
| `runs/v22_C_redundant_201` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.852803e-05 | 1.281357e-05 | 5.13416e-05 | 0.57606 | GF PASS; acc 0.574845; MC not run |
| `runs/v22_C_redundant_2031` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.859423e-05 | 1.296634e-05 | 5.156057e-05 | 0.57431 | GF PASS; acc 0.573360; MC not run |
| `runs/v22_C_redundant_210` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.865221e-05 | 1.281552e-05 | 5.146773e-05 | 0.57607 | GF PASS; acc 0.575086; MC not run |
| `runs/v22_C_redundant_2130` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.869654e-05 | 1.282177e-05 | 5.15183e-05 | 0.57606 | GF PASS; acc 0.575179; MC not run |
| `runs/v22_C_redundant_2301` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.86299e-05 | 1.28987e-05 | 5.15286e-05 | 0.57660 | GF PASS; acc 0.575415; MC not run |
| `runs/v22_C_redundant_2310` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.865663e-05 | 1.290287e-05 | 5.15595e-05 | 0.57488 | GF PASS; acc 0.573513; MC not run |
| `runs/v22_C_redundant_3012` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.868072e-05 | 1.310278e-05 | 5.178349e-05 | 0.57830 | GF PASS; acc 0.577505; MC not run |
| `runs/v22_C_redundant_3021` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.876819e-05 | 1.316197e-05 | 5.193016e-05 | 0.57428 | GF PASS; acc 0.574367; MC not run |
| `runs/v22_C_redundant_3102` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.867007e-05 | 1.330928e-05 | 5.197935e-05 | 0.57258 | GF PASS; acc 0.572353; MC not run |
| `runs/v22_C_redundant_3120` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.867334e-05 | 1.30372e-05 | 5.171054e-05 | 0.57543 | GF PASS; acc 0.574098; MC not run |
| `runs/v22_C_redundant_3201` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.872539e-05 | 1.302143e-05 | 5.174682e-05 | 0.57314 | GF PASS; acc 0.572863; MC not run |
| `runs/v22_C_redundant_3210` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.875212e-05 | 1.302183e-05 | 5.177395e-05 | 0.57314 | GF PASS; acc 0.572495; MC not run |
| `runs/v22_C_seq_012` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 4.069542e-05 | 1.795854e-05 | 5.865395e-05 | 0.55586 | GF PASS; acc 0.555423; MC not run |
| `runs/v22_C_seq_021` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 4.120328e-05 | 1.773113e-05 | 5.893441e-05 | 0.55586 | GF PASS; acc 0.555257; MC not run |
| `runs/v22_C_seq_102` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 3.967665e-05 | 1.795267e-05 | 5.762932e-05 | 0.55586 | GF PASS; acc 0.555830; MC not run |
| `runs/v22_C_seq_120` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 4.055283e-05 | 1.780212e-05 | 5.835496e-05 | 0.55531 | GF PASS; acc 0.555195; MC not run |
| `runs/v22_C_seq_201` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 4.129608e-05 | 1.753919e-05 | 5.883527e-05 | 0.55531 | GF PASS; acc 0.555186; MC not run |
| `runs/v22_C_seq_210` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 4.157979e-05 | 1.754284e-05 | 5.912263e-05 | 0.55531 | GF PASS; acc 0.554980; MC not run |
| [runs/v22_ref](runs/v22_ref.qasm) · [JSON](runs/v22_ref.json) · [receipt](runs/v22_ref.result.json) |  direct | 123 | 45 | 2.923587e-19 | 3.858427e-05 | 1.240382e-05 | 5.098808e-05 | 0.60239 | GF PASS; acc 0.601428; MC mean 5.215695e-05 |
| `runs/v22h_ABC_cat_012` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.0001623385 | 2.716256e-05 | 0.0001895011 | 0.54626 | GF PASS; acc 0.545891; MC not run |
| `runs/v22h_ABC_cat_021` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.0001577327 | 2.699385e-05 | 0.0001847266 | 0.54626 | GF PASS; acc 0.545900; MC not run |
| `runs/v22h_ABC_cat_102` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.0001551295 | 2.712835e-05 | 0.0001822579 | 0.54626 | GF PASS; acc 0.545704; MC not run |
| `runs/v22h_ABC_cat_120` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.0001409606 | 2.847896e-05 | 0.0001694396 | 0.54095 | GF PASS; acc 0.541220; MC not run |
| `runs/v22h_ABC_cat_201` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.0001364025 | 2.936001e-05 | 0.0001657625 | 0.53826 | GF PASS; acc 0.539272; MC not run |
| `runs/v22h_ABC_cat_210` (regenerate) | ABC cat | 141 | 45 | 2.923587e-19 | 0.0001218603 | 2.740669e-05 | 0.000149267 | 0.54420 | GF PASS; acc 0.544561; MC not run |
| `runs/v22h_ABC_direct_012` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 4.781192e-05 | 2.696189e-05 | 7.477381e-05 | 0.54666 | GF PASS; acc 0.546147; MC not run |
| `runs/v22h_ABC_direct_021` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 4.782054e-05 | 2.887846e-05 | 7.6699e-05 | 0.54015 | GF PASS; acc 0.540283; MC not run |
| `runs/v22h_ABC_direct_102` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 5.725546e-05 | 3.011322e-05 | 8.736868e-05 | 0.53694 | GF PASS; acc 0.536686; MC not run |
| `runs/v22h_ABC_direct_120` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 4.619731e-05 | 2.733063e-05 | 7.352793e-05 | 0.54502 | GF PASS; acc 0.545070; MC not run |
| `runs/v22h_ABC_direct_201` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 4.522312e-05 | 2.713113e-05 | 7.235425e-05 | 0.54502 | GF PASS; acc 0.545083; MC not run |
| `runs/v22h_ABC_direct_210` (regenerate) | ABC direct | 132 | 45 | 2.923587e-19 | 4.505127e-05 | 2.712437e-05 | 7.217564e-05 | 0.54502 | GF PASS; acc 0.544599; MC not run |
| `runs/v22h_ABC_flag_012` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.406999e-05 | 3.181438e-05 | 6.588437e-05 | 0.49308 | GF FAIL; acc 0.493295; MC not run |
| `runs/v22h_ABC_flag_021` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.376198e-05 | 3.383563e-05 | 6.759762e-05 | 0.48577 | GF FAIL; acc 0.486002; MC not run |
| `runs/v22h_ABC_flag_102` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.48977e-05 | 3.511626e-05 | 7.001396e-05 | 0.48144 | GF FAIL; acc 0.482003; MC not run |
| `runs/v22h_ABC_flag_120` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.455159e-05 | 3.231385e-05 | 6.686544e-05 | 0.49159 | GF FAIL; acc 0.491834; MC not run |
| `runs/v22h_ABC_flag_201` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.367808e-05 | 3.214203e-05 | 6.582011e-05 | 0.49159 | GF FAIL; acc 0.491836; MC not run |
| `runs/v22h_ABC_flag_210` (regenerate) | ABC flag | 150 | 45 | 2.923587e-19 | 3.4007e-05 | 3.215386e-05 | 6.616085e-05 | 0.49159 | GF FAIL; acc 0.492078; MC not run |
| `runs/v22h_ABC_flag_redundant_012` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.41811e-05 | 2.228801e-05 | 5.646911e-05 | 0.51682 | GF PASS; acc 0.517432; MC not run |
| `runs/v22h_ABC_flag_redundant_021` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.387309e-05 | 2.307388e-05 | 5.694698e-05 | 0.51017 | GF PASS; acc 0.510573; MC not run |
| `runs/v22h_ABC_flag_redundant_102` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.520659e-05 | 2.385332e-05 | 5.90599e-05 | 0.50663 | GF PASS; acc 0.506548; MC not run |
| `runs/v22h_ABC_flag_redundant_120` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.468937e-05 | 2.233667e-05 | 5.702604e-05 | 0.51527 | GF PASS; acc 0.515158; MC not run |
| `runs/v22h_ABC_flag_redundant_201` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.379808e-05 | 2.223288e-05 | 5.603095e-05 | 0.51527 | GF PASS; acc 0.515316; MC not run |
| `runs/v22h_ABC_flag_redundant_210` (regenerate) | ABC flag,redundant,redundant | 146 | 45 | 2.923587e-19 | 3.414477e-05 | 2.226712e-05 | 5.641189e-05 | 0.51527 | GF PASS; acc 0.515026; MC not run |
| `runs/v22h_ABC_hybrid1_012` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.609996e-05 | 3.030464e-05 | 7.64046e-05 | 0.53554 | GF PASS; acc 0.536171; MC not run |
| `runs/v22h_ABC_hybrid1_021` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.572584e-05 | 3.012421e-05 | 7.585005e-05 | 0.53554 | GF PASS; acc 0.536905; MC not run |
| `runs/v22h_ABC_hybrid1_102` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.609996e-05 | 3.030464e-05 | 7.64046e-05 | 0.53554 | GF PASS; acc 0.536171; MC not run |
| `runs/v22h_ABC_hybrid1_120` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.609996e-05 | 3.030464e-05 | 7.64046e-05 | 0.53554 | GF PASS; acc 0.536171; MC not run |
| `runs/v22h_ABC_hybrid1_201` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.572584e-05 | 3.012421e-05 | 7.585005e-05 | 0.53554 | GF PASS; acc 0.536905; MC not run |
| `runs/v22h_ABC_hybrid1_210` (regenerate) | ABC hybrid1 | 129 | 45 | 2.923587e-19 | 4.572584e-05 | 3.012421e-05 | 7.585005e-05 | 0.53554 | GF PASS; acc 0.536905; MC not run |
| `runs/v22h_ABC_hybrid2_012` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.238155e-05 | 2.665994e-05 | 6.904149e-05 | 0.54450 | GF PASS; acc 0.544683; MC not run |
| `runs/v22h_ABC_hybrid2_021` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.238155e-05 | 2.665994e-05 | 6.904149e-05 | 0.54450 | GF PASS; acc 0.544683; MC not run |
| `runs/v22h_ABC_hybrid2_102` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.238155e-05 | 2.665994e-05 | 6.904149e-05 | 0.54450 | GF PASS; acc 0.544683; MC not run |
| `runs/v22h_ABC_hybrid2_120` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.238155e-05 | 2.665994e-05 | 6.904149e-05 | 0.54450 | GF PASS; acc 0.544683; MC not run |
| `runs/v22h_ABC_hybrid2_201` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.238155e-05 | 2.665994e-05 | 6.904149e-05 | 0.54450 | GF PASS; acc 0.544683; MC not run |
| `runs/v22h_ABC_hybrid2_210` (regenerate) | ABC hybrid2 | 126 | 45 | 2.923587e-19 | 4.238155e-05 | 2.665994e-05 | 6.904149e-05 | 0.54450 | GF PASS; acc 0.544683; MC not run |
| `runs/v22h_ABC_hybrid2t_012` (regenerate) | ABC hybrid2t | 123 | 45 | 2.923587e-19 | 6.2168e-05 | 2.871404e-05 | 9.088204e-05 | 0.53805 | GF PASS; acc 0.537673; MC not run |
| `runs/v22h_ABC_redundant_012` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.126401e-05 | 1.957106e-05 | 6.083507e-05 | 0.52911 | GF PASS; acc 0.529250; MC not run |
| `runs/v22h_ABC_redundant_0132` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.40217e-05 | 2.244358e-05 | 6.646528e-05 | 0.51963 | GF PASS; acc 0.519538; MC not run |
| `runs/v22h_ABC_redundant_021` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.122193e-05 | 2.016387e-05 | 6.13858e-05 | 0.52281 | GF PASS; acc 0.523255; MC not run |
| `runs/v22h_ABC_redundant_0231` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.566252e-05 | 2.092605e-05 | 6.658857e-05 | 0.52116 | GF PASS; acc 0.520720; MC not run |
| `runs/v22h_ABC_redundant_0312` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.409425e-05 | 2.119993e-05 | 6.529418e-05 | 0.52577 | GF PASS; acc 0.525412; MC not run |
| `runs/v22h_ABC_redundant_0321` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.417061e-05 | 2.23077e-05 | 6.647831e-05 | 0.51797 | GF PASS; acc 0.517751; MC not run |
| `runs/v22h_ABC_redundant_102` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.661784e-05 | 2.085058e-05 | 6.746843e-05 | 0.51970 | GF PASS; acc 0.519039; MC not run |
| `runs/v22h_ABC_redundant_1032` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.433608e-05 | 2.243093e-05 | 6.676701e-05 | 0.51963 | GF PASS; acc 0.519537; MC not run |
| `runs/v22h_ABC_redundant_120` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.126735e-05 | 1.939602e-05 | 6.066336e-05 | 0.52752 | GF PASS; acc 0.527472; MC not run |
| `runs/v22h_ABC_redundant_1230` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.138877e-05 | 1.93983e-05 | 6.078707e-05 | 0.52752 | GF PASS; acc 0.526614; MC not run |
| `runs/v22h_ABC_redundant_1302` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.365873e-05 | 2.160788e-05 | 6.52666e-05 | 0.52431 | GF PASS; acc 0.524830; MC not run |
| `runs/v22h_ABC_redundant_1320` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.339776e-05 | 2.167202e-05 | 6.506978e-05 | 0.51805 | GF PASS; acc 0.517472; MC not run |
| `runs/v22h_ABC_redundant_201` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.099689e-05 | 1.934636e-05 | 6.034324e-05 | 0.52752 | GF PASS; acc 0.527533; MC not run |
| `runs/v22h_ABC_redundant_2031` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.557031e-05 | 2.043524e-05 | 6.600555e-05 | 0.52271 | GF PASS; acc 0.522824; MC not run |
| `runs/v22h_ABC_redundant_210` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.111641e-05 | 1.934922e-05 | 6.046563e-05 | 0.52753 | GF PASS; acc 0.527280; MC not run |
| `runs/v22h_ABC_redundant_2130` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.123784e-05 | 1.935096e-05 | 6.05888e-05 | 0.52752 | GF PASS; acc 0.526806; MC not run |
| `runs/v22h_ABC_redundant_2301` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.191757e-05 | 1.951817e-05 | 6.143575e-05 | 0.52901 | GF PASS; acc 0.528225; MC not run |
| `runs/v22h_ABC_redundant_2310` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.511636e-05 | 1.99455e-05 | 6.506186e-05 | 0.52427 | GF PASS; acc 0.523136; MC not run |
| `runs/v22h_ABC_redundant_3012` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.347385e-05 | 2.007418e-05 | 6.354803e-05 | 0.53370 | GF PASS; acc 0.533069; MC not run |
| `runs/v22h_ABC_redundant_3021` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.348436e-05 | 2.147112e-05 | 6.495548e-05 | 0.52263 | GF PASS; acc 0.522386; MC not run |
| `runs/v22h_ABC_redundant_3102` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 5.758972e-05 | 2.259029e-05 | 8.018e-05 | 0.51797 | GF PASS; acc 0.517530; MC not run |
| `runs/v22h_ABC_redundant_3120` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.350126e-05 | 2.054278e-05 | 6.404404e-05 | 0.52576 | GF PASS; acc 0.525048; MC not run |
| `runs/v22h_ABC_redundant_3201` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.307307e-05 | 2.113422e-05 | 6.42073e-05 | 0.51950 | GF PASS; acc 0.519776; MC not run |
| `runs/v22h_ABC_redundant_3210` (regenerate) | ABC redundant | 144 | 45 | 2.923587e-19 | 4.321773e-05 | 2.113161e-05 | 6.434934e-05 | 0.51951 | GF PASS; acc 0.519077; MC not run |
| `runs/v22h_ABC_seq_012` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 5.832583e-05 | 5.846755e-05 | 0.0001167934 | 0.47387 | GF FAIL; acc 0.473887; MC not run |
| `runs/v22h_ABC_seq_021` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 5.443941e-05 | 5.747257e-05 | 0.000111912 | 0.47388 | GF FAIL; acc 0.474573; MC not run |
| `runs/v22h_ABC_seq_102` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 5.860334e-05 | 5.884279e-05 | 0.0001174461 | 0.47388 | GF FAIL; acc 0.473791; MC not run |
| `runs/v22h_ABC_seq_120` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 5.279196e-05 | 5.884373e-05 | 0.0001116357 | 0.47246 | GF FAIL; acc 0.472768; MC not run |
| `runs/v22h_ABC_seq_201` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 4.838997e-05 | 5.702308e-05 | 0.0001054131 | 0.47246 | GF FAIL; acc 0.472462; MC not run |
| `runs/v22h_ABC_seq_210` (regenerate) | ABC seq | 132 | 45 | 2.923587e-19 | 4.751045e-05 | 5.703175e-05 | 0.0001045422 | 0.47247 | GF FAIL; acc 0.472581; MC not run |
| `runs/v22h_AB_cat_012` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001239349 | 2.297854e-05 | 0.0001469134 | 0.56462 | GF PASS; acc 0.564212; MC not run |
| `runs/v22h_AB_cat_021` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001214602 | 2.286626e-05 | 0.0001443265 | 0.56462 | GF PASS; acc 0.564232; MC not run |
| `runs/v22h_AB_cat_102` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001204374 | 2.295232e-05 | 0.0001433897 | 0.56462 | GF PASS; acc 0.564253; MC not run |
| `runs/v22h_AB_cat_120` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001131699 | 2.384668e-05 | 0.0001370166 | 0.56095 | GF PASS; acc 0.560545; MC not run |
| `runs/v22h_AB_cat_201` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001093387 | 2.442065e-05 | 0.0001337593 | 0.55909 | GF PASS; acc 0.558938; MC not run |
| `runs/v22h_AB_cat_210` (regenerate) | AB cat | 135 | 45 | 2.923587e-19 | 0.0001006036 | 2.312173e-05 | 0.0001237253 | 0.56320 | GF PASS; acc 0.563471; MC not run |
| `runs/v22h_AB_direct_012` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 4.513562e-05 | 2.319618e-05 | 6.83318e-05 | 0.56489 | GF PASS; acc 0.565464; MC not run |
| `runs/v22h_AB_direct_021` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 4.500702e-05 | 2.458054e-05 | 6.958757e-05 | 0.56040 | GF PASS; acc 0.559592; MC not run |
| `runs/v22h_AB_direct_102` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 5.262905e-05 | 2.547605e-05 | 7.810509e-05 | 0.55818 | GF PASS; acc 0.557412; MC not run |
| `runs/v22h_AB_direct_120` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 4.4284e-05 | 2.34816e-05 | 6.77656e-05 | 0.56376 | GF PASS; acc 0.563584; MC not run |
| `runs/v22h_AB_direct_201` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 4.324765e-05 | 2.33273e-05 | 6.657496e-05 | 0.56376 | GF PASS; acc 0.563635; MC not run |
| `runs/v22h_AB_direct_210` (regenerate) | AB direct | 129 | 45 | 2.923587e-19 | 4.33731e-05 | 2.333788e-05 | 6.671098e-05 | 0.56376 | GF PASS; acc 0.563105; MC not run |
| `runs/v22h_AB_flag_012` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.406999e-05 | 2.62146e-05 | 6.028459e-05 | 0.52735 | GF PASS; acc 0.528018; MC not run |
| `runs/v22h_AB_flag_021` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.376198e-05 | 2.759208e-05 | 6.135407e-05 | 0.52213 | GF PASS; acc 0.522239; MC not run |
| `runs/v22h_AB_flag_102` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.48977e-05 | 2.848159e-05 | 6.337928e-05 | 0.51903 | GF PASS; acc 0.518996; MC not run |
| `runs/v22h_AB_flag_120` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.455159e-05 | 2.657847e-05 | 6.113006e-05 | 0.52629 | GF PASS; acc 0.526097; MC not run |
| `runs/v22h_AB_flag_201` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.367808e-05 | 2.644353e-05 | 6.012161e-05 | 0.52629 | GF PASS; acc 0.526116; MC not run |
| `runs/v22h_AB_flag_210` (regenerate) | AB flag | 141 | 45 | 2.923587e-19 | 3.4007e-05 | 2.646656e-05 | 6.047355e-05 | 0.52629 | GF PASS; acc 0.526033; MC not run |
| `runs/v22h_AB_hybrid1_012` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.414363e-05 | 2.583275e-05 | 6.997638e-05 | 0.55721 | GF PASS; acc 0.556806; MC not run |
| `runs/v22h_AB_hybrid1_021` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.37741e-05 | 2.572633e-05 | 6.950042e-05 | 0.55721 | GF PASS; acc 0.556244; MC not run |
| `runs/v22h_AB_hybrid1_102` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.414363e-05 | 2.583275e-05 | 6.997638e-05 | 0.55721 | GF PASS; acc 0.556806; MC not run |
| `runs/v22h_AB_hybrid1_120` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.414363e-05 | 2.583275e-05 | 6.997638e-05 | 0.55721 | GF PASS; acc 0.556806; MC not run |
| `runs/v22h_AB_hybrid1_201` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.37741e-05 | 2.572633e-05 | 6.950042e-05 | 0.55721 | GF PASS; acc 0.556244; MC not run |
| `runs/v22h_AB_hybrid1_210` (regenerate) | AB hybrid1 | 127 | 45 | 2.923587e-19 | 4.37741e-05 | 2.572633e-05 | 6.950042e-05 | 0.55721 | GF PASS; acc 0.556244; MC not run |
| `runs/v22h_AB_hybrid2_012` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.322709e-05 | 6.476103e-05 | 0.56340 | GF PASS; acc 0.563339; MC not run |
| `runs/v22h_AB_hybrid2_021` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.322709e-05 | 6.476103e-05 | 0.56340 | GF PASS; acc 0.563339; MC not run |
| `runs/v22h_AB_hybrid2_102` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.322709e-05 | 6.476103e-05 | 0.56340 | GF PASS; acc 0.563339; MC not run |
| `runs/v22h_AB_hybrid2_120` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.322709e-05 | 6.476103e-05 | 0.56340 | GF PASS; acc 0.563339; MC not run |
| `runs/v22h_AB_hybrid2_201` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.322709e-05 | 6.476103e-05 | 0.56340 | GF PASS; acc 0.563339; MC not run |
| `runs/v22h_AB_hybrid2_210` (regenerate) | AB hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.322709e-05 | 6.476103e-05 | 0.56340 | GF PASS; acc 0.563339; MC not run |
| `runs/v22h_AB_hybrid2t_012` (regenerate) | AB hybrid2t | 123 | 45 | 2.923587e-19 | 5.811315e-05 | 2.46739e-05 | 8.278705e-05 | 0.55895 | GF PASS; acc 0.558678; MC not run |
| `runs/v22h_AB_redundant_012` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.111918e-05 | 1.869805e-05 | 5.981723e-05 | 0.55274 | GF PASS; acc 0.552290; MC not run |
| `runs/v22h_AB_redundant_0132` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.316525e-05 | 2.083223e-05 | 6.399747e-05 | 0.54612 | GF PASS; acc 0.546057; MC not run |
| `runs/v22h_AB_redundant_021` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.115686e-05 | 1.925774e-05 | 6.04146e-05 | 0.54835 | GF PASS; acc 0.547437; MC not run |
| `runs/v22h_AB_redundant_0231` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.491727e-05 | 1.976489e-05 | 6.468216e-05 | 0.54719 | GF PASS; acc 0.547149; MC not run |
| `runs/v22h_AB_redundant_0312` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.325925e-05 | 1.984009e-05 | 6.309934e-05 | 0.55041 | GF PASS; acc 0.549929; MC not run |
| `runs/v22h_AB_redundant_0321` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.340248e-05 | 2.07586e-05 | 6.416108e-05 | 0.54496 | GF PASS; acc 0.544937; MC not run |
| `runs/v22h_AB_redundant_102` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.628539e-05 | 1.977985e-05 | 6.606524e-05 | 0.54617 | GF PASS; acc 0.545400; MC not run |
| `runs/v22h_AB_redundant_1032` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.345758e-05 | 2.081797e-05 | 6.427555e-05 | 0.54612 | GF PASS; acc 0.545666; MC not run |
| `runs/v22h_AB_redundant_120` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.11469e-05 | 1.862002e-05 | 5.976692e-05 | 0.55163 | GF PASS; acc 0.551065; MC not run |
| `runs/v22h_AB_redundant_1230` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.126832e-05 | 1.862218e-05 | 5.98905e-05 | 0.55163 | GF PASS; acc 0.551030; MC not run |
| `runs/v22h_AB_redundant_1302` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.29125e-05 | 2.016296e-05 | 6.307546e-05 | 0.54939 | GF PASS; acc 0.549027; MC not run |
| `runs/v22h_AB_redundant_1320` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.305607e-05 | 2.036454e-05 | 6.342061e-05 | 0.54501 | GF PASS; acc 0.545376; MC not run |
| `runs/v22h_AB_redundant_201` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.090746e-05 | 1.857203e-05 | 5.947949e-05 | 0.55163 | GF PASS; acc 0.551045; MC not run |
| `runs/v22h_AB_redundant_2031` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.47831e-05 | 1.937474e-05 | 6.415785e-05 | 0.54827 | GF PASS; acc 0.547841; MC not run |
| `runs/v22h_AB_redundant_210` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.099597e-05 | 1.8578e-05 | 5.957396e-05 | 0.55164 | GF PASS; acc 0.550470; MC not run |
| `runs/v22h_AB_redundant_2130` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.111739e-05 | 1.857955e-05 | 5.969694e-05 | 0.55163 | GF PASS; acc 0.550632; MC not run |
| `runs/v22h_AB_redundant_2301` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.160682e-05 | 1.862725e-05 | 6.023407e-05 | 0.55267 | GF PASS; acc 0.552649; MC not run |
| `runs/v22h_AB_redundant_2310` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.454558e-05 | 1.900749e-05 | 6.355306e-05 | 0.54936 | GF PASS; acc 0.548748; MC not run |
| `runs/v22h_AB_redundant_3012` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.274907e-05 | 1.890074e-05 | 6.164981e-05 | 0.55593 | GF PASS; acc 0.556085; MC not run |
| `runs/v22h_AB_redundant_3021` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.282631e-05 | 2.009684e-05 | 6.292315e-05 | 0.54822 | GF PASS; acc 0.547103; MC not run |
| `runs/v22h_AB_redundant_3102` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 5.503494e-05 | 2.08896e-05 | 7.592454e-05 | 0.54496 | GF PASS; acc 0.545021; MC not run |
| `runs/v22h_AB_redundant_3120` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.313708e-05 | 1.939949e-05 | 6.253657e-05 | 0.55041 | GF PASS; acc 0.550184; MC not run |
| `runs/v22h_AB_redundant_3201` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.270463e-05 | 1.992884e-05 | 6.263347e-05 | 0.54603 | GF PASS; acc 0.546295; MC not run |
| `runs/v22h_AB_redundant_3210` (regenerate) | AB redundant | 137 | 45 | 2.923587e-19 | 4.293325e-05 | 1.993316e-05 | 6.286642e-05 | 0.54603 | GF PASS; acc 0.545602; MC not run |
| `runs/v22h_AB_seq_012` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 5.207959e-05 | 4.555742e-05 | 9.763701e-05 | 0.51358 | GF PASS; acc 0.513441; MC not run |
| `runs/v22h_AB_seq_021` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 4.920605e-05 | 4.481086e-05 | 9.401691e-05 | 0.51358 | GF PASS; acc 0.513614; MC not run |
| `runs/v22h_AB_seq_102` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 5.34074e-05 | 4.584937e-05 | 9.925677e-05 | 0.51358 | GF PASS; acc 0.513033; MC not run |
| `runs/v22h_AB_seq_120` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 4.973358e-05 | 4.589005e-05 | 9.562363e-05 | 0.51256 | GF PASS; acc 0.512632; MC not run |
| `runs/v22h_AB_seq_201` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 4.535581e-05 | 4.449315e-05 | 8.984896e-05 | 0.51256 | GF PASS; acc 0.512851; MC not run |
| `runs/v22h_AB_seq_210` (regenerate) | AB seq | 129 | 45 | 2.923587e-19 | 4.547939e-05 | 4.462295e-05 | 9.010234e-05 | 0.51257 | GF PASS; acc 0.512990; MC not run |
| `runs/v22h_AC_cat_012` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001239349 | 2.292814e-05 | 0.000146863 | 0.56462 | GF PASS; acc 0.564508; MC not run |
| `runs/v22h_AC_cat_021` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001214602 | 2.281578e-05 | 0.000144276 | 0.56462 | GF PASS; acc 0.564518; MC not run |
| `runs/v22h_AC_cat_102` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001204374 | 2.290184e-05 | 0.0001433392 | 0.56462 | GF PASS; acc 0.564180; MC not run |
| `runs/v22h_AC_cat_120` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001131699 | 2.379441e-05 | 0.0001369643 | 0.56095 | GF PASS; acc 0.560736; MC not run |
| `runs/v22h_AC_cat_201` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001093387 | 2.436797e-05 | 0.0001337067 | 0.55909 | GF PASS; acc 0.558249; MC not run |
| `runs/v22h_AC_cat_210` (regenerate) | AC cat | 135 | 45 | 2.923587e-19 | 0.0001006036 | 2.307336e-05 | 0.0001236769 | 0.56320 | GF PASS; acc 0.563098; MC not run |
| `runs/v22h_AC_direct_012` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 4.513562e-05 | 2.31594e-05 | 6.829501e-05 | 0.56489 | GF PASS; acc 0.565372; MC not run |
| `runs/v22h_AC_direct_021` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 4.500702e-05 | 2.453914e-05 | 6.954617e-05 | 0.56040 | GF PASS; acc 0.559763; MC not run |
| `runs/v22h_AC_direct_102` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 5.262905e-05 | 2.543168e-05 | 7.806073e-05 | 0.55818 | GF PASS; acc 0.558089; MC not run |
| `runs/v22h_AC_direct_120` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 4.4284e-05 | 2.344352e-05 | 6.772752e-05 | 0.56376 | GF PASS; acc 0.563352; MC not run |
| `runs/v22h_AC_direct_201` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 4.324765e-05 | 2.328913e-05 | 6.653678e-05 | 0.56376 | GF PASS; acc 0.563334; MC not run |
| `runs/v22h_AC_direct_210` (regenerate) | AC direct | 129 | 45 | 2.923587e-19 | 4.33731e-05 | 2.329974e-05 | 6.667285e-05 | 0.56376 | GF PASS; acc 0.563436; MC not run |
| `runs/v22h_AC_flag_012` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.406999e-05 | 2.617815e-05 | 6.024814e-05 | 0.52735 | GF PASS; acc 0.527345; MC not run |
| `runs/v22h_AC_flag_021` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.376198e-05 | 2.75522e-05 | 6.131419e-05 | 0.52213 | GF PASS; acc 0.521879; MC not run |
| `runs/v22h_AC_flag_102` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.48977e-05 | 2.844065e-05 | 6.333834e-05 | 0.51903 | GF PASS; acc 0.518600; MC not run |
| `runs/v22h_AC_flag_120` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.455159e-05 | 2.654072e-05 | 6.109231e-05 | 0.52629 | GF PASS; acc 0.525905; MC not run |
| `runs/v22h_AC_flag_201` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.367808e-05 | 2.640573e-05 | 6.00838e-05 | 0.52629 | GF PASS; acc 0.525978; MC not run |
| `runs/v22h_AC_flag_210` (regenerate) | AC flag | 141 | 45 | 2.923587e-19 | 3.4007e-05 | 2.642878e-05 | 6.043577e-05 | 0.52629 | GF PASS; acc 0.526261; MC not run |
| `runs/v22h_AC_hybrid1_012` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.414363e-05 | 2.578321e-05 | 6.992684e-05 | 0.55721 | GF PASS; acc 0.556871; MC not run |
| `runs/v22h_AC_hybrid1_021` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.37741e-05 | 2.567677e-05 | 6.945087e-05 | 0.55721 | GF PASS; acc 0.557436; MC not run |
| `runs/v22h_AC_hybrid1_102` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.414363e-05 | 2.578321e-05 | 6.992684e-05 | 0.55721 | GF PASS; acc 0.556871; MC not run |
| `runs/v22h_AC_hybrid1_120` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.414363e-05 | 2.578321e-05 | 6.992684e-05 | 0.55721 | GF PASS; acc 0.556871; MC not run |
| `runs/v22h_AC_hybrid1_201` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.37741e-05 | 2.567677e-05 | 6.945087e-05 | 0.55721 | GF PASS; acc 0.557436; MC not run |
| `runs/v22h_AC_hybrid1_210` (regenerate) | AC hybrid1 | 127 | 45 | 2.923587e-19 | 4.37741e-05 | 2.567677e-05 | 6.945087e-05 | 0.55721 | GF PASS; acc 0.557436; MC not run |
| `runs/v22h_AC_hybrid2_012` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.318874e-05 | 6.472268e-05 | 0.56340 | GF PASS; acc 0.563366; MC not run |
| `runs/v22h_AC_hybrid2_021` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.318874e-05 | 6.472268e-05 | 0.56340 | GF PASS; acc 0.563366; MC not run |
| `runs/v22h_AC_hybrid2_102` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.318874e-05 | 6.472268e-05 | 0.56340 | GF PASS; acc 0.563366; MC not run |
| `runs/v22h_AC_hybrid2_120` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.318874e-05 | 6.472268e-05 | 0.56340 | GF PASS; acc 0.563366; MC not run |
| `runs/v22h_AC_hybrid2_201` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.318874e-05 | 6.472268e-05 | 0.56340 | GF PASS; acc 0.563366; MC not run |
| `runs/v22h_AC_hybrid2_210` (regenerate) | AC hybrid2 | 125 | 45 | 2.923587e-19 | 4.153394e-05 | 2.318874e-05 | 6.472268e-05 | 0.56340 | GF PASS; acc 0.563366; MC not run |
| `runs/v22h_AC_hybrid2t_012` (regenerate) | AC hybrid2t | 123 | 45 | 2.923587e-19 | 5.811315e-05 | 2.462858e-05 | 8.274173e-05 | 0.55895 | GF PASS; acc 0.558816; MC not run |
| `runs/v22h_AC_redundant_012` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.111918e-05 | 1.865576e-05 | 5.977494e-05 | 0.55274 | GF PASS; acc 0.552023; MC not run |
| `runs/v22h_AC_redundant_0132` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.316525e-05 | 2.078319e-05 | 6.394844e-05 | 0.54612 | GF PASS; acc 0.545710; MC not run |
| `runs/v22h_AC_redundant_021` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.115686e-05 | 1.921092e-05 | 6.036778e-05 | 0.54835 | GF PASS; acc 0.548103; MC not run |
| `runs/v22h_AC_redundant_0231` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.491727e-05 | 1.971642e-05 | 6.463369e-05 | 0.54719 | GF PASS; acc 0.546249; MC not run |
| `runs/v22h_AC_redundant_0312` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.325925e-05 | 1.979529e-05 | 6.305454e-05 | 0.55041 | GF PASS; acc 0.549751; MC not run |
| `runs/v22h_AC_redundant_0321` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.340248e-05 | 2.070818e-05 | 6.411065e-05 | 0.54496 | GF PASS; acc 0.544552; MC not run |
| `runs/v22h_AC_redundant_102` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.628539e-05 | 1.973014e-05 | 6.601553e-05 | 0.54617 | GF PASS; acc 0.545903; MC not run |
| `runs/v22h_AC_redundant_1032` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.345758e-05 | 2.076889e-05 | 6.422646e-05 | 0.54612 | GF PASS; acc 0.545935; MC not run |
| `runs/v22h_AC_redundant_120` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.11469e-05 | 1.857661e-05 | 5.972351e-05 | 0.55163 | GF PASS; acc 0.550923; MC not run |
| `runs/v22h_AC_redundant_1230` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.126832e-05 | 1.85788e-05 | 5.984712e-05 | 0.55163 | GF PASS; acc 0.551119; MC not run |
| `runs/v22h_AC_redundant_1302` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.29125e-05 | 2.011728e-05 | 6.302977e-05 | 0.54939 | GF PASS; acc 0.548699; MC not run |
| `runs/v22h_AC_redundant_1320` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.305607e-05 | 2.031427e-05 | 6.337033e-05 | 0.54501 | GF PASS; acc 0.544921; MC not run |
| `runs/v22h_AC_redundant_201` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.090746e-05 | 1.852854e-05 | 5.9436e-05 | 0.55163 | GF PASS; acc 0.552156; MC not run |
| `runs/v22h_AC_redundant_2031` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.47831e-05 | 1.932732e-05 | 6.411042e-05 | 0.54827 | GF PASS; acc 0.547729; MC not run |
| `runs/v22h_AC_redundant_210` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.099597e-05 | 1.853457e-05 | 5.953054e-05 | 0.55164 | GF PASS; acc 0.550835; MC not run |
| `runs/v22h_AC_redundant_2130` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.111739e-05 | 1.853615e-05 | 5.965354e-05 | 0.55163 | GF PASS; acc 0.551536; MC not run |
| `runs/v22h_AC_redundant_2301` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.160682e-05 | 1.858472e-05 | 6.019154e-05 | 0.55267 | GF PASS; acc 0.552081; MC not run |
| `runs/v22h_AC_redundant_2310` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.454558e-05 | 1.896119e-05 | 6.350676e-05 | 0.54936 | GF PASS; acc 0.549612; MC not run |
| `runs/v22h_AC_redundant_3012` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.274907e-05 | 1.886155e-05 | 6.161062e-05 | 0.55593 | GF PASS; acc 0.555090; MC not run |
| `runs/v22h_AC_redundant_3021` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.282631e-05 | 2.004979e-05 | 6.28761e-05 | 0.54822 | GF PASS; acc 0.548021; MC not run |
| `runs/v22h_AC_redundant_3102` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 5.503494e-05 | 2.083774e-05 | 7.587268e-05 | 0.54496 | GF PASS; acc 0.545063; MC not run |
| `runs/v22h_AC_redundant_3120` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.313708e-05 | 1.935456e-05 | 6.249163e-05 | 0.55041 | GF PASS; acc 0.550313; MC not run |
| `runs/v22h_AC_redundant_3201` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.270463e-05 | 1.987937e-05 | 6.258399e-05 | 0.54603 | GF PASS; acc 0.546033; MC not run |
| `runs/v22h_AC_redundant_3210` (regenerate) | AC redundant | 137 | 45 | 2.923587e-19 | 4.293325e-05 | 1.988369e-05 | 6.281695e-05 | 0.54603 | GF PASS; acc 0.545885; MC not run |
| `runs/v22h_AC_seq_012` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 5.207959e-05 | 4.546384e-05 | 9.754344e-05 | 0.51358 | GF PASS; acc 0.513760; MC not run |
| `runs/v22h_AC_seq_021` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 4.920605e-05 | 4.471707e-05 | 9.392312e-05 | 0.51358 | GF PASS; acc 0.512950; MC not run |
| `runs/v22h_AC_seq_102` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 5.34074e-05 | 4.575531e-05 | 9.916271e-05 | 0.51358 | GF PASS; acc 0.513134; MC not run |
| `runs/v22h_AC_seq_120` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 4.973358e-05 | 4.57947e-05 | 9.552829e-05 | 0.51256 | GF PASS; acc 0.513046; MC not run |
| `runs/v22h_AC_seq_201` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 4.535581e-05 | 4.439743e-05 | 8.975324e-05 | 0.51256 | GF PASS; acc 0.513754; MC not run |
| `runs/v22h_AC_seq_210` (regenerate) | AC seq | 129 | 45 | 2.923587e-19 | 4.547939e-05 | 4.45274e-05 | 9.000678e-05 | 0.51257 | GF PASS; acc 0.512529; MC not run |
| `runs/v22h_A_cat13_012` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.342482e-05 | 2.097289e-05 | 6.439771e-05 | 0.58058 | GF PASS; acc 0.580009; MC not run |
| `runs/v22h_A_cat13_021` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.31499e-05 | 2.189236e-05 | 6.504227e-05 | 0.57826 | GF PASS; acc 0.577735; MC not run |
| `runs/v22h_A_cat13_102` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.957079e-05 | 2.25074e-05 | 7.20782e-05 | 0.57711 | GF PASS; acc 0.576278; MC not run |
| `runs/v22h_A_cat13_120` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.334905e-05 | 2.119438e-05 | 6.454343e-05 | 0.57999 | GF PASS; acc 0.579563; MC not run |
| `runs/v22h_A_cat13_201` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.223199e-05 | 2.108835e-05 | 6.332034e-05 | 0.57999 | GF PASS; acc 0.579560; MC not run |
| `runs/v22h_A_cat13_210` (regenerate) | A cat13 | 129 | 45 | 2.923587e-19 | 4.26638e-05 | 2.1117e-05 | 6.37808e-05 | 0.57999 | GF PASS; acc 0.579037; MC not run |
| `runs/v22h_A_cat13red_012` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.242537e-05 | 1.954584e-05 | 6.197121e-05 | 0.56928 | GF PASS; acc 0.568670; MC not run |
| `runs/v22h_A_cat13red_0132` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.317555e-05 | 1.966647e-05 | 6.284202e-05 | 0.56849 | GF PASS; acc 0.567569; MC not run |
| `runs/v22h_A_cat13red_021` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.254228e-05 | 2.016325e-05 | 6.270553e-05 | 0.56702 | GF PASS; acc 0.566531; MC not run |
| `runs/v22h_A_cat13red_0231` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.300881e-05 | 2.034221e-05 | 6.335102e-05 | 0.56604 | GF PASS; acc 0.565690; MC not run |
| `runs/v22h_A_cat13red_0312` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.353758e-05 | 1.987171e-05 | 6.340929e-05 | 0.56769 | GF PASS; acc 0.566721; MC not run |
| `runs/v22h_A_cat13red_0321` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.34547e-05 | 1.98517e-05 | 6.33064e-05 | 0.56769 | GF PASS; acc 0.566785; MC not run |
| `runs/v22h_A_cat13red_102` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.856658e-05 | 2.057393e-05 | 6.914051e-05 | 0.56589 | GF PASS; acc 0.565541; MC not run |
| `runs/v22h_A_cat13red_1032` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.337605e-05 | 1.966944e-05 | 6.304549e-05 | 0.56848 | GF PASS; acc 0.568424; MC not run |
| `runs/v22h_A_cat13red_120` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.262088e-05 | 1.960844e-05 | 6.222932e-05 | 0.56871 | GF PASS; acc 0.568462; MC not run |
| `runs/v22h_A_cat13red_1230` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.274222e-05 | 1.962662e-05 | 6.236884e-05 | 0.56795 | GF PASS; acc 0.567532; MC not run |
| `runs/v22h_A_cat13red_1302` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.370814e-05 | 2.02018e-05 | 6.390994e-05 | 0.56641 | GF PASS; acc 0.566428; MC not run |
| `runs/v22h_A_cat13red_1320` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.360101e-05 | 1.971825e-05 | 6.331926e-05 | 0.56754 | GF PASS; acc 0.567507; MC not run |
| `runs/v22h_A_cat13red_201` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.234062e-05 | 1.955181e-05 | 6.189243e-05 | 0.56871 | GF PASS; acc 0.567476; MC not run |
| `runs/v22h_A_cat13red_2031` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.274949e-05 | 1.97182e-05 | 6.246769e-05 | 0.56772 | GF PASS; acc 0.567264; MC not run |
| `runs/v22h_A_cat13red_210` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.246986e-05 | 1.957546e-05 | 6.204532e-05 | 0.56871 | GF PASS; acc 0.567587; MC not run |
| `runs/v22h_A_cat13red_2130` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.25912e-05 | 1.959244e-05 | 6.218363e-05 | 0.56795 | GF PASS; acc 0.567288; MC not run |
| `runs/v22h_A_cat13red_2301` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.269162e-05 | 1.967987e-05 | 6.237148e-05 | 0.56735 | GF PASS; acc 0.567173; MC not run |
| `runs/v22h_A_cat13red_2310` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.283838e-05 | 1.968963e-05 | 6.252801e-05 | 0.56735 | GF PASS; acc 0.566066; MC not run |
| `runs/v22h_A_cat13red_3012` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.350167e-05 | 1.981262e-05 | 6.331429e-05 | 0.56769 | GF PASS; acc 0.566791; MC not run |
| `runs/v22h_A_cat13red_3021` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.366241e-05 | 2.047733e-05 | 6.413974e-05 | 0.56543 | GF PASS; acc 0.565024; MC not run |
| `runs/v22h_A_cat13red_3102` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.997068e-05 | 2.08737e-05 | 7.084439e-05 | 0.56430 | GF PASS; acc 0.564205; MC not run |
| `runs/v22h_A_cat13red_3120` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.372356e-05 | 1.990293e-05 | 6.362649e-05 | 0.56712 | GF PASS; acc 0.566288; MC not run |
| `runs/v22h_A_cat13red_3201` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.334833e-05 | 1.984316e-05 | 6.319149e-05 | 0.56712 | GF PASS; acc 0.566268; MC not run |
| `runs/v22h_A_cat13red_3210` (regenerate) | A cat13red | 134 | 45 | 2.923587e-19 | 4.349509e-05 | 1.985563e-05 | 6.335072e-05 | 0.56712 | GF PASS; acc 0.566754; MC not run |
| `runs/v22h_A_cat3_012` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.877527e-05 | 2.195763e-05 | 0.0001207329 | 0.57617 | GF PASS; acc 0.576385; MC not run |
| `runs/v22h_A_cat3_021` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.856134e-05 | 2.193835e-05 | 0.0001204997 | 0.57617 | GF PASS; acc 0.576381; MC not run |
| `runs/v22h_A_cat3_102` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.885626e-05 | 2.193391e-05 | 0.0001207902 | 0.57617 | GF PASS; acc 0.576406; MC not run |
| `runs/v22h_A_cat3_120` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.883515e-05 | 2.27808e-05 | 0.0001216159 | 0.57387 | GF PASS; acc 0.573268; MC not run |
| `runs/v22h_A_cat3_201` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.854245e-05 | 2.277386e-05 | 0.0001213163 | 0.57387 | GF PASS; acc 0.573255; MC not run |
| `runs/v22h_A_cat3_210` (regenerate) | A cat3 | 132 | 45 | 2.923587e-19 | 9.854592e-05 | 2.275362e-05 | 0.0001212995 | 0.57387 | GF PASS; acc 0.573263; MC not run |
| `runs/v22h_A_cat4_012` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.000114746 | 2.748923e-05 | 0.0001422353 | 0.56624 | GF PASS; acc 0.565383; MC not run |
| `runs/v22h_A_cat4_021` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001134078 | 2.733101e-05 | 0.0001407388 | 0.56624 | GF PASS; acc 0.565394; MC not run |
| `runs/v22h_A_cat4_102` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001148055 | 2.746678e-05 | 0.0001422723 | 0.56624 | GF PASS; acc 0.565424; MC not run |
| `runs/v22h_A_cat4_120` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001134657 | 2.729221e-05 | 0.0001407579 | 0.56624 | GF PASS; acc 0.566485; MC not run |
| `runs/v22h_A_cat4_201` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001120719 | 2.713009e-05 | 0.000139202 | 0.56624 | GF PASS; acc 0.566489; MC not run |
| `runs/v22h_A_cat4_210` (regenerate) | A cat4 | 135 | 45 | 2.923587e-19 | 0.0001120533 | 2.711335e-05 | 0.0001391667 | 0.56624 | GF PASS; acc 0.566491; MC not run |
| `runs/v22h_A_cat_012` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 9.327571e-05 | 1.899772e-05 | 0.0001122734 | 0.58359 | GF PASS; acc 0.583643; MC not run |
| `runs/v22h_A_cat_021` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 9.290105e-05 | 1.894183e-05 | 0.0001118429 | 0.58359 | GF PASS; acc 0.583637; MC not run |
| `runs/v22h_A_cat_102` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 9.348969e-05 | 1.898754e-05 | 0.0001124772 | 0.58359 | GF PASS; acc 0.582691; MC not run |
| `runs/v22h_A_cat_120` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 9.348371e-05 | 1.94989e-05 | 0.0001129826 | 0.58170 | GF PASS; acc 0.581438; MC not run |
| `runs/v22h_A_cat_201` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 8.905933e-05 | 1.979067e-05 | 0.00010885 | 0.58073 | GF PASS; acc 0.580591; MC not run |
| `runs/v22h_A_cat_210` (regenerate) | A cat | 129 | 45 | 2.923587e-19 | 8.490909e-05 | 1.904722e-05 | 0.0001039563 | 0.58286 | GF PASS; acc 0.583203; MC not run |
| `runs/v22h_A_catred_012` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001070721 | 1.632961e-05 | 0.0001234017 | 0.57568 | GF PASS; acc 0.575503; MC not run |
| `runs/v22h_A_catred_0132` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001089252 | 1.626156e-05 | 0.0001251868 | 0.57567 | GF PASS; acc 0.575270; MC not run |
| `runs/v22h_A_catred_021` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001070886 | 1.629899e-05 | 0.0001233876 | 0.57568 | GF PASS; acc 0.574805; MC not run |
| `runs/v22h_A_catred_0231` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.786008e-05 | 1.733344e-05 | 0.0001151935 | 0.57266 | GF PASS; acc 0.572261; MC not run |
| `runs/v22h_A_catred_0312` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.934134e-05 | 1.691996e-05 | 0.0001162613 | 0.57438 | GF PASS; acc 0.573275; MC not run |
| `runs/v22h_A_catred_0321` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.934134e-05 | 1.6908e-05 | 0.0001162493 | 0.57438 | GF PASS; acc 0.573280; MC not run |
| `runs/v22h_A_catred_102` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.000104995 | 1.654259e-05 | 0.0001215376 | 0.57510 | GF PASS; acc 0.574471; MC not run |
| `runs/v22h_A_catred_1032` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001069814 | 1.647116e-05 | 0.0001234526 | 0.57510 | GF PASS; acc 0.574963; MC not run |
| `runs/v22h_A_catred_120` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001051743 | 1.692686e-05 | 0.0001221012 | 0.57342 | GF PASS; acc 0.572344; MC not run |
| `runs/v22h_A_catred_1230` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001008547 | 1.660293e-05 | 0.0001174576 | 0.57552 | GF PASS; acc 0.574487; MC not run |
| `runs/v22h_A_catred_1302` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001068351 | 1.647059e-05 | 0.0001233057 | 0.57510 | GF PASS; acc 0.574667; MC not run |
| `runs/v22h_A_catred_1320` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.000109084 | 1.712542e-05 | 0.0001262094 | 0.57265 | GF PASS; acc 0.571484; MC not run |
| `runs/v22h_A_catred_201` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001033498 | 1.685757e-05 | 0.0001202073 | 0.57304 | GF PASS; acc 0.572749; MC not run |
| `runs/v22h_A_catred_2031` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001048789 | 1.795894e-05 | 0.0001228379 | 0.56947 | GF PASS; acc 0.569193; MC not run |
| `runs/v22h_A_catred_210` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.701057e-05 | 1.673143e-05 | 0.000113742 | 0.57457 | GF PASS; acc 0.574430; MC not run |
| `runs/v22h_A_catred_2130` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001008601 | 1.658089e-05 | 0.000117441 | 0.57552 | GF PASS; acc 0.575787; MC not run |
| `runs/v22h_A_catred_2301` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.260676e-05 | 1.685438e-05 | 0.0001094611 | 0.57442 | GF PASS; acc 0.574130; MC not run |
| `runs/v22h_A_catred_2310` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.644408e-05 | 1.723824e-05 | 0.0001136823 | 0.57270 | GF PASS; acc 0.572367; MC not run |
| `runs/v22h_A_catred_3012` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001025715 | 1.656015e-05 | 0.0001191317 | 0.57495 | GF PASS; acc 0.574336; MC not run |
| `runs/v22h_A_catred_3021` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001025715 | 1.654044e-05 | 0.000119112 | 0.57495 | GF PASS; acc 0.574329; MC not run |
| `runs/v22h_A_catred_3102` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001023146 | 1.677617e-05 | 0.0001190908 | 0.57399 | GF PASS; acc 0.573886; MC not run |
| `runs/v22h_A_catred_3120` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001025411 | 1.712461e-05 | 0.0001196657 | 0.57327 | GF PASS; acc 0.572611; MC not run |
| `runs/v22h_A_catred_3201` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 0.0001008604 | 1.735079e-05 | 0.0001182112 | 0.57213 | GF PASS; acc 0.571509; MC not run |
| `runs/v22h_A_catred_3210` (regenerate) | A catred | 134 | 45 | 2.923587e-19 | 9.386342e-05 | 1.692392e-05 | 0.0001107873 | 0.57442 | GF PASS; acc 0.573752; MC not run |
| `runs/v22h_A_direct_012` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.264598e-05 | 1.956965e-05 | 6.221563e-05 | 0.58374 | GF PASS; acc 0.584579; MC not run |
| `runs/v22h_A_direct_021` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.237128e-05 | 2.044325e-05 | 6.281453e-05 | 0.58141 | GF PASS; acc 0.581148; MC not run |
| `runs/v22h_A_direct_102` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.847819e-05 | 2.104526e-05 | 6.952345e-05 | 0.58026 | GF PASS; acc 0.580013; MC not run |
| `runs/v22h_A_direct_120` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.256625e-05 | 1.977212e-05 | 6.233837e-05 | 0.58315 | GF PASS; acc 0.582620; MC not run |
| `runs/v22h_A_direct_201` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.144996e-05 | 1.966455e-05 | 6.111451e-05 | 0.58315 | GF PASS; acc 0.582617; MC not run |
| `runs/v22h_A_direct_210` (regenerate) | A direct | 126 | 45 | 2.923587e-19 | 4.18816e-05 | 1.969301e-05 | 6.157461e-05 | 0.58315 | GF PASS; acc 0.583116; MC not run |
| `runs/v22h_A_flag_012` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.416777e-05 | 2.073581e-05 | 5.490358e-05 | 0.56401 | GF PASS; acc 0.563207; MC not run |
| `runs/v22h_A_flag_021` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.385976e-05 | 2.148431e-05 | 5.534407e-05 | 0.56121 | GF PASS; acc 0.560443; MC not run |
| `runs/v22h_A_flag_102` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.499547e-05 | 2.199559e-05 | 5.699107e-05 | 0.55954 | GF PASS; acc 0.559192; MC not run |
| `runs/v22h_A_flag_120` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.464937e-05 | 2.096212e-05 | 5.561149e-05 | 0.56344 | GF PASS; acc 0.562006; MC not run |
| [runs/v22h_A_flag_201](runs/v22h_A_flag_201.qasm) · [JSON](runs/v22h_A_flag_201.json) · [receipt](runs/v22h_A_flag_201.result.json) | A flag | 132 | 45 | 2.923587e-19 | 3.377585e-05 | 2.086278e-05 | 5.463864e-05 | 0.56344 | GF PASS; acc 0.562023; MC not run |
| `runs/v22h_A_flag_210` (regenerate) | A flag | 132 | 45 | 2.923587e-19 | 3.410477e-05 | 2.089878e-05 | 5.500356e-05 | 0.56344 | GF PASS; acc 0.562828; MC not run |
| `runs/v22h_A_hybrid1_012` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.22673e-05 | 2.152172e-05 | 6.378902e-05 | 0.57976 | GF PASS; acc 0.578799; MC not run |
| `runs/v22h_A_hybrid1_021` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.189347e-05 | 2.149121e-05 | 6.338468e-05 | 0.57976 | GF PASS; acc 0.579833; MC not run |
| `runs/v22h_A_hybrid1_102` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.22673e-05 | 2.152172e-05 | 6.378902e-05 | 0.57976 | GF PASS; acc 0.578799; MC not run |
| `runs/v22h_A_hybrid1_120` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.22673e-05 | 2.152172e-05 | 6.378902e-05 | 0.57976 | GF PASS; acc 0.578799; MC not run |
| `runs/v22h_A_hybrid1_201` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.189347e-05 | 2.149121e-05 | 6.338468e-05 | 0.57976 | GF PASS; acc 0.579833; MC not run |
| `runs/v22h_A_hybrid1_210` (regenerate) | A hybrid1 | 125 | 45 | 2.923587e-19 | 4.189347e-05 | 2.149121e-05 | 6.338468e-05 | 0.57976 | GF PASS; acc 0.579833; MC not run |
| `runs/v22h_A_hybrid2_012` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.07041e-05 | 1.990181e-05 | 6.060591e-05 | 0.58297 | GF PASS; acc 0.582448; MC not run |
| `runs/v22h_A_hybrid2_021` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.07041e-05 | 1.990181e-05 | 6.060591e-05 | 0.58297 | GF PASS; acc 0.582448; MC not run |
| `runs/v22h_A_hybrid2_102` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.07041e-05 | 1.990181e-05 | 6.060591e-05 | 0.58297 | GF PASS; acc 0.582448; MC not run |
| `runs/v22h_A_hybrid2_120` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.07041e-05 | 1.990181e-05 | 6.060591e-05 | 0.58297 | GF PASS; acc 0.582448; MC not run |
| `runs/v22h_A_hybrid2_201` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.07041e-05 | 1.990181e-05 | 6.060591e-05 | 0.58297 | GF PASS; acc 0.582448; MC not run |
| `runs/v22h_A_hybrid2_210` (regenerate) | A hybrid2 | 124 | 45 | 2.923587e-19 | 4.07041e-05 | 1.990181e-05 | 6.060591e-05 | 0.58297 | GF PASS; acc 0.582448; MC not run |
| `runs/v22h_A_hybrid2t_012` (regenerate) | A hybrid2t | 123 | 45 | 2.923587e-19 | 5.484719e-05 | 2.083351e-05 | 7.56807e-05 | 0.58066 | GF PASS; acc 0.579800; MC not run |
| `runs/v22h_A_redundant_012` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.11299e-05 | 1.793416e-05 | 5.906407e-05 | 0.57742 | GF PASS; acc 0.576860; MC not run |
| `runs/v22h_A_redundant_0132` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.247324e-05 | 1.939762e-05 | 6.187085e-05 | 0.57396 | GF PASS; acc 0.574139; MC not run |
| `runs/v22h_A_redundant_021` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.124735e-05 | 1.847476e-05 | 5.97221e-05 | 0.57513 | GF PASS; acc 0.574492; MC not run |
| `runs/v22h_A_redundant_0231` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.445869e-05 | 1.875169e-05 | 6.321038e-05 | 0.57452 | GF PASS; acc 0.573831; MC not run |
| `runs/v22h_A_redundant_0312` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.260202e-05 | 1.863365e-05 | 6.123567e-05 | 0.57621 | GF PASS; acc 0.575714; MC not run |
| `runs/v22h_A_redundant_0321` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.281212e-05 | 1.940623e-05 | 6.221836e-05 | 0.57335 | GF PASS; acc 0.572184; MC not run |
| `runs/v22h_A_redundant_102` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.625295e-05 | 1.885019e-05 | 6.510314e-05 | 0.57398 | GF PASS; acc 0.573103; MC not run |
| `runs/v22h_A_redundant_1032` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.274352e-05 | 1.938438e-05 | 6.21279e-05 | 0.57396 | GF PASS; acc 0.573053; MC not run |
| `runs/v22h_A_redundant_120` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.119534e-05 | 1.795223e-05 | 5.914757e-05 | 0.57684 | GF PASS; acc 0.576028; MC not run |
| `runs/v22h_A_redundant_1230` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.131677e-05 | 1.795615e-05 | 5.927292e-05 | 0.57684 | GF PASS; acc 0.576147; MC not run |
| `runs/v22h_A_redundant_1302` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.233071e-05 | 1.886327e-05 | 6.119398e-05 | 0.57567 | GF PASS; acc 0.574698; MC not run |
| `runs/v22h_A_redundant_1320` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.289215e-05 | 1.922693e-05 | 6.211908e-05 | 0.57338 | GF PASS; acc 0.573208; MC not run |
| `runs/v22h_A_redundant_201` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.097804e-05 | 1.790676e-05 | 5.88848e-05 | 0.57684 | GF PASS; acc 0.576613; MC not run |
| `runs/v22h_A_redundant_2031` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.428701e-05 | 1.846426e-05 | 6.275127e-05 | 0.57508 | GF PASS; acc 0.574452; MC not run |
| `runs/v22h_A_redundant_210` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.104441e-05 | 1.791538e-05 | 5.895979e-05 | 0.57685 | GF PASS; acc 0.575896; MC not run |
| `runs/v22h_A_redundant_2130` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.116583e-05 | 1.791864e-05 | 5.908448e-05 | 0.57684 | GF PASS; acc 0.575726; MC not run |
| `runs/v22h_A_redundant_2301` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.146495e-05 | 1.785439e-05 | 5.931934e-05 | 0.57738 | GF PASS; acc 0.576941; MC not run |
| `runs/v22h_A_redundant_2310` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.427479e-05 | 1.821136e-05 | 6.248615e-05 | 0.57566 | GF PASS; acc 0.575371; MC not run |
| `runs/v22h_A_redundant_3012` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.220207e-05 | 1.785354e-05 | 6.005561e-05 | 0.57909 | GF PASS; acc 0.579609; MC not run |
| `runs/v22h_A_redundant_3021` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.234604e-05 | 1.888172e-05 | 6.122776e-05 | 0.57506 | GF PASS; acc 0.574072; MC not run |
| `runs/v22h_A_redundant_3102` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 5.320197e-05 | 1.940327e-05 | 7.260524e-05 | 0.57335 | GF PASS; acc 0.573810; MC not run |
| `runs/v22h_A_redundant_3120` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.296401e-05 | 1.840161e-05 | 6.136562e-05 | 0.57620 | GF PASS; acc 0.576245; MC not run |
| `runs/v22h_A_redundant_3201` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.25184e-05 | 1.889727e-05 | 6.141567e-05 | 0.57391 | GF PASS; acc 0.573584; MC not run |
| `runs/v22h_A_redundant_3210` (regenerate) | A redundant | 130 | 45 | 2.923587e-19 | 4.283989e-05 | 1.890713e-05 | 6.174702e-05 | 0.57392 | GF PASS; acc 0.573635; MC not run |
| `runs/v22h_A_seq_012` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.602003e-05 | 3.342509e-05 | 7.944512e-05 | 0.55661 | GF PASS; acc 0.557019; MC not run |
| `runs/v22h_A_seq_021` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.415047e-05 | 3.29027e-05 | 7.705317e-05 | 0.55662 | GF PASS; acc 0.556725; MC not run |
| `runs/v22h_A_seq_102` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.839813e-05 | 3.365671e-05 | 8.205484e-05 | 0.55662 | GF PASS; acc 0.555892; MC not run |
| `runs/v22h_A_seq_120` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.687077e-05 | 3.37037e-05 | 8.057447e-05 | 0.55606 | GF PASS; acc 0.555004; MC not run |
| `runs/v22h_A_seq_201` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.249942e-05 | 3.276483e-05 | 7.526425e-05 | 0.55606 | GF PASS; acc 0.555610; MC not run |
| `runs/v22h_A_seq_210` (regenerate) | A seq | 126 | 45 | 2.923587e-19 | 4.363499e-05 | 3.299737e-05 | 7.663237e-05 | 0.55607 | GF PASS; acc 0.555668; MC not run |
| `runs/v22h_BC_cat13_012` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.127935e-05 | 1.914524e-05 | 6.042459e-05 | 0.55880 | GF PASS; acc 0.558911; MC not run |
| `runs/v22h_BC_cat13_021` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.19363e-05 | 1.962496e-05 | 6.156126e-05 | 0.55435 | GF PASS; acc 0.554014; MC not run |
| `runs/v22h_BC_cat13_102` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.144848e-05 | 2.005372e-05 | 6.15022e-05 | 0.55215 | GF PASS; acc 0.551761; MC not run |
| `runs/v22h_BC_cat13_120` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.126181e-05 | 1.919485e-05 | 6.045665e-05 | 0.55767 | GF PASS; acc 0.557687; MC not run |
| `runs/v22h_BC_cat13_201` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.1768e-05 | 1.906075e-05 | 6.082875e-05 | 0.55767 | GF PASS; acc 0.557660; MC not run |
| `runs/v22h_BC_cat13_210` (regenerate) | BC cat13 | 135 | 45 | 2.923587e-19 | 4.172332e-05 | 1.906994e-05 | 6.079326e-05 | 0.55768 | GF PASS; acc 0.557581; MC not run |
| `runs/v22h_BC_cat13red_012` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.842216e-05 | 1.3512e-05 | 5.193417e-05 | 0.53726 | GF PASS; acc 0.536729; MC not run |
| `runs/v22h_BC_cat13red_0132` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.822708e-05 | 1.336946e-05 | 5.159654e-05 | 0.53576 | GF PASS; acc 0.535819; MC not run |
| `runs/v22h_BC_cat13red_021` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.842134e-05 | 1.35253e-05 | 5.194664e-05 | 0.53300 | GF PASS; acc 0.532952; MC not run |
| `runs/v22h_BC_cat13red_0231` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.83859e-05 | 1.320494e-05 | 5.159084e-05 | 0.53115 | GF PASS; acc 0.531229; MC not run |
| `runs/v22h_BC_cat13red_0312` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.831153e-05 | 1.293435e-05 | 5.124588e-05 | 0.53426 | GF PASS; acc 0.533558; MC not run |
| `runs/v22h_BC_cat13red_0321` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.831153e-05 | 1.291756e-05 | 5.122909e-05 | 0.53426 | GF PASS; acc 0.533593; MC not run |
| `runs/v22h_BC_cat13red_102` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.861912e-05 | 1.371782e-05 | 5.233694e-05 | 0.53087 | GF PASS; acc 0.530733; MC not run |
| `runs/v22h_BC_cat13red_1032` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.823597e-05 | 1.336315e-05 | 5.159913e-05 | 0.53576 | GF PASS; acc 0.536348; MC not run |
| `runs/v22h_BC_cat13red_120` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.86883e-05 | 1.337561e-05 | 5.206391e-05 | 0.53618 | GF PASS; acc 0.535868; MC not run |
| `runs/v22h_BC_cat13red_1230` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.877695e-05 | 1.339779e-05 | 5.217474e-05 | 0.53476 | GF PASS; acc 0.535169; MC not run |
| `runs/v22h_BC_cat13red_1302` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.823597e-05 | 1.355176e-05 | 5.178773e-05 | 0.53186 | GF PASS; acc 0.531617; MC not run |
| `runs/v22h_BC_cat13red_1320` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.838673e-05 | 1.326973e-05 | 5.165645e-05 | 0.53398 | GF PASS; acc 0.534014; MC not run |
| `runs/v22h_BC_cat13red_201` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.843105e-05 | 1.337807e-05 | 5.180913e-05 | 0.53618 | GF PASS; acc 0.535459; MC not run |
| `runs/v22h_BC_cat13red_2031` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.839562e-05 | 1.305348e-05 | 5.14491e-05 | 0.53432 | GF PASS; acc 0.534056; MC not run |
| `runs/v22h_BC_cat13red_210` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.86883e-05 | 1.337799e-05 | 5.206629e-05 | 0.53618 | GF PASS; acc 0.535222; MC not run |
| `runs/v22h_BC_cat13red_2130` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.877695e-05 | 1.340083e-05 | 5.217778e-05 | 0.53476 | GF PASS; acc 0.534465; MC not run |
| `runs/v22h_BC_cat13red_2301` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.855526e-05 | 1.307205e-05 | 5.162731e-05 | 0.53362 | GF PASS; acc 0.533637; MC not run |
| `runs/v22h_BC_cat13red_2310` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.870602e-05 | 1.307155e-05 | 5.177757e-05 | 0.53362 | GF PASS; acc 0.533397; MC not run |
| `runs/v22h_BC_cat13red_3012` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.831153e-05 | 1.294636e-05 | 5.125789e-05 | 0.53427 | GF PASS; acc 0.533762; MC not run |
| `runs/v22h_BC_cat13red_3021` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.831153e-05 | 1.298162e-05 | 5.129315e-05 | 0.53002 | GF PASS; acc 0.530174; MC not run |
| `runs/v22h_BC_cat13red_3102` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.843819e-05 | 1.315595e-05 | 5.159414e-05 | 0.52791 | GF PASS; acc 0.527489; MC not run |
| `runs/v22h_BC_cat13red_3120` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.840006e-05 | 1.282379e-05 | 5.122385e-05 | 0.53319 | GF PASS; acc 0.532812; MC not run |
| `runs/v22h_BC_cat13red_3201` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.832042e-05 | 1.280996e-05 | 5.113038e-05 | 0.53319 | GF PASS; acc 0.532852; MC not run |
| `runs/v22h_BC_cat13red_3210` (regenerate) | BC cat13red | 145 | 45 | 2.923587e-19 | 3.847117e-05 | 1.280781e-05 | 5.127898e-05 | 0.53320 | GF PASS; acc 0.533135; MC not run |
| `runs/v22h_BC_cat13red_m3_0123` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.927159e-05 | 1.422023e-05 | 5.349182e-05 | 0.54846 | GF PASS; acc 0.548641; MC not run |
| `runs/v22h_BC_cat13red_m3_0132` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.942252e-05 | 1.510568e-05 | 5.45282e-05 | 0.53371 | GF PASS; acc 0.533591; MC not run |
| `runs/v22h_BC_cat13red_m3_0213` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.960024e-05 | 1.443999e-05 | 5.404023e-05 | 0.54192 | GF PASS; acc 0.540781; MC not run |
| `runs/v22h_BC_cat13red_m3_0231` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.989666e-05 | 1.490553e-05 | 5.480219e-05 | 0.53080 | GF PASS; acc 0.530646; MC not run |
| `runs/v22h_BC_cat13red_m3_0312` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.950614e-05 | 1.465606e-05 | 5.41622e-05 | 0.53017 | GF PASS; acc 0.530471; MC not run |
| `runs/v22h_BC_cat13red_m3_0321` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.967479e-05 | 1.467738e-05 | 5.435217e-05 | 0.53017 | GF PASS; acc 0.530445; MC not run |
| `runs/v22h_BC_cat13red_m3_1023` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.946936e-05 | 1.441312e-05 | 5.388248e-05 | 0.54192 | GF PASS; acc 0.541907; MC not run |
| `runs/v22h_BC_cat13red_m3_1032` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.9919e-05 | 1.528225e-05 | 5.520125e-05 | 0.53053 | GF PASS; acc 0.530407; MC not run |
| `runs/v22h_BC_cat13red_m3_1203` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.961357e-05 | 1.452339e-05 | 5.413696e-05 | 0.54518 | GF PASS; acc 0.545434; MC not run |
| `runs/v22h_BC_cat13red_m3_1230` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.961357e-05 | 1.453396e-05 | 5.414753e-05 | 0.54445 | GF PASS; acc 0.544515; MC not run |
| `runs/v22h_BC_cat13red_m3_1302` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.961947e-05 | 1.52748e-05 | 5.489427e-05 | 0.53089 | GF PASS; acc 0.530962; MC not run |
| `runs/v22h_BC_cat13red_m3_1320` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.978999e-05 | 1.515104e-05 | 5.494103e-05 | 0.53229 | GF PASS; acc 0.531717; MC not run |
| `runs/v22h_BC_cat13red_m3_2013` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.018187e-05 | 1.509879e-05 | 5.528066e-05 | 0.54518 | GF PASS; acc 0.545072; MC not run |
| `runs/v22h_BC_cat13red_m3_2031` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.063011e-05 | 1.537832e-05 | 5.600843e-05 | 0.53185 | GF PASS; acc 0.531148; MC not run |
| `runs/v22h_BC_cat13red_m3_2103` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.032187e-05 | 1.514991e-05 | 5.547178e-05 | 0.54192 | GF PASS; acc 0.541533; MC not run |
| `runs/v22h_BC_cat13red_m3_2130` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.011076e-05 | 1.514739e-05 | 5.525815e-05 | 0.54228 | GF PASS; acc 0.542086; MC not run |
| `runs/v22h_BC_cat13red_m3_2301` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.011947e-05 | 1.491235e-05 | 5.503182e-05 | 0.54149 | GF PASS; acc 0.540940; MC not run |
| `runs/v22h_BC_cat13red_m3_2310` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.044753e-05 | 1.521438e-05 | 5.566191e-05 | 0.53434 | GF PASS; acc 0.534820; MC not run |
| `runs/v22h_BC_cat13red_m3_3012` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.941808e-05 | 1.443063e-05 | 5.384871e-05 | 0.53762 | GF PASS; acc 0.537219; MC not run |
| `runs/v22h_BC_cat13red_m3_3021` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.967479e-05 | 1.468228e-05 | 5.435707e-05 | 0.53017 | GF PASS; acc 0.530451; MC not run |
| `runs/v22h_BC_cat13red_m3_3102` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.959281e-05 | 1.482123e-05 | 5.441403e-05 | 0.52736 | GF PASS; acc 0.527452; MC not run |
| `runs/v22h_BC_cat13red_m3_3120` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.978555e-05 | 1.451828e-05 | 5.430383e-05 | 0.53264 | GF PASS; acc 0.532520; MC not run |
| `runs/v22h_BC_cat13red_m3_3201` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 3.997198e-05 | 1.488263e-05 | 5.485461e-05 | 0.53371 | GF PASS; acc 0.532902; MC not run |
| `runs/v22h_BC_cat13red_m3_3210` (regenerate) | BC cat13red mask=3 | 145 | 45 | 2.923587e-19 | 4.011384e-05 | 1.487666e-05 | 5.49905e-05 | 0.53371 | GF PASS; acc 0.533979; MC not run |
| `runs/v22h_BC_cat13red_m5_0123` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.824936e-05 | 1.472776e-05 | 5.297713e-05 | 0.54919 | GF PASS; acc 0.548958; MC not run |
| `runs/v22h_BC_cat13red_m5_0132` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.911909e-05 | 1.581241e-05 | 5.49315e-05 | 0.53187 | GF PASS; acc 0.531846; MC not run |
| `runs/v22h_BC_cat13red_m5_0213` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.848936e-05 | 1.480899e-05 | 5.329835e-05 | 0.54264 | GF PASS; acc 0.542024; MC not run |
| `runs/v22h_BC_cat13red_m5_0231` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.869221e-05 | 1.53215e-05 | 5.401371e-05 | 0.53229 | GF PASS; acc 0.532480; MC not run |
| `runs/v22h_BC_cat13red_m5_0312` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.892798e-05 | 1.522192e-05 | 5.41499e-05 | 0.53335 | GF PASS; acc 0.532982; MC not run |
| `runs/v22h_BC_cat13red_m5_0321` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.873947e-05 | 1.506325e-05 | 5.380272e-05 | 0.53229 | GF PASS; acc 0.532134; MC not run |
| `runs/v22h_BC_cat13red_m5_1023` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.862714e-05 | 1.578766e-05 | 5.44148e-05 | 0.54264 | GF PASS; acc 0.542893; MC not run |
| `runs/v22h_BC_cat13red_m5_1032` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.938759e-05 | 1.638875e-05 | 5.577634e-05 | 0.53187 | GF PASS; acc 0.531659; MC not run |
| `runs/v22h_BC_cat13red_m5_1203` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.842492e-05 | 1.522386e-05 | 5.364878e-05 | 0.54590 | GF PASS; acc 0.545034; MC not run |
| `runs/v22h_BC_cat13red_m5_1230` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.842492e-05 | 1.522692e-05 | 5.365184e-05 | 0.54590 | GF PASS; acc 0.544989; MC not run |
| `runs/v22h_BC_cat13red_m5_1302` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.938759e-05 | 1.639032e-05 | 5.577791e-05 | 0.53187 | GF PASS; acc 0.531578; MC not run |
| `runs/v22h_BC_cat13red_m5_1320` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.880368e-05 | 1.608785e-05 | 5.489153e-05 | 0.53221 | GF PASS; acc 0.532670; MC not run |
| `runs/v22h_BC_cat13red_m5_2013` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.867825e-05 | 1.470152e-05 | 5.337977e-05 | 0.54264 | GF PASS; acc 0.542594; MC not run |
| `runs/v22h_BC_cat13red_m5_2031` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.913704e-05 | 1.507475e-05 | 5.421179e-05 | 0.53654 | GF PASS; acc 0.536520; MC not run |
| `runs/v22h_BC_cat13red_m5_2103` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.87227e-05 | 1.496793e-05 | 5.369062e-05 | 0.54264 | GF PASS; acc 0.542510; MC not run |
| `runs/v22h_BC_cat13red_m5_2130` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.87227e-05 | 1.497166e-05 | 5.369436e-05 | 0.54264 | GF PASS; acc 0.542517; MC not run |
| `runs/v22h_BC_cat13red_m5_2301` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.860415e-05 | 1.485106e-05 | 5.345521e-05 | 0.54193 | GF PASS; acc 0.542102; MC not run |
| `runs/v22h_BC_cat13red_m5_2310` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.878554e-05 | 1.530279e-05 | 5.408834e-05 | 0.53406 | GF PASS; acc 0.534071; MC not run |
| `runs/v22h_BC_cat13red_m5_3012` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.830708e-05 | 1.498861e-05 | 5.32957e-05 | 0.53869 | GF PASS; acc 0.538840; MC not run |
| `runs/v22h_BC_cat13red_m5_3021` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.873947e-05 | 1.506521e-05 | 5.380468e-05 | 0.53229 | GF PASS; acc 0.532033; MC not run |
| `runs/v22h_BC_cat13red_m5_3102` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.85107e-05 | 1.596824e-05 | 5.447894e-05 | 0.52947 | GF PASS; acc 0.528920; MC not run |
| `runs/v22h_BC_cat13red_m5_3120` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.839035e-05 | 1.536621e-05 | 5.375656e-05 | 0.53370 | GF PASS; acc 0.533527; MC not run |
| `runs/v22h_BC_cat13red_m5_3201` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.84307e-05 | 1.476665e-05 | 5.319735e-05 | 0.53264 | GF PASS; acc 0.532040; MC not run |
| `runs/v22h_BC_cat13red_m5_3210` (regenerate) | BC cat13red mask=5 | 145 | 45 | 2.923587e-19 | 3.843479e-05 | 1.49129e-05 | 5.334769e-05 | 0.53264 | GF PASS; acc 0.532369; MC not run |
| `runs/v22h_BC_cat13red_m6_0123` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.020379e-05 | 1.518653e-05 | 5.539032e-05 | 0.54918 | GF PASS; acc 0.548550; MC not run |
| `runs/v22h_BC_cat13red_m6_0132` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.25374e-05 | 1.693254e-05 | 5.946993e-05 | 0.52382 | GF PASS; acc 0.523472; MC not run |
| `runs/v22h_BC_cat13red_m6_0213` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.06811e-05 | 1.567341e-05 | 5.635451e-05 | 0.54264 | GF PASS; acc 0.542260; MC not run |
| `runs/v22h_BC_cat13red_m6_0231` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.06811e-05 | 1.56723e-05 | 5.63534e-05 | 0.54264 | GF PASS; acc 0.542274; MC not run |
| `runs/v22h_BC_cat13red_m6_0312` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.08198e-05 | 1.619719e-05 | 5.701699e-05 | 0.53328 | GF PASS; acc 0.533109; MC not run |
| `runs/v22h_BC_cat13red_m6_0321` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.099582e-05 | 1.654366e-05 | 5.753948e-05 | 0.52625 | GF PASS; acc 0.526067; MC not run |
| `runs/v22h_BC_cat13red_m6_1023` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.023737e-05 | 1.497259e-05 | 5.520996e-05 | 0.54264 | GF PASS; acc 0.543423; MC not run |
| `runs/v22h_BC_cat13red_m6_1032` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.16813e-05 | 1.635652e-05 | 5.803782e-05 | 0.52277 | GF PASS; acc 0.522404; MC not run |
| `runs/v22h_BC_cat13red_m6_1203` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.015514e-05 | 1.467017e-05 | 5.482531e-05 | 0.54590 | GF PASS; acc 0.545398; MC not run |
| `runs/v22h_BC_cat13red_m6_1230` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.027257e-05 | 1.506456e-05 | 5.533713e-05 | 0.53762 | GF PASS; acc 0.537847; MC not run |
| `runs/v22h_BC_cat13red_m6_1302` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.101138e-05 | 1.575761e-05 | 5.676898e-05 | 0.52423 | GF PASS; acc 0.523932; MC not run |
| `runs/v22h_BC_cat13red_m6_1320` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.093606e-05 | 1.53265e-05 | 5.626256e-05 | 0.52632 | GF PASS; acc 0.526419; MC not run |
| `runs/v22h_BC_cat13red_m6_2013` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.048181e-05 | 1.497489e-05 | 5.54567e-05 | 0.54263 | GF PASS; acc 0.542018; MC not run |
| `runs/v22h_BC_cat13red_m6_2031` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.048181e-05 | 1.497344e-05 | 5.545525e-05 | 0.54263 | GF PASS; acc 0.542020; MC not run |
| `runs/v22h_BC_cat13red_m6_2103` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.04107e-05 | 1.471465e-05 | 5.512535e-05 | 0.54264 | GF PASS; acc 0.541529; MC not run |
| `runs/v22h_BC_cat13red_m6_2130` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.063867e-05 | 1.508533e-05 | 5.572399e-05 | 0.53654 | GF PASS; acc 0.536561; MC not run |
| `runs/v22h_BC_cat13red_m6_2301` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.012777e-05 | 1.528359e-05 | 5.541135e-05 | 0.53619 | GF PASS; acc 0.536602; MC not run |
| `runs/v22h_BC_cat13red_m6_2310` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.001701e-05 | 1.485335e-05 | 5.487036e-05 | 0.54193 | GF PASS; acc 0.542138; MC not run |
| `runs/v22h_BC_cat13red_m6_3012` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.006975e-05 | 1.547409e-05 | 5.554384e-05 | 0.53478 | GF PASS; acc 0.534405; MC not run |
| `runs/v22h_BC_cat13red_m6_3021` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.024613e-05 | 1.581192e-05 | 5.605805e-05 | 0.52772 | GF PASS; acc 0.526985; MC not run |
| `runs/v22h_BC_cat13red_m6_3102` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 4.016999e-05 | 1.550246e-05 | 5.567246e-05 | 0.52947 | GF PASS; acc 0.528889; MC not run |
| `runs/v22h_BC_cat13red_m6_3120` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 3.983912e-05 | 1.488609e-05 | 5.472521e-05 | 0.53370 | GF PASS; acc 0.533435; MC not run |
| `runs/v22h_BC_cat13red_m6_3201` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 3.986053e-05 | 1.506387e-05 | 5.49244e-05 | 0.52877 | GF PASS; acc 0.528675; MC not run |
| `runs/v22h_BC_cat13red_m6_3210` (regenerate) | BC cat13red mask=6 | 145 | 45 | 2.923587e-19 | 3.992696e-05 | 1.492269e-05 | 5.484965e-05 | 0.52877 | GF PASS; acc 0.528423; MC not run |
| `runs/v22h_BC_cat3_012` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.203322e-05 | 2.122966e-05 | 7.326288e-05 | 0.55034 | GF PASS; acc 0.550728; MC not run |
| `runs/v22h_BC_cat3_021` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.228211e-05 | 2.114467e-05 | 7.342677e-05 | 0.55034 | GF PASS; acc 0.550716; MC not run |
| `runs/v22h_BC_cat3_102` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.135813e-05 | 2.126026e-05 | 7.261839e-05 | 0.55034 | GF PASS; acc 0.550761; MC not run |
| `runs/v22h_BC_cat3_120` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.182e-05 | 2.174918e-05 | 7.356918e-05 | 0.54596 | GF PASS; acc 0.545990; MC not run |
| `runs/v22h_BC_cat3_201` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.263731e-05 | 2.162327e-05 | 7.426058e-05 | 0.54596 | GF PASS; acc 0.546058; MC not run |
| `runs/v22h_BC_cat3_210` (regenerate) | BC cat3 | 141 | 45 | 2.923587e-19 | 5.213988e-05 | 2.16597e-05 | 7.379958e-05 | 0.54596 | GF PASS; acc 0.545990; MC not run |
| `runs/v22h_BC_cat3red_0123` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 5.037991e-05 | 1.281478e-05 | 6.31947e-05 | 0.53174 | GF PASS; acc 0.531112; MC not run |
| `runs/v22h_BC_cat3red_0132` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 5.083888e-05 | 1.297652e-05 | 6.381539e-05 | 0.52828 | GF PASS; acc 0.528274; MC not run |
| `runs/v22h_BC_cat3red_0213` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 5.037991e-05 | 1.280276e-05 | 6.318267e-05 | 0.53174 | GF PASS; acc 0.531079; MC not run |
| `runs/v22h_BC_cat3red_0231` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.961366e-05 | 1.340055e-05 | 6.301421e-05 | 0.51990 | GF PASS; acc 0.519956; MC not run |
| `runs/v22h_BC_cat3red_0312` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.823977e-05 | 1.33905e-05 | 6.163027e-05 | 0.52275 | GF PASS; acc 0.522344; MC not run |
| `runs/v22h_BC_cat3red_0321` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.823977e-05 | 1.339368e-05 | 6.163345e-05 | 0.52275 | GF PASS; acc 0.522364; MC not run |
| `runs/v22h_BC_cat3red_1023` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.970311e-05 | 1.282501e-05 | 6.252813e-05 | 0.53067 | GF PASS; acc 0.529607; MC not run |
| `runs/v22h_BC_cat3red_1032` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 5.016208e-05 | 1.298386e-05 | 6.314593e-05 | 0.52722 | GF PASS; acc 0.526980; MC not run |
| `runs/v22h_BC_cat3red_1203` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.980978e-05 | 1.293524e-05 | 6.274502e-05 | 0.52645 | GF PASS; acc 0.526989; MC not run |
| `runs/v22h_BC_cat3red_1230` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.980978e-05 | 1.293978e-05 | 6.274956e-05 | 0.52645 | GF PASS; acc 0.526954; MC not run |
| `runs/v22h_BC_cat3red_1302` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.950747e-05 | 1.290613e-05 | 6.24136e-05 | 0.53039 | GF PASS; acc 0.529986; MC not run |
| `runs/v22h_BC_cat3red_1320` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 5.027292e-05 | 1.321223e-05 | 6.348515e-05 | 0.52337 | GF PASS; acc 0.522374; MC not run |
| `runs/v22h_BC_cat3red_2013` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.970311e-05 | 1.283605e-05 | 6.253916e-05 | 0.53067 | GF PASS; acc 0.529887; MC not run |
| `runs/v22h_BC_cat3red_2031` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.961366e-05 | 1.35354e-05 | 6.314906e-05 | 0.51577 | GF PASS; acc 0.516357; MC not run |
| `runs/v22h_BC_cat3red_2103` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.980978e-05 | 1.293983e-05 | 6.274961e-05 | 0.52645 | GF PASS; acc 0.526981; MC not run |
| `runs/v22h_BC_cat3red_2130` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.980978e-05 | 1.294505e-05 | 6.275483e-05 | 0.52645 | GF PASS; acc 0.526973; MC not run |
| `runs/v22h_BC_cat3red_2301` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.959624e-05 | 1.323822e-05 | 6.283446e-05 | 0.52303 | GF PASS; acc 0.522986; MC not run |
| `runs/v22h_BC_cat3red_2310` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.950759e-05 | 1.334968e-05 | 6.285726e-05 | 0.51818 | GF PASS; acc 0.517974; MC not run |
| `runs/v22h_BC_cat3red_3012` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.815123e-05 | 1.310287e-05 | 6.12541e-05 | 0.53011 | GF PASS; acc 0.529982; MC not run |
| `runs/v22h_BC_cat3red_3021` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.815123e-05 | 1.3106e-05 | 6.125724e-05 | 0.53011 | GF PASS; acc 0.529978; MC not run |
| `runs/v22h_BC_cat3red_3102` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.799147e-05 | 1.319708e-05 | 6.118855e-05 | 0.52519 | GF PASS; acc 0.524898; MC not run |
| `runs/v22h_BC_cat3red_3120` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.808012e-05 | 1.340818e-05 | 6.14883e-05 | 0.52136 | GF PASS; acc 0.521403; MC not run |
| `runs/v22h_BC_cat3red_3201` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.823988e-05 | 1.329169e-05 | 6.153157e-05 | 0.52624 | GF PASS; acc 0.526541; MC not run |
| `runs/v22h_BC_cat3red_3210` (regenerate) | BC cat3red | 153 | 45 | 2.923587e-19 | 4.815123e-05 | 1.339343e-05 | 6.154466e-05 | 0.52136 | GF PASS; acc 0.521407; MC not run |
| `runs/v22h_BC_cat3reusered_0123` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.91947e-05 | 1.921894e-05 | 6.841364e-05 | 0.44558 | GF FAIL; acc 0.445482; MC not run |
| `runs/v22h_BC_cat3reusered_0132` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.875512e-05 | 1.956176e-05 | 6.831688e-05 | 0.44653 | GF FAIL; acc 0.446368; MC not run |
| `runs/v22h_BC_cat3reusered_0213` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.91947e-05 | 1.91079e-05 | 6.830261e-05 | 0.44558 | GF FAIL; acc 0.445528; MC not run |
| `runs/v22h_BC_cat3reusered_0231` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.921498e-05 | 1.924806e-05 | 6.846304e-05 | 0.44653 | GF FAIL; acc 0.446529; MC not run |
| `runs/v22h_BC_cat3reusered_0312` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.955541e-05 | 1.972458e-05 | 6.927998e-05 | 0.44748 | GF FAIL; acc 0.447007; MC not run |
| `runs/v22h_BC_cat3reusered_0321` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.008555e-05 | 1.949113e-05 | 6.957668e-05 | 0.44748 | GF FAIL; acc 0.448287; MC not run |
| `runs/v22h_BC_cat3reusered_1023` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.91947e-05 | 1.935932e-05 | 6.855403e-05 | 0.44559 | GF FAIL; acc 0.446202; MC not run |
| `runs/v22h_BC_cat3reusered_1032` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.875512e-05 | 1.96962e-05 | 6.845132e-05 | 0.44653 | GF FAIL; acc 0.446195; MC not run |
| `runs/v22h_BC_cat3reusered_1203` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.075619e-05 | 1.939772e-05 | 7.015391e-05 | 0.44560 | GF FAIL; acc 0.446030; MC not run |
| `runs/v22h_BC_cat3reusered_1230` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.128704e-05 | 1.949571e-05 | 7.078274e-05 | 0.44558 | GF FAIL; acc 0.446059; MC not run |
| `runs/v22h_BC_cat3reusered_1302` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.875512e-05 | 1.979767e-05 | 6.855279e-05 | 0.44652 | GF FAIL; acc 0.447001; MC not run |
| `runs/v22h_BC_cat3reusered_1320` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.955139e-05 | 1.959606e-05 | 6.914745e-05 | 0.44653 | GF FAIL; acc 0.446940; MC not run |
| `runs/v22h_BC_cat3reusered_2013` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.91947e-05 | 1.951049e-05 | 6.870519e-05 | 0.44559 | GF FAIL; acc 0.445898; MC not run |
| `runs/v22h_BC_cat3reusered_2031` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.921498e-05 | 1.964738e-05 | 6.886236e-05 | 0.44653 | GF FAIL; acc 0.445749; MC not run |
| `runs/v22h_BC_cat3reusered_2103` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.075619e-05 | 1.965995e-05 | 7.041613e-05 | 0.44560 | GF FAIL; acc 0.446036; MC not run |
| `runs/v22h_BC_cat3reusered_2130` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.128704e-05 | 1.975879e-05 | 7.104583e-05 | 0.44558 | GF FAIL; acc 0.446003; MC not run |
| `runs/v22h_BC_cat3reusered_2301` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.025597e-05 | 1.972815e-05 | 6.998412e-05 | 0.44652 | GF FAIL; acc 0.446372; MC not run |
| `runs/v22h_BC_cat3reusered_2310` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.05221e-05 | 1.975694e-05 | 7.027904e-05 | 0.44653 | GF FAIL; acc 0.446322; MC not run |
| `runs/v22h_BC_cat3reusered_3012` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.955541e-05 | 1.974065e-05 | 6.929605e-05 | 0.44746 | GF FAIL; acc 0.447477; MC not run |
| `runs/v22h_BC_cat3reusered_3021` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.008555e-05 | 1.950838e-05 | 6.959392e-05 | 0.44746 | GF FAIL; acc 0.447613; MC not run |
| `runs/v22h_BC_cat3reusered_3102` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.851512e-05 | 1.975166e-05 | 6.826678e-05 | 0.44747 | GF FAIL; acc 0.447344; MC not run |
| `runs/v22h_BC_cat3reusered_3120` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 4.931139e-05 | 1.954491e-05 | 6.88563e-05 | 0.44748 | GF FAIL; acc 0.447440; MC not run |
| `runs/v22h_BC_cat3reusered_3201` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.008555e-05 | 1.938923e-05 | 6.947478e-05 | 0.44747 | GF FAIL; acc 0.447582; MC not run |
| `runs/v22h_BC_cat3reusered_3210` (regenerate) | BC cat3reusered | 153 | 45 | 2.923587e-19 | 5.035168e-05 | 1.94143e-05 | 6.976598e-05 | 0.44748 | GF FAIL; acc 0.447987; MC not run |
| `runs/v22h_BC_cat3spinered_0123` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.199927e-05 | 1.918007e-05 | 7.117934e-05 | 0.44747 | GF FAIL; acc 0.447286; MC not run |
| `runs/v22h_BC_cat3spinered_0132` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.173384e-05 | 1.948572e-05 | 7.121956e-05 | 0.44747 | GF FAIL; acc 0.447835; MC not run |
| [runs/v22h_BC_cat3spinered_0213](runs/v22h_BC_cat3spinered_0213.qasm) · [JSON](runs/v22h_BC_cat3spinered_0213.json) · [receipt](runs/v22h_BC_cat3spinered_0213.result.json) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.199927e-05 | 1.875186e-05 | 7.075113e-05 | 0.44747 | GF FAIL; acc 0.447684; MC not run |
| `runs/v22h_BC_cat3spinered_0231` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.226914e-05 | 1.8824e-05 | 7.109313e-05 | 0.44747 | GF FAIL; acc 0.448036; MC not run |
| `runs/v22h_BC_cat3spinered_0312` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.273928e-05 | 1.939277e-05 | 7.213205e-05 | 0.44747 | GF FAIL; acc 0.447559; MC not run |
| `runs/v22h_BC_cat3spinered_0321` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.327457e-05 | 1.91592e-05 | 7.243377e-05 | 0.44747 | GF FAIL; acc 0.447345; MC not run |
| `runs/v22h_BC_cat3spinered_1023` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.199927e-05 | 1.918884e-05 | 7.11881e-05 | 0.44747 | GF FAIL; acc 0.447843; MC not run |
| `runs/v22h_BC_cat3spinered_1032` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.173384e-05 | 1.949069e-05 | 7.122453e-05 | 0.44747 | GF FAIL; acc 0.447300; MC not run |
| `runs/v22h_BC_cat3spinered_1203` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.350742e-05 | 1.882315e-05 | 7.233056e-05 | 0.44747 | GF FAIL; acc 0.447535; MC not run |
| `runs/v22h_BC_cat3spinered_1230` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.404271e-05 | 1.891825e-05 | 7.296096e-05 | 0.44747 | GF FAIL; acc 0.447325; MC not run |
| `runs/v22h_BC_cat3spinered_1302` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.173384e-05 | 1.937146e-05 | 7.11053e-05 | 0.44747 | GF FAIL; acc 0.447659; MC not run |
| `runs/v22h_BC_cat3spinered_1320` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.253456e-05 | 1.916502e-05 | 7.169958e-05 | 0.44747 | GF FAIL; acc 0.447991; MC not run |
| `runs/v22h_BC_cat3spinered_2013` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.200371e-05 | 1.877383e-05 | 7.077754e-05 | 0.44747 | GF FAIL; acc 0.447992; MC not run |
| `runs/v22h_BC_cat3spinered_2031` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.226469e-05 | 1.884297e-05 | 7.110767e-05 | 0.44747 | GF FAIL; acc 0.447672; MC not run |
| `runs/v22h_BC_cat3spinered_2103` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.351186e-05 | 1.88361e-05 | 7.234797e-05 | 0.44747 | GF FAIL; acc 0.447356; MC not run |
| `runs/v22h_BC_cat3spinered_2130` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.403827e-05 | 1.893244e-05 | 7.297071e-05 | 0.44747 | GF FAIL; acc 0.447572; MC not run |
| `runs/v22h_BC_cat3spinered_2301` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.327013e-05 | 1.912608e-05 | 7.239621e-05 | 0.44747 | GF FAIL; acc 0.447297; MC not run |
| `runs/v22h_BC_cat3spinered_2310` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.353555e-05 | 1.915296e-05 | 7.268851e-05 | 0.44747 | GF FAIL; acc 0.447854; MC not run |
| `runs/v22h_BC_cat3spinered_3012` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.274372e-05 | 1.940578e-05 | 7.21495e-05 | 0.44747 | GF FAIL; acc 0.447334; MC not run |
| `runs/v22h_BC_cat3spinered_3021` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.327013e-05 | 1.917334e-05 | 7.244347e-05 | 0.44747 | GF FAIL; acc 0.447553; MC not run |
| `runs/v22h_BC_cat3spinered_3102` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.173829e-05 | 1.937963e-05 | 7.111792e-05 | 0.44747 | GF FAIL; acc 0.448009; MC not run |
| `runs/v22h_BC_cat3spinered_3120` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.253012e-05 | 1.917021e-05 | 7.170033e-05 | 0.44747 | GF FAIL; acc 0.447673; MC not run |
| `runs/v22h_BC_cat3spinered_3201` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.327013e-05 | 1.912111e-05 | 7.239124e-05 | 0.44747 | GF FAIL; acc 0.447897; MC not run |
| `runs/v22h_BC_cat3spinered_3210` (regenerate) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.353555e-05 | 1.914419e-05 | 7.267974e-05 | 0.44747 | GF FAIL; acc 0.447334; MC not run |
| `runs/v22h_BC_cat4_012` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.249941e-05 | 2.376264e-05 | 7.626205e-05 | 0.53153 | GF PASS; acc 0.532759; MC not run |
| `runs/v22h_BC_cat4_021` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.31035e-05 | 2.358868e-05 | 7.669217e-05 | 0.53153 | GF PASS; acc 0.532734; MC not run |
| `runs/v22h_BC_cat4_102` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.182445e-05 | 2.378799e-05 | 7.561244e-05 | 0.53153 | GF PASS; acc 0.532737; MC not run |
| `runs/v22h_BC_cat4_120` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.193123e-05 | 2.364693e-05 | 7.557816e-05 | 0.53153 | GF PASS; acc 0.532108; MC not run |
| `runs/v22h_BC_cat4_201` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.310362e-05 | 2.343736e-05 | 7.654098e-05 | 0.53153 | GF PASS; acc 0.532166; MC not run |
| `runs/v22h_BC_cat4_210` (regenerate) | BC cat4 | 147 | 45 | 2.923587e-19 | 5.260608e-05 | 2.347042e-05 | 7.607649e-05 | 0.53153 | GF PASS; acc 0.532130; MC not run |
| `runs/v22h_BC_cat_012` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.950848e-05 | 1.871207e-05 | 6.822054e-05 | 0.56462 | GF PASS; acc 0.563614; MC not run |
| `runs/v22h_BC_cat_021` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.98107e-05 | 1.861986e-05 | 6.843056e-05 | 0.56462 | GF PASS; acc 0.563610; MC not run |
| `runs/v22h_BC_cat_102` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.883351e-05 | 1.873218e-05 | 6.75657e-05 | 0.56462 | GF PASS; acc 0.564576; MC not run |
| `runs/v22h_BC_cat_120` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.996566e-05 | 1.930294e-05 | 6.926861e-05 | 0.56095 | GF PASS; acc 0.560408; MC not run |
| `runs/v22h_BC_cat_201` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.950237e-05 | 1.951752e-05 | 6.90199e-05 | 0.55909 | GF PASS; acc 0.558661; MC not run |
| `runs/v22h_BC_cat_210` (regenerate) | BC cat | 135 | 45 | 2.923587e-19 | 4.747209e-05 | 1.889496e-05 | 6.636705e-05 | 0.56320 | GF PASS; acc 0.562384; MC not run |
| `runs/v22h_BC_catred_012` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.850833e-05 | 1.248976e-05 | 6.099808e-05 | 0.54940 | GF PASS; acc 0.549981; MC not run |
| `runs/v22h_BC_catred_0132` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.877316e-05 | 1.238335e-05 | 6.115651e-05 | 0.54940 | GF PASS; acc 0.548763; MC not run |
| `runs/v22h_BC_catred_021` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.850996e-05 | 1.247324e-05 | 6.09832e-05 | 0.54940 | GF PASS; acc 0.549646; MC not run |
| `runs/v22h_BC_catred_0231` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.550379e-05 | 1.290207e-05 | 5.840586e-05 | 0.54365 | GF PASS; acc 0.543448; MC not run |
| `runs/v22h_BC_catred_0312` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.587737e-05 | 1.275889e-05 | 5.863625e-05 | 0.54692 | GF PASS; acc 0.546674; MC not run |
| `runs/v22h_BC_catred_0321` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.587737e-05 | 1.276181e-05 | 5.863917e-05 | 0.54692 | GF PASS; acc 0.546668; MC not run |
| `runs/v22h_BC_catred_102` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.783153e-05 | 1.250262e-05 | 6.033415e-05 | 0.54830 | GF PASS; acc 0.547463; MC not run |
| `runs/v22h_BC_catred_1032` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.809636e-05 | 1.239468e-05 | 6.049104e-05 | 0.54830 | GF PASS; acc 0.547618; MC not run |
| `runs/v22h_BC_catred_120` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.868418e-05 | 1.283296e-05 | 6.151714e-05 | 0.54510 | GF PASS; acc 0.545576; MC not run |
| `runs/v22h_BC_catred_1230` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.74952e-05 | 1.277851e-05 | 6.027372e-05 | 0.54911 | GF PASS; acc 0.548679; MC not run |
| `runs/v22h_BC_catred_1302` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.809636e-05 | 1.240306e-05 | 6.049942e-05 | 0.54830 | GF PASS; acc 0.547677; MC not run |
| `runs/v22h_BC_catred_1320` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.970095e-05 | 1.28908e-05 | 6.259175e-05 | 0.54365 | GF PASS; acc 0.543299; MC not run |
| `runs/v22h_BC_catred_201` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.771316e-05 | 1.283346e-05 | 6.054662e-05 | 0.54438 | GF PASS; acc 0.544555; MC not run |
| `runs/v22h_BC_catred_2031` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.698379e-05 | 1.328579e-05 | 6.026959e-05 | 0.53761 | GF PASS; acc 0.537465; MC not run |
| `runs/v22h_BC_catred_210` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.624151e-05 | 1.27878e-05 | 5.902931e-05 | 0.54729 | GF PASS; acc 0.547320; MC not run |
| `runs/v22h_BC_catred_2130` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.749683e-05 | 1.277783e-05 | 6.027466e-05 | 0.54911 | GF PASS; acc 0.548998; MC not run |
| `runs/v22h_BC_catred_2301` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.495491e-05 | 1.301986e-05 | 5.797477e-05 | 0.54700 | GF PASS; acc 0.547240; MC not run |
| `runs/v22h_BC_catred_2310` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.554368e-05 | 1.306889e-05 | 5.861257e-05 | 0.54373 | GF PASS; acc 0.544240; MC not run |
| `runs/v22h_BC_catred_3012` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.689994e-05 | 1.26251e-05 | 5.952504e-05 | 0.54801 | GF PASS; acc 0.547399; MC not run |
| `runs/v22h_BC_catred_3021` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.689994e-05 | 1.262843e-05 | 5.952837e-05 | 0.54801 | GF PASS; acc 0.547409; MC not run |
| `runs/v22h_BC_catred_3102` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.617351e-05 | 1.26342e-05 | 5.880771e-05 | 0.54619 | GF PASS; acc 0.545241; MC not run |
| `runs/v22h_BC_catred_3120` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.696812e-05 | 1.306776e-05 | 6.003588e-05 | 0.54482 | GF PASS; acc 0.544619; MC not run |
| `runs/v22h_BC_catred_3201` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.720457e-05 | 1.321016e-05 | 6.041472e-05 | 0.54265 | GF PASS; acc 0.542144; MC not run |
| `runs/v22h_BC_catred_3210` (regenerate) | BC catred | 145 | 45 | 2.923587e-19 | 4.49059e-05 | 1.301648e-05 | 5.792237e-05 | 0.54700 | GF PASS; acc 0.547174; MC not run |
| [runs/v22h_BC_direct_012](runs/v22h_BC_direct_012.qasm) · [JSON](runs/v22h_BC_direct_012.json) · [receipt](runs/v22h_BC_direct_012.result.json) | BC direct | 129 | 45 | 2.923587e-19 | 4.077992e-05 | 1.798858e-05 | 5.876849e-05 | 0.56489 | GF PASS; acc 0.563926; MC not run |
| `runs/v22h_BC_direct_021` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.143639e-05 | 1.846521e-05 | 5.990161e-05 | 0.56040 | GF PASS; acc 0.560455; MC not run |
| `runs/v22h_BC_direct_102` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.094904e-05 | 1.888707e-05 | 5.983611e-05 | 0.55818 | GF PASS; acc 0.557612; MC not run |
| `runs/v22h_BC_direct_120` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.076261e-05 | 1.803559e-05 | 5.87982e-05 | 0.56376 | GF PASS; acc 0.564021; MC not run |
| `runs/v22h_BC_direct_201` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.126833e-05 | 1.790235e-05 | 5.917068e-05 | 0.56376 | GF PASS; acc 0.564021; MC not run |
| `runs/v22h_BC_direct_210` (regenerate) | BC direct | 129 | 45 | 2.923587e-19 | 4.122389e-05 | 1.791084e-05 | 5.913473e-05 | 0.56376 | GF PASS; acc 0.563011; MC not run |
| `runs/v22h_BC_flag_012` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.175296e-05 | 2.061035e-05 | 6.236332e-05 | 0.52735 | GF PASS; acc 0.527111; MC not run |
| `runs/v22h_BC_flag_021` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.249599e-05 | 2.121419e-05 | 6.371018e-05 | 0.52213 | GF PASS; acc 0.521567; MC not run |
| `runs/v22h_BC_flag_102` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.168104e-05 | 2.174142e-05 | 6.342246e-05 | 0.51903 | GF PASS; acc 0.519244; MC not run |
| `runs/v22h_BC_flag_120` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.169163e-05 | 2.06624e-05 | 6.235403e-05 | 0.52629 | GF PASS; acc 0.526485; MC not run |
| `runs/v22h_BC_flag_201` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.22319e-05 | 2.05407e-05 | 6.27726e-05 | 0.52629 | GF PASS; acc 0.526506; MC not run |
| `runs/v22h_BC_flag_210` (regenerate) | BC flag | 141 | 45 | 2.923587e-19 | 4.211676e-05 | 2.054874e-05 | 6.26655e-05 | 0.52629 | GF PASS; acc 0.526037; MC not run |
| `runs/v22h_BC_hybrid1_012` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.088493e-05 | 1.828605e-05 | 5.917098e-05 | 0.55721 | GF PASS; acc 0.556473; MC not run |
| `runs/v22h_BC_hybrid1_021` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.118656e-05 | 1.817172e-05 | 5.935828e-05 | 0.55721 | GF PASS; acc 0.556797; MC not run |
| `runs/v22h_BC_hybrid1_102` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.088493e-05 | 1.828605e-05 | 5.917098e-05 | 0.55721 | GF PASS; acc 0.556473; MC not run |
| `runs/v22h_BC_hybrid1_120` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.088493e-05 | 1.828605e-05 | 5.917098e-05 | 0.55721 | GF PASS; acc 0.556473; MC not run |
| `runs/v22h_BC_hybrid1_201` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.118656e-05 | 1.817172e-05 | 5.935828e-05 | 0.55721 | GF PASS; acc 0.556797; MC not run |
| `runs/v22h_BC_hybrid1_210` (regenerate) | BC hybrid1 | 127 | 45 | 2.923587e-19 | 4.118656e-05 | 1.817172e-05 | 5.935828e-05 | 0.55721 | GF PASS; acc 0.556797; MC not run |
| `runs/v22h_BC_hybrid2_012` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 4.005174e-05 | 1.734052e-05 | 5.739225e-05 | 0.56340 | GF PASS; acc 0.563603; MC not run |
| `runs/v22h_BC_hybrid2_021` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 4.005174e-05 | 1.734052e-05 | 5.739225e-05 | 0.56340 | GF PASS; acc 0.563603; MC not run |
| `runs/v22h_BC_hybrid2_102` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 4.005174e-05 | 1.734052e-05 | 5.739225e-05 | 0.56340 | GF PASS; acc 0.563603; MC not run |
| `runs/v22h_BC_hybrid2_120` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 4.005174e-05 | 1.734052e-05 | 5.739225e-05 | 0.56340 | GF PASS; acc 0.563603; MC not run |
| `runs/v22h_BC_hybrid2_201` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 4.005174e-05 | 1.734052e-05 | 5.739225e-05 | 0.56340 | GF PASS; acc 0.563603; MC not run |
| `runs/v22h_BC_hybrid2_210` (regenerate) | BC hybrid2 | 125 | 45 | 2.923587e-19 | 4.005174e-05 | 1.734052e-05 | 5.739225e-05 | 0.56340 | GF PASS; acc 0.563603; MC not run |
| [runs/v22h_BC_hybrid2t_012](runs/v22h_BC_hybrid2t_012.qasm) · [JSON](runs/v22h_BC_hybrid2t_012.json) · [receipt](runs/v22h_BC_hybrid2t_012.result.json) | BC hybrid2t | 123 | 45 | 2.923587e-19 | 4.122902e-05 | 1.802462e-05 | 5.925364e-05 | 0.55895 | GF PASS; acc 0.558206; MC not run |
| `runs/v22h_BC_redundant_012` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.868812e-05 | 1.37194e-05 | 5.240752e-05 | 0.55274 | GF PASS; acc 0.552346; MC not run |
| `runs/v22h_BC_redundant_0132` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.902306e-05 | 1.464481e-05 | 5.366787e-05 | 0.54612 | GF PASS; acc 0.545900; MC not run |
| `runs/v22h_BC_redundant_021` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.86873e-05 | 1.372416e-05 | 5.241145e-05 | 0.54835 | GF PASS; acc 0.548053; MC not run |
| `runs/v22h_BC_redundant_0231` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.895079e-05 | 1.405802e-05 | 5.300881e-05 | 0.54719 | GF PASS; acc 0.546621; MC not run |
| `runs/v22h_BC_redundant_0312` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.910751e-05 | 1.437304e-05 | 5.348055e-05 | 0.55041 | GF PASS; acc 0.550930; MC not run |
| `runs/v22h_BC_redundant_0321` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.928306e-05 | 1.453168e-05 | 5.381474e-05 | 0.54496 | GF PASS; acc 0.544540; MC not run |
| `runs/v22h_BC_redundant_102` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.888507e-05 | 1.391572e-05 | 5.280079e-05 | 0.54617 | GF PASS; acc 0.546017; MC not run |
| `runs/v22h_BC_redundant_1032` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.903195e-05 | 1.464665e-05 | 5.36786e-05 | 0.54612 | GF PASS; acc 0.545546; MC not run |
| `runs/v22h_BC_redundant_120` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.895425e-05 | 1.359014e-05 | 5.25444e-05 | 0.55163 | GF PASS; acc 0.551348; MC not run |
| `runs/v22h_BC_redundant_1230` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.904291e-05 | 1.360387e-05 | 5.264677e-05 | 0.55163 | GF PASS; acc 0.551044; MC not run |
| `runs/v22h_BC_redundant_1302` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.89446e-05 | 1.447695e-05 | 5.342155e-05 | 0.54939 | GF PASS; acc 0.549740; MC not run |
| `runs/v22h_BC_redundant_1320` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.900623e-05 | 1.424363e-05 | 5.324986e-05 | 0.54501 | GF PASS; acc 0.544349; MC not run |
| [runs/v22h_BC_redundant_201](runs/v22h_BC_redundant_201.qasm) · [JSON](runs/v22h_BC_redundant_201.json) · [receipt](runs/v22h_BC_redundant_201.result.json) | BC redundant | 137 | 45 | 2.923587e-19 | 3.869701e-05 | 1.358696e-05 | 5.228397e-05 | 0.55163 | GF PASS; acc 0.550802; MC not run |
| `runs/v22h_BC_redundant_2031` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.896051e-05 | 1.39432e-05 | 5.29037e-05 | 0.54827 | GF PASS; acc 0.548151; MC not run |
| `runs/v22h_BC_redundant_210` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.895425e-05 | 1.359152e-05 | 5.254577e-05 | 0.55164 | GF PASS; acc 0.551266; MC not run |
| `runs/v22h_BC_redundant_2130` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.904291e-05 | 1.360558e-05 | 5.264849e-05 | 0.55163 | GF PASS; acc 0.550425; MC not run |
| `runs/v22h_BC_redundant_2301` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.890963e-05 | 1.376522e-05 | 5.267486e-05 | 0.55267 | GF PASS; acc 0.551985; MC not run |
| `runs/v22h_BC_redundant_2310` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.90942e-05 | 1.380487e-05 | 5.289906e-05 | 0.54936 | GF PASS; acc 0.548602; MC not run |
| `runs/v22h_BC_redundant_3012` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.902015e-05 | 1.41825e-05 | 5.320265e-05 | 0.55593 | GF PASS; acc 0.555351; MC not run |
| `runs/v22h_BC_redundant_3021` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.919592e-05 | 1.435108e-05 | 5.3547e-05 | 0.54822 | GF PASS; acc 0.547284; MC not run |
| `runs/v22h_BC_redundant_3102` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.954465e-05 | 1.470718e-05 | 5.425184e-05 | 0.54496 | GF PASS; acc 0.544504; MC not run |
| `runs/v22h_BC_redundant_3120` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.901956e-05 | 1.408138e-05 | 5.310094e-05 | 0.55041 | GF PASS; acc 0.550167; MC not run |
| `runs/v22h_BC_redundant_3201` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.91157e-05 | 1.408483e-05 | 5.320053e-05 | 0.54603 | GF PASS; acc 0.545414; MC not run |
| `runs/v22h_BC_redundant_3210` (regenerate) | BC redundant | 137 | 45 | 2.923587e-19 | 3.917804e-05 | 1.408564e-05 | 5.326368e-05 | 0.54603 | GF PASS; acc 0.545501; MC not run |
| `runs/v22h_BC_redundant_m3_0123` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.928806e-05 | 1.414619e-05 | 5.343425e-05 | 0.56276 | GF PASS; acc 0.562819; MC not run |
| `runs/v22h_BC_redundant_m3_0132` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.961571e-05 | 1.523371e-05 | 5.484941e-05 | 0.55349 | GF PASS; acc 0.553207; MC not run |
| `runs/v22h_BC_redundant_m3_0213` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.961648e-05 | 1.433519e-05 | 5.395166e-05 | 0.55828 | GF PASS; acc 0.557869; MC not run |
| `runs/v22h_BC_redundant_m3_0231` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.008937e-05 | 1.541958e-05 | 5.550895e-05 | 0.54793 | GF PASS; acc 0.547396; MC not run |
| `runs/v22h_BC_redundant_m3_0312` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.978751e-05 | 1.541197e-05 | 5.519948e-05 | 0.54946 | GF PASS; acc 0.548552; MC not run |
| `runs/v22h_BC_redundant_m3_0321` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.995592e-05 | 1.530589e-05 | 5.526182e-05 | 0.54837 | GF PASS; acc 0.548043; MC not run |
| `runs/v22h_BC_redundant_m3_1023` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.948584e-05 | 1.433215e-05 | 5.381799e-05 | 0.55606 | GF PASS; acc 0.556805; MC not run |
| `runs/v22h_BC_redundant_m3_1032` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.011219e-05 | 1.542444e-05 | 5.553663e-05 | 0.54800 | GF PASS; acc 0.547521; MC not run |
| `runs/v22h_BC_redundant_m3_1203` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.962981e-05 | 1.445233e-05 | 5.408214e-05 | 0.55940 | GF PASS; acc 0.558569; MC not run |
| `runs/v22h_BC_redundant_m3_1230` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.962981e-05 | 1.446199e-05 | 5.40918e-05 | 0.55940 | GF PASS; acc 0.559260; MC not run |
| `runs/v22h_BC_redundant_m3_1302` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.981349e-05 | 1.539575e-05 | 5.520924e-05 | 0.55129 | GF PASS; acc 0.550208; MC not run |
| `runs/v22h_BC_redundant_m3_1320` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.980706e-05 | 1.503331e-05 | 5.484037e-05 | 0.55054 | GF PASS; acc 0.550331; MC not run |
| `runs/v22h_BC_redundant_m3_2013` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.019787e-05 | 1.500759e-05 | 5.520546e-05 | 0.56165 | GF PASS; acc 0.560793; MC not run |
| `runs/v22h_BC_redundant_m3_2031` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.082259e-05 | 1.589786e-05 | 5.672045e-05 | 0.54902 | GF PASS; acc 0.548819; MC not run |
| `runs/v22h_BC_redundant_m3_2103` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.033787e-05 | 1.507324e-05 | 5.541111e-05 | 0.55606 | GF PASS; acc 0.554741; MC not run |
| `runs/v22h_BC_redundant_m3_2130` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.012676e-05 | 1.505116e-05 | 5.517792e-05 | 0.55941 | GF PASS; acc 0.559189; MC not run |
| `runs/v22h_BC_redundant_m3_2301` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.022389e-05 | 1.532937e-05 | 5.555326e-05 | 0.55786 | GF PASS; acc 0.557393; MC not run |
| `runs/v22h_BC_redundant_m3_2310` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.04633e-05 | 1.562126e-05 | 5.608455e-05 | 0.55048 | GF PASS; acc 0.550623; MC not run |
| `runs/v22h_BC_redundant_m3_3012` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.961126e-05 | 1.507951e-05 | 5.469078e-05 | 0.55608 | GF PASS; acc 0.555486; MC not run |
| `runs/v22h_BC_redundant_m3_3021` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.995592e-05 | 1.530573e-05 | 5.526166e-05 | 0.54837 | GF PASS; acc 0.547481; MC not run |
| `runs/v22h_BC_redundant_m3_3102` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.992951e-05 | 1.573465e-05 | 5.566416e-05 | 0.54438 | GF PASS; acc 0.544410; MC not run |
| `runs/v22h_BC_redundant_m3_3120` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 3.980179e-05 | 1.503721e-05 | 5.4839e-05 | 0.54982 | GF PASS; acc 0.549061; MC not run |
| `runs/v22h_BC_redundant_m3_3201` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.00764e-05 | 1.527043e-05 | 5.534682e-05 | 0.54982 | GF PASS; acc 0.549504; MC not run |
| `runs/v22h_BC_redundant_m3_3210` (regenerate) | BC redundant mask=3 | 137 | 45 | 2.923587e-19 | 4.012985e-05 | 1.527092e-05 | 5.540076e-05 | 0.54982 | GF PASS; acc 0.549896; MC not run |
| `runs/v22h_BC_redundant_m5_0123` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.851532e-05 | 1.458164e-05 | 5.309696e-05 | 0.56276 | GF PASS; acc 0.562424; MC not run |
| `runs/v22h_BC_redundant_m5_0132` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 4.085713e-05 | 1.681683e-05 | 5.767396e-05 | 0.54144 | GF PASS; acc 0.540977; MC not run |
| `runs/v22h_BC_redundant_m5_0213` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.875532e-05 | 1.46495e-05 | 5.340482e-05 | 0.55606 | GF PASS; acc 0.555394; MC not run |
| `runs/v22h_BC_redundant_m5_0231` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.913488e-05 | 1.539008e-05 | 5.452497e-05 | 0.54909 | GF PASS; acc 0.548463; MC not run |
| `runs/v22h_BC_redundant_m5_0312` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.972478e-05 | 1.56972e-05 | 5.542199e-05 | 0.55166 | GF PASS; acc 0.551315; MC not run |
| `runs/v22h_BC_redundant_m5_0321` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 4.01222e-05 | 1.599197e-05 | 5.611417e-05 | 0.54620 | GF PASS; acc 0.544629; MC not run |
| `runs/v22h_BC_redundant_m5_1023` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.88931e-05 | 1.56349e-05 | 5.4528e-05 | 0.55607 | GF PASS; acc 0.555161; MC not run |
| `runs/v22h_BC_redundant_m5_1032` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 4.125811e-05 | 1.741604e-05 | 5.867415e-05 | 0.54145 | GF PASS; acc 0.541407; MC not run |
| `runs/v22h_BC_redundant_m5_1203` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.869088e-05 | 1.507602e-05 | 5.37669e-05 | 0.55940 | GF PASS; acc 0.559143; MC not run |
| `runs/v22h_BC_redundant_m5_1230` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.869088e-05 | 1.50772e-05 | 5.376808e-05 | 0.55940 | GF PASS; acc 0.559145; MC not run |
| `runs/v22h_BC_redundant_m5_1302` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.990733e-05 | 1.67652e-05 | 5.667253e-05 | 0.54795 | GF PASS; acc 0.547328; MC not run |
| `runs/v22h_BC_redundant_m5_1320` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.999994e-05 | 1.668708e-05 | 5.668702e-05 | 0.54178 | GF PASS; acc 0.542212; MC not run |
| `runs/v22h_BC_redundant_m5_2013` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.894421e-05 | 1.454213e-05 | 5.348634e-05 | 0.55605 | GF PASS; acc 0.555755; MC not run |
| `runs/v22h_BC_redundant_m5_2031` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.957971e-05 | 1.514008e-05 | 5.471979e-05 | 0.55348 | GF PASS; acc 0.552643; MC not run |
| `runs/v22h_BC_redundant_m5_2103` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.898865e-05 | 1.481402e-05 | 5.380268e-05 | 0.55606 | GF PASS; acc 0.555644; MC not run |
| `runs/v22h_BC_redundant_m5_2130` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.898865e-05 | 1.481557e-05 | 5.380422e-05 | 0.55606 | GF PASS; acc 0.555677; MC not run |
| `runs/v22h_BC_redundant_m5_2301` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.895852e-05 | 1.481637e-05 | 5.37749e-05 | 0.55792 | GF PASS; acc 0.557119; MC not run |
| `runs/v22h_BC_redundant_m5_2310` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.90515e-05 | 1.512955e-05 | 5.418105e-05 | 0.54944 | GF PASS; acc 0.548589; MC not run |
| `runs/v22h_BC_redundant_m5_3012` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.901571e-05 | 1.537174e-05 | 5.438745e-05 | 0.55608 | GF PASS; acc 0.555473; MC not run |
| `runs/v22h_BC_redundant_m5_3021` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.941358e-05 | 1.565514e-05 | 5.506873e-05 | 0.55056 | GF PASS; acc 0.549509; MC not run |
| `runs/v22h_BC_redundant_m5_3102` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.921933e-05 | 1.632735e-05 | 5.554668e-05 | 0.54655 | GF PASS; acc 0.545990; MC not run |
| `runs/v22h_BC_redundant_m5_3120` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.901067e-05 | 1.559331e-05 | 5.460399e-05 | 0.54982 | GF PASS; acc 0.549232; MC not run |
| `runs/v22h_BC_redundant_m5_3201` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.922682e-05 | 1.52582e-05 | 5.448501e-05 | 0.54654 | GF PASS; acc 0.546535; MC not run |
| `runs/v22h_BC_redundant_m5_3210` (regenerate) | BC redundant mask=5 | 137 | 45 | 2.923587e-19 | 3.914249e-05 | 1.528264e-05 | 5.442512e-05 | 0.54546 | GF PASS; acc 0.544905; MC not run |
| `runs/v22h_BC_redundant_m6_0123` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.995384e-05 | 1.504466e-05 | 5.49985e-05 | 0.56277 | GF PASS; acc 0.561879; MC not run |
| `runs/v22h_BC_redundant_m6_0132` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.255269e-05 | 1.737988e-05 | 5.993257e-05 | 0.54181 | GF PASS; acc 0.541538; MC not run |
| `runs/v22h_BC_redundant_m6_0213` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.043091e-05 | 1.551915e-05 | 5.595006e-05 | 0.55607 | GF PASS; acc 0.555162; MC not run |
| `runs/v22h_BC_redundant_m6_0231` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.043091e-05 | 1.551879e-05 | 5.59497e-05 | 0.55607 | GF PASS; acc 0.555126; MC not run |
| `runs/v22h_BC_redundant_m6_0312` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.083533e-05 | 1.645173e-05 | 5.728706e-05 | 0.54940 | GF PASS; acc 0.549602; MC not run |
| `runs/v22h_BC_redundant_m6_0321` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.109954e-05 | 1.675915e-05 | 5.785868e-05 | 0.54215 | GF PASS; acc 0.541798; MC not run |
| `runs/v22h_BC_redundant_m6_1023` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.998741e-05 | 1.480731e-05 | 5.479472e-05 | 0.55606 | GF PASS; acc 0.555142; MC not run |
| `runs/v22h_BC_redundant_m6_1032` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.169684e-05 | 1.679597e-05 | 5.849281e-05 | 0.54072 | GF PASS; acc 0.540871; MC not run |
| `runs/v22h_BC_redundant_m6_1203` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.990543e-05 | 1.451417e-05 | 5.441959e-05 | 0.55940 | GF PASS; acc 0.559667; MC not run |
| `runs/v22h_BC_redundant_m6_1230` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.002308e-05 | 1.510469e-05 | 5.512777e-05 | 0.55681 | GF PASS; acc 0.556402; MC not run |
| `runs/v22h_BC_redundant_m6_1302` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.102738e-05 | 1.631945e-05 | 5.734683e-05 | 0.54331 | GF PASS; acc 0.543455; MC not run |
| `runs/v22h_BC_redundant_m6_1320` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.104095e-05 | 1.59945e-05 | 5.703545e-05 | 0.54656 | GF PASS; acc 0.545862; MC not run |
| `runs/v22h_BC_redundant_m6_2013` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.023186e-05 | 1.481545e-05 | 5.504731e-05 | 0.55606 | GF PASS; acc 0.555830; MC not run |
| `runs/v22h_BC_redundant_m6_2031` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.023186e-05 | 1.481493e-05 | 5.504679e-05 | 0.55606 | GF PASS; acc 0.555838; MC not run |
| `runs/v22h_BC_redundant_m6_2103` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.016098e-05 | 1.454901e-05 | 5.470999e-05 | 0.55606 | GF PASS; acc 0.555912; MC not run |
| `runs/v22h_BC_redundant_m6_2130` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.038919e-05 | 1.514197e-05 | 5.553116e-05 | 0.55348 | GF PASS; acc 0.552665; MC not run |
| `runs/v22h_BC_redundant_m6_2301` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.987805e-05 | 1.508185e-05 | 5.49599e-05 | 0.55385 | GF PASS; acc 0.552965; MC not run |
| `runs/v22h_BC_redundant_m6_2310` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.976753e-05 | 1.481523e-05 | 5.458276e-05 | 0.55792 | GF PASS; acc 0.557168; MC not run |
| `runs/v22h_BC_redundant_m6_3012` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.008576e-05 | 1.572227e-05 | 5.580803e-05 | 0.55092 | GF PASS; acc 0.550756; MC not run |
| `runs/v22h_BC_redundant_m6_3021` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.035031e-05 | 1.602166e-05 | 5.637197e-05 | 0.54365 | GF PASS; acc 0.544248; MC not run |
| `runs/v22h_BC_redundant_m6_3102` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.018599e-05 | 1.598012e-05 | 5.616611e-05 | 0.54765 | GF PASS; acc 0.547490; MC not run |
| `runs/v22h_BC_redundant_m6_3120` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 3.994401e-05 | 1.535829e-05 | 5.53023e-05 | 0.55202 | GF PASS; acc 0.551381; MC not run |
| `runs/v22h_BC_redundant_m6_3201` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.005348e-05 | 1.53752e-05 | 5.542868e-05 | 0.54582 | GF PASS; acc 0.545212; MC not run |
| `runs/v22h_BC_redundant_m6_3210` (regenerate) | BC redundant mask=6 | 137 | 45 | 2.923587e-19 | 4.012015e-05 | 1.535654e-05 | 5.547669e-05 | 0.54691 | GF PASS; acc 0.546634; MC not run |
| `runs/v22h_BC_seq_012` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.306473e-05 | 2.479176e-05 | 6.785649e-05 | 0.51358 | GF PASS; acc 0.513428; MC not run |
| `runs/v22h_BC_seq_021` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.407157e-05 | 2.434217e-05 | 6.841374e-05 | 0.51358 | GF PASS; acc 0.513554; MC not run |
| `runs/v22h_BC_seq_102` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.102719e-05 | 2.48135e-05 | 6.584069e-05 | 0.51358 | GF PASS; acc 0.512825; MC not run |
| `runs/v22h_BC_seq_120` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.278845e-05 | 2.456411e-05 | 6.735256e-05 | 0.51256 | GF PASS; acc 0.512972; MC not run |
| `runs/v22h_BC_seq_201` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.425718e-05 | 2.398554e-05 | 6.824272e-05 | 0.51256 | GF PASS; acc 0.512882; MC not run |
| `runs/v22h_BC_seq_210` (regenerate) | BC seq | 129 | 45 | 2.923587e-19 | 4.483347e-05 | 2.403211e-05 | 6.886558e-05 | 0.51257 | GF PASS; acc 0.512350; MC not run |
| `runs/v22h_B_cat13_012` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 3.987108e-05 | 1.57546e-05 | 5.562568e-05 | 0.58058 | GF PASS; acc 0.579821; MC not run |
| `runs/v22h_B_cat13_021` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 4.0204e-05 | 1.598154e-05 | 5.618554e-05 | 0.57826 | GF PASS; acc 0.576895; MC not run |
| `runs/v22h_B_cat13_102` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 3.98112e-05 | 1.617973e-05 | 5.599093e-05 | 0.57711 | GF PASS; acc 0.576818; MC not run |
| `runs/v22h_B_cat13_120` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 3.985787e-05 | 1.577527e-05 | 5.563314e-05 | 0.57999 | GF PASS; acc 0.579887; MC not run |
| `runs/v22h_B_cat13_201` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 4.011985e-05 | 1.570909e-05 | 5.582894e-05 | 0.57999 | GF PASS; acc 0.579902; MC not run |
| `runs/v22h_B_cat13_210` (regenerate) | B cat13 | 129 | 45 | 2.923587e-19 | 4.009307e-05 | 1.571173e-05 | 5.58048e-05 | 0.57999 | GF PASS; acc 0.579926; MC not run |
| `runs/v22h_B_cat13red_012` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.845805e-05 | 1.291753e-05 | 5.137557e-05 | 0.56928 | GF PASS; acc 0.569442; MC not run |
| `runs/v22h_B_cat13red_0132` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.835606e-05 | 1.283548e-05 | 5.119154e-05 | 0.56849 | GF PASS; acc 0.567705; MC not run |
| `runs/v22h_B_cat13red_021` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.845722e-05 | 1.291339e-05 | 5.137061e-05 | 0.56702 | GF PASS; acc 0.566145; MC not run |
| `runs/v22h_B_cat13red_0231` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.843506e-05 | 1.273684e-05 | 5.11719e-05 | 0.56604 | GF PASS; acc 0.564917; MC not run |
| `runs/v22h_B_cat13red_0312` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.839162e-05 | 1.259328e-05 | 5.09849e-05 | 0.56769 | GF PASS; acc 0.566703; MC not run |
| `runs/v22h_B_cat13red_0321` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.839162e-05 | 1.258491e-05 | 5.097653e-05 | 0.56769 | GF PASS; acc 0.566303; MC not run |
| `runs/v22h_B_cat13red_102` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.848389e-05 | 1.300076e-05 | 5.148464e-05 | 0.56589 | GF PASS; acc 0.565259; MC not run |
| `runs/v22h_B_cat13red_1032` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.836051e-05 | 1.283537e-05 | 5.119588e-05 | 0.56848 | GF PASS; acc 0.567478; MC not run |
| `runs/v22h_B_cat13red_120` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.858445e-05 | 1.285505e-05 | 5.14395e-05 | 0.56871 | GF PASS; acc 0.569028; MC not run |
| `runs/v22h_B_cat13red_1230` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.862877e-05 | 1.286551e-05 | 5.149428e-05 | 0.56795 | GF PASS; acc 0.567452; MC not run |
| `runs/v22h_B_cat13red_1302` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.836051e-05 | 1.29159e-05 | 5.127641e-05 | 0.56641 | GF PASS; acc 0.565816; MC not run |
| `runs/v22h_B_cat13red_1320` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.842922e-05 | 1.278692e-05 | 5.121614e-05 | 0.56754 | GF PASS; acc 0.566761; MC not run |
| `runs/v22h_B_cat13red_201` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.846027e-05 | 1.285317e-05 | 5.131344e-05 | 0.56871 | GF PASS; acc 0.568140; MC not run |
| `runs/v22h_B_cat13red_2031` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.843811e-05 | 1.267561e-05 | 5.111372e-05 | 0.56772 | GF PASS; acc 0.566479; MC not run |
| `runs/v22h_B_cat13red_210` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.858445e-05 | 1.285619e-05 | 5.144063e-05 | 0.56871 | GF PASS; acc 0.567969; MC not run |
| `runs/v22h_B_cat13red_2130` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.862877e-05 | 1.286695e-05 | 5.149572e-05 | 0.56795 | GF PASS; acc 0.567524; MC not run |
| `runs/v22h_B_cat13red_2301` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.851793e-05 | 1.26803e-05 | 5.119823e-05 | 0.56735 | GF PASS; acc 0.566819; MC not run |
| `runs/v22h_B_cat13red_2310` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.858886e-05 | 1.268232e-05 | 5.127118e-05 | 0.56735 | GF PASS; acc 0.567120; MC not run |
| `runs/v22h_B_cat13red_3012` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.839162e-05 | 1.258975e-05 | 5.098136e-05 | 0.56769 | GF PASS; acc 0.567187; MC not run |
| `runs/v22h_B_cat13red_3021` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.839162e-05 | 1.259733e-05 | 5.098894e-05 | 0.56543 | GF PASS; acc 0.564443; MC not run |
| `runs/v22h_B_cat13red_3102` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.838273e-05 | 1.267335e-05 | 5.105608e-05 | 0.56430 | GF PASS; acc 0.563947; MC not run |
| `runs/v22h_B_cat13red_3120` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.842922e-05 | 1.253342e-05 | 5.096264e-05 | 0.56712 | GF PASS; acc 0.566127; MC not run |
| `runs/v22h_B_cat13red_3201` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.839384e-05 | 1.252442e-05 | 5.091826e-05 | 0.56712 | GF PASS; acc 0.566117; MC not run |
| `runs/v22h_B_cat13red_3210` (regenerate) | B cat13red | 134 | 45 | 2.923587e-19 | 3.846477e-05 | 1.252559e-05 | 5.099037e-05 | 0.56712 | GF PASS; acc 0.566435; MC not run |
| `runs/v22h_B_cat3_012` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.070913e-05 | 1.668701e-05 | 5.739614e-05 | 0.57617 | GF PASS; acc 0.575404; MC not run |
| `runs/v22h_B_cat3_021` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.083357e-05 | 1.664478e-05 | 5.747835e-05 | 0.57617 | GF PASS; acc 0.575409; MC not run |
| `runs/v22h_B_cat3_102` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.037159e-05 | 1.6692e-05 | 5.706359e-05 | 0.57617 | GF PASS; acc 0.575381; MC not run |
| `runs/v22h_B_cat3_120` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.060252e-05 | 1.689394e-05 | 5.749646e-05 | 0.57387 | GF PASS; acc 0.572826; MC not run |
| `runs/v22h_B_cat3_201` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.101117e-05 | 1.684283e-05 | 5.7854e-05 | 0.57387 | GF PASS; acc 0.572837; MC not run |
| `runs/v22h_B_cat3_210` (regenerate) | B cat3 | 132 | 45 | 2.923587e-19 | 4.076246e-05 | 1.684942e-05 | 5.761188e-05 | 0.57387 | GF PASS; acc 0.572825; MC not run |
| `runs/v22h_B_cat3red_0123` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.858273e-05 | 1.240631e-05 | 5.098904e-05 | 0.56635 | GF PASS; acc 0.565984; MC not run |
| `runs/v22h_B_cat3red_0132` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.861822e-05 | 1.245924e-05 | 5.107746e-05 | 0.56450 | GF PASS; acc 0.563782; MC not run |
| `runs/v22h_B_cat3red_0213` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.858273e-05 | 1.240019e-05 | 5.098291e-05 | 0.56635 | GF PASS; acc 0.565972; MC not run |
| `runs/v22h_B_cat3red_0231` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.86691e-05 | 1.262689e-05 | 5.129599e-05 | 0.56001 | GF PASS; acc 0.559818; MC not run |
| `runs/v22h_B_cat3red_0312` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.871796e-05 | 1.266668e-05 | 5.138464e-05 | 0.56154 | GF PASS; acc 0.560682; MC not run |
| `runs/v22h_B_cat3red_0321` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.871796e-05 | 1.266838e-05 | 5.138634e-05 | 0.56154 | GF PASS; acc 0.560707; MC not run |
| `runs/v22h_B_cat3red_1023` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.858273e-05 | 1.241114e-05 | 5.099387e-05 | 0.56578 | GF PASS; acc 0.565202; MC not run |
| `runs/v22h_B_cat3red_1032` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.861822e-05 | 1.246341e-05 | 5.108163e-05 | 0.56394 | GF PASS; acc 0.563667; MC not run |
| `runs/v22h_B_cat3red_1203` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.863606e-05 | 1.242355e-05 | 5.105961e-05 | 0.56352 | GF PASS; acc 0.563517; MC not run |
| `runs/v22h_B_cat3red_1230` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.863606e-05 | 1.242105e-05 | 5.105711e-05 | 0.56352 | GF PASS; acc 0.563540; MC not run |
| `runs/v22h_B_cat3red_1302` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.861822e-05 | 1.245399e-05 | 5.107221e-05 | 0.56563 | GF PASS; acc 0.565371; MC not run |
| `runs/v22h_B_cat3red_1320` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.866255e-05 | 1.253704e-05 | 5.119959e-05 | 0.56187 | GF PASS; acc 0.561343; MC not run |
| `runs/v22h_B_cat3red_2013` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.858273e-05 | 1.240681e-05 | 5.098954e-05 | 0.56578 | GF PASS; acc 0.565808; MC not run |
| `runs/v22h_B_cat3red_2031` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.86691e-05 | 1.2645e-05 | 5.13141e-05 | 0.55778 | GF PASS; acc 0.557916; MC not run |
| `runs/v22h_B_cat3red_2103` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.863606e-05 | 1.242542e-05 | 5.106148e-05 | 0.56352 | GF PASS; acc 0.563524; MC not run |
| `runs/v22h_B_cat3red_2130` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.863606e-05 | 1.242327e-05 | 5.105933e-05 | 0.56352 | GF PASS; acc 0.563535; MC not run |
| `runs/v22h_B_cat3red_2301` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.866039e-05 | 1.255163e-05 | 5.121202e-05 | 0.56169 | GF PASS; acc 0.560822; MC not run |
| `runs/v22h_B_cat3red_2310` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.861606e-05 | 1.256751e-05 | 5.118357e-05 | 0.55908 | GF PASS; acc 0.558862; MC not run |
| `runs/v22h_B_cat3red_3012` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.867369e-05 | 1.257143e-05 | 5.124512e-05 | 0.56548 | GF PASS; acc 0.564395; MC not run |
| `runs/v22h_B_cat3red_3021` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.867369e-05 | 1.25731e-05 | 5.124679e-05 | 0.56548 | GF PASS; acc 0.564391; MC not run |
| `runs/v22h_B_cat3red_3102` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.859381e-05 | 1.25835e-05 | 5.117731e-05 | 0.56285 | GF PASS; acc 0.562648; MC not run |
| `runs/v22h_B_cat3red_3120` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.863813e-05 | 1.265726e-05 | 5.12954e-05 | 0.56079 | GF PASS; acc 0.560483; MC not run |
| `runs/v22h_B_cat3red_3201` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.871802e-05 | 1.263506e-05 | 5.135308e-05 | 0.56341 | GF PASS; acc 0.563249; MC not run |
| `runs/v22h_B_cat3red_3210` (regenerate) | B cat3red | 138 | 45 | 2.923587e-19 | 3.867369e-05 | 1.264918e-05 | 5.132287e-05 | 0.56079 | GF PASS; acc 0.560478; MC not run |
| `runs/v22h_B_cat3reusered_0123` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.895218e-05 | 1.447262e-05 | 5.34248e-05 | 0.51846 | GF PASS; acc 0.517283; MC not run |
| `runs/v22h_B_cat3reusered_0132` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.885461e-05 | 1.466656e-05 | 5.352117e-05 | 0.51901 | GF PASS; acc 0.518747; MC not run |
| `runs/v22h_B_cat3reusered_0213` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.895218e-05 | 1.435693e-05 | 5.330911e-05 | 0.51846 | GF PASS; acc 0.518583; MC not run |
| `runs/v22h_B_cat3reusered_0231` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.908232e-05 | 1.443994e-05 | 5.352225e-05 | 0.51901 | GF PASS; acc 0.519117; MC not run |
| `runs/v22h_B_cat3reusered_0312` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.937253e-05 | 1.476592e-05 | 5.413845e-05 | 0.51956 | GF PASS; acc 0.519363; MC not run |
| `runs/v22h_B_cat3reusered_0321` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.96376e-05 | 1.46453e-05 | 5.42829e-05 | 0.51956 | GF PASS; acc 0.518903; MC not run |
| `runs/v22h_B_cat3reusered_1023` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.895218e-05 | 1.447464e-05 | 5.342683e-05 | 0.51847 | GF PASS; acc 0.518627; MC not run |
| `runs/v22h_B_cat3reusered_1032` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.885461e-05 | 1.466842e-05 | 5.352303e-05 | 0.51901 | GF PASS; acc 0.518512; MC not run |
| `runs/v22h_B_cat3reusered_1203` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.973292e-05 | 1.439191e-05 | 5.412483e-05 | 0.51847 | GF PASS; acc 0.517520; MC not run |
| `runs/v22h_B_cat3reusered_1230` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.999835e-05 | 1.44368e-05 | 5.443515e-05 | 0.51846 | GF PASS; acc 0.518282; MC not run |
| `runs/v22h_B_cat3reusered_1302` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.885461e-05 | 1.470585e-05 | 5.356046e-05 | 0.51901 | GF PASS; acc 0.518366; MC not run |
| `runs/v22h_B_cat3reusered_1320` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.925275e-05 | 1.459672e-05 | 5.384947e-05 | 0.51901 | GF PASS; acc 0.518359; MC not run |
| `runs/v22h_B_cat3reusered_2013` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.895218e-05 | 1.436169e-05 | 5.331387e-05 | 0.51847 | GF PASS; acc 0.517829; MC not run |
| `runs/v22h_B_cat3reusered_2031` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.908232e-05 | 1.444413e-05 | 5.352645e-05 | 0.51901 | GF PASS; acc 0.519195; MC not run |
| `runs/v22h_B_cat3reusered_2103` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.973292e-05 | 1.439463e-05 | 5.412756e-05 | 0.51847 | GF PASS; acc 0.517525; MC not run |
| `runs/v22h_B_cat3reusered_2130` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.999835e-05 | 1.44394e-05 | 5.443775e-05 | 0.51846 | GF PASS; acc 0.518304; MC not run |
| `runs/v22h_B_cat3reusered_2301` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.960281e-05 | 1.446806e-05 | 5.407087e-05 | 0.51901 | GF PASS; acc 0.518386; MC not run |
| `runs/v22h_B_cat3reusered_2310` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.973588e-05 | 1.447902e-05 | 5.421489e-05 | 0.51901 | GF PASS; acc 0.519031; MC not run |
| `runs/v22h_B_cat3reusered_3012` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.937253e-05 | 1.474387e-05 | 5.411641e-05 | 0.51955 | GF PASS; acc 0.519187; MC not run |
| `runs/v22h_B_cat3reusered_3021` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.96376e-05 | 1.462328e-05 | 5.426089e-05 | 0.51955 | GF PASS; acc 0.519524; MC not run |
| `runs/v22h_B_cat3reusered_3102` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.885239e-05 | 1.473093e-05 | 5.358332e-05 | 0.51956 | GF PASS; acc 0.518979; MC not run |
| `runs/v22h_B_cat3reusered_3120` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.925053e-05 | 1.462167e-05 | 5.38722e-05 | 0.51956 | GF PASS; acc 0.519734; MC not run |
| `runs/v22h_B_cat3reusered_3201` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.96376e-05 | 1.448175e-05 | 5.411935e-05 | 0.51956 | GF PASS; acc 0.518872; MC not run |
| `runs/v22h_B_cat3reusered_3210` (regenerate) | B cat3reusered | 138 | 45 | 2.923587e-19 | 3.977067e-05 | 1.449258e-05 | 5.426325e-05 | 0.51956 | GF PASS; acc 0.519503; MC not run |
| `runs/v22h_B_cat3spinered_0123` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.891446e-05 | 1.439908e-05 | 5.331354e-05 | 0.51956 | GF PASS; acc 0.519575; MC not run |
| `runs/v22h_B_cat3spinered_0132` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.878175e-05 | 1.45541e-05 | 5.333585e-05 | 0.51956 | GF PASS; acc 0.519234; MC not run |
| `runs/v22h_B_cat3spinered_0213` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.891224e-05 | 1.428613e-05 | 5.319837e-05 | 0.51956 | GF PASS; acc 0.518702; MC not run |
| `runs/v22h_B_cat3spinered_0231` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.904495e-05 | 1.431832e-05 | 5.336327e-05 | 0.51956 | GF PASS; acc 0.519719; MC not run |
| `runs/v22h_B_cat3spinered_0312` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.928447e-05 | 1.460284e-05 | 5.388731e-05 | 0.51956 | GF PASS; acc 0.519520; MC not run |
| `runs/v22h_B_cat3spinered_0321` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.954767e-05 | 1.447941e-05 | 5.402708e-05 | 0.51956 | GF PASS; acc 0.518989; MC not run |
| `runs/v22h_B_cat3spinered_1023` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.891446e-05 | 1.440073e-05 | 5.33152e-05 | 0.51956 | GF PASS; acc 0.519224; MC not run |
| `runs/v22h_B_cat3spinered_1032` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.878175e-05 | 1.455512e-05 | 5.333687e-05 | 0.51956 | GF PASS; acc 0.519589; MC not run |
| `runs/v22h_B_cat3spinered_1203` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.966854e-05 | 1.432101e-05 | 5.398955e-05 | 0.51956 | GF PASS; acc 0.519525; MC not run |
| `runs/v22h_B_cat3spinered_1230` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.993174e-05 | 1.436628e-05 | 5.429802e-05 | 0.51956 | GF PASS; acc 0.519011; MC not run |
| `runs/v22h_B_cat3spinered_1302` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.878397e-05 | 1.459101e-05 | 5.337498e-05 | 0.51956 | GF PASS; acc 0.518714; MC not run |
| `runs/v22h_B_cat3spinered_1320` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.917767e-05 | 1.448198e-05 | 5.365965e-05 | 0.51956 | GF PASS; acc 0.519658; MC not run |
| `runs/v22h_B_cat3spinered_2013` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.89078e-05 | 1.429077e-05 | 5.319856e-05 | 0.51956 | GF PASS; acc 0.519685; MC not run |
| `runs/v22h_B_cat3spinered_2031` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.904051e-05 | 1.432258e-05 | 5.336309e-05 | 0.51956 | GF PASS; acc 0.518681; MC not run |
| `runs/v22h_B_cat3spinered_2103` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.966632e-05 | 1.432396e-05 | 5.399028e-05 | 0.51956 | GF PASS; acc 0.518993; MC not run |
| `runs/v22h_B_cat3spinered_2130` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.992952e-05 | 1.436962e-05 | 5.429913e-05 | 0.51956 | GF PASS; acc 0.519529; MC not run |
| `runs/v22h_B_cat3spinered_2301` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.954545e-05 | 1.434514e-05 | 5.389059e-05 | 0.51956 | GF PASS; acc 0.519589; MC not run |
| `runs/v22h_B_cat3spinered_2310` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.967816e-05 | 1.435894e-05 | 5.40371e-05 | 0.51956 | GF PASS; acc 0.519216; MC not run |
| `runs/v22h_B_cat3spinered_3012` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.928224e-05 | 1.458069e-05 | 5.386294e-05 | 0.51956 | GF PASS; acc 0.519002; MC not run |
| `runs/v22h_B_cat3spinered_3021` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.954545e-05 | 1.445757e-05 | 5.400302e-05 | 0.51956 | GF PASS; acc 0.519523; MC not run |
| `runs/v22h_B_cat3spinered_3102` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.878397e-05 | 1.456776e-05 | 5.335173e-05 | 0.51956 | GF PASS; acc 0.519662; MC not run |
| `runs/v22h_B_cat3spinered_3120` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.917767e-05 | 1.445836e-05 | 5.363602e-05 | 0.51956 | GF PASS; acc 0.518697; MC not run |
| `runs/v22h_B_cat3spinered_3201` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.954545e-05 | 1.43189e-05 | 5.386435e-05 | 0.51956 | GF PASS; acc 0.519201; MC not run |
| `runs/v22h_B_cat3spinered_3210` (regenerate) | B cat3spinered | 138 | 45 | 2.923587e-19 | 3.967816e-05 | 1.43321e-05 | 5.401026e-05 | 0.51956 | GF PASS; acc 0.519572; MC not run |
| `runs/v22h_B_cat4_012` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.108445e-05 | 1.78318e-05 | 5.891625e-05 | 0.56624 | GF PASS; acc 0.566304; MC not run |
| `runs/v22h_B_cat4_021` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.138649e-05 | 1.774193e-05 | 5.912842e-05 | 0.56624 | GF PASS; acc 0.566320; MC not run |
| `runs/v22h_B_cat4_102` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.074696e-05 | 1.783657e-05 | 5.858353e-05 | 0.56624 | GF PASS; acc 0.566307; MC not run |
| `runs/v22h_B_cat4_120` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.080036e-05 | 1.775411e-05 | 5.855447e-05 | 0.56624 | GF PASS; acc 0.566046; MC not run |
| `runs/v22h_B_cat4_201` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.138655e-05 | 1.765464e-05 | 5.904119e-05 | 0.56624 | GF PASS; acc 0.566007; MC not run |
| `runs/v22h_B_cat4_210` (regenerate) | B cat4 | 135 | 45 | 2.923587e-19 | 4.113778e-05 | 1.766199e-05 | 5.879977e-05 | 0.56624 | GF PASS; acc 0.566032; MC not run |
| `runs/v22h_B_cat_012` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 4.020676e-05 | 1.556568e-05 | 5.577244e-05 | 0.58359 | GF PASS; acc 0.583316; MC not run |
| `runs/v22h_B_cat_021` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 4.037342e-05 | 1.551688e-05 | 5.58903e-05 | 0.58359 | GF PASS; acc 0.583344; MC not run |
| `runs/v22h_B_cat_102` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 3.986928e-05 | 1.556991e-05 | 5.543919e-05 | 0.58359 | GF PASS; acc 0.583534; MC not run |
| `runs/v22h_B_cat_120` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 4.025535e-05 | 1.582322e-05 | 5.607857e-05 | 0.58170 | GF PASS; acc 0.581203; MC not run |
| `runs/v22h_B_cat_201` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 4.068371e-05 | 1.593478e-05 | 5.661849e-05 | 0.58073 | GF PASS; acc 0.581104; MC not run |
| `runs/v22h_B_cat_210` (regenerate) | B cat | 129 | 45 | 2.923587e-19 | 4.027968e-05 | 1.565104e-05 | 5.593072e-05 | 0.58286 | GF PASS; acc 0.582445; MC not run |
| `runs/v22h_B_catred_012` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.871351e-05 | 1.245583e-05 | 5.116934e-05 | 0.57568 | GF PASS; acc 0.574467; MC not run |
| `runs/v22h_B_catred_0132` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.864702e-05 | 1.239944e-05 | 5.104647e-05 | 0.57567 | GF PASS; acc 0.575161; MC not run |
| `runs/v22h_B_catred_021` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.871354e-05 | 1.244876e-05 | 5.116231e-05 | 0.57568 | GF PASS; acc 0.575138; MC not run |
| `runs/v22h_B_catred_0231` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.873331e-05 | 1.26512e-05 | 5.138451e-05 | 0.57266 | GF PASS; acc 0.571646; MC not run |
| `runs/v22h_B_catred_0312` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.874676e-05 | 1.259367e-05 | 5.134042e-05 | 0.57438 | GF PASS; acc 0.572873; MC not run |
| `runs/v22h_B_catred_0321` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.874676e-05 | 1.259531e-05 | 5.134206e-05 | 0.57438 | GF PASS; acc 0.572845; MC not run |
| `runs/v22h_B_catred_102` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.871351e-05 | 1.24602e-05 | 5.117371e-05 | 0.57510 | GF PASS; acc 0.574393; MC not run |
| `runs/v22h_B_catred_1032` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.864702e-05 | 1.240308e-05 | 5.105011e-05 | 0.57510 | GF PASS; acc 0.574530; MC not run |
| `runs/v22h_B_catred_120` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.885547e-05 | 1.261123e-05 | 5.14667e-05 | 0.57342 | GF PASS; acc 0.573070; MC not run |
| `runs/v22h_B_catred_1230` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.887757e-05 | 1.259924e-05 | 5.147681e-05 | 0.57552 | GF PASS; acc 0.575153; MC not run |
| `runs/v22h_B_catred_1302` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.864702e-05 | 1.240295e-05 | 5.104997e-05 | 0.57510 | GF PASS; acc 0.574415; MC not run |
| `runs/v22h_B_catred_1320` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.882433e-05 | 1.262588e-05 | 5.145021e-05 | 0.57265 | GF PASS; acc 0.572361; MC not run |
| `runs/v22h_B_catred_201` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.871354e-05 | 1.260768e-05 | 5.132122e-05 | 0.57304 | GF PASS; acc 0.572577; MC not run |
| `runs/v22h_B_catred_2031` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.875553e-05 | 1.2813e-05 | 5.156853e-05 | 0.56947 | GF PASS; acc 0.569245; MC not run |
| `runs/v22h_B_catred_210` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.881105e-05 | 1.260343e-05 | 5.141449e-05 | 0.57457 | GF PASS; acc 0.574041; MC not run |
| `runs/v22h_B_catred_2130` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.88776e-05 | 1.260021e-05 | 5.147781e-05 | 0.57552 | GF PASS; acc 0.574636; MC not run |
| `runs/v22h_B_catred_2301` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.876886e-05 | 1.272173e-05 | 5.149059e-05 | 0.57442 | GF PASS; acc 0.574243; MC not run |
| `runs/v22h_B_catred_2310` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.879102e-05 | 1.273148e-05 | 5.152251e-05 | 0.57270 | GF PASS; acc 0.570974; MC not run |
| `runs/v22h_B_catred_3012` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.870249e-05 | 1.252005e-05 | 5.122255e-05 | 0.57495 | GF PASS; acc 0.574431; MC not run |
| `runs/v22h_B_catred_3021` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.870249e-05 | 1.25219e-05 | 5.122439e-05 | 0.57495 | GF PASS; acc 0.574408; MC not run |
| `runs/v22h_B_catred_3102` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.862261e-05 | 1.252217e-05 | 5.114478e-05 | 0.57399 | GF PASS; acc 0.574018; MC not run |
| `runs/v22h_B_catred_3120` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.879991e-05 | 1.273592e-05 | 5.153583e-05 | 0.57327 | GF PASS; acc 0.572363; MC not run |
| `runs/v22h_B_catred_3201` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.883529e-05 | 1.278858e-05 | 5.162387e-05 | 0.57213 | GF PASS; acc 0.571066; MC not run |
| `runs/v22h_B_catred_3210` (regenerate) | B catred | 134 | 45 | 2.923587e-19 | 3.879102e-05 | 1.271871e-05 | 5.150974e-05 | 0.57442 | GF PASS; acc 0.573786; MC not run |
| `runs/v22h_B_direct_012` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.962137e-05 | 1.520695e-05 | 5.482832e-05 | 0.58374 | GF PASS; acc 0.583753; MC not run |
| `runs/v22h_B_direct_021` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.995405e-05 | 1.543368e-05 | 5.538772e-05 | 0.58141 | GF PASS; acc 0.580948; MC not run |
| `runs/v22h_B_direct_102` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.956148e-05 | 1.5631e-05 | 5.519249e-05 | 0.58026 | GF PASS; acc 0.580150; MC not run |
| `runs/v22h_B_direct_120` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.960827e-05 | 1.522697e-05 | 5.483524e-05 | 0.58315 | GF PASS; acc 0.582734; MC not run |
| `runs/v22h_B_direct_201` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.987002e-05 | 1.516112e-05 | 5.503114e-05 | 0.58315 | GF PASS; acc 0.582723; MC not run |
| `runs/v22h_B_direct_210` (regenerate) | B direct | 126 | 45 | 2.923587e-19 | 3.984335e-05 | 1.51635e-05 | 5.500685e-05 | 0.58315 | GF PASS; acc 0.582390; MC not run |
| `runs/v22h_B_flag_012` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.015192e-05 | 1.651224e-05 | 5.666416e-05 | 0.56401 | GF PASS; acc 0.563721; MC not run |
| `runs/v22h_B_flag_021` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.052297e-05 | 1.680458e-05 | 5.732755e-05 | 0.56121 | GF PASS; acc 0.561104; MC not run |
| `runs/v22h_B_flag_102` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.01155e-05 | 1.706001e-05 | 5.717551e-05 | 0.55954 | GF PASS; acc 0.559610; MC not run |
| `runs/v22h_B_flag_120` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.012125e-05 | 1.653653e-05 | 5.665778e-05 | 0.56344 | GF PASS; acc 0.562978; MC not run |
| `runs/v22h_B_flag_201` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.039139e-05 | 1.647728e-05 | 5.686867e-05 | 0.56344 | GF PASS; acc 0.562985; MC not run |
| `runs/v22h_B_flag_210` (regenerate) | B flag | 132 | 45 | 2.923587e-19 | 4.033382e-05 | 1.647941e-05 | 5.681323e-05 | 0.56344 | GF PASS; acc 0.562440; MC not run |
| `runs/v22h_B_hybrid1_012` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.972679e-05 | 1.534347e-05 | 5.507026e-05 | 0.57976 | GF PASS; acc 0.579689; MC not run |
| `runs/v22h_B_hybrid1_021` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.988205e-05 | 1.528505e-05 | 5.51671e-05 | 0.57976 | GF PASS; acc 0.579567; MC not run |
| `runs/v22h_B_hybrid1_102` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.972679e-05 | 1.534347e-05 | 5.507026e-05 | 0.57976 | GF PASS; acc 0.579689; MC not run |
| `runs/v22h_B_hybrid1_120` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.972679e-05 | 1.534347e-05 | 5.507026e-05 | 0.57976 | GF PASS; acc 0.579689; MC not run |
| `runs/v22h_B_hybrid1_201` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.988205e-05 | 1.528505e-05 | 5.51671e-05 | 0.57976 | GF PASS; acc 0.579567; MC not run |
| `runs/v22h_B_hybrid1_210` (regenerate) | B hybrid1 | 125 | 45 | 2.923587e-19 | 3.988205e-05 | 1.528505e-05 | 5.51671e-05 | 0.57976 | GF PASS; acc 0.579567; MC not run |
| `runs/v22h_B_hybrid2_012` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.489608e-05 | 5.42378e-05 | 0.58297 | GF PASS; acc 0.582863; MC not run |
| `runs/v22h_B_hybrid2_021` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.489608e-05 | 5.42378e-05 | 0.58297 | GF PASS; acc 0.582863; MC not run |
| `runs/v22h_B_hybrid2_102` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.489608e-05 | 5.42378e-05 | 0.58297 | GF PASS; acc 0.582863; MC not run |
| `runs/v22h_B_hybrid2_120` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.489608e-05 | 5.42378e-05 | 0.58297 | GF PASS; acc 0.582863; MC not run |
| `runs/v22h_B_hybrid2_201` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.489608e-05 | 5.42378e-05 | 0.58297 | GF PASS; acc 0.582863; MC not run |
| `runs/v22h_B_hybrid2_210` (regenerate) | B hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.489608e-05 | 5.42378e-05 | 0.58297 | GF PASS; acc 0.582863; MC not run |
| `runs/v22h_B_hybrid2t_012` (regenerate) | B hybrid2t | 123 | 45 | 2.923587e-19 | 3.954439e-05 | 1.520348e-05 | 5.474787e-05 | 0.58066 | GF PASS; acc 0.580946; MC not run |
| `runs/v22h_B_redundant_012` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.859102e-05 | 1.308464e-05 | 5.167567e-05 | 0.57742 | GF PASS; acc 0.577294; MC not run |
| `runs/v22h_B_redundant_0132` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.875364e-05 | 1.351624e-05 | 5.226988e-05 | 0.57396 | GF PASS; acc 0.574095; MC not run |
| `runs/v22h_B_redundant_021` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.85902e-05 | 1.307955e-05 | 5.166975e-05 | 0.57513 | GF PASS; acc 0.575007; MC not run |
| `runs/v22h_B_redundant_0231` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.865639e-05 | 1.323585e-05 | 5.189224e-05 | 0.57452 | GF PASS; acc 0.574338; MC not run |
| `runs/v22h_B_redundant_0312` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.878919e-05 | 1.33913e-05 | 5.21805e-05 | 0.57621 | GF PASS; acc 0.575121; MC not run |
| `runs/v22h_B_redundant_0321` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.88765e-05 | 1.344847e-05 | 5.232498e-05 | 0.57335 | GF PASS; acc 0.573218; MC not run |
| `runs/v22h_B_redundant_102` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.861687e-05 | 1.316667e-05 | 5.178353e-05 | 0.57398 | GF PASS; acc 0.573281; MC not run |
| `runs/v22h_B_redundant_1032` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.875808e-05 | 1.351608e-05 | 5.227416e-05 | 0.57396 | GF PASS; acc 0.572708; MC not run |
| `runs/v22h_B_redundant_120` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.871742e-05 | 1.302067e-05 | 5.17381e-05 | 0.57684 | GF PASS; acc 0.576487; MC not run |
| `runs/v22h_B_redundant_1230` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.876175e-05 | 1.302702e-05 | 5.178877e-05 | 0.57684 | GF PASS; acc 0.576942; MC not run |
| `runs/v22h_B_redundant_1302` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.871482e-05 | 1.3448e-05 | 5.216281e-05 | 0.57567 | GF PASS; acc 0.574927; MC not run |
| `runs/v22h_B_redundant_1320` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.873855e-05 | 1.331784e-05 | 5.205639e-05 | 0.57338 | GF PASS; acc 0.572757; MC not run |
| `runs/v22h_B_redundant_201` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.859325e-05 | 1.301842e-05 | 5.161167e-05 | 0.57684 | GF PASS; acc 0.574850; MC not run |
| `runs/v22h_B_redundant_2031` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.865944e-05 | 1.317802e-05 | 5.183746e-05 | 0.57508 | GF PASS; acc 0.574263; MC not run |
| `runs/v22h_B_redundant_210` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.871742e-05 | 1.302105e-05 | 5.173848e-05 | 0.57685 | GF PASS; acc 0.577223; MC not run |
| `runs/v22h_B_redundant_2130` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.876175e-05 | 1.302755e-05 | 5.17893e-05 | 0.57684 | GF PASS; acc 0.576699; MC not run |
| `runs/v22h_B_redundant_2301` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.869511e-05 | 1.310412e-05 | 5.179924e-05 | 0.57738 | GF PASS; acc 0.577148; MC not run |
| `runs/v22h_B_redundant_2310` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.872184e-05 | 1.311263e-05 | 5.183447e-05 | 0.57566 | GF PASS; acc 0.575334; MC not run |
| `runs/v22h_B_redundant_3012` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.874593e-05 | 1.330956e-05 | 5.205549e-05 | 0.57909 | GF PASS; acc 0.578314; MC not run |
| `runs/v22h_B_redundant_3021` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.88334e-05 | 1.337684e-05 | 5.221024e-05 | 0.57506 | GF PASS; acc 0.574034; MC not run |
| `runs/v22h_B_redundant_3102` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.873529e-05 | 1.353307e-05 | 5.226835e-05 | 0.57335 | GF PASS; acc 0.572690; MC not run |
| `runs/v22h_B_redundant_3120` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.873855e-05 | 1.324862e-05 | 5.198718e-05 | 0.57620 | GF PASS; acc 0.575166; MC not run |
| `runs/v22h_B_redundant_3201` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.879061e-05 | 1.323557e-05 | 5.202617e-05 | 0.57391 | GF PASS; acc 0.573740; MC not run |
| `runs/v22h_B_redundant_3210` (regenerate) | B redundant | 130 | 45 | 2.923587e-19 | 3.881733e-05 | 1.323652e-05 | 5.205385e-05 | 0.57392 | GF PASS; acc 0.573849; MC not run |
| `runs/v22h_B_seq_012` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 4.076053e-05 | 1.831677e-05 | 5.90773e-05 | 0.55661 | GF PASS; acc 0.556444; MC not run |
| `runs/v22h_B_seq_021` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 4.126839e-05 | 1.807676e-05 | 5.934516e-05 | 0.55662 | GF PASS; acc 0.555862; MC not run |
| `runs/v22h_B_seq_102` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 3.974176e-05 | 1.831491e-05 | 5.805667e-05 | 0.55662 | GF PASS; acc 0.555568; MC not run |
| `runs/v22h_B_seq_120` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 4.061794e-05 | 1.816078e-05 | 5.877872e-05 | 0.55606 | GF PASS; acc 0.555790; MC not run |
| `runs/v22h_B_seq_201` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 4.13612e-05 | 1.787562e-05 | 5.923681e-05 | 0.55606 | GF PASS; acc 0.555576; MC not run |
| `runs/v22h_B_seq_210` (regenerate) | B seq | 126 | 45 | 2.923587e-19 | 4.16449e-05 | 1.788567e-05 | 5.953057e-05 | 0.55607 | GF PASS; acc 0.555763; MC not run |
| `runs/v22h_C_cat13_012` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 3.987108e-05 | 1.570821e-05 | 5.557929e-05 | 0.58058 | GF PASS; acc 0.579894; MC not run |
| `runs/v22h_C_cat13_021` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 4.0204e-05 | 1.593054e-05 | 5.613454e-05 | 0.57826 | GF PASS; acc 0.578060; MC not run |
| `runs/v22h_C_cat13_102` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 3.98112e-05 | 1.612575e-05 | 5.593695e-05 | 0.57711 | GF PASS; acc 0.577050; MC not run |
| `runs/v22h_C_cat13_120` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 3.985787e-05 | 1.572759e-05 | 5.558546e-05 | 0.57999 | GF PASS; acc 0.579621; MC not run |
| `runs/v22h_C_cat13_201` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 4.011985e-05 | 1.566131e-05 | 5.578116e-05 | 0.57999 | GF PASS; acc 0.579592; MC not run |
| `runs/v22h_C_cat13_210` (regenerate) | C cat13 | 129 | 45 | 2.923587e-19 | 4.009307e-05 | 1.5664e-05 | 5.575706e-05 | 0.57999 | GF PASS; acc 0.579724; MC not run |
| `runs/v22h_C_cat13red_012` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.845805e-05 | 1.285891e-05 | 5.131696e-05 | 0.56928 | GF PASS; acc 0.568018; MC not run |
| `runs/v22h_C_cat13red_0132` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.835606e-05 | 1.277431e-05 | 5.113037e-05 | 0.56849 | GF PASS; acc 0.567533; MC not run |
| `runs/v22h_C_cat13red_021` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.845722e-05 | 1.285024e-05 | 5.130746e-05 | 0.56702 | GF PASS; acc 0.566408; MC not run |
| `runs/v22h_C_cat13red_0231` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.843506e-05 | 1.266997e-05 | 5.110502e-05 | 0.56604 | GF PASS; acc 0.565196; MC not run |
| `runs/v22h_C_cat13red_0312` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.839162e-05 | 1.252727e-05 | 5.091889e-05 | 0.56769 | GF PASS; acc 0.566207; MC not run |
| `runs/v22h_C_cat13red_0321` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.839162e-05 | 1.251888e-05 | 5.09105e-05 | 0.56769 | GF PASS; acc 0.566710; MC not run |
| `runs/v22h_C_cat13red_102` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.848389e-05 | 1.293472e-05 | 5.141861e-05 | 0.56589 | GF PASS; acc 0.565052; MC not run |
| `runs/v22h_C_cat13red_1032` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.836051e-05 | 1.277419e-05 | 5.113469e-05 | 0.56848 | GF PASS; acc 0.567743; MC not run |
| `runs/v22h_C_cat13red_120` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.858445e-05 | 1.279531e-05 | 5.137975e-05 | 0.56871 | GF PASS; acc 0.567494; MC not run |
| `runs/v22h_C_cat13red_1230` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.862877e-05 | 1.28058e-05 | 5.143457e-05 | 0.56795 | GF PASS; acc 0.567668; MC not run |
| `runs/v22h_C_cat13red_1302` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.836051e-05 | 1.285137e-05 | 5.121188e-05 | 0.56641 | GF PASS; acc 0.565322; MC not run |
| `runs/v22h_C_cat13red_1320` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.842922e-05 | 1.272462e-05 | 5.115384e-05 | 0.56754 | GF PASS; acc 0.566588; MC not run |
| `runs/v22h_C_cat13red_201` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.846027e-05 | 1.279335e-05 | 5.125362e-05 | 0.56871 | GF PASS; acc 0.568126; MC not run |
| `runs/v22h_C_cat13red_2031` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.843811e-05 | 1.261206e-05 | 5.105017e-05 | 0.56772 | GF PASS; acc 0.566129; MC not run |
| `runs/v22h_C_cat13red_210` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.858445e-05 | 1.279642e-05 | 5.138087e-05 | 0.56871 | GF PASS; acc 0.567714; MC not run |
| `runs/v22h_C_cat13red_2130` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.862877e-05 | 1.280722e-05 | 5.143599e-05 | 0.56795 | GF PASS; acc 0.567696; MC not run |
| `runs/v22h_C_cat13red_2301` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.851793e-05 | 1.261678e-05 | 5.113471e-05 | 0.56735 | GF PASS; acc 0.566691; MC not run |
| `runs/v22h_C_cat13red_2310` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.858886e-05 | 1.261884e-05 | 5.12077e-05 | 0.56735 | GF PASS; acc 0.566944; MC not run |
| `runs/v22h_C_cat13red_3012` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.839162e-05 | 1.252372e-05 | 5.091534e-05 | 0.56769 | GF PASS; acc 0.566849; MC not run |
| `runs/v22h_C_cat13red_3021` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.839162e-05 | 1.252678e-05 | 5.091839e-05 | 0.56543 | GF PASS; acc 0.564287; MC not run |
| `runs/v22h_C_cat13red_3102` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.838273e-05 | 1.259989e-05 | 5.098262e-05 | 0.56430 | GF PASS; acc 0.564050; MC not run |
| `runs/v22h_C_cat13red_3120` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.842922e-05 | 1.246624e-05 | 5.089546e-05 | 0.56712 | GF PASS; acc 0.566405; MC not run |
| `runs/v22h_C_cat13red_3201` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.839384e-05 | 1.245718e-05 | 5.085102e-05 | 0.56712 | GF PASS; acc 0.566468; MC not run |
| `runs/v22h_C_cat13red_3210` (regenerate) | C cat13red | 134 | 45 | 2.923587e-19 | 3.846477e-05 | 1.245839e-05 | 5.092316e-05 | 0.56712 | GF PASS; acc 0.566417; MC not run |
| `runs/v22h_C_cat3_012` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.070913e-05 | 1.661448e-05 | 5.732361e-05 | 0.57617 | GF PASS; acc 0.576449; MC not run |
| `runs/v22h_C_cat3_021` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.083357e-05 | 1.657226e-05 | 5.740583e-05 | 0.57617 | GF PASS; acc 0.576465; MC not run |
| `runs/v22h_C_cat3_102` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.037159e-05 | 1.66194e-05 | 5.699098e-05 | 0.57617 | GF PASS; acc 0.576450; MC not run |
| `runs/v22h_C_cat3_120` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.060252e-05 | 1.681669e-05 | 5.741921e-05 | 0.57387 | GF PASS; acc 0.573433; MC not run |
| `runs/v22h_C_cat3_201` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.101117e-05 | 1.676563e-05 | 5.77768e-05 | 0.57387 | GF PASS; acc 0.573466; MC not run |
| `runs/v22h_C_cat3_210` (regenerate) | C cat3 | 132 | 45 | 2.923587e-19 | 4.076246e-05 | 1.677218e-05 | 5.753464e-05 | 0.57387 | GF PASS; acc 0.573457; MC not run |
| `runs/v22h_C_cat3red_0123` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.858273e-05 | 1.231547e-05 | 5.089819e-05 | 0.56635 | GF PASS; acc 0.566590; MC not run |
| `runs/v22h_C_cat3red_0132` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.861822e-05 | 1.236609e-05 | 5.098432e-05 | 0.56450 | GF PASS; acc 0.564469; MC not run |
| `runs/v22h_C_cat3red_0213` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.858273e-05 | 1.230935e-05 | 5.089207e-05 | 0.56635 | GF PASS; acc 0.566606; MC not run |
| `runs/v22h_C_cat3red_0231` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.86691e-05 | 1.252587e-05 | 5.119497e-05 | 0.56001 | GF PASS; acc 0.559895; MC not run |
| `runs/v22h_C_cat3red_0312` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.871796e-05 | 1.257124e-05 | 5.12892e-05 | 0.56154 | GF PASS; acc 0.561499; MC not run |
| `runs/v22h_C_cat3red_0321` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.871796e-05 | 1.257293e-05 | 5.129089e-05 | 0.56154 | GF PASS; acc 0.561534; MC not run |
| `runs/v22h_C_cat3red_1023` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.858273e-05 | 1.231982e-05 | 5.090255e-05 | 0.56578 | GF PASS; acc 0.565664; MC not run |
| `runs/v22h_C_cat3red_1032` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.861822e-05 | 1.236978e-05 | 5.0988e-05 | 0.56394 | GF PASS; acc 0.563058; MC not run |
| `runs/v22h_C_cat3red_1203` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.863606e-05 | 1.23277e-05 | 5.096376e-05 | 0.56352 | GF PASS; acc 0.562785; MC not run |
| `runs/v22h_C_cat3red_1230` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.863606e-05 | 1.232523e-05 | 5.096129e-05 | 0.56352 | GF PASS; acc 0.562775; MC not run |
| `runs/v22h_C_cat3red_1302` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.861822e-05 | 1.236417e-05 | 5.09824e-05 | 0.56563 | GF PASS; acc 0.565036; MC not run |
| `runs/v22h_C_cat3red_1320` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.866255e-05 | 1.244008e-05 | 5.110263e-05 | 0.56187 | GF PASS; acc 0.561370; MC not run |
| `runs/v22h_C_cat3red_2013` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.858273e-05 | 1.231547e-05 | 5.08982e-05 | 0.56578 | GF PASS; acc 0.565044; MC not run |
| `runs/v22h_C_cat3red_2031` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.86691e-05 | 1.253945e-05 | 5.120854e-05 | 0.55778 | GF PASS; acc 0.557100; MC not run |
| `runs/v22h_C_cat3red_2103` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.863606e-05 | 1.232958e-05 | 5.096564e-05 | 0.56352 | GF PASS; acc 0.562781; MC not run |
| `runs/v22h_C_cat3red_2130` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.863606e-05 | 1.232744e-05 | 5.096351e-05 | 0.56352 | GF PASS; acc 0.562773; MC not run |
| `runs/v22h_C_cat3red_2301` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.866039e-05 | 1.245395e-05 | 5.111434e-05 | 0.56169 | GF PASS; acc 0.561331; MC not run |
| `runs/v22h_C_cat3red_2310` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.861606e-05 | 1.246526e-05 | 5.108132e-05 | 0.55908 | GF PASS; acc 0.557846; MC not run |
| `runs/v22h_C_cat3red_3012` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.867369e-05 | 1.248385e-05 | 5.115754e-05 | 0.56548 | GF PASS; acc 0.564699; MC not run |
| `runs/v22h_C_cat3red_3021` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.867369e-05 | 1.248552e-05 | 5.115921e-05 | 0.56548 | GF PASS; acc 0.564670; MC not run |
| `runs/v22h_C_cat3red_3102` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.859381e-05 | 1.249133e-05 | 5.108514e-05 | 0.56285 | GF PASS; acc 0.562683; MC not run |
| `runs/v22h_C_cat3red_3120` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.863813e-05 | 1.256172e-05 | 5.119985e-05 | 0.56079 | GF PASS; acc 0.559980; MC not run |
| `runs/v22h_C_cat3red_3201` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.871802e-05 | 1.254409e-05 | 5.126211e-05 | 0.56341 | GF PASS; acc 0.563100; MC not run |
| `runs/v22h_C_cat3red_3210` (regenerate) | C cat3red | 138 | 45 | 2.923587e-19 | 3.867369e-05 | 1.255364e-05 | 5.122733e-05 | 0.56079 | GF PASS; acc 0.559985; MC not run |
| `runs/v22h_C_cat3reusered_0123` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.895218e-05 | 1.427625e-05 | 5.322843e-05 | 0.51846 | GF PASS; acc 0.517902; MC not run |
| `runs/v22h_C_cat3reusered_0132` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.885461e-05 | 1.447191e-05 | 5.332652e-05 | 0.51901 | GF PASS; acc 0.518953; MC not run |
| `runs/v22h_C_cat3reusered_0213` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.895218e-05 | 1.416042e-05 | 5.31126e-05 | 0.51846 | GF PASS; acc 0.517829; MC not run |
| `runs/v22h_C_cat3reusered_0231` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.908232e-05 | 1.424509e-05 | 5.332741e-05 | 0.51901 | GF PASS; acc 0.518602; MC not run |
| `runs/v22h_C_cat3reusered_0312` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.937253e-05 | 1.457326e-05 | 5.394579e-05 | 0.51956 | GF PASS; acc 0.519006; MC not run |
| `runs/v22h_C_cat3reusered_0321` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.96376e-05 | 1.445257e-05 | 5.409017e-05 | 0.51956 | GF PASS; acc 0.518666; MC not run |
| `runs/v22h_C_cat3reusered_1023` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.895218e-05 | 1.427821e-05 | 5.323039e-05 | 0.51847 | GF PASS; acc 0.518018; MC not run |
| `runs/v22h_C_cat3reusered_1032` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.885461e-05 | 1.447372e-05 | 5.332833e-05 | 0.51901 | GF PASS; acc 0.518603; MC not run |
| `runs/v22h_C_cat3reusered_1203` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.973292e-05 | 1.419568e-05 | 5.39286e-05 | 0.51847 | GF PASS; acc 0.518000; MC not run |
| `runs/v22h_C_cat3reusered_1230` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.999835e-05 | 1.42408e-05 | 5.423914e-05 | 0.51846 | GF PASS; acc 0.517990; MC not run |
| `runs/v22h_C_cat3reusered_1302` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.885461e-05 | 1.451129e-05 | 5.33659e-05 | 0.51901 | GF PASS; acc 0.518390; MC not run |
| `runs/v22h_C_cat3reusered_1320` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.925275e-05 | 1.440211e-05 | 5.365486e-05 | 0.51901 | GF PASS; acc 0.519347; MC not run |
| `runs/v22h_C_cat3reusered_2013` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.895218e-05 | 1.4165e-05 | 5.311718e-05 | 0.51847 | GF PASS; acc 0.517600; MC not run |
| `runs/v22h_C_cat3reusered_2031` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.908232e-05 | 1.424909e-05 | 5.333141e-05 | 0.51901 | GF PASS; acc 0.519071; MC not run |
| `runs/v22h_C_cat3reusered_2103` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.973292e-05 | 1.419828e-05 | 5.39312e-05 | 0.51847 | GF PASS; acc 0.517984; MC not run |
| `runs/v22h_C_cat3reusered_2130` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.999835e-05 | 1.424327e-05 | 5.424162e-05 | 0.51846 | GF PASS; acc 0.517984; MC not run |
| `runs/v22h_C_cat3reusered_2301` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.960281e-05 | 1.427324e-05 | 5.387605e-05 | 0.51901 | GF PASS; acc 0.518841; MC not run |
| `runs/v22h_C_cat3reusered_2310` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.973588e-05 | 1.428421e-05 | 5.402009e-05 | 0.51901 | GF PASS; acc 0.518786; MC not run |
| `runs/v22h_C_cat3reusered_3012` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.937253e-05 | 1.45511e-05 | 5.392364e-05 | 0.51955 | GF PASS; acc 0.519390; MC not run |
| `runs/v22h_C_cat3reusered_3021` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.96376e-05 | 1.443045e-05 | 5.406805e-05 | 0.51955 | GF PASS; acc 0.519729; MC not run |
| `runs/v22h_C_cat3reusered_3102` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.885239e-05 | 1.453778e-05 | 5.339017e-05 | 0.51956 | GF PASS; acc 0.519311; MC not run |
| `runs/v22h_C_cat3reusered_3120` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.925053e-05 | 1.442846e-05 | 5.367899e-05 | 0.51956 | GF PASS; acc 0.520404; MC not run |
| `runs/v22h_C_cat3reusered_3201` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.96376e-05 | 1.428846e-05 | 5.392607e-05 | 0.51956 | GF PASS; acc 0.519592; MC not run |
| `runs/v22h_C_cat3reusered_3210` (regenerate) | C cat3reusered | 138 | 45 | 2.923587e-19 | 3.977067e-05 | 1.42993e-05 | 5.406997e-05 | 0.51956 | GF PASS; acc 0.519300; MC not run |
| `runs/v22h_C_cat3spinered_0123` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.891446e-05 | 1.42066e-05 | 5.312106e-05 | 0.51956 | GF PASS; acc 0.519566; MC not run |
| `runs/v22h_C_cat3spinered_0132` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.878175e-05 | 1.436189e-05 | 5.314364e-05 | 0.51956 | GF PASS; acc 0.518282; MC not run |
| `runs/v22h_C_cat3spinered_0213` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.891224e-05 | 1.409352e-05 | 5.300576e-05 | 0.51956 | GF PASS; acc 0.518834; MC not run |
| `runs/v22h_C_cat3spinered_0231` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.904495e-05 | 1.412589e-05 | 5.317085e-05 | 0.51956 | GF PASS; acc 0.518914; MC not run |
| `runs/v22h_C_cat3spinered_0312` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.928447e-05 | 1.44111e-05 | 5.369557e-05 | 0.51956 | GF PASS; acc 0.518983; MC not run |
| `runs/v22h_C_cat3spinered_0321` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.954767e-05 | 1.428761e-05 | 5.383528e-05 | 0.51956 | GF PASS; acc 0.519004; MC not run |
| `runs/v22h_C_cat3spinered_1023` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.891446e-05 | 1.420819e-05 | 5.312265e-05 | 0.51956 | GF PASS; acc 0.518305; MC not run |
| `runs/v22h_C_cat3spinered_1032` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.878175e-05 | 1.436285e-05 | 5.31446e-05 | 0.51956 | GF PASS; acc 0.519491; MC not run |
| `runs/v22h_C_cat3spinered_1203` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.966854e-05 | 1.412863e-05 | 5.379717e-05 | 0.51956 | GF PASS; acc 0.518962; MC not run |
| `runs/v22h_C_cat3spinered_1230` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.993174e-05 | 1.41741e-05 | 5.410584e-05 | 0.51956 | GF PASS; acc 0.519024; MC not run |
| `runs/v22h_C_cat3spinered_1302` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.878397e-05 | 1.439881e-05 | 5.318278e-05 | 0.51956 | GF PASS; acc 0.518806; MC not run |
| `runs/v22h_C_cat3spinered_1320` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.917767e-05 | 1.428971e-05 | 5.346738e-05 | 0.51956 | GF PASS; acc 0.518872; MC not run |
| `runs/v22h_C_cat3spinered_2013` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.89078e-05 | 1.409801e-05 | 5.30058e-05 | 0.51956 | GF PASS; acc 0.518895; MC not run |
| `runs/v22h_C_cat3spinered_2031` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.904051e-05 | 1.413001e-05 | 5.317052e-05 | 0.51956 | GF PASS; acc 0.518855; MC not run |
| `runs/v22h_C_cat3spinered_2103` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.966632e-05 | 1.413151e-05 | 5.379782e-05 | 0.51956 | GF PASS; acc 0.518994; MC not run |
| `runs/v22h_C_cat3spinered_2130` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.992952e-05 | 1.417735e-05 | 5.410687e-05 | 0.51956 | GF PASS; acc 0.518952; MC not run |
| `runs/v22h_C_cat3spinered_2301` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.954545e-05 | 1.415273e-05 | 5.369818e-05 | 0.51956 | GF PASS; acc 0.519507; MC not run |
| `runs/v22h_C_cat3spinered_2310` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.967816e-05 | 1.416653e-05 | 5.384469e-05 | 0.51956 | GF PASS; acc 0.518316; MC not run |
| `runs/v22h_C_cat3spinered_3012` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.928224e-05 | 1.438886e-05 | 5.367111e-05 | 0.51956 | GF PASS; acc 0.518988; MC not run |
| `runs/v22h_C_cat3spinered_3021` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.954545e-05 | 1.426569e-05 | 5.381113e-05 | 0.51956 | GF PASS; acc 0.518968; MC not run |
| `runs/v22h_C_cat3spinered_3102` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.878397e-05 | 1.437555e-05 | 5.315952e-05 | 0.51956 | GF PASS; acc 0.518891; MC not run |
| `runs/v22h_C_cat3spinered_3120` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.917767e-05 | 1.426608e-05 | 5.344374e-05 | 0.51956 | GF PASS; acc 0.518790; MC not run |
| `runs/v22h_C_cat3spinered_3201` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.954545e-05 | 1.412656e-05 | 5.367201e-05 | 0.51956 | GF PASS; acc 0.518288; MC not run |
| `runs/v22h_C_cat3spinered_3210` (regenerate) | C cat3spinered | 138 | 45 | 2.923587e-19 | 3.967816e-05 | 1.413976e-05 | 5.381792e-05 | 0.51956 | GF PASS; acc 0.519495; MC not run |
| `runs/v22h_C_cat4_012` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.108445e-05 | 1.77279e-05 | 5.881234e-05 | 0.56624 | GF PASS; acc 0.565207; MC not run |
| `runs/v22h_C_cat4_021` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.138649e-05 | 1.763799e-05 | 5.902448e-05 | 0.56624 | GF PASS; acc 0.565201; MC not run |
| `runs/v22h_C_cat4_102` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.074696e-05 | 1.773259e-05 | 5.847955e-05 | 0.56624 | GF PASS; acc 0.565218; MC not run |
| `runs/v22h_C_cat4_120` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.080036e-05 | 1.765005e-05 | 5.845041e-05 | 0.56624 | GF PASS; acc 0.565726; MC not run |
| `runs/v22h_C_cat4_201` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.138655e-05 | 1.755059e-05 | 5.893714e-05 | 0.56624 | GF PASS; acc 0.565720; MC not run |
| `runs/v22h_C_cat4_210` (regenerate) | C cat4 | 135 | 45 | 2.923587e-19 | 4.113778e-05 | 1.75579e-05 | 5.869568e-05 | 0.56624 | GF PASS; acc 0.565719; MC not run |
| `runs/v22h_C_cat_012` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 4.020676e-05 | 1.551528e-05 | 5.572204e-05 | 0.58359 | GF PASS; acc 0.584054; MC not run |
| `runs/v22h_C_cat_021` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 4.037342e-05 | 1.54664e-05 | 5.583982e-05 | 0.58359 | GF PASS; acc 0.584035; MC not run |
| `runs/v22h_C_cat_102` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 3.986928e-05 | 1.551943e-05 | 5.538871e-05 | 0.58359 | GF PASS; acc 0.583605; MC not run |
| `runs/v22h_C_cat_120` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 4.025535e-05 | 1.577095e-05 | 5.60263e-05 | 0.58170 | GF PASS; acc 0.580865; MC not run |
| `runs/v22h_C_cat_201` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 4.068371e-05 | 1.58821e-05 | 5.656581e-05 | 0.58073 | GF PASS; acc 0.580884; MC not run |
| `runs/v22h_C_cat_210` (regenerate) | C cat | 129 | 45 | 2.923587e-19 | 4.027968e-05 | 1.560267e-05 | 5.588234e-05 | 0.58286 | GF PASS; acc 0.582444; MC not run |
| `runs/v22h_C_catred_012` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.871351e-05 | 1.239393e-05 | 5.110744e-05 | 0.57568 | GF PASS; acc 0.575376; MC not run |
| `runs/v22h_C_catred_0132` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.864702e-05 | 1.233718e-05 | 5.098421e-05 | 0.57567 | GF PASS; acc 0.574825; MC not run |
| `runs/v22h_C_catred_021` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.871354e-05 | 1.238686e-05 | 5.11004e-05 | 0.57568 | GF PASS; acc 0.575240; MC not run |
| `runs/v22h_C_catred_0231` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.873331e-05 | 1.258751e-05 | 5.132082e-05 | 0.57266 | GF PASS; acc 0.572112; MC not run |
| `runs/v22h_C_catred_0312` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.874676e-05 | 1.253315e-05 | 5.127991e-05 | 0.57438 | GF PASS; acc 0.573723; MC not run |
| `runs/v22h_C_catred_0321` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.874676e-05 | 1.253479e-05 | 5.128155e-05 | 0.57438 | GF PASS; acc 0.573755; MC not run |
| `runs/v22h_C_catred_102` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.871351e-05 | 1.239781e-05 | 5.111133e-05 | 0.57510 | GF PASS; acc 0.574969; MC not run |
| `runs/v22h_C_catred_1032` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.864702e-05 | 1.234034e-05 | 5.098736e-05 | 0.57510 | GF PASS; acc 0.574689; MC not run |
| `runs/v22h_C_catred_120` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.885547e-05 | 1.254809e-05 | 5.140355e-05 | 0.57342 | GF PASS; acc 0.572543; MC not run |
| `runs/v22h_C_catred_1230` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.887757e-05 | 1.254021e-05 | 5.141778e-05 | 0.57552 | GF PASS; acc 0.575469; MC not run |
| `runs/v22h_C_catred_1302` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.864702e-05 | 1.234024e-05 | 5.098727e-05 | 0.57510 | GF PASS; acc 0.573861; MC not run |
| `runs/v22h_C_catred_1320` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.882433e-05 | 1.255982e-05 | 5.138415e-05 | 0.57265 | GF PASS; acc 0.572074; MC not run |
| `runs/v22h_C_catred_201` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.871354e-05 | 1.254448e-05 | 5.125802e-05 | 0.57304 | GF PASS; acc 0.572016; MC not run |
| `runs/v22h_C_catred_2031` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.875553e-05 | 1.274489e-05 | 5.150041e-05 | 0.56947 | GF PASS; acc 0.568792; MC not run |
| `runs/v22h_C_catred_210` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.881105e-05 | 1.254388e-05 | 5.135493e-05 | 0.57457 | GF PASS; acc 0.573711; MC not run |
| `runs/v22h_C_catred_2130` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.88776e-05 | 1.254118e-05 | 5.141878e-05 | 0.57552 | GF PASS; acc 0.573830; MC not run |
| `runs/v22h_C_catred_2301` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.876886e-05 | 1.266439e-05 | 5.143326e-05 | 0.57442 | GF PASS; acc 0.574464; MC not run |
| `runs/v22h_C_catred_2310` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.879102e-05 | 1.267037e-05 | 5.14614e-05 | 0.57270 | GF PASS; acc 0.572016; MC not run |
| `runs/v22h_C_catred_3012` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.870249e-05 | 1.245959e-05 | 5.116208e-05 | 0.57495 | GF PASS; acc 0.574016; MC not run |
| `runs/v22h_C_catred_3021` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.870249e-05 | 1.246143e-05 | 5.116392e-05 | 0.57495 | GF PASS; acc 0.574010; MC not run |
| `runs/v22h_C_catred_3102` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.862261e-05 | 1.246088e-05 | 5.108349e-05 | 0.57399 | GF PASS; acc 0.573338; MC not run |
| `runs/v22h_C_catred_3120` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.879991e-05 | 1.267505e-05 | 5.147497e-05 | 0.57327 | GF PASS; acc 0.572480; MC not run |
| `runs/v22h_C_catred_3201` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.883529e-05 | 1.27254e-05 | 5.156069e-05 | 0.57213 | GF PASS; acc 0.571388; MC not run |
| `runs/v22h_C_catred_3210` (regenerate) | C catred | 134 | 45 | 2.923587e-19 | 3.879102e-05 | 1.266145e-05 | 5.145247e-05 | 0.57442 | GF PASS; acc 0.574176; MC not run |
| `runs/v22h_C_direct_012` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.962137e-05 | 1.517017e-05 | 5.479153e-05 | 0.58374 | GF PASS; acc 0.584273; MC not run |
| `runs/v22h_C_direct_021` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.995405e-05 | 1.539228e-05 | 5.534633e-05 | 0.58141 | GF PASS; acc 0.580842; MC not run |
| `runs/v22h_C_direct_102` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.956148e-05 | 1.558664e-05 | 5.514812e-05 | 0.58026 | GF PASS; acc 0.579879; MC not run |
| `runs/v22h_C_direct_120` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.960827e-05 | 1.518889e-05 | 5.479716e-05 | 0.58315 | GF PASS; acc 0.582706; MC not run |
| `runs/v22h_C_direct_201` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.987002e-05 | 1.512295e-05 | 5.499296e-05 | 0.58315 | GF PASS; acc 0.582770; MC not run |
| `runs/v22h_C_direct_210` (regenerate) | C direct | 126 | 45 | 2.923587e-19 | 3.984335e-05 | 1.512537e-05 | 5.496872e-05 | 0.58315 | GF PASS; acc 0.582947; MC not run |
| `runs/v22h_C_flag_012` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.015192e-05 | 1.647579e-05 | 5.662772e-05 | 0.56401 | GF PASS; acc 0.563417; MC not run |
| `runs/v22h_C_flag_021` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.052297e-05 | 1.67647e-05 | 5.728767e-05 | 0.56121 | GF PASS; acc 0.560848; MC not run |
| `runs/v22h_C_flag_102` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.01155e-05 | 1.701907e-05 | 5.713457e-05 | 0.55954 | GF PASS; acc 0.559018; MC not run |
| `runs/v22h_C_flag_120` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.012125e-05 | 1.649878e-05 | 5.662003e-05 | 0.56344 | GF PASS; acc 0.562622; MC not run |
| `runs/v22h_C_flag_201` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.039139e-05 | 1.643947e-05 | 5.683086e-05 | 0.56344 | GF PASS; acc 0.562708; MC not run |
| `runs/v22h_C_flag_210` (regenerate) | C flag | 132 | 45 | 2.923587e-19 | 4.033382e-05 | 1.644163e-05 | 5.677545e-05 | 0.56344 | GF PASS; acc 0.563391; MC not run |
| `runs/v22h_C_hybrid1_012` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.972679e-05 | 1.529392e-05 | 5.502072e-05 | 0.57976 | GF PASS; acc 0.579304; MC not run |
| `runs/v22h_C_hybrid1_021` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.988205e-05 | 1.523549e-05 | 5.511754e-05 | 0.57976 | GF PASS; acc 0.578870; MC not run |
| `runs/v22h_C_hybrid1_102` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.972679e-05 | 1.529392e-05 | 5.502072e-05 | 0.57976 | GF PASS; acc 0.579304; MC not run |
| `runs/v22h_C_hybrid1_120` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.972679e-05 | 1.529392e-05 | 5.502072e-05 | 0.57976 | GF PASS; acc 0.579304; MC not run |
| `runs/v22h_C_hybrid1_201` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.988205e-05 | 1.523549e-05 | 5.511754e-05 | 0.57976 | GF PASS; acc 0.578870; MC not run |
| `runs/v22h_C_hybrid1_210` (regenerate) | C hybrid1 | 125 | 45 | 2.923587e-19 | 3.988205e-05 | 1.523549e-05 | 5.511754e-05 | 0.57976 | GF PASS; acc 0.578870; MC not run |
| `runs/v22h_C_hybrid2_012` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.485772e-05 | 5.419945e-05 | 0.58297 | GF PASS; acc 0.582427; MC not run |
| `runs/v22h_C_hybrid2_021` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.485772e-05 | 5.419945e-05 | 0.58297 | GF PASS; acc 0.582427; MC not run |
| `runs/v22h_C_hybrid2_102` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.485772e-05 | 5.419945e-05 | 0.58297 | GF PASS; acc 0.582427; MC not run |
| `runs/v22h_C_hybrid2_120` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.485772e-05 | 5.419945e-05 | 0.58297 | GF PASS; acc 0.582427; MC not run |
| `runs/v22h_C_hybrid2_201` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.485772e-05 | 5.419945e-05 | 0.58297 | GF PASS; acc 0.582427; MC not run |
| `runs/v22h_C_hybrid2_210` (regenerate) | C hybrid2 | 124 | 45 | 2.923587e-19 | 3.934172e-05 | 1.485772e-05 | 5.419945e-05 | 0.58297 | GF PASS; acc 0.582427; MC not run |
| `runs/v22h_C_hybrid2t_012` (regenerate) | C hybrid2t | 123 | 45 | 2.923587e-19 | 3.954439e-05 | 1.515816e-05 | 5.470256e-05 | 0.58066 | GF PASS; acc 0.580335; MC not run |
| `runs/v22h_C_redundant_012` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.859102e-05 | 1.304235e-05 | 5.163338e-05 | 0.57742 | GF PASS; acc 0.576517; MC not run |
| `runs/v22h_C_redundant_0132` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.875364e-05 | 1.34672e-05 | 5.222084e-05 | 0.57396 | GF PASS; acc 0.573305; MC not run |
| `runs/v22h_C_redundant_021` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.85902e-05 | 1.303273e-05 | 5.162293e-05 | 0.57513 | GF PASS; acc 0.574123; MC not run |
| `runs/v22h_C_redundant_0231` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.865639e-05 | 1.318737e-05 | 5.184377e-05 | 0.57452 | GF PASS; acc 0.574022; MC not run |
| `runs/v22h_C_redundant_0312` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.878919e-05 | 1.334651e-05 | 5.21357e-05 | 0.57621 | GF PASS; acc 0.575532; MC not run |
| `runs/v22h_C_redundant_0321` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.88765e-05 | 1.339805e-05 | 5.227455e-05 | 0.57335 | GF PASS; acc 0.572597; MC not run |
| `runs/v22h_C_redundant_102` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.861687e-05 | 1.311696e-05 | 5.173382e-05 | 0.57398 | GF PASS; acc 0.572986; MC not run |
| `runs/v22h_C_redundant_1032` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.875808e-05 | 1.3467e-05 | 5.222508e-05 | 0.57396 | GF PASS; acc 0.573781; MC not run |
| `runs/v22h_C_redundant_120` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.871742e-05 | 1.297727e-05 | 5.169469e-05 | 0.57684 | GF PASS; acc 0.576501; MC not run |
| `runs/v22h_C_redundant_1230` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.876175e-05 | 1.298364e-05 | 5.17454e-05 | 0.57684 | GF PASS; acc 0.575952; MC not run |
| `runs/v22h_C_redundant_1302` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.871482e-05 | 1.340231e-05 | 5.211713e-05 | 0.57567 | GF PASS; acc 0.575430; MC not run |
| `runs/v22h_C_redundant_1320` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.873855e-05 | 1.326757e-05 | 5.200612e-05 | 0.57338 | GF PASS; acc 0.573599; MC not run |
| `runs/v22h_C_redundant_201` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.859325e-05 | 1.297493e-05 | 5.156818e-05 | 0.57684 | GF PASS; acc 0.577088; MC not run |
| `runs/v22h_C_redundant_2031` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.865944e-05 | 1.313059e-05 | 5.179003e-05 | 0.57508 | GF PASS; acc 0.573970; MC not run |
| `runs/v22h_C_redundant_210` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.871742e-05 | 1.297762e-05 | 5.169505e-05 | 0.57685 | GF PASS; acc 0.576666; MC not run |
| `runs/v22h_C_redundant_2130` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.876175e-05 | 1.298416e-05 | 5.174591e-05 | 0.57684 | GF PASS; acc 0.576450; MC not run |
| `runs/v22h_C_redundant_2301` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.869511e-05 | 1.306159e-05 | 5.175671e-05 | 0.57738 | GF PASS; acc 0.576565; MC not run |
| `runs/v22h_C_redundant_2310` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.872184e-05 | 1.306633e-05 | 5.178817e-05 | 0.57566 | GF PASS; acc 0.575566; MC not run |
| `runs/v22h_C_redundant_3012` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.874593e-05 | 1.327037e-05 | 5.20163e-05 | 0.57909 | GF PASS; acc 0.578241; MC not run |
| `runs/v22h_C_redundant_3021` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.88334e-05 | 1.332979e-05 | 5.216319e-05 | 0.57506 | GF PASS; acc 0.573893; MC not run |
| `runs/v22h_C_redundant_3102` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.873529e-05 | 1.348121e-05 | 5.221649e-05 | 0.57335 | GF PASS; acc 0.573001; MC not run |
| `runs/v22h_C_redundant_3120` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.873855e-05 | 1.320369e-05 | 5.194224e-05 | 0.57620 | GF PASS; acc 0.575899; MC not run |
| `runs/v22h_C_redundant_3201` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.879061e-05 | 1.318609e-05 | 5.197669e-05 | 0.57391 | GF PASS; acc 0.573656; MC not run |
| `runs/v22h_C_redundant_3210` (regenerate) | C redundant | 130 | 45 | 2.923587e-19 | 3.881733e-05 | 1.318705e-05 | 5.200438e-05 | 0.57392 | GF PASS; acc 0.573638; MC not run |
| `runs/v22h_C_seq_012` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 4.076053e-05 | 1.82232e-05 | 5.898373e-05 | 0.55661 | GF PASS; acc 0.556369; MC not run |
| `runs/v22h_C_seq_021` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 4.126839e-05 | 1.798298e-05 | 5.925137e-05 | 0.55662 | GF PASS; acc 0.556236; MC not run |
| `runs/v22h_C_seq_102` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 3.974176e-05 | 1.822085e-05 | 5.796261e-05 | 0.55662 | GF PASS; acc 0.555957; MC not run |
| `runs/v22h_C_seq_120` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 4.061794e-05 | 1.806543e-05 | 5.868338e-05 | 0.55606 | GF PASS; acc 0.555390; MC not run |
| `runs/v22h_C_seq_201` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 4.13612e-05 | 1.77799e-05 | 5.91411e-05 | 0.55606 | GF PASS; acc 0.555710; MC not run |
| `runs/v22h_C_seq_210` (regenerate) | C seq | 126 | 45 | 2.923587e-19 | 4.16449e-05 | 1.779011e-05 | 5.943501e-05 | 0.55607 | GF PASS; acc 0.554923; MC not run |
| `runs/v22h_ref` (regenerate) |  direct | 123 | 45 | 2.923587e-19 | 3.864948e-05 | 1.255789e-05 | 5.120737e-05 | 0.60321 | GF PASS; acc 0.602356; MC not run |
| [spine_BC_sep](spine_BC_sep.qasm) · [JSON](spine_BC_sep.json) · [receipt](spine_BC_sep.result.json) | BC cat3spinered | 159 | 33 | 3.182639e-19 | 4.674921e-05 | 6.538883e-06 | 5.32881e-05 | 0.49908 | GF PASS; acc 0.500172; MC not run |
| [spine_BC_v22](spine_BC_v22.qasm) · [JSON](spine_BC_v22.json) · [receipt](spine_BC_v22.result.json) | BC cat3spinered | 153 | 45 | 2.923587e-19 | 5.19386e-05 | 1.857767e-05 | 7.051627e-05 | 0.44686 | GF FAIL; acc 0.446660; MC not run |
| `test_A` (regenerate) | A direct | 132 | 33 | 3.182639e-19 | 3.761698e-05 | 4.537546e-06 | 4.215452e-05 | 0.65111 | GF PASS; acc 0.650685; MC not run |
| `test_B` (regenerate) | B direct | 132 | 33 | 3.182639e-19 | 3.436038e-05 | — | — | 0.65111 | GF PASS; acc 0.650766; MC not run |
| `test_cat3` (regenerate) | A cat3 | 138 | 33 | 3.182639e-19 | 7.477921e-05 | 5.334675e-06 | 8.011389e-05 | 0.64267 | GF PASS; acc 0.642010; MC not run |
| [tree2_ABC_v22](tree2_ABC_v22.qasm) · [JSON](tree2_ABC_v22.json) · [receipt](tree2_ABC_v22.result.json) | ABC hybrid2t | 123 | 45 | 2.923587e-19 | 6.21679e-05 | 2.837407e-05 | 9.054197e-05 | 0.53732 | GF PASS; acc 0.537277; MC not run |
| [tree2_BC_v22](tree2_BC_v22.qasm) · [JSON](tree2_BC_v22.json) · [receipt](tree2_BC_v22.result.json) | BC hybrid2t | 123 | 45 | 2.923587e-19 | 4.116381e-05 | 1.777025e-05 | 5.893405e-05 | 0.55819 | GF PASS; acc 0.557755; MC mean 6.038067e-05 |
