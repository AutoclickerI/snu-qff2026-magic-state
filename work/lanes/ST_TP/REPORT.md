# ST_TP: teleport-output Steane round

## 1. Grid-free exact proxy (tp.py; poc/steane/proxy2.joint_loss, judge noise, p=1e-3)

| O (=A) encoder | current round | teleport round | first order |
|---|---|---|---|
| standard dual encoders | 3.2324e-5 | 3.2324e-5 | 0 |
| L5 A s7307 (11 CX) | 3.5386e-5 | 3.5386e-5 | 0 |
| L5 A exact (12 CX) | 3.5453e-5 | 3.5453e-5 | 0 |

(FINDINGS' 3.20e-5 is this 3.2324e-5 rounded down; steane.score(vblock=True) gives the same.) Teleport = current to all
printed digits: the two rounds are the same fault graph with D and O exchanging the roles of control/target and of
"measured block", and DEPOLARIZE2 is symmetric. Observables in tp.py: Z_L(O) xor Z_L(D)init xor m (m = XOR of the 7 D
bits), X_L(O) xor X_L(D)init, X stabilizers of O xor D's init X stabilizers, Z stabilizers of O alone; noiseless
determinism of all detectors/observables is asserted by stim. Validity of the teleport and its frame are therefore checked.

## 2. Grid feasibility with chain adjacency d_i ~ o_i ~ b_i ~ c_i: NONE FOUND (model infeasible, proven fast)

layout.py (CP-SAT, time-expanded). Model: 48 placements (8 symmetries x translations of the pre-stage footprint, data and
cat-ancilla cells transform together); O,B,C final cells; pairings d-o and b-c over all 168 Hamming-code automorphisms
(o-b identity); per block either in place (finals + helpers connected, helpers busy only during that block's prep) or
staged (stage cells + helpers connected, member i hops to a final cell adjacent to its stage cell, reset dst / cx / cx);
free cells release 0, ancilla cells 33, data never; a cell may be reused in time (helper/stage cell of X as final cell of Y
only if X's use ended before Y's start/hop); all 28 final cells (7 D + 21) busy from their block start to the end;
checkerboard colour counts imposed.

Results (owl, docker, 100-150 s limit each, all returned INFEASIBLE = proof within the model, not UNKNOWN):
- 48/48 placements INFEASIBLE with fixed data.
- 48/48 INFEASIBLE when each data qubit may also hop one cell (T >= 35).
- spot checks (placements 3, 14, 21) INFEASIBLE with data moves of up to 2 cells (T >= 39) and with staged members up
  to 2 cells from their finals.
- Without the time reuse rule (cells reusable freely) the same chains ARE feasible (e.g. placement 14, T=40, 7 blocks
  in place); with it only O+B or O+C connected is feasible (T=50), never B+C or all three. Cause: all 28 finals persist
  to the end, so the block prepared last may use only the 8 spare cells (6 usable; cells 1 and 2 are enclosed) as helpers,
  and the earlier ones only spare cells plus finals of later blocks; no placement lets all three blocks do this.
- A 7x7 board with the same footprint is feasible (centre placement, T=45, all in place), so the obstruction is area.
- Final-cell chain alone (no connectivity) is feasible in 32 of 48 placements; the footprint corner placement (original
  cells) is not (cells 6,1,2 are dead ends: cell 6 has one free neighbour).
Evidence, not proof for the real hardware (models the encoder as a connected region; ignores lazy first-use of a cell,
which could free a cell a few steps earlier), but a robust negative: the star of the old round and the chain of the
new one both exceed the 6x6 area once C is a full block.

## 3. Not built
No feasible layout, so no circuit, no exact2/--third/tprep.check numbers.

## Side result: verifier ancillas instead of C (grid-free, same proxy, ver_scan.py)
Best single weight-3 Z verifier on B: 7.85e-5; best pair: 5.56e-5 (supports W3[0], W3[6]); three or more do not fit the
builder's schedule. Pair vs C: 5.56e-5 vs 3.23e-5 (data-side floor 2.57e-5), and the proxy excludes grid cross terms and
third order, so a verifier round would still sit above the 7.6e-5 board leader unless the rest of the circuit is clean.
O+B alone (no C) connected is feasible in the layout model (T=50 for placement 14 in place; staged variants not tuned).

# Update: joint B+C region (coordinator's trick)

layout5.py (groups: B and C prepared jointly on one connected region, O separate; time-expanded; data may hop up to K
cells, T >= 33 + 3*dist) over the 48 placements. Pipeline: mklay.py (code-ordered layout) -> o_synth.py (O prep, DR/synth CP-SAT)
-> sat_tp.py/ft_tp.py (CEGAR joint BC prep, ST_BC's tools with the layout's cells) -> merge_tp.py (teleport round, FRAME_X = XOR of
the 7 D bits, FRAME_Z empty, D/B/C detectors) -> exact2.py.

- The joint rule makes the chain FEASIBLE: 24 of 48 placements (the rest INFEASIBLE with fixed data and joint B+C, O alone).
  O joint with B (C separate): INFEASIBLE on every placement tried (placements 0-25 and 36-38, rest not run).
- Fixed data: best model T = 55-57 (O in place after BC, sequential). With data hops (<= 2-3 cells, cheap: T >= 33+3*dist) and O staged
  (prepared on cells released before 33, hopped in at 33): model T = 51 (= the L5 star reference), BC with 0-6 helpers.
- The obstruction moved to O: its cells sit next to the scattered data, so it needs 5-10 helper cells. O prep by CP-SAT:
  lay5 (5 helpers): 37 CX, depth 10, danger 2.9e-3 (compact L5 A: 11 CX, 6.7e-4); lay31 (10 helpers): 56-58 CX, danger 5e-3.
- Full circuit built and verified correct: work/lanes/ST_TP/c5.qasm/.json (layout lay5: 3 data hops, O staged on the B cells,
  O 37 CX, BC = sat_p5_18_1.json 103 CX depth 18, FT-checked). exact2: first order 3.3e-19 (teleport frame, detectors, round valid),
  round starts at step 60, 1-F (2nd order) 1.53e-4, exp(-A1) = 0.405 (< 0.55, acceptance < 0.5 fails). Not taken to --third or MC.
- Shallower BC (depth 14-16) SAT jobs on lay31/lay5 had not finished after ~1 h CPU each (killed); the 103-CX depth-18 BC and the
  10+ layer O chain are why R = 60, not 51.

Conclusion: the chain is placeable once B+C are joint, but with fixed scattered data O costs ~37+ CX and danger 3e-3, and R >= 55-60 with
usable preps, so it does not beat v12 (1.12e-4) nor keep acceptance >= 0.55. What would change this: a compact O (data hops that
make the d cells compact around 7 O cells, cost ~4e-6 per hop) together with a depth <= 14 FT joint BC on the same region; the
model has K (hop distance) and WHO (O-helper weight) knobs; layouts with O helpers <= 2 were not found within K <= 4.
