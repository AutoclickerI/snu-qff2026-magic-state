# Native architecture, second pass — checkpoint

This lane has produced complete legal native circuits, exact noisy prices,
independent simulator checks, and a reusable source/resource boundary. It has
**not produced a circuit beating v37j**. The strongest complete fresh-source
circuit here has loss **5.02464164493e-5** and acceptance **0.507156407551**.
The lower **2.74984614967e-5** value below uses an explicitly perfect resource
and is a design diagnostic, not a legal complete candidate.

Work remains active on joint native preparation for END2's corrected
six-square/one-tree ending. No submission, commit, push, or external run was
made by this lane. Shared judge and qtools sources remain unchanged.

## Complete fresh-source circuits

`separate.py` constructs a native one-T Steane encoder on a connected
seven-cell patch, transfers the data to its terminal footprint, optionally
checks source stabilizers, and performs two logical-W checks. The physical T
and T-dagger layers are shared between both W checks, so these circuits use
15 T gates in total. Each seven-cat grows on a three-layer native tree; the
full inverse tree exposes six zero flags and one X-parity result. Measured
cells are reused for the next cat and terminal resource.

All entries in this table have passed the official noiseless gate/target
check. Prices include all gate and elapsed-time noise.

| Circuit | CX | Ticks | Exact loss | Acceptance |
|---|---:|---:|---:|---:|
| Z precheck, six-layer source | 184 | 46 | 5.57836038317e-5 | 0.559199591887 |
| Same, source T at its latest equivalent location | 184 | 46 | 5.55576754790e-5 | 0.559571794490 |
| X and Z prechecks | 204 | 55 | **5.02464164493e-5** | 0.507156407551 |
| Y precheck using idle S/S-dagger slots | 184 | 46 | 5.14357874460e-5 | 0.559174992179 |
| Two early-read W flags plus overlapping A preparation | 183 | 44 | 6.4071063988e-5 | 0.5724394 |
| Early GHZ-growth flag on helper 13 | 180 | 46 | 6.70195853334e-5 | 0.558825265299 |

The first three use pinned qtools evaluator version
`94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f`.
The Y circuit uses the separately identified lane-local S/S-dagger extension
described below. Full receipts are the matching `.result.json` files; emitted
QASM and data-qubit metadata are in `cand/`.

The selected full-XZ circuit is
`cand/separate_w2_full_pcXZ_reuse_jit_linear_magic_d6_s2_d66d232003ca254d_d0_20_7_10_3_22_21`.
Its exact loss is about 40% above the v37j baseline, despite using half as many
CX gates. This is not a promotion candidate.

Partial-rank source checks and cat shortcuts were also physically built.
One additional X generator before the Z precheck gives 5.57531116261e-5 at
191 CX/51 ticks. A Z generator before the Y precheck gives 5.14837971316e-5.
Neither improves the respective full circuit materially. Three full W
checks give acceptance 0.4950226 and fail the acceptance constraint.

### Pair mechanism

`audit.py` uses linear-in-p channel weights for Taylor coefficients, while
the full prices retain the exact finite-p channels. The 184-CX Z circuit has
first-order coefficient consistent with zero and second-order numerator
41.6555555556. Contributions include 22.8666666667 from the final B-to-D
stage paired with itself, 3.92 from that stage paired with D-to-A, 3.6844444444
from B/C resource faults paired with each other, and 6.1233333333 from source
or precheck faults paired with W-check faults. The final-stage grouping
includes its attached waits; it is not solely a count of CX fault pairs.

Replacing the older native B/C factory by END2's verified 59-CX joint module
reduced CX count but increased its resource-resource pair term from
3.6844444444 to 7.2444444444. This explains why that smaller resource was not
an improvement. Representative rank-one and rank-two gauge variants were
also raw-valid but priced at 7.729449e-5 and 7.58991197e-5, respectively.

### Native Clifford extension and official check

`frontend_clifford.py` is an explicitly separate frontend supporting S and
S-dagger; `clifford_price.py` temporarily selects it inside its own process
and restores the original frontend. It does not modify shared evaluator
sources or write a price under the pinned evaluator's cache identity.
The extension's source hash is
`c350c1627077bb41a66a445ed18733f0e1b23ca03c37dffd7f99b23009506028`.

`verify_clifford.py` independently replays 20 randomized 64-gate Clifford
circuits through Stim tableaux. All 12,964 fault pullbacks and 1,440 signed
output-Pauli pullbacks agree exactly. A no-S complete-circuit control also
agrees with the pinned evaluator. The receipt is
`clifford_frontend_verification.json`.

The complete Y circuit additionally passed the official checker with one
million noisy shots, seed zero: sampled loss 4.56022447033e-5, reported SEM
7.31877456548e-6, acceptance 0.559183, 184 CX, and no format, gate, or
correctness errors. This one-seed check validates the gate/noise integration;
it is not used as a precision ranking claim. Its receipt is the Y circuit's
`.mc.json` file in `cand/`.

## Conservative source boundary for a new ending

