# Source and ending decision experiment

## Decision

The current evidence favors **native co-design of the final checking instrument,
its resource preparation, and its incoming state**, with complete noisy loss as
the objective. A grid-free source remains a useful diagnostic but does not earn
an open-ended embedding effort merely by having a low abstract score.

The new crossed experiment strengthens that decision. Changing the ending
improves the two-Bell source by 4.3174651e-6. Adding two further logical checks to
that source improves the square-ended circuit by only 3.6235207e-9 while adding
16 CX gates. Cheap B-verification designs eliminate every harmful single fault
yet have substantially worse full loss.

The experiment completed **24 source/ending prices and four affine-frame
terminal-reuse controls**, all complete noisy abstract circuits, not new native results.
All actual resets, preparations, gates, reads, and waiting noise are included.
Only the 6x6 adjacency requirement is relaxed. There is no claim of a submission,
native performance improvement, SOTA, or a globally best architecture.

## Experiments completed

`cross.py` crosses three independently specified source constructions with five
endings. It rebuilds the complete deterministic detector space of each actual
circuit and checks the raw state using the official exact simulator before
decoding. Every raw-valid circuit is priced at all orders. Harmful singles are
recorded as a diagnostic; they are never used to veto an otherwise raw-valid
all-orders price.

The sources are two interleaved Bell checks, four interleaved Bell checks, and
two interleaved three-member cats with coordinate loads 1/3/3. They include the
actual noisy injection and both physical prechecks.

| Source | Ending | CX | Ticks | Exact loss | Acceptance | c1 |
|---|---|---:|---:|---:|---:|---:|
| Bell2 | Original |107|19|3.441123040187426e-5|0.7828018721|0|
| Bell2 | Square |114|19|**3.009376529596726e-5**|0.7769742239|0|
| Bell2 | No C |91|19|3.126807870430824e-4|0.8056761061|0.2333333|
| Bell2 | Compensated six square |117|19|2.969251549492645e-4|0.7809676137|0.2333333|
| Bell2 | Compensated four square |111|19|3.035624432131055e-4|0.7805454855|0.2333333|
| Bell4 | Original |123|19|3.419374457407645e-5|0.7739680055|0|
| Bell4 | Square |130|19|**3.009014177531279e-5**|0.7682057621|0|
| Bell4 | No C |107|19|3.123615681177935e-4|0.7965829089|0.2333333|
| Bell4 | Compensated six square |133|19|2.967179613250126e-4|0.7721540812|0.2333333|
| Bell4 | Compensated four square |127|19|3.034780361524284e-4|0.7717364650|0.2333333|
| Cat 1/3/3 | Original |109|18|3.461949073397834e-5|0.7801589539|0|
| Cat 1/3/3 | Square |116|18|**3.043012985456136e-5**|0.7743510268|0|
| Cat 1/3/3 | No C |93|18|3.128303539730393e-4|0.8029556062|0.2333333|
| Cat 1/3/3 | Compensated six square |119|18|2.970053190462892e-4|0.7783299496|0.2333333|
| Cat 1/3/3 | Compensated four square |113|18|3.034886101004815e-4|0.7779089579|0.2333333|

The square uses actual positive A and C encoded resources, an actual zero B
encoder, the two square interaction layers, and actual readout. The compensated
constructions use actual shortened-C encoders and the actual inverse BC
pre-entangler, retaining its noise and duration. Their simple B preparation
leaves seven harmful fault components. These failures concern the constructed
resource encoders, not every possible preparation of those resource states.

The original controls reproduce the earlier CAT3 and CATREVIEW3 all-orders
numbers to the printed precision. None of the exact evaluations removes noise
channels or uses ideal resources.

## Why a single-fault objective is insufficient

In the no-C family, all seven harmful components arise from the final two B
encoder layers. Measuring either logical-Z line {1,4,6} or {2,3,6} detects every
one. A physical helper uses one reset, three B-to-helper CXs, and a Z read.
Both lines were also measured together with independent helpers. The B encoder
starts two ticks earlier; all waiting is charged. The 1/3/3 source receives one
real extra clock because its B precheck otherwise occupies that slot.

All nine physical flag variants have exact raw correctness and c1=0:

| Source | One flag {1,4,6} | One flag {2,3,6} | Both flags |
|---|---:|---:|---:|
| Bell2 |8.122221632865516e-5|8.121495549813589e-5|5.797645110439802e-5|
| Bell4 |8.098488408407786e-5|8.098110969315193e-5|5.777230082832518e-5|
| Cat 1/3/3 |8.191721003405077e-5|8.191113289077465e-5|5.866225959711668e-5|

The best of these remains far worse than the incumbent and the square controls.
This directly demonstrates why cheaper resource preparation and zero harmful
singles cannot stand in for the complete conditional noise objective. These
small flags suppress a dangerous single-fault class while leaving the broader
accepted residual distribution costly.

## Replacing the last idle using the measured resource

`reuse_final.py` tests a distinct terminal instrument requested during the
review. In the Bell2 control, A is read in Z at round+1, B couples into D at
round+1, and B is read in X at round+2. The candidate uses the measured A
qubits as controls of seven A-to-D CXs at round+2. Its final data idle is thus
replaced by an actual two-qubit interaction, with no additional clock.

