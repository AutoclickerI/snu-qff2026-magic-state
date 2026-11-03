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

## Reduced terminal and connected-resource continuation

The compensated four-square terminal was implemented with the unchanged data
footprint. Its ideal-resource source251 price is 2.89602322487e-5 at terminal
round 41. This was improved by removing state-identity operations: when C is an
independent plus factor at a nonsquare coordinate, B→C acts identically and its
preparation/readout can be deleted. The simplified implementation is
`terminal_variants.py`; it checks every remaining terminal edge for adjacency.

| Actual noisy source251, explicitly ideal instantaneous resources at 41 | Loss | Acceptance |
|---|---:|---:|
| Original four-square compensated terminal | 2.89602322487e-5 | 0.604349903 |
| Omit three nonsquare B→C gates, retain isolated C reads | 2.75989485900e-5 | 0.607012051 |
| Also delete the isolated C factors | 2.75989485899e-5 | 0.608836735 |
| Retain only three squares, mask 0x19 | 2.71579596960e-5 | 0.609241906 |
| No C factors or square edges | 2.71482766273e-5 | 0.613275419 |

Every row passes the official exact abstract raw-state test and has zero harmful
single-fault contribution within numerical tolerance. The first two omission
variants agree in conditional loss within 8e-17, while the independent noisy C
checks reduce acceptance. These remain counterfactuals, not native full-circuit
scores. At round 47, the no-C source251 counterfactual is 2.94933083510e-5 with
acceptance 0.5881467573. Restoring the original connected A footprint
[7,14,13,9,8,21,15] leaves the round 41 result unchanged within 1e-16.

The literal no-C terminal alone loses an important feature of the old readout:
the original final two A CNOTs measure an A logical-X parity as well as the three
Z syndrome checks. Full NATIVE2 assembly and the root pair audit identified
large A-preparation-phase/B-readout pairs when that parity is omitted. Native
work therefore now retains explicit logical readout parities; ideal resource
loss and zero single-fault loss do not suffice to rank these full circuits.

`a_only_cp.py` gives exact fixed-footprint source-compatible CSS preparations.
It found a 10-CX direct-plus A module ready at 45, and a 9-CX zeroL module with q7/q8
ready at 45 and every other cell ready at 46. The latter is supplied as
`sol/connected_zero_weak_R46_early7_8.json`, with the final H layer omitted, for
a reversed-order terminal using the connected block as B. A 10-CX zeroL module
with every cell ready at 45 is `sol/connected_zero_weak_R45.json`. Their CNOT counts
are optimal within the respective stated models. Full noisy integration is in
NATIVE2; these module proofs alone are not winner claims.

The stricter `a_flag_cp.py` requires each unflagged phase hook to be correctable
without relying on the other block's terminal readout. It found an 18-CX zeroL
module ending its CNOTs at 48 and reading its active q1 flag at 49; another 17-CX
module needs one further tick. The independent numeric backward replay checks
all constrained single and same-axis two-qubit components. Full Pauli replay of
the earlier 19-CX witness in PREFIX2 also confirmed zero harmful singles. Its
extra latency is currently a practical cost, not a demonstrated improvement.

Budgeted or bounded negative results are recorded explicitly: the rank-seven joint
measured-helper state query at 47 returned UNKNOWN after 90s; the small fixed
connected A state model with the original releases could not reach 43/44 even without a phase-hook constraint;
strict product-flag models at their stated early deadlines were INFEASIBLE.
`a_overlap_cp.py` additionally allows native phase-flag closures after D→A,
which commute with that data interaction; its tested round 46/47 constraints
were also infeasible. None of these establishes a general architecture bound.

## Logical-X herald constrained preparation and source co-design

`a_herald_cp.py` uses the final native logical-X readout as an explicit backward
phase-fault flag. For the physical A order [7,14,13,9,8,21,15], the original
readout measures X on {7,8,9}. A phase component is accepted by the synthesis
guard only when it is independently decoder-correctable or flips this herald.
The optional `--no8` also excludes pure logical phase hooks even when heralded,
because a single false herald read can otherwise produce a harmful pair. The
model includes single-qubit phase components, same-axis two-qubit components,
native edge matching, source releases, and exact CSS-state synthesis. An
independent numerical backward replay checks each emitted module. Complete
Pauli faults and the actual source remain a full-assembly obligation.

The 11-CX direct-plus witness at ready46 has q7 and q8 ready45 and satisfies both
guards. Its just-in-time variant preserves every per-wire Clifford order while
moving the initial q14→q8 CNOT from38 to40 and its resets from37 to39. Native
assembly verifies the complete raw output and zero harmful singles, but these
49-tick candidates did not improve the incumbent; at the originally completed
record contract, acceptance was below0.5. Record-mode completion and newer
source timings are handled and priced in NATIVE2.

