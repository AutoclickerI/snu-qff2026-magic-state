<task>
You run research lane ACCARB of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F (lower is better) with a hard acceptance gate A >= 0.5 (we keep exact A >= 0.5002).
Working dir: /home/jihoon/competitions/quantumn/work/lanes/ACCARB. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/PLAN.md, docs/reference/circuit.md, docs/reference/judge.md, then
work/lanes/{ACCBUY,IFACE,EARLY,INTEG2,PCC}/REPORT.md and work/lanes/MAIN/spec/reviewer13/REPORT_KO.md section 5.

Goal: beat the incumbent v36h (work/lanes/MAIN/v36h.{qasm,json}; L = tau = 3.815473322483099e-5, A = 0.5016415) by
acceptance arbitrage on the real grid: buy acceptance where it is cheap and spend it on protections whose only blocker
was the acceptance gate. Rank by J_tau = A*(L - tau).

Acceptance sources (measured unless marked):
- IFACE (work/lanes/IFACE/results.json, builds/): if_d (delete CX10->4 at 34, prefix retimed) L 3.825307e-5 (+9.83e-8),
  A 0.508576 (+0.00693): about 1.4e-5 loss per unit of acceptance; if_hde +0.00602 A for +1.00e-7; del_echo14
  (delete CX13->14 at 32) +6.9e-10 L, -0.00036 A; and the other if_* rows.
- Reviewer 13's R6 (reviewer-reported, rebuild and verify from section 5): C resource R_V with V = span{e1+e2}
  (cells 25, 19), q12 R -> RX at tick 38, the two C-copy CX replaced by CX25->19 at 45, MX25 and MZ19 at 46, helper
  18/31 copy actions removed: 3.8339504321e-5, A 0.504023485849, 326 CX (+1.85e-7 L, +0.00238 A); with the off-grid
  room phantoms it reports 3.56770844022e-5 at A 0.500894.
- BCX's b1h:435e5b798acada04 (work/lanes/BCX/front_w1.jsonl, cand/): L +2.03e-9, A +0.00084.
- ACCBUY's buyers and trades (ACCBUY/greedy.py, trades.py, kstate.py).
Acceptance sinks (protections that lower L but cost acceptance):
- X echoes on waiting data (EARLY on v36c: about -0.38e-6 per -0.0034 A; all echoes 3.9160e-5 at A 0.4873 vs v36c
  4.1152e-5; ST2 WAITPROT and INTEG2 echo gadgets); re-measure on v36h, whose known-state guards may already hold part
  of that value.
- Extra detectors, flags, Z or X parity checks on any free on-grid slots (free-cell map in work/lanes/GLOBAL/BRIEF.md),
  and gadgets INTEG2/ACCBUY rejected only for acceptance (their logs).
- Room checks from lane GLOBAL (work/lanes/GLOBAL) when they land; do not duplicate GLOBAL's placement work.

Approach: measure each source's and sink's exchange rate on v36h exactly; then combine greedily or as a knapsack with
joint all-orders pricing (effects do not add), keeping exact A >= 0.5002. Stop rule: a finalist, or every listed source
and sink priced alone and in the best joint combinations with none below tau.
Hosts: hippo <= 12 processes now and <= 24 from 17:30 KST (the main session finishes BCX pricing there), zebra <= 4.
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
circuit, recorded with its qasm sha256. A finalist has L < tau - 3e-7 and exact A >= 0.5002, and fast_check at 1e6 shots prints gates_ok=True (its 1e6-shot acceptance is a binomial estimate: an exact A of 0.5002 misses 0.5 there 34% of the time, so do not reject on it).
Stop at a finalist or when the stop rule below is met; then name, per approach, the measured cost that blocked it. Do not
stop to ask questions: decide within this brief and record each decision in REPORT.md.
</completeness_contract>

<action_safety>
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f. Always OMP_NUM_THREADS=1
  OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. ssh as ssh -q -o ControlMaster=no -o ControlPath=none <host> '...' < /dev/null;
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
