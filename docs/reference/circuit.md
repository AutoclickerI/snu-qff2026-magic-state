# Our circuit and its search tools
Serves: G1, G2. Read before changing the circuit, its layout or the search code.

## Structure
1. **Injection** and **double-cat check**: Gidney's d=3 cultivation stages, ported from
   `upstream/magic-state-cultivation` by `work/cultiv_port.py` (`make_chunk_d3_init_unitary`,
   `make_chunk_d3_double_cat_check`, T gates swapped in with `s_to="Tswap"`).
2. **Final superdense cycle**: one Bell pair per plaquette, at (1,0)-(2,0), (1,2)-(2,2) and (3,1)-(4,1).
   Each pair measures both X and Z stabilizers of its plaquette, then unbells and is measured.
   Post-unbell single CNOTs are hook-safe and allowed.
3. **Extras**: X-only cat members attached to a Bell parent that do one data CNOT and an MX. An extra
   must be a common neighbour of a parent and a data qubit, so plaquette 0 can have none.
4. **A1 layout**: d1 moves (2,3)→(1,3) by a 2-CNOT hop; (2,3) becomes d1's X extra (parent (2,2)), and
   (4,2) serves d5 (parent (4,1)). Data in several plaquettes cannot move.
5. **ALAP pre-cycle**: stages 1–2 are rescheduled as late as possible with commuting gates reordered
   (`alap.py`, greedy priority seed s). Commuting variants raise acceptance to ~0.68.

## Code map (`work/`)
- `qcirc.py`: QASM builder (`Circ`), `rescheduled(lazy_init=True)` emits a fixed layer schedule.
- `lanes/EVAL/exact2.py <qasm> [--top N] [--json f] [--third]`: exact score of a whole submission, no sampling (faults as bit signatures through the T-rotation frame, 2nd order in 2 s, 3rd order in ~30 s); loss by fault pair and per-channel sensitivity. Matches v12's 12-seed MC mean to −0.08% at 3rd order; below acceptance ~0.5 the series converges slowly (st_L2_v0: −6% at 3rd order), so rank such circuits with MC.
- `proxy2.py`: exact second-order loss of the cycle alone via Stim DEM; `joint_loss` prices Y_L at ½.
- `gen2_cycle.py`: v6-era cycle model and annealer (gen2 json format). `batch_score.make(spec)` builds
  full circuits from gen2 files.
- `lanes/me_layout/gmodel.py`: generalized cycle with moves, Bell pairs and extras (`GModel`), with
  `feasible`, `emit`, `proxy`, `full_circuit`, `anneal`. `run_moves.py` has the v6/A1/A2/A3 variants
  and the `BASE=` seeding mode. `alap.py`, `alap_seeds.py`, `alap_gen2.py` and `mseed.py` score.
- `bounds.py`, `decompose.py`, `idle_decomp.py`: floors and loss splits.
- `lanes/DR/`, the Steane-type round: `steane.py` (grid-free exact proxy), `steane_layout.py` and
  `steane_layout2.py` (layouts), `synth.py`, `synth_joint.py`, `synth_blocks.py`, `synth_l5.py` (block CNOT
  synthesis; `synth.dangerous_z` is the danger metric), `steane_full.py` (full-circuit assembler), `merge.py`
  (integration, PLAN P16), `regions.py` (noise by region); direct-readout rounds: `relaxed.py`, `poc.py`,
  `flagsched.py`.
- `lanes/L1_cpsat_schedule/`: CP-SAT with an exact closed-form objective (`cpsat.py`,
  `ordered_objective.py`, `validity.py`).

## Validity
A cycle schedule is valid if a noiseless Stim run reports every stabilizer and preserves both logical
bases (`cycle_interleave.stim_cycle`). Parity rules (even count of X-before-Z on shared data, within
and across tiles) give no false negatives but 2–4% false positives, so Stim stays the oracle.
