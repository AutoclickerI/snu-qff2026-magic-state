Continuation from the main session. Your gates 1-2 are a real result (grid-free square suffix 3.4896e-5, already
2.7e-6 below v37a's heavily optimized on-grid 3.7618e-5, with plain 9-CX encoders); your grid builds lose because
preparing blocks scattered over seven squares takes R85-R94 instead of R44. That closes those embeddings, not the
square on the grid. The square stays our largest lever; continue step 3 with these approaches, cheapest first, each
built and priced exactly, and a finalist does not end the lane:

1. Mirrored tiling: alternate the orientation of neighbouring squares ([[d,a],[b,c]] next to [[a,d],[c,b]], and
   vertically mirrored bands) so that same-block qubits touch across square edges; each block then has a connected
   sub-graph plus the eight free cells. Synthesize the A, B and C encoders (and B's logical-Z check) directly on that
   geometry with CP-SAT for depth (EXENC/AENC/BCX-style models), not by routing a fixed CSS encoder.
2. Early preparation in place: the square region can host A/B/C preparation while the 15-T prefix runs; idle errors
   on the resources are mostly caught by the square round itself (A's Z by C, B's X by A through C, B's Z by MX(B)), so
   long-lived resources cost acceptance more than loss. Measure that with region counterfactuals (resource idles
   noiseless) before relying on it. Bring the data in with the fewest hops; the prefix itself may move (COMPLETE's and
   GLOBAL's tools re-place the prefix outputs).
3. Time-varying adjacency: the 4-cycle d_i-a_i-c_i-b_i must exist only at the two round ticks; before that blocks may
   sit where encoding is cheap and shift one cell (ancilla hops) right before the round.
4. Acceptance: the square's grid-free acceptance was 0.539; buy back with ACCBUY's tools (cheap detector trades)
   where needed.
Target: L < L(v37b) = 3.7423214600721095e-5 at A >= 0.5002 (v37b is the new incumbent: work/lanes/MAIN/v37b). Hosts
now: owl <= 24 inside docker (rsync inputs there: owl has its own disk) and hippo <= 8. Update REPORT.md (<= 100 lines,
each < 2,000 characters) and results.json; finalists to cand/. Do not stop to ask questions; other brief rules stand.
