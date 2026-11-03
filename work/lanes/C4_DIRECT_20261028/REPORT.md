# Direct C4–Steane source from initialization

## Result

A complete abstract-connectivity C4–Steane circuit was constructed **from tile initialization**, rather than by growing a finished seven-qubit magic state. It includes the physical tile encoders, logical magic injection, transversal outer encoder, both nondemolition outer syndrome meters, two seven-cat logical checks and the two-clock tile contraction. All physical gates, resets, measurements and idles are noisy.

All six tested circuits pass the raw Steane-state check but fail the acceptance requirement at p=.001, even before grid routing. The simplest unflagged control has 202 CX and 43 clocks, exact loss **.006530844922103654**, acceptance **.3935079593885619**, and accepted single-fault coefficient **4.8833333333**. A physical shared-flag variant reduces that coefficient but needs more time and further reduces acceptance. None is a native candidate or a SOTA result; the finite constructions do not exclude other directly concatenated architectures.

| Construction | CX / clocks | c1; harmful components | Exact loss | Acceptance |
|---|---:|---:|---:|---:|
| Unflagged outer meters and cats | 202 / 43 | 4.88333; 55 | .0065308449 | .3935079594 |
| Two in-place cat parity checks per round | 210 / 49 | 1.58333; 35 | .0046291849 | .3312852284 |
| One shared q35 parity meter per cat round | 206 / 49 | .38333; 15 | .0037124788 | .3287931438 |
| Two serial q35 checks per cat, second checks 28/32 | 210 / 57 | .38333; 15 | .0062998104 | .2612925954 |
| Two serial q35 checks per cat, corrected second checks 28/29 | 210 / 57 | .1166667; 7 | .0061683014 | .2625359812 |
| Serial three-flag SpiderCSS outer-X meter plus corrected cat flags | 216 / 60 | .4666667; 7 | .0091898680 | .2257296463 |

The table gives exact all-orders conditional losses and physical acceptance; c1 is a diagnostic rather than a score or eligibility condition. The QASM, ordered-output JSON and complete raw/singles/exact receipt for each row are named `direct_unflagged`, `direct_flagged`, `direct_meterflag`, `direct_two_meterflags`, `direct_two_repairedflags`, and `flagged_meter` respectively. Their builder scripts are in this lane. Every construction uses only 36 physical wires, but many CX connections are nonlocal and are deliberately priced with abstract connectivity. No resource or output wait is made perfect.

## Physical construction and instrument details

Each tile uses `(H,D,L,K)=(4i,4i+1,4i+2,4i+3)`. It starts from an encoded logical input using RX(H), CX(H,D), then CX(D,K) and CX(H,L) in parallel. The logical Z seed on tile 2 is injected physically via CX(H,D), T(D), CX(H,D). The two additional source logical CX gates and nine outer Steane encoder logical CX gates are each expanded into four physical transversal CX gates. This places the state in the concatenated code before the logical magic checks; the independently contracted pre-check state was verified as raw |T_L>.

The outer Z-syndrome meter is a physical seven-qubit |+L> target. It receives two data-control CXs per outer coordinate, one from H and one from D, and its Z measurements furnish the three Steane syndrome parities. The outer X-syndrome meter is a physical |0L> control; it couples to D and K of each tile and is measured in X, again detecting the three syndrome parities. Their logical meter outcomes remain random and are not incorrectly postselected. Using |0L> for the Z-read target instead actually measured logical Z and dephased the magic state to ideal infidelity .5; raw-state analysis exposed and corrected that construction error.

For the two cat rounds, each 7-cell GHZ control acts on both D and K of the corresponding tile. One logical-T basis-change sandwich is shared across both rounds: seven physical T gadgets occur before the first coupling and seven T-dagger gadgets after the second. No noncommuting outer syndrome operation is inserted between the rounds. Together with the seed T, each circuit has 15 physical T/T-dagger gates. The seven cat cells are reused between rounds. The two-clock inverse applies CX(D,K) and CX(H,L), then CX(H,D) and Z measurements on K and L; every contraction record is physically checked.

The shared-q35 flag variant checks cat Z parities (29,30) and (28,29), serially reusing that one helper per round. Both reset, both cat-to-helper CXs and the helper Z read are actual noisy operations. The corrected second parity detects the correlated cat root/branch X components that were invisible to the earlier (28,32) choice. In `direct_two_repairedflags`, all seven remaining accepted harmful single components are in the outer X-meter encoder: CX28→32, CX29→34 and CX31→33 at clock20, plus CX28→34, CX29→30 and CX31→32 at clock21. Their Pauli components and coefficients are in that circuit's result receipt.

`flagged_meter.py` replaces the outer X meter with the 15-CX/three-flag SpiderCSS Steane-zero preparation, using the one spare q35 sequentially for all three flags. Its 18-clock local factory schedule is optimal for its stated wire-order and serial-flag constraints (`spider_serial.json`); the factory is overlapped with early outer encoding. It nevertheless has seven harmful single components, c1=.4666667, and acceptance .22573. This tests one flagged meter construction, not every possible verified meter.

## Geometry and interpretation

The independent exact tile audit in `work/lanes/CONTINUE_20261028/c4_identity_audit.json` verifies the logical T gadget and coherent controlled X_D X_K action on the tile code space. It is an ideal identity, not an FT or noise certificate. A stationary cat control cannot be adjacent to both D and K of a square tile on the bipartite grid. The native three-CX bridge `CX(D,K); CX(cat,D); CX(D,K)` implements the two desired cat-controlled Xs but adds a physical CX per cat/tile interaction and must be audited for correlated faults. Separately, the finite audit in `work/lanes/CONTINUE_20261028/c4_geometry_audit.json` examines all 242 disjoint seven-square packings: 28 admit distinct external cat neighbors for all seven tiles, but none admits such a matching with those seven cat cells mutually connected. That is a scoped static-layout obstruction, not a bound on moving cats, bus interactions or other encodings.

The abstract results already fail acceptance substantially, and native bridges, cat movement and routing have not been added. No conclusion about all C4 or other codes follows from these bounded constructions. No submission or production change was made.
