# WHOLEEND
**Verdict: no finalist. Step 1 reproduced; the constructed branches in steps 2–4 failed their numerical gates.**
Best complete circuit remains `../MAIN/v37c`: L=3.6904034715818095e-5, A=0.5057191647109531, J_tau=0; SHA256 42df45423212. No new ending passed its last gate, so no new full-prefix preparation was required. `cand/` is empty.
All prices are all-orders conditional expectations at p=0.001; tau is v37c above and J_tau=A*(L−tau). A negative J on an ideal-resource tail is not a realizable full-circuit gain.

1. **Necessary condition reproduced and certified.** Floors for k=0..7 outputs without a penultimate CX, in 1e-6: 13.657851, 16.516810, 19.726400, 23.286001, 27.194994, 31.452950, 36.059062, 41.012809.
Integer Fourier moments cover 279,936 assignments × 64 syndrome sectors via 2,766 GL(3,2) orbits; unreduced floating enumeration agrees, and BOUND’s direct rational moment routine verifies each winner. Use k≤4 for L≤2.99e-5, k≤3 for L≤2.62e-5 or the 2.4e-5 tail gate. These bound expectations, not finite-shot draws or attainability.
2. **35-role tree: gate failed.** Reviewer arrival prices reproduce: early 4.209586375e-5; perfect JIT 2.676028750e-5; JIT with diagnostic D1(p/5) on A/B/C 2.945493827e-5. The p/5 diagnostic is not asserted to bound every preparation.
CP-SAT packed seven E–D–B–C trees with D–A leaves (35 distinct cells); the spare cell routes preparation. Four connected-grid GF(2) encoders were built. The two shallower schedules, 142 CX/R61 and 149 CX/R65, were priced with every ancillary preparation channel and with ideal D supplied at R. E is ready at R, A/B/C at R+1, and their last preparation gates overlap E→D.
Corrected best tree L=0.016082055515, A=0.459769988736; the other is 0.020195892831. Both fail <2.8e-5 and have harmful single preparation faults (single-fault contributions 0.014276 and 0.016739). These constructions are closed; this is not a lower bound on all fault-tolerant JIT preparation.
3. **T-preserving contracts: gate failed in the tested search.** Reproduced 1,072/1,728 signed square contracts, and 112 identity plus 22 extra T-only positive-sign contracts. Expanded 44,928 positive-Pauli-resource/readout contracts over all 16 CX orientations of square, path and reviewer-tree graphs: 4,797 T-only contracts. Output stays D and reads are X/Z in this search.
All six minimum-c2 T-only contracts were priced: best 2.558464159e-5, above ordinary square 2.555843124e-5, with the same square graph. Best tested path is 2.712559466e-5. No tested tree matches the square. Higher-c2 contracts were screened by the coefficient, not exhaustively priced at finite p.
With the noisy causal v37c prefix through native tick 43, perfect ancillary arrivals and no artificial boundary wait, best tested T-only square is 2.878042451e-5 vs ordinary square 2.859799469e-5. This includes the actual incoming distribution, but excludes resource-preparation cost and grid routing.
Reviewer #8’s arbitrary-logical-B contract reproduces 2.977318202e-5 (t_11_round). On that same incoming prefix it becomes 4.475176306e-4: lost Z-syndrome visibility is fatal here. t_09 fixes B=0 and adds its deterministic logical-Z detector; its slightly lower round value is a different, stronger resource contract.
4. **Whole-grid backward synthesis: gate failed.** Two sweeps × 48 final layouts, each with two or three preceding CX layers: 104 feasible first-order-safe schedules (60 distinct), 88 infeasible greedy extensions. CP-SAT chooses grid-wide matchings without per-index replication; outputs may move one cell, read bases vary by cell, and shared readouts are permitted. The broader sweep uses the k≤3 floor pruning.
Synthesis fixes final unmeasured helper→output CXs, then works backwards using exact propagated single-fault constraints and a linear cross-with-suffix pair-cost objective. Each layer is solved exactly, but layerwise choices, final matching and read bases are searched heuristically: no global optimality/infeasibility certificate is claimed.
Back-propagation gives 28 independent commuting stabilizers (six output-code rows + 22 record rows), encoded logical X/Z with target T, and seven gauge qubits. Pure completions supply inverse-Clifford QASM witnesses. The best three-/four-tick tails are 3.371181230e-5 / 4.019855706e-5, both above 2.4e-5; no preparation synthesis follows this failed gate.
Best whole-grid tail: `builds/whole_b2_s35_tail.{qasm,json}`, A=0.954536653645, J_tau=−3.04709330140e-6; output 20→26. Its boundary resource is supplied perfectly and is not a complete preparation. Final contacts, all preceding native gates, shared detector rows, and gauge contracts are saved in its JSON.

Every priced circuit/noise experiment (same hash can have different cuts; `_incoming` uses the real prefix, `_round` perfect inputs/resources):

