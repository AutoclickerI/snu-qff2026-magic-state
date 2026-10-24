# WAITPROT — v35a acceptance-efficient protection

Best verified all-orders candidate: **terminal_joint**, **4.291562260848e-05** (2.3208% below v35a), acceptance **0.514800277**, 246 CX, R44, depth47. Official 1e6 PASS and XTIM FAST.

Artifacts: [v35_best.qasm](v35_best.qasm), [v35_best.json](v35_best.json), [v35_best.metrics.json](v35_best.metrics.json).

Best measured seed-0 key among completed finalists: **4.172584e-05**, acceptance **0.51383**, `close_ABCDEF_postT0`. Its all-orders loss is 4.293169630781e-05; MC3 mean 4.232869333e-05. [QASM](v35_seed0_best.qasm) · [JSON](v35_seed0_best.json).

| Finalist | All-orders loss | Acceptance | Judge 1e6 | FAST s/1e6 | MC3: seed0 / mean |
|---|---:|---:|---|---:|---|
| [v35/terminal_joint](v35/terminal_joint.qasm) | 4.291562260848e-05 | 0.514800277 | PASS 4.7611552e-05, acc 0.514581 | 9.417 | pending |
| [v35/close_ABCDEF_postT0](v35/close_ABCDEF_postT0.qasm) | 4.293169630781e-05 | 0.513777275 | PASS 4.2789569e-05, acc 0.514144 | 4.103 | 4.172584e-05 / 4.232869333e-05 |
| [v35/final_own_mz19](v35/final_own_mz19.qasm) | 4.310078428807e-05 | 0.503918446 | PASS 2.9757299e-05, acc 0.504078 | 4.701 | 4.303789e-05 / 4.300229667e-05 |
| [v35/final_st2share_packall_late](v35/final_st2share_packall_late.qasm) | 4.310111730986e-05 | 0.508810707 | PASS 3.9327809e-05, acc 0.508546 | 4.023 | 4.179318e-05 / 4.233022333e-05 |
| [v35/live_Z_q10_h16_37_39](v35/live_Z_q10_h16_37_39.qasm) | 4.358401123035e-05 | 0.501967158 | PASS 3.7948239e-05, acc 0.500682 | 4.787 | 4.342366e-05 / 4.368002000e-05 |
| [v35/combo_fund_fold15_released7Z](v35/combo_fund_fold15_released7Z.qasm) | 4.358696196916e-05 | 0.501015847 | PASS 3.5990427e-05, acc 0.500133 | 5.780 | 4.344215e-05 / 4.338103000e-05 |
| [v35/released_q7_h13_Z_reset](v35/released_q7_h13_Z_reset.qasm) | 4.375436491373e-05 | 0.501463648 | PASS 5.0909889e-05, acc 0.500885 | 4.735 | 4.358876e-05 / 4.345223667e-05 |
| [v35/new_05_X_q20_h21](v35/new_05_X_q20_h21.qasm) | 4.390915495755e-05 | 0.501631832 | PASS 4.0844953e-05, acc 0.501898 | 5.000 | 4.327406e-05 / 4.424190333e-05 |
| [v35/late_resets_joint](v35/late_resets_joint.qasm) | 4.393449210371e-05 | 0.505244596 | PASS 3.8624493e-05, acc 0.504861 | 7.967 | 4.442880e-05 / 4.427284667e-05 |

Base v35a: **4.393527676042e-05**, acceptance **0.501236938624**. Required candidate budget: ≥0.5005. The parsed source has native ticks0–46 (47 layers), despite the briefing’s depth48; all original schedules are preserved unless an edit explicitly retimes an operation.

[menu_v35a.json](menu_v35a.json): 200 numerical standalone prices and 3 noiseless rejections, including ST2 receipts imported to avoid duplicate work. [v35/windows.json](v35/windows.json) maps data paths, idle runs and released helpers.

Current scope: guard initialization/parity changes, shortened windows, guard duals, shared helpers, readout folded into an existing check, and newly released helper windows. ST2 owns the broad detector/physical-removal knapsack; this lane prices complementary gadgets and complete combinations.

