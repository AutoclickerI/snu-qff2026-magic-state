Status: **R43 target not achieved. Verified R44 improvement delivered; all jobs exited.** Prior result: [REPORT_guard5_R44.md](REPORT_guard5_R44.md).

## Verified finalists

| Stem | R / CX | All-orders 1−F | All-orders acceptance | exp(-A1) | Judge 1e6 on zebra | MC3 mean |
|---|---:|---:|---:|---:|---|---:|
| [v34/checked16_timing_0](v34/checked16_timing_0.qasm) | 44 / 207 | 4.146051958326e-05 | 0.500832514 | 0.500985055 | PASS, 4.6s, FAST | 4.1769980e-05 |
| [v34/layer26_timing_0](v34/layer26_timing_0.qasm) | 44 / 207 | 4.152425077604e-05 | 0.500998189 | 0.501144091 | PASS, 3.1s, FAST | 4.1052480e-05 |
| [v34/layer_26_R44_m2](v34/layer_26_R44_m2.qasm) | 44 / 207 | 4.177608289385e-05 | 0.502666063 | 0.502810876 | PASS, 8.8s, FAST | 4.1737200e-05 |

Choose **checked16_timing_0** by all-orders expectation: 11.085% below v34m (4.662933481719e-05) and 5.631% below FRESH’s decoder port. Its cubic parts are second=3.500154419293e-05, third=6.177157492898e-06, total=4.117870168583e-05; c1=3.090e-19. Native depth47, 207 CX, 68 detectors, 84 measurements. The acceptance floor0.5005 is met.

Best MC seeds0/1000/2000: 4.057677e-5 / 4.262330e-5 / 4.210989e-5; acceptances0.50090 / 0.50078 / 0.50083. The million-shot gate acceptance is0.501715. The variant without the added q16 check has a lower sampled MC mean, but the all-orders expectation ranks the checked circuit first; the 6.37e-8 expectation difference is much smaller than MC uncertainty.

FRESH’s guard5_timing_0_a_decode is the rebase, credited to FRESH/reviewer6: all-orders4.39344936172e-5, acceptance0.500899908, MC mean4.377908e-5. The local decoder0 copy is byte-identical; native noisy blocks and the million-shot seed-0 result agree. Its MC receipt is reused with provenance in fresh_rebase_proof.json. The three finalists above have their own new judge/speed/MC runs.

## What changed

Data and final roles are unchanged: D=[0,20,7,10,3,22,21], A=[1,14,8,9,2,16,15], B=[6,26,13,11,4,23,27], C=[12,25,19,17,5,29,28]. The guard5 prefix, its five waiting-data guards, coherent data-hop plan and correlated 57-CX B/C resource are retained. The successful new encoder uses12 CX and X pivots[14,8,9,16]. It prepares the same |+L> state; it was synthesized with the actual cell releases, not ported from a free-space schedule.

All data-source checks are retained, including c54/c55/c56/c57 and the blue outputs c64/c67. Old A-input X verifications on q1/q2/q8 are not source checks: q1/q2 become Z inputs in the new encoder, and the whole new preparation is independently priced. The best adds a native known-X check on q16 in its idle slot at40, after RX16 at39 and before CX16→15 at41. q16’s source-zero MZ c55 remains at38.

| Native step | A encoder CX |
|---:|---|
| 37 | 8→2 |
| 38 | 14→8, 2→1 |
| 39 | 1→2, 9→8 |
| 40 | 8→2, 9→15 |
| 41 | 8→9, 16→15 |
| 42 | 9→8, 15→14 |
| 43 | 14→8 |

Decoder compatibility is explicit: D10→A9 and D21→A15 run at43, CX9→15 at44, CX8→9 at45, then MX8 and MZ9/MZ15 at46. The other five D→A couplings and all B→C checks run at44. The decoder adds no native step relative to the guard5 readout tail. Every new pivot is reset into its preparation basis; the successful variants do not reuse the troublesome pre-blue random X state.

## R43 work and closure scope

The detailed node/edge timing certificate is [v34/CRITICAL_PATH.md](v34/CRITICAL_PATH.md). On the initial R44 decoder port, q8’s source check at35, RX at36, input verification at37, and the A encoder38–43 bind the round. On the new encoder, parallel critical branches meet at CX8→2 at37: q8 is released/checked at35 and initialized at36; the blue q2 output is measured at35 and reset in Z at36. The encoder then occupies the central cells through43, forcing the remaining data couplings at44. Final component ready slack: A0, data-hop completion4, B/C5, prefix8. Terminal T/T† operations are ready by31 in the emitted-order earliest schedule (13 steps of ready slack).

