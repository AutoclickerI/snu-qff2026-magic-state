<task>
You run research lane BCV of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F (lower is better) with an acceptance gate (we keep exact A >= 0.5002). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/BCV. Read first: /home/jihoon/competitions/quantumn/AGENTS.md, docs/GOAL.md,
docs/CONSTRAINTS.md, docs/PLAN.md, docs/FINDINGS.md, docs/reference/circuit.md, docs/reference/judge.md, then work/lanes/DIGEST/DIGEST.md (priority 3; rows C08, C15, C21, C55, C63, C69, C70),
work/lanes/MAIN/spec/reviewer13/REPORT_KO.md sections 5-7, and work/lanes/{BCX,BFLAG,PCC,ACCARB}/REPORT.md, BCX/HANDOFF.md.

Goal: beat the incumbent v36i (work/lanes/MAIN/v36i.{qasm,json}; L = tau = 3.809137946902697e-5, A = 0.5067293) by a
different B/C verification instrument: B (cells [6,26,13,11,4,23,27]) must reach B->D at 45 free of dangerous X errors;
today C (cells [12,25,19,17,5,29,28]) does this with the correlated rank-3 resource r3 (56 CX, ticks 33-43), B->C at 44
and C read in Z. B/C cells 28-42 made noiseless are worth -3.81e-6 on v36h (overlapping); r3's preparation cost is
3.76e-6. Rank by J_tau = A*(L - tau). Acceptance is cheap (deleting the early q25 echo buys +0.006 for +5.8e-9), so
spend it freely.

Closed (do not repeat; each closes only the recipe tested): r3-contract LNS and decoder-safe residues (BCX leads 1-2),
direct rank-four R_102 (best 4.831e-5), C as four parity ancillas or redundant weight-3 checks (ANC4), partially
coherent C on r3 + a noiseless V map (PCC), product-C/MX single-coordinate diagnostics and S/H/SX final conjugations
(reviewer 13). Reviewer 13's R6 (V = span{e1+e2} via one R->RX at q12/38, Bell readout CX25->19 at 45, MX25, MZ19) is
rebuilt in work/lanes/ACCARB/builds (3.8339504321e-5, A 0.504023 on v36h; it trades loss for acceptance).

Open directions, in order:
1. A branch-aware meter during B's preparation (an earlier encoded flag) that catches B's dangerous X errors before
   44, so the pre-use check can be lighter, synthesized jointly with the resource and readout (DIGEST #3). First price
   ideal meters at three r3 cuts (perfect, noiseless measurement of the chosen parities) to find which information is
   worth having, then synthesize only a meter with value.
2. Resources R_V with V outside C2 that need no new routing (reviewer 13 #5: any linear V in F2^7 works); enumerate
   rank-one and rank-two V reachable by reset-basis changes on v36i's existing r3 network, with matching C readouts.
3. Logical-coset tagging of B through redundant C marks with weight >= 2 tags (reviewer 13 #6), only if a prep fits the
   existing window (their nearest-neighbour prep is 77 CX at depth 31) and the evaluator handles the FRAME it needs.
Stop rule: a finalist, or each direction priced at its decisive test with the cost that blocks it.
Hosts: hippo <= 24 processes in total for this lane, zebra <= 4.
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
