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
- **Selection** (the one promotion policy; lanes add no caps of their own): the finalist is the lowest exact L at exact
  A ≥ 0.5002, raw-valid, `gates_ok`, by the expected-key speed rule below; c1 = 0 is a preference, not a gate.
  J_τ = A(L − τ) is only a search heuristic, with τ = the current incumbent's L: MERGE's τ fixed at v37b's L made `greedy_pass.choose` trade loss for acceptance
  (cost so far 6.5e-11). Keep the (L, A) Pareto front for later acceptance buys.
- **Validity before ranking**: the all-orders price checks only the decoded loss; a build that changes the outputs or
  the tail must first have its six noiseless output stabilizers at +1 (the judge's raw code-space check; reviewer 16:
  H·T⁴·H = X on one output keeps decoded loss 0 and fails). Stem files must be named by QASM plus ordered
  `data_qubits`: `qtools.write_stem`.
- **All orders** (AGENTS): `work/tools/qtools` (README there): `price` (loss, acceptance; rejects raw-invalid builds),
  `validate` (adds judge gates and seconds at 1e6), `is_finalist` (the policy above), `write_stem`. v37i: 2.7 s warm vs
  447 s with MAIN's old copy; the shared registry `work/tools/bases.json` replays every saved detector basis and trains only
  above width 12; the cache keys on QASM sha256, ordered outputs and the package's source hashes. Scope: barriers over
  all used qubits, no FRAME/POSTSELECT, ≤ 20 T. After editing qtools, run its tests, `pin_hosts.py`, and restart
  long searches (FINDINGS "Failures").
- **With FRAME lines and S/Pauli gates**: `work/lanes/WHOLEEND/sparseframe/` (called by WHOLEEND's `price.py`;
  verified against the organizer's raw correctness check).
- **Exact 2nd + 3rd order with sensitivities**: `work/lanes/EVAL/exact2.py <qasm> [--top N] [--json f] [--third]`.
- **Detector-span completeness** (per new incumbent): `work/lanes/INTEG2/detgap.py` lists the deterministic record
  parities outside the declared detector span (Clifford surrogate); price each and small combinations by all orders, never
  prune them by second order (reviewer 17: v37f had 6 missing, c309 gains −8.3e-9 at zero second-order effect).
- **3-seed official MC**: `work/lanes/MAIN/spec/mc3.py <stem>`; one seed hides ≈ 1%.
- **Region counterfactuals**: `cd work/lanes/MAIN/sparse; ../../../../.venv/bin/python region.py ../<stem> <spec.json> 16`,
  spec = `{"name", "units": [[time, [qubits]], ...]}`: the named ops' noise channels made perfect. The cut sweep
  (every op before tick t0 perfect) is `work/lanes/TERMINAL/cut.py`.
- **Per-channel counterfactuals**: `cd work/lanes/MAIN/sparse; ../../../../.venv/bin/python adjoint_ablation.py ../<stem> 72`
  (one process, ≈ 1 min; each channel made perfect in turn; values overlap, not additive).
- **Phantom gadgets** (ideal adjacency, off-grid ancillas, up to 40 qubits): `work/lanes/ACCBUY/sparse40/`.
- **Terminal model** (exact second order of any ending with perfect resources): `work/lanes/TERM/terminal_model.py`;
  block-transversal endings: `work/lanes/ENDSEARCH/MODEL.md`.
- **Judge speed**: `work/fast_check.py <qasm> <json> 1000000 1` prints the seconds. `promote.sh` refuses > 20 s per 1e6
  shots, our margin under the one-hour scoring limit (CONSTRAINTS rule 5; ≈ 27 server minutes at 1e8). Promotion compares expected keys: a finalist wins if its loss gain exceeds
  ≈ 1.1e-7 × log2(its judge time / the incumbent's), timed on the same host in the same minutes (the hourly race's draw
  count falls with judge time; FINDINGS "Score spread per stem").

## Search machinery
Pricing, stems, validity and policy live in `work/tools/qtools`; lanes still running copied tools switch at their next
restart, and new lanes import qtools instead of copying. Code of removed lanes:
`git log --oneline -1 -- work/lanes/<LANE>` names the removing commit (use its `^`).
- Greedy repair on any stem (singles, connected bundles, guard trades, retiming, joint extension, acceptance buying,
  pass 4's ejections, multi-buyer funding and signature pairs) in `work/lanes/MERGE/`. A known mechanism the grammar cannot
  express is never searched: the reset-then-herald compound (R one tick earlier, M plus detector in its place; reviewer 17's
  q17, −8.3e-8, was missing until pass 5). Code: `menu.py`, `lib.py`, `elements.py`, `joint.py`; cached pricing keyed by sha256:
  `work/lanes/BUNDLE/ev.py`.
- Gadget libraries: `work/lanes/INTEG/` (`lib.py`, `gadgets.py`, `joint.py`), `INTEG2/`, `ACCBUY/` (`kstate.py`,
  `greedy.py`).
- A encoders: exhaustive 11–13-CX enumeration `work/lanes/EXENC/` (`exact.cpp`, `exenc.py`); A process windows
  (encoder, guards, decoder jointly) `work/lanes/AJOINT/`.
- B/C resource synthesis: `work/lanes/BFLAG/` (`synth_bc.py`, `lns3.py`, proxy J), adapted to R46 in
  `work/lanes/GLOBAL/`.
- Layout and timing CP-SAT: `work/lanes/EARLY/layout.py`, `work/lanes/R43/`, GLOBAL's R46 models; square layouts with a
  Steane automorphism: `work/lanes/SQUARE/` (`find_layout.py`, `layout_model.py`).
- Floors: `work/lanes/BOUND/` (any-circuit certificate, 1.366e-5), reviewer 18's penultimate-layer certificate
  (`work/lanes/MAIN/spec/reviewer18/penultimate_bound_certificate.py`, 2.189e-5; C4–Steane tail `c4_steane_tail.py`), `work/lanes/WHOLEEND/logs/floors_exact_certificate.json`
  (outputs without a CX at T−1).
