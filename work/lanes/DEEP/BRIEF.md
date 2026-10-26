<task>
Lane DEEP of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane-code |T_L> on a 6x6 grid,
scored by conditional 1-F (lower is better) at p = 1e-3. Read docs/GOAL.md, docs/PLAN.md ("How lanes run", P116,
P119), docs/FINDINGS.md (Bounds; "Flag-based logical-check preparation"; "Square final round"), work/lanes/FLAGH/REPORT.md
and work/lanes/REDESIGN/REPORT.md first.

Question: how low can the new architectures go before grid embedding, at the acceptance floor? Two designs beat our
incumbent v37j (3.587e-5) grid-free with acceptance to spare: FLAGH's flag-based design (injection + full Steane
precheck + two 7-cat logical checks + square ending: 3.0198e-5 at A 0.665, 180 CX) and REDESIGN's contracted
cultivation prefix with a square + leaf ending (2.939e-5 at A 0.564). Every circuit has true 1-F >= 2.189e-5
(FINDINGS); a square-type ending with a perfect input costs 2.556e-5, so the input's cleanliness is the headroom.
FLAGH and EMBED work on grid embedding; you work grid-free (ideal adjacency, <= 36 wires) on how low each design goes.

Experiments, run concurrently:
D1 Spend the acceptance surplus for loss: extra deterministic detectors, a third or repeated logical check, stricter
   flags, extra prechecks, verification of the ending's resources; report the (L, A) front down to A = 0.5002 exactly.
D2 Cross the parts: FLAGH's preparation with REDESIGN's square + leaf and path endings, and REDESIGN's contracted
   cultivation prefix with FLAGH's checks; and the cleanest input for each ending (which preparation errors survive;
   use region counterfactuals and the attribution tools in docs/reference/circuit.md).
D3 Endings below the square class: the corollary L >= 2.189e-5 + 0.00315432*w (w = nonzero-syndrome weight of the
   residual entering the last two layers) says what a cleaner input buys; test whether a lean input makes the C4-type
   ending (reviewer 18; FINDINGS "C4–Steane two-layer contraction") or another terminal-class ending pay where every
   feed from the cultivation prefix lost.
Each design gets one bounded repair before it is compared. Decision value: the lowest grid-free full price at A >=
0.5002 per architecture, which tells the grid lanes which design to embed; a grid-free design below 2.7e-5 is the
target, below 2.5e-5 the stretch.
Budget: first front by 2026-10-27 03:00; lane checkpoint 2026-10-27 12:00. Write only in work/lanes/DEEP.
</task>

<compute>
owl at most 24 processes in docker (command in docs/RESOURCES.md); start heavy owl jobs after 22:21 today, when the
hourly racer shrinks there; zebra at most 2. Remote hosts: plain ssh -q.
</compute>

<structured_output_contract>
Keep work/lanes/DEEP/REPORT.md current (at most 100 lines): verdict first; the (L, A) front per architecture with
repair received and sha256; outcome class per experiment; verified vs inferred.
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