| Standalone edit | All-orders loss | Acceptance | Loss gain | Acceptance cost |
|---|---:|---:|---:|---:|
| cxpair_q10_h16_37_38 | 4.3577686083e-05 | 0.501967588 | +3.57591e-07 | -0.0007306 |
| cxpair_q10_h16_38_39 | 4.3577686083e-05 | 0.501967588 | +3.57591e-07 | -0.0007306 |
| live_Z_q10_h16_37_39 | 4.3584011230e-05 | 0.501967158 | +3.51266e-07 | -0.0007302 |
| live_X_q10_h16_37_39 | 4.3596332726e-05 | 0.501799181 | +3.38944e-07 | -0.0005622 |
| live_X_q10_h4_38_39 | 4.3695293480e-05 | 0.502232141 | +2.39983e-07 | -0.0009952 |
| live_Z_q10_h4_38_39 | 4.3695293480e-05 | 0.502232141 | +2.39983e-07 | -0.0009952 |
| shared_20_15_h21_X_separate | 4.3751198175e-05 | 0.496633453 | +1.84079e-07 | +0.0046035 |
| shared_20_15_h21_X_first_use | 4.3751414197e-05 | 0.497133088 | +1.83863e-07 | +0.0041039 |
| shared_20_15_h21_X_fold | 4.3751414197e-05 | 0.497133088 | +1.83863e-07 | +0.0041039 |
| released_q7_h13_Z_reset | 4.3754364914e-05 | 0.501463648 | +1.80912e-07 | -0.0002267 |
| fold15_h16_X_20_29_first_use | 4.3769953920e-05 | 0.499292741 | +1.65323e-07 | +0.0019442 |
| fold15_h16_X_20_29_reset | 4.3769953920e-05 | 0.499292741 | +1.65323e-07 | +0.0019442 |
| ST2/echo_15_21_X_20_29 | 4.3770456250e-05 | 0.496147736 | +1.64821e-07 | +0.0050892 |
| fold_q15_h21_20_29_first_use | 4.3770744595e-05 | 0.496647017 | +1.64532e-07 | +0.0045899 |
| fold_q15_h21_20_29_reset | 4.3770744595e-05 | 0.496647017 | +1.64532e-07 | +0.0045899 |
| fold_q15_h21_20_29_mz_parity | 4.3770964973e-05 | 0.495822804 | +1.64312e-07 | +0.0054141 |
| fold15_h16_X_21_29_first_use | 4.3786799728e-05 | 0.499790917 | +1.48477e-07 | +0.0014460 |
| fold15_h16_X_21_29_reset | 4.3786799728e-05 | 0.499790917 | +1.48477e-07 | +0.0014460 |
| early_q7_h13_27_31_n2 | 4.3793967437e-05 | 0.502700793 | +1.41309e-07 | -0.0014639 |
| live_Z_q22_h16_37_39 | 4.3809232301e-05 | 0.501968807 | +1.26044e-07 | -0.0007319 |
| cxpair_q22_h16_37_38 | 4.3809457073e-05 | 0.501967589 | +1.25820e-07 | -0.0007307 |
| cxpair_q22_h16_38_39 | 4.3809457073e-05 | 0.501967589 | +1.25820e-07 | -0.0007307 |
| live_X_q22_h16_37_39 | 4.3817352751e-05 | 0.501799797 | +1.17924e-07 | -0.0005629 |
| released_q7_h13_X_reset | 4.3825492406e-05 | 0.501460000 | +1.09784e-07 | -0.0002231 |
| released_q7_h13_X_reuse | 4.3825716736e-05 | 0.500960519 | +1.09560e-07 | +0.0002764 |
| early_q20_h14_19_24_n3 | 4.3847653064e-05 | 0.504235273 | +8.76237e-08 | -0.0029983 |
| live_X_q3_h2_33_34 | 4.3854163590e-05 | 0.502237720 | +8.11132e-08 | -0.0010008 |
| live_Z_q3_h2_33_34 | 4.3854163590e-05 | 0.502237720 | +8.11132e-08 | -0.0010008 |
| early_q0_h6_19_24_n3 | 4.3858389031e-05 | 0.504435530 | +7.68877e-08 | -0.0031986 |
| live_X_q7_h13_30_31 | 4.3864632027e-05 | 0.501967873 | +7.06447e-08 | -0.0007309 |
| live_Z_q7_h13_30_31 | 4.3864632027e-05 | 0.501967873 | +7.06447e-08 | -0.0007309 |
| live_X_q7_h1_30_31 | 4.3865331595e-05 | 0.502238098 | +6.99452e-08 | -0.0010012 |
| live_Z_q7_h1_30_31 | 4.3865331595e-05 | 0.502238098 | +6.99452e-08 | -0.0010012 |
| new_17_X_q15_h16 | 4.3871347225e-05 | 0.501291566 | +6.39295e-08 | -0.0000546 |
| early_q15_h16_25_29_n2 | 4.3876253405e-05 | 0.502698775 | +5.90234e-08 | -0.0014618 |
| shared_20_15_h21_Z_separate | 4.3885418029e-05 | 0.496798433 | +4.98587e-08 | +0.0044385 |
| new_15_X_q15_h16 | 4.3888823748e-05 | 0.499964349 | +4.64530e-08 | +0.0012726 |
| early_q10_h9_24_27_n2 | 4.3892836347e-05 | 0.503238845 | +4.24404e-08 | -0.0020019 |
| early_q15_h16_25_29_n1 | 4.3905769297e-05 | 0.501966865 | +2.95075e-08 | -0.0007299 |
| new_14_Z_q15_h16 | 4.3905818376e-05 | 0.500299170 | +2.94584e-08 | +0.0009378 |
| early_q20_h14_19_24_n1 | 4.3906051546e-05 | 0.502233454 | +2.92252e-08 | -0.0009965 |
| early_q15_h9_21_22_n1 | 4.3906657459e-05 | 0.502235485 | +2.86193e-08 | -0.0009985 |
| new_05_X_q20_h21 | 4.3909154958e-05 | 0.501631832 | +2.61218e-08 | -0.0003949 |
| repair_replace45_Zguard | 4.3909205827e-05 | 0.502468488 | +2.60709e-08 | -0.0012315 |
| early_q0_h6_19_24_n1 | 4.3909616662e-05 | 0.502299904 | +2.56601e-08 | -0.0010630 |
| moving_helper_q20_h21_33_35_n1 | 4.3910095411e-05 | 0.501967033 | +2.51813e-08 | -0.0007301 |
| ablate_new05_no_detector | 4.3910208607e-05 | 0.501632907 | +2.50682e-08 | -0.0003960 |
| postT0_pair15_16 | 4.3910682128e-05 | 0.502300346 | +2.45946e-08 | -0.0010634 |
| early_q10_h9_24_27_n1 | 4.3914050785e-05 | 0.502236424 | +2.12260e-08 | -0.0009995 |
| early_q7_h6_21_22_n1 | 4.3914438025e-05 | 0.502236661 | +2.08387e-08 | -0.0009997 |
| cxpair_q0_h6_36_37 | 4.3914711061e-05 | 0.502305147 | +2.05657e-08 | -0.0010682 |
| cxpair_q0_h6_37_38 | 4.3914711061e-05 | 0.502305147 | +2.05657e-08 | -0.0010682 |
| moving_helper_q4_h10_30_31_n1 | 4.3915719510e-05 | 0.502234976 | +1.95573e-08 | -0.0009980 |
| early_q10_h9_21_22_n1 | 4.3916135591e-05 | 0.502236924 | +1.91412e-08 | -0.0010000 |
| repair_new_16_Z_q15_h16 | 4.3920466779e-05 | 0.501629400 | +1.48100e-08 | -0.0003925 |
| early_q7_h1_21_22_n1 | 4.3920496445e-05 | 0.502236899 | +1.47803e-08 | -0.0010000 |
| new_02_Z_q20_h26 | 4.3927383375e-05 | 0.495326435 | +7.89339e-09 | +0.0059105 |
| fold_q20_h26_19_30_reset | 4.3927390859e-05 | 0.494998085 | +7.88590e-09 | +0.0062389 |
| ST2/echo_20_26_Z_20_30 | 4.3928043862e-05 | 0.495819718 | +7.23290e-09 | +0.0054172 |
| new_00_Z_q20_h21 | 4.3928043863e-05 | 0.495819718 | +7.23290e-09 | +0.0054172 |
| fold_q10_h16_20_27_first_use | 4.3931915448e-05 | 0.499637240 | +3.36131e-09 | +0.0015997 |
| fold_q10_h16_20_27_reset | 4.3931915448e-05 | 0.499637240 | +3.36131e-09 | +0.0015997 |
| fold_q10_h16_20_27_mz_parity | 4.3932165650e-05 | 0.498807427 | +3.11111e-09 | +0.0024295 |
| ST2/echo_10_16_X_21_27 | 4.3932173154e-05 | 0.499633390 | +3.10361e-09 | +0.0016035 |
| fresh_all | 4.3932917032e-05 | 0.508286499 | +2.35973e-09 | -0.0070496 |
| fresh_three | 4.3932923617e-05 | 0.506598317 | +2.35314e-09 | -0.0053614 |
| ST2/mz_19_33 | 4.3933615176e-05 | 0.500568883 | +1.66158e-09 | +0.0006681 |
| fresh_q22_t34 | 4.3933836346e-05 | 0.503241262 | +1.44041e-09 | -0.0020043 |
| repair_new_08_Z_q10_h16 | 4.3934034454e-05 | 0.501797542 | +1.24231e-09 | -0.0005606 |
| new_07_X_q10_h16 | 4.3934063565e-05 | 0.499967411 | +1.21320e-09 | +0.0012695 |
| fold_q10_h16_20_22_first_use | 4.3934064431e-05 | 0.500468416 | +1.21233e-09 | +0.0007685 |
| fold_q10_h16_20_22_reset | 4.3934064431e-05 | 0.500468416 | +1.21233e-09 | +0.0007685 |
| new_09_X_q10_h16 | 4.3934076378e-05 | 0.501630902 | +1.20038e-09 | -0.0003940 |
| early_q10_h16_25_27_n1 | 4.3934283221e-05 | 0.501968091 | +9.93540e-10 | -0.0007312 |
| fold_q10_h16_20_22_mz_parity | 4.3934315862e-05 | 0.499640839 | +9.60898e-10 | +0.0015961 |
| new_06_Z_q10_h16 | 4.3934412104e-05 | 0.500300449 | +8.64656e-10 | +0.0009365 |
| ST2/echo_10_16_X_21_22 | 4.3934412105e-05 | 0.500467215 | +8.64656e-10 | +0.0007697 |
| late_resets_joint | 4.3934492104e-05 | 0.505244596 | +7.84657e-10 | -0.0040077 |
| late_reset_q19 | 4.3934543492e-05 | 0.502565914 | +7.33269e-10 | -0.0013290 |
| ST2/watch16_t30 | 4.3934773147e-05 | 0.500733542 | +5.03613e-10 | +0.0005034 |
| fresh_q16_t30 | 4.3934773147e-05 | 0.503239027 | +5.03613e-10 | -0.0020021 |
| new_21_X_q16_h17 | 4.3934842384e-05 | 0.498770203 | +4.34376e-10 | +0.0024667 |
| ablate_q21_refresh_m36 | 4.3934867452e-05 | 0.500902080 | +4.09308e-10 | +0.0003349 |
| fresh_q21_t36 | 4.3934867452e-05 | 0.502573197 | +4.09308e-10 | -0.0013363 |
| ablate_q21_measurement36 | 4.3934867453e-05 | 0.500735781 | +4.09308e-10 | +0.0005012 |
| ablate_q21_reset36 | 4.3934918667e-05 | 0.502405606 | +3.58093e-10 | -0.0011687 |
| guard277_mz_parity | 4.3934957162e-05 | 0.500403768 | +3.19598e-10 | +0.0008332 |
| ablate_q21_refresh_m35 | 4.3934969779e-05 | 0.500901503 | +3.06981e-10 | +0.0003354 |
| new_12_Z_q22_h28 | 4.3934989142e-05 | 0.500100956 | +2.87619e-10 | +0.0011360 |
| new_13_X_q22_h28 | 4.3934989142e-05 | 0.500100956 | +2.87619e-10 | +0.0011360 |
| new_11_X_q22_h23 | 4.3934989142e-05 | 0.500267656 | +2.87619e-10 | +0.0009693 |
| new_10_X_q22_h21 | 4.3934989142e-05 | 0.500267656 | +2.87618e-10 | +0.0009693 |
| guard275_mz_parity | 4.3935023208e-05 | 0.501403860 | +2.53552e-10 | -0.0001669 |
| ablate_q21_refresh_m34 | 4.3935072107e-05 | 0.500901372 | +2.04654e-10 | +0.0003356 |
| guard276_mz_parity | 4.3935076344e-05 | 0.500405390 | +2.00416e-10 | +0.0008315 |
| new_22_X_q16_h22 | 4.3935176200e-05 | 0.500267212 | +1.00560e-10 | +0.0009697 |
| new_20_Z_q16_h17 | 4.3935178127e-05 | 0.497446296 | +9.86337e-11 | +0.0037906 |
| guard274_mz_parity | 4.3935185011e-05 | 0.501402839 | +9.17490e-11 | -0.0001659 |
| late_reset_q13 | 4.3935225372e-05 | 0.503908537 | +5.13885e-11 | -0.0026716 |
| fresh_q20_t7 | 4.3935270175e-05 | 0.502907255 | +6.58504e-12 | -0.0016703 |
| ST2/mz_13_25 | 4.3935273545e-05 | 0.500568242 | +3.21511e-12 | +0.0006687 |
| guard276_omit | 4.3935276760e-05 | 0.501236939 | +0.00000e+00 | +0.0000000 |
| guard277_omit | 4.3935276760e-05 | 0.501236939 | +0.00000e+00 | +0.0000000 |
| ST2/reuse_13_25 | 4.3935279969e-05 | 0.501071075 | -3.20855e-12 | +0.0001659 |
| guard274_omit | 4.3935368325e-05 | 0.501071481 | -9.15644e-11 | +0.0001655 |
| moving_helper_q4_h10_20_27_n1 | 4.3936709542e-05 | 0.502233522 | -1.43278e-09 | -0.0009966 |
| ST2/reuse_19_33 | 4.3936935016e-05 | 0.501070435 | -1.65826e-09 | +0.0001665 |
| new_01_X_q20_h21 | 4.3938961102e-05 | 0.495510066 | -3.68434e-09 | +0.0057269 |
| new_03_X_q20_h26 | 4.3938961102e-05 | 0.495344951 | -3.68434e-09 | +0.0058920 |
| early_q0_h6_26_29_n1 | 4.3939839796e-05 | 0.502300179 | -4.56304e-09 | -0.0010632 |
| moving_helper_q4_h10_20_27_n4 | 4.3941033569e-05 | 0.505240860 | -5.75681e-09 | -0.0040039 |
| early_q0_h6_26_29_n2 | 4.3944446870e-05 | 0.503366650 | -9.17011e-09 | -0.0021297 |
| early_q15_h9_24_27_n1 | 4.3948370626e-05 | 0.502235800 | -1.30939e-08 | -0.0009989 |
| early_q20_h19_19_30_n1 | 4.3948852076e-05 | 0.502300697 | -1.35753e-08 | -0.0010638 |
| guard274_w18_30 | 4.3954091937e-05 | 0.503066591 | -1.88152e-08 | -0.0018297 |
| guard274_w19_31 | 4.3954091937e-05 | 0.503066591 | -1.88152e-08 | -0.0018297 |
| live_Z_q0_h6_36_38 | 4.3960379591e-05 | 0.502473953 | -2.51028e-08 | -0.0012370 |
| live_X_q0_h6_36_38 | 4.3960611876e-05 | 0.502473289 | -2.53351e-08 | -0.0012364 |
| early_q15_h9_24_27_n2 | 4.3961533081e-05 | 0.503237595 | -2.62563e-08 | -0.0020007 |
| early_q20_h14_26_30_n1 | 4.3961594033e-05 | 0.502233218 | -2.63173e-08 | -0.0009963 |
| ST2/resource_262_reset | 4.3961744723e-05 | 0.501071140 | -2.64680e-08 | +0.0001658 |
| ST2/resource_260_reset | 4.3961853548e-05 | 0.501071373 | -2.65768e-08 | +0.0001656 |
| ST2/resource_256_reset | 4.3974132291e-05 | 0.501071098 | -3.88555e-08 | +0.0001658 |
| guard273_w35_38 | 4.3980776288e-05 | 0.501738489 | -4.54995e-08 | -0.0005016 |
| guard273_w36_39 | 4.3980776288e-05 | 0.501738489 | -4.54995e-08 | -0.0005016 |
| live_X_q4_h5_30_31 | 4.3986343500e-05 | 0.502300759 | -5.10667e-08 | -0.0010638 |
| live_Z_q4_h5_30_31 | 4.3986343500e-05 | 0.502300759 | -5.10667e-08 | -0.0010638 |
| early_q20_h14_26_30_n2 | 4.3987964337e-05 | 0.503232424 | -5.26876e-08 | -0.0019955 |
| early_q10_h11_20_27_n1 | 4.3987983846e-05 | 0.502304047 | -5.27071e-08 | -0.0010671 |
| cxpair_q20_h14_33_34 | 4.3991725661e-05 | 0.502300060 | -5.64489e-08 | -0.0010631 |
| cxpair_q20_h14_34_35 | 4.3991725661e-05 | 0.502300060 | -5.64489e-08 | -0.0010631 |
| cxpair_q20_h14_32_33 | 4.3991725662e-05 | 0.502300060 | -5.64489e-08 | -0.0010631 |
| nested15_Z_standalone | 4.3996654242e-05 | 0.500138014 | -6.13775e-08 | +0.0010989 |
| early_q3_h2_18_25_n1 | 4.3999305145e-05 | 0.502234630 | -6.40284e-08 | -0.0009977 |
| guard277_w19_32 | 4.4001890039e-05 | 0.501735501 | -6.66133e-08 | -0.0004986 |
| guard277_w18_31 | 4.4001890039e-05 | 0.501401791 | -6.66133e-08 | -0.0001649 |
| guard276_w20_28 | 4.4002206775e-05 | 0.501737200 | -6.69300e-08 | -0.0005003 |
| guard276_w19_27 | 4.4002206775e-05 | 0.501403936 | -6.69300e-08 | -0.0001670 |
| fold15_h16_Z_20_28_reset30 | 4.4012018991e-05 | 0.499641551 | -7.67422e-08 | +0.0015954 |
| early_q3_h9_21_22_n1 | 4.4013797937e-05 | 0.502236995 | -7.85212e-08 | -0.0010001 |
| early_q0_h1_18_25_n1 | 4.4015191752e-05 | 0.502232416 | -7.99150e-08 | -0.0009955 |
| early_q20_h19_19_30_n6 | 4.4016834292e-05 | 0.507668200 | -8.15575e-08 | -0.0064313 |
| early_q8_h14_27_29_n1 | 4.4022028985e-05 | 0.502233789 | -8.67522e-08 | -0.0009969 |
| cxpair_q10_h9_39_40 | 4.4024273790e-05 | 0.502300872 | -8.89970e-08 | -0.0010639 |
| cxpair_q10_h9_40_41 | 4.4024273790e-05 | 0.502300872 | -8.89970e-08 | -0.0010639 |
| guard273_w35_37 | 4.4026369305e-05 | 0.502240935 | -9.10925e-08 | -0.0010040 |
| guard273_w37_39 | 4.4026369305e-05 | 0.502240935 | -9.10925e-08 | -0.0010040 |
| new_18_Z_q15_h21 | 4.4027888305e-05 | 0.496332164 | -9.26115e-08 | +0.0049048 |
| cxpair_q3_h9_41_42 | 4.4044623236e-05 | 0.502233146 | -1.09346e-07 | -0.0009962 |
| cxpair_q3_h9_39_40 | 4.4044623236e-05 | 0.502233146 | -1.09346e-07 | -0.0009962 |
| cxpair_q3_h9_40_41 | 4.4044623236e-05 | 0.502233146 | -1.09346e-07 | -0.0009962 |
| early_q15_h14_20_24_n1 | 4.4053459674e-05 | 0.502232845 | -1.18183e-07 | -0.0009959 |
| early_q15_h14_26_29_n1 | 4.4053563958e-05 | 0.502231787 | -1.18287e-07 | -0.0009948 |
| early_q3_h9_24_27_n1 | 4.4053762211e-05 | 0.502236527 | -1.18485e-07 | -0.0009996 |
| guard274_w18_24 | 4.4071703206e-05 | 0.506089482 | -1.36426e-07 | -0.0048525 |
| guard274_w25_31 | 4.4071703206e-05 | 0.506089482 | -1.36426e-07 | -0.0048525 |
| early_q10_h11_20_27_n4 | 4.4146204962e-05 | 0.505524878 | -2.10928e-07 | -0.0042879 |
| early_q7_h13_21_22_n1 | 4.4149646372e-05 | 0.502307250 | -2.14370e-07 | -0.0010703 |
| early_q15_h14_20_24_n2 | 4.4171780564e-05 | 0.503231675 | -2.36504e-07 | -0.0019947 |
| early_q15_h14_26_29_n2 | 4.4171994229e-05 | 0.503229554 | -2.36717e-07 | -0.0019926 |
| early_q3_h9_24_27_n2 | 4.4172365717e-05 | 0.503239052 | -2.37089e-07 | -0.0020021 |
| ST2/guard_273_off | 4.4183999156e-05 | 0.503687016 | -2.48722e-07 | -0.0024501 |
| early_q3_h2_18_25_n4 | 4.4191932413e-05 | 0.505245320 | -2.56656e-07 | -0.0040084 |
| ST2/guard_274_off | 4.4195868915e-05 | 0.509588963 | -2.60592e-07 | -0.0083520 |
| guard275_w20_22 | 4.4204663465e-05 | 0.501738492 | -2.69387e-07 | -0.0005016 |
| guard275_w21_23 | 4.4204663465e-05 | 0.501738492 | -2.69387e-07 | -0.0005016 |
| early_q4_h5_19_31_n6 | 4.4241962205e-05 | 0.507668570 | -3.06685e-07 | -0.0064316 |
| early_q0_h1_18_25_n4 | 4.4255433771e-05 | 0.505236416 | -3.20157e-07 | -0.0039995 |
| cxpair_q7_h6_36_37 | 4.4256635024e-05 | 0.502235160 | -3.21358e-07 | -0.0009982 |
| cxpair_q7_h6_37_38 | 4.4256635024e-05 | 0.502235160 | -3.21358e-07 | -0.0009982 |
| live_X_q20_h14_32_35 | 4.4259065837e-05 | 0.502636933 | -3.23789e-07 | -0.0014000 |
| live_Z_q20_h14_32_35 | 4.4263334076e-05 | 0.502633360 | -3.28057e-07 | -0.0013964 |
| guard276_w24_28 | 4.4270382521e-05 | 0.503747182 | -3.35106e-07 | -0.0025102 |
| guard276_w19_23 | 4.4270382521e-05 | 0.502078642 | -3.35106e-07 | -0.0008417 |
| live_X_q3_h4_38_39 | 4.4300387638e-05 | 0.502299716 | -3.65111e-07 | -0.0010628 |
| live_Z_q3_h4_38_39 | 4.4300387638e-05 | 0.502299716 | -3.65111e-07 | -0.0010628 |
| early_q7_h6_27_29_n1 | 4.4324710494e-05 | 0.502235187 | -3.89434e-07 | -0.0009982 |
| guard274_dualZ | 4.4391159431e-05 | 0.502604164 | -4.55883e-07 | -0.0013672 |
| guard277_w18_25 | 4.4402559443e-05 | 0.502405005 | -4.67283e-07 | -0.0011681 |
| guard277_w25_32 | 4.4402559443e-05 | 0.504745604 | -4.67283e-07 | -0.0035087 |
| guard275_w20_21 | 4.4474230756e-05 | 0.502240939 | -5.38954e-07 | -0.0010040 |
| guard275_w22_23 | 4.4474230756e-05 | 0.502240939 | -5.38954e-07 | -0.0010040 |
| live_Z_q10_h9_39_41 | 4.4477984940e-05 | 0.502382889 | -5.42708e-07 | -0.0011460 |
| cxpair_q3_h4_41_42 | 4.4515116192e-05 | 0.502299578 | -5.79839e-07 | -0.0010626 |
| cxpair_q3_h4_42_43 | 4.4515116192e-05 | 0.502299578 | -5.79839e-07 | -0.0010626 |
| ST2/guard_276_off | 4.4553744836e-05 | 0.507053703 | -6.18468e-07 | -0.0058168 |
| live_X_q22_h16_42_43 | 4.4708100155e-05 | 0.502432567 | -7.72823e-07 | -0.0011956 |
| live_Z_q22_h16_42_43 | 4.4708100155e-05 | 0.502432567 | -7.72823e-07 | -0.0011956 |
| ST2/guard_275_off | 4.4799304347e-05 | 0.503180377 | -8.64028e-07 | -0.0019434 |
| ST2/guard_277_off | 4.4888060828e-05 | 0.508910374 | -9.52784e-07 | -0.0076734 |
| guard276_dualZ | 4.5013333386e-05 | 0.501425621 | -1.07806e-06 | -0.0001887 |
| guard275_dualZ | 4.5016579323e-05 | 0.501239559 | -1.08130e-06 | -0.0000026 |
| live_X_q10_h9_39_41 | 4.5270237686e-05 | 0.502467616 | -1.33496e-06 | -0.0012307 |
| live_Z_q3_h9_39_42 | 4.5299999111e-05 | 0.502229269 | -1.36472e-06 | -0.0009923 |
| live_Z_q7_h6_36_38 | 4.5398117764e-05 | 0.502234088 | -1.46284e-06 | -0.0009971 |
| live_X_q3_h9_39_42 | 4.5437120687e-05 | 0.502232362 | -1.50184e-06 | -0.0009954 |
| live_X_q7_h6_36_38 | 4.5475939818e-05 | 0.502235049 | -1.54066e-06 | -0.0009981 |
| guard277_dualZ | 4.5673984434e-05 | 0.501438339 | -1.73871e-06 | -0.0002014 |
| live_X_q3_h4_41_43 | 4.6338107662e-05 | 0.502464603 | -2.40283e-06 | -0.0012277 |
| live_Z_q3_h4_41_43 | 4.6349563187e-05 | 0.502465474 | -2.41429e-06 | -0.0012285 |

