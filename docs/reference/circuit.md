# Our circuit and its search tools
Serves: G1, G2. Read before changing the circuit, its layout or the search code.

## Structure of the incumbent (`work/lanes/MAIN/v37d`; lineage in SOTA)
GLOBAL's R46 layout: data D = [6,20,19,10,2,22,16] (code order, the JSON `data_qubits`); B, the source of the last CX
into each data qubit, = [12,26,25,11,3,28,17]; read A and C from the round in the QASM. 406 CX, 48 native ticks,
round R45 (one tick earlier than v37a's).
1. **Prefix**: Gidney's d=3 cultivation stages (injection, double-cat check with T/T† layers) plus PRESYN's blue XZ
   stabilizer check, then coherent data hops into D. COMPLETE's end: the blue check's last CX reversed with its X/Z
   readout ports exchanged, a measured-Z state reused for a data hop, direct Z-read handoffs instead of resets, which
   moves the round one tick earlier.
2. **Waiting data**: live-live CX pairs, echoed parity checks, continuous and known-state guards, measured-Z inits
   where the record can be a detector (FINDINGS "Gadgets on waiting qubits").
3. **A**: Steane \|+_L⟩ by an 11-CX encoder synthesized against the actual cell releases; data control onto A (D→A);
   A partial decoder (two CXs and an MX on three A qubits read a logical-X representative that commutes with D→A, a
   deterministic flag); both A-flag-gap helpers on the grid (fresh helpers on the two data that gap for the decoder).
4. **B/C**: correlated rank-three resource Σ_x \|x⟩_B\|x⟩_C (65 CX, warm-started on R46's cells); transversal B→C
   leaves B = \|0_L⟩ and C as seven literal-zero detectors; B controls onto the data in the round and is read in X.
5. **Detectors and output**: `// DETECTOR c[..] ...` lines carry every parity; the judge then decodes the six data
   stabilizers ideally (judge.md).

Every gate, init, measurement and idle tick is noisy (judge.md), so lifetimes and timing are design variables.

## Evaluators (rank by all orders; the others diagnose, confirm or gate)
- **All orders** (AGENTS): `cd work/lanes/MAIN/sparse; ../../../../.venv/bin/python sparse_walsh.py <path/stem> 72 canonical 16`,
  ≈ 1 s (7 s at 1 process); prints JSON with loss and acceptance. Scope: barriers over all used qubits, no
  FRAME/POSTSELECT, ≤ 20 T. `compile_best` replays saved detector bases (`basis_warm.json`) and searches only above
  width 9. A result cache must key on the QASM sha256, the ordered `data_qubits` and the evaluator files' hashes. After
  editing `sparse_walsh.py`, rsync it to the hosts and restart long searches (FINDINGS "Failures").
- **With FRAME lines and S/Pauli gates**: `work/lanes/WHOLEEND/sparseframe/` (called by WHOLEEND's `price.py`;
  verified against the organizer's raw correctness check).
- **Exact 2nd + 3rd order with sensitivities**: `work/lanes/EVAL/exact2.py <qasm> [--top N] [--json f] [--third]`.
- **3-seed official MC**: `work/lanes/MAIN/spec/mc3.py <stem>`; one seed hides ≈ 1%.
- **Region counterfactuals**: `cd work/lanes/MAIN/sparse; ../../../../.venv/bin/python region.py ../<stem> <spec.json> 16`,
  spec = `{"name", "units": [[time, [qubits]], ...]}`: the named ops' noise channels made perfect. The cut sweep
  (every op before tick t0 perfect) is `work/lanes/TERMINAL/cut.py`.
- **Per-channel counterfactuals**: `cd work/lanes/MAIN/sparse; ../../../../.venv/bin/python adjoint_ablation.py ../<stem> 72`
  (one process, ≈ 1 min; each channel made perfect in turn; values overlap, not additive).
- **Phantom gadgets** (ideal adjacency, off-grid ancillas, up to 40 qubits): `work/lanes/ACCBUY/sparse40/`.
- **Terminal model** (exact second order of any ending with perfect resources): `work/lanes/TERM/terminal_model.py`;
  block-transversal endings: `work/lanes/ENDSEARCH/MODEL.md`.
- **Judge speed**: `work/fast_check.py <qasm> <json> 1000000 1` prints the seconds; a finalist stays within 1.5× the
  incumbent's, and `promote.sh` refuses > 20 s per 1e6 shots.

## Search machinery
Lanes copy the tools they use into their own dirs, so a fix in one lane reaches no other. Code of removed lanes:
`git log --oneline -1 -- work/lanes/<LANE>` names the removing commit (use its `^`).
- Greedy repair on any stem (singles, connected bundles, guard trades, retiming, joint extension, acceptance buying):
  `work/lanes/MERGE/` (`menu.py`, `lib.py`, `elements.py`, `joint.py`); cached pricing keyed by sha256:
  `work/lanes/BUNDLE/ev.py`.
- Gadget libraries: `work/lanes/INTEG/` (`lib.py`, `gadgets.py`, `joint.py`), `INTEG2/`, `ACCBUY/` (`kstate.py`,
  `greedy.py`).
- A encoders: exhaustive 11–13-CX enumeration `work/lanes/EXENC/` (`exact.cpp`, `exenc.py`); A process windows
  (encoder, guards, decoder jointly) `work/lanes/AJOINT/`.
- B/C resource synthesis: `work/lanes/BFLAG/` (`synth_bc.py`, `lns3.py`, proxy J), adapted to R46 in
  `work/lanes/GLOBAL/`.
- Layout and timing CP-SAT: `work/lanes/EARLY/layout.py`, `work/lanes/R43/`, GLOBAL's R46 models; square layouts with a
  Steane automorphism: `work/lanes/SQUARE/` (`find_layout.py`, `layout_model.py`).
- Floors: `work/lanes/BOUND/` (any-circuit certificate), `work/lanes/WHOLEEND/logs/floors_exact_certificate.json`
  (outputs without a CX at T−1).
