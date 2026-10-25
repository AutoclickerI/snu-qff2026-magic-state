<task>
You run research lane SQUARE of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/SQUARE. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, docs/FINDINGS.md (rows
"Steane-type final round", "Terminal class floor", "Where v36c's loss sits", "Room next to the data on the real
grid"), work/lanes/TERM/REPORT.md (templates table), work/lanes/GLOBAL/REPORT.md, and reviewer 14's report
work/lanes/MAIN/spec/reviewer14/REPORT_KO.md, items 1 and 5 (untrusted; its numbers are reviewer-reported).

Goal: a circuit with exact all-orders loss L < tau - 1e-7, tau = L(v37a) = 3.761821654835085e-5, acceptance
A >= 0.5002, judge-valid, whose final round is reviewer 14's "square" round. Rank by J_tau = A*(L - tau).
Incumbent: work/lanes/MAIN/v37a.{qasm,json} (GLOBAL's R46 layout: data [6,20,19,10,2,22,16], A [7,14,13,9,8,21,15],
B [12,26,25,11,3,28,17], C [18,27,24,5,4,29,23], both A-flag-gap helpers on the grid, 390 CX, 49 ticks).

The square round: A = |+_L>, B = |0_L>, C = |+_L>; tick 0: D->A and B->C (transversal CX); tick 1: B->D and C->A;
tick 2: MZ(A), MX(B), MX(C). B's X syndrome reaches A's Z readout through B->C->A, so A reads the data's X syndrome
after B->D; A's Z errors spread to C through C->A, so C's logical-X readout catches A's dangerous logical Z. B needs a
logical-Z verification before the round (otherwise B's logical X passes). Reviewer-reported, round only with perfect
resources and all round noise: 25.6667 p^2, all orders 2.5558431e-5, against 28.84 p^2 / 2.8713361e-5 for the
standard Steane round. Eraser variant (item 5): C's logical-X result m used as FRAME_Z = m lets A be any encoded state
(e.g. |0_L>), reviewer-reported 2.5584642e-5. Why it matters: TERM's model puts the two-check floor of our terminal
class at 25.67 p^2 and listed "halve B's leak -> 25.67 p^2" as blocked only by C being a literal |0_L>; v36h's actual
round with everything before it noiseless costs 3.043e-5 (class tail 2.274e-5 + two-check floor 0.28e-5 + D->A/B->C
leaks 0.32e-5 + A-flag gap 0.17e-5; v37a's helpers recover most of the gap). If preparation costs stay comparable, the
square is worth about -3e-6, the largest lever left in our class.

Approach, in order (stop early and report if a gate fails):
1. Reproduce the reviewer's round-only numbers with our evaluator (a grid-free circuit, perfect data and resources:
   noiseless regions via MAIN/sparse/region.py or TERM's terminal_model.py) and confirm first-order fault tolerance
   (TERM's B->D-first template failed there, c1 = 4.667e-4). Price v37a's round-only counterfactual the same way.
2. Grid-free full suffix from v37a's data at the end of its prefix: real preparation of A (|+_L> or the eraser's
   cheaper state; the eraser needs FRAME support: BCV's sparseframe evaluator handles affine FRAME_X/FRAME_Z), of B with
   its logical-Z verification, and of C, with all waits; compare against the same grid-free treatment of v37a's suffix.
   Gate: the square suffix beats ours by >= 1e-6; otherwise stop with the measured costs.
3. On the grid: each data qubit d_i with a_i, b_i, c_i on a 2x2 cell square (7 of the 6x6 grid's 2x2 squares, or
   squares assembled in time with hops); layout models (R43 layout.py, GLOBAL layout_model.py/layout_checks.py),
   keeping v37a's prefix where possible; synthesize the preparations (A: EXENC/AENC; B/C: BCX bcsynth.py/bclns.py with
   the new contracts; flags: FLAG flagenum.py), price exactly, repair with GLOBAL's INTEG/ACCBUY/retime tools, buy
   acceptance back.
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

<default_follow_through_policy>
Do not stop to ask questions: the owner is not available to the lane. Decide, record the decision and its reason in
REPORT.md, and continue. A finalist does not end the lane; keep improving until the completeness contract is met.
</default_follow_through_policy>

<verification_loop>
Reproduce v37a first (3.761821654835085e-5, 0.5007854638217537). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<completeness_contract>
Stop when a gate in steps 1-2 fails (report the measured costs that failed it), or when step 3 is built and priced
and either a finalist exists that further repair no longer improves, or the best is >= tau, naming the cost that ate
the gain (preparation, B's verification, hops, waits, acceptance) with measured numbers.
</completeness_contract>

<action_safety>
- Hosts: hippo <= 12 processes in total; owl <= 16 only inside docker, e.g. ssh -q -o ControlMaster=no -o
  ControlPath=none owl 'cd /home/jihoon/competitions/quantumn/work; docker run --rm -u 1010:1012 -e HOME=/home/jihoon -e
  OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -v /home/jihoon:/home/jihoon -w <dir> --cpus=16
  fnc-build:22.04 /home/jihoon/competitions/quantumn/.venv/bin/python <script>' < /dev/null (owl has its own disk:
  rsync inputs there first, results back). Never use zebra for computation (its load is at its core count), tom, jerry, sunfish,
  faraday, dragon, Parrot or any GPU.
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q -o ControlMaster=no -o
  ControlPath=none <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>
<structured_output_contract>
Write REPORT.md (<= 100 lines: verdict; table of every priced circuit with L, A, J_tau, sha256 prefix, what moved;
verified vs inferred; files) and results.json (keyed by qasm sha256). Finalists go to cand/<name>.{qasm,json}.
Final answer: verdict line, best candidate (path, L, A, J_tau), what moved, verified vs inferred.
</structured_output_contract>
