# GAP

Status: **no circuit below 5.6e-5 was found**.  The strongest judge-valid circuit retained here is the
normal-speed LNS control `best_lns` (exact 6.85320e-5, three-seed mean 6.895644e-5).  The structurally
different early-round and merged-block mechanisms are priced below; the attractive ones are grid-free only.

## Budget of v23h_c2c9

The task brief quotes 215 CX and round start R=48.  The current canonical QASM at
`work/lanes/MAIN/v23h_c2c9.qasm` is byte-identical to every lane input and is judge-counted as **203 CX,
native depth 48, R=45**; its exact receipt is unchanged at 6.92210e-5.  I use the judge-counted QASM below
and preserve the brief's 215/48 figures as the stale budget reference.  The 12-CX/three-step discrepancy is
metadata drift, not a score difference.

| region | CX in the current QASM | native step span | what a 179-CX/R~33 design must change |
|---|---:|---:|---|
| prefix (cultivation, excluding the later BC insertion) | 78 | 0–32 | retain or cut; it already ends near 33 |
| B+C joint preparation | 83 (82 in the lane contract; one boundary CX is counted with the prefix by the builder) | 31–44 | remove about 20–30 CX or replace with a 7-cell/flag mechanism, and finish by ~33 |
| A preparation | 13 | 33–44 | remove about 5–10 CX or prepare in released cells while B is checked |
| data hops | 6 | 35–40 | remove all six by choosing a round-native data placement, or route before the block stage |
| final Steane round | 23 | 45–46 (readout through 47) | the round itself is already near its 23-CX floor; starting it ~10–12 steps earlier is the larger gain |
| **total** | **203** | **0–47** | **179 CX requires 24 fewer CX than the checked QASM (36 fewer than the brief's 215 count), plus an earlier round** |

The measured loss budget explains the required shape.  v23h_c2c9 has exact second/third parts
5.24923e-5 + 1.67287e-5 = 6.92210e-5, exp(-A1)=0.54086.  Internal prefix idles are already a 24%
relative loss source; the largest remaining mechanism is data idle exposure to late A/BC faults.  A design
that only saves CX while leaving R≈45 cannot close the leader gap.

## Architectures priced

All grid-free prices use the repository's `work/lanes/MAIN/gf/exact_gf.py` and STANDARD p=1e-3.  A
third-order number is used only when c1 is below 1e-12.

| architecture | CX / R | grid-free 1-F (third order) | exp(-A1) | grid embedding | mechanism and result |
|---|---:|---:|---:|---|---|
| separate 9-CX A, B, C blocks (`gf/sep33`) | 129 / 33 | **3.54847e-5** (3.33885e-5 + 2.09623e-6) | 0.67283 | **infeasible** as a static 6x6 embedding | Uses all 21 cells unused by the prefix for three blocks; this is the right early-round price, but the A/B/C contact and encoder graph cannot be packed next to the live data. Existing connected-region CP-SAT/annealing searches close this footprint family. |
| A-verified separate blocks (`gf/ver33g4`) | 145 / 33 | **3.62454e-5** (3.17143e-5 + 4.53103e-6) | 0.61653 | **infeasible** statically | Adds a verifier for A's dangerous Z class. The verifier improves the grid-free mechanism only modestly and consumes the cells needed for a grid placement. |
| three parallel flagged Z checks + verified Steane X check (`ARCH/hybridPZ4`) | 131 / 33–40 | **5.18493e-5** (ARCH third-order price) | 0.65128 | **infeasible** statically; interaction graph has odd cycles (for example flag–data–data triangles) | This is the strongest flag-style round price. It removes the full C block and keeps 27 logical/check cells, but a nearest-neighbour grid cannot realize its simultaneous contacts without a dynamic flag-routing construction. |
| checked dummy controls after A readout (`ARCH/dummy_checked`) | 143 / 32–40 | **4.65190e-5** (4.41063e-5 + 2.41274e-6) | 0.65486 | **infeasible** statically; 35 cells and odd cycles | Reuses measured A cells as checked zero controls for the final data CXs. It lowers the grid-free tail, but the checks' control graph is not bipartite/planar on the fixed layout; routing would add an unpriced number of CX and wait steps. |
| merged 7-cell B with three post-preparation parity flags (`merged3_r39`, this lane) | 125 / 39 | **1.15235e-4** (9.96085e-5 + 1.56261e-5) | 0.60812 | **infeasible** statically; flag/B encoder graph has odd cycles | This directly tests the suggested “one 7-cell block verified by flags” route. c1=5.95e-19, so single faults are caught, but the four-step parity checks and the long B/data wait create a large quadratic loss. It is closed as a useful candidate for this schedule. |

The static embedding tests are graph constraints over every CX edge; the odd-cycle witnesses are saved in
`embed_receipt.json`.  A grid is bipartite, so those static graphs cannot embed.  This is not a claim that all dynamic routing is
impossible.  Dynamic flag movement could remove the odd-cycle obstruction, but it needs free paths through
cells occupied by A/B or live data; no such route with an acceptance-preserving cost was built here.

## Best built and verified circuit

`best_lns` is a byte copy of the completed LNS delivery `bc_port_ed4839a8a8`.  It is retained as the
judge-valid control and is not claimed as the structural GAP win.

- **Files:** `best_lns.qasm`, `best_lns.json`
- **Exact parts:** second 5.20467e-5; third 1.64852e-5; exact third-order total **6.85320e-5**; c1=2.92e-19.
- **Acceptance estimate:** exp(-A1)=**0.53248** (A1=0.63022).
- **Judge speed/gates:** `fast_check` at 1,000,000 shots, one process: **3.8 s**, 204 CX, format/class/correctness/acceptance PASS (acceptance 0.532376).
- **Three-seed MC:** 6.852339e-5 (seed 0), 6.904925e-5 (seed 1000), 6.929668e-5 (seed 2000), mean **6.895644e-5**; seed-0 acceptance 0.53259.

The current v23 reference is 6.92210e-5 exact, so this control is a 1.0% exact improvement, not a route
to the 5.6e-5 target.  Its gain comes from local initialization/readout/timing edits and therefore does not
answer the structural GAP by itself.

## Verified versus inferred

Verified: the v23 regional counts and native spans were counted from the checked QASM; all exact values in
the tables come from the repository evaluators; the merged3 candidate has zero first-order loss and passes
the grid-free noiseless correctness test; `best_lns` passes the real judge at 1e6 shots and the speed gate;
its MC values are completed 1e8-shot runs at seeds 0, 1000 and 2000; static graph embedding infeasibility
was solved directly on the 6x6 adjacency graph.

Inferred: a 179-CX design must cut roughly 24 CX from the actual checked QASM (or 36 from the brief's stale
215-CX budget) and move the round close to the prefix boundary; static odd-cycle/area failures do not prove
that every dynamic routing construction is impossible; no candidate below 5.6e-5, and no dynamic flag route
with a verified runtime, was established in this lane.
