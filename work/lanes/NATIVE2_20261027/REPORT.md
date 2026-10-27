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

## Continued native integration and measurement-instrument search

`measured_assemble.py` now combines complete source and measured-helper
resource modules. It derives the actual affine record checks, verifies every
native edge and operation collision, checks raw output, and optionally computes
all single-fault contributions and the full noisy price. It permits independent
helper reads to overlap the terminal and permits the B factory to finish during
the first D-to-A layer, before B's own first terminal use.

The first joint resource witnesses were actual complete circuits, but failed the
noise objective. The four-square 84-CX factory produced a 360-CX, 72-tick raw-valid
circuit with c1=6.5333. The no-C 59-CX factory produced 324 CX and 53 ticks with
c1=27.1667. These are measured failures, not merely solver budget limits.

### Preserve the old B factory and change A

`old_b_new_a.py` restores the incumbent's complete B factory, including its lower
flag qubits, while preparing A on the connected footprint
`[7,14,13,9,8,21,15]`. The full restored B component contains 109 CX; the often-used
77-CX count covers only its smaller internal B/C portion.

The initial 9-CX A encoder with all-Z A readout was raw-valid and had c1=0, but its
full loss was 1.01935788786e-4 at acceptance 0.493820753. Its c2=94.9333 exposed
A phase errors masked by a second fault in B's phase check.

The old A instrument contains a useful logical-X readout that all-Z readout
discards. Its two decoder CXs, 8-to-7 then 9-to-8, followed by MX9 measure the
logical-X representative on physical A cells {7,8,9}. `compact_a_readout.py`
restores this readout with staggered data taps, keeping the full 49-tick clock.
The 10-CX A version scored 4.39235744267e-5 at acceptance 0.494394659 under the
then-complete detector contract. It is still worse than the incumbent.

An END2 11-CX A encoder constrains every phase hook to be either correctable or
detected by this logical-X herald. The stronger no-logical-hook JIT variant has
c2=33.5188889. Its previously priced *ignore-record* policy gave
4.05667562545e-5 at acceptance 0.493161933; that policy is a distinct experiment,
not a reconstruction of the incumbent's acceptance rule. The corrected candidate
is `compact_a_modes_no8_jit_106223fb2b053761_d6_20_19_10_2_22_16`, with raw output
correct and c1=0. Its c2 is unchanged. Full pricing and further timing improvements
remain separate steps.

### Exact acceptance-contract control

Unrestricted deterministic-record completion added two independent checks to the
reconstructed incumbent: rank 71 became 73. They involved MX26 at tick 31 and
M31 at tick 42. Completing those records as separate zero conditions changed
acceptance to 0.493484676886, while loss remained 3.58720776604e-5.

These records are not unused. The original detector contract uses their relative
phases in `[330,332,334,336,352,361]` and `[348,376]`. Simply excluding their records
from completion also changes the accepted subspace. The retained
`record_contract_filtered_control.json` explicitly records this failed control.

The correct implementation accepts the two physical record-flip modes generated
by Z before MX26 and X before M31, including their downstream record correlations.
The assembler derives each mode from the candidate's own full Pauli model, checks
that it changes neither output data nor source rotations, and projects the detector
row space to accept those modes. `record_contract_modes_control.json` proves that
the reconstructed 412-CX circuit then has exactly the original canonical detector
row space, rank 71, and the same physical gate/time multiset. Original record labels
identify the physical measurements even when the B factory is retimed.

### Other tested freedoms

`dual_old_factory.py` implements a native Hadamard dual of the old B factory as
a sparse A phase resource. It reverses CX directions, exchanges native preparation
and readout bases, and makes four explicit boundary changes. The 107-CX resource
has all four A-X stabilizers +1 and correct raw source output. Complete probes
confirmed zero accepted harmful singles from this A module and its modified
source. This is a verified module, not a complete competitive circuit by itself.