Negative acceptance cost means recovered acceptance. These marginal prices guide proposals; no joint loss is inferred by addition.

Previous v30f campaign and its completed evidence: [REPORT_v30f.md](REPORT_v30f.md). No submissions, commits, pushes or credentials.

## Mechanisms and decisions

The acceptance budget changed the best construction. The original five guards remain useful, but preparation timing creates substantially more budget than removing one of them. Moving q19's guard reset from13 to17 and q13's resource reset from25 to33 changes the complete circuit from loss4.393527676e-5/acceptance0.501236939 to4.393449210e-5/0.505244596. Moving the initial measurements of fresh cells16/21/22 to just before first use gives4.393292362e-5/0.506598317. These changes remove rejected idle faults. They are separately priced, and every combination is repriced.

The most useful new separate guard uses q13 after its first guard measurement: reset+H at26, CX13→7 at27 and31, MX13 at32, then the original resource reset at33. With that reset retiming included, its standalone loss is4.375436491e-5 and acceptance0.501463648. It protects Z/Y on q7 while accepting some helper-X faults. The X dual is weaker on this window. A no-reset X reuse was also priced; its detector uses the prior helper record.

A q15–q21 X guard can reuse q21's existing initialization measurement as its final detector. The folded form loses4.377074460e-5 at acceptance0.496647017; the separate-readout form imported from ST2 loses4.377045625e-5 at0.496147736. Folding saves approximately0.0004993 acceptance for a2.88e-10 loss cost. Sharing this helper with q20 can outperform an isolated q15 guard, but the endpoint order matters. Crossing a q20–q26 guard endpoint changes the ideal instrument and fails correctness; the successful shared variant nests the extra CXs within compatible endpoints.

