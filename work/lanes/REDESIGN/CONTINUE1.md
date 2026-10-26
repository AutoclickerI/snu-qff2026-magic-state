# REDESIGN continuation (main session, 2026-10-26 16:00)
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
1. Racer reservation: you SIGSTOPped 24 contest-racer children on jerry. Never signal processes you did not start. The
   jerry racer is now capped at 24 processes (work/receipts/race_specs.sh), so your 24 fit within 75% of 64 cores. If
   any racer child is still stopped from your reservation, resume it now by its recorded PID and starttime and record
   the release.
2. Run three tests concurrently, keeping square, square + leaf and path alive until their budgets end them:
   geometry (at most 2 transfers per coordinate, and relaxed prefix occupancy, to separate preparation geometry from
   prefix occupancy; each CP-SAT model at most 30 min, UNKNOWN = budget exhausted); numerical (each family's best
   grid-free build through one bounded repair, so families are compared at equal polish; the path mixed control at
   3.30467e-5 is the current lead); preparation (templates that use measured transfers or teleported hops).
3. The cultivation circuit is scope with an expiry, not a contest constraint. Open a bounded boundary-window branch
   (budget 6 hours of wall time): the ending may change the prefix-ending interface - the blue XZ check, the data hops,
   the handoff (your M(q1)@28 -> R change is one example) and which detector parities the ending consumes - while the
   cultivation stages before the blue check stay fixed unless a measured obstacle names them.
4. Two single-fault tracks: zero harmful singles, and bounded residue priced by all orders. Your "no harmful singles
   within roundoff" filter becomes a preference, not a gate.
5. Reuse, do not duplicate: WAITCUT (work/lanes/WAITCUT/REPORT.md, grid_factory.py, jit_model.py) hit the same
   obstacle with a just-in-time B/C factory (grid-free 3.341e-5, grid 5.27e-5 before repair). A new CONTRACTS lane
   (work/lanes/CONTRACTS) prices T-only resource contracts chosen for preparation cost; use its frontier when it
   appears.
Targets and checkpoints are unchanged (aim 3.2e-5, stretch 2.9e-5; 2026-10-27 12:00 and 2026-10-28 18:00). You may keep
v37h's prefix as your base; compare full prices to v37i's L.
</task_delta>
