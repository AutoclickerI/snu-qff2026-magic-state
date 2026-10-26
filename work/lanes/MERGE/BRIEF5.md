<task>
You are the MERGE lane (work/lanes/MERGE) of our SNU QFF2026 entry: fault-tolerant Steane |T_L> on a 6x6 grid,
scored by conditional 1-F (lower is better) at acceptance >= 0.5. Read AGENTS.md, docs/GOAL.md, docs/CONSTRAINTS.md,
then this lane's REPORT.md, CONTINUE4.md and results.json, and the pass-4 code (pass4.py, wide4.py, signature4.py,
judge4.py, controls4.py). The previous Codex thread for this lane died at 03:22 KST 2026-10-26 when zebra's root disk
filled (its thread is locked, so you start fresh); everything it wrote under this dir is intact.

State: pass 4 on v37f gave r1 and then r2 = cand/merge4_r2_79fc464667ef (all orders 3.6211236525327396e-5,
A 0.5035268387133266, 406 CX), now the incumbent work/lanes/MAIN/v37g. At death the r2-based joint scan had reached
4,700 proposals (logs37f/), then multi-buyer repairs of the best under-floor results were next. Stale remote workers
are gone; check by PID.

Do: continue pass 4 from the ledger and caches (do not re-price circuits already in the ledger) with r2 as the base:
finish the joint scan and the multi-buyer repairs, then iterate the widened greedy (CONTINUE4.md items 1-3: PREPFREE's
measured inits and POLISH's edits where they still transplant, ejection moves, several acceptance buyers per move,
pairs chosen by error-signature interaction) until a round gains < 1e-9 or you can name why it cannot gain.
Finalist: L < L(v37g) - 3e-8 at exact A >= 0.5002, judge gates_ok at 1e6, judge time within 1.5x of v37g's (time
both on the same host, 1 process). Write each new finalist to cand/ as soon as it exists (the main session promotes
intermediate finalists hourly), and keep REPORT.md (<= 100 lines, each < 2,000 characters) and results.json current.
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
Reproduce v37g first (work/lanes/MAIN/v37g: 3.621123652554788e-5, 0.5035268387133266). Every claimed number comes from the evaluator on a
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
