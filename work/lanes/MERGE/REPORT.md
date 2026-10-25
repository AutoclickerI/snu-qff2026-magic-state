# MERGE — pass3 on v37d

Verdict: COMPLETE. tau=3.676346632406467e-05; finalist L<tau−5e-8, exact A≥.5002, judge gates_ok at1e6, single-process fast_check≤4.8s.
Best verified: [cand/merge3_final](cand/merge3_final.qasm), L=3.630560623406489e-05, A=0.5034645094225927, J_tau=-2.30516305595925e-07; gain vs v37d=4.5786009e-07.
SHA256 `e055c98eddbccdface98ee6bb3a45eec92c39aef78ee2e3b34eff6d626faae04`; judge median4.633s; limit4.8s is fixed to the supplied v37d3.2s reference. Loaded local baseline times do not relax it.
Final fast_check CLI: 4.711699s at1e6 shots/1process onhippo; gates_ok=True. 405CX,48native ticks. Archived original evaluator replay matches L and A exactly.
Completion: all seven BC3 module combinations and POLISH transports priced;1539 singles,1196 connected/contextual bundles, six complete greedy rounds with acceptance funding. Last-round gain2.787344985e-10<1e-9. Bulk prefix measurements were not required for the final gain. No submission, commit or push.

Source controls: v37d reproduced exactly; GLOBAL G3 reproduced3.676199483205871e-5,A=.5037245347586016; BC2-polish control3.7225517523299324e-5,A=.5046963821877385. Independent measured gain4.63523e-7 in GLOBAL’s exterior.
Footprint: G3 versus its BC2-polish control removes17/adds18 native units, touches36 qubit/tick cells and12 classical bits, replaces4 detector rows. Full diff: res37d/G3_diff.json. Relative to v37d, prefix measured preparations/readout shifts are independent repairs, not part of the resource core.
Transport: R45 q17/q23/q28/q29 changes reverse four resource edges and move the measured-plus source fromq17 toq28; allocate a fresh record and rebuild three B detector rows by their logical parity. The q26/q29 source records keep v37d meanings.
Transport: q18/q24 preparations advance to31, addCX24→18@32 andCX12→18@33, reverse two late18/24 edges. Remove competing known-zeroCX12→13@33. q3 branch advances its three resource gates by1 and removes competingCX3→4@39; retain v37d’s already-reused q3 source.

| BC3 modules on v37d | L | A | Delta vs v37d |
|---|---:|---:|---:|
| R | 3.683939074215e-05 | 0.502356013575 | +7.59244181e-08 |
| L | 3.660947677649e-05 | 0.501622168839 | -1.53989548e-07 |
| R+L | 3.668495982378e-05 | 0.501623416138 | -7.85065003e-08 |
| q3 | 3.667426938304e-05 | 0.501821165718 | -8.9196941e-08 |
| R+q3 | 3.652574742299e-05 | 0.501821763075 | -2.37718901e-07 |
| L+q3 | 3.65203146874e-05 | 0.501089347672 | -2.43151637e-07 |
| R+L+q3 | 3.637134950758e-05 | 0.501089943959 | -3.92116816e-07 |

Interaction: R alone loses7.59e-8; with q3 it gains. All seven nonempty combinations were priced; no additive gain assumption is used.
Measured-source port: eligible GLOBAL reset→measurement substitutions propagate the recorded Pauli byproduct through the actual merged circuit and XOR affected detector rows. q21@19 andq13@25 fail the stabilizer-output byproduct condition and remain resets. RX12@26 remains unchanged to avoid the known slow dispatch.
POLISH: latest source compared by native footprint against v37b; already-carried edits retained; surviving reversalCX21→15@34, prefix removals and retimed pair16→17 tested as complete combinations. Conflicting R46 guard timings are regenerated, not copied literally. Detailed outcomes under res37d/polish3*.
bc3polish_history: 6 complete greedy rounds; last gain2.787344985e-10, stop=True; L=3.6305606234065e-05, A=0.5034645094226.

