<task>
You run research lane POLISH of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/POLISH. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, docs/FINDINGS.md (rows on
BUNDLE, GUARDNET, APROC, ACCBUY, INTEG2 and "Room next to the data on the real grid"), work/lanes/{BUNDLE,GUARDNET,
APROC}/REPORT.md, work/lanes/GLOBAL/REPORT.md.

Goal: the lowest exact all-orders loss L at acceptance A >= 0.5002, judge-valid, by local edits on the new incumbent
v37a (work/lanes/MAIN/v37a.{qasm,json}: GLOBAL's R46 layout, data qubits [6,20,19,10,2,22,16], 390 CX, 49 ticks;
tau = L(v37a) = 3.761821654835085e-5, A(v37a) = 0.5007854638217537). Finalist: L < tau - 5e-8. Rank by
J_tau = A*(L - tau) with the A floor enforced.

Why: v37a got GLOBAL's repairs but not the local polish that took v36h to v36k. On v36h each connected 2-edit bundle
gained <= 3e-8, yet a greedy joint extension compounded them: v36i -> v36k -1.93e-7 in 35 edits (each round prices
every valid addition of a positive single or pair onto the current set, keeps the best at A >= 0.5002, funds acceptance
with cheap singles; reference script greedy_ref.py in your dir, written for v36i). GUARDNET's joint guard-network
re-synthesis and APROC's A-process witness each found further small gains on that layout.

Approach, in order:
1. Port BUNDLE's edit menu (work/lanes/BUNDLE/menu.py, elements.py, gadgets.py, lib.py, ev.py: CX insertions and
   removals, guard pairs, shifts, echoes, trades over the P1/P2/P4 neighbourhoods) to v37a. Its data qubits are
   hard-coded for v36h (lib.D = [0,20,7,10,3,22,21]): take them from v37a.json. Price all singles.
2. Enumerate connected 2-edit bundles over the positive and acceptance-cheap singles (BUNDLE's b2 procedure), then run
   the greedy joint extension to convergence (a round gaining < 1e-9 over all valid candidates ends it).
3. On the polished circuit run GUARDNET's guard-network re-synthesis and APROC's A-side pass, then one more greedy
   round. Put each finalist in cand/ as soon as it is verified, so the main session can race it.
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
Reproduce v37a first (3.761821654835085e-5, 0.5007854638217537). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<completeness_contract>
Stop when steps 1-3 are done and a final greedy round gains < 1e-9; report the gain per stage with measured numbers.
</completeness_contract>

<action_safety>
- Hosts: zebra (local) <= 16 processes in total. Never use owl, tom, jerry, hippo, sunfish, faraday, dragon,
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
