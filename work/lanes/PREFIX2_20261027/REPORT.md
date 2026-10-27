# PREFIX2_20261027 checkpoint

Checkpoint: 2026-10-27T09:27:20.548083+00:00. Prefix searches are checkpointed; the lane is moving to native B/C resource synthesis. No candidate here beats the incumbent.

## Measured candidates

All losses below are the all-orders expectation at p=0.001. Acceptance must be at least 0.5002. The incumbent is L=3.58709500347e-5. The 15-T phase polynomial and the fifth detection coordinate are preserved. Additional flags use Clifford operations only.

| Family | Full loss L | Acceptance A | Full CX | Native ticks | c1 audit | Candidate |
|---|---:|---:|---:|---:|---|---|
| dynamic_schedule | 7.81576076591e-05 | 0.6298608979 | 153 | 38 | 0 | dynamic11_schedule_e0_d1 |
| flag6 | 8.08603222531e-05 | 0.6493069167 | 141 | 39 | 0 | flag6_012_random2 |
| dynamic9 | 8.39436056695e-05 | 0.6170338146 | 158 | 46 | 0 | dynamic9_8_random2 |
| bell | 8.45418152099e-05 | 0.6822164711 | ? | ? | not in family-best row | bell_r1_0_25678ba0c6d1db37_d0_20_7_10_3_22_21 |
| flagged_terminal | 8.9937312562e-05 | 0.6974267616 | ? | ? | 0 | flagterm_e6_d2_h1_86e7734830fa18c7_d0_20_7_10_3_22_21 |
| dynamic11 | 9.17572372319e-05 | 0.6232988551 | 153 | 43 | 0 | dynamic11_5_first0 |
| pairnet | 9.30271649967e-05 | 0.6639347916 | 137 | 36 | 0 | pairnet_000_first |
| guarded_layer | 0.000105282278392 | 0.5898852905 | 158 | 54 | 0 | guardlayer_2_first0 |
| guarded | 0.000109444468475 | 0.5944926303 | 153 | 53 | 0 | guarded_009_first0 |
| temporal_guard | 0.000126258963006 | 0.5345378754 | ? | ? | not in family-best row | guarded_temporal_r3_i11_2cf3ffd5662fea45_d0_20_7_10_3_22_21 |
| guardgeo11S | 0.000136218883642 | 0.5459890313 | 155 | 59 | 0 | guardgeo11S_2_first0 |
| terminal_plus | 0.000142993735258 | 0.6654168748 | ? | ? | 0 | terminal_plus_000_parallel_fbdfd51fbecb1dc0_d0_20_7_10_3_22_21 |

## Findings that determine the next work

1. The compact native 134-CX source/control has exact L=8.48960074708e-5, A=0.68901191635. Its accepted second-order loss coefficient is 70.0036111. Fault-pair attribution is in base_pairs.json.
2. Bell-pair meters targeted at copied computational rows preserve raw validity and c1=0, but improve the compact source only to approximately 8.20e-5. These meters are physical, adjacent, and fully noisy; no ideal measurement is used in candidate circuits.
3. A sixth Clifford flag with the original fifteen phase axes gives 8.08603222531e-5. Fresh flag periods and native reset scheduling improve this to 7.81576076591e-5, acceptance 0.62986089791, at 153 CX and 38 native ticks. It is a measured improvement over the 134-CX redesign, not over the incumbent.
4. Restricting every non-target intermediate parity to carry the sixth flag, then measuring that flag whenever it becomes a physical plus factor, removes the large pure-Z complementary-pair mechanism. The price is longer coherent arithmetic. The audited 154-CX example has second-order coefficient 84.3295833, dominated by X/Y histories and the terminal round. These facts do not prove all guarded constructions fail.
5. Fifteen simultaneous phase cells are native and valid in the constructed witnesses, but preparing all fifteen rows creates long exposed complementary Z histories. The original wide example has second-order coefficient 181.4077778; its largest single grouped pair contributes 73.6 p^2. Exact-kernel-weighted preparation improves that family to roughly 1.25e-4, still far worse than the incumbent. Early flag/herald readout and early transfers were tested separately.
6. Replacing the terminal A ancilla by a jointly synthesized 11-CX, six-layer encoder with a two-CX logical-X decoder is native, raw-valid, and c1=0, but yields 8.99e-5 on its tested source. The three pure-Z parity-only version loses the logical-X check and is worse. The original terminal A structure remains the better measured choice for this source.
7. Fresh-flag relocation was tested on nine and eleven source cells (three search seeds each, 72 phase variants and eight scheduling controls). Once the sixth coordinate factorizes on a physical qubit, MX followed by reset removes it. A later RX can introduce an independent flag on any available zero cell. This keeps separate time-slice records without a coherent SWAP. dynamic_guard.py synthesizes these resets and native CX gates together, checks raw validity and singles, and ranks by the unchanged qtools all-orders evaluator. dynamic_schedule.py removes unused initial and discarded-state resets and tests individual wire release. Every scheduled control passed raw validity and had c1=0.
8. The best fresh-flag candidate has exact second-order coefficient 57.9402777778, versus 70.0036111111 for the original compact source. Its largest grouped accepted pair is now below 1 p^2. The three largest terminal time-pair groups contribute 22.8666667, 4.2933333, and 2.24 p^2; the largest source groups are X/Y propagation histories. Evidence: dynamic_pairs.json. Further changes require an identified physical mechanism; the next assignment is native B/C preparation for the independently developed rank-eight four-square ending.

## Scope and controls

- Every full candidate uses ordinary native gates. Raw checks require adjacency and the six final Steane stabilizers, ideal acceptance, and ideal logical fidelity. A c1 audit is a diagnostic only; the ranking is the full all-orders loss.
- ideal_precheck.py is explicitly a counterfactual diagnostic. It inserts noiseless nonlocal checks while preserving original source-channel noise. Its outputs are not legal candidates. Both ideal X/Z prechecks before transfer lower the compact source to 5.44729e-5; this establishes that fixed source checks alone leave a substantial suffix contribution.
- CP-SAT UNKNOWN and beam-search exhaustion are budget outcomes, not impossibility proofs. The failed scopes include the tested geometry, hard row restrictions, fixed 112-CX transfer/suffix, and bounded repair; none excludes a different native source or tail.
- No submission, commit, push, qtools edit, or judge edit was made by this lane.

## Reproduction and selected handoff

Run from the repository root with `.venv/bin/python` and `PYTHONPATH=work/tools:upstream/snu-qff2026-problem`; set OMP/OPENBLAS/MKL thread counts to 1. Use `.venv/bin/python -m qtools price <stem> --processes 1`. The repository runtime qtools version recorded by the exact receipts is `94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f`.

`selected_files.json` contains SHA-256 hashes for the generators, exact ledgers, network descriptors, chosen full QASM/JSON candidates, and exact old-prefix/T14 dependencies. `checkpoint_results.json` is the machine-readable family table at this timestamp. `reproduce_dynamic.py` rebuilt six representative family winners byte-for-byte; `reproduction.json` records their exact QASM hashes. Run `checkpoint.py` after new results to update this checkpoint. The full candidate metadata embeds its network descriptor.
