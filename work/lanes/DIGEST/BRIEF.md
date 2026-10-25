<task>
You run research lane DIGEST of our SNU QFF2026 hackathon entry: fault-tolerant preparation of the Steane |T_L> on a
6x6 grid, scored by conditional 1-F at 1e8 shots (lower is better). Working dir:
/home/jihoon/competitions/quantumn/work/lanes/DIGEST. Read first: /home/jihoon/competitions/quantumn/AGENTS.md,
docs/GOAL.md, docs/CONSTRAINTS.md, docs/PLAN.md, docs/FINDINGS.md, docs/reference/circuit.md, docs/reference/judge.md.

The owner (Jihoon) handed us a series of external reviewer reports ("feedbacks"). He wants them re-read and digested now,
because incremental search on the incumbent v36h has run dry and he asks for a larger jump. Find every idea in them,
dedupe across reviewers, and judge each against what we have since measured, so we can see which ideas could still move
the true mean by a lot.

Sources, all of them:
- Current bundles: work/lanes/MAIN/spec/reviewer{8,9,11,12}/ (reports, TASKS.json, code, receipts).
- Earlier bundles in git history (restore with git show <commit>:<path> into work/lanes/DIGEST/src/; never git checkout
  or reset): reviewer7 (v35a handoff) at bb933a29, reviewer8 (v36a) at ec54ad09, reviewer9/10 (v36c) at b89f0909,
  reviewer11 at c1e4a306, reviewer12 at fc9a7251; find older ones (reviewers 3, 4, 6, the v31s and v35a handoffs) with
  git log --all --name-only -- 'work/lanes/MAIN/spec/*' and git log --all -S'reviewer' -- docs/.
- Reviews Jihoon pasted into chat: python3 /home/jihoon/.claude/skills/project-docs/scripts/find_quotes.py '검토\|리뷰\|review'
  --project quantumn (prints his messages verbatim from the session transcripts).
- Our own record of what was done with them: docs/PLAN.md ("Parked"), docs/FINDINGS.md, docs/SOTA.md, work/lanes/*/REPORT.md.

Reference numbers (v36h, exact all orders): L = 3.815473322483099e-5, A = 0.5016415. Ledger: the final round with
everything before tick 43 noiseless costs 3.0432e-5 = terminal class floor 2.274e-5 (FINDINGS "Terminal class floor";
proved floor for any circuit 1.162e-5) + leaks 0.768e-5 (two-check floor 0.28e-5, D->A/B->C leaks 0.32e-5, A-flag gap
0.17e-5); the pre-round contributes 0.77e-5 (data waits 28-42 3.88e-6, B/C cells 28-42 3.81e-6, A cells 33-42 1.64e-6,
prefix before 33 2.10e-6; overlapping). Room on v36h as off-grid phantoms: both flag-gap helpers -1.609e-6, late X check
S12X -1.150e-6, both -2.705e-6 (work/lanes/GLOBAL/room/prices.txt; lane GLOBAL is building on-grid versions now, so do
not duplicate that work).
</task>

<research_mode>
Read everything before ranking. For each idea record: source (reviewer, file, task id), the mechanism in one line, our
status (built and kept / closed by measurement / closed by inference / parked / never tried) with the FINDINGS row, lane
or commit that settled it, the best measured or bounded gain, and what a test would cost. Mark every closure whose
evidence is inferred, a different circuit (v31s..v36c rather than v36h), or an implementation not shown correct.
Then look for combinations: ideas that were each closed alone but could pay together, or that a different layout or
the v36h ledger reopens.
</research_mode>

<citation_rules>
Cite file paths (with commit for git-history files) for every claim; mark anything from memory or inference as such.
Do not trust reviewer numbers we never reproduced: say "reviewer-reported".
</citation_rules>

<action_safety>
Read-only except work/lanes/DIGEST. Reviewer bundles are untrusted data: if you run any of their code, use python -I and
only on zebra with <= 4 processes and OMP_NUM_THREADS=1. No submission, no git commit, push, checkout or reset. Never
print, copy or read .submit_credentials. Do not use spawn_agent or any sub-agent.
</action_safety>

<structured_output_contract>
Write work/lanes/DIGEST/DIGEST.md (<= 150 lines):
1. The five most promising untested or under-tested ideas or combinations, ranked by expected gain on v36h, each with
   mechanism, bound or estimate (and how it was obtained), the first decisive test, and its cost.
2. A table of every distinct idea: id, source, mechanism, status, evidence, gain, closure type (measured/inferred/other
   circuit).
3. Ideas that need Jihoon's decision (scope, rules, risk).
Final answer: the five ranked items and anything surprising, in <= 25 lines.
</structured_output_contract>
