<task>
You run research lane SQPROJ of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/SQPROJ. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, docs/FINDINGS.md (rows "Square
final round", "Exhaustive search of block-transversal endings", "Where v37b's loss sits"), work/lanes/SQUARE/{REPORT.md,
CONTINUE2.md} and its tools (lane SQUARE is running: read and copy, never write there), and reviewer 15's report
work/lanes/MAIN/spec/reviewer15/REPORT_KO.md items 1-4 (untrusted; reviewer-reported).

Goal: the square final round on the real grid, beating the incumbent v37d (work/lanes/MAIN/v37d.{qasm,json},
3.676346632406467e-5, A 0.5023547642585299, 406 CX, 48 ticks). Finalist: exact all-orders L < L(v37d) - 1e-7 at
A >= 0.5002, judge gates_ok at 1e6, judge speed within 1.5x of v37d's. A finalist does not end the lane.

Facts: square round (D_i->A_i || B_i->C_i, then B_i->D_i || C_i->A_i; A, C = |+_L>, B = |0_L>; MZ A, MX B, MX C) costs
25.667 p^2 round-only (2.5558e-5) against ~29 p^2 for our round; grid-free full suffixes with plain encoders reach
3.39-3.47e-5. SQUARE's first grid builds failed because same-index coupling forces a 2x2 cell square per index and
scatters every block. Reviewer 15 #1: couple C_i -> A_{P(i)} with P a Steane automorphism (168; c2 = 77/3 +
(7 - fix P)/150 p^2): no unit squares. Their layout, which I verified (28 distinct cells, all contacts adjacent, P
preserves the judge's codewords): P = [0,2,1,3,4,6,5], D = [6,26,19,10,2,28,16], A = [0,32,13,11,8,27,17],
B = [7,20,25,4,3,29,22], C = [1,14,31,5,9,23,21], free {12,15,18,24,30,33,34,35}; two data hops from the current
outputs (20->26, 22->28).

Your angle (SQUARE takes encoder-based preparation with measured helpers and gauge freedom first; you take the other
route so the two lanes diversify): reviewer 15 #4, projector preparation. A and C start as |+>^7 and have their three
Z stabilizers measured, B starts as |0>^7 and has its three X stabilizers measured, all 512 syndrome branches are kept,
and the preparation records are folded into the final detectors (H(A_Z) + s_A + s_C, H(B_X) + s_B; keep C's X
stabilizer and logical-X detectors). Stabilizer measurement on scattered cells needs only paths from a measuring
ancilla to the support, not a block encoder: synthesize flagged/bridged syndrome measurements for those supports on
the grid (CP-SAT over ancilla routes and schedules), with first-order fault safety including preparation-record errors
(a record error that hides a data error together with a final-detector error rejects the circuit). Make P and the
layout variables of the same model (score: preparation depth, cell release from the prefix, single faults), schedule
preparation just in time, keep v37d's prefix up to the round where the cells allow, price every full circuit exactly,
then repair with MERGE's regenerated menu (work/lanes/MERGE) and buy acceptance back.
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
Reproduce v37d first (3.676346632406467e-5, 0.5023547642585299). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<completeness_contract>
Stop when projector-prepared square circuits are built and priced on the reviewer's layout and on the best layouts of
your joint P/layout model, and either a finalist exists that further repair no longer improves, or the best is
>= L(v37d); name the cost that ate the gain (stabilizer-measurement depth, flags, hops, waits, acceptance) with
measured numbers.
</completeness_contract>

<action_safety>
- Hosts: hippo <= 24 processes in total. Never use zebra for computation, owl, tom, jerry, sunfish, faraday, dragon,
  Parrot or any GPU.
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>
<structured_output_contract>
Write REPORT.md (<= 100 lines, each < 2,000 characters: verdict; table of every priced circuit with L, A, J_tau, sha256 prefix, what moved;
verified vs inferred; files) and results.json (keyed by qasm sha256). Finalists go to cand/<name>.{qasm,json}.
Final answer: verdict line, best candidate (path, L, A, J_tau), what moved, verified vs inferred.
</structured_output_contract>