Swapped A/B roles and reversed verification order were also assembled. The
381-CX, 49-tick reversed-order probe had c1=0 but c2=70.8417. Restoring a logical-Z
B herald reduced c2 to 48.4733 or 51.7861 in two variants. A fully hook-protected
18-CX connected B module in the normal order produced a 390-CX, 51-tick full
circuit with c1=0 but c2=88.8178: many accepted correctable B-X faults accumulated
before the terminal and paired with later faults. These families are not winners.

`instrument_schedule.py` schedules the entire A instrument by exact CX commutation,
including data taps, instead of imposing a completed pure-A boundary. It found a
48-tick endpoint for the weak 10-CX A instrument, with all data taps by tick 45
and A reads by tick 47. The fixed stronger 11-CX JIT instrument was infeasible
under those same deadlines. The 48-tick witness still requires a compatible
earlier B factory and a complete noisy audit; it is not a scored improvement.

### Concrete 48-tick source-boundary experiment

The CP-retimed weak 10-CX instrument turned out to have exactly the same physical
gate/time multiset as PREFIX2's shifted `compact_a_48tick.json`; it was not
re-priced as a distinct result. PREFIX2's complete 376-CX, 48-tick weak-A candidate
had c1=0, c2=39.2, full loss 4.62502747419e-5, and acceptance 0.472779781363.
It is both ineligible and worse than the incumbent.

`strong48_boundary.py` now builds a stronger complete 48-tick experiment from
PREFIX2's 243-CX aligned source and 107-CX B module. It moves M7 and M13 to tick
39, removes the final zero-control CX13-to-19 at tick 39, removes source M15 at
tick 40, and replaces source M9 at tick 39 with RX9. The 11-CX phase-guarded A
instrument can then run one tick earlier. The source loses two explicit herald
bits, so the descriptor labels its changed postselection. It does not claim
baseline-equivalent acceptance.

The actual circuit `strong48_boundary_deba84a0bf51a2bf_d6_20_19_10_2_22_16`
has 376 CX, 48 ticks, all six raw output stabilizers +1, and c1=0 over 6,494
fault components. Its c2 is 36.2144444. The terminal contribution is identical
to the strong 49-tick circuit shifted one tick earlier; the excess second-order
loss lies in earlier source/B fault pairs.

The `--preserve-m9` variant retains source record c321. It replaces the
zero-control CX9-to-10 at tick 38 by a standalone H9, and changes the next
measurement to native MX9 at tick 39. This H is explicitly a one-tick noisy
operation, followed by a separate native measurement. The official unmodified
converter and noise scheduler confirm H38 with DEPOLARIZE1(0.001), MX39 with
its readout and post-measurement noise, then the first A CX9-to-15 at tick 40.
The full receipts are in `strong48_m9_herald.result.json`.

This 375-CX, 48-tick circuit,
`strong48_m9_herald_aff5199534254d12_d6_20_19_10_2_22_16`, is raw-correct,
has c1=0 over 6,488 components, and c2=35.43. It still needs B's wait times fixed
and a full price before any performance conclusion. PREFIX2 owns the fixed-order
late B schedule; no full price has been duplicated here.

A proposed same-tick MZ-then-H shortcut was invalid: standalone H is neither
zero-duration nor noiseless. Its temporary collision-check relaxation was
reverted, its artifacts were deleted, and `discarded_mz_h_probe.json` records
why it is not a candidate. Only the separate H38/MX39 construction above was
retained and checked against the official native stream.

### Complete B scheduling, A alternatives, and priced spare checks

PREFIX2 replaced the earliest-start B schedule by a fixed-order late schedule
weighted by actual first-order rejection. This removed its unnecessary waits
without changing the B gate sequence or its accepted physical record modes.
The completed 375-CX, 48-tick strong-A circuit then priced at
4.06936374726e-5, acceptance 0.506398489982, with c2=35.03.

`assemble_48_solution.py` integrates the two supported native logical-X
readouts and supports a 47- or 48-tick deadline. It also accepts a different
certified source boundary, checks every A input that is reused without a reset,
and then runs the full raw, single-fault, and pair tests. This is a physical
source change, not an inference of noisy equivalence from product states.

