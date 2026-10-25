# Implementation instructions for the v36g review

## Objective and evidence standard

Work from the current repository after checking its actual HEAD. The reviewed code at `0ff9423a8e69c13998ab1baf7bf09c8e97558a60` is unchanged in final checked HEAD `157d48d12c10dc06bc6bebc79adc3f8c64e6d6a3`; that last commit only updates PLAN/SOTA and switches the documented race stem to v36g.

The physical reference is v36g: L=3.836054467100275e-5, A=0.5015149656065663, 320 CX, native depth 47. Match its QASM SHA256 before using the supplied evidence. Keep the official judge unchanged. Treat source-local host paths and operating instructions as context, not as a requirement to reproduce this review on those hosts.

This package contains two implemented evaluator optimizations and eight gated extensions. It does not contain a new physical winner. Do not promote any supplied RCCX, endpoint-W or resource-deletion diagnostic circuit.

For physical comparisons, price unnormalized A and N before taking L=N/A. Preserve the ordered output-qubit mapping. Account for all native idles, first-use preparation, reset/readout effects, detector references and frames. Confirm ideal accepted T_L and class with the unchanged official checker. Track sparse omission separately from floating roundoff. Use independent full reevaluation of promising finalists; the official sample minimum does not establish a lower expected loss.

## Stage 0 Reproduce and repair result identity

1. Run `verify_package.py --evaluate` in the supplied environment. All 73 moments must agree with the original result to the stated 1e-12 regression tolerance; observed max difference was 7.66e-15.
2. Fix `INTEG2/greedy.py:run_prices`: an existing filename must not bypass semantic hash validation. Every result lookup goes through a content-aware function.
3. Extend the result key beyond QASM: ordered data JSON, evaluator/frontend/judge-subset semantics, p/cutoff settings and extension version. The portable wrapper's `(qasm_sha256, semantic_context_sha256)` is an example. Runtime overrides must enter the actual context, not just a source-code hash.
4. Include the exact accepted bundle in candidate identity. An invalid edit must fail an all-or-nothing bundle; silently applying only a subset changes the experiment.

There is no evidence that the current published finalists are corrupted. The cache repair prevents a concrete hazard in a new lane.

## Task 1 Analytical Pauli factors

Implementation is ready in `audit/review11/evaluator/channel_algebra.py` and `character_eval.py`.

- Compile the full propagated signature image, including kernel, residual detector and observable bits.
- Preserve the strict equal-probability guard. Near-uniform, non-subspace and unsupported factors use the original implementation.
- Keep both characteristic levels `p0+n*p_term` and `p0-p_term`. Keep nonunit constants. Never replace approximate normalization by 1.
- Merge only equal full signature images; retain physical source-channel provenance outside this compressed representation.
- Integrate at the factor/compiler boundary and compare every moment on actual current variants, including unsupported fallback examples.

Guaranteed property: algebraic equivalence over real represented inputs under the guards. No bit-identical floating-point or universal wall-time guarantee. Measured structural reduction on v36g: 692→438 factors, 5580→1011 summands/predicates.

First deliverable: a minimal integrated patch plus a workload report showing semantic equality and total evaluation throughput. Stop broad optimization after this gate; do not add unrelated evaluator rewrites.

## Task 2 Amortized planner

Current `compile_best` pays two 1000-proposal warm searches even for acceptance-only calls. On v36g, saved bases alone retain width 8 and work 2195; the full search reaches 2113 after roughly 12 s of planning.

First evaluate saved bases, then choose extra search budget using total expected cost: planning + requested moments × reuse count × contraction. Cache plans by an adequate semantic graph identity. Do not disable search globally merely because zero trials worked on v36g.

First deliverable: acceptance-only and full-score current-candidate benchmarks, including setup/planning time. Adopt only if useful workload throughput improves without a worse fallback for changed graphs.

## Task 3 Current BFLAG decoder-safe residue search

Keep the current ideal B/C endpoint. Change the allowed accepted single-X residue contract, not the resource state itself. Replace hard `s=0` by decoder-safe signatures `{0,9,10,11,12,13,14,15}`; equivalent to `s3=OR(s0,s1,s2)`. The exact 128-pattern certificate and CP-SAT clauses are supplied.

At the same time, include `X2leak` in proxy diagnostics and rank candidates with full current exterior A,N. Old FRESH relaxed-residue builds lost because a correctable accepted residue combines with a later error. The old proxy is not a valid ranking objective after enlarging this space.

