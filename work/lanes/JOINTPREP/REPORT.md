# JOINTPREP

Verdict: no finalist. The requested finite synthesis and module-combination campaigns are complete. Negatives apply only to the recorded grammars, windows and finite choices.
Latest MAIN pointer checked at completion: `lanes/MAIN/v37h`. Finalist gate: exact L < 3.601954991494178e-05 and A >= 0.5002.
No submissions, commits, pushes, subagents, GPUs, or writes outside this lane. No credentials were accessed.

## Controls and identities
v37g independently reproduced with the original MAIN evaluator: L=3.621123652554788e-5, A=0.5035268387133266, 348.22 s at one process; SHA256=79fc464667ef82bc8b9b9113a5807a1d9459132e4a4f72fb8a8e68ceaaf6645c.
v37h: L=3.611954991494178e-05, A=0.5015489333258329; SHA256=78ca0e26298a1df5090b2ccc779cf2e3c4ba3f9298ef8d85487297be0432918b.
GLOBAL’s saved v37g detector basis reduced contraction width 12 -> 9, with v37h replay L=3.611954991483112e-5, A=0.5015489333258327 in 7.22 s; difference <=1.2e-16. Only contraction coordinates changed.
All exact prices refer to saved QASM with SHA256, ordered data_qubits=[6,20,19,10,2,22,16], evaluator identity, omission bound and six raw output stabilizers +1. Stem identities include QASM plus ordered outputs.
An old remote log snapshot overwrote the local v37g redirect; that receipt was restored from its captured completed tool output. Trained-basis controls remain independently saved in results.json.

## Complete-circuit costs on v37h
| Family | Attempts / exact prices / A-feasible | Best feasible L | Exact A | Delta L |
|---|---:|---:|---:|---:|
| proxy | 40 / 34 / 19 | 3.61195499149418e-05 | 0.501548933325833 | +0 |
| joint | 80 / 80 / 25 | 3.62125538842969e-05 | 0.500557039237165 | +9.3003969e-08 |
| residue | 72 / 72 / 8 | 3.70929499777581e-05 | 0.501749318258311 | +9.7340006e-07 |
| combinations | 112 / 112 / 50 | 3.61195499149418e-05 | 0.501548933325833 | +2.0328791e-20 |
| repair | 4075 / 2757 / 1757 | 3.61150745203165e-05 | 0.501449438892023 | -4.4753946e-09 |

The table includes the incumbent wherever the finite choice set includes it. Repair includes incidental generic edits; a small improvement is not a finalist.
Best incidental measured circuit: `/home/jihoon/competitions/quantumn/work/lanes/JOINTPREP/c/0a9aef0bf4d9adeddd0a4100f2af6045b0baa9622245e77a3a41e18c12a6cebe_c22bc387f6eb74bf`; SHA256=0a9aef0bf4d9adeddd0a4100f2af6045b0baa9622245e77a3a41e18c12a6cebe. Gain 4.47539463e-09, below the required 1e-7; no judge or runtime certification claimed.

## 2. Proxy calibration
48 BFLAG/GLOBAL-derived CP windows generated 111 distinct physical schedules; farthest-point CX-set sampling selected 40 without proxy filtering. 34 passed the complete ideal contract and received exact prices.
Proxy X2+1.1e-4*RZ+3e-5*acc1: Spearman=0.990772; 12/538 strict ranking inversions, 0/149 among pairs where both meet A. No feasible candidate beats the incumbent.
Six isolated-endpoint-valid proposals changed exterior guard detector 43. They were rejected, not ranked. Added the full coherent record contract to subsequent synthesis. Every subsequent candidate was selected by full (L,A), retaining the acceptance Pareto front.

