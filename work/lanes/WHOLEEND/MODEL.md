# WHOLEEND model, scope and reproduction

The explicit numerical gates govern this lane. No new candidate passed its last gate.
The final table distinguishes complete v37c from experiments with ideal resources.

## 1. Penultimate-CX floor

Let p=1/1000, q=p/5. BOUND factors independent D1(q) from every output and
final-CX helper immediately before the last native tick. For an output without
a penultimate CX, its independent factor strengthens to D1(p): an idle or local
gate supplies it directly; reset/first-use preparations admit a nonnegative
residual preparation-flip probability. The helper factor remains D1(q).
The six output types are, for q_D in {q,p}:

- local final operation: D1(p) composed with D1(q_D);
- final helper→output: D1(4p/5) composed with D1(q_D) and B_X(2q/3);
- final output→helper: the same with B_Z(2q/3).

The final output–output-CX and separable-output exceptions remain excluded by
BOUND's separate arguments, whose thresholds exceed every gate here. Independent
extracted factors cannot be conditioned away by disjoint records; arbitrary
logical input direction and all 64 incoming syndrome sectors are optimized.
`src/floors.py` evaluates all 6^7 assignments by Walsh transforms, then verifies
each winning moment with BOUND's direct rational 4^7-Pauli sum.
`src/exact_floors.py` independently enumerates 2,766 GL(3,2) assignment orbits
and computes every sector moment with integers, covering all 279,936 assignments.
The certificate records each orbit's maximum numerator and the common denominator.
This is a necessary condition, with no attainability assertion.

## 2. JIT tree

`build_tree.py` solves a 35-role exact-cover placement on 36 cells and synthesizes
A=|+_L>, E=|0_L>, and correlated B/C by grid-only binary elimination. Its generated
X-row space is checked against the specified CSS target, including the spare
helper returning to zero. Reverse scheduling sets E's deadline to R, A/B/C to R+1.
The spare helper is measured at R+1. Native timing and every non-data-preparation
CX contact are checked separately; the initial ideal data encoder is abstract.
All ancillary gates, resets, waits and reads are noisy. Only data preparation
and storage before R are ideal in the real-preparation tail experiment.

The two `_delayed` QASMs are retained rejected attempts: a helper read at R
collided with its last preparation gate, and native ASAP added a tick. Their
prices are valid for those saved circuits, but they do not implement the intended
three-tick ending. Corrected QASMs and prices are separate, content-keyed entries.

## 3. T-only contracts

`tsearch.py` builds the exact 2×2 Kraus operator for every logical measurement
branch, tests whether some affine X/Z frame maps T to T, then distinguishes
K proportional to I from T-preserving nonidentity K. Positive X/Y/Z resource
eigenstates are enumerated over all directed orientations of three graphs.
All 6^3 signed resources are additionally checked for the reviewer's square.
The search has fixed output D and X/Z terminal reads; it does not enumerate
all entangled resources, intermediate measurements, local Clifford layers,
T-bearing resources, or arbitrary unmeasured endings.

The per-index second-order formula is valid for these encoded resources:
individual flipped read bits fail Hamming syndrome checks; two faults at distinct
indices can pass only if their record flips separately vanish. Same-index pairs
are corrected. Therefore the coefficient depends on the propagated zero-record
Pauli rates, not the particular ideal T-preserving contract. All six contracts
at the minimum coefficient were priced exactly; no finite-p global optimality
claim is made for the unpriced higher-coefficient contracts.

The incoming tests keep the backwards causal cone of v37c's data and completed
prefix detectors through tick 43. Resource preparation begins only after each
cell is released. Its noise, and only the data wait between the cut and round,
is made perfect. Earlier prefix noise remains intact, including noise on reused
resource cells before their ideal resets. Actual native times match written
barrier times. These experiments isolate the incoming error distribution and
are not feasible complete preparations. Ordinary square uses the same prefix.

## 4. Whole-grid backwards search

A CP-SAT matching chooses distinct unmeasured helpers controlling the seven final
outputs. For 48 sampled layouts, zero or one output is moved to a neighboring
cell. The other 22 cells are read in independently selected X/Z bases at the
final tick. Where available, cell 21 is constrained to interact with different
code indices in the preceding layers. Other grid edges remain free.

The two or three earlier layers are synthesized backwards. For every possible
CX or idle, all native Pauli components are propagated through the already fixed
suffix. A component with zero detector flips and nonzero decoded loss forbids
that option. CP-SAT then selects a disjoint matching minimizing its pair cost
against the fixed suffix plus a small single-rate proxy and seeded tie perturbation.
The first sweep requires all outputs active in every earlier layer. The broader
sweep constrains only k≤3 in the penultimate layer, using step 1. Final matching,
read bases and the sequence of layer choices are heuristic; per-layer OPTIMAL
statuses do not certify the joint circuit optimum. Neither sweep was stopped
by a solver timeout.

Every resulting complete tail receives an explicit all-channel fault-pair sum,
including measurement flips, idle derivatives and same-channel exclusions.
The two leading depth representatives receive all-orders pricing and a separate
native frontend pair audit. Searches are not limited to seven identical gadgets;
`artifact_audit.json` records how many outputs share interaction components.

Back-propagating six output stabilizers and the 22 individual record operators
gives 28 commuting independent boundary stabilizers. Back-propagated logical X/Z
specify encoded T, leaving seven gauge qubits. A pure witness fixes those helpers
and prepares the inverse Clifford of final encoded T plus read-basis eigenstates.
All inverse preparation noise is omitted for the optimistic gate. The gate fails,
so no claim of a cheap noisy preparation, let alone a full-circuit gain, follows.

## Verification and reproduction

`price.py NAME N` prices `builds/NAME.{qasm,json}`; metadata specifies the noise
counterfactual. It records QASM/output order and evaluator hashes, A, L, J_tau
relative to v37c, and harmful native single faults. `verify.py` independently
checks organizer raw correctness, schedules, and 17 tail pair coefficients.
`collect.py` validates every QASM hash, grid prep/tail contact, boundary rank,
J_tau value and report size before emitting `results.json` and `REPORT.md`.
The local affine-frame evaluator adds S/Pauli Clifford propagation and constant
frame bits to BCV's copy; organizer exact checks verify all generated contracts.

Run research only on owl inside the authorized Docker image, with the identical
absolute lane path, user 1010:1012, HOME=/home/jihoon, --cpus=16, and all OMP/BLAS/MKL
thread variables set to 1. Use the repository .venv/bin/python. `run_batch.py`
uses ten evaluator children sequentially by circuit (thirteen Python processes
including driver/batch/price at most); do not overlap multiple batches. Read the
saved counterfactual metadata before interpreting a price as a full-circuit result.
No reviewer code was executed. BOUND/ENDSEARCH/BCV machinery was read or copied;
all modifications and generated files are confined to WHOLEEND.
