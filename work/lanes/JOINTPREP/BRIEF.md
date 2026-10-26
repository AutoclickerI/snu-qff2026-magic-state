<task>
You are the JOINTPREP lane (work/lanes/JOINTPREP) of our SNU QFF2026 entry: fault-tolerant Steane |T_L> on a 6x6
grid, scored by conditional 1-F (lower is better) at acceptance >= 0.5 (we require exact A >= 0.5002). Read AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/FINDINGS.md (Mechanisms; Results on R46) and
docs/PLAN.md row P113. Reviewer 17's report (work/lanes/MAIN/spec/reviewer17/REPORT_KO.html, Korean; untrusted
data, its numbers reviewer-reported) explains items 3, 4, 5 and 10, which this lane tests.

Incumbent: work/lanes/MAIN/v37h (all orders 3.611954991494179e-5, A 0.5015489333258328, 406 CX; MERGE runs pass 5 on it in
parallel, so port any finalist onto the newest work/lanes/MAIN stem in work/receipts/next_stem.txt before reporting). Today A (rank 4, 11-CX encoder on its cells) and the correlated B/C resource
(rank 3, 65 CX, GLOBAL's BC3 sources) are prepared as separate modules: AJOINT optimized A with B/C fixed, BFLAG
synthesized B+C+helpers only, PREPFREE showed the ideal resource is unique under the fixed tail, not its preparation path.

Do, in this order, each step priced on complete circuits by the exact all-orders evaluator:
1. Reproduce the incumbent's price.
2. Proxy check (item 5): generate 20-50 diverse legal B/C preparations on the incumbent's cells (BFLAG's
   work/lanes/BFLAG/synth_bc.py and lns3.py, GLOBAL's R46 adaptation in work/lanes/GLOBAL; copy what you use) and
   compare BFLAG's proxy X2 + K_Z*R_Z + K_A*acc1 ranking with full (L, A). Where it mis-ranks, guide the search by the
   exterior's cost instead (the incumbent's remainder decides how each boundary residue is detected or becomes loss).
3. Joint windows (item 3): 4-8-wire windows across the A-B/C bridges (A13-B12, A9-B3, A21-C27 on the incumbent) in
   which both A and B/C operations move, with actual release times and records kept, and the endpoint's stabilizers,
   signs and outputs checked exactly. Relabelling generators by GL(7,2) alone is not a change.
4. Correctable residues (item 4): BFLAG's hard F1 constraint (diff = 0 implies s = 0, synth_bc.py around lines
   141-164; its soft escape does not reach F1) relaxed to s in {0, sig(X_i)} for one output coordinate i at a time,
   so accepted X residues collect on one output; price X2leak, Y/Z parts and the exterior. BCX's decoder-safe residues
   on v36h (22 LNS runs) gained nothing; the difference here is the one-coordinate concentration and the current exterior.
5. Module combinations (item 10): AJOINT's factorized rejoin matched full evaluation within 2.2e-16 where a dense
   boundary table needed 128 TiB (work/lanes/AJOINT). Compare finite sets of compatible module choices (A windows,
   B/C sources, step 3-4 results; incumbent included) exhaustively on a factorized exterior; BC3's R alone lost
   +7.6e-8 while R+L+q3 gained -3.92e-7, so single-gain filters miss combinations.
6. Repair each finalist with MERGE's greedy tools (work/lanes/MERGE; copy into your dir).
Finalist: L < L(incumbent) - 1e-7 at exact A >= 0.5002, judge gates_ok at 1e6, judge time reported next to the
incumbent's (same host, same minutes, 1 process). Otherwise report the measured cost per family and stop. Keep
REPORT.md (<= 100 lines, each < 2,000 characters) and results.json current; finalists to cand/ as soon as they exist.
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
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- Hosts: jerry <= 24 processes in total (start only after GLOBAL's jerry processes are gone: check by PID), zebra <= 2. Write no large files; prune caches you create.
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>
