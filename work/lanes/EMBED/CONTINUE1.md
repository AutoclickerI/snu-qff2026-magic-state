# EMBED continuation 1 (main session, 2026-10-26 21:15) - new target, new method
Your closure is accepted (REDESIGN-family embeddings lose to transport; no exclusion). New target: FLAGH's flag-based
design, which passed its grid-free test at 3.0198428e-5, A 0.6654, 180 CX, 36 wires, 15 T, no harmful single fault
(work/lanes/FLAGH/REPORT.md, its builds/ and evidence/, stem sha256 14680d5155ff1afb...). The named way to cut
transport: it is small and made of gadgets whose connectivity is free (cat states along any spanning tree, any encoder
per cell set, flags beside the CXs they guard), so it can be laid out on the grid from the start.
FLAGH itself now does constructive gadget-by-gadget grid synthesis. You take a different method, so the two do not
duplicate: an exact time-expanded placement model (CP-SAT): each logical wire occupies one cell per time window, a CX
needs adjacent cells at its tick, wires move only by measured transfers or SWAPs that the model pays for, a reset frees a
cell for reuse, gadget connectivity is a choice inside the model (cat-state trees, encoder variants from
work/lanes/EXENC, flag positions), objective = ticks plus idle exposure weighted by the measured channel costs.
Decompose by time (prefix of injection + precheck, logical checks, square ending) if the full model is too large.
Price raw-valid builds exactly with qtools, one bounded repair on the best, then spend the acceptance surplus.
Budget: first raw-valid native build by 2026-10-27 06:00 (each model at most 30 min; UNKNOWN = budget exhausted);
checkpoint 14:00. Any grid build at or below 3.4e-5 at A >= 0.5002 goes to cand/ at once with paired judge timing
against v37j. Read FLAGH/REPORT.md first and again at each step; never write in FLAGH's dir.
Compute: sunfish at most 20 processes, zebra at most 2.