Start with one 4–6-wire, 3–5-layer window around current r3, retaining r3 as feasible incumbent. Retain full-circuit first-order decoder safety for this first bounded experiment; this is a search policy, not a contest rule. Price a small Pareto set. The 1596 one/two-CX deletion census found no new accepted-residue witness and supplies no winning candidate.

First deliverable: a fully routed endpoint-correct candidate and full-price comparison, or an explicit finite-window closure. Stop if the first corrected-objective window supplies no candidate with useful headroom. Do not restart the failed older R45 architecture under a new name.

## Task 4 B/C preparation plus verification Clifford window

Join the last preparation layers and the fixed B→C layer at tick 44. Keep final ideal endpoint `|0_L>_B |0>_C^7` and the actual B→D/readout exterior. Do not insist on the old pure correlated state at tick 43.

First implement the joined window with CX-only propagation if convenient: endpoint generator columns are code columns on B and zero on C; endpoint X-fault signatures use literal C output bits. Preserve tick 44 A coupling and reset occupancy. Then extend a 4–6-wire window to a complete symplectic H/S/CX representation.

An already-charged idle is available only if the unchanged official native compiler confirms the same time and noise slot after insertion. First-use, terminal measurement release, barriers and RX/MX folding matter. Reject a pure isotropic-noise frame gauge as a non-improvement.

First deliverable: one physically distinct exact ideal boundary-instrument witness, checked on boundary Pauli inputs and records. Then check class, single faults and full L. Stop a broad solver effort before this witness exists.

## Task 5 Joint A encoder decoder and data guard

Change the module boundary, rather than merely applying Task 4's larger gate alphabet. Current q16 guard at ticks 38–40 and q14–q20 pair at 40–41 are inside the nominal A preparation region. AENC's old CX-only optimum and 128-class table were for a fixed v36c exterior.

Build a sufficient boundary carrying data/ancilla Pauli information, quantum inputs/outputs as required and all classical records used outside. Reproduce current v36g and simple actual edits before using the model for ranking. Do not assume the old 128 A-only classes remain sufficient in the presence of crossing data–A interactions.

Then synthesize one 4–6-wire region spanning preparation/guard and decoder or flag operations. Preserve its ideal accepted quantum/classical map while improving the noisy channel. Charge removed gadgets and added waiting in the whole circuit.

First deliverable: sufficient-boundary certificate + baseline reproduction, followed by one combined witness. Stop if the boundary is not computationally manageable or the supposed improvement only moves a cost outside the region.

## Task 6 Fourteen partially coherent C contracts

Use the supplied 16-subspace enumeration and take the 14 cases with k=dim(V)=1 or 2. Resource `R_V` must map under B→C to `|0_L>_B |V>_C`. This changes the ideal C state/readout; it is distinct from Task 3's accepted noisy B residue.

All single X_C/Y_C remain detectable by the remaining Z stabilizers. X(V) sees single Z_C on 4 or 6 sites. The restricted second-order terminal gain is about 0.991–1.009e-6 or 1.482–1.493e-6, with ideal resource/readout. This is not a full-score prediction or universal upper bound.

First build and price ideal instruments on the current v36g boundary. Then jointly synthesize the preparation and actual complementary stabilizer readout. Measuring all GHZ members in X destroys retained Z information and is not the required instrument. Current C geometry is disconnected; account for helpers, routing and output waiting. An extra global tick may erase the gain.

First deliverable: one complete readout-priced routed candidate, or an explicit fixed-layout cost failure. Stop cases whose actual readout cost consumes their mechanism. Do not label a fixed-layout failure universal.

## Task 7 Nonmonotone connected bundles

Remove only the unsound coverage assumptions: positive isolated-gain menu filtering, context-independent permanent dead flags, and stopping after a losing first K while later candidates remain unseen. Keep useful cheap legality checks.

Define a finite neighborhood by shared helpers, overlapping windows or common propagated signatures. Enumerate connected 2 and 3 edit bundles, including remove-one/add-two and negative-single combinations. Record attempted and rejected bundles. Require all-or-nothing application and semantic cache identity. Price full A,N in the current exterior.

Optionally follow with a small beam, but call it heuristic. Harmful 27-trade interaction proves nonadditivity, not beneficial synergy. Only an exhausted finite neighborhood supports a closure statement.

First deliverable: the exact enumerated neighborhood, all prices and either a legal winner or a scoped no-win result. Stop after the agreed neighborhood before inventing more random-search budget.

