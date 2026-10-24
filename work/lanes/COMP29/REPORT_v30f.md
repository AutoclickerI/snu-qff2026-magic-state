SUPERSEDED: MAIN cancelled the v30f campaign and retargeted COMP29 to v34m. Pending jobs are not confirmations.

# COMP29 — v30f composition

**Status: RUNNING. Retargeted from v29c by MAIN.** Earlier artifacts and their incomplete evidence remain in `REPORT_v29c.md`; the v29c jobs were stopped by MAIN. No submission, commit, push, credential access or subagent use.

**Verified delivery:** [best.qasm](best.qasm) / [best.json](best.json) = `f_timing_mz_5_12`: **all-orders 5.68688901449e-05 (−3.51023% vs v30f), acceptance 0.506635004404, 194 CX, R48, FAST**. Independent unchanged exact2 confirms 5.62043e-05; three-seed 1e8 mean is 5.742882e-05, seed-0 acceptance 0.50664. Actual 1e6 judge time: 3.34 s. The per-combination reference sweep is still running; this delivery’s own checks are complete.

## Baseline audit

The task’s description of an older prefix is contradicted by the native files. v30f’s entire exterior before B/C preparation matches `ST1/v25k_exchange4` operation-for-operation and time-for-time (`v30_prefix_diff.json`). It already includes the full KNAP/PRESYN blue XZ check (q1/q2 at t28–41, detector bits c64/c67), the early verification checks, and the fused q4/q10 terminal exchange (CX4→10, CX10→4, MX4→c8, T†10). These are retained, not counted as added gains. FRESH’s `inputs/freshbase.json` names the exchange explicitly.

The retained resource is FRESH’s 57-CX clean correlated rank-three B/C preparation on its existing cells; B→C and A/data round stay at R48. v30f itself is 189 CX. Our emitted baseline is byte-identical to FRESH’s supplied `fast_zlast` winner (SHA-256 1cca56a2400030e25ae4210b0669092028a3f2e04e1118c912a03c0e6f5e621c). The inherited unchanged exact2 receipt is `f_base.inherited_exact.log`: 5.82393315e-5, acceptance proxy 0.5276872043. Supplied three-seed mean is 5.89438407e-5; newly run measurements are distinguished below.

## Composition and verification

Nine native choices: q15 four-CX instrument, imported ST1 prefix timing feedback, reviewer copy4, timing10, late q1 commute, extra early q19 X check, q11 reset→measure, final edge14→15, and an additional known-zero q13 measurement at t39. Copy4 is the reviewer readout copy itself. The existing q13 t40 check is preserved. The full compatible subset product is generated; structural incompatibilities have explicit receipts. The q15 retimer fixes the FRESH B/C native times and R48. Prefix feedback contains the 17 ST1 timing changes other than timing10, which is tested independently.

Every candidate receives a complete categorical-channel Fourier cubic screen from the unchanged exact2 model; no delta/additivity assumption is used. Independent unchanged `work/lanes/EVAL/exact2.py --third` CLI confirmations are labeled separately. The task’s shorter `work/EVAL/exact2.py` path does not exist. No incomplete CLI is claimed as confirmation. The first three new singleton CLI runs are q15, prefix feedback and copy4.

The all-orders evaluator is BCPOL’s unchanged five-projector extension, with its per-circuit channel/decoder/sector and nonzero-error validation. It runs only when the validated scope checks pass. Speed uses XTIM’s unchanged predictor; full 1e6 checks use fast_check; finalist means use MAIN/spec/mc3.py at 1e8 and seeds 0/1000/2000. Portable copies of those tools are byte-identical except their filesystem/cache location, under this lane.

Current receipts: 576 candidates; 574 screens; 117 direct CLI results; 43 proved-equivalent CLI prices; 522 judge/speed results; 3 all-orders results; 2 complete MC means.