| Saved stem under builds/ | L | A | J_tau | SHA256 prefix | What moved |
|---|---:|---:|---:|---|---|
| [v37c](builds/v37c.qasm) | 3.6904034716e-05 | 0.50571916471 | 0 | 42df45423212 | full incumbent, reproduced |
| [t_00_incoming](builds/t_00_incoming.qasm) | 2.8780424513e-05 | 0.58835170305 | -4.7795398976e-06 | 5220467b3104 | square YZZ/ZXX; real prefix |
| [t_00_round](builds/t_00_round.qasm) | 2.5584641585e-05 | 0.95752516178 | -1.0838603739e-05 | e650596c4495 | square YZZ/ZXX; round only |
| [t_01_incoming](builds/t_01_incoming.qasm) | 2.8804438774e-05 | 0.58835170305 | -4.7654110664e-06 | 28b7e97c4aec | square ZZY/ZXX; real prefix |
| [t_01_round](builds/t_01_round.qasm) | 2.5608520473e-05 | 0.95752516178 | -1.0815739103e-05 | 202e29331dc7 | square ZZY/ZXX; round only |
| [t_02_incoming](builds/t_02_incoming.qasm) | 2.8780424513e-05 | 0.58835170305 | -4.7795398977e-06 | eec571438aa9 | square YZZ/XXZ; real prefix |
| [t_02_round](builds/t_02_round.qasm) | 2.5584641585e-05 | 0.95752516178 | -1.0838603739e-05 | 8270f3ee669c | square YZZ/XXZ; round only |
| [t_03_incoming](builds/t_03_incoming.qasm) | 3.0476375885e-05 | 0.58071777765 | -3.7326557517e-06 | cb6f1986ee80 | path YZXZ/XXXZ; real prefix |
| [t_03_round](builds/t_03_round.qasm) | 2.7125594664e-05 | 0.94509619606 | -9.2415664965e-06 | 6021fff8d137 | path YZXZ/XXXZ; round only |
| [t_04_incoming](builds/t_04_incoming.qasm) | 3.0476645106e-05 | 0.58071778604 | -3.7324994642e-06 | 8ab382e4edf0 | path YZYZ/XXXZ; real prefix |
| [t_04_round](builds/t_04_round.qasm) | 2.7125860583e-05 | 0.94509620969 | -9.2413153108e-06 | 9224de807cee | path YZYZ/XXXZ; round only |
| [t_05_incoming](builds/t_05_incoming.qasm) | 3.0476645106e-05 | 0.58071778604 | -3.7324994642e-06 | 6ba4b875507b | path YZZZ/XXXZ; real prefix |
| [t_05_round](builds/t_05_round.qasm) | 2.7125860583e-05 | 0.94509620969 | -9.2413153108e-06 | 5746ed8f7d79 | path YZZZ/XXXZ; round only |
| [t_06_incoming](builds/t_06_incoming.qasm) | 3.1405412815e-05 | 0.57263028003 | -3.1486773991e-06 | 98114079ee6b | r15tree YXZZ/ZXZX; real prefix |
| [t_06_round](builds/t_06_round.qasm) | 2.8906329826e-05 | 0.93197377494 | -7.4536512173e-06 | 983ed3ec7a20 | r15tree YXZZ/ZXZX; round only |
| [t_07_incoming](builds/t_07_incoming.qasm) | 3.1405412815e-05 | 0.57263028003 | -3.1486773991e-06 | 5bd6417ecc94 | r15tree YYZZ/ZXZX; real prefix |
| [t_07_round](builds/t_07_round.qasm) | 2.8906329826e-05 | 0.93197377494 | -7.4536512173e-06 | f64a9e2498ae | r15tree YYZZ/ZXZX; round only |
| [t_08_incoming](builds/t_08_incoming.qasm) | 3.1387526933e-05 | 0.57263028003 | -3.1589193967e-06 | 073c67e3f12a | r15tree YZXZ/ZXZX; real prefix |
| [t_08_round](builds/t_08_round.qasm) | 2.8888443545e-05 | 0.93197377494 | -7.4703207617e-06 | 77f9ba07d039 | r15tree YZXZ/ZXZX; round only |
| [t_09_incoming](builds/t_09_incoming.qasm) | 0.00044749978568 | 0.6027447435 | 0.00024748443059 | 559d8fc8e01c | square YZZ/ZZX; real prefix |
| [t_09_round](builds/t_09_round.qasm) | 2.9755325649e-05 | 0.95842103257 | -6.8514731259e-06 | 1ddcabe3bf82 | square YZZ/ZZX; round only |
| [t_10_incoming](builds/t_10_incoming.qasm) | 2.8597994686e-05 | 0.58835168717 | -4.8868726655e-06 | 5b965b9b5800 | square_baseline XZX/ZXX; real prefix |
| [t_10_round](builds/t_10_round.qasm) | 2.5558431236e-05 | 0.9575251362 | -1.0863700517e-05 | 008e0a47a90f | square_baseline XZX/ZXX; round only |
| [t_11_incoming](builds/t_11_incoming.qasm) | 0.00044751763062 | 0.60274476317 | 0.00024749519462 | 81bd26f1f51d | reviewer15_arbitrary_B YXZ/ZZX; real prefix |
| [t_11_round](builds/t_11_round.qasm) | 2.9773182016e-05 | 0.95842106379 | -6.8343594306e-06 | bdb5695f81fa | reviewer15_arbitrary_B YXZ/ZZX; round only |
| [t_22_round](builds/t_22_round.qasm) | 2.5584641585e-05 | 0.95752516178 | -1.0838603739e-05 | fcbeef145405 | square YZZ/ZXX; round only |
| [t_24_round](builds/t_24_round.qasm) | 2.5608520473e-05 | 0.95752516178 | -1.0815739103e-05 | 8cc492bfb534 | square ZZY/XXZ; round only |
| [t_25_round](builds/t_25_round.qasm) | 2.5584641585e-05 | 0.95752516178 | -1.0838603739e-05 | 6ea4138e9b85 | square YZZ/XXZ; round only |
| [tree_early](builds/tree_early.qasm) | 4.2095863755e-05 | 0.95308815622 | 4.9482707662e-06 | df420a8dfeec | all resources present before tick 0 |
| [tree_grid_jit_s0](builds/tree_grid_jit_s0.qasm) | 0.020195892831 | 0.46923315404 | 0.009459265895 | 3f6cc367fc2e | real JIT grid preparation; perfect data input |
| [tree_grid_jit_s0_delayed](builds/tree_grid_jit_s0_delayed.qasm) | 0.020412689252 | 0.45869578757 | 0.0093462868475 | ae7f783f4d11 | rejected spare-helper timing; retained evidence |
| [tree_grid_jit_s3](builds/tree_grid_jit_s3.qasm) | 0.016082055515 | 0.45976998874 | 0.0073770791154 | 2c0910a130f6 | real JIT grid preparation; perfect data input |
| [tree_grid_jit_s3_delayed](builds/tree_grid_jit_s3_delayed.qasm) | 0.016333783578 | 0.44943243635 | 0.0073243462782 | b243532e8488 | rejected spare-helper timing; retained evidence |
| [tree_jit_q](builds/tree_jit_q.qasm) | 2.9454938268e-05 | 0.96380658852 | -7.1794882349e-06 | df420a8dfeec | same arrival plus D1(p/5) |
| [tree_perfect_jit](builds/tree_perfect_jit.qasm) | 2.6760287497e-05 | 0.96650468468 | -9.803979207e-06 | df420a8dfeec | perfect A/B/C supplied at tick 1 |
| [whole_b2_s35_tail](builds/whole_b2_s35_tail.qasm) | 3.3711812301e-05 | 0.95453665365 | -3.0470933014e-06 | d6aef88556b4 | global CX layers; inverse resource perfect |
| [whole_b3_s47_tail](builds/whole_b3_s47_tail.qasm) | 4.0198557062e-05 | 0.93877286186 | 3.0928081712e-06 | 47fc1fa70b82 | global CX layers; inverse resource perfect |