Existing syndrome helpers allow a cheaper family: apply the same adjacent CX twice while both wires are otherwise idle, and use the existing detector. No new helper preparation/readout is required. For consecutive endpoints, the CXs cancel ideally and isotropic two-qubit depolarization commutes through them. Both orientations give identical channels; seven independently priced orientation pairs agree within1e-13. At p=0.001, two CX noise channels compose to DEPOLARIZE2 with probability0.001998933333. For an ideal Z helper and ideal Z herald, the conditional data-error probability is0.000800427, versus0.001998667 for two data idles alone. Real rankings include the helper's preparation/readout, other idles, future resource use and all joint faults. See [v35/cx_pair_mechanism.json](v35/cx_pair_mechanism.json).

This effect is strongly location-dependent. Consecutive q10/q16 CXs at37/38 give4.357768608e-5 and acceptance0.501967588, while q3/q4 at41/42 give4.451511619e-5 despite higher acceptance. Filling all five existing guard interiors gives4.472885648e-5/0.520796827 and loses. Acceptance recovery alone is not the objective.

## Fault evidence and coverage

The unchanged exact2 pair diagnostic for v35a gives second order3.813456124748495e-5. Symmetric channel attribution: idle2.141335469781621e-5, gates1.632120654966874e-5, flips4.0e-7. Four leading1.549e-7 pairs combine data-q10 Z idles during35–41 with A-resource faults at41–43. The largest pair is q4's reset flip at36 with q17's idle at42,1.667e-7. The unavoidable final data idles remain prominent. [Per-run attribution](v35/base_wait_pair_decomposition.json) and [unchanged evaluator log](v35/base.pair_decomposition.log) distinguish this second-order evidence from the all-orders ranking.

