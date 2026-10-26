<task>
You run research lane COMPLETE of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/COMPLETE. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/circuit.md, docs/reference/judge.md, docs/FINDINGS.md,
work/lanes/DIGEST/DIGEST.md (item 1), work/lanes/{EARLY,R43,FRESH}/REPORT*.md, work/lanes/GLOBAL/CHECKPOINT.md (lane
GLOBAL is running; read, do not write), and reviewer 12's TASKS.json #2-#4 (work/lanes/MAIN/spec/reviewer12/).

Goal: a circuit with exact all-orders loss L < tau - 3e-7, tau = L(v36k) = 3.789826092701952e-5, acceptance
A >= 0.5002, judge-valid, obtained by redesigning how the 15-T phase network ends (up to about tick 28) so that cells
next to the data and the A/B/C cells free earlier. Rank by J_tau = A*(L - tau). Incumbent:
work/lanes/MAIN/v36k.{qasm,json} (v36i + 35 local edits, listed in the json "source").

Why: on v36h the pre-round costs 7.72e-6 above the round alone: data waits 28-42 3.88e-6, B/C cells 28-42 3.81e-6,
A cells 33-42 1.64e-6, prefix before 33 2.10e-6 (noiseless-region counterfactuals, overlapping). Every data wait one
tick shorter is worth -0.684e-6 and an inserted tick costs +2.6e-6; room for the two A-flag-gap helpers and a late X
check is worth -2.7e-6 as off-grid phantoms, but lane GLOBAL's on-grid builds so far lose to rebuild costs (best
3.841e-5 on its R46 layout). The phase network's routing CXs are fully reversed (TREP2's network(), in git history:
git log --all -- 'work/lanes/TREP2/*'); reviewer 12 #2 proposes synthesizing only the Clifford completion the target
state needs, with output placement free. The old global models (ST1/FRESH) used independent A/B/C encoders and cannot
express r3 (FRESH/REPORT_prior_architecture.md); EARLY closed fixed-prefix placements only; ST2's pop36_search.py drops
slot-opening prefixes whose fixed-suffix score loses (reviewer 12 #4). The prefix's own noise is cheap (summed
per-channel removal gains 0.4e-6 for ticks <= 12 and 1.1e-6 for 13-22, MAIN/sparse/v36h_adjoint_72.json): the prize is
what an earlier release enables downstream.

Approach, in order:
1. A fixed-variable model that round-trips v36k exactly (roles, records, guards, r3, A encoder), so every change is
   measured against the incumbent, not against a model artifact.
2. Open one 4-6-wire completion window at the end of the phase network: synthesize state-specific completions with free
   output placement; archive 20-50 distinct release profiles (cell x release tick near the data and the A/B/C cells),
   not only the best fixed-suffix score.
3. For the most promising profiles build complete circuits downstream: A/B/C preparation and the round moved earlier,
   shorter data waits, or room for GLOBAL's helpers/checks; re-synthesize moved blocks with the existing tools (A:
   EXENC/AENC/APROC; B/C: BCX bcsynth.py/bclns.py, BFLAG synth_bc.py; guards: ACCBUY kstate.py/greedy.py, GUARDNET),
   price exactly, polish, buy acceptance back if needed.
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
Reproduce v36k first (3.789826092701952e-5, 0.5010395982258441). Every claimed number comes from the evaluator on a
saved circuit; record the sha256 of each priced qasm. Run fast_check on each finalist.
</verification_loop>

<completeness_contract>
Stop when steps 1-3 are built and priced for at least three release profiles and either a finalist exists that further
polish no longer improves, or the best is >= tau; then name per family the cost that ate the gain (rebuilt block, hops,
lost guard, acceptance) with measured numbers.
</completeness_contract>

<action_safety>
- Hosts: tom <= 24 processes in total, zebra (local) <= 4. Never use owl, jerry, hippo, sunfish, faraday, dragon,
  Parrot or any GPU.
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null; sync with rsync -a --exclude .submit_credentials, keeping identical
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
