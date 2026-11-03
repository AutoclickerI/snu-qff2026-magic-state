# Independent small-cat review

## Scope and result

The shared-basis source construction is valid. Its physical axis is
`W = T† X T = (X−Y)/sqrt(2)`. On the canonical Steane code, `W^⊗7` is the
logical axis stabilizing the desired logical T state. The six-stabilizer code
projector commutes with this transversal operator.

Two distinct evidence levels are kept separate here:

1. The independent dense and exact-algebra audits assume an ideal encoded T
   input and an ideal final code projector. They establish the source's
   single-fault behavior, not a complete score.
2. The candidate comparisons retain all reset, gate, measurement, and waiting
   noise in the complete abstract circuit supplied by the architecture lane.
   Their raw correctness and all-orders loss are checked, but their nonlocal
   encoders and abstract placement are not legal native-grid submissions.

No result in this lane establishes a new native best or SOTA.

## Exact suffix criterion

Consider a fault immediately after a cat-control CX into data coordinate q.
Let R be the data coordinates that the same logical cat control will visit
later. The logical control can continue through correctly implemented moves;
R must follow its trajectory, not just one physical wire.

After propagation through the remaining CX operations and the final TDG,
the potentially damaging operators are:

| Physical two-qubit fault | Data operator after propagation |
|---|---|
| cat X, data X | product of W on R union {q} |
| cat X, data Y | product of W on R, times (X+Y)/sqrt(2) on q |
| cat X, data Z | product of W on R, times Z on q |

Pure products of W preserve the target eigenspace after code projection.
For the other two rows, exact Gaussian-integer/rational enumeration of every
possible q and R gives only two harmful cases:

* XY: R has two coordinates and R union {q} is a Fano line.
* XZ: R has four coordinates and its three-coordinate complement is a Fano line.

A Fano line means that the three binary labels (data index plus one) XOR to
zero. Each harmful operator has accepted probability 1/4, zero target-state
probability, and therefore conditional infidelity one. All other 854 of the
896 operators have zero target-orthogonal probability. The same exact script
checks all 128 pure partial-W operators.

There is a crucial additional condition in overlapping checks. A Y or Z data
component propagates Z onto every later check that visits q. Any such later
visit flips another independently postselected cat parity and rejects the
fault. Consequently the suffix condition matters only at the **last overall
visit to q**. This rule applies to any number of complete checks, with different
partitions in different rounds.

`suffix_constraints.audit_order(groups_by_round, timeline)` implements this
criterion. Timeline entries are `(round, data_index)`. It returns explicit
harmful CX witnesses. It does not certify noise in movement implementations
or in a physical final code check.

For sequential checks and groups of size at most four, making each group's
last three visits noncollinear is necessary and sufficient for eliminating
these joint-CX failures in the final check. Groups of size one or two impose
no such condition. A single control visiting all seven coordinates also needs
its first three visits noncollinear, because the complementary-suffix condition
then applies at its third visit.

## Counterexamples and interleaving

The independent dense simulator includes every nonidentity two-qubit Pauli at
each CX, all one-qubit Pauli faults, every active-wire cut, and cat-parity
measurement flips. It uses the actual GHZ, T, CX, and TDG operations and sums
over individual cat outcomes subject only to their product parity.

| Construction | Fault components | Harmful singles |
|---|---:|---:|
| Sequential 3/2/2: [0,1,3], [2,4], [5,6] | 1,496 | 0 |
| Sequential 3/4: [0,1,3], [2,4,5,6] | 1,253 | 0 |
| Sequential 3/4: [0,1,2], [3,4,5,6] | 1,253 | 1 |
| Sequential single controls, natural order | 1,034 | 1 |
| Sequential single controls, order [0,1,3,5,2,4,6] | 1,034 | 0 |
| Interleaved 3/2/2, three coupling clocks | 1,550 | 0 |
| Interleaved nonline 3/4, four coupling clocks | 1,289 | 0 |
| Interleaved line 3/4: [0,1,2], [3,4,5,6] | 1,289 | 0 |
| Interleaved original line 4/3: [0,1,3,6], [2,4,5] | 1,289 | 0 |

The failing sequential line case is XY after the last check's first CX into
data 0. It is accepted with probability 1/4 and produces the orthogonal logical
T state. The natural single-control order fails through XZ after data 2.
These are raw, projected-state failures; no decoder is credited with fixing them.

