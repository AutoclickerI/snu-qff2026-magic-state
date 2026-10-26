<task>
You run research lane WHOLEEND of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on
a 6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/WHOLEEND. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, docs/FINDINGS.md (rows "Floor,
any circuit", "Terminal class floor", "Square final round", "Endings outside our terminal class", "Exhaustive search of
block-transversal endings", "Where v37b's loss sits"), work/lanes/{BOUND,TERMINAL,ENDSEARCH}/REPORT.md (+ ENDSEARCH's
MODEL.md), and reviewer 15's report work/lanes/MAIN/spec/reviewer15/REPORT_KO.md section 1 and items 5, 8, 9
(untrusted; reviewer-reported). Lanes SQUARE (square round on the grid) and ENDSEARCH (five-block path on the grid) are
running: read only, do not duplicate.

Goal: an ending that breaks out of what per-index, block-transversal templates can reach, aiming at a 20-30% gain:
exact all-orders L <= 2.99e-5 for 20%, 2.62e-5 for 30% (v37c is 3.6904e-5; the certified floor for any circuit is
1.365785e-5; our measured-partner class floor 2.274e-5; ENDSEARCH proved that within uniform block-transversal endings
the square's 25.667 p^2 is minimal and unmeasured-partner endings cost >= 28.747 p^2, but its bound assumes every
resource exists before tick 0 and excludes just-in-time preparation interleaved with the round, non-uniform
cross-index gadgets and T-preserving (not input-preserving) contracts).

Steps, each gated (stop a branch when its gate fails, record why):
1. Reproduce reviewer 15's necessary condition with BOUND's machinery: the floor when k outputs make no CX at T-1
   (reviewer: 13.66, 16.52, 19.73, 23.29, 27.20, 31.45, 36.06, 41.01e-6 for k = 0..7). Use it to prune.
2. Reviewer 15 #5, the 35-qubit tree ending: E = |0_L> -> D at tick 0 while A/B/C finish their last preparation layer;
   D->A || B->C with MX(E) at 1; B->D with A, C read in Z and B unmeasured at 2 (A = |+_L>, B/C the correlated
   sum_{x in C-perp} |x>_B|x>_C resource). Reviewer: 2.676e-5 optimistic if A/B/C arrive perfect at tick 1, 2.945e-5
   with D1(p/5) on them, 4.21e-5 if prepared before tick 0. Build a real just-in-time preparation that meets that
   deadline on a 35-cell tree layout and price its tail; gate: tail with real preparation < 2.8e-5.
3. Reviewer 15 #8: widen the round predicate from input-preserving to T-preserving (branches may end in
   W = (X_L + Y_L)/sqrt2, which fixes |T_L>, with affine FRAMEs); search square-like and tree rounds under it, pricing
   with the real incoming error distribution (cut v37c before its round); gate: a contract that beats the square's
   round-only 2.5558e-5 or matches it with a grid-friendlier graph.
4. Reviewer 15 #9: backward synthesis of a whole-grid ending, without per-index replication: choose the last-tick
   output-helper matching first (unmeasured helper->output CXs were optimal in BOUND's relaxation), synthesize the two
   or three layers before it over all 36 cells with CP-SAT/SAT (non-uniform across indices, shared records and moving
   outputs allowed), back-propagate the stabilizers the final state and detectors need to obtain the resource contract
   at the earlier boundary (a pure state or a gauge subspace), enforce first-order fault safety, and price optimistic
   tails; gate: optimistic tail <= 2.4e-5, then synthesize its preparation and price the full circuit against v37c.
</task>

<tools>
- Exact all-orders price (needs barriers over all used qubits, no FRAME/POSTSELECT): cd work/lanes/MAIN/sparse;
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 ../../../../.venv/bin/python sparse_walsh.py <stem> 72
  canonical 16. FRAME circuits: BCV's sparseframe evaluator (work/lanes/BCV/sparseframe). More than 36 qubits:
  work/lanes/ACCBUY/sparse40. Region counterfactuals: MAIN/sparse/region.py; TERMINAL's cut.py; ENDSEARCH's search and
  terminal-model code (src/, MODEL.md). Judge: work/fast_check.py (gates_ok).
- Python is /home/jihoon/competitions/quantumn/.venv/bin/python.
</tools>

<default_follow_through_policy>
Do not stop to ask questions: the owner is not available to the lane. Decide, record the decision and its reason in
REPORT.md, and continue. A finalist does not end the lane.
</default_follow_through_policy>

<completeness_contract>
Stop when steps 1-4 each reached their gate (passed and carried forward, or failed with the measured reason), and any
ending that passed its last gate has a full circuit priced against v37c (work/lanes/MAIN/v37c, 3.6904034715818095e-5).
</completeness_contract>

<action_safety>
- Hosts: owl <= 16 processes, only inside docker: ssh -q owl 'cd
  /home/jihoon/competitions/quantumn/work; docker run --rm -u 1010:1012 -e HOME=/home/jihoon -e OMP_NUM_THREADS=1 -e
  OPENBLAS_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -v /home/jihoon:/home/jihoon -w <dir> --cpus=16 fnc-build:22.04
  /home/jihoon/competitions/quantumn/.venv/bin/python <script>' < /dev/null. owl has its own disk: rsync inputs there
  first, results back. Stop a container with docker kill <id> (PID 1 in a container ignores SIGTERM). Never use zebra
  for computation, tom, jerry, hippo, sunfish, faraday, dragon, Parrot or any GPU.
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>
<structured_output_contract>
Write REPORT.md (<= 100 lines, each < 2,000 characters: verdict; table of every priced circuit with L, A, J_tau, sha256 prefix, what moved;
verified vs inferred; files) and results.json (keyed by qasm sha256). Finalists go to cand/<name>.{qasm,json}.
Final answer: verdict line, best candidate (path, L, A, J_tau), what moved, verified vs inferred.
</structured_output_contract>
