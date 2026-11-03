# PREFIX2_20261027 checkpoint

Checkpoint: 2026-10-27. Prefix searches and native resource searches are recorded below. The lane has produced complete native 48-tick circuits that pass raw correctness and the full single-Pauli audit. Late scheduling restores noisy acceptance above 0.5, but the measured loss remains worse than the incumbent. No result in this report establishes SOTA.

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

## Native resource work after the prefix search

The four-square ending initially required simultaneous preparation of a sparse A block and a correlated B/C block. Treating them as separate measured-helper modules exposed a real scheduling cycle: the A factory borrows B/C cells 3, 9, 12 and 13, while the B/C factory needs A cells 4 and 18 as bridges. `measured_resource.py` therefore synthesizes the complete dual-A/BC CSS state and permits spare cells to retain copied parities. Measuring those spares in X produces known phase corrections; after the final A Hadamards, the corrections are A-X and B/C-Z, which can be incorporated into the terminal measurement records.

These native state witnesses are correct, but their noise can be poor. The first 84-CX joint witness passed the full raw-state test and had harmful-single coefficient 6.5333333. The shorter no-C rank-six witness has 59 CX and becomes ready at tick 50, but its coefficient is 27.1666667. The full assembled oracle and the independent Pauli audit agree on the latter coefficient. These candidates were rejected before expensive full pricing.

### Fast full-Pauli audit

`resource_pauli_audit.py` propagates both Pauli axes through the complete preparation and terminal, including the final A Hadamards and measurement-record corrections. It checks all fifteen two-qubit Pauli components, resets, single-qubit gates, measurement flips, measurement back-action noise, and waiting intervals. Its decoder rule matches the official independent CSS correction. It is a resource diagnostic with ideal incoming data; full source integration is still required.

The audit explicitly tests mixed Pauli components. Separate XX and ZZ checks can miss cancellation of two detector flips when a circuit uses A and B as each other's bridges. This was a practical failure mode of otherwise correct joint state preparations.

### B-only and connected-B searches

`b_resource.py` searches B-only encoders on the graph excluding the A outputs. It can preserve selected zero helper rows for MZ flags, start input variables on early available spare cells, and score each emitted module with the Pauli audit.

| Native resource family | Tested seeds | Best relevant result | Decision |
|---|---:|---|---|
| Joint rank-six, all spare outputs kept at zero | 12,000 | c1=1/6; first such retained witness ready at 75 | Too deep and still has harmful singles |
| Sparse B, target-cell input roots | 12,000 | 55 CX, ready 56, c1=0.4666667 | Rejected |
| Sparse B, arbitrary early input roots | 20,000 | 50 CX, ready 52, c1=1/3 | Rejected |
| Connected B after exchanging A/B roles | 20,000 | 18 CX, ready 48, c1=1/3 | Requires additional verification |
| END2 strict CP witness, independently imported here | Solver witness | **18 CX, ready 49, c1=0** | Full integration works; c2=88.8177778 is uncompetitive |

The connected B footprint is `[7,14,13,9,8,21,15]`. Its sparse A counterpart is `[12,26,25,11,3,28,17]`. This exchange follows the asymmetry of the final interactions: A phase errors occur before the B check, while B bit errors enter the data after the A check. A sparse A factory can therefore have a different protection requirement from a B factory on the same physical cells.

The final verified B descriptor is `b_connected_cp18.json`. It is derived from END2's `sol/a_flag_dual_R50_h0_1.json` by removing the final A Hadamards and the disconnected dummy q0 reset/read. The actual B preparation uses 18 native CXs. Its q1 MZ flag runs at tick 49, and can overlap the terminal operations on other qubits. The independent audit checks 621 Pauli components and reports c1=0. This coefficient is not an all-orders score.

An earlier 19-CX witness was reduced from readiness 54 to 52 by moving operations while preserving each wire's gate order. Exchanging commuting gates on shared wires reached readiness 51 but introduced c1=0.0666667. Equal noiseless unitary maps therefore do not establish equal noisy behavior.

### Tested repairs that did not help

`herald_resource.py` tests deterministic MZ reads during intervals when a spare cell's binary row is zero, optionally inserting one extra clock step. None of the eight leading sparse-B seeds improved its harmful-single coefficient in this screen.

A matched S/Sdg phase operation on a copied helper and the B qubit carrying the same parity was also tested. Sixteen candidate placements passed a positive-reference Stim state check, but the best coefficient remained 1/3. One invalid placement was rejected because it preceded the control's initialization. The probe is retained as diagnostic evidence, not as a candidate full circuit.

