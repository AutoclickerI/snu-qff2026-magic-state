# END2 checkpoint: native terminal resources

This is a work-in-progress checkpoint, not a promotion report. No complete new
native circuit in this lane beats the pinned incumbent. The promising numerical
results below explicitly exclude resource-preparation noise and cost.

## Pinned comparison and public target

The reproduced incumbent v37j has exact loss 3.58709500347e-5 and acceptance
0.50101790473. The public leaderboard snapshot in `evidence/leaderboard.json`
records Placeholder at 3.0423837010265e-5, 277 two-qubit gates and acceptance
0.50059432, retrieved on 2026-10-27. No winning circuit or method is public in
the retrieved evidence. This lane has made no submission.

All computations use the shared, restored qtools package; this lane makes no
changes to qtools or the official judge. Native source preparation, abstract
ideal-resource counterfactuals and full noisy prices are kept separate.

## Complete native resource replacements tested

The initial structural replacement jointly prepares B=zeroL and C=seven zero
readouts, absorbing the old B/C encoder and final B→C layer. A source bit matters:
the original c366 measurement correlates B's final coordinate with the data.
Either carrying that variable or fixing its physical source is necessary.
Simply resetting the new B/C output destroys the raw data syndrome.

| Full native construction | Resource CX | Exact loss | Acceptance | Result |
|---|---:|---:|---:|---|
| Original v37j, c366 source changed M1@29→R | unchanged | 3.58728118032e-5 | 0.5008509091 | Raw-valid, slightly worse |
| Independent resource, source fixed | 39 | 1.76438784121e-3 | 0.5263901671 | Raw-valid, unprotected hooks |
| Carry-preserving resource | 42 | 3.23382117025e-3 | 0.5158068529 | Raw-valid, unprotected hooks |
| First-order constrained carry | 60 | 8.10336536342e-5 | 0.5163067988 | Worse |
| Source-fixed risk objective | 60 | 5.62674591608e-5 | 0.5129412133 | Zero harmful singles, worse pairs |
| Carry-preserving risk objective | 61 | 5.82813002066e-5 | 0.5139713307 | Worse |
| Verified initializations on 60-CX source-fixed resource | 60 | 5.38223231228e-5 | 0.4962974817 | Worse and fails acceptance |

The 60-CX source-fixed resource has c2=51.4133333. Its accepted resource-resource
and resource-other pairs remain too costly. These are actual complete noisy
tests, not counterfactual improvements. Their stems and audit records are under
`cand/` and `sol/`.

The exact joint counterfactual that removes noise from all 77 old resource CXs
and associated operations/attached idles gives loss 2.90214057768e-5 and acceptance
0.5596558517. The selected operation list and 115 removed channels are in
`evidence/resource_counterfactual.json`. This is nonadditive headroom, not an
obtainable gain or an allocation of error by independent region.

## Fresh-footprint modules

The 59-CX/13-layer resource in `sol/fresh_native_d13.json` was independently
verified as a positive stabilizer state and integrated by NATIVE2. It increased
that complete circuit's loss from 6.13543608706e-5 to 6.58342727275e-5 despite
removing ten CXs. The extra second-order cost is mainly resource-resource pairs.

Two actual C stabilizer gauge modules were also built and verified:
`fresh_g1_102` (57 CX, rank-one C gauge) and `fresh_g2_102_120` (59 CX, rank-two
C gauge). All 14 independent resource generators have expectation +1. Native
integration prices reported by NATIVE2 were respectively 7.729449e-5 and
7.589912e-5; neither improves its old-tail control. These finite tests do not
exclude other gauge preparations.

## Constrained incumbent geometry

`incumbent_tiles.py` enumerates anchored tile packings exactly.

* Holding the other six data coordinates fixed, moving only D16 by one grid
  edge cannot produce seven disjoint same-index squares, even with all B roles
  free. This finite result is not a global grid-packing claim.
* Across all 26 one-hop moves of any single data coordinate, exactly one final
  data assignment allows seven squares: D22→28. One layout is
  A=[7,21,18,4,8,29,22], B=[12,26,25,11,3,34,17],
  C=[13,27,24,5,9,35,23].
* With every data cell unchanged, six squares plus one tree are possible:
  A=[7,21,18,4,8,23,17], B=[12,26,25,11,3,28,15],
  C=[13,27,24,5,9,29,14]. The tree coordinate is A17–D16–B15–C14.

