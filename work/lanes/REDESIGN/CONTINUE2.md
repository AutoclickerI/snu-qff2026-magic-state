# REDESIGN continuation 2 (main session, 2026-10-26 20:00) - priority change
Another team now holds rank 1 at an official 3.086e-5 (293 two-qubit gates, acceptance 0.510); our best key is 3.325e-5
and v37j's mean 3.587e-5 cannot reach 3.09e-5 by racing. Your contracted-prefix families (B1: square + leaf 2.942e-5,
path 3.017e-5, square 3.114e-5 grid-free before repair) are our best route. From now:
1. Every budget goes to a complete, raw-valid grid circuit of a contracted-prefix family. Certificates and controls
   only when they unblock a build. Any grid build at or below 3.4e-5 at A >= 0.5002 is valuable: it goes to cand/ at
   once (with paired judge timing), even before repair converges.
2. Widen the geometry freely: move the whole prefix by grid symmetries or translations, re-choose output cells and data
   hops, accept more transfers, drop guards when their cells are needed (then add guards back where cells are free),
   and let ending blocks borrow freed prefix cells after their last use.
3. First priced grid build by 2026-10-27 06:00. A second lane, EMBED (work/lanes/EMBED), attacks the same embedding with
   a constructive local search instead of CP-SAT and will read your models/ and builds/; keep REPORT.md and your saved
   contracted prefix (models/contracted_prefix_retime.json and the B1 QASMs) current so it can reuse them.
