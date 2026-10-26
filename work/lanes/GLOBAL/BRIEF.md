<task>
You run research lane GLOBAL of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F (lower is better). Working dir: /home/jihoon/competitions/quantumn/work/lanes/GLOBAL.
Read first: /home/jihoon/competitions/quantumn/AGENTS.md, docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md,
docs/reference/judge.md, and work/lanes/{R43,FLAG,EARLY,ACCBUY,TERM}/REPORT.md.

Goal: a circuit with exact all-orders loss L < tau - 5e-7, tau = L(v36h) = 3.815473322483099e-5, acceptance A >= 0.5002
(A(v36h) = 0.5016415049479505), judge-valid, obtained by creating space-time room next to the data at ticks 39-44 on the
real grid for (a) the two A-flag-gap helpers and (b) one or two late X-type stabilizer checks. Rank by
J_tau = A*(L - tau). Incumbent: work/lanes/MAIN/v36h.{qasm,json}; timeline work/lanes/R43/v36h.timeline.txt.

Measured prizes on v36h (all orders; off-grid phantom ancillas q36-39; builder room/gen.py, circuits and prices in room/):
- both flag-gap helpers (|+> helper, CX d->a at 44 on q10 and q21, MX at 45): 3.654534e-5 (-1.609e-6), A 0.49950
- late X check S12X (data 0,20,3,22 at ticks 40,43,41,42; ancilla RX 39, MX 44): 3.700478e-5 (-1.150e-6), A 0.50066
- both together: 3.544974e-5 (-2.705e-6, -7.1%), A 0.49853 (acceptance must be bought back: ACCBUY's rate is about
  1.6e-5 loss per unit of acceptance)
- other X checks alone 3.728-3.746e-5 (S123X, S13X, S1X, S3X, S23X, S2X), with both helpers 3.572-3.589e-5; Z checks gain
  <= 0.36e-6 or lose; blue-style XZ checks do not fit v36h's idle data slots.
- every data wait one tick shorter (R43): -0.684e-6; an inserted tick: +2.6e-6.

Why it is blocked today (each closes only the placement tested): in v36h no free cell touches flag data q10, q21 at 44,
and no free cells cover a stabilizer's support at 39-43. Free non-data cells next to data in v36h (recompute; my parse
may be off by one tick): t39 q11(->10), q14(->20); t40 q1(->0,7); t41 q1, q2(->3); t42 q1, q2, q11, q16(->10,22);
t43 q1, q2, q4(->10,3), q6(->0,7), q16; t44 none. Row 5 (cells 30-35) and cell 24 are idle until 39-44 (q30 is never
used); cells 23, 27, 29 until 32. R43's CP-SAT layout model (work/lanes/R43/layout.py, solve(helper=, check=, xcheck=),
logs in R43/lay/) found one helper at R44 with 4 moved roles and 10 hops (v36h has 6) and two helpers only at R45 (12
hops, 17 moved roles) or R46; nobody built or priced these, so "does not pay" is inferred. Known costs: a hop 0.1-1.0e-6,
a re-placed A encoder about +1.4e-6 (AENC next best), a fresh B/C synthesis about +0.7e-6 above r3, and about 3e-6 of
v36c -> v36h came from layout-bound gadgets and guards that a new layout must redo.

Approach, in order:
1. Cheapest realizations first, keeping v36h's prefix, A encoder, r3 and guards and moving as little as possible: a
   check as a short cat or chain over free cells; a helper made available by retiming, dropping or swapping one guard
   or one role; role swaps or block translations under which r3 and the A encoder carry over unchanged (cells free at
   the same ticks). Build each as a full circuit and price it exactly.
2. Then R43's model layouts (R44 one helper; R45/R46 two helpers; with check=/xcheck=) built into full circuits with
   the existing synthesizers (A: work/lanes/EXENC, AENC against actual releases; B/C: BFLAG synth_bc.py/lns3.py or BCX
   bcsynth.py/bclns.py on the new cells; guards: ACCBUY kstate.py/greedy.py; flag: FLAG flagenum.py), priced exactly,
   then repaired with INTEG2/ACCBUY greedy passes.
3. Buy acceptance back with ACCBUY's buyers if a winner sits below 0.5002.
</task>

<tools>
- Exact all-orders price (needs barriers over all used qubits, no FRAME/POSTSELECT):
  cd work/lanes/MAIN/sparse; OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 ../../../../.venv/bin/python
  sparse_walsh.py <path/stem without suffix> 72 canonical 16   (about 1-5 s; prints JSON with loss, acceptance)
- Circuits with qubits 36-39 (phantoms): the same command in work/lanes/ACCBUY/sparse40.
- Region counterfactuals: work/lanes/MAIN/sparse/region.py (spec format in circuit.md). Adjoint map of v36h:
  work/lanes/MAIN/sparse/v36h_adjoint_72.json.
- Judge check at 1e6 shots: work/fast_check.py (see docs/RESOURCES.md "Setup").
- Python is /home/jihoon/competitions/quantumn/.venv/bin/python.
</tools>

<completeness_contract>
Stop when a finalist exists (L < tau - 5e-7, A >= 0.5002, fast_check PASS at 1e6), or when every realization from steps 1
and 2 is built and priced and the best is >= tau. In the second case, name per family the cost that ate the prize
(hops, rebuilt block, lost guard, acceptance), with the measured numbers.
</completeness_contract>

<verification_loop>
Reproduce v36h first (3.815473322483099e-5, 0.5016415049479505) and the room/ prices before building anything. Every
claimed number comes from the evaluator on a saved circuit; record sha256 of each priced qasm.
</verification_loop>

<action_safety>
- Hosts: jerry <= 24 processes in total (ssh -q jerry '...' < /dev/null; sync with
  rsync -a --exclude .submit_credentials), zebra (local) <= 8 processes. Never use owl, tom, sunfish, hippo, faraday,
  dragon, Parrot or any GPU. Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1.
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- No submission, no git commit or push. Write only under work/lanes/GLOBAL; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Do not use spawn_agent or any sub-agent.
</action_safety>

<structured_output_contract>
Write REPORT.md (<= 100 lines: verdict; table of every priced circuit with L, A, J_tau, sha256 prefix, what moved;
verified vs inferred; files) and results.json (keyed by qasm sha256). Finalists go to cand/<name>.{qasm,json}.
Final answer: verdict line, best candidate (path, L, A, J_tau), what moved, verified vs inferred.
</structured_output_contract>
