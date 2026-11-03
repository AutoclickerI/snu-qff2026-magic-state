# Earlier-boundary joint interface

## Result

A coherent source parity leg exists in the actual 49-clock native incumbent, and it is consumed before the incumbent prepares and uses its terminal A block. A complete physical parity-check witness uses a related leg on a six-square parent, but this implementation is far from competitive. No improved incumbent or SOTA candidate was found.

At cut 39 (before operations at clock 39), the incumbent has unconditional expectations `<Z15 Z16>=1`, `<X15 X16 X19 X20 X22>=1/sqrt(2)` and `<X15>=<Y15>=<Z15>=0`. The oracle retains prior measurement registers coherently and no detector conditioning is applied. Because `Z15 Z16=+1`, any state separable across q15 versus the rest must have q15 diagonal in Z within that support; the nonzero X15 correlation proves the physical state is entangled across that cut even when previous records are traced out. q21 is also `+Z` at this cut. Reproduce with `incumbent_cut.py`; values are in `incumbent_cut.json`.

The original NATIVE2 prefix gives the particularly transparent exact stabilizer pairs, also unconditioned on records:

- cut 36: `Z7 Z13=+1` and `X7 X13 X3 X6 X9=+1`;
- cut 38: `Z13 Z19=+1` and `X13 X19 X15 X20 X22=+1`;
- cut 39: `Z15 Z16=+1` and `X15 X16 X19 X20 X22=+1`.

Each pair witnesses entanglement across the first listed cell and its complement. At cut 40, immediately before the last source reads, q7, q13 and q15 already have individual +Z expectation, so those qubits are factorized even without conditioning on earlier detectors. This distinguishes their earlier, coherent correlation from the completed product boundary. `probe.py`, `coherence.py` and their JSON receipts use the pinned official `tprep.exact.run` Pauli oracle on literal prefixes.

## Complete native instrument witness

At cut 39 of the six-square parent, q15 is a coherent Z-copy of data q16 and q21 is already `|0>`. The native operations

1. `CX19,20` and `CX15,21`;
2. `CX20,21`;
3. `CX19,20` and `CX22,21`;
4. measure q21 in Z,

measure `Z19 Z20 Z22 Z16`, a Steane Z stabilizer, while restoring q20. The first three gates compute q19 XOR q20 into q21 with q20 restored; `Z15 Z16=+1` lets q15 supply the q16 leg. The source's original uncompute and all terminal resource operations remain after this instrument; q21's earlier measurement supplies its clean input, so no new reset is assumed. The operation is an exact isometry on the witnessed source subspace, but its fault action is different from a hypothetical direct q16 coupling.

The complete circuit `copied_parity_check_*.qasm` is native and raw-correct, with ideal acceptance 1 and six code stabilizers +1. Its exact all-noise loss is **0.006295837532704547**, acceptance **0.2664143792906354**, first-order coefficient **5.7**. Omitting the newly added detector but retaining its physical measurement gives loss **0.006323583847691382**, acceptance **0.26722923013977073**. The original complete six-square parent is **0.006270610322780911**, acceptance **0.27801426350428343**. Hence this shows a real source-embedded measurement interface, not a competitive architecture; the parent itself is extremely poor and this witness does not absorb the source uncompute. `instrument.py` constructs both variants; the `.result.json` receipts contain the all-orders evaluator output. `control.py` merely shifts the same later operations by empty ticks, which the emitter collapses, and reproduces the parent's price; it is not a waiting-noise control.

## Absorbing a source leg into the actual incumbent

At clock 39 the incumbent's `CX16,15` erases the copied leg. M15 at 40 reads the resulting zero. The terminal later recopies data with `CX16,15` at clock 46. However the intervening A preparation has `CX9,15` at 41, `CX21,15` at 42, `CX15,14` at 43, `CX15,9` at 44 and `CX9,15` at 45. Conjugating the earlier X15 contribution through this fixed A subcircuit maps it to X9 X14, not X15. Therefore deleting the erase, read and recopy while keeping the existing encoder does not implement the same A interface; the copied-data dependence fans into other A qubits.

