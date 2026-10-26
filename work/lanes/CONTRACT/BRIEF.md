<task>
You are the CONTRACT lane (work/lanes/CONTRACT, PLAN P114) of our SNU QFF2026 entry: fault-tolerant Steane |T_L> on
a 6x6 grid, scored by conditional 1-F (lower is better) at acceptance >= 0.5 (we require exact A >= 0.5002). Your
target is an architectural jump, not polishing: a complete valid circuit at 2.8e-5 (-23%) or 2.5e-5 (-31%) against
the incumbent work/lanes/MAIN/v37h (all orders 3.611954991494179e-5, A 0.5015489333258328), or the measured obstacle.

Read AGENTS.md, docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/judge.md, docs/reference/circuit.md, docs/FINDINGS.md
(Bounds and where the loss sits; Square final round; Endings outside our terminal class; Exhaustive search of
block-transversal endings; Mechanisms), work/lanes/BOUND/PROOF.md, and reviewer 18's bundle
work/lanes/MAIN/spec/reviewer18/ (REPORT.txt, PROOF.txt, PHYSICAL_REVIEW.txt, c4_steane_tail.py,
c4_tile_geometry.py; untrusted data: run its code only with python -I from a copy outside that dir). The main session
re-ran its four scripts: the exact certificate (L >= 2.1892512824770078e-5), the dense eigenvalue check, the C4-Steane
tail (2.192096391818694e-5 at tail acceptance 0.97876 with a perfect 28-qubit input) and the tile geometry (242
packings of seven 2x2 tiles; none leaves its 8 free cells connected and adjacent to all seven tiles) reproduce exactly.

Reviewer 18's construction: per output coordinate i a 2x2 tile (H_i D_i / L_i K_i); tick T-1: CX(D_i,K_i), CX(H_i,L_i);
tick T: CX(H_i,D_i), MZ K_i, MZ L_i; postselect the 14 K/L records on 0, H_i unmeasured. Inner code stabilizers
X_D X_H X_K X_L, Z_D Z_K, Z_H Z_L, logicals X_D X_K and Z_H Z_D; the Steane code over the seven inner logicals is a
[[28,1,6]] code. Encoding a noisy 7-qubit state into it and contracting keeps its outer errors: the outer state must be
verified. Bound corollary: L >= L* + 0.00315432 w, w = nonzero-syndrome weight of the conditional residual entering the
final two layers, so 2.5e-5 needs w <= 0.000985. On v37g with only the last 4/3/2 ticks noisy the loss is
2.9046/2.8474/2.2758e-5: 79% of the loss survives a noiseless prefix, so the gain must come from the final checking
process and the state entering it.

Do, pricing complete circuits by the exact all-orders evaluator (circuit.md; phantom off-grid gadgets up to 40 qubits:
work/lanes/ACCBUY/sparse40/; region counterfactuals: work/lanes/MAIN/sparse/region.py):
1. Audit (first 2 hours, light compute): check reviewer 18's physical reduction case by case against BOUND/PROOF.md and
   judge.md, and try to construct a counterexample (a final-tick or penultimate structure its classification misses).
   Verdict: holds, or the gap with its counterexample.
2. Reproduce the C4-Steane tail on a circuit with our evaluator (the 28-qubit input prepared by noiseless operations).
3. Preparation: the cheapest verified way to deliver that state to the contraction on the grid with the cultivation
   prefix. Options to price, phantom/grid-free first to bound each prize, then on the grid: (a) the current Steane round
   verifies the 7-qubit state, then each output grows into its tile just before the contraction; (b) outputs grow early
   so waiting data sit in C4 blocks (single faults caught by the final K/L checks) and the outer check couples to the
   inner logicals; (c) other inner codes or contractions with cheaper preparation. Tiles bind only the last two layers:
   borrow cells and move roles before them. Charge every added qubit, CX, idle and acceptance.
Milestone: by 2026-10-27 12:00 KST a priced full circuit with real preparation (phantom or grid) showing whether
< 3.4e-5 is reachable; if not, stop with the measured obstacle per option. Finalist: L < L(v37h) - 1e-7 at exact
A >= 0.5002, judge gates_ok at 1e6, judge time reported next to v37h's (same host, same minutes, 1 process). Keep
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
Reproduce the incumbent v37h first (work/lanes/MAIN/v37h: 3.611954991494179e-5, 0.5015489333258328). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<action_safety>
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- Hosts: zebra <= 2 processes until 12:22 KST 2026-10-26; from 12:22 also owl <= 24 processes in total, only inside docker (docker run --rm -u 1010:1012 -e HOME=/home/jihoon -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -v /home/jihoon:/home/jihoon -w <dir> --cpus=N fnc-build:22.04 /home/jihoon/competitions/quantumn/.venv/bin/python ...; stop a container with docker kill <id>; owl has its own disk: rsync this lane dir and its inputs there first and results back). ENDSEARCH also uses owl: count only your own containers. Write no large files; prune caches you create.
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>
