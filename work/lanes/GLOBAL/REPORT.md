# GLOBAL

Verdict: FINALIST VERIFIED; positive stop rule met.
Target: L < 3.765473322483099e-5, A >= 0.5002, fast_check PASS at 1e6. Ranking: J_tau=A*(L-tau), tau=3.815473322483099e-5.
Best feasible saved circuit: `cand/global_r46_m14.qasm`, L=3.7618216548239997e-05, A=0.50078546382175371, J_tau=-2.6867975273472643e-07, SHA256 `cdaa719694c647348ca0fc5e3b311f1586df7f974ad993c0249fef18b9ee1b0e`.
Finalist and judge evidence: {"path":"cand/global_r46_m14.qasm","sha256":"cdaa719694c647348ca0fc5e3b311f1586df7f974ad993c0249fef18b9ee1b0e","loss":3.761821654824e-05,"acceptance":0.5007854638217537,"J_tau":-2.6867975273472643e-07,"improvement":5.365166765909933e-07,"threshold_margin":3.651667659099471e-08,"judge_1e6":{"shots":1000000,"seed":0,"passed":true,"gates_ok":true,"sampled_loss":3.090481317541957e-05,"sampled_acceptance":0.50154,"sem":6.38e-06,"seconds":3.5,"log":"logs/global_r46_m14.judge1e6.txt","log_sha256":"dff3f19ed8c6a1ef9affd21e27e2d55082bdb3033979a844ad69ca9b0dceb9ca"},"data_qubits":[6,20,19,10,2,22,16],"native_depth":49,"cx":390,"bytes":20304,"commands":649,"resets_and_measurements":152}
What moved: R46 data [6,20,19,10,2,22,16], A [7,14,13,9,8,21,15], B [12,26,25,11,3,28,17], C [18,27,24,5,4,29,23]. The model moves 15 ancilla roles and routes data in 10 hops (baseline 6); rebuilt A/B/C, two flag-gap helpers, acceptance trades, and relocated guards/identity pairs.

Verified baseline: L=3.815473322483099e-5, A=0.5016415049479505. All quoted room prizes reproduced from saved circuits; S123Z_original preserves the original schedule (the current generator conflicts with Tdg). Phantom references are excluded from candidate ranking.
Family comparisons: circuit prices and paired differences are measured; explanations of excess cost are inferred except where an explicit control/counterfactual is given.
| Family | Measured result / cost |
|---|---|
| Coherent handoff | Best full build L=5.39091203022032e-5, A=0.493023111563; route/schedule cost exceeds the helper prize. Empty-tick control collapses natively and equals baseline. |
| R44 four-role move | Without helper L=4.238363950695258e-5; with helper 4.146180314080995e-5 (gain 0.921836e-6); repaired r44gfr1j0 L=3.974091169505472e-5, A=0.5002549617498283. |
| R45 rebuild | Without helpers L=4.858515483905999e-5; with helpers 4.6939351587325604e-5 (gain 1.645803e-6). Rebuilt BC dominates excess cost; all repair prices appear below. |
| R46 rebuild | Without helpers L=4.275887823791441e-5; with helpers 4.1058812395574686e-5 (gain 1.700066e-6), initially A=0.4895241030. Repairs and acceptance trades overcome this deficit. |
| Acceptance purchase | r46gr2j8: L=3.932526483407596e-5, A=0.4906512758; r46buys8_omit293: L=3.933405462173297e-5, A=0.5007935504. Later r46warm_000 to r46fundfs2_omit294 costs 4.8479085e-8 loss for about 0.00829 acceptance. |
| BC refinement | 65-CX r46warm_000: L=3.8410065051386464e-5, A=0.5023236003934403; better measured loss than the 61-CX structural-objective optimum. |
| Joint late S23 X check | joint_s23_drop L=5.2925932818620726e-5, A=0.5053241439; rebuilding A and dropping source checks consumes the prize. No isolated check-cost attribution was measured. |
| Earlier two-helper R44 | r46fast44 helpers L=4.240165145187328e-5 versus 4.4073242100496195e-5 control; prefix changes and removed source checks consume the gain. |
| Swapped D5/D6 roles | r46swap44drop_a0_h L=5.006307788828618e-5, A=0.5208329663; r46swap45_a0_h L=4.320954929333763e-5, A=0.5117759954. Source-check/A-encoder changes dominate. |
Counterfactual diagnostics (diagnostics.json): making BC gate noise perfect removes 3.805739e-6 from baseline, 5.061666e-6 from R44, 10.355254e-6 from R45, 4.726312e-6 from R46; A removes 0.875607/4.247198/2.803366/1.049939e-6 respectively. Idle noise remains; effects overlap and are not additive cost allocations.

Verified versus inferred: every table price is a completed evaluator run on saved QASM; receipts include ordered data and evaluator hashes. CP UNSAT closes only encoded placement/footprint domains, not all possible circuits. First-order diagnostics for joint_s23_drop and r46fast44 are roundoff zero; excess loss is higher order.
Decision: kept prefix/r3 where geometry allowed, then built R44/R45/R46 layouts; expanded checks to all seven X stabilizers and one-/two-cell footprints. Both-A-and-r3 preservation was infeasible in the tested model; r3-only R44 was built.
Decision: used clean-only BC synthesis when the stronger robustness search yielded no circuit; full all-orders and judge checks remain the validity/performance tests. Encoder/CP objectives only rank proposals.
Decision: enforced A>=0.5002 for feasible-J greedy selection; unconstrained J rewards rejection above tau. Preserved those losing prices and bought acceptance before adding guards.
Decision: used equivalent detector-basis copies sparse_fast and sparse_r45 after saved-control reproduction; kept running evaluator copies immutable. Added process-safe ledger locking and per-hash receipts; reconstruct older complete runs from logs.
Decision: included relocated data-data identity pairs and measured initializations with propagated detector byproducts. Corrected CNOT direction parsing (Unit.qs sorts cells); all numerical claims use full evaluator results, including proposals made before correction.
Decision: redirected local R45 repair capacity to depth-preserving operation retiming of the improving R46 circuit. Also tested source detectors on measured initializations; nondeterministic proposals are rejected by the evaluator.
Decision: combined the independently successful q5 checked preparation and q14 final readout retiming, then priced the full combination. The finalist advances A14 measurement from tick 48 to 47 and retains 49 native ticks/390 CX. It uses the authorized R46 two-helper branch; no separate late X stabilizer check is included.
Final numerical verification: L improvement over tau is 5.365166765909933e-7, leaving 3.651667659099471e-8 below the requested threshold. The evaluator reports a sparse-kernel omission bound of 3.690417315070938e-14 (excluding floating-point roundoff). Judge PASS is the actual seed-0 1e6 verdict, not an inferred acceptance pass.
Positive stop: remaining GLOBAL searches were terminated by numeric PID and their exit was observed. Both hosts were checked for remaining GLOBAL search/evaluator processes; none remained. Negative exhaustion is neither needed nor claimed.
Decision: GLOBAL allocation <=8 zebra and <=8 Jerry until observed racer exit, then <=24 Jerry. No subagents, other hosts, GPUs, submissions, commits or pushes. Writes/temp outputs stay under GLOBAL; credentials were not accessed.
Files: results.json (full SHA256 keys); priced/ (receipts); builds/ and room/; cand/ (verified finalists only); logs/; diagnostics.json; enc/ and layouts/; builders/repairtools and evaluator copies. Interrupted/error evaluations are not prices; logs remain.
Full table of all 11,473 priced circuits: REPORT.full.md and results.json (local, not in git).