The mapped data order is[0,20,7,10,3,22,21]. After the cultivation prefix, output10 moves4→10 at33/34; output22 moves15→16 at31–33, then16→22 at35/36; output21 moves8→9 at33/34,9→15 at35/36,15→21 at37/38. Earlier q10 is an ancilla, not the final data10. Cells labelled as eventual outputs can still be helpers before those transfers; the closing sweep includes cells10 and21 in that role.

Fano lines in this labelling are(0,20,7), (0,10,3), (20,10,22), (7,3,22), (7,10,21), (20,3,21), (0,22,21). The final combinations cover the feasible(0,20,7) line with Z guards, including a separate released-q7 guard; sharing the existing q0 helper with q7 late was directly priced and lost. A separate new four-operation helper window does not fit output21's final wait. Existing-helper CX pairs on its earlier cell8 were priced and lost. This is a finite search over the documented native windows, helper lifetimes and complete combinations, not a global circuit optimum.

## Negative results and corrections

- Shortening the five guards recovers acceptance but loses useful detection. The q7 X guard20–23 is especially efficient: removing one endpoint tick costs about2.69e-7 in loss for0.000502 acceptance. Its full window was retained.
- Early Z duals and some nested X/Z combinations add helper-X exposure in expensive fault signatures. The menu records their complete loss and acceptance; no negative is hidden by ranking only a pair-order approximation.
- A Z guard can leave a measured helper in the X basis even though the next data-transfer operation expects a Z-basis initialization. The exact2/Stim path rejects these cases. Restoring the Z basis needs a free tick; where none exists, the old initialization must be replaced explicitly. The repaired q20/q21 Z variant is priced as a distinct circuit.
- The first shared-helper endpoint19 conflicted with its preparation and with a crossing existing guard. Native-slot checks caught the scheduling conflict; noiseless checks caught the crossing instrument. The successful variant uses21/28. Failed source files and errors are retained.
- The initial helper enumeration excluded all eventual output labels. That was too broad: cells10 and21 can be available before data arrives. The moving-helper sweep corrects that omission explicitly.
- An owl probe sharing an eight-CPU quota with active pricing reported24.44s/1e6 for the reset-retimed control. On zebra the same bytes pass FAST at7.97s/1e6; the baseline comparison is4.38s/1e6. Both receipts are retained. Finalist gates and speed comparisons use zebra; full MC runs use owl.

