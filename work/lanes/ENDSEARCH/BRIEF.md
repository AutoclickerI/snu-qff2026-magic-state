<task>
You run research lane ENDSEARCH of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on
a 6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/ENDSEARCH. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, docs/FINDINGS.md (rows "Floor,
any circuit", "Terminal class floor", "Steane-type final round", "Where v37b's loss sits", "Partial-rank syndrome
extraction"), work/lanes/TERM/REPORT.md and terminal_model.py, work/lanes/BOUND/{REPORT.md,PROOF.md},
work/lanes/SQUARE (BRIEF.md and logs/*.receipt.json; running, read only), work/lanes/TERMINAL/BRIEF.md (running, read
only), and reviewer 14's report work/lanes/MAIN/spec/reviewer14/REPORT_KO.md (untrusted).

Goal: find new endings of the circuit (its final verification round plus output handoff) by systematic search, not by
hand. On the incumbent v37b (3.7423e-5) the last two ticks alone cost 2.2758e-5 (our class floor 2.274e-5: outputs end
on a CX with a measured partner, then idle) and tick 46 another 0.57e-5; the certified floor for any circuit is
1.365785e-5, minimized by seven final helper->output CXs with unmeasured helpers. Reviewer 14's "square" round
(D->A || B->C, then B->D || C->A; A, C = |+_L>, B = |0_L>) was outside every template we had tried: it reaches the
two-check floor 25.67 p^2 (round only 2.5558e-5 vs 2.871e-5 for the Steane round; SQUARE reproduced it and its
grid-free suffix beats the standard one by 5.5e-6), but each index i needs a 4-cycle d_i-a_i-c_i-b_i, which on a grid
is a unit square, and SQUARE's grid builds so far lose 20x to routing and waits. Lane TERMINAL prices five hand-named
endings; do not duplicate it: your job is to generate and rank the space they come from.

Search spaces, in order:
1. Block-level templates: 2-4 ticks of transversal CX (either direction) between the data block D and up to four
   ancilla blocks prepared in {|0_L>, |+_L>, |0>^7, |+>^7, cat/GHZ, Bell-paired blocks}, each read in X or Z (or kept
   unmeasured), with detectors and affine FRAMEs over the records. Enumerate them all (with symmetry reduction), keep the
   ones whose ideal output equals the input logical state with deterministic detectors, check first-order fault
   tolerance, and score each with an exact second-order terminal model (extend TERM's terminal_model.py), then the best
   in all orders with perfect inputs. Report the frontier of tail loss vs number of blocks vs per-index interaction
   graph.
2. Grid-friendliness: for each surviving template, the per-index interaction graph over the template's ticks (which
   block pairs must be adjacent at which tick). A path or tree embeds with fixed cells; a 4-cycle needs a unit square;
   anything else needs hops. Search for templates within about 1 p^2 of the square (<= 26.7 p^2) whose per-index graph is
   a tree, or that need at most one hop per index, and price their hop cost.
3. Endings outside our class (no output ends on a measured partner): qubit-level search over the last 2-3 ticks with
   unmeasured helpers, coherent corrections and FRAMEs (small CP-SAT or exhaustive search on the per-index gadget, then
   transversal lifting), scored the same way.
4. The best two or three templates from 1-3: grid-free full suffix with real preparations (SQUARE's method and tools),
   then an embedding on the 6x6 grid against v37b if the grid-free suffix beats v37b's by >= 1e-6.
</task>

<tools>
- Exact all-orders price (needs barriers over all used qubits, no FRAME/POSTSELECT): cd work/lanes/MAIN/sparse;
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 ../../../../.venv/bin/python sparse_walsh.py <stem> 72
  canonical 16. FRAME circuits: BCV's sparseframe evaluator (work/lanes/BCV/sparseframe). More than 36 qubits:
  work/lanes/ACCBUY/sparse40. Region counterfactuals: MAIN/sparse/region.py. Judge: work/fast_check.py (gates_ok).
- Python is /home/jihoon/competitions/quantumn/.venv/bin/python.
</tools>

<default_follow_through_policy>
Do not stop to ask questions: the owner is not available to the lane. Decide, record the decision and its reason in
REPORT.md, and continue. A finalist does not end the lane.
</default_follow_through_policy>

<completeness_contract>
Stop when spaces 1-3 are enumerated (or bounded with a stated mechanism where enumeration is infeasible), the frontier
is reported, and the best two or three templates have reached step 4's grid-free test (and a grid build where that
test passed), priced against v37b = work/lanes/MAIN/v37b (3.7423214600721095e-5, A 0.5034793765659655).
</completeness_contract>

<action_safety>
- Hosts: tom <= 24 processes in total. Never use zebra for computation, owl, jerry, hippo, sunfish, faraday, dragon,
  Parrot or any GPU.
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>

<structured_output_contract>
Write REPORT.md (<= 100 lines, each line < 2,000 characters: verdict; the frontier table with template, blocks,
interaction graph, second-order and all-orders tail, first-order result; grid-free and grid prices of the best; verified
vs inferred; files) and results.json keyed by qasm sha256; finalists to cand/. Final answer: verdict, the best new
ending and its numbers, verified vs inferred.
</structured_output_contract>