A correct R43 construction exists by removing the reset before the blue q2 check and reusing its earlier X measurement. That shifts Bell preparation29→28 and the q8 release35→34. It fails the speed requirement. With the original A encoder, XTIM predicts169.05s/1e6; retiming gives174.83s/1e6. With the new12-CX encoder and q2 later reset in Z, it still predicts146.31s/1e6. No million-shot gate or MC was wasted on these SLOW recipes.

| Tested family | Measured or proved result | Exact scope |
|---|---|---|
| Fixed-operation retiming | R43 INFEASIBLE with the ordinary reset; R43 constructible with pre-blue X reuse | Tested global CX/control-phase commutations; no gate resynthesis |
| Unitary A preparation | No R42/R43 witness;120 R44 algebraic witnesses replayed | 11811 rank-four subspaces,35 input coordinate sets,95 matching layers including empty, no CX-count cap; two routes and five initialization modes at recorded release bounds |
| Route through q14 instead of q9 | Full R44 circuits built/priced; no R43 state-prep witness | Corrected prefix-release order, same final geometry |
| One UVUV dirty bus | No R43 witness in132 recipes | One macro through data3/7/10, specified directions/start times; endpoints reserved during the macro |
| Measurement-assisted prep | No R43 witness;41 R44 calibration branches replayed | Rank5→4 by one Z measurement, or rank4→3 then one X preparation; no external helpers or multiple measurements |
| Earlier D→A during A encoding | No R43 assignment | 168 invertible syndrome maps HM=NH on the selected fresh-input R44 witnesses, not every possible gate path |
| Four staggered branch schedules | Schedule-infeasible | Only the four exact branch recipes tested |
| Permuting the four blue-q2 data gates | Schedule-infeasible or ideal detectors become random | All24 permutations with the existing detector contract; no detector removed to pass |

These negatives do not prove a global R43 lower bound. More general Clifford encoders, multiple measured helpers, different endpoint layouts and a larger prefix-instrument redesign remain outside the search. Measurement calibration verifies the algebraic zero-outcome CSS update, not a complete emitted judge circuit. A q14 route ordering bug was corrected before final witnesses and full-circuit prices were generated; final search_validation.json checks their release times, disjoint layers and target subspace independently.

## Price of the decoder and the R step

All values below are full all-orders expectations. The no-decoder ablations keep the early data couplings and restore the original A-Z detector basis; they are matched controls, not separately optimized no-decoder designs.

| Variant | R / depth | With decoder | Without decoder | Runtime status |
|---|---|---:|---:|---|
| decoder0 | 44 / 47 | 4.393449361722e-05 | 5.132475620295e-05 | FAST |
| reuseblue_0_R43 | 43 / 46 | 4.415679458516e-05 | 5.165839099178e-05 | SLOW |
| checked16_timing_0 | 44 / 47 | 4.146051958326e-05 | 8.680970845494e-05 | FAST |
| layer_26_R44_m2_reuse_R43 | 43 / 46 | 4.362032871903e-05 | 9.081307105621e-05 | SLOW |

The new encoder is poor without the logical-X flag:8.68097e-5 versus4.14605e-5 with it. This is why judging encoders only by their old unflagged danger score misses the improvement. The actual R43 reuse constructions also alter prefix noise and timing, so the earlier free-space estimate of1.4e-6 saved per tick cannot be applied to them. The tested R43 recipe loses fidelity to its R44 parent as well as failing speed.

## Loss split

Values are cubic loss ×10⁶. Channel-removal ablations are nonadditive counterfactuals, not attainable circuits. There are no measured block teleports. Idle gaps crossing R are grouped with round.

| Circuit | Full | No pre-round idle | No B/C noise | No A noise | No data-hop noise | Round only |
|---|---:|---:|---:|---:|---:|---:|
| decoder0 | 43.678423 | 36.086985 | 38.467458 | 39.503451 | 43.306149 | 30.411993 |
| checked16_timing_0 | 41.178702 | 34.437073 | 36.153452 | 40.181675 | 40.784895 | 30.411993 |
| layer_26_R44_m2_reuse_R43 | 43.351185 | 35.267794 | 37.980459 | 40.671775 | 42.952241 | 30.411993 |