`absorb_search.py` tests 64 literal incumbent circuits. Every circuit deletes source `CX16,15` at 39 and M15 at 40; the six independent deletion choices are those five q15 A-encoder CX gates and final `CX16,15` at 46. It drops all original acceptance rows and derives all noiseless deterministic record relations afresh, so a changed record labeling is not presumed. No variant is raw-valid Steane output under that record contract. This bounded deletion result excludes neither changes to other gates nor added correction gates, redesigned terminal resources, multi-leg interfaces, physical frame correction, or random-record postselection. The test is not a global impossibility theorem. See `absorb_search.log` and `absorb_search.json` for all variants and raw diagnostics.

The path to an actual improvement requires co-designing the terminal A isometry or a larger source window so that the live parity's propagated support is useful at the terminal measurement. The full accepted-map and physical noise must then be evaluated; fewer CX gates or the existence of this witness alone do not establish lower conditional loss. The complete `isometry_search.json` ledger is retained in `isometry_search_parts/index.json` and its readable parts; run `python work/lanes/CONTINUE_20261028/restore_ledgers.py` to reconstruct it byte-for-byte.

## Actual incumbent joint replacement and isometry

A constructive replacement now exists on the full incumbent. The source's `CX16,15` at 39 and M15 at 40 are removed, as is terminal `CX16,15` at 46. Before the incumbent A network, six added native gates fan out the retained q15 tag:

`CX15,14; CX14,13; CX15,14; CX14,13; CX13,7; CX13,12`.

The intermediate q14 state is restored by the first four gates. The full circuit, with all deterministic records recomputed, passes the raw check (all six code stabilizers +1, zero ideal infidelity). It is 416 CX and 55 clocks. The exact all-orders loss is **7.338708952633611e-5**, acceptance **0.4151343748644743**. It fails acceptance and is materially worse than the 49-clock incumbent. This is a complete noisy physical circuit, not an ideal-resource diagnostic.

The local propagation algebra explains the joint interface. At the start of clock 41, conjugating X tags through the existing encoder up to its final copy gives the following images, written as sets of physical cells:

| Input X tag | Output X support |
|---|---|
| 7 | 13 |
| 14 | 7,13,14 |
| 13 | 7,12,13 |
| 9 | 8,14,15 |
| 8 | 9,13,15 |
| 21 | 9,14,21 |
| 15 | 9,14 |
| 12 | 12 |

On this fixed network, the physical tag input `7,13,15,12` propagates to `7,9,14`. This differs from the desired X15 by `X7 X9 X14 X15`, an X stabilizer of the intended A resource. The q12 leg is essential to cancel the cross-block image created by the incumbent `CX13,12` at 41. Enumerating all four independent A X-stabilizer combinations and these eight input columns yields 16 preimages of X15 modulo A stabilizers; **all include 7, 13, 15 and 12**, with the other four inputs optional. This statement is scoped to the fixed incumbent encoder and this X-stabilizer equivalence; it is not a bound on redesigned networks, frames or measured-helper instruments.

A five-gate construction deletes the first `CX15,14`: `CX14,13; CX15,14; CX14,13; CX13,7; CX13,12`. It deliberately leaves an extra tag on q14; the resulting tag support is `9,13`, which differs from desired X15 by the A stabilizer `X9 X13 X15`. The full physical five-CX construction has 415 CX, 54 clocks and passes raw Steane correctness after a fresh deterministic contract. Its exact all-orders loss is **6.833230355928453e-5** at acceptance **0.4263680173940226**, so it is inadmissible and worse than the incumbent. Exhausting deletion/reversal choices for these five added gates yielded exactly one raw-valid choice, the five-gate construction, among 243 tested; see `fanout_orient.json` and `fanout_orient.log`.

The three bounded native schedule proposals for the five-CX construction each remained at 54 clocks. One scored acceptance **0.463303** and loss **2.73039e-4 ± 1.98e-5** in a one-million-shot check; this is a noisy sampled control, not an exact mean, and fails acceptance. These are only three feasible schedules; neither their 54-clock depth nor their score is a lower bound on other schedules or joint designs.

The unscheduled five-CX circuit has **c1=0**, so its substantially worse exact loss is not explained by an accepted single-fault component alone. Two full-window schedule proposals also passed raw correctness: a 53-clock proposal had one-million-shot acceptance .373327 and sampled loss .00023036; a 54-clock late-preparation proposal had acceptance .445828 and sampled loss .00010206. Both fail acceptance. These samples are not exact means or global scheduling bounds; their purpose was to test whether reducing clock count alone repaired this concrete construction.