| Greedy round | L | A | Gain in round | J_tau |
|---|---:|---:|---:|---:|
| bc3polish_history/1 | 3.633499996126e-05 | 0.500923527297 | 3.63495463e-08 | -2.146288818e-07 |
| bc3polish_history/2 | 3.632437512259e-05 | 0.500923248563 | 1.06248387e-08 | -2.199509911e-07 |
| bc3polish_history/3 | 3.631533086718e-05 | 0.500424354986 | 9.0442554e-09 | -2.24257897e-07 |
| bc3polish_history/4 | 3.631069123709e-05 | 0.501091060291 | 4.6396301e-09 | -2.268815484e-07 |
| bc3polish_history/5 | 3.630588496856e-05 | 0.501257239183 | 4.80626852e-09 | -2.29365967e-07 |
| bc3polish_history/6 | 3.630560623406e-05 | 0.503464509423 | 2.78734499e-10 | -2.305163056e-07 |
Runtime diagnosis: Same-host matched1e6 controls on hippo: GLOBAL G3 8.853s versus prefix-reset control 5.243s; loss cost only5.7591e-10. Both have zero general-path atoms, so the matched intervention attributes substantial residual cost to measured preparations (the precise inner-loop cost is inferred, not profiled), distinct from the MX12@26 catastrophic dispatch. R45 core 4.798s; all measured sources 6.760s; R45+POLISH without bulk source conversions 4.886s. Loaded zebra reached86/64 load and inflated incumbent timings; final greedy speed tests run on hippo with v37d controls, while the absolute4.8s cap is unchanged.

Greedy: regenerated all singles, connected positive/cheap-buyer pairs, additions unlocked by freeing edits, then full-price joint extensions and funding until gain<1e-9. Rank feasible candidates byA(L−tau). A speed rejection excludes promotion, never changes the numerical receipt.
Evaluator speed repair: q11 read/reset fusion invalidated the prior warm detector basis (replay width14). Trained a width8 basis, reproduced the full candidate price exactly, stopped only this lane’s identified evaluator PIDs, observed their exit, and resumed pending tasks from completed hash-keyed receipts. Basis files and control receipts are retained; no numerical objective or check was changed.
Evaluator refinement now trains the cheapest replay once instead of retraining every stored warm basis; all73 moments still contract exactly. A difficult saved case replayed its recorded loss under the change, and the final circuit matches the archived original evaluator. Profiling and both source versions are retained.
Provenance correction: updating the evaluator file while an old module remained loaded mislabeled172 hashes when its driver recomputed a version key. Stopped the old process tree, archived original metadata, and rekeyed343 receipts/cache entries to the actual loaded original core. Numerical values were unchanged; the incumbent was independently repriced after restart. res37d/provenance_correction.json and archive/provenance_fix3/.
Finalization correction: hippo’s older fast_check CLI omits the gates_ok text field. Its passed=True run was valid; the handoff parser now checks the actual rep.correct_ok structured result. The complete final CLI run satisfies correctness and4.8s without relaxing either check.
Verified: saved QASM+data mapping and SHA256 for every numerical claim; native schedule/adjacency and exact ideal checks; candidate judge correctness and measured1e6 speed. All factor/kernel omission bounds and evaluator hashes are retained.
Inferred only: finite menu transport/search coverage, no global optimality claim. Short sampler timings and static zero-general-atom status diagnose speed; only full single-process1e6 judge times qualify candidates.
Scope: only MERGE written; hippo≤24 processes including controller, zebra≤4; BLAS/OpenMP caps1; no subagents/GPU/submission/commit/push/credential access. Heavy local jobs ended before search moved to hippo when zebra became overfull. Host allocations are for this pass, not new standing rules.
Ledger: 6119 pass3 hashes;14817 total. [Full table](priced_circuits.md), [results.json](results.json), v37d/,res37d/,logs37d/,cand/. Prior evidence archived in archive/.