The unchanged exact2 second-order pair contraction agrees with the lane moment contraction to<1e-15. The decoder-matched new encoder eliminates A×pre-round-idle (1.550352e-6), A×round (0.728889e-6) and A×B/C (0.337778e-6) contributions to evaluator precision. A×prefix falls0.504444e-6→0.006667e-6. Second order improves3.813456e-5→3.500154e-5, while third order increases5.543862e-6→6.177157e-6. All-orders confirms the net gain.

The final round×round pair component is3.054444e-5, about87.27% of the remaining second-order loss. This is a component of this round instrument, not a universal lower bound. Remaining B/C self pairs contribute2.18e-6. The full physical-pair classes and examples are in checked16_timing_0.pairs.json.

## Complete priced ledger

Every ideal-valid emitted circuit has an all-orders price. Failed ideal/schedule recipes are in the search/build JSON files. Nonfinal plans are archived in v34/nonfinal_plans.json.gz; numeric receipts remain separate. Gate/MC “not selected” means it was a comparator, not a delivered finalist.

| Variant | R | Cubic 1−F | All orders | Acceptance | Gate / MC |
|---|---:|---:|---:|---:|---|
| layer26_timing_0_check16 | 44 | 4.1178701686e-05 | 4.146039041078e-05 | 0.500162816 | acceptance<0.5005 / no MC |
| checked16_timing_0 | 44 | 4.1178701686e-05 | 4.146051958326e-05 | 0.500832514 | PASS/FAST / 4.1769980e-05 |
| layer26_timing_0 | 44 | 4.1240357412e-05 | 4.152425077604e-05 | 0.500998189 | PASS/FAST / 4.1052480e-05 |
| layer_26_R44_m2_check16 | 44 | 4.1296530691e-05 | 4.157952038425e-05 | 0.502159917 | not selected / no MC |
| layer26_timing_0_check14_16 | 44 | 4.1302817741e-05 | 4.158548831528e-05 | 0.499827053 | acceptance<0.5005 / no MC |
| layer26_timing_0_check14 | 44 | 4.1365253977e-05 | 4.165013998788e-05 | 0.500661866 | not selected / no MC |
| layer_26_R44_m2_check14_16 | 44 | 4.1422588299e-05 | 4.170657073327e-05 | 0.501822818 | not selected / no MC |
| layer_26_R44_m2 | 44 | 4.1486558494e-05 | 4.177608289385e-05 | 0.502666063 | PASS/FAST / 4.1737200e-05 |
| layer_25_R44_m2 | 44 | 4.1607573111e-05 | 4.189986762907e-05 | 0.502696165 | not selected / no MC |
| layer_26_R44_m2_check14 | 44 | 4.1614957634e-05 | 4.190550480953e-05 | 0.502328625 | not selected / no MC |
| layer_24_R44_m2 | 44 | 4.1753854998e-05 | 4.205139001468e-05 | 0.502532810 | not selected / no MC |
| layer_32_R44_m2 | 44 | 4.2806104986e-05 | 4.308362707799e-05 | 0.502416573 | not selected / no MC |
| layer_87_R44_m12 | 44 | 4.2826618060e-05 | 4.313299771338e-05 | 0.503837230 | not selected / no MC |
| layer_85_R44_m12 | 44 | 4.2847706893e-05 | 4.316106983151e-05 | 0.503201922 | not selected / no MC |
| layer_84_R44_m12 | 44 | 4.2864976895e-05 | 4.318280183408e-05 | 0.503713983 | not selected / no MC |
| layer_17_R44_m1 | 44 | 4.2923527583e-05 | 4.320438887578e-05 | 0.502252442 | not selected / no MC |
| layer_31_R44_m2 | 44 | 4.2943215562e-05 | 4.322567992010e-05 | 0.502253147 | not selected / no MC |
| layer_26_R44_m2_reuse_R43 | 43 | 4.3351185267e-05 | 4.362032871903e-05 | 0.511898235 | SLOW / no MC |
| layer26_timing_0_reuse_R43 | 43 | 4.3356921926e-05 | 4.362448412358e-05 | 0.509859342 | not selected / no MC |
| decoder0 | 44 | 4.3678422988e-05 | 4.393449361722e-05 | 0.500899908 | PASS/FAST / 4.3779080e-05 |
| decoder_timing_0 | 44 | 4.3677625703e-05 | 4.393519211295e-05 | 0.500903747 | not selected / no MC |
| decoder1 | 44 | 4.3677625703e-05 | 4.393527676042e-05 | 0.501236939 | not selected / no MC |
| no_prepcheck_272 | 44 | 4.3683900930e-05 | 4.394082436169e-05 | 0.501402100 | not selected / no MC |
| layer_9_R44_m1 | 44 | 4.3791167046e-05 | 4.405052212555e-05 | 0.500568976 | not selected / no MC |
| blue43_timing_0 | 43 | 4.3824810270e-05 | 4.406691589588e-05 | 0.502568031 | not selected / no MC |
| blue43_timing_1 | 43 | 4.3822992317e-05 | 4.406822588163e-05 | 0.500905657 | SLOW / no MC |
| no_prepcheck_60 | 44 | 4.3846819550e-05 | 4.410754308370e-05 | 0.501406017 | not selected / no MC |
| no_prepcheck_180 | 44 | 4.3847539076e-05 | 4.410859392978e-05 | 0.501405317 | not selected / no MC |
| layer_1_R44_m0 | 44 | 4.3867962612e-05 | 4.412621671318e-05 | 0.500231472 | acceptance<0.5005 / no MC |
| reuseblue_0_R43 | 43 | 4.3917119826e-05 | 4.415679458516e-05 | 0.509629630 | SLOW / no MC |
| reuseblue_1_R43 | 43 | 4.4059223452e-05 | 4.429789511261e-05 | 0.508982948 | not selected / no MC |
| layer_11_R44_m1 | 44 | 4.4033994136e-05 | 4.430007433356e-05 | 0.500901831 | not selected / no MC |
| layer_92_R44_m12 | 44 | 4.4114246111e-05 | 4.441171624293e-05 | 0.502922003 | not selected / no MC |
| layer_19_R44_m2 | 44 | 4.4145874350e-05 | 4.441616658399e-05 | 0.502083552 | not selected / no MC |
| layer_90_R44_m12 | 44 | 4.4136025240e-05 | 4.443755180827e-05 | 0.503432563 | not selected / no MC |
| layer_10_R44_m1 | 44 | 4.4165558884e-05 | 4.443809924437e-05 | 0.501241675 | not selected / no MC |
| layer_78_R44_m11 | 44 | 4.4223332376e-05 | 4.452330535926e-05 | 0.502923631 | not selected / no MC |
| layer_60_R44_m10 | 44 | 4.4733356729e-05 | 4.501280318955e-05 | 0.501398461 | not selected / no MC |
| layer_71_R44_m11 | 44 | 4.4738810389e-05 | 4.501915181176e-05 | 0.501902525 | not selected / no MC |
| layer_70_R44_m11 | 44 | 4.4751067908e-05 | 4.503423557271e-05 | 0.501741107 | not selected / no MC |
| layer_69_R44_m11 | 44 | 4.4903524858e-05 | 4.519231086321e-05 | 0.502079725 | not selected / no MC |
| layer_81_R44_m12 | 44 | 4.5124643978e-05 | 4.541864377472e-05 | 0.502755192 | not selected / no MC |
| layer_80_R44_m12 | 44 | 4.5285509939e-05 | 4.558667585302e-05 | 0.503263807 | not selected / no MC |
| layer_64_R44_m10 | 44 | 4.8131269681e-05 | 4.846433270610e-05 | 0.501804846 | not selected / no MC |
| layer_88_R44_m12 | 44 | 4.8180042616e-05 | 4.851561274848e-05 | 0.503316388 | not selected / no MC |
| layer_75_R44_m11 | 44 | 4.8338478283e-05 | 4.867543025429e-05 | 0.502811439 | not selected / no MC |
| layer_8_R44_m1 | 44 | 5.0029375951e-05 | 5.030365645085e-05 | 0.501413957 | not selected / no MC |
| layer_3_R44_m0 | 44 | 5.0192923440e-05 | 5.046764621078e-05 | 0.500573148 | not selected / no MC |
| layer_20_R44_m2 | 44 | 5.0338935324e-05 | 5.062566534674e-05 | 0.502087057 | not selected / no MC |
| layer_21_R44_m2 | 44 | 5.0373955259e-05 | 5.066028777562e-05 | 0.502252700 | not selected / no MC |
| layer_2_R44_m0 | 44 | 5.0407952079e-05 | 5.068857674463e-05 | 0.500575498 | not selected / no MC |
| layer_13_R44_m1 | 44 | 5.0596850596e-05 | 5.089181458043e-05 | 0.501451917 | not selected / no MC |
| layer_23_R44_m2 | 44 | 5.0763398151e-05 | 5.105912746315e-05 | 0.501625334 | not selected / no MC |
| layer_30_R44_m2 | 44 | 5.0932851904e-05 | 5.123691491591e-05 | 0.502293404 | not selected / no MC |
| layer_68_R44_m11 | 44 | 5.0987394406e-05 | 5.127979469062e-05 | 0.502749187 | not selected / no MC |
| decoder0_no_decoder | 44 | 5.1019640683e-05 | 5.132475620295e-05 | 0.501328730 | not selected / no MC |
| layer_82_R44_m12 | 44 | 5.1101539809e-05 | 5.140266858051e-05 | 0.503256717 | not selected / no MC |
| reuseblue_0_R43_no_decoder | 43 | 5.1371311551e-05 | 5.165839099178e-05 | 0.510065419 | not selected / no MC |
| layer_91_R44_m12 | 44 | 5.1806337258e-05 | 5.212100090072e-05 | 0.502939104 | not selected / no MC |
| layer_62_R44_m10 | 44 | 5.1853809158e-05 | 5.217415622183e-05 | 0.500623451 | not selected / no MC |
| layer_73_R44_m11 | 44 | 5.2140873854e-05 | 5.246935984353e-05 | 0.502136883 | not selected / no MC |
| layer_27_R44_m2 | 44 | 5.3158779631e-05 | 5.345344768841e-05 | 0.502332204 | not selected / no MC |
| layer_0_R44_m0 | 44 | 5.4199310498e-05 | 5.447597618684e-05 | 0.500410702 | acceptance<0.5005 / no MC |
| layer_18_R44_m2 | 44 | 5.4377481548e-05 | 5.466448283165e-05 | 0.502260529 | not selected / no MC |
| layer_79_R44_m12 | 44 | 5.5358365159e-05 | 5.566429655452e-05 | 0.503597916 | not selected / no MC |
| layer_67_R44_m10 | 44 | 5.6564778314e-05 | 5.690571176704e-05 | 0.501140306 | not selected / no MC |
| layer_22_R44_m2 | 44 | 5.9009056972e-05 | 5.931738133782e-05 | 0.502102733 | not selected / no MC |
| layer_29_R44_m2 | 44 | 5.9902814319e-05 | 6.020746368717e-05 | 0.501501338 | not selected / no MC |
| layer_83_R44_m12 | 44 | 5.9924207735e-05 | 6.025129287893e-05 | 0.503440460 | not selected / no MC |
| checked16_timing_0_no_decoder | 44 | 8.6482298795e-05 | 8.680970845494e-05 | 0.501267204 | not selected / no MC |
| layer_26_R44_m2_reuse_R43_no_decoder | 43 | 9.0499736099e-05 | 9.081307105621e-05 | 0.512343552 | not selected / no MC |

