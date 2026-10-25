<task>
You run research lane PREPFREE of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on
a 6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/PREPFREE. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, docs/FINDINGS.md (rows on r3,
BCX, AENC, APROC, AJOINT, GLOBAL's B/C, "Where v37b's loss sits"), reviewer 15's report
work/lanes/MAIN/spec/reviewer15/REPORT_KO.md items 2-4 (untrusted; reviewer-reported), and the incumbent
work/lanes/MAIN/v37c.{qasm,json} (3.6904034715818095e-5, A 0.5057191647109531, 400 CX, 48 ticks; R46 layout, COMPLETE's
R45 phase-network end, GLOBAL's 65-CX-class B/C core, the 11-CX A encoder, guards, POLISH/MERGE edits).

Goal: lower v37c's loss by re-synthesizing its A and B/C preparations under the weakest contract its round actually
needs. Finalist: exact all-orders L < L(v37c) - 5e-8 at A >= 0.5002, judge gates_ok at 1e6, judge speed within 1.5x of
v37c's. A finalist does not end the lane. Rank by J = A*(L - L(v37c)).

Why: on v37b the ops before the round (ticks 30-45) cost about 0.7e-5 and noiseless B/C gates alone were worth 3.8-4.7e-6
on our layouts, yet every synthesizer we have (EXENC/AENC for A, BCX bcsynth/bclns and GLOBAL's warm_bc for B/C)
targets an exact pure state and returns every helper to |0> with reverse CX chains. Reviewer 15 shows both are stronger
than the function needs:
(a) Measured helpers: a preparation leaving sum_u |Gu>_block |Ku>_helper may MX the helpers; the block keeps a known
    Pauli byproduct Z_e with G^T e = K^T m. When that byproduct only flips read bits (never reaches the data), fold it
    into the detectors instead of uncomputing (a clean helper path of length l: 2l-1 CX -> l CX + l-1 MX).
(b) Subspace targets: compute, for v37c's own round, the stabilizer subspace of the A/B/C resource that the round's
    correctness and detectors need (for the square round it is 18 generators on 21 qubits with 3 gauge qubits free);
    let the gauge qubits be mixed or entangled with helpers, or fix gauge-X to add deterministic detectors on bits
    already read. Warning: the naive aggressive completion has one native fault giving an undetected Z0Z6 on the data;
    synthesize for fault safety, never just weaken the target.
(c) Projector preparation: start from product states, measure the needed stabilizers, keep all syndrome branches and
    fold the preparation records into the final detectors.

Approach: derive v37c's A and B/C contracts exactly (round-trip v37c first); for each block, synthesize preparations
under (a), (b), (c) on its present cells and release times (CP-SAT with the native schedule, first-order fault safety
as a hard constraint, records and detectors explicit); price every full circuit in all orders; repair with MERGE's
regenerated menu and buy acceptance back as needed.
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
Reproduce v37c first (3.6904034715818095e-5, 0.5057191647109531). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<completeness_contract>
Stop when (a), (b) and (c) are each built and priced for A and for B/C on v37c, and either a finalist exists that
further repair no longer improves, or the best is >= L(v37c); name the cost that ate each gain with measured numbers.
</completeness_contract>

<action_safety>
- Hosts: sunfish <= 12 processes in total. Never use zebra for computation, owl, tom, jerry, hippo, faraday, dragon,
  Parrot or any GPU.
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q -o ControlMaster=no -o
  ControlPath=none <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
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
