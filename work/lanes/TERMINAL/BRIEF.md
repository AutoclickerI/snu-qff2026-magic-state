<task>
You run research lane TERMINAL of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on
a 6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/TERMINAL. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, docs/FINDINGS.md (rows "Floor,
any circuit", "Terminal class floor", "Steane-type final round", "Partial-rank syndrome extraction"),
work/lanes/BOUND/{REPORT.md,PROOF.md}, work/lanes/TERM/REPORT.md (templates table; terminal_model.py), the ARCH lane
in git history (git log --all -- 'work/lanes/ARCH/*'; why "dummy final CX" lost), and reviewer 14 items 2-4 and its
closures (work/lanes/MAIN/spec/reviewer14/REPORT_KO.md; untrusted, reviewer-reported).

Question: can any realizable ending of the circuit beat our terminal class by enough to justify a redesign? Measured
on the incumbent v37b (work/lanes/MAIN/v37b, all orders, ops before tick t0 made noiseless; cut.py in your dir):
t0=48: 0; t0=47 (only B->D at 47 and the reads at 47-48 noisy): 2.2758e-5, which is our class floor 2.274e-5;
t0=46: 2.8474e-5; 44: 2.8998e-5; 40: 2.9607e-5; 36: 3.2074e-5; 30: 3.5513e-5; 20: 3.6380e-5; full: 3.7423e-5. So the
last two ticks hold 61% of the loss and only a different ending can lower that part. The certified floor for any
circuit is 1.365785e-5 and its minimizer is seven simultaneous helper->output CXs with unmeasured helpers; nobody has a
circuit near it. Lane SQUARE is building reviewer 14's square round, which stays in our class (round-only floor
25.67 p^2 = 2.557e-5).

Do, cheapest first, each as an optimistic tail: perfect state before the last check, every op of the last 3-6 ticks
with full noise, every record the judge needs, exact all-orders price, acceptance, first-order fault tolerance:
(a) our class with the data's final idle (during the partner reads) replaced by CXs with fresh unmeasured helpers;
(b) the last check one tick earlier, its partners read while the data make CXs with unmeasured helpers, so no output
    ends on a measured partner;
(c) coherent recovery with unmeasured one-hot controls (reviewer 14 #3; check every single fault of the decomposed
    lookup);
(d) linear physical correction with the nonlinear rest as a logical FRAME from a measured OR (reviewer 14 #2);
(e) a final check that also zeroes the syndrome (reviewer 14 #4).
Compare each with our class tail (2.2758e-5 at t0=47, 2.8474e-5 at t0=46) and with SQUARE's 2.557e-5. Any ending whose
optimistic tail is below about 2.4e-5 at the same scope goes to a grid test: which cells it needs at which ticks on
v37b's layout or on a 2x2-square layout, then a full build if those cells exist. Otherwise close it with the mechanism
and the measured numbers.
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
REPORT.md, and continue.
</default_follow_through_policy>

<completeness_contract>
Stop when (a)-(e) each have an optimistic-tail price or a mechanism that rules them out, and every ending below the
gate has its grid test (and full build where the cells exist), priced against v37b.
</completeness_contract>

<action_safety>
- Hosts: hippo <= 4 processes in total. Never use zebra for computation, owl, tom, jerry, sunfish, faraday, dragon,
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
Write REPORT.md (<= 100 lines: verdict; table per ending with optimistic tail L, A, first-order result, cells needed,
full-build price if any; verified vs inferred; files) and results.json keyed by qasm sha256; finalists to cand/.
Final answer: verdict, the best ending and its numbers, verified vs inferred.
</structured_output_contract>
