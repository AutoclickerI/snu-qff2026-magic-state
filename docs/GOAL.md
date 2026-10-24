# Goal

## G0 — Official 1-F of 1e-5, or as close to it as possible, by the deadline (R-20261024-3)
The measure is the official 1-F (`tprep.check(..., shots=10**8, seed=0)`) of our best board entry when
submissions close, 2026-10-30 12:00 KST; the target is 1e-5 and the score is the remaining gap. Every admissible
circuit has true expected 1-F ≥ 1.162e-5 (proved; FINDINGS "Floor, any circuit"), so 1e-5 is out of reach in
expectation and "as close as possible" is the operative reading. A one-step final readout costs ≥ 2.567e-5;
the grid-free reference design gives 3.55e-5; our grid incumbent's all-orders expectation is in PLAN "Status".
Rank 1 (R-20261023-1) holds while our key stays below every other team's; ties go to fewer 2-qubit gates, then the
earlier submission.

## Subgoals (ranked)

| Rank | Id | Subgoal | Serves G0 by | Done when |
|---|---|---|---|---|
| 1 | G1 | Lowest true 1-F circuit that passes every judge gate, submitted | it is the key; a lower true mean keeps the seed-0 key low | our key is within reach of the floor (≤ 1.5e-5) and below every competitor's at the deadline |
| 2 | G2 | Fast, predictable search with solvers and validated evaluators (R-20261023-4, R-20261023-5) | turns each idea into a ranked, verified candidate in minutes | evaluator ranking matches 3-seed official means; edit to official score < 5 min |
| 3 | G3 | Bounds and the gap per loss source | picks the lever with the most headroom | current best has floors and a loss split (FINDINGS) |
| 4 | G4 | Fewer 2-qubit gates at equal key | wins ties | our best entry has the fewest CX among teams at our key |

## Non-goals
- The ideathon track.
- `fault_scan` c1 = 0: the judge does not check it; it is a diagnostic.

## Decision rights
- Pre-authorized beyond the global list: choosing which candidate to submit and when (R-20261023-1,
  R-20261023-3); starting and stopping our jobs and Codex lanes on the hosts in CONSTRAINTS rule 9.
- Ask Jihoon: team registration or name changes; anything shown outside the team other than contest submissions;
  award-ceremony logistics; turning any instruction of his into a standing rule (question tool; confirmed rules go to
  RULINGS with his words).

## Terms
- **True mean**: the expected official 1-F of a circuit. Computed exactly by the all-orders evaluator
  (`docs/reference/circuit.md`); estimated by the 3-seed MC mean or the mean of seed-0 re-draws. The board shows
  one MC draw (seed 0, ±0.8e-6 near 4e-5); a submission is the best seed-0 re-draw of the best true-mean circuit.
