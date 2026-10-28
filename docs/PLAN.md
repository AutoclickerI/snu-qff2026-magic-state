# Plan

## Research checkpoint — 2026-10-28 KST

**SOTA is not reached.** The best complete native research candidate is
`SOTA_20261028/native_best/schedule_heralds_c167977fdd48de1f_d6_20_19_10_2_22_16`:
exact L=3.566732196898089e-5, A=0.5016443322953218, 412 CX, 49 clocks.
It passes raw output correctness and the official 1M gate check. It is not
submitted and has no new official 100M score. The gain is 0.0391% over the
previous phase candidate and 0.5677% over `MAIN/v37j`.

At 2026-10-28 02:29:26 KST the public leader's sampled score is
2.82064394141452e-5 (key 2.82e-5, 277 CX). Our existing board entry is
3.30430020090153e-5 (key 3.30e-5, 412 CX). These are sampled official scores,
not exact expectations. See [SOTA](SOTA.md) and the
[timestamped public snapshot](../work/lanes/SOTA_20261028/leaderboard_final.json).

The hourly race remains parked: Jihoon stopped it at 2026-10-27 23:01 KST,
[R-20261027-1](RULINGS.md). All new lanes in this workspace have completed.
No race was restarted, submission made or production candidate changed by
this checkpoint.

## Architecture decision for this request

Prioritize **joint native synthesis of an earlier source boundary and its final
measurement instrument**, with the full accepted output as the contract.
Source, resource preparation, helper reuse, record relations, legal logical
frames and timing may change together. A fixed grid-free gate list or exact
intermediate CSS state is an optional construction, not a required interface.

Use graph/stabilizer and ZX constructions to generate structural alternatives.
Use CP-SAT for useful finite local synthesis, geometry and scheduling problems.
Select complete candidates by full-noise L=N/A at A>=0.5002, rather than CX
count, makespan, c1 or c2. Keep distinct feasible families when their
preparation cost, timing and acceptance tradeoffs differ. This is a one-time
research priority for this request, not a new owner rule or a proof that one
optimizer is globally best.

The [completed research report](../work/lanes/SOTA_20261028/REPORT.md) supersedes
the earlier plan to make the historical DEEP grid-free design the sole
embedding target. The previous
[architecture review](../work/lanes/STRATEGY_20261027/DECISION.md) remains available.

## What the experiments establish

| Finding | Consequence |
|---|---|
| Best new complete abstract circuit is 2.96499e-5 before routing | Useful mechanism control; not native or SOTA |
| Unmoved source plus perfect six-square resources gives 2.74985e-5 at terminal clock 41, 2.84559e-5 at 44 | Physical preparation must be very early and clean in this source neighborhood |
| Routed seven-square source plus perfect resources gives 3.08422e-5 at 44 | The extra square did not pay for this route and delay |
| Measured-helper joint ABC circuits are raw-valid but finish around 81 and fail acceptance | Workable representation; tested constructors are far from competitive |
| SpiderCSS, corrected live-output Gao conversion and published 14-CX Steane checks were implemented | Current methods were tested under this judge contract |
| Direct native parity reads and a native teleported-output role swap lose | These explicit constructions fail; jointly designed instruments remain open |
| All 29 non-data cells are product axes at the completed source boundary | Useful source-entanglement reuse requires an earlier boundary |

Ideal-resource figures are counterfactual diagnostics, not achieved scores or
monotone global bounds. Solver `UNKNOWN` means budget exhaustion, not
infeasibility. The historical DEEP 2.7185e-5 QASM/receipt was not recovered
from the inspected checkout, main/PR or queried GitHub path history.

## Remaining work, in order of expected value

1. Produce a complete native construction that changes preparation and
   verification together. Preserve useful source entanglement before its
   measurement, or prepare a verified receiver/resource in parallel with the
   preceding check. Include physical corrections when a previously measured
   ancilla becomes live output.
2. Compare it against the verified native reference using the complete exact
   expectation and raw output oracle. A substantial native gain is the
   evidence for more repair. A mean below the current leading draw is a
   conservative milestone; an official score and current board comparison are
   still needed to claim rank 1.
3. Recover the historical DEEP circuit from its original host if access becomes
   available. Until then, use independently reconstructed seven-cat/ULO
   artifacts with their actual receipts.

No competitive native implementation of item 1 exists in this checkpoint.
Fixed-graph routing, larger versions of the same CP-SAT model and small
incumbent retimings have not supplied the requested jump. The stopped sampling
race is not a substitute for that missing circuit.

## Reproduction and validation

Selected circuits, generators, dependency hashes and receipts are indexed in
[REPRODUCE](../work/lanes/SOTA_20261028/REPRODUCE.md) and its manifests. The judge
and shared evaluator are unchanged. Preserve all noise, 6×6 adjacency and the
external limits in [CONSTRAINTS](CONSTRAINTS.md). Check raw noiseless code-space
correctness before ideal decoding. Distinguish the exact mean, a low-shot gate
check and the official 100M seed-zero score. Only the main session submits;
this checkpoint made no submission or production promotion.