Four constrained 11-CX A topologies on the certified q9-plus boundary gave c2
35.0133333, 34.9855556, 35.03, and 35.1133333. All were raw-correct and c1=0.
The distinct 9-CX encoder uses logical-X representative {8,14,15}, with decoder
14-to-8 then 15-to-14 and MX15. It gave c2=35.0222222 both on the q9-plus source
(373 total CX) and on the simpler aligned source with only M15 omitted
(375 total CX). These small differences do not establish an all-orders winner.

`idle_parking48.py` inserts real noisy native identity interactions in vacant
data slots. Preparing spare q0 and q1 in plus, using them as CX targets, and
checking them in X reduced c2 from 35.03 to 33.17. The full 386-CX, 48-tick
artifact `park48_a3_p0_8356c82dc05d4556_d6_20_19_10_2_22_16` is priced at
**3.80823788643e-5**, acceptance **0.503853819645**. It is eligible, but still
worse than the incumbent. Its process exited successfully and the exact receipt
is retained. Checking only q0 or only q1 was weaker; omitting the new heralds
also increased c2. Adding repeated D-to-A CX pairs on cells13/14/21 instead
increased c2 to 38.07 and was rejected.

The best alternative 11-CX topology with both spare checks has c2=33.1255556
(386 CX); the 9-CX/alternate-readout version with them has c2=34.2822222
(386 CX). Neither was redundantly priced because neither established a material
advantage over the already-priced family. The change in the early data cells
matters: the alternate readout makes data20 finish its bit check early, while
that cell has no free plus-state neighbor for the following idle slot.

### A complete native 47-tick circuit

`source_q15_advance.py` starts from PREFIX2's B-ready45 source, preserving its
q28/q4/q5 timing changes. Its `cut3` variant removes the zero-control
CX15-to-21 at35 and the identity pair CX10-to-16 at36/37. It then moves
CX9-to-15 to35, CX9-to-8 to36, M8 to37, CX15-to-16 to36, and CX16-to-15 to38.
The shared-control reordering preserves the ideal transfer; every removed gate
is still treated as a real change in noise and tested in the complete circuit.

The official product-state oracle certifies q15 as +Z at release39, with A
releases `{7:40,14:37,13:40,9:40,8:38,21:38,15:39}`. The source/release and
product receipts are `q15_early39_cut3_release.json` and
`q15_early39_cut3_product_states.json`. END2 independently rederived the shifted
9-CX A factory as optimal in its constrained state/phase/no-logical-hook model.

With rejection-optimized B45 timing, the actual full circuit
`full47_cut3_breject_4e91e2e1cb3d917a_d6_20_19_10_2_22_16` has **369 CX and
47 ticks**, correct raw output, c1=0, and c2=34.9711111. Adding both free-plus
spares gives `park47_cut3_breject_693f80ade86eb391_d6_20_19_10_2_22_16`,
**378 CX**, with c1=0 and c2=34.2311111. Its full-price job is separate from
these structural and low-order certificates. That job has now exited
successfully: its exact loss is **3.89104079039e-5** at acceptance
**0.510125086243**. It is eligible but worse than the priced 48-tick parked
version and the incumbent. No SOTA claim follows from the clock reduction.

Removing two additional ideal-zero-control gates, CX16-to-15 at34 and
CX16-to-10 at35, also passed raw/F1 but increased c2 to40.4288889. That 367-CX
variant is rejected on measured fault-pair loss. Zero action on the ideal state
does not make a noisy gate irrelevant to the postselected instrument.

Reproduce the source and 47-tick control with:

```bash
.venv/bin/python work/lanes/NATIVE2_20261027/source_q15_advance.py --integrate
.venv/bin/python work/lanes/NATIVE2_20261027/assemble_48_solution.py work/lanes/NATIVE2_20261027/q15_early39_cut3_a9_R44.json work/lanes/NATIVE2_20261027/q15_early39_cut3_b_reject_module.json --name full47_cut3_breject --end 47
.venv/bin/python work/lanes/NATIVE2_20261027/idle_parking48.py work/lanes/NATIVE2_20261027/boundary/full47_cut3_breject_4e91e2e1cb3d917a_d6_20_19_10_2_22_16 --name park47_cut3_breject
```
