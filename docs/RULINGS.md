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

## R-20261024-3 — 2026-10-24 02:20 KST — goal 1e-5
> "Ok. with those, set up the project goal and work until you reach the final goal. set the goal to 1e-5. and go there. be as close as possible."

- Source: this session, after the report that 1e-5 lies below the judge-noise floor (1.116e-5).
- Effect: GOAL G0 is now "official 1-F of 1e-5, or as close as possible, by the deadline"; work continues
  without stopping until the deadline or the floor.

## R-20261024-4 — 2026-10-24 02:57 KST — acceptance is only a gate
> "lower acceptance is fine if it pass the leaderboard submission. do not wrongly target to optimize anything. compare our budget and performance. higher performance wins. acceptance doesn't affect our rank if it pass the hard gate."

- Source: this session, after the agent dismissed a scheduled v14 partly for acceptance 0.521 and briefed a lane to keep
  exp(-A1) >= 0.52.
- Effect: CONSTRAINTS boundary case under rule 3: rank by 1-F alone; acceptance headroom above 0.5 is budget to spend on
  lower 1-F, with no margin kept beyond verification.

## R-20261024-5 — 2026-10-24 03:12 KST — CPU cap reading
> Q: "The CPU cap \"~75%\": does it limit only OUR processes to 75% of each host's cores, or the host's TOTAL load (other users included)? ..." A: "Ours ≤75%, total ≤100% (Recommended)"

- Source: question tool, this session.
- Effect: CONSTRAINTS rule 9: our processes use at most ~75% of each host's cores, and we never push a host's total
  load above its core count.

## R-20261024-6 — 2026-10-24 21:45 KST — ST_BC disposed
> "is that run are far different from our current scope? if so, dispose them."

- Source: this session (question-tool answer to: stop ST_BC's 35 sat6.py jobs, kept running by the
  2026-10-24 11:20 answer "Keep ST_BC running"?).
- Effect: checked: sat6.py synthesizes the old rank-6 joint B+C contract (two clean |0_L⟩, < 82 CX) that
  v30f's 57-CX correlated rank-3 resource replaced, so it is out of scope. All ST_BC jobs and its collector
  loops were killed by PID at 21:45; outputs stay in `work/lanes/ST_BC`. The hold is lifted.

## R-20261025-1 — 2026-10-25 03:58 KST — Claude workers while Codex is down
> Q: "Should Claude subagents continue while Codex is down? ..." A: "Keep Claude (Recommended)" — option text: "Rule 11 is suspended while Codex is down. I keep the three subagents and add Claude lanes where they pay off (e.g. the earlier round, the mid-preparation B flag). I switch back to Codex when it answers again."
> Q: "Can you restore Codex capacity? ..." A: "No, go without it" — "Proceed on Claude and scripts until the deadline."

- Source: this session, question-tool answers after the Hermes proxy returned 429 with a ~6-day retry on every model.
- Effect: CONSTRAINTS rule 11 is suspended while Codex does not answer; new workers are Claude subagents.


## R-20261025-2 — 2026-10-25 14:47 KST — Codex reported back, still refused locally
> "codex subagents are back. use codex subagents from now on again."
> Q: "Codex is still blocked on this machine ... 429 local_auth_cap with retry_after ≈ 475,000 s ... How should I proceed?" A: "Claude until Codex admits (Recommended)" — option text: "Keep the running Claude lanes (BCX nearly done, BUNDLE just started); test the proxy before each new lane and switch to Codex as soon as it answers."

- Source: this session; the first message restates CONSTRAINTS rule 11 (Codex first), not a new rule.
- Effect: R-20261025-1 continues until a proxy probe (RESOURCES "Codex") admits Codex; then new workers go to Codex.

## R-20261025-3 — 2026-10-25 16:41 KST — no zip archives in work/
> "and read my feedbacks previously handed off and digest it. don't keep zip archive in works directory."
> Q: "Should this become a standing rule for future reviewer handoffs? I recommend yes: unpack each zip into a new spec/reviewerN folder, commit what we use, then delete the zip." A: "Yes, standing rule (Recommended)"

