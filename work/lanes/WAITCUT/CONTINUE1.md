# WAITCUT continuation (main session, 2026-10-26 16:00)
<process_change>
Main session, 2026-10-26 16:00 (docs/PLAN.md "How lanes run", from a process review). Apply from now:
- Work in budgeted experiments: hypothesis, the smallest result that changes your next decision, a wall-time and price
  budget, and what earns more budget. Close each with one class: finalist; certified exclusion (scope named); measured
  failure (that recipe only); budget exhausted (open); proxy rejection (open, proxy named). Solver UNKNOWN or a timeout
  is budget exhausted, never exclusion.
- Compare families only after the same bounded repair: one standard pass of at most 200 exact prices or 30 minutes of
  MERGE's singles each, and record the repair each compared price received. An unrepaired loss closes nothing.
- Run independent tests concurrently within your host limits instead of in sequence.
- A finalist (exact L below the incumbent's at exact A >= 0.5002, raw-valid, gates_ok) goes to cand/ at once with one
  REPORT line; do not wait for convergence.
- Zero harmful single faults (c1 = 0) is a preference: keep a bounded-residue track priced by all orders.
- No lane-local speed caps: report judge time at 1e6 shots / one process paired with the incumbent on the same host in
  the same minutes; the main session applies the expected-key rule (a gain wins if it exceeds about
  1.1e-7 x log2(judge-time ratio)). 20 s per 1e6 shots at one process stays the margin under the one-hour scoring limit.
- Never signal, stop or kill a process you did not start (contest racers included); on an overfull host shrink your own
  jobs and record it.
New incumbent: v37i = EARLIER's r46_3ee1824 (work/lanes/MAIN/v37i.{qasm,json}): all orders L 3.591182404095001e-05,
A 0.5003576309837844, 411 CX, 49 native ticks; gates_ok at 1e6 and 1e7; judge time equal to v37h's. It is v37g plus
EARLIER's R45 route repair, the q17 reset herald, DETECTOR c309 and acceptance buys. Racing since 16:20.
</process_change>
<task_delta>
1. Bound the running repairs: the joint extension and acceptance buys on the grid factory and the native meter get one
   standard pass each (at most 200 exact prices or 30 minutes); continue one only if its improvement curve still falls
   by more than 1e-7 per 50 prices. Report repaired and unrepaired prices side by side.
2. Then run concurrently: (a) movement-based embeddings of the just-in-time B/C factory (measured transfers or
   teleported hops instead of fixed borrowed slots; read REDESIGN's models in work/lanes/REDESIGN/models and MODEL.md,
   which hit the same obstacle, and do not duplicate them); (b) a native history parity that separates the B/C X-fault
   pairs with identical final signatures (9895604649984); (c) for the top attribution cells, explicit pair
   interventions (both regions perfect versus each alone) so designs target what is jointly removable.
3. A grid build of any family below v37i goes to cand/ at once.
Checkpoint unchanged: 2026-10-27 12:00. You may keep v37h as base; compare to v37i's L.
</task_delta>
