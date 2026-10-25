Continuation from the main session. Your frontier is a strong result (square minimal at 25.667 p^2, trees >= 27.207,
unmeasured-partner >= 28.747; grid-free JIT suffixes 3.39-3.47e-5) and is recorded in docs/FINDINGS.md. The new
incumbent is v37c (work/lanes/MAIN/v37c, 3.6904034715818095e-5, A 0.50572, 400 CX, 48 ticks: R46 layout, COMPLETE's
R45 phase-network end, GLOBAL's B/C core, POLISH edits). Lane SQUARE is building the square on the grid (read only);
you take the trees: build the five-block path E-A-D-B-C (and the square-with-leaf if the path stalls) on the 6x6 grid
so that it beats v37c. Finalist: exact L < L(v37c) - 1e-7 at A >= 0.5002, judge gates_ok at 1e6, judge speed within
1.5x of v37c's. A finalist does not end the lane.

The obstacle is preparation, not the round: your routed builds spend R104-R120 preparing blocks. Approaches, cheapest
first, each built and priced exactly:
1. Keep as much of v37c as possible: its A (11-CX encoder), its correlated B/C resource (r3-style, B and C are both
   |0_L>-type there) and its prefix; add only E = |+_L> checking A (A->E), placed in the cells v37c leaves free or frees
   by the R45 schedule, so that only E needs fresh preparation. Measure first what E-checking-A is worth on v37c with E
   perfect (off-grid phantom cells q36+, work/lanes/ACCBUY/sparse40), and what it replaces (A's partial decoder, the gap
   helpers).
2. Co-design layout and preparation: one CP-SAT model over the suffix (ticks ~28 to the end) with the prefix outputs
   fixed, encoders synthesized in place on the cells each block occupies (not fixed CSS encoders routed), just-in-time
   starts, and data hops counted; price the model's best few schedules in all orders.
3. Repair the best build with GLOBAL's INTEG/ACCBUY/retime tools (copy them) and buy acceptance back.
Hosts: tom <= 24 processes in total. Update REPORT.md (<= 100 lines, each < 2,000 characters) and results.json;
finalists to cand/. Do not stop to ask questions; the other rules of your brief stand.