## Task 8 Four-T record logic after a favorable policy oracle

Keep the measured-classical RCCX primitive; reject the supplied first placement as a performance candidate. Its ideal AND truth table and 47-tick 19-T physical placement are valid. Format/class/ideal checks pass. Its 100k noisy acceptance is 0.49862; its cost-free NAND policy already raises L by 3.0779e-9.

For another pair or small record set, compute Boolean-policy coefficients with `boolean_policy.py` and combine zero-reference relaxation A,N. All input evaluations must have the same physical circuit/schedule and all other detectors unchanged. Propagate signed-combination omission bounds. Do not average L or call the oracle a universal normalized-loss bound.

Only implement a policy with enough direct L gain or a specifically valuable acceptance trade. Prove relative phases remain invisible in the final record sectors with no later recombination. Previously Z-measured controls and a measured target are the supplied sufficient case. Charge measurement/carrier discrepancies, added gates, idles and non-Clifford simulation costs. 20 T is an internal sparse cap, not an official rule.

First deliverable: favorable exact policy table, then a complete noisy realization. Stop before a large 19 T contraction when the cheap policy provides no use.

## Task 9 Open-boundary response tables

Keep the validated old v36c boundary as the first target. Instead of 128 separate exterior queries, retain boundary bits as output indices and contract once per required observable/kernel. Do not claim the entire 73-moment score is one contraction without separately implementing batching.

Prove the linear decomposition and compare every class's A,N with the existing table. Measure induced width, peak memory and complete table time. 128 outputs do not imply 128× speedup. Batch subsets of boundary indices if retaining all is too expensive.

Only then expand to current v36g, after Task 5's sufficient-boundary proof. A general subcircuit may need a process tensor with incoming and outgoing Pauli/record indices, rather than an independent probability vector P(c).

First deliverable: exact old 128-class reproduction plus a real cost benefit. Stop or use hybrid batching if width/memory destroys the benefit. This work improves evaluation cost, not physical L.

## Task 10 Valid key wins per compute across physical families

Do not propose gate-permutation racing, threshold sharing or early drop as new: they are implemented. Run a balanced pilot comparing v36f and v36g on identical workers with disjoint variant IDs. Include setup, early drops, completed checks, acceptance and validity in cost and success. A win follows the official 3-significant-digit key and CX tie rule, not just raw score<t.

Estimate q_j/E[C_j] with uncertainty and held-out validation. In a repeated stationary IID policy this is inverse expected CPU to first valid win. It is not an optimal finite-horizon adaptive policy proof. For deterministic costs, independent finite-budget success depends on `-log(1-q_j)/C_j`. Variant correlations and rare-tail calibration matter.

First deliverable: a pilot table and justified allocation, or an explicit insufficient-evidence result. Keep research incumbents ranked by expected L. No family-win or improved official score was measured in this review.

## Closed or negative directions to preserve

- T14 `t14a`: L 1.73021e-4 on v36c suffix. The rank 4 phase identity did not preserve the fifth-coordinate fault flagging benefit.
- Endpoint S on all outputs plus FRAME_X(1): exact v36g L 4.5464344742292077e-5, +18.52%, same A/depth/CX.
- Old v36c partial-rank detector screen: all 2824 proper subgroups lose even with free arbitrary sector-dependent Pauli frames under the three saved tail models. This does not close other boundaries.
- First NAND/RCCX placement: negative cost-free loss trade and failed sampled acceptance; keep only as a primitive/placement certificate.
- Simple current r3 one/two-CX deletion census: no new accepted-residue witness.

## Lower-bound and rule interpretation

The retained two-tick proof certifies true expected decoded loss>=1.162e-5 under the inspected STANDARD model and ideal-output requirements. The 7.44545e-6 last-tick-only relaxation omits compulsory previous noise. A below-threshold lower bound would not itself prove achievability. Finite selected Monte Carlo outcomes are a different quantity.

Do not promote regional perfect-noise ablations to universal redesign bounds. Postselection and correlations can change. The measured-helper terminal-class floor has its own assumptions; changing the final instrument requires a new analysis.

Official freedom includes A0<1, random-outcome POSTSELECT, nonzero deterministic references, affine logical X/Z frames, partial barriers, arbitrary ordered output cells and allowed 1q Cliffords. None gives arbitrary Boolean annotation or conditional quantum gates for free. Official time limit is 1 hour; the team's 20 s/1m-shots gate is a calibrated local proxy. Check actual processability and runtime before promotion.
