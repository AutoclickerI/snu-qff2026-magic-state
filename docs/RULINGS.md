# Rulings

Jihoon's words behind standing decisions, verbatim, oldest first: a rule Jihoon confirmed, a change to
G0 or the ranking, an answer to an agent's question. One-time instructions are carried out, not
recorded. Ids are `R-<YYYYMMDD>-<n>`. Entries are never edited except to add "superseded by <id>"
(naming the clause when only part is superseded). An entry whose words turn out not to be Jihoon's is
deleted, and the change says so; git keeps it. A chosen question-tool label is Jihoon's word; the
question and option text are agent context.

Transcript `T` = `/home/jihoon/.claude/projects/-home-jihoon-competitions-quantumn/b847d206-5793-4080-bd90-5ce9cfd3f5dd.jsonl`.

## R-20261023-1 — 2026-10-23 14:35 KST — goal and submission rights
> I'm aiming to win 1st place. and I just registered. and I want you to submit as you want. and use codex rescue subagent for expansion work.

- Source: T:231
- Effect: G0 ([GOAL](GOAL.md)). Agents choose what and when to submit (GOAL "Decision rights"). The Codex
  clause is carried out as an instruction; whether it is a standing rule is an open question
  ([CONSTRAINTS](CONSTRAINTS.md) "Open questions").

## R-20261023-2 — 2026-10-23 14:45 KST — team
> 한성재팬티도둑

- Source: T:291. Answered which registered team is ours.
- Effect: team identity. The board later showed our entries under 초정밀모델제어학회쨩 and the server
  rejected the old name (2026-10-23 18:0x KST); see [RESOURCES](RESOURCES.md) "Inventory".

## R-20261023-3 — 2026-10-23 15:30 KST — who runs submissions
> you run yourself.

- Source: T:681. Answered how the agent should get the submission password.
- Effect: the agent runs submissions through `work/submit.py`. The password itself was given later
  (T:1727) and is deliberately not quoted here (CONSTRAINTS rule 8).

## R-20261023-4 — 2026-10-23 17:11 KST — solver-backed search
> Ok. doing everything in vibe is not a good idea. find if we have any other search/simulation method to get the good implementation more predictable way using solver.

- Source: T:2058
- Effect: subgoal G2 (predictable, solver- and simulation-backed search). Whether this is a standing
  rule is an open question.

## R-20261023-5 — 2026-10-23 17:55 KST — parallel push and fast iteration
> Ok. if anything can be done by parallel, do it altogether. especially, start 1 right now. target finishing it by today 23:59. use codex rescue for every possible lanes in parallel.

> and find method for the fast experiment and iteration.

- Source: T:2199, T:2207
- Effect: the 2026-10-23 23:59 KST milestone in [PLAN](PLAN.md); subgoal G2 includes the fast loop.
  The parallelism clauses are on the open-question list as possible rules.

## R-20261023-6 — 2026-10-23 19:45 KST — no blocking on one experiment
> can you do basically the parallel work? instead of blocking on one experiments?

- Source: T:3249
- Effect: carried out (experiments run in the background, decisions on completion signals). Proposed
  as a rule in the open questions.

## R-20261023-7 — 2026-10-23 19:54 KST — hosts
> you may use all permitted host in furiosa challenge. write those down to our resources.

- Source: T:3626
- Effect: the hosts permitted in `/home/jihoon/FuriosaNPUChallenge/docs/CONSTRAINTS.md` rule 13 are
  ours to use: dragon, faraday, hippo, jerry, owl, pegasus, sunfish, tom, plus zebra (R-20261023-8);
  never Parrot; never zebra GPU0. CONSTRAINTS rule 9 and RESOURCES "Inventory".

## R-20261023-8 — 2026-10-23 19:56 KST — zebra use and CPU cap
> "rule 13 is meant only for light commands (taskset/nice) and not heavy builds or checks" is not I intended. you may use zebra if needed.

> cap is CPU ~75%.

- Source: T:3698, T:3699. Answered the agent's statement that zebra was light-only.
- Effect: CONSTRAINTS rule 9: zebra may run heavy work; our CPU use stays at or below ~75% of a host.
- Confirmed: in the words (the cap is stated as a limit).
- Intention: inferred: the cap applies per host to our total use, on zebra and on the other hosts;
  asked 2026-10-23 whether it is meant for every host.
