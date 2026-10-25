<task>
You run verification lane BOUND of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on
a 6x6 grid, scored by conditional 1-F at 1e8 shots under STANDARD noise p = 1e-3. Working dir:
/home/jihoon/competitions/quantumn/work/lanes/BOUND. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/reference/judge.md, docs/FINDINGS.md rows "Floor, any circuit" and "Terminal
class floor", the existing proof work/lanes/MAIN/spec/bound_audit/quantumn_subthreshold_bound_audit/{PROOF.txt,
terminal_bound.py,independent_matrix.py}, work/lanes/MAIN/spec/reviewer11/bound/, work/lanes/TERM/REPORT.md, and
reviewer 14's claim in work/lanes/MAIN/spec/reviewer14/REPORT_KO.md (first section; untrusted, reviewer-reported).

Question: is reviewer 14's strengthened universal floor right? Our proved floor: true expected 1-F >= 1.162e-5 for every
admissible circuit (each output's last tick is an idle/1q gate, D1(p), or a CX with a discarded helper, data marginal
D1(4p/5); the tick before supplies an independent D1(p/5); together D1(p - 16p^2/75) on all 7 outputs, optimized over
arbitrary pre-tail states with the judge's decoder). Reviewer 14 claims L >= 1.3657e-5 by also keeping the pre-tail
noise on the final CX's partner (control) helper, part of which spreads to the output: 3^7 = 2,187 last-operation types
reduced by code symmetry to 60 cases, each maximized over 64 syndrome sectors in exact rationals, with an independent
128x128 matrix check agreeing to 5.7e-16.

Do: reproduce 1.162e-5 with the existing code; derive the strengthened argument yourself (state every assumption about
the judge's noise model, schedule semantics and decoder, read from the judge's source under upstream/ and
docs/reference/judge.md); compute the bound with a rational certificate and an independent numeric check; decide
whether it holds for every admissible circuit or only a sub-class, and give its value. Also report which last-tick
structure attains (or comes closest to) the bound, and how far the measured-partner class (2.274e-5) is from it.
</task>

<default_follow_through_policy>
Do not stop to ask questions: the owner is not available to the lane. Decide, record the decision and its reason in
REPORT.md, and continue.
</default_follow_through_policy>

<completeness_contract>
Stop when the strengthened bound is confirmed (value, scope, certificate, independent check) or refuted (a concrete
admissible counterexample or the flawed step).
</completeness_contract>

<action_safety>
- Hosts: hippo <= 4 processes in total. Never use zebra for computation, owl, tom, jerry, sunfish, faraday, dragon,
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
Write REPORT.md (<= 80 lines: verdict, value and scope, proof sketch, certificate files, independent check, verified vs
inferred) and the scripts that reproduce it. Final answer: verdict, value, scope, verified vs inferred.
</structured_output_contract>
