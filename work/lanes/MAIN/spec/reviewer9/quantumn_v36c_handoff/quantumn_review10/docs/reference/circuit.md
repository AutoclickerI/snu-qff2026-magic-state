# Our circuit and its search tools
Serves: G1, G2. Read before changing the circuit, its layout or the search code.

## Structure of the incumbent (`work/lanes/MAIN/v36a`, PLAN "Status")
Roles (physical qubits, code order): data D = [0,20,7,10,3,22,21] (the JSON `data_qubits`), A = [1,14,8,9,2,16,15],
B = [6,26,13,11,4,23,27], C = [12,25,19,17,5,29,28]. 207 CX, 47 native ticks, round R44.
1. **Prefix**: Gidney's d=3 cultivation stages (injection, double-cat check with T/T† layers) plus PRESYN's blue XZ
   stabilizer check, then coherent two-CX data hops into D. Source checks c54–c57 and blue outputs c64/c67 are detectors.
2. **Waiting data**: five storage guards (helper reset, CX data→helper, measured) on the data runs before the round;
   echoed parity checks (helper prepared, CX twice around a window, measured) are the alternative gadget (ST2,
   WAITPROT). Measured-Z inits replace resets where the record can be a detector.
3. **A**: Steane |+_L⟩ by a 12-CX encoder at ticks 37–43 synthesized against the actual cell releases (X pivots
   14, 8, 9, 16). Data controls onto A (D→A) at 43–44, before B. **A partial decoder**: CX9→15 (44), CX8→9 (45), MX8 (46)
   reads X8·X9·X15, a logical-X representative that commutes with D→A, as a deterministic flag (record c16).
4. **B/C**: correlated rank-three resource Σ_x |x⟩_B|x⟩_C (57 CX, FRESH); transversal B→C leaves B = |0_L⟩ and C as
   seven literal-zero detectors. B controls onto the data in the round and is read in X; terminal readout edges
   (14→15 instrument, copies) re-express detector rows.
5. **Detectors and output**: `// DETECTOR c[..] ...` lines carry every parity; the judge then decodes the six data
   stabilizers ideally (judge.md).

Every gate, init, measurement and idle tick is noisy (judge.md), so lifetimes and timing are design variables.

## Evaluators (rank by all orders; the others diagnose, confirm or gate)
- **All orders** (AGENTS): `cd work/lanes/MAIN/sparse; ../../../../.venv/bin/python sparse_walsh.py <path/stem> 72 canonical 16`,
  ~11–35 s. Scope: barriers over all used qubits, no FRAME/POSTSELECT, ≤ 20 T rotations, ideal acceptance ≈ 1.
- **Exact 2nd + 3rd order with sensitivities**: `work/lanes/EVAL/exact2.py <qasm> [--top N] [--json f] [--third]`
  (loss by fault pair, per-channel gradients). Converges slowly below acceptance ≈ 0.5; use all orders to rank.
- **3-seed official MC**: `work/lanes/MAIN/spec/mc3.py <stem>`; one seed hides ≈ 1%.
- **Per-channel counterfactuals** (which noise matters, all orders): `cd work/lanes/MAIN/sparse; ../../../../.venv/bin/python adjoint_ablation.py ../<stem> 72`
  (~2 min; each channel made perfect in turn, values overlap, not additive; reviewer 8's tool).
- **Speed**: `work/lanes/XTIM/speed_predict.py <stem>` (seconds per 1e6 shots; > 20 s is refused by promote.sh).

## Search machinery in the lanes
- Resource synthesis (CNOT circuits for B/C, clean/FT contracts): `work/lanes/FRESH/{synth,sat_core,ft}.py`.
- A-encoder enumeration (all rank-four states, 11–13 CX paths): `work/lanes/EXENC/exact.cpp`, `exenc.py`.
- B/C boundary cache (B/C variants in 0.035 s against a fixed exterior): `work/lanes/BCPOL/cache*.py`, `boundary_api.py`.
- Critical path, timing and A synthesis on a fixed exterior: `work/lanes/SEPBC/` (`exenc.py`, plan JSONs per candidate).
- In-place B∪C regions and end-state enumeration: `work/lanes/ENDSTATE/`; full prefix/round co-design with CP-SAT and
  exact-gradient retiming: `work/lanes/ST1/{redesign,gradient_retime}.py`.
- Population search and acceptance knapsack: `work/lanes/ST2/pop35_*.py`, `knapsack_select.py`; region ledger `ledger.py`.
