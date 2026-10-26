<task>
Lane CONTRACTS (P117 in docs/PLAN.md) of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane-code
|T_L> on a 6x6 grid, scored by conditional 1-F (lower is better) at p = 1e-3. Read docs/GOAL.md, docs/PLAN.md ("How
lanes run", P116, P117), docs/FINDINGS.md (Bounds, Layout and geometry) and docs/reference/circuit.md first.

Question: does choosing the final round's resource contract for preparation cost, not for the tail's second-order
coefficient c2, give a full circuit below the incumbent?

Context:
- Incumbent v37i (work/lanes/MAIN/v37i): L 3.591182404095001e-05, A 0.5003576309837844. Our final check is a Steane
  round; square, square + leaf and path rounds are cheaper with perfect resources (square 2.5558e-5 round only) but
  every grid build so far lost on preparation and movement (FINDINGS "Grid cost of moving resources").
- WHOLEEND (work/lanes/WHOLEEND: tsearch.py, logs/tsearch.json, MODEL.md section 3, REPORT.md) enumerated 4,797
  T-only contracts (resource Pauli eigenstates and readouts over the directed orientations of square, path and tree
  graphs that keep T up to an affine X/Z frame) and priced only the six minimum-c2 ones, with perfect resources
  (best square 2.558e-5 versus ordinary 2.556e-5; on v37c's noisy prefix with perfect arrivals 2.878e-5 versus
  2.860e-5). c2 ignores preparation; ENDSEARCH's grid-free full prices already invert the round-only order (square
  round 2.556e-5 but full 3.467e-5; path round 2.709e-5 but full 3.408e-5). Reviewer 16's proposal (work/lanes/MAIN/
  spec/reviewer16/REPORT_KO.md, section 2): choose 20-50 discarded contracts with different preparation stabilizer
  structure and verification burden, and price them on the same prefix with real noisy preparation; CX count alone is
  not a valid preparation-cost proxy.
- REDESIGN (work/lanes/REDESIGN: REPORT.md, MODEL.md, templates.py, template_prize.py, mixed_prize.py, price.py) prices
  square, square + leaf and path endings with real just-in-time preparation on v37h's prefix (grid-free path mixed
  control 3.30467e-5) and builds grid layouts; WAITCUT (work/lanes/WAITCUT) built a just-in-time B/C factory. Copy what
  you use into your lane dir; do not duplicate their layout searches.

Work:
1. Load the 4,797 contracts; for each compute preparation features: the resource stabilizer group per block (product
   vs entangled, weight), a minimum-CX and minimum-depth fault-tolerant preparation (exact search where small, else a
   synthesized template), the verification needed (which preparation faults the round's detectors catch), and the
   grid footprint (block cells and degree needs).
2. Select 20-50 contracts spread over those features and over c2 (not the top of any single feature), plus the
   ordinary square, path and square + leaf as controls.
3. Price each grid-free with real noisy just-in-time preparation on the same prefix (v37h's or v37i's; say which), at
   equal bounded repair, by the exact all-orders evaluator; record raw validity first.
4. Report the frontier over (L, A, preparation CX/depth/footprint). For the best three, attempt a grid embedding with
   REDESIGN's layout models within budget; any full grid circuit below v37i goes to cand/ at once.
Budget: first decision by 2026-10-27 06:00 (does any non-minimum-c2 contract beat its graph's ordinary contract on
grid-free full price?); lane end 2026-10-27 18:00.
</task>

<compute>
owl only, at most 24 processes, in docker (owl's native python cannot load numpy):
docker run --rm -u 1010:1012 -e HOME=/home/jihoon -v /home/jihoon:/home/jihoon -w <dir> --cpus=24
fnc-build:22.04 /home/jihoon/competitions/quantumn/.venv/bin/python ... ; zebra at most 2 processes for construction
and verification. Stop containers with docker kill <name>; name your containers contracts_*.
</compute>

<structured_output_contract>
Keep work/lanes/CONTRACTS/REPORT.md current (at most 100 lines): verdict first, then the frontier table (contract id,
graph, preparation features, L, A, repair received, sha256), decisions with reasons, what is verified versus
inferred, and each experiment's outcome class. Save every priced circuit as a stem named by QASM plus ordered
data_qubits, and results.json keyed by QASM sha256.
</structured_output_contract>

<tools>
- Exact all-orders price (needs barriers over all used qubits, no FRAME/POSTSELECT):
  cd work/lanes/MAIN/sparse; OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 ../../../../.venv/bin/python
  sparse_walsh.py <path/stem without suffix> 72 canonical 16   (about 1 s at 16 processes; prints JSON with loss, acceptance).
  Many single-process prices in parallel: work/lanes/BUNDLE/ev.py (price_stem) and menu.py (edit menu, apply_bundle).
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
Reproduce the incumbent v37i first (work/lanes/MAIN/v37i: 3.591182404095001e-05, 0.5003576309837844). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<action_safety>
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Never signal, stop or kill a process you did not start (contest racers included). If a host is over its core count,
  shrink your own jobs and record it in REPORT.md.
- Do not use spawn_agent or any sub-agent.
</action_safety>
