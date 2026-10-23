# Goal

## G0 — Official 1-F of 1e-5, or as close to it as possible, by the deadline (R-20261024-3)
The measure is the official 1-F (`tprep.check(..., shots=10**8, seed=0)`) of our best board entry when
submissions close, 2026-10-30 12:00 KST; the target is 1e-5 and the score is the remaining gap. Under the
judge's noise no circuit goes below 1.116e-5 and a one-step final readout costs ≥ 2.567e-5 (FINDINGS
"Floor, any circuit"), so "as close as possible" is the operative reading. Rank 1 (R-20261023-1) follows
from any entry below the leader (6.29e-5 on 2026-10-24); ties go to fewer 2-qubit gates, then the
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
- Ask Jihoon: team registration or name changes; anything shown outside the team; award-ceremony
  logistics.

## Terms
- **True mean**: mean of the official score over seeds 0, 1000 and 2000 (1e8 shots each), or the mean of
  seed-0 re-draws (`work/reorder.py`), which is tighter for a submitted circuit. The board shows one MC
  draw (seed 0, ±1.2e-6).
