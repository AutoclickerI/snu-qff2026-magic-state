<task>
You run research lane AJOINT of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/AJOINT. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, docs/FINDINGS.md,
work/lanes/DIGEST/DIGEST.md (item 2), work/lanes/{AENC,FLAG,APROC,GUARDNET,EXENC}/REPORT.md.

Goal: a circuit with exact all-orders loss L < tau - 3e-7, tau = L(v36k) = 3.789826092701952e-5, acceptance
A >= 0.5002, judge-valid, obtained by optimizing the A encoder, the data guards next to it and A's partial decoder as
one process across their present module boundaries (the q14/q16 guard slots and neighbours), allowing transient encoded
flags: a borrowed encoded wire carries an error trace that a later deterministic parity reads. Rank by
J_tau = A*(L - tau). Incumbent: work/lanes/MAIN/v36k.{qasm,json} (v36i + 35 local edits, listed in the json "source").

Why: on v36h, A cells 33-42 noiseless are worth -1.64e-6 and data waits 28-42 -3.88e-6 (counterfactuals, overlapping,
not additive). AENC's exact optimum holds only on v36c's A-only boundary; FLAG's two-gap theorem fixes the flagged
round's roles, depth and couplings; APROC re-synthesized A's process on v36h (v36i, -6.3e-8); GUARDNET found the guard
network at a local optimum given the A process. Nobody optimized encoder, guards and decoder jointly. Sources: reviewer
11 Task 5 (work/lanes/MAIN/spec/reviewer11/TASKS.json; it needs an exterior table built on the incumbent, AENC's is
v36c's), reviewer 12 #6 (spec/reviewer12/TASKS.json), reviewer 7 M06 transient flags on encoded resource wires (git
show b2a5243:work/lanes/MAIN/spec/reviewer7/...).

Approach, in order:
1. Reproduce v36k's A process (encoder, guards near A, partial decoder, flag) behind a boundary of inputs, outputs and
   records sufficient to price any replacement inside it exactly; round-trip the incumbent through that boundary.
2. Synthesize one 4-6-wire cross-boundary witness (CP-SAT or enumeration; first-order fault tolerance, deterministic
   detectors), including transient encoded flags; price each candidate in the full circuit with every removed guard and
   new idle.
3. Grow the window (more wires and ticks, guard slots on q14/q16 and neighbours) while it pays; polish and buy
   acceptance back as needed.
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
Reproduce v36k first (3.789826092701952e-5, 0.5010395982258441). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<completeness_contract>
Stop when steps 1-3 are built and priced up to the window size where the boundary model no longer fits, and either a
finalist exists that further growth or polish no longer improves, or the best is >= tau; then name the cost that ate
the gain (encoder, guard, decoder, acceptance) with measured numbers.
</completeness_contract>

<action_safety>
- Hosts: hippo <= 24 processes in total, zebra (local) <= 4. Never use owl, tom, jerry, sunfish, faraday, dragon,
  Parrot or any GPU.
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q -o ControlMaster=no -o
  ControlPath=none <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
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
