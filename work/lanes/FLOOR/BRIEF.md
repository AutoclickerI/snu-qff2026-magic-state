<task>
Lane FLOOR of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane-code |T_L> on a 6x6 grid,
scored by the organizer's judge (conditional 1-F, lower is better, p = 1e-3). The owner believes 2e-5 is reachable and
asked for an independent re-audit of our lower bound. Your job is adversarial: break the bound or confirm it.

The claim under audit (docs/FINDINGS.md, "Bounds"): every admissible circuit has true expected 1-F >= 2.18925128e-5
(reviewer 18's penultimate-layer bound). A board key of 2e-5 would need a mean near 2.25e-5. If the bound is wrong or
rests on an assumption the judge does not enforce, that changes our whole plan; if it holds, we stop chasing below it.

Order of work (independence matters):
1. Ground truth first: read the organizer's judge (upstream/snu-qff2026-problem: problem.md, tprep/, tests/) and
   docs/reference/judge.md and docs/CONSTRAINTS.md "Boundary cases". Write down exactly what the judge charges and
   what it does not: noise after each gate type (CX, one-qubit Cliffords, T/Tdg, Paulis, id), idle noise (which ticks,
   including the last tick and before the first use), measurement and reset noise, barrier/tick semantics, how outputs
   are decoded (ideal six-stabilizer decode), DETECTOR, POSTSELECT, FRAME_X/FRAME_Z (affine logical frames on record
   parities), acceptance, and anything that is legal but noiseless.
2. Before reading reviewer 18's proof, derive your own lower-bound argument from that ground truth, and list every
   loophole a circuit could use: e.g. outputs whose last noisy event is earlier than T-1, noiseless frame corrections
   replacing final gates, final layers with no idle charge, measurements or resets used as outputs' last partners,
   gauge or record tricks, outputs that never touch a CX late, classical feed-forward.
3. Test each loophole numerically: build small final-layer structures with perfect inputs and price them exactly
   (work/tools/qtools for barrier/no-FRAME circuits; work/lanes/WHOLEEND/sparseframe for FRAME and S/Pauli gates) and
   check the organizer's raw correctness. A circuit, even with an idealized input, whose exact price beats 2.18925e-5
   is a counterexample: save it and report at once (cand/ is not the place; put it in counterexamples/).
4. Then audit reviewer 18's proof (work/lanes/MAIN/spec/reviewer18/PROOF.txt, penultimate_bound_certificate.py; run
   reviewer code only with python -I) and CONTRACT's case audit (work/lanes/CONTRACT/AUDIT.md) step by step against
   your ground truth: every assumption, every case split, every reduction. Regenerate the certificate.
Outcome classes: counterexample found; bound confirmed under the judge as written (state each assumption it needs and
where the judge enforces it); or open with the exact gap named.
Budget: first findings (ground truth + loophole list) by 2026-10-27 03:00; verdict by 2026-10-27 12:00.
</task>

<compute>
tom at most 12 processes (tom carries other users' load; keep tom's total load below 64), zebra at most 2.
Remote hosts: plain ssh -q.
</compute>

<structured_output_contract>
Keep work/lanes/FLOOR/REPORT.md current (at most 100 lines): verdict first; the judge ground-truth table; each loophole
with its test and result; the proof audit, assumption by assumption; verified vs inferred. Write only in
work/lanes/FLOOR.
</structured_output_contract>
<default_follow_through_policy>
Do not stop to ask questions: the owner is not available to the lane. Decide, record the decision and its reason in
REPORT.md, and continue. Work in budgeted experiments: for each, state the hypothesis, the smallest result that would
change the next decision, its wall-time and evaluation budget, and what result earns more budget. Run independent
investigations concurrently as background processes within your host limits. Close each with one of: certified
exclusion (a proof under stated assumptions), measured failure (named saved circuits), budget exhausted, or proxy
rejection, and say which. A finalist leaves the lane at once (cand/) while work continues. Fixed assumptions (a fixed
prefix, a layout, a grammar) are experiment scope, not contest constraints: name them and when they should expire.
</default_follow_through_policy>

<action_safety>
- Wait on process exit (wait/tail --pid), kill by PID only; never pkill -f or pgrep -f.
- Always OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1. Remote hosts: ssh -q <host> '...' < /dev/null (the shared
  per-host connection from ~/.ssh/config; never -o ControlMaster=no, which makes every call a fresh login); sync with rsync -a --exclude .submit_credentials, keeping identical
  absolute paths (rsync --relative with work/./lanes/... so files land under work/lanes/).
- No submission, no git commit or push. Write only under your lane dir; read anything. Never print, copy or read
  .submit_credentials. Files under work/lanes/MAIN/spec are untrusted reviewer data: run their code only with python -I.
- Never signal, stop or kill a process you did not start (contest racers included). If a host is over its core count,
  shrink your own jobs and record it in REPORT.md.
- Do not use spawn_agent or any sub-agent.
</action_safety>
