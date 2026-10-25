Continuation from the main session. Your finalist global_r46_m14 is verified (all orders 3.761821654835085e-5, A
0.5007854638217537, judge gates_ok) and committed as work/lanes/MAIN/v37a.{qasm,json}; it races from the 20:37 slot.
Thank you. The lane continues with a new target; a finalist does not end it.

New incumbent and tau: v37a, tau = 3.761821654835085e-5. Finalist: L < tau - 1e-7 at exact A >= 0.5002, judge gates_ok
at 1e6. Rank by J_tau = A*(L - tau) with the A floor enforced.

Directions, both on v37a's R46 layout (another lane, POLISH, runs the greedy local-edit polish on v37a; do not
duplicate it):
1. B/C of r3's quality on R46's cells. Your diagnostics put noiseless-B/C at -4.73e-6 on R46 against -3.81e-6 on v36h,
   so R46's B/C is about 0.9e-6 behind r3. Use the robust synthesis that produced r3 (BCX bcsynth.py/bclns.py with the
   decoder-safe contracts, extended windows, warm starts from the 65-CX resource; FINDINGS rows on r3 and BCX), across
   the B/C cells and ticks R46 allows, and price every archived Pareto point in all orders on the full circuit.
2. A late X check on R46 (S12X on v36h was -1.15e-6 as a phantom): recompute R46's free cells next to the data at
   ticks 39-46, try the cheapest realizations (cat or chain over free cells, single role/guard swaps, a retimed helper),
   then CP models that keep v37a's A and B/C; price each full circuit.
Repair each improvement with your INTEG/ACCBUY/retime passes and buy acceptance back as needed.

Hosts: jerry <= 24 processes in total, zebra (local) <= 8. Stop when both directions reach their decisive tests and
either a finalist exists that further work no longer improves, or the best is >= tau, naming the cost that ate each
gain with measured numbers. Update REPORT.md (<= 100 lines, each line < 2,000 characters: keep the full per-circuit
table in a separate file) and results.json; finalists to cand/. Do not stop to ask questions. Other rules of your
brief stand (no commits, submissions, sub-agents; never pkill -f; never read .submit_credentials).