## Verification scope

The lane-local sparse evaluator and its six supporting files are byte-identical to MAIN's implementation; [source hashes](v35/source_hashes.json) record this. The canonicalized baseline exactly reproduces v35a. All priced circuits first pass the official exact2/Stim noiseless path; invalid instruments retain errors. All-orders contractions use72 observables, canonical detector rows, full used-qubit barriers, no FRAME/POSTSELECT, and no fault-order truncation. Sparse omission bounds are approximately1.2e-14, excluding floating-point roundoff.

For finalists, independent frontend audits compare every noise channel/probability and Pauli fault signature against the official Model, plus every rotation, projector, decoder observable and native tick. Official1e6 gates, unchanged XTIM speed probes and unchanged MAIN three-seed MC are recorded separately. MC means are measurements; the all-orders expectation determines ranking. The best observed seed0 draw is exported separately.

The menu includes exact native-tick patches and full standalone prices for ST2. [The per-run index](menu_v35a_by_run.json) gives every mapped data wait, compatible priced additions, acceptance-free gains and the local loss/acceptance frontier. Q0 at33 and q7 at34 have only one idle tick. Q0 at40–43, q20 at37–42 and q21 at39–42 have no separate helper slot under this schedule; the non-data neighbours are occupied. The index explicitly leaves these runs without a new gadget rather than inventing one. Imported ST2 prices retain their source paths; its physical-removal/detector knapsack was not rerun. Combination prices are full reevaluations, not sums of the menu gains. No submissions, commits, pushes, credentials or subagents were used.

The terminal comparison worker initially shared the lifetime of another Docker container and exited137 when that original batch finished. All four unfinished cases were restarted in their own named container. No incomplete price was used; completed receipts and the failed process exit are preserved in `v35/run_completion.json`.