- Confirmed: "Yes, standing rule (Recommended)" (question-tool answer, 16:41 KST).
- Source: this session (message 15:51 KST).
- Effect: CONSTRAINTS rule 14. The digest itself was a one-time instruction (DIGEST lane, PLAN P93/P94).

## R-20261026-1 — 2026-10-26 14:00 KST — redesign lane now
> "so what larger gain can we get from now? what is our limit and how can we approach there?"
> Q: "How much should I bet on a from-scratch redesign (new layout and starting stage built around a cheaper final check) versus locking in the steady gains?" A: "Redesign lane now"

- Source: this session (question-tool answer).
- Effect: one-time decision, not a rule: PLAN P116 (REDESIGN lane started 2026-10-26 on jerry, racing cores ceded),
  alongside racing, repair lanes and WAITCUT.

## R-20261026-2 — 2026-10-26 21:40 KST — target 2e-5; re-audit the floor
> "we need large jump. target 2e-5. I believe we can reach there."
> Q: "A true mean of 2e-5 is below the audited floor ... Which target should drive the lanes' go/stop decisions?" A: "Re-audit the floor"

- Source: this session (message and question-tool answer).
- Effect: one-time decision: an independent adversarial re-audit of the 2.189e-5 floor (PLAN P121, lane FLOOR). G0 is
  unchanged ("1e-5, or as close as possible"); lanes keep reachable go/stop gates until the audit reports.

## R-20261027-1 — 2026-10-27 23:00 KST — hourly race stopped
> "it just pushed to quantumn repo in 10 minutes before. see what is running in background. I want to kill all stale sessions."
> Q: "The quantumn push came from receipts/draw_loop.sh, an orphan of ended session b847d206. It isn't a stray process: PLAN.md names it as the hourly seed-0 race that should run until submissions close (10-30 12:00 KST). ... What should I do with it?" A: "Stop it now"

- Source: `/home/jihoon/.claude/projects/-home-jihoon/f989403d-d772-4c20-a29f-4ad22dbf8b1c.jsonl` (message and
  question-tool answer; the agent recommended keeping it).
- Effect: one-time decision, not a rule: at 23:01 the loop, its v37j_h2723 promote and cut, and the race workers on
  owl, jerry, hippo, sunfish, tom and zebra were killed before the hour's pick. PLAN parks the hourly race.

## R-20261103-1 — 2026-11-03 22:02 KST — public repo, renamed, with its full history
> update the "https://github.com/AutoclickerI/quantumn" and open to public in the same way. and we won the 2nd place. so make the repo like that as well. make anyone can understand what it is.
> and polish repo name. I think the repo name is bad.

- Source: Claude Code session `0045ab8f-54dd-41a4-8c54-fd714e9ef389`. Question-tool answers: "Publish as-is" (the
  history, including the team's earlier name) and "English (Recommended)" for the README.
- Effect: the repo is public as github.com/AutoclickerI/snu-qff2026-magic-state with its full history; README.md is a
  plain-language front door for the 2nd-place result; the research logs stay as they were.

## Dropped agent rules (do not reintroduce)

| Rule an agent introduced | Dropped | Match |
|---|---|---|
| A candidate must have fault_scan c1 == 0 (or < 1e-12) to be eligible | 2026-10-23: the judge does not check c1 | `c1 *(==\|<) *(0\|1e-12).*eligib` |
| Resubmit only when the 3-s.f. key improves | 2026-10-23: the board keeps only the best entry | `[Rr]esubmit only when` |
| Each lane may use at most 8 CPU processes | 2026-10-23: rule 9 (~75% per host) is the limit | `at most (8\|eight) CPU` |
| zebra is for light commands only, no heavy builds or checks | 2026-10-23: not intended (R-20261023-8) | `zebra.{0,20}light commands only` |
| Keep acceptance (exp(-A1)) at or above a margin such as 0.52 | 2026-10-24: only the 0.5 gate counts (R-20261024-4) | `exp\(-A1\) *>= *0\.5[1-9]` |
