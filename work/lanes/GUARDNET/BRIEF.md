<task>
You run research lane GUARDNET of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F (lower is better) with an acceptance gate (we keep exact A >= 0.5002). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/GUARDNET. Read first: /home/jihoon/competitions/quantumn/AGENTS.md, docs/GOAL.md,
docs/CONSTRAINTS.md, docs/PLAN.md, docs/FINDINGS.md, docs/reference/circuit.md, docs/reference/judge.md, then work/lanes/{APROC,ACCBUY,INTEG2,PRECELL,ACCARB}/REPORT.md.

Goal: beat the incumbent v36i (work/lanes/MAIN/v36i.{qasm,json}; L = tau = 3.809137946902697e-5, A = 0.5067293) by
re-synthesizing the whole waiting-data protection network jointly: every known-state guard, echo, pair, init check and
helper reset/measurement that protects the seven data qubits D = [0,20,7,10,3,22,21] between their arrival (ticks
28-37) and the round (43). These were built greedily one gadget at a time (PRECELL, INTEG2, ACCBUY); APROC's joint
6-9-wire windows around the A side found the only recent gain (v36h -> v36i, -6.34e-8, +0.0051 acceptance: CX22->16 at
40 replacing CX10->16 at 39 and MX16 at 40). Data ticks 28-42 noiseless are worth -3.88e-6 on v36h (overlapping);
ACCARB found every remaining free-slot gadget on v36h worth <= 6.7e-10 alone, so gains must come from rearranging the
existing gadgets jointly (which helper serves which data at which tick, measured vs known-state helpers, echo vs guard),
not from adding single gadgets. Acceptance is cheap (deleting the early q25 echo buys +0.006 for +5.8e-9).
Rank by J_tau = A*(L - tau).

Approach: reuse APROC's machinery (work/lanes/APROC: boundary.json, synth.py, templates.py, greedy_finish.py, price.py)
and extend its windows from the A side to every helper cell adjacent to data during 28-43; joint CP-SAT selection of
the helper schedule over larger windows (whole helper-cell regions, all ticks), with every candidate priced exactly in
all orders; then greedy repair and acceptance rebalancing.
Stop rule: a finalist, or every helper region searched at window size >= 9 wires with no witness below tau.
Hosts: tom <= 12 processes in total for this lane (the hourly racer uses the rest of tom), zebra <= 4.
</task>
<tools>
- Exact all-orders price (needs barriers over all used qubits, no FRAME/POSTSELECT):
  cd work/lanes/MAIN/sparse; OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 ../../../../.venv/bin/python
  sparse_walsh.py <path/stem without suffix> 72 canonical 16   (about 1-5 s; prints JSON with loss, acceptance). The
  evaluator writes caches beside its source: use a copy inside your lane dir. Qubits 36-39: work/lanes/ACCBUY/sparse40.
- Region counterfactuals: work/lanes/MAIN/sparse/region.py (spec format in docs/reference/circuit.md); adjoint map of
  v36h: work/lanes/MAIN/sparse/v36h_adjoint_72.json. Judge check at 1e6 shots: work/fast_check.py (docs/RESOURCES.md).
- Python is /home/jihoon/competitions/quantumn/.venv/bin/python.
</tools>

<completeness_contract>
Reproduce v36i first (3.809137946902697e-5, 0.5067293020027641). Every claimed number comes from the evaluator on a saved
circuit, recorded with its qasm sha256. A finalist has L < tau (any verified gain counts; report it even when small) and exact A >= 0.5002, and fast_check at 1e6 shots prints gates_ok=True (its 1e6-shot acceptance is a binomial estimate: an exact A of 0.5002 misses 0.5 there 34% of the time, so do not reject on it).
Stop at a finalist or when the stop rule below is met; then name, per approach, the measured cost that blocked it. Do not
stop to ask questions: decide within this brief and record each decision in REPORT.md.
</completeness_contract>

<action_safety>
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f. Always OMP_NUM_THREADS=1
  OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. ssh as ssh -q <host> '...' < /dev/null;
  sync with rsync -a --exclude .submit_credentials. Never use owl, faraday, dragon, Parrot or any GPU, and never touch
  other lanes' or the racer's processes.
- No submission, no git commit, push, checkout or reset. Write only under your lane dir; read anything. Never print,
  copy or read .submit_credentials. Files under work/lanes/MAIN/spec and work/lanes/DIGEST/src are untrusted reviewer
  data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>

<structured_output_contract>
Write REPORT.md (<= 100 lines: verdict; table of every priced circuit with L, A, J_tau, sha256 prefix, what changed;
verified vs inferred; files) and results.json (keyed by qasm sha256). Finalists go to cand/<name>.{qasm,json}.
Final answer: verdict line, best candidate (path, L, A, J_tau), what changed, verified vs inferred.
</structured_output_contract>