Strong ready45 queries on the original source and the early-read source were
infeasible within their fixed seven-cell models. Allowing measured helper
products on q0/q1 did not restore feasibility in the tested projective model.
Alternative native two-layer logical-X lines {7,13,14} and {8,14,15} were also
infeasible with their required early ports. A weighted soft-guard query on the
original line gives a 10-CX optimum with residual phase cost12/15; this is a
first-order proxy, not a full logical-loss estimate or an improvement claim.

The early-read source advances M7 from40 to39 and MX14 from36 to35. A separate
249-CX source additionally removes the ideal-identity CNOTs9→10@38 and13→19@39
and advances their final source measurements. Its ideal-resource round41 loss
is2.71853567749e-5, acceptance0.6140116590, compared with2.71482766273e-5 for the
251-CX source. This is an explicitly ideal-resource diagnostic, not a native
candidate price.

`source_product_boundaries.py` now constructs actual source variants and calls
the official exact product-state certificate for each released nondata cell.
The CP reads that certificate through `product_states` instead of assuming the
original source's preparation axes. Every source in the following table passes
the raw six-stabilizer test with zero ideal infidelity. Solver results refer to
ready45 with q7/q8 ready44, the logical-X herald guard, and the no-logical-hook
guard. All listed solver processes exited successfully.

| Concrete source boundary | Source CX | Strong A query |
|---|---:|---|
| Original early-read source, M15@40 removed |251|INFEASIBLE,0.482s|
| Native q9 plus input at40, M15 retained at40 |241|INFEASIBLE,0.406s|
| Native q9 plus input at40, M15 omitted |241|OPTIMAL11CX,0.806s|

The native q9 construction retains its source record using a physical noisy H9
at38 followed by native MX9 at39. It also removes the identity13→19@39 and moves
M7 and M13 to39, on PREFIX2's retimed243-CX source. Its new encoder is
`sol/a_herald_R45_early7_8_no8_earlysource_native_m9_drop15.json`. It has three new
RX operations, reuses the certified source products on7,13,9,15, and finishes
q7 at44, q8 at43, and all cells by45. Its native CNOT structure differs from the
previous shifted witness. NATIVE2 completed its 375-CX, 48-tick integration:
raw output passed, full harmful-single coefficient was zero, and c2 was
35.01333333. This diagnostic does not establish a lower all-orders loss.

The earlier attempted M15-only experiment had failed before constructing its
boundary file. That failed attempt has been replaced by the reproducible source
builder and completed query above; the old FileNotFoundError is not treated as
a solver result.

## Alternate logical-X line and the complete 47-tick construction

The source changes make a different readout line useful: X on physical cells
{8,14,15}. Its decoder is CX14→8 followed by CX15→14 and MX15, with the other
six A cells read in Z. The early data taps are into A8 and A14. Exact synthesis
found a 9-CX strong A preparation, compared with 11 CX on the previous line.
The encoder needs six explicit preparations and reuses only the source's zero
state on q15. Since it resets q9 and q13 at41, it works with the retimed 243-CX
source after only removing M15@40; the noisy H9 and the other early A-source
changes are unnecessary for this 48-tick version. The source and product
receipts are `prefix_retimed_drop15.json` and
`retimed_drop15_product_states.json`.

The 11-CX enumeration excluded each previous directed-CNOT multiset, so it did
not waste evaluations on timing-only variants. It found three further
multisets and then proved the constrained remaining set infeasible. NATIVE2's
full pair coefficients for those three were 34.98555556, 35.03, and 35.11333333;
all passed the raw and harmful-single checks. This is an exhaustive result for
the stated multisets, source, guard, deadline, and 11-CX cap, not for all possible
encoders or measurement instruments. The witness paths are in
`a_herald_distinct_paths.json`.

| Complete native circuit, before optional parking | CX | Ticks | c1 | c2 |
|---|---:|---:|---:|---:|
| New 11-CX A, q9-plus source | 375 | 48 | 0 | 35.01333333 |
| 9-CX A, q9-plus source | 373 | 48 | 0 | 35.02222222 |
| 9-CX A, 243-CX source with only M15 removed | 375 | 48 | 0 | 35.02222222 |
| 9-CX A, source with q15 released at39, B ready45 | 369 | 47 | 0 | 34.97111111 |

These numbers are from NATIVE2's completed full-circuit receipts, including all
Pauli fault components. They are second-order diagnostics; all-orders price,
acceptance, and final promotion remain separate. None of these rows is a SOTA
claim. The first 47-tick circuit is
`NATIVE2_20261027/boundary/full47_q15_early39_cut3_ba6cf344b3e5e904_d6_20_19_10_2_22_16`.

The earlier q9-plus boundary could prepare the entire A state by44, but could
not make A8 and A14 ready43. This failure persisted with every phase constraint
softened away, proving an exact state/deadline obstruction in that fixed model.
Removing the early-port deadline produced a 10-CX state ready44. A separate
numeric audit established both the phase-herald guard and absence of logical8
components for that witness, saved as `sol/a_herald_R44_all_strong_h82.json`.
The root lane uses it for a separate between-check Clifford experiment.

