<task>
You run research lane IFACE of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F (lower is better). Working dir: /home/jihoon/competitions/quantumn/work/lanes/IFACE.
Read first: /home/jihoon/competitions/quantumn/AGENTS.md, docs/GOAL.md, docs/CONSTRAINTS.md, docs/PLAN.md,
docs/reference/circuit.md, docs/reference/judge.md, then work/lanes/DIGEST/DIGEST.md (priority 1 and rows C19, C27, C33,
C71, C72) and work/lanes/{EARLY,R43,TREP2,ST2,FRESH}/REPORT.md.

Goal: beat the incumbent v36h (work/lanes/MAIN/v36h.{qasm,json}; L = tau = 3.815473322483099e-5, A = 0.5016415) by
changing the prefix-to-suffix interface: which cells the prefix releases and when, where the data end up, and how the
prefix's last stage completes (a state-specific completion that absorbs routing inverses into the next check instead of
reversing every routing CX, reviewer 12 #2), so that the suffix (data hops, guards, A, the r3 B/C resource, the round)
gets earlier releases or room next to the data. Rank by J_tau = A*(L - tau).

Why this is the larger lever: with everything before tick 43 noiseless v36h costs 3.0432e-5, so the pre-round
contributes 7.72e-6 (data waits 28-42 alone 3.88e-6, B/C cells 28-42 3.81e-6, A 1.64e-6, before 33 2.10e-6;
overlapping). EARLY's layout floor R42 and R43's helper placements assumed v36h-like prefix releases; a prefix with a
different release profile changes those occupancy assumptions. Room next to the data is worth up to -2.705e-6 as
phantoms (both A-flag-gap helpers plus a late X check; work/lanes/GLOBAL/room/prices.txt); one tick less of data wait
-0.684e-6. Lane GLOBAL (work/lanes/GLOBAL) is building on-grid room with v36h's prefix fixed; you own the prefix side
and may reuse GLOBAL's outputs as they appear.

Approach, in order:
1. Find out exactly what v36h's prefix is (circuit.md: Gidney d=3 cultivation stages, PRESYN's blue XZ check, coherent
   two-CX hops into D = [0,20,7,10,3,22,21]) and where its routing/uncompute steps and cell releases sit (timeline:
   work/lanes/R43/v36h.timeline.txt; cells 30-35 and 24 idle until 39-44, cells 23, 27, 29 until 32).
2. A fixed-variable round-trip model of v36h's roles, lifetimes, records, guards and r3 that reproduces v36h exactly
   (reviewer 12 #3; the old FRESH/ST1 model could not express r3).
3. Generate prefix-tail variants (state-specific completions, different output placements, merged hops, earlier blue
   check releases) and keep a release-profile archive of 20-50 diverse interfaces, not only the best by L (reviewer 12
   #4). Price each with v36h's suffix where it still fits.
4. For the three most promising interfaces, build the downstream suffix (reuse r3 and the A encoder by translation where
   cells allow; otherwise BFLAG synth_bc/lns3 or BCX bcsynth/bclns, EXENC/AENC, ACCBUY kstate/greedy, FLAG flagenum) and
   price the complete circuits.
Stop rule: a finalist, or all three downstream builds priced with none below tau.
Hosts: hippo <= 24 processes in total for this lane, starting 16:45 KST (the main session prices BCX there until then;
before that use zebra <= 4).
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
