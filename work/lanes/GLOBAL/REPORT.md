# GLOBAL

Verdict: COMPLETE — residual B/C finalist improves the supplied v37g incumbent.
Selection: lowest exact L at exact A>=0.5002. Current tau=3.6211236525327396e-05; J is diagnostic only. The previous J-selected R46 campaign remains archived in phase2/REPORT_R46.md.
Finalist: [cand/global_v37g_bcflip.qasm](cand/global_v37g_bcflip.qasm), L=3.6190305632615202e-05, A=0.50032228639581333, gain=2.0930892712194536e-08, J_v37g=-1.0472192098070637e-08.
SHA256 10f7b7cd5522c0670541f92addd3b3baaa4a44c73dded7c8099fd2f7a56e8eb8. Parent v37g SHA256 79fc464667ef82bc8b9b9113a5807a1d9459132e4a4f72fb8a8e68ceaaf6645c.
What moved: CX25->24 becomes CX24->25 at native tick36 (zero based), just before checked M25@37. Semantic diff confirms exactly one reversal, unchanged detector rows,406CX and48 native ticks.
Judge: gates_ok=True and passed=True at1e6;14.4s during concurrent evaluation. Ideal A=1,L=0,all six output stabilizers +1; full single-fault coefficient2.79e-19 with no harmful singles. Logs bind QASM hashes and ordered output metadata.
Paired same-core1e6 sampling, reversed order: incumbent mean10.867736s, candidate9.344156s. Zero general-path atoms. Host load affects absolute time; paired raw timings: logs/runtime_pinned_v37g_port.json.
Control: v37g reproduces L=3.621123652543765e-5,A=0.5035268387133264; loss differs from the supplied receipt by1.10e-16. Numerical ties within1e-13 are resolved by the simplest edit.

B/C resource:
All6636 archived R46 synthesis states were priced:4629 BC2,1960 actual-release BC3,47 wider fresh witnesses; every archived Pareto point included. Hard/decoder-safe/robust contracts, actual releases, extended windows and65-CX warm starts are recorded in bc2/,bc3/.
R46 best: cand/global_bc3_final.qasm, L=3.662135985101407e-5,A=0.5009568267260757,75 core CX. Full INTEG and retime passes flattened on both74/75-CX branches; both100-pair funding menus added no gain. Five further full116-buyer passes each returned to the selected parent price.
MERGE had already absorbed the initial BC3 resource. Residual transport on v37g:19 complete circuits built;12 pass raw ideal checks and are priced,7 fail deterministic detector15 (expectation0). Valid combinations cover Bell-source swaps, the middle CNOT reversal and both late identity-pair reversals.
The middle reversal gives the entire measured gain2.09309e-8, while acceptance falls by0.0032045523 to0.5003222864. Other valid source/pair reversals tie within1.11e-16 loss. Larger75-CX port: q25 is occupied at30; dropping CX25->19@30 and advancing preparations violates its current prefix contract. No loss is claimed for invalid circuits.
Current packet: resource/best_resource.json and resource/README.md. Earlier75-CX encoder, actual sources, detector dependencies and full reference are preserved in resource/r46_resource75.json. Do not transplant that old schedule wholesale.

Late X checks:
Original fixed-block searches: borrowed ancilla/chain CP was infeasible within its stated source/endpoint domains;21 one-role moves and210 pair swaps provided no legal replacement. These certificates are not global impossibility results.
Physical initial-zero correction and data-to-data parity-fold expansion were tested. All72 CP witnesses were priced, including the wider commuting-T window. Best unrestricted data map L=4.8437722159384854e-5; best B/C-root check7.955072882883894e-5. None improved its parent.
R46 six-CNOT S3X: L=8.030460799742367e-5 versus matched control3.668085144086832e-5; folding ladder alone5.262374390529666e-5. Even noiseless added CX gives7.511006330428228e-5. It has ideal target and no harmful single faults: changed higher-order propagation/detection consumes the prize.
v37g matched test: retime/remove-one-helper-guard control L=3.626513449876476e-5,A=0.5031593707455638; four-CNOT folding ladder L=5.2281904782174e-5,A=0.5045911925993691. Full borrowed-root check violates detector34 (expectation0), so no numerical loss is claimed. v37g_late_* saves the tested circuits.
Fresh cats: earliest native finish52 (four extra ticks), S2 L=9.775353309153167e-4,A=0.4932937427347392; no-data-coupling timing control3.640350824151622e-4. Ideal added-cat floor1.2433160174013205e-4. Waiting and hooks dominate the phantom prize; retiring both helpers did not shorten those schedules.
R46 phantom checks remain references only: S12X matched gain1.566e-6 and S23X1.615e-6, with A below0.5002. Every phantom QASM is excluded from candidate selection.

Runtime and verification:
global_bc3_fast slowdown was diagnosed by controlled ablation: same-core1e6 means v37a4.469s, GLOBAL8.470s, restoring nine prefix MX preparations to RX4.628s with the same B/C core. Both original circuits have zero general-path calls. Prefix measured preparations cause most of the excess; exact internal cost allocation remains inferred. RUNTIME.md contains hashes and paired traces.
Separate slow-path exclusions are retained: MX12@26 took285.4s/1e6; the marginally better MZ2@36 price took387.4s/1e6. The latter improves old loss only4.10e-11 and fails the documented20s promotion limit. Other static slow-path exclusions are labelled predictions.
Equivalent detector-basis refinement preserves byte-identical evaluator cores. Two difficult buyer prices reproduce exactly with refined bases (one389.8s->6.6s, another3.95s after training); cross-host speed differences are observational. All original receipts and validation logs remain.
Interrupted jobs: the earlier Jerry orphan was adopted and finished; after the03:22 disk interruption, no GLOBAL science jobs survived on either host. All required prior buyer jobs had exited. Only the small current-incumbent controls/ports were restarted.
Execution corrections retained: two earlier local batches briefly counted9 Python processes including launchers; subsequently fixed. Two early judge calls used the default repository cache; later caches were explicitly GLOBAL-local. No unrelated processes or out-of-lane files were removed.
Verified: saved-circuit all-orders prices, QASM SHA256, ordered data mapping, current raw ideal code space, final1e6 judge and single-fault certificate. Inferred/unproved: global optimality, unenumerated layouts, and performance after future unrelated merges.
Ledger: 37302 unique QASM hashes in results.json; complete table in priced_circuits.md. Historical J_tau in that ledger uses v37a; finalist.json and the current packet give J_v37g. No submissions, commits, pushes, agents, credentials or GPUs. Research writes remain in GLOBAL; caches are pruned after validation.
Files: finalist.json; resource/best_resource.json; logs/current_closure.json; logs/final_audit.json; RUNTIME.md; phase2/REPORT_R46.md; all circuits, receipts and failed-test logs retained.
