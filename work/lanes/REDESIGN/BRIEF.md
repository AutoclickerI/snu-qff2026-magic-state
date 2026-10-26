<task>
You are the REDESIGN lane (work/lanes/REDESIGN, PLAN P116; Jihoon's decision R-20261026-1) of our SNU QFF2026 entry:
fault-tolerant Steane |T_L> on a 6x6 grid, scored by conditional 1-F (lower is better) at acceptance >= 0.5 (we
require exact A >= 0.5002). Build, from scratch, a layout + prefix placement + ending around a final check cheaper than
the Steane round. Incumbent: work/lanes/MAIN/v37h, all orders 3.611954991494179e-5, A 0.5015489333258328.
A valid full circuit below 3.6019e-5 is a finalist; aim 3.2e-5 (-11%), stretch 2.9e-5.

Read AGENTS.md, docs/GOAL.md (Target), docs/CONSTRAINTS.md, docs/PLAN.md (Levers), docs/reference/circuit.md,
docs/reference/judge.md, docs/FINDINGS.md in full (Bounds, Square final round, Endings outside our terminal class,
Exhaustive search of block-transversal endings, C4-Steane contraction, Layout and geometry, Closed recipes), then
work/lanes/SQUARE/REPORT.md, work/lanes/WHOLEEND/REPORT.md and MODEL.md, work/lanes/ENDSEARCH/REPORT.md,
FRONTIER.md, tree37/PATH_REPORT.md and tree37/MODEL_LIMITS.md. Code to reuse (copy into your dir): SQUARE
(find_layout.py, layout_model.py, cp_prep.py, css_synth.py, build_suffix.py), WHOLEEND (build_whole.py),
ENDSEARCH (jit.py, grid_jit.py, build_grid.py, geometry.py), EARLY/layout.py, EXENC/exenc.py (exhaustive 11-13-CX
Steane encoders), MERGE (repair), evaluators per circuit.md (phantoms up to 40 qubits: ACCBUY/sparse40/).

What is known:
- Final check alone with perfect resources: square 2.5558e-5 (25.667 p^2), square + leaf 2.565e-5, path E-A-D-B-C
  2.709e-5, Steane round 2.871e-5 (ours 2.90e-5). On v37c's real prefix with perfect A/B/C arriving just in time:
  square 2.860e-5.
- Grid-free (all-to-all) full suffixes with real just-in-time preparation on v37b's prefix: square + leaf 3.3945e-5,
  path 3.4080e-5, square 3.4665e-5, against v37b's 3.7423e-5 (-9%); with 9-CX encoders square 3.4896e-5 vs standard
  4.0423e-5. The prize of a square-type ending is real off the grid.
- Every grid embedding so far failed on preparation geometry with a prefix laid out for the Steane round: same-index
  square coupling needs a unit square per index (routed R85-R94 best 8.93e-4); coupling C_i -> A_P(i) by a Steane
  automorphism P removes that but the blocks interleave; in-place preparation of interleaved blocks on reviewer 15's
  layout or a new P layout 2.55e-3 at A 0.19 (the projector and every nontrivial gauge completion have harmful single
  faults); three 7-cell factories on the prefix's 21 unused cells then 102-114 transport CX: 1.38e-4 at A 0.46; path
  grid builds 1.05e-3 (one A cell had a free neighbour), compiled path builds 5.33e-5, dominated by data waits.
- v37h: with only its last 3 ticks noisy 2.847e-5, so preparation and waits hold about 0.77e-5 and the final check
  about 0.57e-5. The floor for any circuit is 2.189e-5 (audited).
The lesson: the layout must be chosen jointly. The cultivation circuit itself is fixed (v37h's prefix; upstream
magic-state-cultivation), but its embedding on the grid and its timing may move; data end positions, every check
block's cells (non-interleaved, or interleaved with a preparation shown free of harmful single faults) and the times
cells are shared between the prefix and the blocks are all free.

Do:
1. Prize (first): grid-free full circuits on v37h's real prefix (not v37b's) for the square, square + leaf and path
   endings with real just-in-time preparation; pick the family to target by its price.
2. Layout: a joint CP-SAT model of cultivation placement (rigid pattern with its schedule, or its known re-embeddings),
   data hop paths, block cells with fault-tolerant preparation templates (harmful-single-fault check as a constraint),
   cell time-sharing, and adjacency for every coupling (Steane automorphisms allowed). Objective: release times and
   data waits. Return a witness or an infeasibility certificate per family.
3. Build the best witness as a full circuit, price it by all orders, repair it with MERGE's tools.
Checkpoints: 2026-10-27 12:00 KST, step 1 prices and a witness or certificate for the best family; 2026-10-28 18:00
KST, a priced grid build; if none is below 3.6e-5 by then, stop with the measured obstacle. The final stem must be set
by 2026-10-30 10:20 KST, so finalists go to cand/ at once with judge gates_ok at 1e6 and their judge time next to
v37h's (same host, same minutes, 1 process). Keep REPORT.md (<= 100 lines, each < 2,000 characters) and results.json
current.
</task>

<tools>
- Exact all-orders price (needs barriers over all used qubits, no FRAME/POSTSELECT):
  cd work/lanes/MAIN/sparse; OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 ../../../../.venv/bin/python
  sparse_walsh.py <path/stem without suffix> 72 canonical 16   (about 1 s at 16 processes; prints JSON with loss, acceptance).
  Many single-process prices in parallel: work/lanes/BUNDLE/ev.py (price_stem) and menu.py (edit menu, apply_bundle).
- Region counterfactuals: work/lanes/MAIN/sparse/region.py (spec format in circuit.md).
- Judge check at 1e6 shots: work/fast_check.py; its gates_ok is the verdict (format, class, correctness); acceptance
  below 1e8 shots is a binomial estimate, the criterion is exact all-orders A >= 0.5002.
- Polishing a new circuit: BUNDLE's greedy joint extension (the main session's v36i -> v36k: 35 edits, -1.9e-7),
  INTEG2 echo/pair/guard passes, ACCBUY buyers (acceptance costs about 1.6e-5 loss per unit; cheap sources: echo
  deletions, trades). Compare a new family only after the same polish the incumbent got.
- Python is /home/jihoon/competitions/quantumn/.venv/bin/python.
</tools>

<selection_rules>
Select finalists by the lowest exact L at exact A >= 0.5002; J_tau = A*(L - tau) is only a search heuristic, with tau =
the current incumbent's L (a stale tau trades loss for acceptance). Keep the (L, A) Pareto front for acceptance buys.
Before ranking a build that changes the outputs or the tail, check raw correctness (six noiseless output stabilizers
+1): the all-orders price checks only the decoded loss. Name stem files by QASM plus ordered data_qubits.
</selection_rules>

<default_follow_through_policy>
Do not stop to ask questions: the owner is not available to the lane. Decide, record the decision and its reason in
REPORT.md, and continue. A finalist does not end the lane; keep improving until the completeness contract is met.
</default_follow_through_policy>

<verification_loop>
Reproduce the incumbent v37h first (work/lanes/MAIN/v37h: 3.611954991494179e-5, 0.5015489333258328). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<action_safety>
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q -o ControlMaster=no -o
  ControlPath=none <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- Hosts: jerry <= 24 processes in total (other users also load jerry: keep the host total load <= 64), zebra <= 2 light work. Write no large files; prune caches you create.
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>
