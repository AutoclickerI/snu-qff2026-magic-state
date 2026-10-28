# Architecture audit: direct C4-concatenated cultivation

## Finding and scope

An A/B/C square tail is not a mathematical requirement. The distinct physical architecture most worth a bounded falsification test is **direct preparation and verification of the magic state in seven four-qubit error-detecting tiles, concatenated with the Steane code**, followed by local parallel tile contraction into seven live Steane outputs. This is a construction hypothesis, not a complete candidate or evidence of an improvement. It deliberately avoids preparing a finished seven-qubit source and then adding tiles late, a recipe that has already failed.

The motivation is concrete: the checked ideal-input two-clock tile contraction is 2.192096e-5, just above the universal 2.18925128e-5 floor, whereas the perfect-resource square round is 2.555843e-5. Both numbers are in `docs/FINDINGS.md` and use this judge's noise model. Those tail-only numbers do not price source preparation and do not add linearly to a full conditional loss. Existing direct encoded-check and late-growth experiments were bad: even a perfect seven-qubit input with minimal 3-CX tile growth cost 8.717e-5 in the tested setting, while early growth plus both outer checks gave 1.105e-4 at acceptance 0.372. They strongly argue against a superficial implementation. The untested change is to keep the useful state encoded from its creation, replace the old stabilizer-measurement schedule, and exploit physical shared checks; no result here demonstrates that this overcomes those losses.

The current incumbent's exact mean is 3.566732196898089e-5, A=0.5016443323, versus the board's 2026-10-28 09:46 KST sampled key 2.767689e-5 (277 CX). The latter is a draw, not the leader's exact mean. The gap from the theoretical floor to that draw is only 5.784377e-6. The floor certificate's bound L >= 2.18925128e-5 + 0.00315432 w implies, in its defined residual model, w <= 0.001834 for an exact mean at that numerical target. This is a necessary threshold, not a prediction of achievable loss. A >= 0.5002 is the local expected-acceptance selection margin, not spare budget: the incumbent has only ~0.00144 margin under the current selection convention.

## Exact tile and live output

Put four physical qubits on each 2x2 tile:

    H  D
    L  K

Prepare an arbitrary input |psi> on D, |0> on H,L,K, then execute H(H); CX(H,D); CX(D,K) and CX(H,L) in parallel. Its stabilizers are X_H X_D X_L X_K, Z_D Z_K and Z_H Z_L; logical X is X_D X_K and logical Z is Z_H Z_D. Concatenating these seven logical qubits with the Steane stabilizers defines a [[28,1,at least 2]] state; its full distance and fault-tolerance under a proposed preparation must be separately certified.

The terminal inverse consists of CX(D,K) and CX(H,L) in one clock, followed by CX(H,D) while measuring K and L in Z in the next. Both measurement records are zero in the ideal encoded space, and D carries the live original logical qubit; H remains |+> after the ideal inverse. No physical correction is required for the accepted ideal branch. The measurements are not a complete outer-code check; a noisy input can pass inner checks while carrying a damaging Steane syndrome or logical error. This is exactly why the source/instrument must be designed together.

`tile_audit.py` explicitly simulates the ideal tile on |0>, |1> and (|0>+i|1>)/sqrt(2): maximum amplitude error is 5.56e-17. This is an ideal unitary check only; it is not the organizer's raw-output oracle, a fault-tolerance certificate, or a full candidate.

## A concrete 6x6 layout and gate skeleton

Use row-major cells 0–35. One 28-cell witness is seven tiles:

| Tile | H | D | L | K |
|---|---:|---:|---:|---:|
| 1 | 0 | 1 | 6 | 7 |
| 2 | 2 | 3 | 8 | 9 |
| 3 | 4 | 5 | 10 | 11 |
| 4 | 12 | 13 | 18 | 19 |
| 5 | 16 | 17 | 22 | 23 |
| 6 | 24 | 25 | 30 | 31 |
| 7 | 28 | 29 | 34 | 35 |

