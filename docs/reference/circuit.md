# Our circuit and its search tools
Serves: G1, G2. Read before changing the circuit, its layout or the search code.

## Structure of the incumbent (`work/lanes/MAIN/v36c`; v36d–v36h add gadgets, resource r3 and guards; PLAN "Status")
Roles (physical qubits, code order): data D = [0,20,7,10,3,22,21] (the JSON `data_qubits`), A = [1,14,8,9,2,16,15],
B = [6,26,13,11,4,23,27], C = [12,25,19,17,5,29,28]. 213 CX, 47 native ticks, round R44 (B/D CX at ticks 43–44).
v36a → v36b added timing, echo and reset trades (211 CX); v36b → v36c (ST2 population) swaps echo helpers (q26–q20 out;
q20–q21 and q7–q13 in) and turns several first-use resets (q8, q9, q13, q19, q20, q1) into measured inits.
v36c → v36d (INTEG) adds acceptance-only trades and 34 gadgets on waiting qubits: live-live CX pairs, echoed parity
checks and guards (282 CX; list in `v36d.json` "integ"). v36d → v36e (BFLAG) replaces the 57-CX B/C resource by the 56-CX r3
(`work/lanes/BFLAG/syn/r3.json`), 281 CX. v36e → v36f (PRECELL) adds continuous guards (q6, q13 on q7), q14/q21 echo ends
and five late guards on idle B/C qubits from never-used cells (293 CX). v36f → v36g (INTEG2) re-integrates gadgets and
shifts six gates (320 CX). v36g → v36h (ACCBUY) adds seven known-state guards (a helper in a known state runs an identity
CX on an idle data qubit) and two init-check trades (327 CX).
1. **Prefix**: Gidney's d=3 cultivation stages (injection, double-cat check with T/T† layers) plus PRESYN's blue XZ
   stabilizer check, then coherent two-CX data hops into D. Source checks c54–c57 and blue outputs c64/c67 are detectors.
2. **Waiting data**: five storage guards (helper reset, CX data→helper, measured) on the data runs before the round;
   echoed parity checks (helper prepared, CX twice around a window, measured) are the alternative gadget (ST2,
   WAITPROT). Measured-Z inits replace resets where the record can be a detector.
3. **A**: Steane |+_L⟩ by a 12-CX encoder at ticks 37–43 synthesized against the actual cell releases (X pivots
   14, 8, 9, 16). Data controls onto A (D→A) at 43–44, before B. **A partial decoder**: CX9→15 (44), CX8→9 (45), MX8 (46)
   reads X8·X9·X15, a logical-X representative that commutes with D→A, as a deterministic flag (record c16).
4. **B/C**: correlated rank-three resource Σ_x |x⟩_B|x⟩_C (57 CX from FRESH; r3 from v36e, 56 CX); transversal B→C leaves B = |0_L⟩ and C as
   seven literal-zero detectors. B controls onto the data in the round and is read in X; terminal readout edges
   (14→15 instrument, copies) re-express detector rows.
5. **Detectors and output**: `// DETECTOR c[..] ...` lines carry every parity; the judge then decodes the six data
   stabilizers ideally (judge.md).

Every gate, init, measurement and idle tick is noisy (judge.md), so lifetimes and timing are design variables.

## Evaluators (rank by all orders; the others diagnose, confirm or gate)
- **All orders** (AGENTS): `cd work/lanes/MAIN/sparse; ../../../../.venv/bin/python sparse_walsh.py <path/stem> 72 canonical 16`,
  ≈ 1 s (v29c 0.8 s, v36h 1.3 s; 7 s at 1 process). Each noise channel is a character table on its signature image
  (uniform Pauli channels have two levels; channels with the same image merge, v36g 692 → 439 entries; EVALF, from
  reviewer 11). `compile_best` contracts in a detector basis: saved XOR sequences keyed
  by detector record sets (`basis_warm.json`: v36c from reviewer 9, v36f from INTEG2) are replayed where their rows exist,
  and 1,000 seeded hill-climb steps run only if the best width exceeds `SEARCH_WIDTH` = 9; the plain basis took ≈ 130–190 s
  on v36f/v36g. Values agree with
  the plain basis to ≈ 1e-16 absolute. Scope: barriers over all used qubits, no FRAME/POSTSELECT, ≤ 20 T rotations, ideal
  acceptance ≈ 1. After editing `sparse_walsh.py`, rsync it to the hosts and restart long searches (FINDINGS
  "Failures"); `ST2/sparse` links to it. A result cache must key on the QASM sha256, the ordered `data_qubits` and the hashes of
  `sparse_walsh.py`, `frontend.py`, `fastfill.py`, `basis_warm.json` (reviewer 11 found name-keyed caches in INTEG2
  `ev2.py`/`greedy.py` that can return a stale price).
