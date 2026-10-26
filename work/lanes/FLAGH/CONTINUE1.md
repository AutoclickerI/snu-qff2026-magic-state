# FLAGH continuation 1 (main session, 2026-10-26 21:00)
E1 accepted: the repaired precheck + 7-cat double + square design (3.0198428e-5, A 0.6654, 180 CX, grid-free) is our
best architecture result and the rival's 293-CX entry at 3.086e-5 fits a design of this kind plus routing. E2 is now
the lane's whole budget, with a different method: synthesize the circuit natively on the grid instead of routing an
abstract circuit afterwards (SABRE and reverse routes are closed as measured failures).
- Every gadget has freedom that routing ignores: a cat state can be grown along any spanning tree of free cells; the
  precheck and the Steane encoders can use any encoder of the chosen cells (work/lanes/EXENC: every heptomino shape has a
  CX-only encoder <= 14 CX); flags can sit next to the CXs they guard; the square ending's blocks and data can be
  placed first (REDESIGN's and CONTRACTS' native square/leaf/path tiles and encoder templates are reusable); a qubit
  that is done can be reset and reused as another gadget's cell; measured or coherent transfers move a logical wire
  when adjacency runs out.
- Place the data and the terminal tiles first, then the logical-check gadgets around the data at each check time, with
  a joint model (CP-SAT or constructive search) whose objective is ticks and idle exposure, not routed-CX count.
- Spend the acceptance surplus (A 0.665 versus 0.5002) on lower loss once a grid build exists: extra detectors,
  repeated checks, stricter flags (about 1.6e-5 loss per unit of acceptance has been the exchange rate).
- Budget: first raw-valid native grid build priced by 2026-10-27 06:00; lane checkpoint 2026-10-27 14:00. Any grid build
  at or below 3.4e-5 at A >= 0.5002 goes to cand/ at once with paired judge timing against v37j.
Compute: hippo at most 24 processes, zebra at most 2.
