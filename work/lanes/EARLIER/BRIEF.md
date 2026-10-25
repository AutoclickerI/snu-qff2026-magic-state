<task>
You run research lane EARLIER of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/EARLIER. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, docs/FINDINGS.md (rows "Waiting
exposure, not hop CX, is the data cost", "Placement (EARLY's CP-SAT model)", "A different end of the phase network",
"Where v37b's loss sits", "Prefix checks"), and work/lanes/COMPLETE/REPORT.md with its tools (closed lane: read and
copy, never write there).

Goal: the incumbent v37e (work/lanes/MAIN/v37e.{qasm,json}, 3.637095528032376e-5, A 0.5024263760643374, 406 CX, 48
ticks, round R45 on GLOBAL's R46 layout, data [6,20,19,10,2,22,16]) with its round one native tick earlier (R44), or
any other shortening of the data's pre-round wait. Measured value: each tick of every pre-round data wait shortened was
worth -0.684e-6 on v36h (R43 lane); an inserted tick costs +2.6e-6. COMPLETE reached R45 on v37a by reversing the blue
check's last CX with its readout ports exchanged, reusing a measured-Z state for a data hop and direct Z-read handoffs
on q3/q7/q13, then restoring three guards; dropping three source checks for an earlier round cost +6.30e-6. It left
open larger completion windows and other output geometries. Find what fixes the round tick on v37e (the critical path
through prefix release, data hops, A/B/C readiness and the A partial decoder) with an exact schedule/critical-path
analysis first, then attack it: wider phase-network completion windows, re-routed data hops or a different output
placement (the outputs may move by one cell if the round contacts survive), A/B/C preparation moved or shortened
where it binds, guards restored afterwards. Price every full circuit exactly, repair with work/lanes/MERGE's menu
(copy its tools) and buy acceptance back. Finalist: L < L(v37e) - 1e-7 at exact A >= 0.5002, judge gates_ok at 1e6,
judge speed within 1.5x of v37e's (time fast_check at 1e6 with 1 process against v37e on the same host).
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
Reproduce v37e first (3.637095528032376e-5, 0.5024263760643374). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<completeness_contract>
Stop when the critical path to the round is mapped and every attack on it is built and priced, and either a finalist
exists that further repair no longer improves, or the best is >= L(v37e); name what fixes the round tick, with the
measured cost of each attempt to move it.
</completeness_contract>

<action_safety>
- Hosts: sunfish <= 20 processes in total, but only from 02:22 KST 2026-10-26 (the hourly racer holds sunfish until
  02:20 and then re-sizes around you; check the clock with date), zebra <= 6 at any time. Never use owl, tom, jerry, hippo, faraday, dragon, Parrot
  or any GPU.
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q -o ControlMaster=no -o
  ControlPath=none <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
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