The measured A bit string lies in the classical Steane code. The stabilizer
part of that codeword acts trivially and its logical coset is removed by
`FRAME_X(0)` on the parity of all seven A measurements; `FRAME_Z` is zero.
The official exact checker includes this declared frame and verifies the raw
output before syndrome decoding. All six raw stabilizers remain +1.

| Complete abstract instrument | CX | Exact loss | Acceptance | Harmful singles |
|---|---:|---:|---:|---:|
| Ordinary Bell2 control |107|3.441123040187426e-5|0.7828018721|0|
| Reuse measured A, logical X frame |114|**4.707090637637821e-5**|0.7828018721|0|
| Reverse order control |107|5.935879665627128e-4|0.7843152434|7|
| Reverse order, reuse measured B, logical Z frame |114|6.495034517477272e-4|0.7843152434|7|

The reverse order places B-to-D before D-to-A, reads B in X one clock before
the end, and then uses D-to-B at the final clock. The Z frame is the parity
of the seven B X outcomes. Both reverse-order circuits are raw-valid, but
their unchanged A preparation leaves first-order loss 0.0004666667 at
p=0.001. Their failure is not a general exclusion of reverse-order endings.

Measured-A reuse is a valid accepted instrument, but its full loss worsens by
36.79%. The exact calculation includes the official postmeasurement
depolarization on the reused qubits, final CX noise, detector correlations,
and noisy frame records. Removing an output idle therefore does not by itself
establish a cleaner terminal channel. The frame-aware evaluator reproduces
the ordinary control exactly and is isolated to this lane's process; neither
the shared frontend nor the official judge is modified.

The raw oracle bypasses only physical adjacency validation because these
circuits are abstract. It calls the unmodified official `verify` with absolute
record indices for the actual frame and separately checks all six raw
stabilizers. Finite-p evaluation uses the existing FRAME20261027 lane-local
frame implementation with the pinned sparse-Walsh contraction. The aggregate
kernel omission diagnostic is 3.66e-13; it is not a symbolic roundoff proof.

## Native overhead budget

The verified native comparison is the phase candidate with loss
3.568127239134716e-5. Relative to it:

- Bell4 square has a 15.67% abstract gain.
- To retain a 10% native gain, its complete localization, extra waiting,
  resource verification, and any decoder changes may add at most
  **2.023003377e-6** of loss.
- A 20% gain requires loss <=2.854501791307773e-5. Every source-ending circuit
  in this bounded experiment already exceeds that target before localization.
- Bell2 square is preferable to Bell4 as a native construction seed unless the
  latter maps materially better: the abstract loss difference is only
  3.6235207e-9 and it requires sixteen more CX gates.
- The one-clock-shorter 1/3/3 square has 3.3628806e-7 more abstract loss than
  Bell2 square. It may still be preferable if its native topology saves that
  much loss. An abstract score alone cannot decide that tradeoff.

No universal nonnegative routing-penalty theorem is asserted here. A new native
design may change the instrument or exploit beneficial noisy channels. The
budget above is a practical exact-loss target for any complete implementation.

## High-level recommendation

1. Start from candidate **native final checking layers**, retaining the true
   logical output and detector contract. Synthesize preparation and input into
   that footprint, rather than asking a router to preserve a finished abstract
   circuit.
2. Compare complete accepted instruments: incoming residual distributions,
   resource verification, waiting, final readout, and accepted record sectors
   must be optimized together. Perfect resource or c1-only objectives miss the
   mechanisms measured here.
3. Use beam or population search for architecture, qubit lifetimes, output
   placement, code-coordinate permutation, and destructive measurement/reuse.
   Use small CP/SAT subproblems for local exact synthesis or schedule repair.
   Replacing CP-SAT alone while preserving a restrictive search grammar would
   retain the same limitation.
4. Keep grid-free designs as headroom tests. Continue a native construction only
   when its measured loss budget can still reach a meaningful target. The
   two-Bell square is a compact comparison case, not evidence it is the global
   best family or that its encoder fits on the grid cheaply.
5. For a target beyond 20%, the present result calls for a better final resource
   and accepted measurement instrument, or a different joint source/ending.
   More repetitions of the same Bell checks do not supply that gain.

## Reproduction

From the repository root:

```bash
.venv/bin/python work/lanes/STRATEGY_CROSS_20261027/cross.py --workers 2
.venv/bin/python work/lanes/STRATEGY_CROSS_20261027/cross.py \
  --endings bflag146,bflag236,bflag_both --workers 2 --output bflag_results.json
.venv/bin/python work/lanes/STRATEGY_CROSS_20261027/reuse_final.py
```

Every process completed. `cross_results.json`, `bflag_results.json`, and
`reuse_results.json` hold the complete row summaries. `cand/` contains the generated full QASM circuits,
raw/first-order/all-orders receipts, and output specifications. Exact receipts
include the pinned evaluator identity, QASM hash, and analytic kernel omission
bound. The generator writes only this lane and does not modify the shared
evaluator, official judge, production circuit, or submission process.
