# Remaining search-cost decisions on current HEAD

Pin: `0ff9423a8e69c13998ab1baf7bf09c8e97558a60`.

## Candidate 2: optimize planning plus contraction, not contraction work alone

Current `MAIN/sparse/sparse_walsh.py:compile_best` calls `search_basis` for every saved warm start, with the default 1,000 proposals each. It unconditionally pays for this search even for an acceptance-only evaluation. The criterion only minimizes `(work_entries,width)`. It does not charge planning time, the number of requested moments, or expected reuse.

On the exact current v36g input:

| Method | Planning | Width | Work proxy |
|---|---:|---:|---:|
| Current two warm starts, 1,000 proposals each | 11.943 s | 8 | 2,113 |
| Both warm starts evaluated, zero new proposals | 0.316 s | 8 | 2,195 |

The default spent roughly twelve seconds to remove 3.7% of the warm plan's proxy work. This is a current objective mismatch, not a claim that detector-basis search is unnecessary in general.

With the analytical channel factors, the four-worker wrapper using zero new proposals completed all 73 moments in **6.118 s**: preparation 0.644, planning 0.316, character compilation 0.005, contraction 5.154. Maximum absolute moment difference from the original evaluator is **7.66054e-15**. L was **3.836054467100216e-5**, versus baseline **3.836054467100275e-5**; the difference is numerical roundoff. `portable_warm_only_validation.json` is the comparison receipt.

The separately run default-search wrapper took 16.939 s, including an optional factor-construction ABBA microbenchmark of about 0.614 s. Host load and different elimination plans affect timings, so this is not a matched end-to-end speedup guarantee. The deterministic improvement is avoiding 2,000 proposal evaluations on this circuit while retaining width eight and exact moment semantics.

Implementation:

1. Compile/check saved bases first.
2. Estimate total evaluation cost for the requested number of moments and expected reuse count.
3. Search a new basis only while plausible contraction savings can amortize the extra planning cost.
4. Cache validated transforms/plans by a complete semantic graph signature, not only circuit filename. Probability-only counterfactuals can often reuse exactly the same graph.

The first adoption gate is a workload of actual current candidates, including acceptance-only screening. Compare all moments and total wall/CPU cost. Warm-only is a demonstrated v36g setting; do not disable search for arbitrary new graphs.

Run the supplied wrapper with `--basis-trials 0` to reproduce the witness. Omitting the option preserves the upstream proposal count.

## Candidate 3: choose racing families by official-key success per compute

Current `race.py` takes a single stem, while the plan promotes the best expected-loss stem into the hourly race. Within a stem, racing is already implemented and should not be proposed again. The remaining choice is **which physical families deserve the racing budget**.

For a fixed official threshold t, let q_j(t) be a valid candidate family's probability of producing a completed score below t, and c_j(t) its expected CPU cost per attempted variant including preparation and early dropping. The operational target is q_j/c_j, with updates as the threshold moves. Lower expected loss alone does not determine this rate: variance, acceptance, setup/runtime, and drop behavior also matter. For a fixed nonadaptive policy and independent attempts, the probability of at least one success after n attempts is `1-(1-q_j)^n`; the fixed-budget comparison follows directly.

This is particularly relevant for v36f versus v36g. Their expected losses differ by only 1.551731513294e-8, while their circuits have 293 versus 320 CX and different acceptances. That does **not** prove v36f races better: gate count is not a reliable runtime measure, and published speed measurements came from different loads/hosts. It makes the comparison cheap and worthwhile before concentrating all race resources on either family.

First gate: run a balanced pilot on identical hosts and disjoint variant IDs for v36f, v36g, and optionally a cheaper near-incumbent. Measure per-chunk distributions and total CPU, then evaluate current and one-next-key thresholds using an independent pilot/validation split. Allocate race work by measured valid winners per CPU and keep actual completed official checks. Continue choosing physical research incumbents by expected loss; do not redefine a sampled minimum as a physical improvement.

No race experiment or improved score is claimed here. The proposal is a finite-budget selection extension, distinct from the existing single-family early-drop policy and the previously proposed control-variate estimator for expected-loss differences.

## Correctness issue to fix while integrating

`INTEG2/ev2.py:one` keys its result only by QASM SHA256, omitting output-qubit metadata, evaluator version and numerical settings. More immediately, `INTEG2/greedy.py:run_prices` skips calling that hash-aware function whenever a name already has a loss result. Rebuilding an existing candidate name can therefore reuse stale prices. This does not prove that any reported finalist is wrong; the public closures were independently rechecked. It is a concrete cache invalidation hazard to remove before reusing these builders for a new lane.

The greedy implementation also filters the menu by positive isolated base gain, permanently marks non-improving current moves dead, and stops when its first K candidates do not improve. Its own report accurately labels menu exhaustion as inferred beyond the tested singles, greedy chain and swaps. The large +1.43e-6 interaction of about 27 combined trades is positive evidence that a monotone, context-independent menu is incomplete; a bounded connected multi-edit search is a separate physical-search task.

Sources: current `work/race.py`, `work/lanes/INTEG2/{ev2.py,greedy.py,REPORT.md}`, `work/lanes/MAIN/sparse/{sparse_walsh.py,basis_warm.json}`, `docs/PLAN.md`, `docs/FINDINGS.md`. Pinned source copies are under `source/`.
