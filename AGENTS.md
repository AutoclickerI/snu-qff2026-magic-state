# AGENTS

Our entry in the SNU Qiskit Fall Fest 2026 hackathon: fault-tolerant preparation of the Steane-code
|T_L⟩ on a 6×6 grid, scored by the organizers' judge. Owner: Jihoon.

**Before any work, read [docs/GOAL.md](docs/GOAL.md) and [docs/CONSTRAINTS.md](docs/CONSTRAINTS.md) in
full.** Everything here serves G0 in GOAL.

## Files

| File | Owns |
|---|---|
| [GOAL](docs/GOAL.md) | G0, ranked subgoals, decision rights, glossary |
| [CONSTRAINTS](docs/CONSTRAINTS.md) | hard limits, Jihoon's rules, boundary cases, not-constraints, open questions |
| [RULINGS](docs/RULINGS.md) | Jihoon's words behind standing decisions |
| [PLAN](docs/PLAN.md) | status, critical path and the ranked queue |
| [RESOURCES](docs/RESOURCES.md) | setup, everything usable, headroom |
| [SOTA](docs/SOTA.md) · [FINDINGS](docs/FINDINGS.md) | baseline and results · measurements, closed recipes, failures |

On demand: [docs/reference/judge.md](docs/reference/judge.md) before reasoning about scores, noise or
validity; [docs/reference/circuit.md](docs/reference/circuit.md) before changing the circuit or its
search tools. The contest text itself is `upstream/snu-qff2026-problem/problem.md`.

Update each fact at its owner file and link elsewhere; never restate a rule. Replace superseded text in
place and delete what is stale or finished; history is git.

## Precedence

Hard limits > G0 > Jihoon's project rules > this file's practice. Between subgoals, the higher rank
wins. Anything not forbidden is permitted if it serves G0.

## Jihoon's words and rule changes

- Jihoon is human and can be wrong. Treat what Jihoon says as evidence of intent: infer the intention,
  and ask for the details you need.
- Instructions are one-time unless Jihoon confirms a rule. When Jihoon's words sound standing ("from
  now on", "always", "never"), ask "Add this as a rule?" and add it only on a yes; record the words and
  the yes in RULINGS and the rule in CONSTRAINTS in the same change. Either way, carry the instruction
  out this time. Words that say rule or permanent ("make this a rule") and limits quoted from an
  external source are recorded without asking. Ask before removing or changing any other rule. Never
  set or unset a rule silently.
- A rule with no owner words behind it (check with `find_quotes.py` in the project-docs skill) and no
  external source that does not clearly serve G0 is removed and listed under "Not constraints". A rule
  of Jihoon's that looks ritual for G0 is proposed for removal with the reason; it goes only on a yes.
  Hard limits stay.
- When a new instruction contradicts earlier words, the goal tree or CONSTRAINTS, take the side that
  serves performance within the hard limits, act, and tell Jihoon what conflicted and why. Say so if you
  think Jihoon is wrong.
- An exception Jihoon allows covers that case only. A hold on one item ("do not submit X") is that
  item's PLAN state, quoting the words (add a parked row if it has none), until Jihoon lifts it; argue
  against it with evidence if it costs performance.
- Write "Jihoon said/ruled/wants" only with a RULINGS id.

## Practice

- Resources first. Before a task, check RESOURCES for idle capacity, caches, seeds and other lanes'
  outputs, and use them. Idle capacity, serial work that could run in parallel, rebuilding what exists
  and waiting without a real external event are defects to fix.
- Work the critical path in PLAN: find what the experiment loop waits on and fix it.
- Full effort and full speed. No self-imposed waits, cooldowns, hold cadences, sleep-polling, rate limits
  or "later" deferrals unless CONSTRAINTS names one. Wait only on a real external event, using its
  completion signal, and do independent work meanwhile. A named next step is not a stopping point.
- Take the widest reading the rules support (CONSTRAINTS "Boundary cases"). When a case is unclear, ask
  Jihoon with your recommended reading; never settle on the narrow one by default. Keep working on it
  meanwhile; only shipping or submitting what depends on the answer waits.
- Not conservative, not incremental. Test the full change when it can be tested; keep no fallback paths
  or "just in case" variants; run no ritual check that does not serve G0.
- A failure is a defect to diagnose and fix; record it in FINDINGS "Failures" only when its cause was
  not obvious. A measured negative closes only the exact recipe tested; a negative from an
  implementation not yet shown correct closes nothing (park it as "implementation suspect").
- Done means verified where Jihoon will look at it (the leaderboard and `submit.py status`), not only
  at the component you changed. Report what you verified and what you inferred.
- When a usage or capacity limit stops a worker, reroute the work to another available model rather
  than waiting for the reset.
- Do the pre-authorized actions in GOAL's decision rights without asking, and report them afterwards.
  Decide everything else the decision rights give you; ask only what they reserve for Jihoon.
- Delegation briefs name the subgoal served, cite CONSTRAINTS rule numbers and quote RULINGS; they never
  paraphrase a rule.
- Rank candidates by true mean (3 seeds), submit by seed-0 key; report both. One seed hides 1% effects.
- Launch long jobs in the background and wait on process exit, never on an output file.
- Spread heavy runs across the mirrored hosts in RESOURCES (rule 9 cap per host); check `uptime` there
  first, and open SSH connections one host at a time.
- Default: only the main session submits, so the hourly slot is not wasted by two writers.
- Every new candidate goes into `work/submissions/` (qasm + json with `data_qubits`, score, source)
  before it is submitted.

## Commands

See [docs/RESOURCES.md](docs/RESOURCES.md) "Setup". Python is always `.venv/bin/python`.
