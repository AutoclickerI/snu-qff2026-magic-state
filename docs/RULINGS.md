# Rulings

Jihoon's words behind current standing decisions, verbatim, oldest first. Ids are `R-<YYYYMMDD>-<n>`.
`T` = `/home/jihoon/.claude/projects/-home-jihoon-competitions-quantumn/b847d206-5793-4080-bd90-5ce9cfd3f5dd.jsonl`.

## R-20261023-1 — 2026-10-23 14:35 KST — goal and submissions
> I'm aiming to win 1st place. and I just registered. and I want you to submit as you want. and use codex rescue subagent for expansion work.

- Source: T:231
- Effect: G0; agents choose what and when to submit. The Codex clause is CONSTRAINTS rule 11
  (R-20261023-9).

## R-20261023-3 — 2026-10-23 15:30 KST — who runs submissions
> you run yourself.

- Source: T:681; answered how the agent gets the submission password.
- Effect: the agent submits through `work/submit.py` with `.submit_credentials` (CONSTRAINTS rule 8).

## R-20261023-4 — 2026-10-23 17:11 KST — solver-backed search
> Ok. doing everything in vibe is not a good idea. find if we have any other search/simulation method to get the good implementation more predictable way using solver.

- Source: T:2058
- Effect: G2.

## R-20261023-5 — 2026-10-23 17:55 KST — parallel push and fast iteration
> Ok. if anything can be done by parallel, do it altogether. especially, start 1 right now. target finishing it by today 23:59. use codex rescue for every possible lanes in parallel.

> and find method for the fast experiment and iteration.

- Source: T:2199, T:2207
- Effect: CONSTRAINTS rule 12 (parallel work); G2 covers the fast loop. The 23:59 target was for that day only.

## R-20261023-6 — 2026-10-23 19:45 KST — no blocking
> can you do basically the parallel work? instead of blocking on one experiments?

- Source: T:3249
- Effect: experiments run in the background, decisions on completion signals.

## R-20261023-7 — 2026-10-23 19:54 KST — hosts
> you may use all permitted host in furiosa challenge. write those down to our resources.

- Source: T:3626
- Effect: CONSTRAINTS rule 9 host list (from FuriosaNPUChallenge CONSTRAINTS 13); RESOURCES "Inventory".

## R-20261023-8 — 2026-10-23 19:56 KST — zebra and CPU cap
> "rule 13 is meant only for light commands (taskset/nice) and not heavy builds or checks" is not I intended. you may use zebra if needed.

> cap is CPU ~75%.

- Source: T:3698, T:3699; answered the agent's reading that zebra was light-only.
- Effect: CONSTRAINTS rule 9: zebra runs heavy work; our CPU use stays ≤ ~75% of a host.
- Confirmed: in the words.
- Intention: the cap is per host on every host (confirmed R-20261023-9).

## R-20261023-9 — 2026-10-23 20:11 KST — standing rules and per-host cap
> for all questions " Questions (also listed in docs/PLAN.md):", my answer is yes. and please use question feature. not ask in text.

- Source: T:4304; answered the agent's three questions: (1) make standing rules of Codex lanes for
  expansion work, running everything in parallel, and preferring solver-backed search; (2) does the ~75%
  CPU cap apply to every host; (3) fix FuriosaNPUChallenge CONSTRAINTS 13 (zebra light-only).
- Effect: CONSTRAINTS rules 11–13; rule 9 cap is per host on every host; (3) relayed to the Furiosa
  session (jihoon-a5), whose rule 13 already allows heavy zebra work. Questions go through the question
  tool (agent memory).
- Confirmed: in the words.

## R-20261023-10 — 2026-10-23 21:00 KST — seed-0 re-draws; ceremony
> Q: Seed-0 re-draws [reorder simultaneous gates: identical noise model, fresh seed-0 draw; pick the best of ~100] … Use it for our submissions? A: "Yes, use re-draws (Recommended)"

> Q: If we win, who attends the award ceremony in person on 2026-10-31 (Sat) 16:30? A: "A teammate will attend"

- Source: T:4795 (question-tool answers).
- Effect: CONSTRAINTS boundary case (re-draws); submissions are the best seed-0 draw of the best
  true-mean circuit, reported with the true mean. Rule 10 is covered by a teammate (name not given).

## R-20261024-1 — 2026-10-24 00:40 KST — open chat; asking organizers
> Q: The contest's KakaoTalk open chat is where 'all key announcements' go … Are you in it, and has anything been announced since Oct 22? A: "In it, nothing relevant"

> Q: Should someone ask the organizers (Office Hour Sun 10/25 or the open chat) how the final ranking is computed? A: "Don't ask"

- Source: this session (question-tool answers).
- Effect: no announcement changes rules, judge or scoring as of 2026-10-24 00:40; nobody asks the
  organizers about the ranking or re-draws; the written rules stand (ranking = official seed-0 score).

## R-20261024-2 — 2026-10-24 02:50 KST — Codex-only workers
> "don't fall back to sonnet worker. just try to assign only to codex. keep current workers running now, but take that policy if you assign work to next workers."

- Source: this session.
- Effect: CONSTRAINTS rule 11: every new worker is a Codex lane, with no fallback to Sonnet or any other
  model; a Codex job that fails is relaunched on Codex. The Sonnet lanes already running (ST_BC, ST_TP,
  PARITY) finish as they are.

## Dropped agent rules (do not reintroduce)

| Rule an agent introduced | Dropped | Match |
|---|---|---|
| A candidate must have fault_scan c1 == 0 (or < 1e-12) to be eligible | 2026-10-23: the judge does not check c1 | `c1 *(==\|<) *(0\|1e-12).*eligib` |
| Resubmit only when the 3-s.f. key improves | 2026-10-23: the board keeps only the best entry | `[Rr]esubmit only when` |
| Each lane may use at most 8 CPU processes | 2026-10-23: rule 9 (~75% per host) is the limit | `at most (8\|eight) CPU` |
| zebra is for light commands only, no heavy builds or checks | 2026-10-23: not intended (R-20261023-8) | `zebra.{0,20}light commands only` |