- **Exact 2nd + 3rd order with sensitivities**: `work/lanes/EVAL/exact2.py <qasm> [--top N] [--json f] [--third]`
  (loss by fault pair, per-channel gradients). Converges slowly below acceptance ≈ 0.5; use all orders to rank.
- **3-seed official MC**: `work/lanes/MAIN/spec/mc3.py <stem>`; one seed hides ≈ 1%.
- **Region counterfactuals**: `cd work/lanes/MAIN/sparse; ../../../../.venv/bin/python region.py ../<stem> <spec.json> 16`, spec =
  `{"name", "units": [[time, [qubits]], ...]}`: the named ops' noise channels made perfect (example: `T14/spec_prefix.json`).
- **Per-channel counterfactuals** (which noise matters, all orders): `cd work/lanes/MAIN/sparse; ../../../../.venv/bin/python adjoint_ablation.py ../<stem> 72`
  (one process, ≈ 1 min; each channel made perfect in turn, values overlap, not additive; reviewer 8's tool; derivatives
  from merged-factor gradients; `v36{c,f,g,h}_adjoint_72.json`). Single Pauli components: `work/lanes/IDEAS/abl.py`.
- **Phantom gadgets** (ideal adjacency, off-grid ancillas, up to 40 qubits): `work/lanes/ACCBUY/sparse40/` (frontend
  for phantom qubits; ACCBUY `ph.py`).
- **Speed**: `work/lanes/XTIM/speed_predict.py <stem>` (seconds per 1e6 shots; > 20 s is refused by promote.sh).

## Search machinery in the lanes
Code of removed lanes: `git show b2a5243:work/lanes/<LANE>/<file>` (ENDSTATE, ST1, BCPOL, LNS) or `e438fb6^` (older);
for BCFB, COMP29, WAITPROT, `git log --oneline -1 -- work/lanes/<LANE>` names the removing commit (use its `^`).
- Floors and Steane-round mechanics: `work/lanes/DR/{relaxed,steane,synth}.py` (`synth.dangerous_z`).
- Exact 2nd/3rd order with sensitivities: `work/lanes/EVAL/exact2.py`; xtim speed: `work/lanes/XTIM/speed_predict.py`;
  slow-path atom check: `work/lanes/FRESH/general_atoms.py`.
- Resource synthesis (CNOT circuits for B/C, clean/FT contracts): `work/lanes/FRESH/{synth,sat_core,ft}.py`;
  CEGAR clean B+C preps and exact-loss feedback: `work/lanes/BCSYN2/`; shared scheduler `work/lanes/SCHED/schedule.py`.
- A-encoder enumeration (all rank-four states, 11–13 CX paths): `work/lanes/EXENC/exact.cpp`, `exenc.py`; release-aware
  A synthesis and critical path on a fixed exterior: `work/lanes/SEPBC/` (`exenc.py`, `v30/CRITICAL_PATH.md`).
- Population search with all-orders fitness and acceptance knapsack: `work/lanes/ST2/pop36_*.py`, `knapsack_select.py`,
  scorer `sparse_budget.py`; region ledger `ledger.py`.
- Gadget library, acceptance trades and joint builder: `work/lanes/INTEG/` (`lib.py`, `gadgets.py`, `joint.py`, `ev.py`);
  re-integration on a newer schedule (leave-one-out, singles, swaps, shifts): `work/lanes/INTEG2/`; known-state guards and
  greedy acceptance buying: `work/lanes/ACCBUY/` (`kstate.py`, `greedy.py`, `loo.py`).
- Continuous guards and phantom-gadget bounds: `work/lanes/PRECELL/` (`guards.py`, `joint_g.py`, `phantom.py`, `redit.py`).
- B/C resource synthesis by proxy-scored windowed LNS (Z-weighted CP-SAT start, `proxy.py` J = X2 + 1.1e-4·RZ +
  3e-5·acc1): `work/lanes/BFLAG/` (`synth_bc.py`, `lns3.py`, `pipe.sh`, `mkcand.py`); guard bound `sparse/idlebound.py`.
- A-region class table (prices any A-encoder change with v36c's surroundings fixed in microseconds): `work/lanes/AENC/`
  (`table_v36c.json`, `evalx.py`, `bmodel.py`); placement/timing CP-SAT model calibrated on v36c: `work/lanes/EARLY/layout.py`.
- Stationary 7-cell encoder library and end-state witnesses: ENDSTATE (git); prefix/round co-design with CP-SAT and
  exact-gradient retiming: ST1 (git, `redesign.py`, `gradient_retime.py`); B/C boundary cache: BCPOL (git).
