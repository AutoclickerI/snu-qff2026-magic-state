# Goal

## G0 — Win 1st place in the SNU Qiskit Fall Fest 2026 hackathon
Rank 1 on the official board when submissions close, 2026-10-30 12:00 KST (R-20261023-1). The key is
the official 1-F (`tprep.check(..., shots=10**8, seed=0)`) at 3 significant figures, then fewer 2-qubit
gates, then the earlier submission. A team that ties our key with fewer CNOTs beats us, so we need a
strictly lower key with margin.

## Subgoals (ranked)

| Rank | Id | Subgoal | Serves G0 by | Done when |
|---|---|---|---|---|
| 1 | G1 | Lowest true 1-F circuit that passes every judge gate, submitted | it is the key; a lower true mean keeps the seed-0 key low | our key is strictly below every competitor's at the deadline |
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
- **True mean**: mean of the official score over seeds 0, 1000 and 2000 (1e8 shots each). The board
  shows one MC draw (seed 0, ±1.2e-6).
