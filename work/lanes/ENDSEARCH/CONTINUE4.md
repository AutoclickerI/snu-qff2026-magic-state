Main session: I interrupted your turn on purpose to refocus the lane on a stronger terminal target.

Reviewer 18 (work/lanes/MAIN/spec/reviewer18/: REPORT.txt, PROOF.txt, c4_steane_tail.py, c4_tile_geometry.py;
untrusted, run only copies with python -I) gives (a) a floor with the penultimate layer kept, L >= 2.1892512824770078e-5
for every admissible circuit, and (b) a C4-Steane contraction ending: per output coordinate a 2x2 tile (H D / L K);
tick T-1 CX(D,K), CX(H,L); tick T CX(H,D), MZ K, MZ L; 14 K/L records postselected; H unmeasured; the Steane code over
the seven [[4,1,2]] inner logicals is [[28,1,6]]. With a perfect 28-qubit input its tail is 2.192096e-5 (A_tail 0.979),
below your square (2.556e-5) and path (2.709e-5) tails. The main session and the CONTRACT lane reproduced it.
CONTRACT (work/lanes/CONTRACT; read its REPORT.md and circuits, never write there) audits the bound and prices option
(a): the Steane round verifies the 7-qubit state, then outputs grow into tiles just before the contraction. It found
that the final K/L reads check only the two Z parities, not the inner XXXX stabilizer, so C4 does not catch every
waiting fault.

Your new scope (P114 option b/c), using your joint layout/CP-SAT and grid-preparation machinery:
1. Close the path work in REPORT.md in a few lines: what is measured (compiled builds 5.33e-5; A noiseless 5.165e-5;
   data waits noiseless 3.161e-5), what stays open. Stop your path containers on owl (docker kill by ID; only your own
   endsearch-* containers).
2. Option (b): outputs grow into C4 blocks early, so waiting data sit in inner blocks, and the outer verification
   couples to the inner logicals (weight-2 X_D X_K, Z_H Z_D), or happens before growth with an inner check that also
   covers XXXX. Option (c): other inner codes or contractions whose preparation is cheaper on this grid. Tiles bind
   only the last two layers (no static packing of seven 2x2 tiles leaves a connected 8-cell bus adjacent to all of
   them): borrow cells and move roles before. Bound each option with phantom/grid-free full circuits with real
   preparation first (work/lanes/ACCBUY/sparse40/), then grid builds on v37h's prefix (work/lanes/MAIN/v37h, all orders
   3.611954991494179e-5, A 0.5015489333258328).
Targets: a full circuit at <= 2.8e-5 (stretch 2.5e-5) at A >= 0.5002; checkpoint 2026-10-27 12:00 KST: a priced full
circuit with real preparation showing whether < 3.4e-5 is reachable for options (b)/(c), else stop with the measured
obstacle per option. A finalist below L(v37h) - 1e-7 goes to cand/ at once. Hosts unchanged: owl <= 24 processes in
docker (count only your own containers; CONTRACT also uses owl <= 24), zebra <= 4 light work. Other rules as before.