## 3. Joint windows
54 CP runs: 4–8 wires across 13–12, 9–3 and 21–27, ticks 36–44; 24/30 s solve limits and up to 12 physical witnesses each. Actual release gaps include M7@39 -> 38 and RX21@39 -> 36/37/38. Original fixed-source windows and stricter internal-CX-only change constraints are retained as separate receipts.
72 mixed A/B/C witnesses plus 8 A-only control schedules were fully priced. All preserve the coherent endpoint rowspace, discard/record identities, T phase rows and outputs; independent exact ideal/raw checks passed. No generator relabeling is counted as a physical candidate.
38 witnesses actually change a bridge (15 meet A); their best is L=3.82823579911816e-05, A=0.501549268304792, delta L=+2.16280808e-06, SHA256=3959c141e578f32f48a6177cb36d749917652e324b7dc4e3924f1ab7bb855575. The 9–3 window yielded no witness within this grammar.
The cheaper mixed-window candidate retains the existing bridge, advances M7, and removes two late B/C CXs. Repair removed every A change, ejecting that joint family; the remaining early guard/source-fusion changes are generic. Follow-on generic second-round receipts are partial and are not called global convergence.

## 4. Concentrated correctable residues
56 CP windows, eight per output coordinate, changed hard F1 itself to s in {0,sig(X_i)} and required a real nonzero residue. 72 distinct witnesses, all coordinate 0, all exact-valid; the other six coordinates had no witness in the tested windows. Independent backward-propagation certificates verify every nonzero local residue has signature 9.
Best feasible raw concentrated resource: L=3.709294997775814e-5, A=0.5017493182583111. Proxy X2leak rises 1.68e-6 -> 2.00e-6; leak rises 0.0028 -> 0.0030666667; RZ falls 0.0327333333 -> 0.0326.
Exact counterfactuals (14 B/C cells after their actual starts, before tick 45; all other channels kept): resource perfect gives the same L=3.245277983198987e-5 for both circuits. Exterior perfect gives incumbent 1.847922424270369e-6 vs concentrated 1.850178249976399e-6.
With the real exterior: X-only resource noise gives 3.343103322568371e-5 -> 3.390679526955371e-5; Y-containing gives 3.299672264871271e-5 -> 3.325663617051212e-5; Z-containing without Y gives 3.389196234050915e-5 -> 3.411953657198522e-5. These overlapping finite-p counterfactuals are not additive budgets.

## 5. Finite module combinations
Five choice sets: A (3), B/C-left including the concentrated source (4), B/C-right (2), q3 (2), mixed-window/changed-bridge options (3). All 144 tuples checked: 112 compatible circuits priced, 32 operation conflicts recorded. Individually losing modules were included. Incumbent is best.
Copied AJOINT factorized rejoin retains complete T-sign, detector and output signatures. Propagation is rebuilt on every circuit; differing exterior fingerprints cannot silently reuse a marginal. Three direct full-versus-rejoin controls agree within 1.2e-16. No dense boundary table was constructed.
A resume check exposed nondeterministic ordering of disjoint same-tick gates. Fixed deterministic serialization; reused only the original saved/priced QASM after exact native-event equivalence, never assigned an old price to a new QASM hash.

## 6. Repair and limits
Copied MERGE menu, source fusion, herald/detector tools and greedy joint extension. Both closest new families received full single-edit sweeps, acceptance buyers, joint extension and explicit whole-module ejection. Completed Cartesian-pair pilot results were retained; its unrequested exhaustive expansion was replaced by the requested greedy method.
Repair attempt counts by stage: {"joint_1_extension": 109, "joint_1_joint": 316, "joint_1_singles": 1641, "joint_2_singles": 279, "residue_1_extension": 108, "residue_1_singles": 1622}.
No build passes the finalist margin, so no finalist judge test, paired runtime benchmark or latest-MAIN finalist port was needed. This does not claim that all joint rank-7 preparation paths are exhausted.
Jerry GLOBAL processes were absent before launch. Other workloads caused a load spike; our numerical workers were stopped by recorded PIDs, caches retained, and work resumed at lower concurrency. All OMP/BLAS/MKL thread counts were 1; zebra used at most two numerical workers.
Evidence: results.json; res/*_prices.jsonl; res/*_solves.json; res/combination_manifest.json; res/concentration_certificates.json; res/pauli_exterior_diagnostics.json; res/identity_audit.json; logs/factor_roundtrips.json. Process exit and final identity audit are recorded separately.
