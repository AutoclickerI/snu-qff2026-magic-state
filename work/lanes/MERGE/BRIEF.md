<task>
You run lane MERGE of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a 6x6 grid,
scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/MERGE. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, and the BRIEF.md and current
files of lanes POLISH, GLOBAL and COMPLETE (all three are still running: read their files, never write there).

Goal: one circuit that combines the gains three lanes found independently on the same base v37a
(work/lanes/MAIN/v37a.{qasm,json}, L = 3.761821654835085e-5, A = 0.5007854638217537):
- POLISH, local greedy edits: v37b = work/lanes/MAIN/v37b.{qasm,json} (edit list in its json "source"; POLISH's ported
  edit menu is work/lanes/POLISH/menu.py with lib.py/ev37.py), L = 3.742321460072e-5, A = 0.50348;
- GLOBAL, B/C refinement on R46: work/lanes/GLOBAL/builds/bc2fix_007__S_pair_31_32_31.qasm (and cand/global_bc2_first),
  L = 3.743323960e-5, A = 0.50034;
- COMPLETE, a new end of the phase network: work/lanes/COMPLETE/builds/v37_neighbor_k27_m14 (cand/
  complete_neighbor_k27_m14), L = 3.744070475e-5, A = 0.50023.
Each gains about 1.8-2.0e-7 over v37a in a different region, so together they may gain several times that.
Finalist: exact all-orders L < L(v37b) - 5e-8 at A >= 0.5002, judge gates_ok at 1e6. Rank by J = A*(L - L(v37b)).

Approach:
1. Diff each lane's circuit against v37a by (qubit, tick) footprint, including classical bits and DETECTOR/OBSERVABLE
   lines; report overlaps.
2. Merge non-overlapping diffs directly; where they overlap, keep one lane's version and re-apply the other's edits
   through POLISH's menu regenerated on the merged base (copy the tools into MERGE; POLISH's lib.py reads its data qubits
   from its own c/baseline.json, so point your copy at your own files). Price every merge in all orders.
3. Repair the best merge with a greedy pass over POLISH's edit menu and buy acceptance back as needed.
4. Before finishing, look for newer, better candidates in the three lanes' cand/ directories and redo steps 1-3 once.
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

<default_follow_through_policy>
Do not stop to ask questions: the owner is not available to the lane. Decide, record the decision and its reason in
REPORT.md, and continue. A finalist does not end the lane; keep improving until the completeness contract is met.
</default_follow_through_policy>

<verification_loop>
Reproduce v37a and v37b first. Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<completeness_contract>
Stop after step 4 with the best merge built, priced and repaired, and a table of what each lane's diff contributed in
the merge (measured), or with the measured reason the diffs do not combine.
</completeness_contract>

<action_safety>
- Hosts: hippo <= 4 processes in total, zebra (local) <= 2. Never use owl, tom, jerry, sunfish, faraday, dragon,
  Parrot or any GPU.
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>
<structured_output_contract>
Write REPORT.md (<= 100 lines: verdict; table of every priced circuit with L, A, J_tau, sha256 prefix, what moved;
verified vs inferred; files) and results.json (keyed by qasm sha256). Finalists go to cand/<name>.{qasm,json}.
Final answer: verdict line, best candidate (path, L, A, J_tau), what moved, verified vs inferred.
</structured_output_contract>