**Verified:** all 37 saved experiments pass the organizer’s exact raw-state target check; all current schedules match native ticks and the claimed grid prep/tail contacts. The two explicitly rejected `_delayed` files retain their known mismatch. 17 independent native fault-pair coefficients agree with search within 4.3e-14; all T-only/whole-grid tails have zero harmful singles.
**Corrections:** schedule audit caught a spare-helper read in its last preparation tick, which inserted one extra native tick; moving it to R+1 fixes the deadline, and both grid trees were repriced. A builder substitution initially mangled `reset` while replacing T by S; it was fixed before any valid price. Local affine-frame evaluator gained S/Pauli gates and frame constants, verified against organizer raw correctness.
**Inferred/open:** no universal exclusion of T-preserving contracts, JIT preparations, or whole-grid endings. Optimistic-resource witnesses are not format-valid complete submissions; no new full-circuit noisy judge/1e8-shot test is claimed. The best full circuit remains v37c, not an optimistic tail.
**Decisions:** used the task’s numerical gates and stopped failed constructions; supplied ideal data only where the requested tail gate permits it; preserved actual prefix noise for incoming tests. No standing rule was added. SQUARE/ENDSEARCH stayed read-only; no subagents, submissions, commits or pushes.
**Files:** `results.json` is keyed by QASM SHA256 with cut-specific experiments; `verification.json`, `artifact_audit.json`, `MODEL.md`, `logs/floors_exact_certificate.json`, `logs/{tsearch,t_frontier,whole_search,whole_search_allactive,tree_builds}.json`, QASM/metadata under `builds/`, and source/reproduction tools in this lane. All research computation ran inside owl Docker, at most 15 concurrent Python processes, OMP/BLAS/MKL=1; no GPU or other compute host.