`prefix_boundary.py` extracts the original v37j source lifetimes, retains
their heralds and guard interactions, removes the old terminal factories,
and fixes the obsolete c366 source record by reset. T/T-dagger gates are
moved only through empty slots and CX gates on which that wire is control.

The resulting real native source is **251 CX, 41 ticks, 15 T**, ending at
tick 40. Its official raw check passes: six output stabilizers are +1,
accepted loss is zero to numerical precision, and rotation rank is five.
The saved stem is
`boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16`.

`prefix_release.json` supplies first-free ticks for every non-data cell.
`boundary_product.py` then uses the official exact simulator to certify the
final product state of all 29 such cells. Plain plus states are on
4, 12, 14, 18, 25, and 26; cell 17 has X phase XOR c311; every other released
cell is zero. In particular, cells 7, 13, and 15 are already measured zero
and can take a resource CX at tick 41 without another reset. These are ideal
state certificates: reuse retains the source's actual measurement and idle
noise in every complete circuit.

The new terminal role assignment supplied by END2 is:

| Role | Ordered physical cells |
|---|---|
| D | 6, 20, 19, 10, 2, 22, 16 |
| A | 7, 21, 18, 4, 8, 23, 17 |
| B | 12, 26, 25, 11, 3, 28, 15 |
| C | 13, 27, 24, 5, 9, 29, 14 |

Its resource is A plus-L, B zero-L, C in the span of code-index masks
7/25/42/64, with B-to-C precorrelation. Six local squares and one tree form
the two terminal CX layers. The first six tiles allow independent A/B swaps.

With the real noisy source and an explicitly perfect instantaneous version
of this resource, the exact diagnostic is **2.74984614967e-5**, acceptance
**0.603735893558**, and first-order coefficient consistent with zero.
`boundary/stripped_prefix_perfect_partial_resource.diagnostic.json` records
that the five artificial preparation ticks, their noise, and their added
wait duration are excluded. Its nonlocal resource QASM is diagnostic-only;
it must never be labeled grid-valid or submitted.

Root subsequently supplied a separate 105-CX source variant. Its product
states are independently certified in `contracted105_product_states.json`.
Its earlier free cells can help resource scheduling, but its perfect-resource
loss is worse; no replacement of the conservative prefix is assumed here.

## Native resource preparation still in progress

`a_factory_search.py` searches state-specific native A-only encoders using
three-variable dual or four-variable direct preparation, free input bases,
Steiner elimination, exact row-space deletion tests, and commuting-CX
scheduling. Borrowed cells are returned to zero and measured. On the
conservative role assignment it found a **45-CX factory ready at tick 49**.
The official exact replay in `a_factory_verify.py` confirms all seven A
stabilizers, all 14 returned helper zeros, and unchanged correct source data.
That artifact is a valid A-only module, not a completed A/B/C factory.

`a_orientation.py` screened all 64 square A/B orientations with both encoder
types. The first 400-trial-per-orientation pass found mask 15,
A = [12,26,25,11,8,23,17], ready at tick 47 using 40 CX. Mask 31 found a
34-CX direct preparation ready at tick 48. These are exact binary-map seeds;
the orientation-specific official replays are pending at this checkpoint.
The separate A factory continues to borrow cells needed by B/C, so its ready
time alone is not a full joint-resource completion time.

`partial_assemble.py` integrates a joint solver solution with either certified
source prefix, uses actual noisy resets or certified measured-state reuse,
accepts rank-ten preparation with a late physical RX14, regenerates the
complete affine record contract, and runs official raw validation before
optional full pricing. The late RX is counted as a real noisy operation.
Orientation roles are preserved in the emitted terminal gates. This builder
is ready; no competitive complete joint A/B/C solution has yet been supplied.

## Reproduction and provenance

Run commands from the repository root using `.venv/bin/python`. The scripts
set numerical-library thread counts to one. The exact default source and
product certificates can be regenerated with:

```bash
.venv/bin/python work/lanes/NATIVE2_20261027/prefix_boundary.py --diagnose
.venv/bin/python work/lanes/NATIVE2_20261027/boundary_product.py
.venv/bin/python work/lanes/NATIVE2_20261027/a_factory_search.py --trials 10000 --seed 1 --cp-seconds 2
.venv/bin/python work/lanes/NATIVE2_20261027/a_factory_verify.py work/lanes/NATIVE2_20261027/a_factory_search.json
.venv/bin/python work/lanes/NATIVE2_20261027/a_orientation.py --trials 400 --seed 1
.venv/bin/python work/lanes/NATIVE2_20261027/verify_clifford.py
```

Cross-lane imports come from NATIVE20261027, PREFIX20261027, END2_20261027,
and REBUILD20261027. Those sources and MAIN/v37j must accompany this lane's
selected files in the combined handoff. Exact receipts identify the QASM
hash, data-qubit order, and evaluator version. `selected_files.json` is
generated by `checkpoint_manifest.py` and is a checkpoint, not a statement
that all active research has finished.