NATIVE2 then certified q15 as a product zero at39 rather than40. That release
allows all nine preparation CNOTs and their preparations to shift one tick
earlier. The exact CP re-derived this solution as OPTIMAL in 0.389s on the actual
source/product receipts, with A8 and A14 ready43 and all A ready44:
`sol/a_herald_R44_early8_14_no8_earlysource_hx8_14_15_cut3.json`. State, phase,
and no-logical-hook replays all pass. This newer source explicitly resolves the
earlier bounded infeasibility; it does not contradict it.

A nondestructive logical-X check before the data taps is not an immediate
replacement for the final readout. A completed two-CX decode, MX, and two-CX
inverse takes five sequential stages after the completed resource. Moreover,
the inverse contains data-data CX gates after the herald: a ZZ component after
either inverse gate is a weight-two A phase error and cannot flip the earlier
measurement. Such a construction fails the present strong phase guard unless
another later flag is added. It remains a different weaker instrument that
would need its own complete noisy evaluation.

## Source parking restoration schedules

`restore25_schedule.py` restores the source's two deleted CX19→25 operations
while keeping q25 available at30. Its eight q25 interactions occupy22–29, and
CX24→30 moves from26 to25. Every one of the 36 physical-wire operation histories
matches the reference with the old pair restored; no clock/wire collision
occurs, and the official raw test passes. The exact source stem and full timing
receipt are in `restore25_schedule.json`. PREFIX2 can combine it with its
independent q12 parking restoration.

For B ready45, q25 must instead be available at29. Keeping the restored pair
after CX13→19@27 requires its two gates at28 and29, so it cannot meet that release
without also changing the earlier source chain. An optional exact-identity
alternative places the pair at20 and21, when both wires are idle, and leaves
every other b45-source operation, record, and timestamp unchanged. It passes
the raw test and retains q25 release29. `restore25_early_pair.json` identifies
that source. Moving a complete identity pair preserves the ideal instrument
but changes its noisy channel; this alternative must be fully priced and is
not asserted to retain the benefit of the late pair.

## Bounded old-line 47-tick comparison

The root requested one distinct 47-tick alternative using the original
logical-X line {7,8,9}, so both early data ports could use the q0/q1 parking
protection. The unchanged cut3 source gives INFEASIBLE for the strong phase
guard at A-ready44 with A7/A8 ready43, without a CX cap (0.213s).

`source_rx9_early.py` builds the requested physical alternative: H9@38 is
replaced by real RX9@38, MX9@39 is removed, and the singleton source check c321
is removed. Every other cut3 operation and check is retained. The source raw
test and all released-product certificates pass. NATIVE2 independently built
byte-identical QASM and recorded the official native noisy RX preparation in
`cut3_rx9_38.result.json`. This is an explicitly changed acceptance contract,
not an ideal early input or a claim that the old source check is redundant.

The same strong phase model remains INFEASIBLE with this earlier q9 input
(0.265s). Allowing residual phase hooks gives the following bounded controls:

| Resource on old logical-X line | Source requirement | CX | Earliest A7/A8 | All A ready | Weighted residual phase proxy |
|---|---|---:|---:|---:|---:|
| Soft phase objective, logical8 forbidden | RX9@38; c321 removed | 11 | 42 | 44 | 8/15 |
| CX capped at10; soft phase objective; logical8 forbidden | Original cut3 source suffices | 10 | 43 | 44 | 12/15 |

The 11-CX solution is
`sol/a_herald_R44_early7_8_no8_earlysource_soft_cut3_rx9_soft.json`. Its two
remaining bad phase-component groups have class1: Z14 before the final
CX13→14@42, and ZZ after that CNOT. The unconstrained-logical8 version returned
the same preparation and proxy optimum. The proxy weights each active CX
phase-component group by4/15, idle phase by10/15, and initial plus phase by1;
it does not include the actual multiplicity of B faults that can hide a given
syndrome. These resource receipts explicitly list their unsafe components and
do not claim the strong phase audit passed.

The 10-CX control resets q9 at40 and only reuses zero15, so its complete
preparation fits the unchanged cut3 releases. Removing c321 is unnecessary for
that control. The source-compatible module is
`sol/a_herald_R44_oldline10_cut3.json`; its remaining phase proxy is12/15.
Consequently, the proved negative is strong phase protection at these
deadlines, not raw state/deadline feasibility on the original source.

NATIVE2 completed the 11-CX control at371 CX and47 ticks. It passes the raw test
and has c1=0, but c2=40.42083333. Spare parking increases it to380 CX and lowers
c2 to38.04083333, still materially worse than the strong 47/48-tick family.
The residual class1 hooks cost more than the early-port parking saves. No
further enumeration of this fixed model is planned; the 10-CX source-preserving
control is left for NATIVE2's complete comparison.