| Stem | Edits | Third order | exp(−A1) | Exact2 CLI | Judge / acceptance | Speed s/1e6 | All-orders | MC mean |
|---|---|---:|---:|---|---|---|---:|---:|
| `f_frame_group_unfold4` | f_frame_group + joint q4 X-cat readout and Z initialization | 5.604395259e-05 | 0.5051857491 | pending | PASS / 0.504700 | FAST 7.82 | pending | pending |
| `f_unfold4` | f_timing_mz_5_12 + joint q4 X-cat readout and Z initialization | 5.604707481e-05 | 0.5067035819 | pending | PASS / 0.506175 | FAST 6.73 | pending | pending |
| `f_frame_group` | f_timing_mz_5_12 + measured BC initializations with stabilizer-frame constraints | 5.620113599e-05 | 0.5053541724 | pending | PASS / 0.505232 | FAST 7.14 | pending | pending |
| `f_frame13` | f_timing_mz_5_12 + q13 measured Z initialization with propagated X frame | 5.620425822e-05 | 0.507041497 | pending | PASS / 0.506137 | FAST 9.64 | pending | pending |
| `f_timing_mz_5_12` | f_timing_best_r2 + mzinit_5 + mzinit_12 | 5.620425822e-05 | 0.5068725113 | completed | PASS / 0.506279 | FAST 5.67 | 5.686889014e-05 | 5.742882e-05 |
| `f_timing_mz_5` | f_timing_best_r2 + mzinit_5 | 5.620554192e-05 | 0.5077180032 | pending | pending | pending | pending | pending |
| `f_edge_9_8` | f_timing_mz_5_12 + {"edge": [9, 8], "family": "readout", "move": "add_edge"} | 5.622835402e-05 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_timing_mz_19` | f_timing_best_r2 + mzinit_19 | 5.627412621e-05 | 0.4993024441 | pending | pending | pending | pending | pending |
| `f_timing_mz_12` | f_timing_best_r2 + mzinit_12 | 5.62744751e-05 | 0.5077180032 | pending | pending | pending | pending | pending |
| `f_edge_8_9` | f_timing_mz_5_12 + {"edge": [8, 9], "family": "readout", "move": "add_edge"} | 5.627552285e-05 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_timing_best` | fresh exact-loss timing feedback on f_c0df | 5.627575881e-05 | 0.5061984815 | pending | pending | pending | pending | pending |
| `f_timing_best_r2` | fresh exact-loss timing feedback on f_c0df | 5.627575881e-05 | 0.5085649054 | completed | PASS / 0.508021 | FAST 5.87 | 5.694074919e-05 | 5.731654e-05 |
| `f_phase_1` | f_timing_best_r2 + Tdag16_to_22 | 5.627641602e-05 | 0.5085628739 | pending | pending | pending | pending | pending |
| `f_edge_1_2` | f_timing_mz_5_12 + {"edge": [1, 2], "family": "readout", "move": "add_edge"} | 5.631607698e-05 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_2_8` | f_timing_mz_5_12 + {"edge": [2, 8], "family": "readout", "move": "add_edge"} | 5.631718134e-05 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_2_1` | f_timing_mz_5_12 + {"edge": [2, 1], "family": "readout", "move": "add_edge"} | 5.631763142e-05 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_8_2` | f_timing_mz_5_12 + {"edge": [8, 2], "family": "readout", "move": "add_edge"} | 5.632186056e-05 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edges_1_2_9_8` | f_timing_mz_5_12 + [1, 2] + [9, 8] | 5.634020119e-05 | 0.5060621637 | pending | pending | pending | pending | pending |
| `f_edges_2_1_9_8` | f_timing_mz_5_12 + [2, 1] + [9, 8] | 5.634155596e-05 | 0.5060621637 | pending | pending | pending | pending | pending |
| `f_edges_1_2_8_9` | f_timing_mz_5_12 + [1, 2] + [8, 9] | 5.638751643e-05 | 0.5060621637 | pending | pending | pending | pending | pending |
| `f_edges_2_1_8_9` | f_timing_mz_5_12 + [2, 1] + [8, 9] | 5.638867154e-05 | 0.5060621637 | pending | pending | pending | pending | pending |
| `f_timing_best_r1` | fresh exact-loss timing feedback on f_c0df | 5.649352797e-05 | 0.5104053363 | pending | pending | pending | pending | pending |
| `f_timing_best_r0` | fresh exact-loss timing feedback on f_c0df | 5.689848015e-05 | 0.5137876758 | pending | pending | pending | pending | pending |
| `f_c1df` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.733378237e-05 | 0.5171712981 | pending | PASS / 0.517222 | FAST 7.77 | pending | pending |
| `f_c0df` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q11measure + edge14to15 | 5.733378237e-05 | 0.5176887281 | completed | PASS / 0.517350 | FAST 9.75 | pending | pending |
| `f_c0ff` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | 5.733378237e-05 | 0.5168266322 | proved equivalent CLI | PASS / 0.516117 | FAST 7.48 | pending | pending |
| `f_c1ff` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.733378237e-05 | 0.5163100639 | pending | PASS / 0.515875 | FAST 5.45 | pending | pending |
| `f_c1d7` | instrument15 + prefix_feedback + copy4 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.736306446e-05 | 0.5171740527 | pending | PASS / 0.517250 | FAST 8.43 | pending | pending |
| `f_c0d7` | instrument15 + prefix_feedback + copy4 + commute1 + q11measure + edge14to15 | 5.736306446e-05 | 0.5176914854 | pending | PASS / 0.517139 | FAST 8.63 | pending | pending |
| `f_c0f7` | instrument15 + prefix_feedback + copy4 + commute1 + q19check + q11measure + edge14to15 | 5.736306446e-05 | 0.5168293849 | pending | PASS / 0.516972 | FAST 9.54 | pending | pending |
| `f_c1f7` | instrument15 + prefix_feedback + copy4 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.736306446e-05 | 0.5163128139 | pending | PASS / 0.515745 | FAST 5.58 | pending | pending |
| `f_c1de` | prefix_feedback + copy4 + timing10 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.743450938e-05 | 0.5174858201 | pending | PASS / 0.517419 | FAST 6.23 | pending | pending |
| `f_c0fe` | prefix_feedback + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | 5.743450938e-05 | 0.5171409445 | pending | PASS / 0.516412 | FAST 6.62 | pending | pending |
| `f_c0de` | prefix_feedback + copy4 + timing10 + commute1 + q11measure + edge14to15 | 5.743450938e-05 | 0.5180035648 | pending | PASS / 0.517730 | FAST 8.72 | pending | pending |
| `f_c1fe` | prefix_feedback + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.743450938e-05 | 0.5166240621 | pending | PASS / 0.516025 | FAST 11.19 | pending | pending |
| `f_c1cf` | instrument15 + prefix_feedback + copy4 + timing10 + q11measure + edge14to15 + zero_13_39 | 5.744536496e-05 | 0.5171706104 | pending | PASS / 0.516949 | FAST 8.19 | pending | pending |
| `f_c0cf` | instrument15 + prefix_feedback + copy4 + timing10 + q11measure + edge14to15 | 5.744536496e-05 | 0.5176880397 | pending | PASS / 0.517501 | FAST 8.47 | pending | pending |
| `f_c0ef` | instrument15 + prefix_feedback + copy4 + timing10 + q19check + q11measure + edge14to15 | 5.744536496e-05 | 0.5168259449 | pending | PASS / 0.516202 | FAST 8.38 | pending | pending |
| `f_c1ef` | instrument15 + prefix_feedback + copy4 + timing10 + q19check + q11measure + edge14to15 + zero_13_39 | 5.744536496e-05 | 0.5163093773 | pending | PASS / 0.515175 | FAST 6.08 | pending | pending |
| `f_c09f` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + edge14to15 | 5.744903425e-05 | 0.5185522621 | pending | PASS / 0.517780 | FAST 7.71 | pending | pending |
| `f_c1bf` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q19check + edge14to15 + zero_13_39 | 5.744903425e-05 | 0.5171712981 | pending | PASS / 0.516711 | FAST 7.51 | pending | pending |
| `f_c0bf` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q19check + edge14to15 | 5.744903425e-05 | 0.5176887281 | pending | PASS / 0.517547 | FAST 7.52 | pending | pending |
| `f_c19f` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + edge14to15 + zero_13_39 | 5.744903425e-05 | 0.518033969 | pending | PASS / 0.517100 | FAST 8.02 | pending | pending |
| `f_c17f` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q19check + q11measure + zero_13_39 | 5.745183362e-05 | 0.5167232772 | pending | PASS / 0.516101 | FAST 5.78 | pending | pending |
| `f_c15f` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q11measure + zero_13_39 | 5.745183362e-05 | 0.5175852007 | pending | PASS / 0.516413 | FAST 8.03 | pending | pending |
| `f_c07f` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q19check + q11measure | 5.745183362e-05 | 0.5172402589 | pending | PASS / 0.517016 | FAST 9.07 | pending | pending |
| `f_c05f` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q11measure | 5.745183362e-05 | 0.5181030448 | pending | PASS / 0.517460 | FAST 8.53 | pending | pending |
| `f_c1d6` | prefix_feedback + copy4 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.746387679e-05 | 0.5174885764 | pending | PASS / 0.517422 | FAST 7.52 | pending | pending |
| `f_c0f6` | prefix_feedback + copy4 + commute1 + q19check + q11measure + edge14to15 | 5.746387679e-05 | 0.517143699 | pending | PASS / 0.516171 | FAST 6.22 | pending | pending |
| `f_c0d6` | prefix_feedback + copy4 + commute1 + q11measure + edge14to15 | 5.746387679e-05 | 0.5180063238 | pending | PASS / 0.518231 | FAST 8.79 | pending | pending |
| `f_c1f6` | prefix_feedback + copy4 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.746387679e-05 | 0.5166268137 | pending | PASS / 0.516277 | FAST 8.34 | pending | pending |
| `f_c1c7` | instrument15 + prefix_feedback + copy4 + q11measure + edge14to15 + zero_13_39 | 5.747462172e-05 | 0.517173365 | pending | PASS / 0.516645 | FAST 8.01 | pending | pending |
| `f_c0c7` | instrument15 + prefix_feedback + copy4 + q11measure + edge14to15 | 5.747462172e-05 | 0.517690797 | pending | PASS / 0.517325 | FAST 7.94 | pending | pending |
| `f_c0e7` | instrument15 + prefix_feedback + copy4 + q19check + q11measure + edge14to15 | 5.747462172e-05 | 0.5168286976 | pending | PASS / 0.516621 | FAST 8.12 | pending | pending |
| `f_c1e7` | instrument15 + prefix_feedback + copy4 + q19check + q11measure + edge14to15 + zero_13_39 | 5.747462172e-05 | 0.5163121273 | pending | PASS / 0.516956 | FAST 6.10 | pending | pending |
| `f_c097` | instrument15 + prefix_feedback + copy4 + commute1 + edge14to15 | 5.747831634e-05 | 0.518555024 | pending | PASS / 0.518363 | FAST 8.15 | pending | pending |
| `f_c1b7` | instrument15 + prefix_feedback + copy4 + commute1 + q19check + edge14to15 + zero_13_39 | 5.747831634e-05 | 0.5171740527 | pending | PASS / 0.517202 | FAST 8.00 | pending | pending |
| `f_c0b7` | instrument15 + prefix_feedback + copy4 + commute1 + q19check + edge14to15 | 5.747831634e-05 | 0.5176914854 | pending | PASS / 0.516910 | FAST 7.60 | pending | pending |
| `f_c197` | instrument15 + prefix_feedback + copy4 + commute1 + edge14to15 + zero_13_39 | 5.747831634e-05 | 0.5180367282 | pending | PASS / 0.517617 | FAST 7.99 | pending | pending |
| `f_c177` | instrument15 + prefix_feedback + copy4 + commute1 + q19check + q11measure + zero_13_39 | 5.748108392e-05 | 0.5167260294 | pending | PASS / 0.516234 | FAST 6.16 | pending | pending |
| `f_c157` | instrument15 + prefix_feedback + copy4 + commute1 + q11measure + zero_13_39 | 5.748108392e-05 | 0.5175879575 | pending | PASS / 0.517099 | FAST 10.12 | pending | pending |
| `f_c077` | instrument15 + prefix_feedback + copy4 + commute1 + q19check + q11measure | 5.748108392e-05 | 0.5172430139 | pending | PASS / 0.516370 | FAST 8.27 | pending | pending |
| `f_c057` | instrument15 + prefix_feedback + copy4 + commute1 + q11measure | 5.748108392e-05 | 0.5181058043 | pending | PASS / 0.518239 | FAST 8.84 | pending | pending |
| `f_c0fb` | instrument15 + prefix_feedback + timing10 + commute1 + q19check + q11measure + edge14to15 | 5.748757957e-05 | 0.5222296763 | pending | PASS / 0.521718 | FAST 8.93 | pending | pending |
| `f_c0db` | instrument15 + prefix_feedback + timing10 + commute1 + q11measure + edge14to15 | 5.748757957e-05 | 0.5231007848 | pending | PASS / 0.522148 | FAST 6.61 | pending | pending |
| `f_c1db` | instrument15 + prefix_feedback + timing10 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.748757957e-05 | 0.5225779455 | pending | PASS / 0.522870 | FAST 8.43 | pending | pending |
| `f_c1fb` | instrument15 + prefix_feedback + timing10 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.748757957e-05 | 0.5217077076 | pending | PASS / 0.521285 | FAST 5.97 | pending | pending |
| `f_c0f3` | instrument15 + prefix_feedback + commute1 + q19check + q11measure + edge14to15 | 5.751686166e-05 | 0.5222324578 | pending | PASS / 0.521751 | FAST 8.04 | pending | pending |
| `f_c0d3` | instrument15 + prefix_feedback + commute1 + q11measure + edge14to15 | 5.751686166e-05 | 0.523103571 | pending | PASS / 0.522589 | FAST 6.75 | pending | pending |
| `f_c1d3` | instrument15 + prefix_feedback + commute1 + q11measure + edge14to15 + zero_13_39 | 5.751686166e-05 | 0.5225807288 | pending | PASS / 0.521978 | FAST 8.74 | pending | pending |
| `f_c1f3` | instrument15 + prefix_feedback + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.751686166e-05 | 0.5217104864 | pending | PASS / 0.521205 | FAST 5.82 | pending | pending |
| `f_c1ce` | prefix_feedback + copy4 + timing10 + q11measure + edge14to15 + zero_13_39 | 5.754566142e-05 | 0.517485132 | pending | PASS / 0.516293 | FAST 6.98 | pending | pending |
| `f_c0ee` | prefix_feedback + copy4 + timing10 + q19check + q11measure + edge14to15 | 5.754566142e-05 | 0.5171402569 | pending | PASS / 0.516101 | FAST 6.76 | pending | pending |
| `f_c0ce` | prefix_feedback + copy4 + timing10 + q11measure + edge14to15 | 5.754566142e-05 | 0.5180028759 | pending | PASS / 0.517454 | FAST 8.66 | pending | pending |
| `f_c1ee` | prefix_feedback + copy4 + timing10 + q19check + q11measure + edge14to15 + zero_13_39 | 5.754566142e-05 | 0.5166233751 | pending | PASS / 0.515827 | FAST 8.52 | pending | pending |
| `f_c0be` | prefix_feedback + copy4 + timing10 + commute1 + q19check + edge14to15 | 5.754976783e-05 | 0.5180035648 | pending | PASS / 0.517164 | FAST 6.35 | pending | pending |
| `f_c19e` | prefix_feedback + copy4 + timing10 + commute1 + edge14to15 + zero_13_39 | 5.754976783e-05 | 0.5183490156 | pending | PASS / 0.518128 | FAST 6.10 | pending | pending |
| `f_c09e` | prefix_feedback + copy4 + timing10 + commute1 + edge14to15 | 5.754976783e-05 | 0.5188676239 | pending | PASS / 0.519010 | FAST 9.81 | pending | pending |
| `f_c1be` | prefix_feedback + copy4 + timing10 + commute1 + q19check + edge14to15 + zero_13_39 | 5.754976783e-05 | 0.5174858201 | pending | PASS / 0.516644 | FAST 6.35 | pending | pending |
| `f_c05e` | prefix_feedback + copy4 + timing10 + commute1 + q11measure | 5.755270602e-05 | 0.5184181334 | pending | PASS / 0.518633 | FAST 8.74 | pending | pending |
| `f_c17e` | prefix_feedback + copy4 + timing10 + commute1 + q19check + q11measure + zero_13_39 | 5.755270602e-05 | 0.5170375267 | pending | PASS / 0.516848 | FAST 13.30 | pending | pending |
| `f_c15e` | prefix_feedback + copy4 + timing10 + commute1 + q11measure + zero_13_39 | 5.755270602e-05 | 0.5178999744 | pending | PASS / 0.518025 | FAST 6.56 | pending | pending |
| `f_c07e` | prefix_feedback + copy4 + timing10 + commute1 + q19check + q11measure | 5.755270602e-05 | 0.5175548228 | pending | PASS / 0.517093 | FAST 10.93 | pending | pending |
| `f_c08f` | instrument15 + prefix_feedback + copy4 + timing10 + edge14to15 | 5.75606205e-05 | 0.5185515725 | pending | PASS / 0.517899 | FAST 12.45 | pending | pending |
| `f_c1af` | instrument15 + prefix_feedback + copy4 + timing10 + q19check + edge14to15 + zero_13_39 | 5.75606205e-05 | 0.5171706104 | pending | PASS / 0.516972 | FAST 9.02 | pending | pending |
| `f_c0af` | instrument15 + prefix_feedback + copy4 + timing10 + q19check + edge14to15 | 5.75606205e-05 | 0.5176880397 | pending | PASS / 0.517302 | FAST 12.18 | pending | pending |
| `f_c18f` | instrument15 + prefix_feedback + copy4 + timing10 + edge14to15 + zero_13_39 | 5.75606205e-05 | 0.5180332801 | pending | PASS / 0.518163 | FAST 8.93 | pending | pending |
| `f_c16f` | instrument15 + prefix_feedback + copy4 + timing10 + q19check + q11measure + zero_13_39 | 5.756328433e-05 | 0.5167225901 | pending | PASS / 0.516000 | FAST 8.27 | pending | pending |
| `f_c14f` | instrument15 + prefix_feedback + copy4 + timing10 + q11measure + zero_13_39 | 5.756328433e-05 | 0.5175845124 | pending | PASS / 0.517404 | FAST 8.29 | pending | pending |
| `f_c06f` | instrument15 + prefix_feedback + copy4 + timing10 + q19check + q11measure | 5.756328433e-05 | 0.5172395711 | pending | PASS / 0.517171 | FAST 9.76 | pending | pending |
| `f_c04f` | instrument15 + prefix_feedback + copy4 + timing10 + q11measure | 5.756328433e-05 | 0.5181023558 | pending | PASS / 0.517821 | FAST 11.18 | pending | pending |
| `f_c11f` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + zero_13_39 | 5.75670855e-05 | 0.518448562 | pending | PASS / 0.518007 | FAST 10.23 | pending | pending |
| `f_c13f` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q19check + zero_13_39 | 5.75670855e-05 | 0.5175852007 | pending | PASS / 0.517189 | FAST 11.50 | pending | pending |
| `f_c01f` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 | 5.75670855e-05 | 0.5189672699 | pending | PASS / 0.518750 | FAST 8.15 | pending | pending |
| `f_c03f` | instrument15 + prefix_feedback + copy4 + timing10 + commute1 + q19check | 5.75670855e-05 | 0.5181030448 | pending | PASS / 0.517594 | FAST 11.67 | pending | pending |
| `f_c1c6` | prefix_feedback + copy4 + q11measure + edge14to15 + zero_13_39 | 5.757500351e-05 | 0.5174878882 | pending | PASS / 0.517349 | FAST 7.16 | pending | pending |
| `f_c0e6` | prefix_feedback + copy4 + q19check + q11measure + edge14to15 | 5.757500351e-05 | 0.5171430113 | pending | PASS / 0.516703 | FAST 6.79 | pending | pending |
| `f_c0c6` | prefix_feedback + copy4 + q11measure + edge14to15 | 5.757500351e-05 | 0.5180056349 | pending | PASS / 0.517647 | FAST 8.59 | pending | pending |
| `f_c1e6` | prefix_feedback + copy4 + q19check + q11measure + edge14to15 + zero_13_39 | 5.757500351e-05 | 0.5166261267 | pending | PASS / 0.516812 | FAST 7.86 | pending | pending |
| `f_c0b6` | prefix_feedback + copy4 + commute1 + q19check + edge14to15 | 5.757913524e-05 | 0.5180063238 | proved equivalent CLI | PASS / 0.516908 | FAST 5.97 | pending | pending |
| `f_c196` | prefix_feedback + copy4 + commute1 + edge14to15 + zero_13_39 | 5.757913524e-05 | 0.5183517765 | completed | PASS / 0.518032 | FAST 5.97 | pending | pending |
| `f_c096` | prefix_feedback + copy4 + commute1 + edge14to15 | 5.757913524e-05 | 0.5188703875 | completed | PASS / 0.518438 | FAST 5.96 | pending | pending |
| `f_c1b6` | prefix_feedback + copy4 + commute1 + q19check + edge14to15 + zero_13_39 | 5.757913524e-05 | 0.5174885764 | completed | PASS / 0.516157 | FAST 6.15 | pending | pending |
| `f_c056` | prefix_feedback + copy4 + commute1 + q11measure | 5.758205369e-05 | 0.5184208946 | completed | PASS / 0.518484 | FAST 8.22 | pending | pending |
| `f_c176` | prefix_feedback + copy4 + commute1 + q19check + q11measure + zero_13_39 | 5.758205369e-05 | 0.5170402806 | completed | PASS / 0.516582 | FAST 8.43 | pending | pending |
| `f_c156` | prefix_feedback + copy4 + commute1 + q11measure + zero_13_39 | 5.758205369e-05 | 0.5179027329 | completed | PASS / 0.517776 | FAST 5.89 | pending | pending |
| `f_c076` | prefix_feedback + copy4 + commute1 + q19check + q11measure | 5.758205369e-05 | 0.5175575794 | completed | PASS / 0.517309 | FAST 6.30 | pending | pending |
| `f_c0fa` | prefix_feedback + timing10 + commute1 + q19check + q11measure + edge14to15 | 5.758830658e-05 | 0.5225472746 | completed | PASS / 0.521703 | FAST 7.76 | pending | pending |
| `f_c1da` | prefix_feedback + timing10 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.758830658e-05 | 0.5228957555 | completed | PASS / 0.523058 | FAST 8.54 | pending | pending |
| `f_c1fa` | prefix_feedback + timing10 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.758830658e-05 | 0.5220249885 | completed | PASS / 0.522388 | FAST 7.87 | pending | pending |
| `f_c0da` | prefix_feedback + timing10 + commute1 + q11measure + edge14to15 | 5.758830658e-05 | 0.5234189128 | completed | PASS / 0.522299 | FAST 8.18 | pending | pending |
| `f_c087` | instrument15 + prefix_feedback + copy4 + edge14to15 | 5.758987727e-05 | 0.5185543344 | completed | PASS / 0.518698 | FAST 7.47 | pending | pending |
| `f_c1a7` | instrument15 + prefix_feedback + copy4 + q19check + edge14to15 + zero_13_39 | 5.758987727e-05 | 0.517173365 | completed | PASS / 0.516402 | FAST 7.52 | pending | pending |
| `f_c0a7` | instrument15 + prefix_feedback + copy4 + q19check + edge14to15 | 5.758987727e-05 | 0.517690797 | completed | PASS / 0.517190 | FAST 7.42 | pending | pending |
| `f_c187` | instrument15 + prefix_feedback + copy4 + edge14to15 + zero_13_39 | 5.758987727e-05 | 0.5180360393 | completed | PASS / 0.518106 | FAST 7.18 | pending | pending |
| `f_c167` | instrument15 + prefix_feedback + copy4 + q19check + q11measure + zero_13_39 | 5.759250949e-05 | 0.5167253422 | completed | PASS / 0.516513 | FAST 6.03 | pending | pending |
| `f_c147` | instrument15 + prefix_feedback + copy4 + q11measure + zero_13_39 | 5.759250949e-05 | 0.5175872692 | completed | PASS / 0.516705 | FAST 8.46 | pending | pending |
| `f_c067` | instrument15 + prefix_feedback + copy4 + q19check + q11measure | 5.759250949e-05 | 0.517242326 | completed | PASS / 0.516219 | FAST 8.34 | pending | pending |
| `f_c047` | instrument15 + prefix_feedback + copy4 + q11measure | 5.759250949e-05 | 0.5181051154 | completed | PASS / 0.517995 | FAST 8.22 | pending | pending |
| `f_c117` | instrument15 + prefix_feedback + copy4 + commute1 + zero_13_39 | 5.75963358e-05 | 0.5184513234 | completed | PASS / 0.518149 | FAST 7.38 | pending | pending |
| `f_c137` | instrument15 + prefix_feedback + copy4 + commute1 + q19check + zero_13_39 | 5.75963358e-05 | 0.5175879575 | proved equivalent CLI | PASS / 0.516525 | FAST 7.39 | pending | pending |
| `f_c017` | instrument15 + prefix_feedback + copy4 + commute1 | 5.75963358e-05 | 0.518970034 | completed | PASS / 0.518925 | FAST 7.34 | pending | pending |
| `f_c037` | instrument15 + prefix_feedback + copy4 + commute1 + q19check | 5.75963358e-05 | 0.5181058043 | proved equivalent CLI | PASS / 0.517860 | FAST 7.15 | pending | pending |
| `f_c0eb` | instrument15 + prefix_feedback + timing10 + q19check + q11measure + edge14to15 | 5.759919441e-05 | 0.5222289818 | proved equivalent CLI | PASS / 0.521442 | FAST 8.12 | pending | pending |
| `f_c0cb` | instrument15 + prefix_feedback + timing10 + q11measure + edge14to15 | 5.759919441e-05 | 0.5231000892 | completed | PASS / 0.522834 | FAST 6.36 | pending | pending |
| `f_c1cb` | instrument15 + prefix_feedback + timing10 + q11measure + edge14to15 + zero_13_39 | 5.759919441e-05 | 0.5225772506 | completed | PASS / 0.522416 | FAST 8.46 | pending | pending |
| `f_c1eb` | instrument15 + prefix_feedback + timing10 + q19check + q11measure + edge14to15 + zero_13_39 | 5.759919441e-05 | 0.5217070139 | proved equivalent CLI | PASS / 0.522102 | FAST 5.50 | pending | pending |
| `f_c1fd` | instrument15 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.759987626e-05 | 0.519235944 | proved equivalent CLI | PASS / 0.518921 | FAST 8.24 | pending | pending |
| `f_c0dd` | instrument15 + copy4 + timing10 + commute1 + q11measure + edge14to15 | 5.759987626e-05 | 0.520622421 | completed | PASS / 0.519154 | FAST 8.08 | pending | pending |
| `f_c1dd` | instrument15 + copy4 + timing10 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.759987626e-05 | 0.5201020588 | completed | PASS / 0.520403 | FAST 7.91 | pending | pending |
| `f_c0fd` | instrument15 + copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | 5.759987626e-05 | 0.5197554396 | proved equivalent CLI | PASS / 0.519664 | FAST 8.32 | pending | pending |
| `f_c0bb` | instrument15 + prefix_feedback + timing10 + commute1 + q19check + edge14to15 | 5.760371145e-05 | 0.5231007848 | proved equivalent CLI | PASS / 0.522543 | FAST 6.02 | pending | pending |
| `f_c09b` | instrument15 + prefix_feedback + timing10 + commute1 + edge14to15 | 5.760371145e-05 | 0.5239733464 | completed | PASS / 0.523444 | FAST 5.89 | pending | pending |
| `f_c1bb` | instrument15 + prefix_feedback + timing10 + commute1 + q19check + edge14to15 + zero_13_39 | 5.760371145e-05 | 0.5225779455 | proved equivalent CLI | PASS / 0.522266 | FAST 7.63 | pending | pending |
| `f_c19b` | instrument15 + prefix_feedback + timing10 + commute1 + edge14to15 + zero_13_39 | 5.760371145e-05 | 0.5234496349 | completed | PASS / 0.522763 | FAST 7.68 | pending | pending |
| `f_c07b` | instrument15 + prefix_feedback + timing10 + commute1 + q19check + q11measure | 5.760563082e-05 | 0.5226476272 | proved equivalent CLI | PASS / 0.522581 | FAST 7.94 | pending | pending |
| `f_c17b` | instrument15 + prefix_feedback + timing10 + commute1 + q19check + q11measure + zero_13_39 | 5.760563082e-05 | 0.5221252408 | proved equivalent CLI | PASS / 0.521725 | FAST 5.95 | pending | pending |
| `f_c05b` | instrument15 + prefix_feedback + timing10 + commute1 + q11measure | 5.760563082e-05 | 0.5235194329 | completed | PASS / 0.523373 | FAST 6.84 | pending | pending |
| `f_c15b` | instrument15 + prefix_feedback + timing10 + commute1 + q11measure + zero_13_39 | 5.760563082e-05 | 0.5229961751 | completed | PASS / 0.522744 | FAST 8.21 | pending | pending |
| `f_c0f2` | prefix_feedback + commute1 + q19check + q11measure + edge14to15 | 5.761767399e-05 | 0.5225500578 | pending | PASS / 0.521766 | FAST 8.55 | pending | pending |
| `f_c1d2` | prefix_feedback + commute1 + q11measure + edge14to15 + zero_13_39 | 5.761767399e-05 | 0.5228985406 | completed | PASS / 0.522889 | FAST 8.31 | pending | pending |
| `f_c1f2` | prefix_feedback + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.761767399e-05 | 0.5220277689 | proved equivalent CLI | PASS / 0.522287 | FAST 8.36 | pending | pending |
| `f_c0d2` | prefix_feedback + commute1 + q11measure + edge14to15 | 5.761767399e-05 | 0.5234217007 | pending | PASS / 0.523012 | FAST 8.42 | pending | pending |
| `f_c0e3` | instrument15 + prefix_feedback + q19check + q11measure + edge14to15 | 5.762845118e-05 | 0.5222317633 | pending | PASS / 0.522849 | FAST 8.52 | pending | pending |
| `f_c0c3` | instrument15 + prefix_feedback + q11measure + edge14to15 | 5.762845118e-05 | 0.5231028753 | pending | PASS / 0.522153 | FAST 6.50 | pending | pending |
| `f_c1c3` | instrument15 + prefix_feedback + q11measure + edge14to15 + zero_13_39 | 5.762845118e-05 | 0.5225800339 | pending | PASS / 0.521946 | FAST 7.98 | pending | pending |
| `f_c1e3` | instrument15 + prefix_feedback + q19check + q11measure + edge14to15 + zero_13_39 | 5.762845118e-05 | 0.5217097926 | pending | PASS / 0.521104 | FAST 5.87 | pending | pending |
| `f_c1f5` | instrument15 + copy4 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.762852432e-05 | 0.5192387095 | pending | PASS / 0.518917 | FAST 8.07 | pending | pending |
| `f_c0d5` | instrument15 + copy4 + commute1 + q11measure + edge14to15 | 5.762852432e-05 | 0.5206251939 | pending | PASS / 0.520543 | FAST 8.33 | pending | pending |
| `f_c1d5` | instrument15 + copy4 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.762852432e-05 | 0.520104829 | pending | PASS / 0.520362 | FAST 8.00 | pending | pending |
| `f_c0f5` | instrument15 + copy4 + commute1 + q19check + q11measure + edge14to15 | 5.762852432e-05 | 0.519758208 | pending | PASS / 0.519254 | FAST 7.94 | pending | pending |
| `f_c0b3` | instrument15 + prefix_feedback + commute1 + q19check + edge14to15 | 5.763299354e-05 | 0.523103571 | pending | PASS / 0.522469 | FAST 6.27 | pending | pending |
| `f_c093` | instrument15 + prefix_feedback + commute1 + edge14to15 | 5.763299354e-05 | 0.5239761372 | pending | PASS / 0.523218 | FAST 5.81 | pending | pending |
| `f_c1b3` | instrument15 + prefix_feedback + commute1 + q19check + edge14to15 + zero_13_39 | 5.763299354e-05 | 0.5225807288 | pending | PASS / 0.522149 | FAST 7.51 | pending | pending |
| `f_c193` | instrument15 + prefix_feedback + commute1 + edge14to15 + zero_13_39 | 5.763299354e-05 | 0.5234524229 | pending | PASS / 0.522868 | FAST 7.51 | pending | pending |
| `f_c073` | instrument15 + prefix_feedback + commute1 + q19check + q11measure | 5.763488112e-05 | 0.5226504109 | pending | PASS / 0.522484 | FAST 8.46 | pending | pending |
| `f_c173` | instrument15 + prefix_feedback + commute1 + q19check + q11measure + zero_13_39 | 5.763488112e-05 | 0.5221280217 | pending | PASS / 0.521239 | FAST 9.75 | pending | pending |
| `f_c053` | instrument15 + prefix_feedback + commute1 + q11measure | 5.763488112e-05 | 0.5235222212 | pending | PASS / 0.523036 | FAST 7.29 | pending | pending |
| `f_c153` | instrument15 + prefix_feedback + commute1 + q11measure + zero_13_39 | 5.763488112e-05 | 0.5229989607 | pending | PASS / 0.522482 | FAST 8.72 | pending | pending |
| `f_c0ae` | prefix_feedback + copy4 + timing10 + q19check + edge14to15 | 5.766092354e-05 | 0.5180028759 | pending | PASS / 0.517901 | FAST 7.13 | pending | pending |
| `f_c18e` | prefix_feedback + copy4 + timing10 + edge14to15 + zero_13_39 | 5.766092354e-05 | 0.5183483263 | pending | PASS / 0.517632 | FAST 5.97 | pending | pending |
| `f_c08e` | prefix_feedback + copy4 + timing10 + edge14to15 | 5.766092354e-05 | 0.5188669339 | pending | PASS / 0.518461 | FAST 6.55 | pending | pending |
| `f_c1ae` | prefix_feedback + copy4 + timing10 + q19check + edge14to15 + zero_13_39 | 5.766092354e-05 | 0.517485132 | pending | PASS / 0.517753 | FAST 6.08 | pending | pending |
| `f_c04e` | prefix_feedback + copy4 + timing10 + q11measure | 5.766372592e-05 | 0.518417444 | pending | PASS / 0.518356 | FAST 8.54 | pending | pending |
| `f_c16e` | prefix_feedback + copy4 + timing10 + q19check + q11measure + zero_13_39 | 5.766372592e-05 | 0.5170368391 | pending | PASS / 0.516965 | FAST 8.60 | pending | pending |
| `f_c14e` | prefix_feedback + copy4 + timing10 + q11measure + zero_13_39 | 5.766372592e-05 | 0.5178992857 | pending | PASS / 0.517853 | FAST 6.71 | pending | pending |
| `f_c06e` | prefix_feedback + copy4 + timing10 + q19check + q11measure | 5.766372592e-05 | 0.5175541346 | pending | PASS / 0.517696 | FAST 6.75 | pending | pending |
| `f_c13e` | prefix_feedback + copy4 + timing10 + commute1 + q19check + zero_13_39 | 5.766796448e-05 | 0.5178999744 | pending | PASS / 0.517574 | FAST 9.80 | pending | pending |
| `f_c01e` | prefix_feedback + copy4 + timing10 + commute1 | 5.766796448e-05 | 0.5192828841 | pending | PASS / 0.518959 | FAST 6.41 | pending | pending |
| `f_c11e` | prefix_feedback + copy4 + timing10 + commute1 + zero_13_39 | 5.766796448e-05 | 0.5187638607 | pending | PASS / 0.518787 | FAST 6.28 | pending | pending |
| `f_c03e` | prefix_feedback + copy4 + timing10 + commute1 + q19check | 5.766796448e-05 | 0.5184181334 | pending | PASS / 0.517876 | FAST 9.45 | pending | pending |
| `f_c10f` | instrument15 + prefix_feedback + copy4 + timing10 + zero_13_39 | 5.767853988e-05 | 0.5184478726 | pending | PASS / 0.518764 | FAST 11.01 | pending | pending |
| `f_c12f` | instrument15 + prefix_feedback + copy4 + timing10 + q19check + zero_13_39 | 5.767853988e-05 | 0.5175845124 | pending | PASS / 0.517302 | FAST 8.02 | pending | pending |
| `f_c00f` | instrument15 + prefix_feedback + copy4 + timing10 | 5.767853988e-05 | 0.5189665797 | pending | PASS / 0.518301 | FAST 7.79 | pending | pending |
| `f_c02f` | instrument15 + prefix_feedback + copy4 + timing10 + q19check | 5.767853988e-05 | 0.5181023558 | pending | PASS / 0.517478 | FAST 9.94 | pending | pending |
| `f_c0a6` | prefix_feedback + copy4 + q19check + edge14to15 | 5.769026563e-05 | 0.5180056349 | pending | PASS / 0.517057 | FAST 6.23 | pending | pending |
| `f_c186` | prefix_feedback + copy4 + edge14to15 + zero_13_39 | 5.769026563e-05 | 0.5183510872 | pending | PASS / 0.518248 | FAST 6.01 | pending | pending |
| `f_c086` | prefix_feedback + copy4 + edge14to15 | 5.769026563e-05 | 0.5188696975 | pending | PASS / 0.519474 | FAST 10.00 | pending | pending |
| `f_c1a6` | prefix_feedback + copy4 + q19check + edge14to15 + zero_13_39 | 5.769026563e-05 | 0.5174878882 | pending | PASS / 0.516963 | FAST 6.39 | pending | pending |
| `f_c046` | prefix_feedback + copy4 + q11measure | 5.769304845e-05 | 0.5184202053 | pending | PASS / 0.517598 | FAST 8.58 | pending | pending |
| `f_c166` | prefix_feedback + copy4 + q19check + q11measure + zero_13_39 | 5.769304845e-05 | 0.517039593 | pending | PASS / 0.517315 | FAST 8.44 | pending | pending |
| `f_c146` | prefix_feedback + copy4 + q11measure + zero_13_39 | 5.769304845e-05 | 0.5179020442 | pending | PASS / 0.516908 | FAST 6.97 | pending | pending |
| `f_c066` | prefix_feedback + copy4 + q19check + q11measure | 5.769304845e-05 | 0.5175568912 | pending | PASS / 0.517645 | FAST 6.33 | pending | pending |
| `f_c136` | prefix_feedback + copy4 + commute1 + q19check + zero_13_39 | 5.769731215e-05 | 0.5179027329 | pending | PASS / 0.516944 | FAST 8.33 | pending | pending |
| `f_c016` | prefix_feedback + copy4 + commute1 | 5.769731215e-05 | 0.5192856499 | pending | PASS / 0.518716 | FAST 6.28 | pending | pending |
| `f_c116` | prefix_feedback + copy4 + commute1 + zero_13_39 | 5.769731215e-05 | 0.5187666238 | pending | PASS / 0.518988 | FAST 6.97 | pending | pending |
| `f_c036` | prefix_feedback + copy4 + commute1 + q19check | 5.769731215e-05 | 0.5184208946 | pending | PASS / 0.517480 | FAST 6.17 | pending | pending |
| `f_c0ea` | prefix_feedback + timing10 + q19check + q11measure + edge14to15 | 5.769949087e-05 | 0.5225465797 | pending | PASS / 0.521588 | FAST 9.95 | pending | pending |
| `f_c1ca` | prefix_feedback + timing10 + q11measure + edge14to15 + zero_13_39 | 5.769949087e-05 | 0.5228950602 | pending | PASS / 0.522105 | FAST 8.72 | pending | pending |
| `f_c1ea` | prefix_feedback + timing10 + q19check + q11measure + edge14to15 + zero_13_39 | 5.769949087e-05 | 0.5220242943 | pending | PASS / 0.521658 | FAST 8.14 | pending | pending |
| `f_c0ca` | prefix_feedback + timing10 + q11measure + edge14to15 | 5.769949087e-05 | 0.5234182168 | pending | PASS / 0.523056 | FAST 9.09 | pending | pending |
| `f_c1dc` | copy4 + timing10 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.770107307e-05 | 0.5204183631 | pending | PASS / 0.519005 | FAST 5.96 | pending | pending |
| `f_c0dc` | copy4 + timing10 + commute1 + q11measure + edge14to15 | 5.770107307e-05 | 0.5209390418 | pending | PASS / 0.520294 | FAST 6.01 | pending | pending |
| `f_c1fc` | copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.770107307e-05 | 0.5195517216 | pending | PASS / 0.518974 | FAST 5.96 | pending | pending |
| `f_c0fc` | copy4 + timing10 + commute1 + q19check + q11measure + edge14to15 | 5.770107307e-05 | 0.5200715332 | pending | PASS / 0.519458 | FAST 6.51 | pending | pending |
| `f_c0ba` | prefix_feedback + timing10 + commute1 + q19check + edge14to15 | 5.770444504e-05 | 0.5234189128 | pending | PASS / 0.523055 | FAST 7.71 | pending | pending |
| `f_c19a` | prefix_feedback + timing10 + commute1 + edge14to15 + zero_13_39 | 5.770444504e-05 | 0.5237679751 | pending | PASS / 0.522608 | FAST 6.04 | pending | pending |
| `f_c09a` | prefix_feedback + timing10 + commute1 + edge14to15 | 5.770444504e-05 | 0.5242920051 | pending | PASS / 0.523263 | FAST 7.59 | pending | pending |
| `f_c1ba` | prefix_feedback + timing10 + commute1 + q19check + edge14to15 + zero_13_39 | 5.770444504e-05 | 0.5228957555 | pending | PASS / 0.521974 | FAST 7.22 | pending | pending |
| `f_c15a` | prefix_feedback + timing10 + commute1 + q11measure + zero_13_39 | 5.770650322e-05 | 0.5233142395 | pending | PASS / 0.522468 | FAST 8.56 | pending | pending |
| `f_c07a` | prefix_feedback + timing10 + commute1 + q19check + q11measure | 5.770650322e-05 | 0.5229654796 | pending | PASS / 0.522197 | FAST 8.34 | pending | pending |
| `f_c17a` | prefix_feedback + timing10 + commute1 + q19check + q11measure + zero_13_39 | 5.770650322e-05 | 0.5224427755 | pending | PASS / 0.521950 | FAST 8.46 | pending | pending |
| `f_c05a` | prefix_feedback + timing10 + commute1 + q11measure | 5.770650322e-05 | 0.5238378155 | pending | PASS / 0.523854 | FAST 8.39 | pending | pending |
| `f_c107` | instrument15 + prefix_feedback + copy4 + zero_13_39 | 5.770776503e-05 | 0.5184506339 | pending | PASS / 0.517135 | FAST 8.38 | pending | pending |
| `f_c127` | instrument15 + prefix_feedback + copy4 + q19check + zero_13_39 | 5.770776503e-05 | 0.5175872692 | pending | PASS / 0.517586 | FAST 7.66 | pending | pending |
| `f_c007` | instrument15 + prefix_feedback + copy4 | 5.770776503e-05 | 0.5189693439 | pending | PASS / 0.519047 | FAST 8.73 | pending | pending |
| `f_c027` | instrument15 + prefix_feedback + copy4 + q19check | 5.770776503e-05 | 0.5181051154 | pending | PASS / 0.517545 | FAST 8.77 | pending | pending |
| `f_c1ed` | instrument15 + copy4 + timing10 + q19check + q11measure + edge14to15 + zero_13_39 | 5.771267947e-05 | 0.5192352517 | pending | PASS / 0.518395 | FAST 8.54 | pending | pending |
| `f_c0cd` | instrument15 + copy4 + timing10 + q11measure + edge14to15 | 5.771267947e-05 | 0.5206217268 | pending | PASS / 0.519861 | FAST 8.29 | pending | pending |
| `f_c1cd` | instrument15 + copy4 + timing10 + q11measure + edge14to15 + zero_13_39 | 5.771267947e-05 | 0.5201013653 | pending | PASS / 0.520206 | FAST 8.36 | pending | pending |
| `f_c0ed` | instrument15 + copy4 + timing10 + q19check + q11measure + edge14to15 | 5.771267947e-05 | 0.5197547466 | pending | PASS / 0.519553 | FAST 8.64 | pending | pending |
| `f_c09d` | instrument15 + copy4 + timing10 + commute1 + edge14to15 | 5.77151427e-05 | 0.5214908485 | pending | PASS / 0.521031 | FAST 7.87 | pending | pending |
| `f_c19d` | instrument15 + copy4 + timing10 + commute1 + edge14to15 + zero_13_39 | 5.77151427e-05 | 0.5209696183 | pending | PASS / 0.520476 | FAST 7.78 | pending | pending |
| `f_c1bd` | instrument15 + copy4 + timing10 + commute1 + q19check + edge14to15 + zero_13_39 | 5.77151427e-05 | 0.5201020588 | pending | PASS / 0.519584 | FAST 7.68 | pending | pending |
| `f_c0bd` | instrument15 + copy4 + timing10 + commute1 + q19check + edge14to15 | 5.77151427e-05 | 0.520622421 | pending | PASS / 0.520572 | FAST 7.60 | pending | pending |
| `f_c0ab` | instrument15 + prefix_feedback + timing10 + q19check + edge14to15 | 5.771532995e-05 | 0.5231000892 | pending | PASS / 0.522922 | FAST 7.29 | pending | pending |
| `f_c08b` | instrument15 + prefix_feedback + timing10 + edge14to15 | 5.771532995e-05 | 0.5239726496 | pending | PASS / 0.523624 | FAST 6.17 | pending | pending |
| `f_c1ab` | instrument15 + prefix_feedback + timing10 + q19check + edge14to15 + zero_13_39 | 5.771532995e-05 | 0.5225772506 | pending | PASS / 0.522218 | FAST 8.30 | pending | pending |
| `f_c18b` | instrument15 + prefix_feedback + timing10 + edge14to15 + zero_13_39 | 5.771532995e-05 | 0.5234489388 | pending | PASS / 0.523001 | FAST 7.92 | pending | pending |
| `f_c06b` | instrument15 + prefix_feedback + timing10 + q19check + q11measure | 5.771711379e-05 | 0.5226469322 | pending | PASS / 0.522736 | FAST 8.17 | pending | pending |
| `f_c16b` | instrument15 + prefix_feedback + timing10 + q19check + q11measure + zero_13_39 | 5.771711379e-05 | 0.5221245465 | pending | PASS / 0.521251 | FAST 6.02 | pending | pending |
| `f_c04b` | instrument15 + prefix_feedback + timing10 + q11measure | 5.771711379e-05 | 0.5235187367 | pending | PASS / 0.522748 | FAST 7.01 | pending | pending |
| `f_c14b` | instrument15 + prefix_feedback + timing10 + q11measure + zero_13_39 | 5.771711379e-05 | 0.5229954796 | pending | PASS / 0.522335 | FAST 8.52 | pending | pending |
| `f_c01b` | instrument15 + prefix_feedback + timing10 + commute1 | 5.77217627e-05 | 0.5243926928 | pending | PASS / 0.524150 | FAST 6.20 | pending | pending |
| `f_c03b` | instrument15 + prefix_feedback + timing10 + commute1 + q19check | 5.77217627e-05 | 0.5235194329 | pending | PASS / 0.522584 | FAST 6.13 | pending | pending |
| `f_c11b` | instrument15 + prefix_feedback + timing10 + commute1 + zero_13_39 | 5.77217627e-05 | 0.5238685622 | pending | PASS / 0.523851 | FAST 8.10 | pending | pending |
| `f_c13b` | instrument15 + prefix_feedback + timing10 + commute1 + q19check + zero_13_39 | 5.77217627e-05 | 0.5229961751 | pending | PASS / 0.522916 | FAST 8.14 | pending | pending |
| `f_c05d` | instrument15 + copy4 + timing10 + commute1 + q11measure | 5.772686424e-05 | 0.5210390855 | pending | PASS / 0.520825 | FAST 8.20 | pending | pending |
| `f_c17d` | instrument15 + copy4 + timing10 + commute1 + q19check + q11measure + zero_13_39 | 5.772686424e-05 | 0.5196514989 | pending | PASS / 0.518265 | FAST 8.34 | pending | pending |
| `f_c07d` | instrument15 + copy4 + timing10 + commute1 + q19check + q11measure | 5.772686424e-05 | 0.5201714103 | pending | PASS / 0.519674 | FAST 8.36 | pending | pending |
| `f_c15d` | instrument15 + copy4 + timing10 + commute1 + q11measure + zero_13_39 | 5.772686424e-05 | 0.5205183069 | pending | PASS / 0.519922 | FAST 7.91 | pending | pending |
| `f_c0e2` | prefix_feedback + q19check + q11measure + edge14to15 | 5.772883296e-05 | 0.5225493629 | pending | PASS / 0.522344 | FAST 7.74 | pending | pending |
| `f_c1c2` | prefix_feedback + q11measure + edge14to15 + zero_13_39 | 5.772883296e-05 | 0.5228978453 | pending | PASS / 0.522507 | FAST 7.85 | pending | pending |
| `f_c1e2` | prefix_feedback + q19check + q11measure + edge14to15 + zero_13_39 | 5.772883296e-05 | 0.5220270747 | pending | PASS / 0.521397 | FAST 8.13 | pending | pending |
| `f_c0c2` | prefix_feedback + q11measure + edge14to15 | 5.772883296e-05 | 0.5234210047 | pending | PASS / 0.523026 | FAST 8.17 | pending | pending |
| `f_c1d4` | copy4 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.772980645e-05 | 0.520421135 | pending | PASS / 0.520381 | FAST 5.72 | pending | pending |
| `f_c0d4` | copy4 + commute1 + q11measure + edge14to15 | 5.772980645e-05 | 0.5209418164 | pending | PASS / 0.519978 | FAST 5.63 | pending | pending |
| `f_c1f4` | copy4 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.772980645e-05 | 0.5195544888 | pending | PASS / 0.519168 | FAST 5.85 | pending | pending |
| `f_c0f4` | copy4 + commute1 + q19check + q11measure + edge14to15 | 5.772980645e-05 | 0.5200743032 | pending | PASS / 0.519137 | FAST 6.12 | pending | pending |
| `f_c0b2` | prefix_feedback + commute1 + q19check + edge14to15 | 5.773381245e-05 | 0.5234217007 | pending | PASS / 0.522963 | FAST 7.44 | pending | pending |
| `f_c192` | prefix_feedback + commute1 + edge14to15 + zero_13_39 | 5.773381245e-05 | 0.5237707648 | pending | PASS / 0.523619 | FAST 6.34 | pending | pending |
| `f_c092` | prefix_feedback + commute1 + edge14to15 | 5.773381245e-05 | 0.5242947976 | pending | PASS / 0.523787 | FAST 7.51 | pending | pending |
| `f_c1b2` | prefix_feedback + commute1 + q19check + edge14to15 + zero_13_39 | 5.773381245e-05 | 0.5228985406 | pending | PASS / 0.522459 | FAST 7.49 | pending | pending |
| `f_c152` | prefix_feedback + commute1 + q11measure + zero_13_39 | 5.773585089e-05 | 0.5233170268 | pending | PASS / 0.523056 | FAST 7.95 | pending | pending |
| `f_c072` | prefix_feedback + commute1 + q19check + q11measure | 5.773585089e-05 | 0.5229682651 | pending | PASS / 0.522643 | FAST 8.21 | pending | pending |
| `f_c172` | prefix_feedback + commute1 + q19check + q11measure + zero_13_39 | 5.773585089e-05 | 0.5224455582 | pending | PASS / 0.521814 | FAST 8.23 | pending | pending |
| `f_c052` | prefix_feedback + commute1 + q11measure | 5.773585089e-05 | 0.5238406056 | pending | PASS / 0.522849 | FAST 8.08 | pending | pending |
| `f_c1e5` | instrument15 + copy4 + q19check + q11measure + edge14to15 + zero_13_39 | 5.774130189e-05 | 0.5192380172 | pending | PASS / 0.518946 | FAST 7.75 | pending | pending |
| `f_c0c5` | instrument15 + copy4 + q11measure + edge14to15 | 5.774130189e-05 | 0.5206244998 | pending | PASS / 0.520769 | FAST 8.17 | pending | pending |
| `f_c1c5` | instrument15 + copy4 + q11measure + edge14to15 + zero_13_39 | 5.774130189e-05 | 0.5201041355 | pending | PASS / 0.520130 | FAST 7.98 | pending | pending |
| `f_c0e5` | instrument15 + copy4 + q19check + q11measure + edge14to15 | 5.774130189e-05 | 0.5197575149 | pending | PASS / 0.520025 | FAST 8.05 | pending | pending |
| `f_c195` | instrument15 + copy4 + commute1 + edge14to15 + zero_13_39 | 5.774379076e-05 | 0.5209723931 | pending | PASS / 0.520905 | FAST 7.41 | pending | pending |
| `f_c095` | instrument15 + copy4 + commute1 + edge14to15 | 5.774379076e-05 | 0.5214936261 | pending | PASS / 0.521137 | FAST 7.14 | pending | pending |
| `f_c1b5` | instrument15 + copy4 + commute1 + q19check + edge14to15 + zero_13_39 | 5.774379076e-05 | 0.520104829 | pending | PASS / 0.519869 | FAST 7.61 | pending | pending |
| `f_c0b5` | instrument15 + copy4 + commute1 + q19check + edge14to15 | 5.774379076e-05 | 0.5206251939 | pending | PASS / 0.519309 | FAST 7.52 | pending | pending |
| `f_c0a3` | instrument15 + prefix_feedback + q19check + edge14to15 | 5.774458672e-05 | 0.5231028753 | pending | PASS / 0.522172 | FAST 6.12 | pending | pending |
| `f_c083` | instrument15 + prefix_feedback + edge14to15 | 5.774458672e-05 | 0.5239754404 | pending | PASS / 0.523342 | FAST 5.61 | pending | pending |
| `f_c1a3` | instrument15 + prefix_feedback + q19check + edge14to15 + zero_13_39 | 5.774458672e-05 | 0.5225800339 | pending | PASS / 0.522661 | FAST 7.75 | pending | pending |
| `f_c183` | instrument15 + prefix_feedback + edge14to15 + zero_13_39 | 5.774458672e-05 | 0.5234517269 | pending | PASS / 0.523196 | FAST 7.14 | pending | pending |
| `f_c063` | instrument15 + prefix_feedback + q19check + q11measure | 5.774633894e-05 | 0.5226497159 | pending | PASS / 0.521498 | FAST 8.36 | pending | pending |
| `f_c163` | instrument15 + prefix_feedback + q19check + q11measure + zero_13_39 | 5.774633894e-05 | 0.5221273274 | pending | PASS / 0.521861 | FAST 5.64 | pending | pending |
| `f_c043` | instrument15 + prefix_feedback + q11measure | 5.774633894e-05 | 0.5235215251 | pending | PASS / 0.522747 | FAST 6.14 | pending | pending |
| `f_c143` | instrument15 + prefix_feedback + q11measure + zero_13_39 | 5.774633894e-05 | 0.5229982652 | pending | PASS / 0.522801 | FAST 8.19 | pending | pending |
| `f_c013` | instrument15 + prefix_feedback + commute1 | 5.7751013e-05 | 0.5243954858 | pending | PASS / 0.523757 | FAST 6.07 | pending | pending |
| `f_c033` | instrument15 + prefix_feedback + commute1 + q19check | 5.7751013e-05 | 0.5235222212 | pending | PASS / 0.523610 | FAST 6.06 | pending | pending |
| `f_c113` | instrument15 + prefix_feedback + commute1 + zero_13_39 | 5.7751013e-05 | 0.5238713524 | completed | PASS / 0.523038 | FAST 7.47 | pending | pending |
| `f_c133` | instrument15 + prefix_feedback + commute1 + q19check + zero_13_39 | 5.7751013e-05 | 0.5229989607 | completed | PASS / 0.522786 | FAST 7.70 | pending | pending |
| `f_c0f9` | instrument15 + timing10 + commute1 + q19check + q11measure + edge14to15 | 5.775367347e-05 | 0.5251891023 | completed | PASS / 0.524936 | FAST 8.01 | pending | pending |
| `f_c1d9` | instrument15 + timing10 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.775367347e-05 | 0.5255393451 | completed | PASS / 0.524839 | FAST 6.30 | pending | pending |
| `f_c1f9` | instrument15 + timing10 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.775367347e-05 | 0.5246641757 | completed | PASS / 0.524915 | FAST 7.88 | pending | pending |
| `f_c0d9` | instrument15 + timing10 + commute1 + q11measure + edge14to15 | 5.775367347e-05 | 0.5260651473 | completed | PASS / 0.525915 | FAST 6.24 | pending | pending |
| `f_c055` | instrument15 + copy4 + commute1 + q11measure | 5.775556539e-05 | 0.5210418607 | completed | PASS / 0.519941 | FAST 8.01 | pending | pending |
| `f_c175` | instrument15 + copy4 + commute1 + q19check + q11measure + zero_13_39 | 5.775556539e-05 | 0.5196542667 | completed | PASS / 0.518582 | FAST 7.87 | pending | pending |
| `f_c155` | instrument15 + copy4 + commute1 + q11measure + zero_13_39 | 5.775556539e-05 | 0.5205210793 | completed | PASS / 0.519551 | FAST 8.00 | pending | pending |
| `f_c075` | instrument15 + copy4 + commute1 + q19check + q11measure | 5.775556539e-05 | 0.5201741809 | completed | PASS / 0.519914 | FAST 7.66 | pending | pending |
| `f_c12e` | prefix_feedback + copy4 + timing10 + q19check + zero_13_39 | 5.777898804e-05 | 0.5178992857 | completed | PASS / 0.517527 | FAST 5.92 | pending | pending |
| `f_c00e` | prefix_feedback + copy4 + timing10 | 5.777898804e-05 | 0.5192821935 | completed | PASS / 0.519215 | FAST 6.01 | pending | pending |
| `f_c10e` | prefix_feedback + copy4 + timing10 + zero_13_39 | 5.777898804e-05 | 0.5187631709 | completed | PASS / 0.518969 | FAST 5.76 | pending | pending |
| `f_c02e` | prefix_feedback + copy4 + timing10 + q19check | 5.777898804e-05 | 0.518417444 | completed | PASS / 0.518087 | FAST 5.43 | pending | pending |
| `f_c0f1` | instrument15 + commute1 + q19check + q11measure + edge14to15 | 5.778232153e-05 | 0.5251918995 | proved equivalent CLI | PASS / 0.524792 | FAST 8.07 | pending | pending |
| `f_c1d1` | instrument15 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.778232153e-05 | 0.5255421442 | completed | PASS / 0.525319 | FAST 5.85 | pending | pending |
| `f_c1f1` | instrument15 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.778232153e-05 | 0.5246669701 | proved equivalent CLI | PASS / 0.523687 | FAST 8.21 | pending | pending |
| `f_c0d1` | instrument15 + commute1 + q11measure + edge14to15 | 5.778232153e-05 | 0.5260679492 | completed | PASS / 0.525552 | FAST 6.26 | pending | pending |
| `f_c126` | prefix_feedback + copy4 + q19check + zero_13_39 | 5.780831057e-05 | 0.5179020442 | proved equivalent CLI | PASS / 0.517868 | FAST 5.77 | pending | pending |
| `f_c006` | prefix_feedback + copy4 | 5.780831057e-05 | 0.5192849594 | completed | PASS / 0.519196 | FAST 6.46 | pending | pending |
| `f_c106` | prefix_feedback + copy4 + zero_13_39 | 5.780831057e-05 | 0.518765934 | completed | PASS / 0.518459 | FAST 5.65 | pending | pending |
| `f_c026` | prefix_feedback + copy4 + q19check | 5.780831057e-05 | 0.5184202053 | proved equivalent CLI | PASS / 0.518019 | FAST 5.65 | pending | pending |
| `f_c1cc` | copy4 + timing10 + q11measure + edge14to15 + zero_13_39 | 5.781344583e-05 | 0.5204176692 | completed | PASS / 0.520396 | FAST 5.44 | pending | pending |
| `f_c0cc` | copy4 + timing10 + q11measure + edge14to15 | 5.781344583e-05 | 0.5209383472 | completed | PASS / 0.521028 | FAST 5.47 | pending | pending |
| `f_c1ec` | copy4 + timing10 + q19check + q11measure + edge14to15 + zero_13_39 | 5.781344583e-05 | 0.5195510288 | proved equivalent CLI | PASS / 0.519180 | FAST 6.04 | pending | pending |
| `f_c0ec` | copy4 + timing10 + q19check + q11measure + edge14to15 | 5.781344583e-05 | 0.5200708397 | proved equivalent CLI | PASS / 0.519569 | FAST 5.63 | pending | pending |
| `f_c0aa` | prefix_feedback + timing10 + q19check + edge14to15 | 5.7815633e-05 | 0.5234182168 | proved equivalent CLI | PASS / 0.522512 | FAST 7.05 | pending | pending |
| `f_c18a` | prefix_feedback + timing10 + edge14to15 + zero_13_39 | 5.7815633e-05 | 0.5237672786 | completed | PASS / 0.523726 | FAST 5.94 | pending | pending |
| `f_c08a` | prefix_feedback + timing10 + edge14to15 | 5.7815633e-05 | 0.5242913079 | completed | PASS / 0.524404 | FAST 7.45 | pending | pending |
| `f_c1aa` | prefix_feedback + timing10 + q19check + edge14to15 + zero_13_39 | 5.7815633e-05 | 0.5228950602 | proved equivalent CLI | PASS / 0.522126 | FAST 7.39 | pending | pending |
| `f_c1bc` | copy4 + timing10 + commute1 + q19check + edge14to15 + zero_13_39 | 5.781634609e-05 | 0.5204183631 | pending | PASS / 0.519703 | FAST 7.69 | pending | pending |
| `f_c09c` | copy4 + timing10 + commute1 + edge14to15 | 5.781634609e-05 | 0.5218079974 | completed | PASS / 0.521221 | FAST 7.20 | pending | pending |
| `f_c19c` | copy4 + timing10 + commute1 + edge14to15 + zero_13_39 | 5.781634609e-05 | 0.5212864503 | pending | PASS / 0.520468 | FAST 7.15 | pending | pending |
| `f_c0bc` | copy4 + timing10 + commute1 + q19check + edge14to15 | 5.781634609e-05 | 0.5209390418 | proved equivalent CLI | PASS / 0.520091 | FAST 7.92 | pending | pending |
| `f_c14a` | prefix_feedback + timing10 + q11measure + zero_13_39 | 5.781755537e-05 | 0.5233135436 | pending | PASS / 0.522943 | FAST 7.70 | pending | pending |
| `f_c06a` | prefix_feedback + timing10 + q19check + q11measure | 5.781755537e-05 | 0.5229647842 | pending | PASS / 0.522785 | FAST 7.49 | pending | pending |
| `f_c16a` | prefix_feedback + timing10 + q19check + q11measure + zero_13_39 | 5.781755537e-05 | 0.5224420808 | pending | PASS / 0.522282 | FAST 7.76 | pending | pending |
| `f_c04a` | prefix_feedback + timing10 + q11measure | 5.781755537e-05 | 0.5238371189 | pending | PASS / 0.522628 | FAST 7.96 | pending | pending |
| `f_c11a` | prefix_feedback + timing10 + commute1 + zero_13_39 | 5.782264168e-05 | 0.5241871572 | pending | PASS / 0.524111 | FAST 5.87 | pending | pending |
| `f_c03a` | prefix_feedback + timing10 + commute1 + q19check | 5.782264168e-05 | 0.5238378155 | pending | PASS / 0.523848 | FAST 6.88 | pending | pending |
| `f_c13a` | prefix_feedback + timing10 + commute1 + q19check + zero_13_39 | 5.782264168e-05 | 0.5233142395 | pending | PASS / 0.523000 | FAST 6.77 | pending | pending |
| `f_c01a` | prefix_feedback + timing10 + commute1 | 5.782264168e-05 | 0.5247116065 | pending | PASS / 0.524526 | FAST 7.06 | pending | pending |
| `f_c08d` | instrument15 + copy4 + timing10 + edge14to15 | 5.782794958e-05 | 0.5214901532 | pending | PASS / 0.520886 | FAST 7.16 | pending | pending |
| `f_c18d` | instrument15 + copy4 + timing10 + edge14to15 + zero_13_39 | 5.782794958e-05 | 0.5209689237 | pending | PASS / 0.520623 | FAST 7.51 | pending | pending |
| `f_c1ad` | instrument15 + copy4 + timing10 + q19check + edge14to15 + zero_13_39 | 5.782794958e-05 | 0.5201013653 | pending | PASS / 0.519554 | FAST 7.32 | pending | pending |
| `f_c0ad` | instrument15 + copy4 + timing10 + q19check + edge14to15 | 5.782794958e-05 | 0.5206217268 | pending | PASS / 0.519718 | FAST 7.43 | pending | pending |
| `f_c05c` | copy4 + timing10 + commute1 + q11measure | 5.782830703e-05 | 0.5213559598 | pending | PASS / 0.521109 | FAST 5.46 | pending | pending |
| `f_c07c` | copy4 + timing10 + commute1 + q19check + q11measure | 5.782830703e-05 | 0.5204877569 | pending | PASS / 0.520016 | FAST 5.56 | pending | pending |
| `f_c15c` | copy4 + timing10 + commute1 + q11measure + zero_13_39 | 5.782830703e-05 | 0.5208348644 | pending | PASS / 0.519820 | FAST 5.81 | pending | pending |
| `f_c17c` | copy4 + timing10 + commute1 + q19check + q11measure + zero_13_39 | 5.782830703e-05 | 0.5199675293 | pending | PASS / 0.519771 | FAST 5.59 | pending | pending |
| `f_c00b` | instrument15 + prefix_feedback + timing10 | 5.783324933e-05 | 0.5243919954 | pending | PASS / 0.524453 | FAST 5.47 | pending | pending |
| `f_c02b` | instrument15 + prefix_feedback + timing10 + q19check | 5.783324933e-05 | 0.5235187367 | pending | PASS / 0.523649 | FAST 5.84 | pending | pending |
| `f_c10b` | instrument15 + prefix_feedback + timing10 + zero_13_39 | 5.783324933e-05 | 0.5238678655 | pending | PASS / 0.523741 | FAST 6.98 | pending | pending |
| `f_c12b` | instrument15 + prefix_feedback + timing10 + q19check + zero_13_39 | 5.783324933e-05 | 0.5229954796 | pending | PASS / 0.522758 | FAST 7.44 | pending | pending |
| `f_c04d` | instrument15 + copy4 + timing10 + q11measure | 5.783956028e-05 | 0.5210383908 | pending | PASS / 0.520208 | FAST 7.48 | pending | pending |
| `f_c16d` | instrument15 + copy4 + timing10 + q19check + q11measure + zero_13_39 | 5.783956028e-05 | 0.5196508061 | pending | PASS / 0.519272 | FAST 8.41 | pending | pending |
| `f_c14d` | instrument15 + copy4 + timing10 + q11measure + zero_13_39 | 5.783956028e-05 | 0.5205176129 | pending | PASS / 0.519919 | FAST 8.11 | pending | pending |
| `f_c06d` | instrument15 + copy4 + timing10 + q19check + q11measure | 5.783956028e-05 | 0.5201707168 | pending | PASS / 0.520031 | FAST 7.77 | pending | pending |
| `f_c01d` | instrument15 + copy4 + timing10 + commute1 | 5.784213068e-05 | 0.5219082081 | pending | PASS / 0.521292 | FAST 7.12 | pending | pending |
| `f_c11d` | instrument15 + copy4 + timing10 + commute1 + zero_13_39 | 5.784213068e-05 | 0.5213865607 | pending | PASS / 0.521615 | FAST 7.18 | pending | pending |
| `f_c13d` | instrument15 + copy4 + timing10 + commute1 + q19check + zero_13_39 | 5.784213068e-05 | 0.5205183069 | pending | PASS / 0.519878 | FAST 7.64 | pending | pending |
| `f_c03d` | instrument15 + copy4 + timing10 + commute1 + q19check | 5.784213068e-05 | 0.5210390855 | pending | PASS / 0.520754 | FAST 7.40 | pending | pending |
| `f_c1c4` | copy4 + q11measure + edge14to15 + zero_13_39 | 5.784215356e-05 | 0.5204204411 | pending | PASS / 0.519655 | FAST 5.52 | pending | pending |
| `f_c0c4` | copy4 + q11measure + edge14to15 | 5.784215356e-05 | 0.5209411218 | pending | PASS / 0.520493 | FAST 5.68 | pending | pending |
| `f_c1e4` | copy4 + q19check + q11measure + edge14to15 + zero_13_39 | 5.784215356e-05 | 0.5195537961 | pending | PASS / 0.518663 | FAST 5.41 | pending | pending |
| `f_c0e4` | copy4 + q19check + q11measure + edge14to15 | 5.784215356e-05 | 0.5200736098 | pending | PASS / 0.519638 | FAST 5.64 | pending | pending |
| `f_c0a2` | prefix_feedback + q19check + edge14to15 | 5.784497509e-05 | 0.5234210047 | pending | PASS / 0.522603 | FAST 7.57 | pending | pending |
| `f_c182` | prefix_feedback + edge14to15 + zero_13_39 | 5.784497509e-05 | 0.5237700683 | pending | PASS / 0.522559 | FAST 6.21 | pending | pending |
| `f_c082` | prefix_feedback + edge14to15 | 5.784497509e-05 | 0.5242941004 | pending | PASS / 0.523760 | FAST 6.97 | pending | pending |
| `f_c1a2` | prefix_feedback + q19check + edge14to15 + zero_13_39 | 5.784497509e-05 | 0.5228978453 | pending | PASS / 0.522715 | FAST 7.03 | pending | pending |
| `f_c1b4` | copy4 + commute1 + q19check + edge14to15 + zero_13_39 | 5.784507947e-05 | 0.520421135 | pending | PASS / 0.520184 | FAST 7.51 | pending | pending |
| `f_c094` | copy4 + commute1 + edge14to15 | 5.784507947e-05 | 0.5218107767 | pending | PASS / 0.520971 | FAST 7.67 | pending | pending |
| `f_c0b4` | copy4 + commute1 + q19check + edge14to15 | 5.784507947e-05 | 0.5209418164 | pending | PASS / 0.519917 | FAST 7.71 | pending | pending |
| `f_c194` | copy4 + commute1 + edge14to15 + zero_13_39 | 5.784507947e-05 | 0.5212892268 | pending | PASS / 0.521029 | FAST 7.42 | pending | pending |
| `f_c142` | prefix_feedback + q11measure + zero_13_39 | 5.78468779e-05 | 0.5233163309 | pending | PASS / 0.523541 | FAST 7.98 | pending | pending |
| `f_c062` | prefix_feedback + q19check + q11measure | 5.78468779e-05 | 0.5229675696 | pending | PASS / 0.523185 | FAST 8.06 | pending | pending |
| `f_c162` | prefix_feedback + q19check + q11measure + zero_13_39 | 5.78468779e-05 | 0.5224448635 | pending | PASS / 0.522645 | FAST 8.15 | pending | pending |
| `f_c042` | prefix_feedback + q11measure | 5.78468779e-05 | 0.523839909 | pending | PASS / 0.522963 | FAST 7.74 | pending | pending |
| `f_c112` | prefix_feedback + commute1 + zero_13_39 | 5.785198935e-05 | 0.5241899491 | pending | PASS / 0.523368 | FAST 5.70 | pending | pending |
| `f_c032` | prefix_feedback + commute1 + q19check | 5.785198935e-05 | 0.5238406056 | pending | PASS / 0.523561 | FAST 7.30 | pending | pending |
| `f_c132` | prefix_feedback + commute1 + q19check + zero_13_39 | 5.785198935e-05 | 0.5233170268 | pending | PASS / 0.523123 | FAST 7.29 | pending | pending |
| `f_c012` | prefix_feedback + commute1 | 5.785198935e-05 | 0.5247144012 | pending | PASS / 0.524448 | FAST 6.97 | pending | pending |
| `f_c1f8` | timing10 + commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.785487028e-05 | 0.5249832545 | pending | PASS / 0.524379 | FAST 8.10 | pending | pending |
| `f_c1d8` | timing10 + commute1 + q11measure + edge14to15 + zero_13_39 | 5.785487028e-05 | 0.5258589561 | pending | PASS / 0.525513 | FAST 7.73 | pending | pending |
| `f_c0f8` | timing10 + commute1 + q19check + q11measure + edge14to15 | 5.785487028e-05 | 0.5255085003 | pending | PASS / 0.525157 | FAST 7.95 | pending | pending |
| `f_c0d8` | timing10 + commute1 + q11measure + edge14to15 | 5.785487028e-05 | 0.5263850781 | pending | PASS / 0.525588 | FAST 7.77 | pending | pending |
| `f_c085` | instrument15 + copy4 + edge14to15 | 5.785657199e-05 | 0.5214929307 | pending | PASS / 0.521385 | FAST 7.48 | pending | pending |
| `f_c185` | instrument15 + copy4 + edge14to15 + zero_13_39 | 5.785657199e-05 | 0.5209716985 | pending | PASS / 0.520125 | FAST 7.25 | pending | pending |
| `f_c1a5` | instrument15 + copy4 + q19check + edge14to15 + zero_13_39 | 5.785657199e-05 | 0.5201041355 | pending | PASS / 0.519408 | FAST 7.15 | pending | pending |
| `f_c0a5` | instrument15 + copy4 + q19check + edge14to15 | 5.785657199e-05 | 0.5206244998 | pending | PASS / 0.520117 | FAST 7.06 | pending | pending |
| `f_c054` | copy4 + commute1 + q11measure | 5.785710556e-05 | 0.5213587366 | pending | PASS / 0.520528 | FAST 5.80 | pending | pending |
| `f_c074` | copy4 + commute1 + q19check + q11measure | 5.785710556e-05 | 0.5204905291 | pending | PASS / 0.521088 | FAST 5.83 | pending | pending |
| `f_c154` | copy4 + commute1 + q11measure + zero_13_39 | 5.785710556e-05 | 0.5208376385 | pending | PASS / 0.519998 | FAST 5.23 | pending | pending |
| `f_c174` | copy4 + commute1 + q19check + q11measure + zero_13_39 | 5.785710556e-05 | 0.5199702987 | pending | PASS / 0.519966 | FAST 5.90 | pending | pending |
| `f_c003` | instrument15 + prefix_feedback | 5.786247448e-05 | 0.5243947885 | pending | PASS / 0.524092 | FAST 6.01 | pending | pending |
| `f_c023` | instrument15 + prefix_feedback + q19check | 5.786247448e-05 | 0.5235215251 | pending | PASS / 0.522686 | FAST 5.57 | pending | pending |
| `f_c103` | instrument15 + prefix_feedback + zero_13_39 | 5.786247448e-05 | 0.5238706558 | pending | PASS / 0.523251 | FAST 7.24 | pending | pending |
| `f_c123` | instrument15 + prefix_feedback + q19check + zero_13_39 | 5.786247448e-05 | 0.5229982652 | pending | PASS / 0.522100 | FAST 7.47 | pending | pending |
| `f_c0e9` | instrument15 + timing10 + q19check + q11measure + edge14to15 | 5.786650892e-05 | 0.525188402 | pending | PASS / 0.524301 | FAST 7.80 | pending | pending |
| `f_c1c9` | instrument15 + timing10 + q11measure + edge14to15 + zero_13_39 | 5.786650892e-05 | 0.5255386443 | pending | PASS / 0.525528 | FAST 5.98 | pending | pending |
| `f_c1e9` | instrument15 + timing10 + q19check + q11measure + edge14to15 + zero_13_39 | 5.786650892e-05 | 0.5246634761 | pending | PASS / 0.524354 | FAST 7.63 | pending | pending |
| `f_c0c9` | instrument15 + timing10 + q11measure + edge14to15 | 5.786650892e-05 | 0.5260644458 | pending | PASS / 0.525143 | FAST 6.07 | pending | pending |
| `f_c045` | instrument15 + copy4 + q11measure | 5.786823603e-05 | 0.521041166 | pending | PASS / 0.519642 | FAST 7.88 | pending | pending |
| `f_c165` | instrument15 + copy4 + q19check + q11measure + zero_13_39 | 5.786823603e-05 | 0.5196535738 | pending | PASS / 0.519271 | FAST 8.13 | pending | pending |
| `f_c145` | instrument15 + copy4 + q11measure + zero_13_39 | 5.786823603e-05 | 0.5205203853 | pending | PASS / 0.519951 | FAST 8.34 | pending | pending |
| `f_c065` | instrument15 + copy4 + q19check + q11measure | 5.786823603e-05 | 0.5201734873 | pending | PASS / 0.520378 | FAST 8.74 | pending | pending |
| `f_c199` | instrument15 + timing10 + commute1 + edge14to15 + zero_13_39 | 5.786981991e-05 | 0.5264159743 | pending | PASS / 0.526364 | FAST 5.68 | pending | pending |
| `f_c0b9` | instrument15 + timing10 + commute1 + q19check + edge14to15 | 5.786981991e-05 | 0.5260651473 | pending | PASS / 0.526203 | FAST 6.29 | pending | pending |
| `f_c099` | instrument15 + timing10 + commute1 + edge14to15 | 5.786981991e-05 | 0.5269426536 | pending | PASS / 0.526868 | FAST 5.47 | pending | pending |
| `f_c1b9` | instrument15 + timing10 + commute1 + q19check + edge14to15 + zero_13_39 | 5.786981991e-05 | 0.5255393451 | pending | PASS / 0.524516 | FAST 6.29 | pending | pending |
| `f_c015` | instrument15 + copy4 + commute1 | 5.787083183e-05 | 0.5219109879 | pending | PASS / 0.522152 | FAST 7.24 | pending | pending |
| `f_c115` | instrument15 + copy4 + commute1 + zero_13_39 | 5.787083183e-05 | 0.5213893378 | pending | PASS / 0.521062 | FAST 7.11 | pending | pending |
| `f_c035` | instrument15 + copy4 + commute1 + q19check | 5.787083183e-05 | 0.5210418607 | pending | PASS / 0.520931 | FAST 7.82 | pending | pending |
| `f_c135` | instrument15 + copy4 + commute1 + q19check + zero_13_39 | 5.787083183e-05 | 0.5205210793 | pending | PASS / 0.519404 | FAST 7.19 | pending | pending |
| `f_c159` | instrument15 + timing10 + commute1 + q11measure + zero_13_39 | 5.788066144e-05 | 0.5259599448 | pending | PASS / 0.524902 | FAST 5.74 | pending | pending |
| `f_c079` | instrument15 + timing10 + commute1 + q19check + q11measure | 5.788066144e-05 | 0.5256094216 | pending | PASS / 0.525888 | FAST 7.88 | pending | pending |
| `f_c059` | instrument15 + timing10 + commute1 + q11measure | 5.788066144e-05 | 0.5264861678 | pending | PASS / 0.525955 | FAST 6.13 | pending | pending |
| `f_c179` | instrument15 + timing10 + commute1 + q19check + q11measure + zero_13_39 | 5.788066144e-05 | 0.5250840749 | pending | PASS / 0.525081 | FAST 7.68 | pending | pending |
| `f_c1f0` | commute1 + q19check + q11measure + edge14to15 + zero_13_39 | 5.788360366e-05 | 0.5249860507 | pending | PASS / 0.524266 | FAST 7.67 | pending | pending |
| `f_c1d0` | commute1 + q11measure + edge14to15 + zero_13_39 | 5.788360366e-05 | 0.525861757 | pending | PASS / 0.525711 | FAST 7.77 | pending | pending |
| `f_c0f0` | commute1 + q19check + q11measure + edge14to15 | 5.788360366e-05 | 0.5255112993 | pending | PASS / 0.525089 | FAST 8.47 | pending | pending |
| `f_c0d0` | commute1 + q11measure + edge14to15 | 5.788360366e-05 | 0.5263878818 | pending | PASS / 0.526088 | FAST 7.84 | pending | pending |
| `f_c0e1` | instrument15 + q19check + q11measure + edge14to15 | 5.789513134e-05 | 0.5251911993 | pending | PASS / 0.525137 | FAST 8.08 | pending | pending |
| `f_c1c1` | instrument15 + q11measure + edge14to15 + zero_13_39 | 5.789513134e-05 | 0.5255414435 | pending | PASS / 0.525165 | FAST 6.45 | pending | pending |
| `f_c1e1` | instrument15 + q19check + q11measure + edge14to15 + zero_13_39 | 5.789513134e-05 | 0.5246662706 | pending | PASS / 0.523808 | FAST 8.29 | pending | pending |
| `f_c0c1` | instrument15 + q11measure + edge14to15 | 5.789513134e-05 | 0.5260672478 | pending | PASS / 0.526566 | FAST 6.03 | pending | pending |
| `f_c191` | instrument15 + commute1 + edge14to15 + zero_13_39 | 5.789846797e-05 | 0.5264187781 | pending | PASS / 0.525767 | FAST 5.71 | pending | pending |
| `f_c0b1` | instrument15 + commute1 + q19check + edge14to15 | 5.789846797e-05 | 0.5260679492 | pending | PASS / 0.525648 | FAST 5.69 | pending | pending |
| `f_c091` | instrument15 + commute1 + edge14to15 | 5.789846797e-05 | 0.5269454602 | pending | PASS / 0.526998 | FAST 5.70 | pending | pending |
| `f_c1b1` | instrument15 + commute1 + q19check + edge14to15 + zero_13_39 | 5.789846797e-05 | 0.5255421442 | pending | PASS / 0.524712 | FAST 5.82 | pending | pending |
| `f_c151` | instrument15 + commute1 + q11measure + zero_13_39 | 5.79093626e-05 | 0.5259627461 | pending | PASS / 0.525005 | FAST 6.30 | pending | pending |
| `f_c071` | instrument15 + commute1 + q19check + q11measure | 5.79093626e-05 | 0.5256122212 | pending | PASS / 0.525150 | FAST 8.04 | pending | pending |
| `f_c051` | instrument15 + commute1 + q11measure | 5.79093626e-05 | 0.526488972 | pending | PASS / 0.525062 | FAST 5.82 | pending | pending |
| `f_c171` | instrument15 + commute1 + q19check + q11measure + zero_13_39 | 5.79093626e-05 | 0.5250868717 | pending | PASS / 0.524583 | FAST 7.68 | pending | pending |
| `f_c1ac` | copy4 + timing10 + q19check + edge14to15 + zero_13_39 | 5.792872251e-05 | 0.5204176692 | pending | PASS / 0.519900 | FAST 7.82 | pending | pending |
| `f_c08c` | copy4 + timing10 + edge14to15 | 5.792872251e-05 | 0.5218073017 | pending | PASS / 0.521554 | FAST 7.26 | pending | pending |
| `f_c18c` | copy4 + timing10 + edge14to15 + zero_13_39 | 5.792872251e-05 | 0.5212857552 | pending | PASS / 0.520838 | FAST 7.63 | pending | pending |
| `f_c0ac` | copy4 + timing10 + q19check + edge14to15 | 5.792872251e-05 | 0.5209383472 | pending | PASS / 0.520707 | FAST 7.36 | pending | pending |
| `f_c10a` | prefix_feedback + timing10 + zero_13_39 | 5.793369749e-05 | 0.5241864601 | pending | PASS / 0.523623 | FAST 6.01 | pending | pending |
| `f_c02a` | prefix_feedback + timing10 + q19check | 5.793369749e-05 | 0.5238371189 | pending | PASS / 0.523115 | FAST 7.30 | pending | pending |
| `f_c12a` | prefix_feedback + timing10 + q19check + zero_13_39 | 5.793369749e-05 | 0.5233135436 | pending | PASS / 0.523177 | FAST 6.92 | pending | pending |
| `f_c00a` | prefix_feedback + timing10 | 5.793369749e-05 | 0.5247109087 | pending | PASS / 0.524739 | FAST 7.29 | pending | pending |
| `f_c04c` | copy4 + timing10 + q11measure | 5.794057225e-05 | 0.5213552646 | pending | PASS / 0.521046 | FAST 5.26 | pending | pending |
| `f_c06c` | copy4 + timing10 + q19check + q11measure | 5.794057225e-05 | 0.5204870629 | pending | PASS / 0.520426 | FAST 5.65 | pending | pending |
| `f_c14c` | copy4 + timing10 + q11measure + zero_13_39 | 5.794057225e-05 | 0.5208341699 | pending | PASS / 0.521030 | FAST 5.64 | pending | pending |
| `f_c16c` | copy4 + timing10 + q19check + q11measure + zero_13_39 | 5.794057225e-05 | 0.519966836 | pending | PASS / 0.520307 | FAST 5.48 | pending | pending |
| `f_c03c` | copy4 + timing10 + commute1 + q19check | 5.794358005e-05 | 0.5213559598 | pending | PASS / 0.520592 | FAST 7.71 | pending | pending |
| `f_c13c` | copy4 + timing10 + commute1 + q19check + zero_13_39 | 5.794358005e-05 | 0.5208348644 | pending | PASS / 0.521162 | FAST 7.71 | pending | pending |
| `f_c01c` | copy4 + timing10 + commute1 | 5.794358005e-05 | 0.5222256109 | pending | PASS / 0.521750 | FAST 7.31 | pending | pending |
| `f_c11c` | copy4 + timing10 + commute1 + zero_13_39 | 5.794358005e-05 | 0.5217036463 | pending | PASS / 0.521147 | FAST 7.51 | pending | pending |
| `f_c00d` | instrument15 + copy4 + timing10 | 5.795483038e-05 | 0.5219075122 | pending | PASS / 0.522208 | FAST 7.15 | pending | pending |
| `f_c10d` | instrument15 + copy4 + timing10 + zero_13_39 | 5.795483038e-05 | 0.5213858656 | pending | PASS / 0.520855 | FAST 7.21 | pending | pending |
| `f_c02d` | instrument15 + copy4 + timing10 + q19check | 5.795483038e-05 | 0.5210383908 | pending | PASS / 0.520656 | FAST 7.32 | pending | pending |
| `f_c12d` | instrument15 + copy4 + timing10 + q19check + zero_13_39 | 5.795483038e-05 | 0.5205176129 | pending | PASS / 0.520599 | FAST 7.08 | pending | pending |
| `f_c1a4` | copy4 + q19check + edge14to15 + zero_13_39 | 5.795743024e-05 | 0.5204204411 | pending | PASS / 0.520106 | FAST 7.40 | pending | pending |
| `f_c084` | copy4 + edge14to15 | 5.795743024e-05 | 0.521810081 | pending | PASS / 0.520597 | FAST 7.35 | pending | pending |
| `f_c0a4` | copy4 + q19check + edge14to15 | 5.795743024e-05 | 0.5209411218 | pending | PASS / 0.520307 | FAST 7.13 | pending | pending |
| `f_c184` | copy4 + edge14to15 + zero_13_39 | 5.795743024e-05 | 0.5212885317 | pending | PASS / 0.520298 | FAST 7.62 | pending | pending |
| `f_c102` | prefix_feedback + zero_13_39 | 5.796302002e-05 | 0.524189252 | pending | PASS / 0.523820 | FAST 5.90 | pending | pending |
| `f_c022` | prefix_feedback + q19check | 5.796302002e-05 | 0.523839909 | proved equivalent CLI | PASS / 0.523579 | FAST 7.52 | pending | pending |
| `f_c122` | prefix_feedback + q19check + zero_13_39 | 5.796302002e-05 | 0.5233163309 | pending | PASS / 0.523478 | FAST 7.04 | pending | pending |
| `f_prefix_feedback` | prefix_feedback | 5.796302002e-05 | 0.5247137035 | completed | PASS / 0.523776 | FAST 8.58 | pending | pending |
| `f_c1e8` | timing10 + q19check + q11measure + edge14to15 + zero_13_39 | 5.796727528e-05 | 0.5249825545 | pending | PASS / 0.525024 | FAST 8.00 | pending | pending |
| `f_c1c8` | timing10 + q11measure + edge14to15 + zero_13_39 | 5.796727528e-05 | 0.525858255 | pending | PASS / 0.525358 | FAST 8.05 | pending | pending |
| `f_c0e8` | timing10 + q19check + q11measure + edge14to15 | 5.796727528e-05 | 0.5255077997 | pending | PASS / 0.525286 | FAST 8.36 | pending | pending |
| `f_c0c8` | timing10 + q11measure + edge14to15 | 5.796727528e-05 | 0.5263843763 | pending | PASS / 0.525843 | FAST 8.19 | pending | pending |
| `f_c044` | copy4 + q11measure | 5.796934538e-05 | 0.5213580415 | pending | PASS / 0.520362 | FAST 5.45 | pending | pending |
| `f_c064` | copy4 + q19check + q11measure | 5.796934538e-05 | 0.5204898351 | pending | PASS / 0.520538 | FAST 5.81 | pending | pending |
| `f_c144` | copy4 + q11measure + zero_13_39 | 5.796934538e-05 | 0.520836944 | pending | PASS / 0.520770 | FAST 5.85 | pending | pending |
| `f_c164` | copy4 + q19check + q11measure + zero_13_39 | 5.796934538e-05 | 0.5199696054 | pending | PASS / 0.518810 | FAST 5.55 | pending | pending |
| `f_c198` | timing10 + commute1 + edge14to15 + zero_13_39 | 5.797102329e-05 | 0.5267361185 | pending | PASS / 0.525952 | FAST 5.68 | pending | pending |
| `f_c1b8` | timing10 + commute1 + q19check + edge14to15 + zero_13_39 | 5.797102329e-05 | 0.5258589561 | pending | PASS / 0.525697 | FAST 6.83 | pending | pending |
| `f_c0b8` | timing10 + commute1 + q19check + edge14to15 | 5.797102329e-05 | 0.5263850781 | pending | PASS / 0.525953 | FAST 7.92 | pending | pending |
| `f_c098` | timing10 + commute1 + edge14to15 | 5.797102329e-05 | 0.5272631181 | pending | PASS / 0.526572 | FAST 6.00 | pending | pending |
| `f_c034` | copy4 + commute1 + q19check | 5.797237858e-05 | 0.5213587366 | pending | PASS / 0.521152 | FAST 8.07 | pending | pending |
| `f_c134` | copy4 + commute1 + q19check + zero_13_39 | 5.797237858e-05 | 0.5208376385 | pending | PASS / 0.520219 | FAST 8.08 | pending | pending |
| `f_c014` | copy4 + commute1 | 5.797237858e-05 | 0.5222283924 | pending | PASS / 0.521558 | FAST 7.68 | pending | pending |
| `f_c114` | copy4 + commute1 + zero_13_39 | 5.797237858e-05 | 0.521706425 | pending | PASS / 0.520363 | FAST 7.49 | pending | pending |
| `f_c158` | timing10 + commute1 + q11measure + zero_13_39 | 5.798210423e-05 | 0.5262798116 | pending | PASS / 0.525854 | FAST 7.72 | pending | pending |
| `f_c178` | timing10 + commute1 + q19check + q11measure + zero_13_39 | 5.798210423e-05 | 0.5254034091 | pending | PASS / 0.524811 | FAST 8.12 | pending | pending |
| `f_c058` | timing10 + commute1 + q11measure | 5.798210423e-05 | 0.5268063547 | pending | PASS / 0.525950 | FAST 8.43 | pending | pending |
| `f_c078` | timing10 + commute1 + q19check + q11measure | 5.798210423e-05 | 0.5259290753 | pending | PASS / 0.525792 | FAST 8.15 | pending | pending |
| `f_c189` | instrument15 + timing10 + edge14to15 + zero_13_39 | 5.798265903e-05 | 0.5264152724 | pending | PASS / 0.526104 | FAST 5.97 | pending | pending |
| `f_c0a9` | instrument15 + timing10 + q19check + edge14to15 | 5.798265903e-05 | 0.5260644458 | pending | PASS / 0.525538 | FAST 6.32 | pending | pending |
| `f_c089` | instrument15 + timing10 + edge14to15 | 5.798265903e-05 | 0.526941951 | pending | PASS / 0.525875 | FAST 5.96 | pending | pending |
| `f_c1a9` | instrument15 + timing10 + q19check + edge14to15 + zero_13_39 | 5.798265903e-05 | 0.5255386443 | pending | PASS / 0.525543 | FAST 6.20 | pending | pending |
| `f_c005` | instrument15 + copy4 | 5.798350614e-05 | 0.521910292 | pending | PASS / 0.521278 | FAST 7.36 | pending | pending |
| `f_c105` | instrument15 + copy4 + zero_13_39 | 5.798350614e-05 | 0.5213886426 | pending | PASS / 0.521205 | FAST 8.52 | pending | pending |
| `f_c025` | instrument15 + copy4 + q19check | 5.798350614e-05 | 0.521041166 | pending | PASS / 0.521556 | FAST 7.67 | pending | pending |
| `f_c125` | instrument15 + copy4 + q19check + zero_13_39 | 5.798350614e-05 | 0.5205203853 | pending | PASS / 0.519708 | FAST 7.43 | pending | pending |
| `f_c149` | instrument15 + timing10 + q11measure + zero_13_39 | 5.799338973e-05 | 0.5259592435 | pending | PASS / 0.525062 | FAST 6.09 | pending | pending |
| `f_c069` | instrument15 + timing10 + q19check + q11measure | 5.799338973e-05 | 0.5256087208 | pending | PASS / 0.525735 | FAST 8.27 | pending | pending |
| `f_c049` | instrument15 + timing10 + q11measure | 5.799338973e-05 | 0.5264854658 | pending | PASS / 0.525707 | FAST 6.54 | pending | pending |
| `f_c169` | instrument15 + timing10 + q19check + q11measure + zero_13_39 | 5.799338973e-05 | 0.5250833748 | pending | PASS / 0.524500 | FAST 11.47 | pending | pending |
| `f_c1e0` | q19check + q11measure + edge14to15 + zero_13_39 | 5.799598301e-05 | 0.5249853507 | pending | PASS / 0.525175 | FAST 8.29 | pending | pending |
| `f_c1c0` | q11measure + edge14to15 + zero_13_39 | 5.799598301e-05 | 0.5258610558 | pending | PASS / 0.525377 | FAST 12.44 | pending | pending |
| `f_c0e0` | q19check + q11measure + edge14to15 | 5.799598301e-05 | 0.5255105986 | pending | PASS / 0.525222 | FAST 8.49 | pending | pending |
| `f_c0c0` | q11measure + edge14to15 | 5.799598301e-05 | 0.5263871799 | pending | PASS / 0.526738 | FAST 8.05 | pending | pending |
| `f_c039` | instrument15 + timing10 + commute1 + q19check | 5.799680788e-05 | 0.5264861678 | pending | PASS / 0.525519 | FAST 6.21 | pending | pending |
| `f_c119` | instrument15 + timing10 + commute1 + zero_13_39 | 5.799680788e-05 | 0.5268372756 | pending | PASS / 0.526741 | FAST 6.08 | pending | pending |
| `f_c139` | instrument15 + timing10 + commute1 + q19check + zero_13_39 | 5.799680788e-05 | 0.5259599448 | pending | PASS / 0.525663 | FAST 6.29 | pending | pending |
| `f_c019` | instrument15 + timing10 + commute1 | 5.799680788e-05 | 0.5273643763 | pending | PASS / 0.527298 | FAST 5.96 | pending | pending |
| `f_c190` | commute1 + edge14to15 + zero_13_39 | 5.799975668e-05 | 0.526738924 | pending | PASS / 0.525848 | FAST 6.15 | pending | pending |
| `f_c1b0` | commute1 + q19check + edge14to15 + zero_13_39 | 5.799975668e-05 | 0.525861757 | pending | PASS / 0.525058 | FAST 7.15 | pending | pending |
| `f_c0b0` | commute1 + q19check + edge14to15 | 5.799975668e-05 | 0.5263878818 | pending | PASS / 0.525883 | FAST 7.97 | pending | pending |
| `f_c090` | commute1 + edge14to15 | 5.799975668e-05 | 0.5272659264 | pending | PASS / 0.526950 | FAST 9.94 | pending | pending |
| `f_c150` | commute1 + q11measure + zero_13_39 | 5.801090276e-05 | 0.5262826147 | pending | PASS / 0.525885 | FAST 7.45 | pending | pending |
| `f_c170` | commute1 + q19check + q11measure + zero_13_39 | 5.801090276e-05 | 0.5254062076 | pending | PASS / 0.524866 | FAST 8.14 | pending | pending |
| `f_c050` | commute1 + q11measure | 5.801090276e-05 | 0.5268091606 | completed | PASS / 0.526423 | FAST 8.32 | pending | pending |
| `f_c070` | commute1 + q19check + q11measure | 5.801090276e-05 | 0.5259318766 | proved equivalent CLI | PASS / 0.525782 | FAST 9.40 | pending | pending |
| `f_c181` | instrument15 + edge14to15 + zero_13_39 | 5.801128144e-05 | 0.5264180762 | completed | PASS / 0.525584 | FAST 6.38 | pending | pending |
| `f_c0a1` | instrument15 + q19check + edge14to15 | 5.801128144e-05 | 0.5260672478 | proved equivalent CLI | PASS / 0.525324 | FAST 6.19 | pending | pending |
| `f_c081` | instrument15 + edge14to15 | 5.801128144e-05 | 0.5269447576 | completed | PASS / 0.526729 | FAST 5.70 | pending | pending |
| `f_c1a1` | instrument15 + q19check + edge14to15 + zero_13_39 | 5.801128144e-05 | 0.5255414435 | proved equivalent CLI | PASS / 0.525455 | FAST 5.96 | pending | pending |
| `f_c141` | instrument15 + q11measure + zero_13_39 | 5.802206548e-05 | 0.5259620449 | completed | PASS / 0.525907 | FAST 6.55 | pending | pending |
| `f_c061` | instrument15 + q19check + q11measure | 5.802206548e-05 | 0.5256115203 | proved equivalent CLI | PASS / 0.524583 | FAST 8.44 | pending | pending |
| `f_c041` | instrument15 + q11measure | 5.802206548e-05 | 0.52648827 | completed | PASS / 0.526894 | FAST 6.41 | pending | pending |
| `f_c161` | instrument15 + q19check + q11measure + zero_13_39 | 5.802206548e-05 | 0.5250861715 | proved equivalent CLI | PASS / 0.524499 | FAST 8.05 | pending | pending |
| `f_c031` | instrument15 + commute1 + q19check | 5.802550904e-05 | 0.526488972 | proved equivalent CLI | PASS / 0.526236 | FAST 6.19 | pending | pending |
| `f_c111` | instrument15 + commute1 + zero_13_39 | 5.802550904e-05 | 0.5268400816 | completed | PASS / 0.527067 | FAST 5.94 | pending | pending |
| `f_c131` | instrument15 + commute1 + q19check + zero_13_39 | 5.802550904e-05 | 0.5259627461 | proved equivalent CLI | PASS / 0.526198 | FAST 6.12 | pending | pending |
| `f_c011` | instrument15 + commute1 | 5.802550904e-05 | 0.5273671852 | completed | PASS / 0.527315 | FAST 5.77 | pending | pending |
| `f_c02c` | copy4 + timing10 + q19check | 5.805584893e-05 | 0.5213552646 | proved equivalent CLI | PASS / 0.520881 | FAST 8.16 | pending | pending |
| `f_c12c` | copy4 + timing10 + q19check + zero_13_39 | 5.805584893e-05 | 0.5208341699 | proved equivalent CLI | PASS / 0.520572 | FAST 9.36 | pending | pending |
| `f_c00c` | copy4 + timing10 | 5.805584893e-05 | 0.5222249146 | completed | PASS / 0.521835 | FAST 9.13 | pending | pending |
| `f_c10c` | copy4 + timing10 + zero_13_39 | 5.805584893e-05 | 0.5217029507 | completed | PASS / 0.521515 | FAST 7.63 | pending | pending |
| `f_c188` | timing10 + edge14to15 + zero_13_39 | 5.808343196e-05 | 0.5267354162 | completed | PASS / 0.526517 | FAST 6.16 | pending | pending |
| `f_c1a8` | timing10 + q19check + edge14to15 + zero_13_39 | 5.808343196e-05 | 0.525858255 | proved equivalent CLI | PASS / 0.525682 | FAST 11.65 | pending | pending |
| `f_c0a8` | timing10 + q19check + edge14to15 | 5.808343196e-05 | 0.5263843763 | proved equivalent CLI | PASS / 0.525650 | FAST 7.65 | pending | pending |
| `f_c088` | timing10 + edge14to15 | 5.808343196e-05 | 0.5272624151 | completed | PASS / 0.526541 | FAST 5.82 | pending | pending |
| `f_c024` | copy4 + q19check | 5.808462206e-05 | 0.5213580415 | proved equivalent CLI | PASS / 0.521628 | FAST 8.21 | pending | pending |
| `f_c124` | copy4 + q19check + zero_13_39 | 5.808462206e-05 | 0.520836944 | proved equivalent CLI | PASS / 0.520412 | FAST 7.62 | pending | pending |
| `f_copy4` | copy4 | 5.808462206e-05 | 0.5222276961 | completed | PASS / 0.522041 | FAST 8.33 | pending | pending |
| `f_c104` | copy4 + zero_13_39 | 5.808462206e-05 | 0.5217057294 | completed | PASS / 0.521266 | FAST 8.43 | pending | pending |
| `f_c148` | timing10 + q11measure + zero_13_39 | 5.80944017e-05 | 0.5262791099 | completed | PASS / 0.525793 | FAST 8.40 | pending | pending |
| `f_c168` | timing10 + q19check + q11measure + zero_13_39 | 5.80944017e-05 | 0.5254027086 | proved equivalent CLI | PASS / 0.525092 | FAST 8.27 | pending | pending |
| `f_c048` | timing10 + q11measure | 5.80944017e-05 | 0.5268056523 | completed | PASS / 0.526194 | FAST 8.25 | pending | pending |
| `f_c068` | timing10 + q19check + q11measure | 5.80944017e-05 | 0.5259283741 | proved equivalent CLI | PASS / 0.525465 | FAST 8.26 | pending | pending |
| `f_c138` | timing10 + commute1 + q19check + zero_13_39 | 5.809825725e-05 | 0.5262798116 | proved equivalent CLI | PASS / 0.526117 | FAST 7.81 | pending | pending |
| `f_c118` | timing10 + commute1 + zero_13_39 | 5.809825725e-05 | 0.527157676 | completed | PASS / 0.526981 | FAST 6.41 | pending | pending |
| `f_c038` | timing10 + commute1 + q19check | 5.809825725e-05 | 0.5268063547 | proved equivalent CLI | PASS / 0.526467 | FAST 7.40 | pending | pending |
| `f_c018` | timing10 + commute1 | 5.809825725e-05 | 0.5276850973 | completed | PASS / 0.527014 | FAST 5.77 | pending | pending |
| `f_c029` | instrument15 + timing10 + q19check | 5.810953983e-05 | 0.5264854658 | proved equivalent CLI | PASS / 0.525510 | FAST 6.01 | pending | pending |
| `f_c109` | instrument15 + timing10 + zero_13_39 | 5.810953983e-05 | 0.5268365731 | completed | PASS / 0.526853 | FAST 5.83 | pending | pending |
| `f_c129` | instrument15 + timing10 + q19check + zero_13_39 | 5.810953983e-05 | 0.5259592435 | completed | PASS / 0.525378 | FAST 6.26 | pending | pending |
| `f_c009` | instrument15 + timing10 | 5.810953983e-05 | 0.5273636732 | completed | PASS / 0.526548 | FAST 5.82 | pending | pending |
| `f_c180` | edge14to15 + zero_13_39 | 5.811213969e-05 | 0.5267382217 | completed | PASS / 0.525988 | FAST 6.45 | pending | pending |
| `f_c1a0` | q19check + edge14to15 + zero_13_39 | 5.811213969e-05 | 0.5258610558 | completed | PASS / 0.525516 | FAST 7.68 | pending | pending |
| `f_c0a0` | q19check + edge14to15 | 5.811213969e-05 | 0.5263871799 | completed | PASS / 0.526736 | FAST 11.28 | pending | pending |
| `f_edge14to15` | edge14to15 | 5.811213969e-05 | 0.5272652234 | completed | PASS / 0.526522 | FAST 9.68 | pending | pending |
| `f_c140` | q11measure + zero_13_39 | 5.812317483e-05 | 0.526281913 | completed | PASS / 0.525882 | FAST 8.50 | pending | pending |
| `f_c160` | q19check + q11measure + zero_13_39 | 5.812317483e-05 | 0.525405507 | completed | PASS / 0.524528 | FAST 8.53 | pending | pending |
| `f_q11measure` | q11measure | 5.812317483e-05 | 0.5268084581 | completed | PASS / 0.526498 | FAST 9.16 | pending | pending |
| `f_mzinit_11` | extra reset→measure 11 | 5.812317483e-05 | 0.5268084581 | completed | PASS / 0.526498 | FAST 8.04 | pending | pending |
| `f_c060` | q19check + q11measure | 5.812317483e-05 | 0.5259311753 | completed | PASS / 0.524998 | FAST 11.83 | pending | pending |
| `f_c130` | commute1 + q19check + zero_13_39 | 5.812705578e-05 | 0.5262826147 | completed | PASS / 0.525697 | FAST 7.35 | pending | pending |
| `f_c110` | commute1 + zero_13_39 | 5.812705578e-05 | 0.5271604838 | completed | PASS / 0.526935 | FAST 6.06 | pending | pending |
| `f_c030` | commute1 + q19check | 5.812705578e-05 | 0.5268091606 | completed | PASS / 0.526090 | FAST 7.41 | pending | pending |
| `f_commute1` | commute1 | 5.812705578e-05 | 0.5276879079 | completed | PASS / 0.526730 | FAST 6.14 | pending | pending |
| `f_c021` | instrument15 + q19check | 5.813821559e-05 | 0.52648827 | completed | PASS / 0.526359 | FAST 6.53 | pending | pending |
| `f_c101` | instrument15 + zero_13_39 | 5.813821559e-05 | 0.5268393792 | completed | PASS / 0.527258 | FAST 5.85 | pending | pending |
| `f_c121` | instrument15 + q19check + zero_13_39 | 5.813821559e-05 | 0.5259620449 | completed | PASS / 0.525230 | FAST 6.17 | pending | pending |
| `f_instrument15` | instrument15 | 5.813821559e-05 | 0.5273664821 | completed | PASS / 0.527106 | FAST 6.73 | pending | pending |
| `f_mzinit_5` | extra reset→measure 5 | 5.816895738e-05 | 0.5268084581 | completed | PASS / 0.525437 | FAST 5.99 | pending | pending |
| `f_c128` | timing10 + q19check + zero_13_39 | 5.821055839e-05 | 0.5262791099 | completed | PASS / 0.526225 | FAST 7.27 | pending | pending |
| `f_c108` | timing10 + zero_13_39 | 5.821055839e-05 | 0.5271569731 | completed | PASS / 0.526958 | FAST 5.97 | pending | pending |
| `f_c028` | timing10 + q19check | 5.821055839e-05 | 0.5268056523 | completed | PASS / 0.526266 | FAST 7.25 | pending | pending |
| `f_timing10` | timing10 | 5.821055839e-05 | 0.5276843938 | proved equivalent CLI | PASS / 0.526790 | FAST 6.13 | pending | pending |
| `f_mzinit_12` | extra reset→measure 12 | 5.823622781e-05 | 0.5268084581 | completed | PASS / 0.526171 | FAST 5.64 | pending | pending |
| `f_mzinit_19` | extra reset→measure 19 | 5.823739003e-05 | 0.5180764697 | completed | PASS / 0.517488 | FAST 5.88 | pending | pending |
| `f_c120` | q19check + zero_13_39 | 5.823933151e-05 | 0.526281913 | completed | PASS / 0.525834 | FAST 7.95 | pending | pending |
| `f_repeat_1_14_8_9_2_15_12_5_29_28` | repeat_Z_1,14,8,9,2,15,12,5,29,28 | 5.823933151e-05 | 0.518965302 | reference scope rejected | pending | pending | pending | pending |
| `f_repeat_12_5_29_28` | repeat_Z_12,5,29,28 | 5.823933151e-05 | 0.52418099 | completed | pending | pending | pending | pending |
| `f_zero_13_39` | zero_13_39 | 5.823933151e-05 | 0.5271597809 | completed | PASS / 0.526532 | FAST 6.10 | pending | pending |
| `f_q19check` | q19check | 5.823933151e-05 | 0.5268084581 | completed | PASS / 0.526185 | FAST 7.50 | pending | pending |
| `f_repeat_1` | repeat_Z_1 | 5.823933151e-05 | 0.5268084581 | completed | pending | pending | pending | pending |
| `f_repeat_14` | repeat_Z_14 | 5.823933151e-05 | 0.5268084581 | completed | pending | pending | pending | pending |
| `f_repeat_8` | repeat_Z_8 | 5.823933151e-05 | 0.5268084581 | completed | pending | pending | pending | pending |
| `f_repeat_9` | repeat_Z_9 | 5.823933151e-05 | 0.5268084581 | completed | pending | pending | pending | pending |
| `f_repeat_2` | repeat_Z_2 | 5.823933151e-05 | 0.5268084581 | completed | pending | pending | pending | pending |
| `f_repeat_15` | repeat_Z_15 | 5.823933151e-05 | 0.5268084581 | completed | pending | pending | pending | pending |
| `f_repeat_12` | repeat_Z_12 | 5.823933151e-05 | 0.5268084581 | completed | pending | pending | pending | pending |
| `f_repeat_5` | repeat_Z_5 | 5.823933151e-05 | 0.5268084581 | completed | pending | pending | pending | pending |
| `f_repeat_29` | repeat_Z_29 | 5.823933151e-05 | 0.5268084581 | completed | pending | pending | pending | pending |
| `f_repeat_28` | repeat_Z_28 | 5.823933151e-05 | 0.5268084581 | completed | pending | pending | pending | pending |
| `f_repeat_1_14_8_9_2_15` | repeat_Z_1,14,8,9,2,15 | 5.823933151e-05 | 0.5224366289 | completed | pending | pending | pending | pending |
| `f_base` | v30f control | 5.823933151e-05 | 0.5276872043 | proved equivalent CLI | PASS / 0.527174 | FAST 7.19 | 5.893774204e-05 | pending |
| `f_remove_edge_19_25` | remove_edge_19_25 | 5.857637121e-05 | 0.5274058462 | completed | pending | pending | pending | pending |
| `f_remove_edge_17_16` | remove_edge_17_16 | 6.011586215e-05 | 0.5274058462 | completed | pending | pending | pending | pending |
| `f_edge_19_25` | f_timing_mz_5_12 + {"edge": [19, 25], "family": "readout", "move": "add_edge"} | 0.0001044960168 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_28_29` | f_timing_mz_5_12 + {"edge": [28, 29], "family": "readout", "move": "add_edge"} | 0.0001044961277 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_34_35` | f_timing_mz_5_12 + {"edge": [34, 35], "family": "readout", "move": "add_edge"} | 0.0001044962499 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_35_34` | f_timing_mz_5_12 + {"edge": [35, 34], "family": "readout", "move": "add_edge"} | 0.000104496461 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_29_28` | f_timing_mz_5_12 + {"edge": [29, 28], "family": "readout", "move": "add_edge"} | 0.0001044965054 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_25_19` | f_timing_mz_5_12 + {"edge": [25, 19], "family": "readout", "move": "add_edge"} | 0.0001044965457 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_25_31` | f_timing_mz_5_12 + {"edge": [25, 31], "family": "readout", "move": "add_edge"} | 0.0001045089008 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_31_25` | f_timing_mz_5_12 + {"edge": [31, 25], "family": "readout", "move": "add_edge"} | 0.0001045089008 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_29_35` | f_timing_mz_5_12 + {"edge": [29, 35], "family": "readout", "move": "add_edge"} | 0.0001045168698 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_35_29` | f_timing_mz_5_12 + {"edge": [35, 29], "family": "readout", "move": "add_edge"} | 0.0001045168698 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_16_15` | f_timing_mz_5_12 + {"edge": [16, 15], "family": "readout", "move": "add_edge"} | 0.0001045280062 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_15_16` | f_timing_mz_5_12 + {"edge": [15, 16], "family": "readout", "move": "add_edge"} | 0.0001045767882 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_28_34` | f_timing_mz_5_12 + {"edge": [28, 34], "family": "readout", "move": "add_edge"} | 0.0001047216337 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_34_28` | f_timing_mz_5_12 + {"edge": [34, 28], "family": "readout", "move": "add_edge"} | 0.0001047218004 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_19_18` | f_timing_mz_5_12 + {"edge": [19, 18], "family": "readout", "move": "add_edge"} | 0.0001048093829 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_18_19` | f_timing_mz_5_12 + {"edge": [18, 19], "family": "readout", "move": "add_edge"} | 0.0001048096162 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_14_15` | f_timing_mz_5_12 + {"edge": [14, 15], "family": "readout", "move": "add_edge"} | 0.000104891614 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_15_14` | f_timing_mz_5_12 + {"edge": [15, 14], "family": "readout", "move": "add_edge"} | 0.0001048966896 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_16_17` | f_timing_mz_5_12 + {"edge": [16, 17], "family": "readout", "move": "add_edge"} | 0.0001060712891 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_edge_17_16` | f_timing_mz_5_12 + {"edge": [17, 16], "family": "readout", "move": "add_edge"} | 0.0001061892789 | 0.5064671754 | pending | pending | pending | pending | pending |
| `f_phase_2` | f_timing_best_r2 + Tdag8_to_21 | pending | pending | model rejected | NOISELESS FAIL | pending | pending | pending |
| `f_phase_3` | f_timing_best_r2 + Tdag16_to_22 + Tdag8_to_21 | pending | pending | model rejected | NOISELESS FAIL | pending | pending | pending |

## Interpretation

A Fourier screen is not a completed independent exact2 CLI receipt or a true-mean ranking. The first three unchanged CLI runs independently confirm the native q15 instrument (5.81382e-5), imported prefix feedback (5.79630e-5), and copy4 (5.80846e-5). The rebuilt q15 artifact therefore has new independent evidence despite the uncertainty described in FRESH’s report.

Fresh ST1-style feedback evaluated 1,066 complete timing proposals/joints over three rounds, using CP-SAT interaction cuts and fixing R48. Its tied best cubic value is 5.62757588061e-5. The first implementation admitted floating-point differences below 1e-18 as improvements; the complete witness ledger was replayed to retain the highest-acceptance tied schedule, f_timing_best_r2 (proxy 0.5085649054, versus 0.5061984815 for the raw floating-point incumbent). New feedback requires a real 1e-14 decrease. This tolerance is far below the physical/MC resolution and does not weaken a gate.

Main timing changes on f_timing_best_r2: delay the q4/q10 fused exchange by five native steps to finish just before the q4 B/C initialization; move the first q16→q22 transfer CX six steps earlier; retime early q0/q6 and blue-check operations. The resource gate sequence and R48 remain unchanged. v30_timing_changes.json records every moved unit. These are measured full-circuit gains; no disjoint-loss attribution is assumed.

The earlier copy4 q25 record/barrier issue and LNS c[256] register-size bug are repaired locally. Existing source tools, evaluator code and other lanes are read-only. No global optimum or server-runtime claim is made.

Receipt audit: FRESH/winner_exact.log explicitly names the baseline fast_zlast.qasm, not its _i15_near rewrite. That baseline receipt cannot establish a mismatch for the instrument circuit. COMP29’s new unchanged CLI result confirms its own rebuilt instrument; the old report’s negative inference is not used.

The baseline all-orders result is now validated: 5.89377420421e-5, acceptance 0.527524506136, versus supplied MC mean 5.89438407e-5. f_timing_best_r2 completed the full judge, FAST speed and three 1e8 seeds: 5.838313e-5 / 5.631083e-5 / 5.725565e-5, mean 5.731654e-5, seed-0 acceptance 0.50845. Independent cubic and all-orders finalist confirmation are tracked in the table.

Confirmed all-orders result for f_timing_best_r2: **5.69407491858e-5**, acceptance **0.508326788756**. This is **3.3883% below v30f** by the preferred all-orders ranking. Its unchanged cubic CLI confirms **5.62758e-5**. This candidate is fully verified locally; broader per-combination reference confirmations and the q5/q12 extension comparison remain in progress.

64-detector reference issue: exact2's triple path may infer float64 when an unsigned-high detector bit mixes with small integers, then cast to int64. This loses low detector bits; the original f_timing_mz_5_12 reference (5.62051e-5) is preserved as unsafe_exact, not accepted. Merely sorting comments cannot repair it because the QASM converter places each detector after its latest measurement. canonical_detectors.py instead XORs every other detector with a required final identity check and puts the five quantum-dependent rows first. This invertible basis change preserves the full acceptance predicate and every gate/noise channel; all fault signatures, rotation axes and decoder operators are independently matched. Every accepted transformed mask is at most 31, making the unchanged engine's accepted arithmetic exact. Rejected high masks remain rejected even under the cast. The 64-detector reference is rerun on this equivalent QASM; evaluator files are unchanged. More than 64 detectors are explicitly rejected by the reference-input guard.

A further timing pass (349 macro/joint prices) found no >1e-14 improvement. Additional repeated terminal-Z checks showed no cubic benefit. Moving T†16 through the final transfer to q22 passes the noiseless model but slightly worsens the cubic screen; moving T†8 through to q21 crosses the intervening blue XZ check and fails correctness. Replacing fresh q5/q12 resets by checked Z measurements gives f_timing_mz_5_12, 5.62042582172e-5 with proxy 0.5068725113. The q19 variant fails the acceptance proxy (0.4993024441). Additional final-readout edges all worsened the screen; adding a final layer was particularly costly.

**Best completed finalist: f_timing_mz_5_12**, also copied to best.qasm/best.json. All-orders **5.68688901449e-5**, acceptance **0.506635004404**, a **3.51023%** improvement over v30f. The guarded, unchanged cubic CLI confirms **5.62043e-5** and agrees with the independent Fourier contraction. The full 1e6 judge passes at acceptance **0.506279** and approximately **3.34 s** on jerry; the XTIM probe is FAST. Three 1e8 scores are **5.742755e-5 / 5.758890e-5 / 5.727002e-5**, mean **5.742882e-5**, seed-0 acceptance **0.50664**. All-orders decides its close ordering over f_timing_best_r2; the opposite three-seed mean order is within MC noise. The original submitted-form QASM is kept in best.qasm; the detector-basis rewrite is an equivalent analytical-reference input only.

The numeric audit reproduces the int64/float failure on 12 of 100 adversarial original-basis tables (maximum error 0.25). The equivalent basis has zero mismatches and maximum loss-table discrepancy 1.12e-16. Warnings remain recorded rather than suppressed. See detector_numeric_audit.json and the per-candidate detorder.validation.json. The exhaustive reference-only sweep continues on jerry and owl within their assigned process limits; reference_owners.json prevents duplicated cross-host work.

**Reference reuse decision:** the requested per-file CLI execution method is reduced only for a proved conditional-noise equivalence. q19_equivalence.json certifies 256 pairs: removing the extra isolated early q19 MX check, restoring its reset time, and renaming records produces identical downstream native circuits and detector predicates. Both versions leave the same post-MX-depolarized |+> state after the already checked MX at t3, before the first q19 CX at t4. The extra check multiplies both accepted mass and accepted error mass by alpha(p)=1−5p/3+4p²/3, so conditional 1−F is identical at all orders. The complete 512 full-circuit screens independently agree with this identity and its A1 shift. Each pair reuses one actual unchanged exact2 result, with each circuit’s own acceptance and judge/speed receipt retained. This is an explicit equivalence certificate, not an additive-gain estimate; cached rows are labeled separately from direct executions. Started jobs finish normally and their direct receipts are preserved.

Further local rewrite: a checked MX followed by a Z reset can be replaced by H at the old MX slot and checked MZ at the reset slot. The accepted ideal instrument is the same |0><+|, with different physical noise channels. f_unfold4 and its grouped-frame combination have passed judge/FAST; true-mean and independent reference receipts are recorded as they complete. All six eligible sites and their 64 compatible subsets are screened in v30_unfold_family.json. The q13 repeated-check equivalence hypothesis was rejected because CX13→19 lies between its reset and final check; no q13 reference reuse is made.

Best finalist: **f_timing_mz_5_12** (complete own gates; broader comparisons still running).
