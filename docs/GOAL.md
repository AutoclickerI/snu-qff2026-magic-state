# Goal

## G0 — Win 1st place in the SNU Qiskit Fall Fest 2026 hackathon
Rank 1 on the official leaderboard when submissions close at 2026-10-30 12:00 KST (R-20261023-1). The
task is to prepare the Steane-code magic state |T_L⟩ on the 6×6 nearest-neighbour grid. The ranking key
is the official 1-F at p=1e-3 (`tprep.check(..., shots=10**8, seed=0)`), compared at 3 significant
figures. Ties go to fewer 2-qubit gates, then to the earlier submission. Only each team's best entry is
shown ([CONSTRAINTS](CONSTRAINTS.md) rules 1–7). Success is a key strictly below every other team at the
deadline, with as much margin as possible, because a competitor that ties on the key with fewer CNOTs
beats us.

## Subgoals (ranked; G0 wins over any subgoal, a higher rank over a lower one)

| Rank | Id | Subgoal | Serves G0 by | Done when |
|---|---|---|---|---|
| 1 | G1 | Lowest true 1-F circuit that passes every judge gate, submitted | the key itself; a lower true mean also makes the seed-0 key lower and robust | our board key is strictly below every competitor's at the deadline |
| 2 | G2 | Fast, predictable search: solvers and exact or validated evaluators instead of hand tuning (R-20261023-4, R-20261023-5) | turns each idea into a ranked, verified candidate in minutes, not hours | candidate ranking by the evaluator matches multi-seed official means, and a new idea goes from edit to official score in < 5 min |
| 3 | G3 | Know the bound and the gap per loss source | picks the lever with the most headroom | bounds and a loss decomposition exist for the current best ([FINDINGS](FINDINGS.md)) |
| 4 | G4 | Fewer 2-qubit gates at equal key | wins ties (Placeholder had 103 CX vs our 115 on 2026-10-23) | our best entry has the fewest CX among teams at our key |

## Non-goals
- The ideathon track (separate contest on the same site).
- Literal first-order fault tolerance (`fault_scan` c1 = 0). The judge does not check it; it is a
  diagnostic (CONSTRAINTS "Not constraints").
- Beating the seed-0 key by selection alone without a better true mean, as an end in itself. It is
  allowed and used, but a true-mean gain is what protects the lead.

## Decision rights
- Pre-authorized (do without asking, report after): official submissions within the hourly quota
  (R-20261023-1, R-20261023-3); commits to this repo (never force-push or rewrite history); deleting
  rebuildable files (caches, vendored packages); starting and stopping our own jobs and Codex lanes.
- Agents decide: technical approach, which candidate to submit and when, experiment order, parallelism
  and CPU allocation within CONSTRAINTS rule 9, tooling, refactors.
- Ask Jihoon: changes to G0 or the subgoal ranking; adding, changing or removing Jihoon's rules; team
  registration or name changes; anything shown to people outside the team; award-ceremony logistics;
  new accounts or paid resources.

## Glossary
- **1-F**: judge infidelity ½(1 − (⟨X_L⟩+⟨Y_L⟩)/√2) averaged over accepted shots. **Key**: 1-F at 3 s.f.
- **Seed-0 score vs true mean**: the official number is one MC draw with ±1.2e-6 (≈1%) noise. "True
  mean" here is the mean over seeds 0, 1000, 2000 at 1e8 shots each.
- **Acceptance**: fraction of shots whose detectors all match and postselections hold; must be ≥ 0.5.
- **Proxy**: exact second-order loss of the final stabilizer cycle alone (`work/proxy2.py`, gmodel).
- **ALAP**: rescheduling the injection and double-cat stages as late as possible before the cycle.
- **A1**: layout variant with data qubit d1 moved (2,3)→(1,3) and (2,3) reused as an X-only cat member.
- **Tail**: data idle after a qubit's last check CNOT; pairs of tail errors dominate 1-F.
- **Lane**: one parallel workstream with its own directory under `work/lanes/`.
