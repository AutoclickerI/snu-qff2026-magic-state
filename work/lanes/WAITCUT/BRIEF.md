<task>
You are the WAITCUT lane (work/lanes/WAITCUT, PLAN P115) of our SNU QFF2026 entry: fault-tolerant Steane |T_L> on a
6x6 grid, scored by conditional 1-F (lower is better) at acceptance >= 0.5 (we require exact A >= 0.5002). Incumbent:
work/lanes/MAIN/v37h (all orders 3.611954991494179e-5, A 0.5015489333258328; a trained detector basis for it is in
work/lanes/MERGE, see JOINTPREP/REPORT.md line 10: width 9, about 7 s per price at one process).

Read AGENTS.md, docs/GOAL.md (Target), docs/CONSTRAINTS.md, docs/PLAN.md (Levers), docs/reference/circuit.md and
docs/FINDINGS.md in full: it lists every closed recipe; do not repeat one without naming what differs.

Why this lane: the reachable gap is 1.42e-5 (v37h 3.612e-5 to the audited floor 2.189e-5). With only the last three
ticks noisy v37g costs 2.847e-5, so preparation and waits before the final check hold <= 0.77e-5 (54% of the gap),
and no lane attacks that share at architecture scale. On v37b the tick cuts (every op before t0 noiseless) gave
t0=20 3.638e-5, 30 3.551e-5, 36 3.207e-5, 40 2.961e-5, 44 2.900e-5: ticks 30-40 held about 0.59e-5. Known pieces:
ideal B/C source and core noise worth 4.09e-6 on v37a; each earlier round tick about 0.68e-6 on v36h; ENDSEARCH's
path builds were dominated by data waits (5.33e-5 -> 3.16e-5 with data waits noiseless). The A and B/C preparations
are at a joint local optimum for the grammars tried (JOINTPREP), BC3 sources are merged, GLOBAL is closed.

Do:
1. Attribution on v37h (region counterfactuals: work/lanes/MAIN/sparse/region.py, spec format in circuit.md; tick
   cuts: work/lanes/TERMINAL/cut.py; per-channel: adjoint_ablation.py): a matrix of roles (the seven data qubits along
   their hop paths, A cells, B cells, C cells, guards/helpers, prefix-only cells) x tick windows (<20, 20-30, 30-36,
   36-40, 40-44, 44-46), each made noiseless alone, then the pairs among the largest cells (counterfactuals overlap
   under postselection; report them as such). Separate idle noise from gate/measurement noise in the largest cells.
2. For the two or three largest cells, name the surviving mechanism (which fault pairs reach the decoded loss and
   why the detectors miss them) and design a change that removes it at the root: for example data that wait less or
   wait in a detected form, resources released just in time, checks that see the dominant pair. Bound each design
   with phantom or grid-free full circuits first (work/lanes/ACCBUY/sparse40/), then build on the grid from v37h and
   repair with MERGE's tools (copy into your dir).
Targets: a full circuit >= 3e-6 below v37h (8%) at A >= 0.5002, judge gates_ok; checkpoint 2026-10-27 12:00 KST: the
attribution matrix and a priced design per top cell, else stop with the measured obstacle. A finalist below
L(v37h) - 1e-7 goes to cand/ at once (the main session promotes intermediate finalists). Keep REPORT.md (<= 100
lines, each < 2,000 characters) and results.json current.
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

<selection_rules>
Select finalists by the lowest exact L at exact A >= 0.5002; J_tau = A*(L - tau) is only a search heuristic, with tau =
the current incumbent's L (a stale tau trades loss for acceptance). Keep the (L, A) Pareto front for acceptance buys.
Before ranking a build that changes the outputs or the tail, check raw correctness (six noiseless output stabilizers
+1): the all-orders price checks only the decoded loss. Name stem files by QASM plus ordered data_qubits.
</selection_rules>

<default_follow_through_policy>
Do not stop to ask questions: the owner is not available to the lane. Decide, record the decision and its reason in
REPORT.md, and continue. A finalist does not end the lane; keep improving until the completeness contract is met.
</default_follow_through_policy>

<verification_loop>
Reproduce the incumbent v37h first (work/lanes/MAIN/v37h: 3.611954991494179e-5, 0.5015489333258328). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<action_safety>
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q -o ControlMaster=no -o
  ControlPath=none <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- Hosts: owl <= 24 processes in total, only inside docker (docker run --rm -u 1010:1012 -e HOME=/home/jihoon -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -v /home/jihoon:/home/jihoon -w <dir> --cpus=N fnc-build:22.04 /home/jihoon/competitions/quantumn/.venv/bin/python ...; stop a container with docker kill <id>; owl has its own disk: rsync this lane dir and its inputs there first and results back; the racer also runs on owl, count only your own containers), zebra <= 2 light work. Write no large files; prune caches you create.
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>