## Verified versus inferred

Verified: full ideal correctness and |c1|<1e-12 for each priced circuit; grid adjacency and emitted native timing; all-orders acceptance≥0.5005 for each finalist; unchanged million-shot judge PASS, ≤20s/1e6 on zebra, XTIM FAST and3×1e8-shot MC. Source checks and decoder timing are audited in the final metadata. Independent search replay and conditional CP certificates are in the lane. No submissions, commits, pushes, credentials, subagents or writes to other lanes were used.

Cubic values use the previously validated lane moment contraction on unchanged EVAL Model/Engine, with exact wide-integer identity-projector rejection before active-projector batching. They are not claimed as unchanged exact2 --third CLI receipts beyond its integer-width scope. Ranking uses the byte-copied current MAIN/sparse evaluator, within its full-barrier/no-FRAME/no-POSTSELECT scope. Independent judge/MC checks validate the finalists. Sparse omission bounds do not include floating-point roundoff.

Unverified/open: a fast R43 construction, a global architecture lower bound, multi-helper/general-Clifford synthesis, and any official submission outcome. All jobs exited. Reproduction uses the saved requests, C++ finite-state engines, assemble_layers.py, feedback.py, input_checks.py, audit.py and restore_variant.py. The previous ENDSTATE emitter remains available; this task did not reopen its old exposure-limited recipes.