The eight other cells are {14,15,20,21,26,27,32,33}. They form one connected region, but reach only five tiles. `tile_audit.py` enumerates all 242 packings of seven disjoint 2x2 squares in the 6x6 grid: only 12 have connected free cells, and none of those reaches more than five tiles. Thus a stationary shared flag bus cannot touch all seven tiles using only the free region. This does not rule out a moving bus, temporarily borrowed tile qubits, non-square tiles, or a time-varying layout.

An implementable *program for building* the candidate, not a finished circuit, is:

1. Generate the desired concatenated magic state directly, using the above logical X/Z representatives. Start from the actual phase-polynomial source or an independently synthesised encoded injection; do not apply seven complete growth gadgets after a separately finished noisy source. For each desired Steane outer stabilizer, expand its X and Z support onto the two-qubit tile logical representatives and simplify products with the tile stabilizers before selecting physical checks.
2. At the listed locations, schedule the checks as a **streaming flag bus** through the connected free region, borrowing cells or moving a tile only for the two unreachable tiles. Measure flag records and incorporate their actual parity relations. A logical check crossing tiles has to include the physical bridge and its preparation/measurement faults. Do not infer nearest-neighbor implementability from block-transversal algebra: horizontally adjacent 2x2 tiles expose only two boundary edges, not four parallel matching edges.
3. Run the two-clock contraction simultaneously on all seven tiles and return D=[1,3,5,13,17,25,29] as the live output. The two first-clock CXs in each tile are disjoint; in the second clock H→D is disjoint from K/L measurements. Assign outer Steane indices to D by an allowed code automorphism or use the output specification to preserve the required code. Include every used qubit in each barrier.
4. Before any costly search, verify exact noiseless output state, ideal record dependencies and all six output stabilizers with the raw oracle. Enumerate single faults through source, bus, bridges and final two clocks; detect every harmful accepted single or explicitly quantify it. Then price all orders at p=0.001 and require acceptance >=0.5002 and a timed official gate check. Reject high-depth candidates before repair if source/flag acceptance is already below margin.

The skeleton is intentionally incomplete at steps 1–2: there is no tested flag-bus circuit, native logical injection circuit, final QASM, full-noise score or runtime measurement. In particular, a weight-eight expanded stabilizer cannot be assumed safe merely because its noiseless parity is right. A bus fault can propagate across data, collapse logical information, or produce correlated errors that alias the Steane decoder. Tile waits and repeated bridge operations can erase the entire 3.64e-6 tail-only advantage. Large multi-round verification also consumes acceptance and can breach the one-hour judge limit. A successful design requires all those effects to be measured.

## Architecture alternatives and evidence

* Gidney, Shutty and Jones, [Magic state cultivation](https://arxiv.org/abs/2409.17595), grows and verifies a single state. Its paper's large-code results are not a live-output 6x6 Steane score under this judge. Here the source is already based on its d=3 stage; the proposal changes the code being cultivated, not merely its solver.
* Itogawa et al., [zero-level distillation](https://doi.org/10.1103/thxx-njr6), combines a Steane magic-state encoding and logical-H test with a subsequent surface-code transfer. That transfer targets a surface-code output, while this task requires a live Steane output. Their approximately 100 p² figure uses their own model and end-to-end protocol and is not an estimate of this tile proposal.
* Daguerre and Kim, [code switching revisited](https://doi.org/10.1103/PhysRevResearch.7.023080), uses a qRM-to-Steane switch with flag postselection. Its published simulation excludes idling noise and does not establish a 6x6 implementation. The repository already tested two-block switching at grid-free 9.02e-5 under this judge's full noise; a new planar qRM source remains open but is weaker evidence than the tile tail's known local contraction.
* The SRP/RP cultivation proposal [uses nonlocal connectivity](https://doi.org/10.1103/9kys-3whh) and grows to a surface-code target. Its reported resource/fidelity numbers cannot be transferred to this 36-cell live-Steane contract without routing and conversion. A surface-to-Steane conversion is therefore a new expensive verification interface, not a free shortcut.

The proposed tile architecture is higher risk than the concurrent CSS-source and compact-instrument work. Its merit is that it attacks the proven terminal floor itself, rather than spending the entire effort reproducing a known expensive A/B/C interaction. It should be abandoned promptly if a physically explicit direct encoded source fails the single-fault or acceptance gates; ideal-tail success alone does not justify more tuning.
