# EMBED restart on a fresh thread (main session, 2026-10-26 23:35)
Your previous Codex thread is locked, so this is a new thread for the same lane. Recover your state from REPORT.md, RESULTS.json, builds/, models/ and logs/ before acting; background processes the previous worker started may still run (check them by the PIDs and logs it recorded; never duplicate a running job; kill only this lane's own processes, by PID). The original brief follows, then two continuations; the later text takes precedence.

<task>
Lane EMBED of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane-code |T_L> on a 6x6 grid,
scored by conditional 1-F (lower is better) at p = 1e-3. Read docs/GOAL.md, docs/PLAN.md ("How lanes run", P116),
docs/FINDINGS.md ("Grid cost of moving resources"), docs/reference/circuit.md and work/lanes/REDESIGN/REPORT.md and
MODEL.md first.

Situation: another team holds rank 1 at an official 3.086e-5 with 293 two-qubit gates; our incumbent v37j
(work/lanes/MAIN/v37j: 3.5870950034704206e-05, A 0.5010179047299785, 412 CX) cannot reach that by racing. REDESIGN
contracted our prefix (40 ideal-identity CXs removed, known-state moves relabelled, dead resets removed; prefix done at
tick 37) and priced new endings with real just-in-time preparation grid-free: square + leaf 2.942e-5, path 3.017e-5,
square 3.114e-5 before repair (repaired older variants: 3.255e-5, 3.279e-5). Every CP-SAT embedding so far is
infeasible or UNKNOWN (fixed prefix placement, <= 2 transfers per coordinate). REDESIGN keeps its CP-SAT models.

Task: get one of those families onto the real grid by a different method: constructive placement plus local search.
- Start from REDESIGN's contracted prefix and B1 builds (work/lanes/REDESIGN/models/, builds/, results.json; copy what
  you use). Choose the ending's block cells first in the region the contracted prefix frees, apply any of the 8 grid
  symmetries (and translations where the prefix fits) to the prefix, re-choose output cells and data hops, route
  resources with measured or coherent transfers, drop guards whose cells are needed and re-add guards where cells are
  free.
- Search by a fast proxy (CX count, ticks, idle exposure on data and resources) with exact all-orders prices on the
  best (work/tools/qtools; price rejects raw-invalid builds), then one bounded repair (MERGE's tools) on the best.
- Any raw-valid grid build at or below 3.4e-5 at A >= 0.5002 goes to cand/ at once with paired judge timing against
  v37j (1e6 shots, one process, same host, same minutes).
Budget: first priced grid build by 2026-10-27 06:00; lane end 2026-10-27 18:00 unless a build below v37j earns more.
</task>

<compute>
sunfish at most 20 processes (start heavy jobs after 20:21 today, when the hourly racer shrinks there), zebra at most 2.
Remote hosts: plain ssh -q.
</compute>

<structured_output_contract>
Keep work/lanes/EMBED/REPORT.md current (at most 100 lines): verdict first; a table of grid builds (family, layout
summary, CX, ticks, L, A, repair received, sha256); outcome class per experiment; verified vs inferred.
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

# EMBED continuation 1 (main session, 2026-10-26 21:15) - new target, new method
Your closure is accepted (REDESIGN-family embeddings lose to transport; no exclusion). New target: FLAGH's flag-based
design, which passed its grid-free test at 3.0198428e-5, A 0.6654, 180 CX, 36 wires, 15 T, no harmful single fault
(work/lanes/FLAGH/REPORT.md, its builds/ and evidence/, stem sha256 14680d5155ff1afb...). The named way to cut
transport: it is small and made of gadgets whose connectivity is free (cat states along any spanning tree, any encoder
per cell set, flags beside the CXs they guard), so it can be laid out on the grid from the start.
FLAGH itself now does constructive gadget-by-gadget grid synthesis. You take a different method, so the two do not
duplicate: an exact time-expanded placement model (CP-SAT): each logical wire occupies one cell per time window, a CX
needs adjacent cells at its tick, wires move only by measured transfers or SWAPs that the model pays for, a reset frees a
cell for reuse, gadget connectivity is a choice inside the model (cat-state trees, encoder variants from
work/lanes/EXENC, flag positions), objective = ticks plus idle exposure weighted by the measured channel costs.
Decompose by time (prefix of injection + precheck, logical checks, square ending) if the full model is too large.
Price raw-valid builds exactly with qtools, one bounded repair on the best, then spend the acceptance surplus.
Budget: first raw-valid native build by 2026-10-27 06:00 (each model at most 30 min; UNKNOWN = budget exhausted);
checkpoint 14:00. Any grid build at or below 3.4e-5 at A >= 0.5002 goes to cand/ at once with paired judge timing
against v37j. Read FLAGH/REPORT.md first and again at each step; never write in FLAGH's dir.
Compute: sunfish at most 20 processes, zebra at most 2.

# EMBED continuation 2 (main session, 2026-10-26 23:30)
New target design: DEEP improved FLAGH's architecture grid-free to 2.7185414e-5 at A 0.6734 with 170 CX, 15 T, 22
native ticks, 36 wires (work/lanes/DEEP/cand/final_flagh.json, final_flagh_roles.json; stem
DEEP/cand/final_flagh_gridfree_9a83951a37ad3cb5_d0_1_2_3_4_5_6). Point your time-expanded placement model at it (its
22 ticks make the model smaller than the 180-CX version). DEEP now also produces embedding-friendly variants (fewer peak
live wires, bounded per-tick degree); read DEEP/REPORT.md as it updates and model the variant that embeds best. Same
milestones: grid build <= 3.4e-5 at A >= 0.5002 to cand/ at once.
