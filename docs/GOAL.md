# Goal

## G0 — Official 1-F of 1e-5, or as close to it as possible, by the deadline (R-20261024-3)
The measure is the official 1-F (`tprep.check(..., shots=10**8, seed=0)`) of our best board entry when submissions
close, 2026-10-30 12:00 KST (last loop slot about 11:24). The key, the best raced seed-0 draw, sits ≈ 3.5–4σ
(≈ 2.7e-6) below its circuit's true mean. Rank 1 (R-20261023-1) holds while our key beats every other team's; ties go
to fewer CX, then the earlier entry.

## Target
Official 1-F now 3.338e-5 ([SOTA](SOTA.md)); true mean 3.587e-5 (v37j); goal 1e-5, out of reach: every admissible
circuit has true mean ≥ 2.189e-5 (reviewer 18; re-audited, R-20261026-2). Reachable gap ≤ 1.40e-5 of mean (39%); a 1% lower
mean ≈ 0.5σ of key. PLAN "Levers" sizes each lever against this gap. Rank 1: Placeholder 3.086e-5 (293 CX).

## Subgoals (ranked)

| Rank | Id | Subgoal | Serves G0 by | Done when |
|---|---|---|---|---|
| 1 | G1 | Lowest true 1-F circuit that passes every judge gate, submitted | it is the key; a lower true mean keeps the seed-0 key low | our key is below every competitor's at the deadline and each PLAN lever got a budget sized by its gain and an outcome |
| 2 | G2 | Fast, predictable search with solvers and validated evaluators (R-20261023-4, R-20261023-5) | turns each idea into a ranked, verified candidate in minutes | evaluator ranking matches 3-seed official means; one all-orders price ≤ 1 s, FRAME lines included; edit to official score < 5 min; every lane prices through one shared, versioned, cached tool set |
| 3 | G3 | Bounds and the gap per loss source | picks the lever with the most headroom | current best has floors and a loss split (FINDINGS) |
| 4 | G4 | Fewer 2-qubit gates at equal key | wins ties | our best entry has the fewest CX among teams at our key |

## Non-goals
- The ideathon track.
- `fault_scan` c1 = 0 (a diagnostic; the judge does not check it).

## Decision rights
- Pre-authorized beyond the global list: choosing which candidate to submit and when (R-20261023-1,
  R-20261023-3); starting and stopping our jobs and research lanes (R-20261025-1) on the hosts in CONSTRAINTS rule 9.
- Ask Jihoon: team registration or name changes; anything shown outside the team other than contest submissions;
  award-ceremony logistics; turning any of Jihoon's instructions into a standing rule (question tool, then RULINGS).

## Terms
- **True mean**: the expected official 1-F of a circuit, computed exactly by the all-orders evaluator
  (`docs/reference/circuit.md`). The board shows one seed-0 draw (σ ≈ 0.7e-6), an
  hour's best re-draw.