Cyclic interleaving moves the hazardous first visit of a three-site line before
the other check visits that coordinate, so the other parity rejects it. Among
all 5,040 ordered 3/4 partitions with the second check cyclically shifted, 4,032
pass the exact order criterion. Only the first check's four-site group's last
three coordinates can be harmful in that specific schedule. The complete
enumeration is reproducible from `suffix_constraints.py`.

## Complete noisy abstract comparisons

All rows below have raw exact correctness, first-order loss coefficient zero,
and 15 T/TDG operations. The ending is the same simple physical Steane-check
control unless stated otherwise.

| Source | CX | Clocks | c2 | All-orders loss | Acceptance |
|---|---:|---:|---:|---:|---:|
| Interleaved 3/2/2 | 109 | 18 | 36.9244444444 | 3.8465569294e-5 | 0.780425144 |
| Interleaved 3/4 Bell controls | 107 | 19 | 33.1616666667 | 3.4702959901e-5 | 0.783064929 |
| Interleaved 3/2/2 with leaf parity verification | 113 | 18 | 33.0377777778 | 3.4376368583e-5 | 0.776976203 |
| Interleaved 1/3/3: [5], [0,1,3], [2,4,6] | 109 | 18 | 33.1161111111 | 3.4619490734e-5 | 0.780158954 |

The unflagged 1/3/3 control provides almost the Bell-control quality while every
control visits at most three data sites. This may be easier to place than a
fixed control with four data neighbors. Both triples are noncollinear. Three
placements of the same groups among GHZ root/leaves were tested; the row above
was best among those three, not a global grouping optimum.

### What the pair ledger shows

`stage_pairs.py` recomputes every physical error pair, subtracts mutually
exclusive alternatives within one noise channel, and checks its total against
the architecture lane's c2. It does not infer totals from the top-100 ledger.
Waiting channels are attributed to the operation to which the official noise
model attaches them.

For all three plain interleaved endings, these contributions are unchanged:

| Pair of physical stages | c2 contribution |
|---|---:|
| Final B→D with final B→D | 22.8666666667 |
| Final B→D with D→A | 2.6133333333 |
| B→C verification with final B→D | 2.6133333333 |

Thus 28.0933333333 of the coefficient comes from just these terminal pairs.
The Bell source has only 0.0466666667 from cat-preparation pairs with any other
stage. Additional Bell-preparation flags have little available benefit.

The original 3/2/2 source instead produces two-coordinate partial-W hooks from
leaf bit flips. A final A-resource or readout fault can mask their X syndrome.
For example, W on data 5 and 6 has an XX component. A false A read at data 0
masks its syndrome because labels 6 XOR 7 = 1. The XX component is accepted
with probability 1/4; the resulting logical-X error has conditional T-state
infidelity 1/2, giving pair numerator 1/8. This matches an explicit complete
pair-kernel witness in the saved ledger.

### Concrete cheap flag

The GHZ3 root controls the nonline triple and its two leaves control pairs.
Measuring Z_leaf1 Z_leaf2 distinguishes the harmful two-/five-site residual
class from the harmless identity/nonline-three/complement-four class.

One helper per GHZ performs R at clock 9, leaf1→helper at 10,
leaf2→helper at 11, and Z readout at 12. Delaying leaf2's data couplings from
11/12 to 12/13 avoids collisions without adding a clock. The two helpers add
four CX gates total. Both parity outcomes are included as actual detectors.

In the full noisy circuit this removes essentially all original cat-preparation
pair cost: only 0.0022222222 remains. New flag-operation pair cost is
0.3066666667. The net c2 reduction is 3.8866666667. This is a tested physical
flag circuit in an abstract layout, not an ideal flag assumption.

## Remaining native work

The geometry lane's moving Bell module is under separate independent audit.
An MX transfer must use a fresh Z-zero destination, preserve each old-wire MX
record in the same check's final parity, and retain that record across reset
and reuse. A data-CX fault's remaining suffix follows the logical control
through every subsequent move. A transfer-CX fault touches no data wire and
therefore has a different, simpler residual-error form.

Full native circuit assembly, all physical ending checks, acceptance, and an
all-orders native score remain necessary before any candidate can replace the
working native circuit.
