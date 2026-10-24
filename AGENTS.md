# AGENTS

Our entry in the SNU Qiskit Fall Fest 2026 hackathon: fault-tolerant preparation of the Steane-code
|T_L⟩ on a 6×6 grid, scored by the organizers' judge. Owner: Jihoon.

**Before any work, read [docs/GOAL.md](docs/GOAL.md) and [docs/CONSTRAINTS.md](docs/CONSTRAINTS.md).**
On demand: [PLAN](docs/PLAN.md) (critical path, ranked work, open questions) ·
[RESOURCES](docs/RESOURCES.md) (setup, hosts) · [FINDINGS](docs/FINDINGS.md) (measurements, closed
recipes, failures) · [SOTA](docs/SOTA.md) (baseline, best) · [RULINGS](docs/RULINGS.md) (Jihoon's words,
dropped rules) · [reference/judge.md](docs/reference/judge.md) (how scores arise) ·
[reference/circuit.md](docs/reference/circuit.md) (our circuit and search tools) · contest text
`upstream/snu-qff2026-problem/problem.md`.

## Practice

- Use idle capacity, caches and other lanes' outputs (RESOURCES); fix the critical path (PLAN).
- Take the widest reading the rules allow (CONSTRAINTS "Boundary cases"); ask Jihoon when unclear.
- No conservative or incremental steps, fallbacks or ritual checks; delete stale docs when you touch them.
- Rank candidates by the all-orders expectation where its scope covers them (`work/lanes/WALSH/allorders.py <qasm>
  --json <json> --procs 4`, width ≤ 26, reproduces reviewer 3's values and our re-draw means within 0.1%;
  `work/lanes/BCPOL/allorders_general.py` for five-projector blue circuits); otherwise by the 3-seed mean (one seed hides 1%), and when that and the exact
  third order disagree within noise, by ≥ 100 seed-0 re-draws. Submit by the seed-0 key and report the numbers used.
- Wait on process exit, never on an output file. Never `pkill -f` a pattern that your own command
  line contains (FINDINGS "Failures").
- Only the main session submits, and every submitted candidate is committed in `work/submissions/` (qasm + json)
  first (default: one lane's submission would spend the team's hourly slot).

## Commands

Python is always `.venv/bin/python`; the tool commands are in RESOURCES "Setup".
