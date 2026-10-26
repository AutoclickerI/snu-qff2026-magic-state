<task>
Lane FLAGH of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane-code |T_L> on a 6x6 grid,
scored by conditional 1-F (lower is better) at p = 1e-3 with the organizer's noise model. Read docs/GOAL.md,
docs/PLAN.md ("How lanes run"), docs/FINDINGS.md (Bounds; Closed recipes), docs/reference/judge.md and
docs/reference/circuit.md first.

Why now: another team jumped to an official 1-F of 3.086e-5 with only 293 two-qubit gates (acceptance 0.510); their
earlier entries were 6.286e-5 at 169 CX and 3.856e-5 at 201 CX. Our incumbent v37j (work/lanes/MAIN/v37j: all orders
3.5870950034704206e-05, A 0.5010179047299785, 412 CX, 35 of 36 qubits used) is a cultivation prefix plus a Steane
check round, and the grid is full. A lean architecture with a different preparation is the hypothesis to test.

Hypothesis: a faithful flag-based fault-tolerant measurement of a logical Clifford whose eigenstate is |T_L> (up to a
transversal Clifford), on the Steane code, followed by an ending in our terminal class, beats v37j. Sources:
Chamberland & Cross, Quantum 3, 143 (2019), arXiv:1811.00566 (Fig. 5(a) flagged logical-H measurement, Fig. 6
repetition, Table 4: level-1 error detection accepts (1-p)^75 with logical rates (9.95, 4.41, 7.87) p^2); Chamberland &
Noh, npj QI 6, 91 (2020), arXiv:2003.03049 (redundant ancilla encoding plus flags). Our earlier attempt (lane CC, in git:
`git show d091f533:work/lanes/CC/REPORT.md` and its build scripts) built a 73-CX grid version that was NOT
fault-tolerant (first-order loss 1.33e-2, 1-F 2.5e-2): read why before building; that negative closes nothing.

Work, as budgeted experiments (process below):
E1 (decision test, by 2026-10-27 03:00): a faithful build with every single fault detected, flagged or harmless
(native single-fault audit), grid-free (ideal adjacency, off-grid ancillas allowed), with a realistic ending into seven
output qubits, priced exactly by all orders (work/tools/qtools: full barriers, no FRAME/POSTSELECT lines, at most 20 T
- Fig. 5(a) uses 15; for up to 40 qubits see work/lanes/ACCBUY/sparse40). Try both the paper's repetition schemes and
our detector conventions (every deterministic parity as a DETECTOR; acceptance must stay >= 0.5002 exactly).
Smallest decision-changing result: grid-free L below 3.3e-5 at A >= 0.5002 earns E2; above 3.6e-5 closes the recipe as a
measured failure, with the dominant fault mechanisms named.
E2: embed the best E1 design on the 6x6 grid (it needs far fewer cells than v37j), route, price, one bounded repair
(MERGE's tools), judge gates and timing. A grid circuit below v37j goes to cand/ at once.
</task>

<compute>
hippo at most 24 processes (start heavy jobs after 20:21 today, when the hourly racer shrinks there), zebra at most 2.
Remote hosts: plain ssh -q.
</compute>

<structured_output_contract>
Keep work/lanes/FLAGH/REPORT.md current (at most 100 lines): verdict first; a table of priced builds (design, qubits,
CX, T count, grid-free or grid, L, A, repair received, sha256); each experiment's outcome class; verified vs inferred.
Save every priced circuit as a stem named by QASM plus ordered data_qubits (qtools.write_stem).
</structured_output_contract>

<tools>
- Exact all-orders price, stems, raw validity, judge gates and the promotion policy: the shared package work/tools/qtools
  (README there). Import it, do not copy it: PYTHONPATH=/home/jihoon/competitions/quantumn/work/tools; price(stem) is
  cached and replays every saved detector basis (v37i about 3 s at one process); write_stem names stems by QASM plus
  ordered data_qubits; price rejects raw-invalid builds. Many single-process prices in parallel: one process each.
- Region counterfactuals: work/lanes/MAIN/sparse/region.py (spec format in circuit.md).
- Judge check at 1e6 shots: work/fast_check.py; its gates_ok is the verdict (format, class, correctness); acceptance
  below 1e8 shots is a binomial estimate, the criterion is exact all-orders A >= 0.5002.
- Repairing a new circuit: MERGE's greedy tools (copy into your dir); acceptance costs about 1.6e-5 loss per unit.
  A new family gets one short standardized repair pass (at most 200 exact prices or 30 minutes) before it is compared;
  record how much optimization each compared candidate received. Spend more repair only when the improvement curve or
  a named unresolved mechanism justifies it.
- Python is /home/jihoon/competitions/quantumn/.venv/bin/python.
</tools>

<selection_rules>
Select finalists by the lowest exact L at exact A >= 0.5002; J_tau = A*(L - tau) is only a search heuristic, with tau =
the current incumbent's L (a stale tau trades loss for acceptance). Keep the (L, A) Pareto front for acceptance buys.
Validity is raw correctness, judge gates_ok and exact A >= 0.5002; zero harmful single faults (fault_scan c1 = 0) is a
search preference, not a validity rule: keep a bounded-residue track priced by its full all-orders loss. Report judge
time next to the incumbent's (same host, same minutes); there is no lane-local speed cap: the main session weighs time
by the expected-key rule (docs/reference/circuit.md). Before ranking a build that changes the outputs or the tail, check raw correctness (six noiseless output stabilizers
+1): the all-orders price checks only the decoded loss. Name stem files by QASM plus ordered data_qubits.
</selection_rules>

<default_follow_through_policy>
Do not stop to ask questions: the owner is not available to the lane. Decide, record the decision and its reason in
REPORT.md, and continue. Work in budgeted experiments: for each, state the hypothesis, the smallest result that would
change the next decision, its wall-time and evaluation budget, and what result earns more budget. Run independent
investigations concurrently as background processes within your host limits. Close each with one of: certified
exclusion (a proof under stated assumptions), measured failure (named saved circuits), budget exhausted, or proxy
rejection, and say which. A finalist leaves the lane at once (cand/) while work continues. Fixed assumptions (a fixed
prefix, a layout, a grammar) are experiment scope, not contest constraints: name them and when they should expire.
</default_follow_through_policy>

<verification_loop>
Reproduce the incumbent v37j first (work/lanes/MAIN/v37j: 3.5870950034704206e-05, 0.5010179047299785). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<action_safety>
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null (the shared
  per-host connection from ~/.ssh/config; never -o ControlMaster=no, which makes every call a fresh login); sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Never signal, stop or kill a process you did not start (contest racers included). If a host is over its core count,
  shrink your own jobs and record it in REPORT.md.
- Do not use spawn_agent or any sub-agent.
</action_safety>
