<task>
You are the MERGE lane (work/lanes/MERGE) of our SNU QFF2026 entry: fault-tolerant Steane |T_L> on a 6x6 grid,
scored by conditional 1-F (lower is better) at acceptance >= 0.5. Read AGENTS.md, docs/GOAL.md, docs/CONSTRAINTS.md,
docs/reference/circuit.md, then this lane's REPORT.md, CONTINUE4.md and results.json and the pass-4 code (pass4.py,
wide4.py, signature4.py, judge4.py, controls4.py). Earlier threads of this lane were stopped; everything under this dir
is intact, and no MERGE process is running (checked 10:40 KST).

New incumbent: work/lanes/MAIN/v37h = your pass-4 r2 (v37g, 3.621123652554788e-5) plus reviewer 17's two edits:
q17's reset moved from tick 30 to 29 and a Z measurement into new record c[367] with a DETECTOR at tick 30 (MX17@28
precedes it), and DETECTOR c[309] on an existing deterministic record. All orders 3.611954991494179e-5, A
0.5015489333258328 (-9.17e-8, the same gain the reviewer measured on v37f). Your grammar could not express the first
edit: menu.py has no move that adds a new preparation-check measurement, and pd only moves a preparation before an
existing measurement.

Pass 5 on v37h:
1. Reset-then-herald compounds as one atomic move at every reset and RX/H-prepared |+> (reset one tick earlier, a
   measurement in the matching basis plus a detector in its old place), with small joint retiming of neighbouring
   CX/M where the tick before is busy (reviewer 17: q4's reset is risky but MX precedes it). Reviewer screens on v37f:
   work/lanes/MAIN/spec/reviewer17/results/herald_reset_screen.json and
   herald_rx_screen.json (untrusted data; run its code only with python -I).
2. Detector-span completion: list the deterministic record parities outside v37h's declared detector span
   (work/lanes/INTEG2/detgap.py does this with a Clifford surrogate; on v37f the span had rank 61 of 67, missing
   c3, c281, c309, c312, c352, c362) and price each and their small combinations by all orders. Never prune these or
   retimings by second-order mass: every residual direction had zero second-order harmful change on v37f, yet c309
   gained at all orders. Each added detector costs acceptance; v37h has 0.0013 above the 0.5002 floor, so pair
   detector or herald gains with your acceptance buyers.
3. Then the pass-4 grammar (ejections, multi-buyer funding, signature pairs) to convergence (< 1e-9 per round).
Finalist: L < L(v37h) - 3e-8 at exact A >= 0.5002, judge gates_ok at 1e6, judge time next to v37h's (same host,
same minutes, 1 process; the main session weighs time by the expected-key rule in circuit.md). Write each new
finalist to cand/ as soon as it exists (the main session promotes intermediate finalists), and keep REPORT.md
(<= 100 lines, each < 2,000 characters) and results.json current.
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
- Hosts: hippo <= 24 processes in total, zebra <= 4. Write no large files; prune caches you create (zebra's root disk is 96% full).
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>