### Reproduce the verified B module

From the repository root:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .venv/bin/python work/lanes/PREFIX2_20261027/import_cp_resource.py

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  .venv/bin/python work/lanes/PREFIX2_20261027/resource_pauli_audit.py \
  work/lanes/PREFIX2_20261027/b_connected_cp18.json
```

The importer checks the native edges, physical time-slot collisions, exact CSS row space, zero helper outputs, and the full Pauli audit. It references NATIVE2's dual sparse-A prefix, whose changes preserve the connected-B release certificate.

NATIVE2 completed the full 390-CX, 51-tick circuit, `boundary/swapped_strong_b18_5c0762c512b06bb7_d6_20_19_10_2_22_16`. All six raw Steane stabilizers equal +1, raw infidelity is zero, and all 6,737 full-circuit single-fault components give c1=0. The exact second-order ledger, `swapped_strong_b18.pairs.json`, gives **c2=88.8177777778**. Correctable B bit faults survive the preparation and combine with a late B-to-data fault, producing a large accepted pair contribution. This measured mechanism closes the connected-B role-swap branch at the tested designs: detecting only harmful singles is insufficient, and the preparation must also suppress the single faults that become harmful in pairs. The complete working circuit is retained as evidence; it is not promoted as an improved candidate.

## Complete 48-tick factory integration

`retime_old_b.py` constructs an explicit native source and B factory that is ready for B-to-data at tick 46. The source cancels four specific CX pairs, moves the now-unblocked source operations, and preserves the fifteen T gates. The B module removes two of its fourteen initial CX32-to-26 parking gates and retains every other preparation operation and herald. Its original measurement identities remain attached to the retimed measurements. The complete weak-A circuit uses 376 CX and 48 ticks; all six raw Steane stabilizers are +1, raw infidelity is zero, and all 6,488 single-Pauli fault components are harmless after acceptance.

The first timing witness was not competitive: exact loss is 4.625027474185073e-5 and acceptance is 0.47277978136283605. The second-order coefficient is 39.2000000000. This is a complete working ideal-state/timing proof, but it fails the noisy acceptance requirement.

### Why the first schedule lost acceptance

The factory's earliest-start schedule prepared free helper cells near tick zero and left them waiting for source cells released near ticks 30–35. Moving resets to just before their next operation did not remove the exposure after early helper measurements and entangling gates. `b_exposure.py` uses the unchanged full-source Pauli model to measure the first-order rejection caused by each gate and waiting interval. The B waiting-noise coefficient was **102.0** in the initial 48-tick schedule, compared with **24.3333333** in the strong 49-tick control. B gate, reset and measurement rejection coefficients were unchanged.

`b_schedule.py` retains the exact operation order on every physical wire and schedules the preparation as late as its fixed deadline permits. Its optional CP objective minimizes the exact first-order rejection of all waiting intervals; this objective is a scheduling diagnostic, and each result is still checked with the full noisy evaluator. No wait or initialization noise is removed from the emitted circuit.

| Complete candidate | CX | Ticks | Raw / c1 | c2 | Exact loss | Exact acceptance |
|---|---:|---:|---|---:|---:|---:|
| Weak A, earliest B | 376 | 48 | Pass / 0 | 39.2000000 | 4.62502747419e-5 | 0.4727797814 |
| Strong A with RX9, late B | 376 | 48 | Pass / 0 | Not separately retained | 4.15299512900e-5 | 0.5051560121 |
| Strong A with source q9 herald, late B | 375 | 48 | Pass / 0 | 35.0300000 | Not priced separately | Not priced separately |
| Same q9-herald source, rejection-weighted B | 375 | 48 | Pass / 0 | 35.0300000 | 4.06936374726e-5 | 0.5063984900 |

The q9-herald source and A instrument are supplied by NATIVE2. The rejection-weighted B descriptor is `retimed/strong48_m9_b_reject46.json`; its complete circuit is NATIVE2's `boundary/strong48_m9_b_reject46_19527263ea6c98d0_d6_20_19_10_2_22_16`. It has c1=0 across 6,458 fault components. Its first-order total rejection coefficient is 681.0666667 and its B waiting-noise coefficient is 23.3333333. Those coefficients are not substitutes for exact loss or acceptance.

### Measurement acceptance policy

The two benign physical record modes accepted by the incumbent must be preserved through retiming. The current B descriptor uses `allow_record_faults` with the original measurement selectors 352 and 376. The assembler resolves their actual retimed operations, verifies that their faults have no source-rotation or data effect, and projects the complete detector space orthogonal to those physical fault vectors. Simply ignoring records 352 and 376 is incorrect: it can retain the same detector rank while changing the accepted detector space. Every current 48-tick descriptor uses the physical-mode policy and retains `original_bit` metadata.

Use `checkpoint_resources.py` to refresh the hashed manifest after these resource results. It preserves the earlier prefix checkpoint and follows the selected circuit, source and module dependencies. Do not use the older prefix-only `checkpoint.py` to overwrite this report's later resource findings.

### Further clock reduction and rejected pair repairs

`b_ready45.py` produces a B factory whose final B-to-C verification gates run at tick 44 and whose helper measurements run at tick 45. It uses 106 CX. The source advances its q28 preparation, seven q28-to-q22 CX gates and q28 readout by one tick. It also advances the q4-to-q5 and q4-to-q10 transfers and the following q4/q5 reads by one tick. These source changes preserve every gate and each physical wire's operation order. The initial B CX3-to-4, whose control is ideally zero at that boundary, is omitted and the complete source/resource circuit is revalidated.

The module is `retimed/b45_alap_b_module.json`; its source is `retimed/b45_source_4e3346193ca9dd50_d6_20_19_10_2_22_16`. Integration with the existing A instrument is raw-correct and gives c1=0 over 6,454 fault components. That integration still takes 48 ticks because A delays B-to-data until tick 46. Its c2=45.0333333 includes an additional exposed B waiting step and is not evidence of a competitive 47-tick circuit. A readout compatible with B-to-data at tick 45 is the remaining timing dependency.

Two source parking restorations fit the 48-tick deadline. Restoring CX12-to-13 at ticks 29 and 30, with MX12 at 31, preserves q12 release at 32. END2 also supplies a source schedule that restores the q19-to-q25 pair while releasing q25 at 30. Each restoration and their combination pass full raw and c1 checks. Their c2 remains 35.03 on the tested A/B baseline; no pair-order improvement was observed.

`data_b_parking.py` screened 36 legal pairs of identical native CX gates between data and B cells. Every intervening operation commutes exactly with the inserted pair, proving an ideal identity. The candidates all pass the full single-Pauli audit, but none improves the CP-A baseline c2=35.0133333. The best tested pair gives 35.6266667. A wide D6-to-B12 pair at ticks 38 and 43 gives 42.6488889: storage faults on B can be transferred back to data during the interval. The complete ledger is `retimed/data_b_cp48/results.json`. These are rejected noise repairs, not candidate improvements.

### Pair-cost scheduling checkpoint

`b_pair_schedule.py` derives the marginal accepted two-fault cost of an additional waiting step after each B/source operation from the full fault-pair ledger. It preserves every B wire's gate order, caps the first-order rejection coefficient, and uses CP to choose times inside a specified local window. The proposed circuit is then checked with the complete raw, single-fault and pair evaluators; a linear objective value is never reported as a physical loss.

The first run used NATIVE2's complete 369-CX, 47-tick `full47_q15_early39_cut3_ba6cf344b3e5e904_d6_20_19_10_2_22_16`. Its c2 is 34.9711111. Within a two-tick timing window, the optimizer advanced only the three benign helper reads already identified by the rejection objective: M33 from 35 to 33, M32 from 45 to 43, and M31 from 45 to 43. The full raw and c1 checks pass, but c2 is unchanged. This is a bounded marginal-search result, not a global schedule optimum. The generator and receipt are retained as `b_pair_schedule.py` and `retimed/b_pair47.result.json` before further scheduling work.

`b_quadratic_schedule.py` then constructed the complete quadratic accepted-pair numerator for every waiting duration permitted by that same fixed B wire order. It contains 41 variable waiting segments and one nonzero quadratic coupling. Both the reference polynomial and the emitted optimized circuit match the independent full fault-pair ledger to numerical precision. CP proves an optimum of c2=34.9711111 under the fixed source/A/terminal schedule and a cap on first-order rejection. The integer coefficient scale is reconstructed from the measured coefficients, with its rounding error explicitly bounded in the receipt. This closes timing-only improvements in that scope: a lower pair coefficient requires a changed gate order, gate set, source, A instrument, terminal, or acceptance tradeoff. The proof does not apply to such changes. The full receipt is `retimed/b_quadratic47.result.json`.
