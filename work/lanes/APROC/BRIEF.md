<task>
You run research lane APROC of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F (lower is better). Working dir: /home/jihoon/competitions/quantumn/work/lanes/APROC.
Read first: /home/jihoon/competitions/quantumn/AGENTS.md, docs/GOAL.md, docs/CONSTRAINTS.md, docs/PLAN.md,
docs/reference/circuit.md, docs/reference/judge.md, then work/lanes/DIGEST/DIGEST.md (priority 2 and rows C07, C09,
C17, C18, C47, C74) and work/lanes/{AENC,EXENC,FLAG,ACCBUY,R43}/REPORT.md.

Goal: beat the incumbent v36h (work/lanes/MAIN/v36h.{qasm,json}; L = tau = 3.815473322483099e-5, A = 0.5016415) by
optimizing the A side as one process instead of three fixed modules: the 12-CX A encoder at ticks 37-43 (cells
A = [1,14,8,9,2,16,15]), the known-state data guards around it (q14/q16 guard slots and the others in v36h), and the A
partial decoder flag (CX9->15 at 44, CX8->9 at 45, MX8 at 46), including transient encoded flags: a borrowed encoded
wire that carries an error trace a later deterministic parity reads (reviewer 7 M06, reviewer 11 Task 5, reviewer 12
#6). Rank by J_tau = A*(L - tau).

Known numbers: A cells 33-42 noiseless on v36h -1.64e-6; data waits 28-42 noiseless -3.88e-6 (overlapping); the two
A-flag gap idles (q10, q21 at 44) noiseless -2.664e-6, off-grid helpers there -1.609e-6 (FLAG, R43); AENC's exact A
optimum was computed on v36c's A-only boundary (headroom 1.982e-6 there) and FLAG's two-gap theorem fixes roles, depth
and couplings, so neither settles a joint process. Lane GLOBAL (work/lanes/GLOBAL) is building on-grid helpers and late
checks with v36h's roles; do not duplicate it, and reuse its outputs if they help.

Approach, in order:
1. Reproduce v36h's A process with a sufficient boundary: inputs (cell releases, data state), outputs (A state, records,
   guards' effect on data) and the record set, so that any replacement inside the window prices exactly.
2. Synthesize cross-boundary witnesses on 4-6 wires in one window at a time (CP-SAT or exact enumeration, EXENC's
   exact.cpp style): encoder, guard and decoder gates chosen jointly, transient flags allowed, every removed guard and new
   idle priced. Keep a Pareto archive over (first-order danger to data, acceptance, idle exposure).
3. Price the best witnesses in all orders, repair with ACCBUY/INTEG2 greedy passes, buy acceptance back if needed.
Stop rule: a finalist, or every window around the A process (encoder, guards, decoder) searched with no witness below tau.
Hosts: tom <= 12 processes in total for this lane from 16:40 KST (the hourly racer uses the rest of tom), zebra <= 4
(before 16:40 only zebra).
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
Reproduce v36h first (3.815473322483099e-5, 0.5016415049479505). Every claimed number comes from the evaluator on a saved
circuit, recorded with its qasm sha256. A finalist has L < tau - 3e-7, A >= 0.5002 and passes fast_check at 1e6 shots.
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