The six square A/B roles can be swapped independently. `partial_contract.py`
provides a pure `make_contract(mask, late_c14=True)` factory for all 64
orientations; `partial_orientations.json` records their targets. No global module
state is changed by this factory.

## The corrected six-square state contract

Omitting C6→A6 while keeping independent C=plusL loses useful record checks.
Although the ideal raw state and all single faults pass, actual incoming source
fault pairs make that naive contract much worse. The correction changes the
resource itself:

* A is plusL.
* B is zeroL.
* After the first terminal B→C layer, C is the positive CSS state with X space
  span(012,034,135,6), where digits are code coordinates.
* The input B/C state is pre-correlated by the inverse of that first B→C layer.

Equivalently, its eleven positive X generators are four A rows with code masks
85,102,120,7; three joint B+C rows with masks85,102,120; and four C-only rows
7,25,42,64. The native terminal remains D→A and B→C, then B→D and C_i→A_i for
i=0..5, followed by A Z reads and B/C X reads. All three A syndrome checks are
restored.

| Explicitly ideal resource/input scope | Loss | Acceptance | c2 |
|---|---:|---:|---:|
| Full square, terminal only | 2.55584312359e-5 | 0.9575251362 | 25.66666667 |
| Naive independent six-square resource, terminal only | 2.68631561819e-5 | 0.9609871995 | 26.97333333 |
| Corrected correlated six-square resource, terminal only | 2.59835167075e-5 | 0.9572711948 | 26.09333333 |
| Full square, actual v37j history through44 + ideal instantaneous resources | 2.83906832183e-5 | 0.5722661751 | — |
| Naive six-square, same source scope | 6.22013274815e-5 | 0.5758890396 | — |
| Corrected six-square, same source scope | 2.88477085183e-5 | 0.5721154457 | — |

The official exact simulator verifies the six output stabilizers at +1 and
zero ideal infidelity for these abstract state contracts. The full counterfactual
QASMs deliberately contain ideal nonlocal encoders and are not gate-valid
submission candidates. Only the six-square terminal edges are native. The
scripts separately remove artificial encoder-duration idles, with the precise
channel changes saved in diagnostic JSON.

NATIVE2 subsequently extracted a raw-valid 251-CX/41-tick source and measured
the same corrected ideal-resource ending at 2.74984614967e-5, acceptance
0.60373589356. Its exact released-product-state certificates and source stem
live in NATIVE2, not this lane.

## Current native implementation work

The q14 plus state is an independent factor. A stronger implementation target
prepares rank ten on the other cells while using q14 as zero workspace, then
performs a late RX14. The backward fault signatures of q14 before that reset
are zero; reset noise remains in full evaluation. This avoids carrying an
unnecessary eleventh variable through the preparation network.

`partial_cp.py` implements joint state synthesis with arbitrary initial plus
basis, native edges, release times, certified immediate reuse of released
product states, optional q14 late reset, and X/Z single- and CX-pair fault
constraints. `partial_factory.py` verifies its exact native resource map and
prices resource+terminal noise with a clearly ideal synthetic input. NATIVE2's
`partial_assemble.py` integrates solver JSON with the real source.

Initial unseeded 16/18-layer and release-constrained R45 state queries returned
UNKNOWN after their stated budgets; they are not infeasibility proofs. Root's
constructive native seeds establish state-preparation upper bounds, but their
depth does not yet fit the source windows. `partial_schedule.py` optimizes their
commuting-gate schedules exactly and rechecks first-order safety; it found only
modest reductions, with one reordering introducing a new harmful axis pair.

The active next steps are longer constrained synthesis, alternate orientations,
and lower-rank compensated partial-square contracts that retain more of the
incumbent A preparation geometry. No partially evaluated artifact is promoted.

## Reproduction

Run from the repository root using `.venv/bin/python`, with
`PYTHONPATH=work/tools:upstream/snu-qff2026-problem`. Key entry points:

* `incumbent_tiles.py` and its `one_hop_neighborhood()` function: finite geometry.
* `partial_square.py --exact`: terminal-only counterfactual controls.
* `partial_incumbent.py`: full incoming-history/ideal-resource controls.
* `partial_contract.py`: exact row target and role/terminal factory.
* `partial_cp.py --help`: state/first-order native synthesis and release input.
* `partial_factory.py SOLUTION --exact`: native resource replay and diagnostic.
* `partial_schedule.py SEED --release RELEASE_JSON`: commuting-gate scheduling.

Numerical results and scope metadata are in the JSON files. Log text is
secondary; the checkpoint manifest lists selected code/evidence with hashes.
