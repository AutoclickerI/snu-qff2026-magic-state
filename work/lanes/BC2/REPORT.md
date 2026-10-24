# BC2 report

Best verified: [compact_clean_d14_k100_m27_29_m25_28.qasm](compact_clean_d14_k100_m27_29_m25_28.qasm), mean **8.4643109e-05**, seed-0 acceptance **0.54027823**; prep 14 layers / 82 CX, round starts at 50.

Objective: full-circuit 1-F only, with judge format/class/correctness and official seed-0 acceptance ≥ 0.5. No submission was made. All lane writes are contained here.

The exact columns are evaluations through order three only when |c1| < 1e-12. `c1` below is the evaluator’s first-order contribution at p=0.001 (its printed `c1 p`). `exp(-A1)` is an estimate. MC entries are 100,000,000 shots each.

Baseline reference supplied in the brief: 1.0382e-4 (100-redraw mean). Our same-text three-seed baseline is recorded in `v14_bcm.score.json`; this is the direct comparison used here.

| Candidate | Prep depth | Prep CX | Rule/recipe | c1 p | 2nd | 3rd | Total through 3rd | exp(-A1) | MC seed 0 | MC 1000 | MC 2000 | MC mean | Seed-0 acceptance | 1e6 judge | Files |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| compact_clean_d14_k100_m27_29_m25_28 | 14 | 82 | clean | 3.182639e-19 | 5.839533e-05 | 2.603291e-05 | 8.442825e-05 | 0.5402158 | 8.401227e-05 | 8.518898e-05 | 8.472808e-05 | 8.464311e-05 | 0.5402782 | PASS | [compact_clean_d14_k100_m27_29_m25_28.qasm](compact_clean_d14_k100_m27_29_m25_28.qasm), [metadata](compact_clean_d14_k100_m27_29_m25_28.json), [receipt](compact_clean_d14_k100_m27_29_m25_28.score.json) |
| compact_base_d13_k82_m27_29_m23_28 | 13 | 73 | base | 3.515706e-19 | 6.575324e-05 | 2.088248e-05 | 8.663572e-05 | 0.5579072 | 8.844162e-05 | 8.710144e-05 | 8.74984e-05 | 8.768049e-05 | 0.5581648 | PASS | [compact_base_d13_k82_m27_29_m23_28.qasm](compact_base_d13_k82_m27_29_m23_28.qasm), [metadata](compact_base_d13_k82_m27_29_m23_28.json), [receipt](compact_base_d13_k82_m27_29_m23_28.score.json) |
| compact_clean_d14_k100_m27_29 | 14 | 82 | clean | 3.182639e-19 | 5.900644e-05 | 2.605646e-05 | 8.50629e-05 | 0.5420195 | 8.830823e-05 | 8.879498e-05 | 8.619417e-05 | 8.776579e-05 | 0.5421352 | PASS | [compact_clean_d14_k100_m27_29.qasm](compact_clean_d14_k100_m27_29.qasm), [metadata](compact_clean_d14_k100_m27_29.json), [receipt](compact_clean_d14_k100_m27_29.score.json) |
| compact_base_d13_k82_m27_29 | 13 | 73 | base | 3.515706e-19 | 6.636435e-05 | 2.09059e-05 | 8.727025e-05 | 0.55977 | 8.709376e-05 | 8.822063e-05 | 9.036419e-05 | 8.855952e-05 | 0.5600861 | PASS | [compact_base_d13_k82_m27_29.qasm](compact_base_d13_k82_m27_29.qasm), [metadata](compact_base_d13_k82_m27_29.json), [receipt](compact_base_d13_k82_m27_29.score.json) |
| compact_clean_d15_k100_m27_29 | 15 | 81 | clean | 3.182639e-19 | 6.485417e-05 | 2.861326e-05 | 9.346743e-05 | 0.5349493 | 9.457173e-05 | 9.518828e-05 | 9.406342e-05 | 9.460781e-05 | 0.5350965 | PASS | [compact_clean_d15_k100_m27_29.qasm](compact_clean_d15_k100_m27_29.qasm), [metadata](compact_clean_d15_k100_m27_29.json), [receipt](compact_clean_d15_k100_m27_29.score.json) |
| compact_clean_d16_k100_m27_29 | 16 | 90 | clean | 3.182639e-19 | 6.519358e-05 | 2.9862e-05 | 9.505558e-05 | 0.5301857 | 9.481378e-05 | 9.601505e-05 | 9.635718e-05 | 9.572867e-05 | 0.5304081 | PASS | [compact_clean_d16_k100_m27_29.qasm](compact_clean_d16_k100_m27_29.qasm), [metadata](compact_clean_d16_k100_m27_29.json), [receipt](compact_clean_d16_k100_m27_29.score.json) |
| combo_18_33_m27_29 | 15 | 86 | extra Z flags | 4.847974e-19 | 6.770206e-05 | 3.266519e-05 | 0.0001003672 | 0.5214731 | 0.0001035681 | 0.0001011838 | 0.0001006642 | 0.0001018054 | 0.5217338 | PASS | [combo_18_33_m27_29.qasm](combo_18_33_m27_29.qasm), [metadata](combo_18_33_m27_29.json), [receipt](combo_18_33_m27_29.score.json) |
| combo_18_34_m27_29 | 15 | 86 | extra Z flags | 4.699944e-19 | 6.801985e-05 | 3.26074e-05 | 0.0001006273 | 0.5211716 | 0.0001017693 | 0.000104293 | 0.0001022793 | 0.0001027805 | 0.5214243 | PASS | [combo_18_34_m27_29.qasm](combo_18_34_m27_29.qasm), [metadata](combo_18_34_m27_29.json), [receipt](combo_18_34_m27_29.score.json) |
| v14_bcm | 14 | 82 | baseline | 5.070018e-19 | 7.333299e-05 | 2.856117e-05 | 0.0001018942 | 0.5440838 | 0.0001025239 | 0.0001043763 | 0.0001042962 | 0.0001037321 | 0.5443609 | PASS | [v14_bcm.qasm](v14_bcm.qasm), [metadata](v14_bcm.json), [receipt](v14_bcm.score.json) |
| compact_clean_d15_k82_m27_29 | 15 | 82 | clean | 3.182639e-19 | 7.091883e-05 | 3.029504e-05 | 0.0001012139 | 0.5310765 | 0.0001047807 | 0.000101978 | 0.0001047204 | 0.0001038264 | 0.5312526 | PASS | [compact_clean_d15_k82_m27_29.qasm](compact_clean_d15_k82_m27_29.qasm), [metadata](compact_clean_d15_k82_m27_29.json), [receipt](compact_clean_d15_k82_m27_29.score.json) |
| flag_35_0q29_1q29_m27_29 | 14 | 84 | extra Z flags | 5.218048e-19 | 7.445299e-05 | 2.860043e-05 | 0.0001030534 | 0.5372669 | 0.0001036836 | 0.0001030063 | 0.0001055907 | 0.0001040935 | 0.5375005 | PASS | [flag_35_0q29_1q29_m27_29.qasm](flag_35_0q29_1q29_m27_29.qasm), [metadata](flag_35_0q29_1q29_m27_29.json), [receipt](flag_35_0q29_1q29_m27_29.score.json) |
| flag_35_2q29_4q29_m27_29 | 14 | 84 | extra Z flags | 5.070018e-19 | 7.37193e-05 | 2.89183e-05 | 0.0001026376 | 0.537325 | 0.0001020776 | 0.0001061366 | 0.0001040989 | 0.0001041044 | 0.5375321 | PASS | [flag_35_2q29_4q29_m27_29.qasm](flag_35_2q29_4q29_m27_29.qasm), [metadata](flag_35_2q29_4q29_m27_29.json), [receipt](flag_35_2q29_4q29_m27_29.score.json) |
| flag_35_2q29_3q29_m27_29 | 14 | 84 | extra Z flags | 5.070018e-19 | 7.37193e-05 | 2.89183e-05 | 0.0001026376 | 0.537325 | 0.000104006 | 0.0001047734 | 0.0001037903 | 0.0001041899 | 0.5375653 | PASS | [flag_35_2q29_3q29_m27_29.qasm](flag_35_2q29_3q29_m27_29.qasm), [metadata](flag_35_2q29_3q29_m27_29.json), [receipt](flag_35_2q29_3q29_m27_29.score.json) |
| window_base_6_k82_m27_29 | 14 | 82 | base local SAT | 5.070018e-19 | 7.333299e-05 | 2.856117e-05 | 0.0001018942 | 0.5440838 | 0.0001041861 | 0.0001041662 | 0.0001047177 | 0.0001043567 | 0.5442663 | PASS | [window_base_6_k82_m27_29.qasm](window_base_6_k82_m27_29.qasm), [metadata](window_base_6_k82_m27_29.json), [receipt](window_base_6_k82_m27_29.score.json) |
| flag_34_3q28_5q28_m27_29 | 14 | 84 | extra Z flags | 5.070018e-19 | 7.492944e-05 | 2.970126e-05 | 0.0001046307 | 0.5330434 | 0.0001060341 | 0.0001066793 | 0.0001057696 | 0.000106161 | 0.5332717 | PASS | [flag_34_3q28_5q28_m27_29.qasm](flag_34_3q28_5q28_m27_29.qasm), [metadata](flag_34_3q28_5q28_m27_29.json), [receipt](flag_34_3q28_5q28_m27_29.score.json) |
| flag_33_4q27_11q27_m27_29 | 15 | 84 | extra Z flags | 4.847974e-19 | 7.166632e-05 | 3.323742e-05 | 0.0001049037 | 0.5242659 | 0.0001071209 | 0.0001061266 | 0.0001061681 | 0.0001064718 | 0.524501 | PASS | [flag_33_4q27_11q27_m27_29.qasm](flag_33_4q27_11q27_m27_29.qasm), [metadata](flag_33_4q27_11q27_m27_29.json), [receipt](flag_33_4q27_11q27_m27_29.score.json) |
| flag_34_5q28_13q28_m27_29 | 15 | 84 | extra Z flags | 4.699944e-19 | 7.193167e-05 | 3.295614e-05 | 0.0001048878 | 0.5246556 | 0.0001101448 | 0.0001082011 | 0.0001066356 | 0.0001083272 | 0.5249454 | PASS | [flag_34_5q28_13q28_m27_29.qasm](flag_34_5q28_13q28_m27_29.qasm), [metadata](flag_34_5q28_13q28_m27_29.json), [receipt](flag_34_5q28_13q28_m27_29.score.json) |
| combo_18_33_34_m27_29 | 16 | 88 | extra Z flags | 4.699944e-19 | 6.824136e-05 | 3.744485e-05 | 0.0001056862 | 0.504748 | — | — | — | — | — | PASS | [combo_18_33_34_m27_29.qasm](combo_18_33_34_m27_29.qasm), [metadata](combo_18_33_34_m27_29.json), [receipt](combo_18_33_34_m27_29.score.json) |
| combo_33_34_m27_29 | 16 | 86 | extra Z flags | 4.699944e-19 | 7.238667e-05 | 3.809438e-05 | 0.000110481 | 0.5074566 | — | — | — | — | — | PASS | [combo_33_34_m27_29.qasm](combo_33_34_m27_29.qasm), [metadata](combo_33_34_m27_29.json), [receipt](combo_33_34_m27_29.score.json) |
| compact_base_d14_k100_m27_29 | 14 | 79 | base | 3.441691e-19 | 8.248802e-05 | 2.91957e-05 | 0.0001116837 | 0.5420968 | — | — | — | — | — | PASS | [compact_base_d14_k100_m27_29.qasm](compact_base_d14_k100_m27_29.qasm), [metadata](compact_base_d14_k100_m27_29.json), [receipt](compact_base_d14_k100_m27_29.score.json) |
| compact_base_d14_k82_m27_29 | 14 | 78 | base | 4.218108e-19 | 8.435741e-05 | 2.767733e-05 | 0.0001120347 | 0.545277 | — | — | — | — | — | PASS | [compact_base_d14_k82_m27_29.qasm](compact_base_d14_k82_m27_29.qasm), [metadata](compact_base_d14_k82_m27_29.json), [receipt](compact_base_d14_k82_m27_29.score.json) |
| compact_base_d15_k100_m27_29 | 15 | 81 | base | 5.981689e-19 | 9.769546e-05 | 3.396347e-05 | 0.0001316589 | 0.532508 | — | — | — | — | — | PASS | [compact_base_d15_k100_m27_29.qasm](compact_base_d15_k100_m27_29.qasm), [metadata](compact_base_d15_k100_m27_29.json), [receipt](compact_base_d15_k100_m27_29.score.json) |
| compact_base_d16_k100_m27_29 | 16 | 83 | base | 3.848773e-19 | 8.786613e-05 | 3.478576e-05 | 0.0001226519 | 0.5269463 | — | — | — | — | — | PASS | [compact_base_d16_k100_m27_29.qasm](compact_base_d16_k100_m27_29.qasm), [metadata](compact_base_d16_k100_m27_29.json), [receipt](compact_base_d16_k100_m27_29.score.json) |
| compact_base_d16_k82_m27_29 | 16 | 82 | base | 3.959795e-19 | 8.581196e-05 | 3.612316e-05 | 0.0001219351 | 0.5223715 | — | — | — | — | — | PASS | [compact_base_d16_k82_m27_29.qasm](compact_base_d16_k82_m27_29.qasm), [metadata](compact_base_d16_k82_m27_29.json), [receipt](compact_base_d16_k82_m27_29.score.json) |
| compact_robust_d15_k82_m27_29 | 15 | 82 | robust | 4.32987e-19 | 9.004145e-05 | 2.771676e-05 | 0.0001177582 | 0.5446968 | — | — | — | — | — | PASS | [compact_robust_d15_k82_m27_29.qasm](compact_robust_d15_k82_m27_29.qasm), [metadata](compact_robust_d15_k82_m27_29.json), [receipt](compact_robust_d15_k82_m27_29.score.json) |
| flag_18_10q12_13q19_m27_29 | 15 | 84 | extra Z flags | 5.255056e-19 | 7.396202e-05 | 3.211049e-05 | 0.0001060725 | 0.5305386 | — | — | — | — | — | PASS | [flag_18_10q12_13q19_m27_29.qasm](flag_18_10q12_13q19_m27_29.qasm), [metadata](flag_18_10q12_13q19_m27_29.json), [receipt](flag_18_10q12_13q19_m27_29.score.json) |
| flag_18_10q12_14q19_m27_29 | 16 | 84 | extra Z flags | 5.439846e-19 | 7.907982e-05 | 3.66022e-05 | 0.000115682 | 0.5195932 | — | — | — | — | — | PASS | [flag_18_10q12_14q19_m27_29.qasm](flag_18_10q12_14q19_m27_29.qasm), [metadata](flag_18_10q12_14q19_m27_29.json), [receipt](flag_18_10q12_14q19_m27_29.score.json) |
| flag_18_8q12_13q19_m27_29 | 15 | 84 | extra Z flags | 5.255056e-19 | 7.396202e-05 | 3.211049e-05 | 0.0001060725 | 0.5305386 | — | — | — | — | — | PASS | [flag_18_8q12_13q19_m27_29.qasm](flag_18_8q12_13q19_m27_29.qasm), [metadata](flag_18_8q12_13q19_m27_29.json), [receipt](flag_18_8q12_13q19_m27_29.score.json) |
| flag_18_9q12_13q19_m27_29 | 15 | 84 | extra Z flags | 5.255056e-19 | 7.396202e-05 | 3.211049e-05 | 0.0001060725 | 0.5305386 | — | — | — | — | — | PASS | [flag_18_9q12_13q19_m27_29.qasm](flag_18_9q12_13q19_m27_29.qasm), [metadata](flag_18_9q12_13q19_m27_29.json), [receipt](flag_18_9q12_13q19_m27_29.score.json) |
| flag_18_9q12_14q19_m27_29 | 16 | 84 | extra Z flags | 5.439846e-19 | 7.907982e-05 | 3.66022e-05 | 0.000115682 | 0.5195932 | — | — | — | — | — | PASS | [flag_18_9q12_14q19_m27_29.qasm](flag_18_9q12_14q19_m27_29.qasm), [metadata](flag_18_9q12_14q19_m27_29.json), [receipt](flag_18_9q12_14q19_m27_29.score.json) |
| flag_24_10q25_11q25_m27_29 | 14 | 84 | extra Z flags | 5.624883e-19 | 8.249194e-05 | 3.126409e-05 | 0.000113756 | 0.5310917 | — | — | — | — | — | PASS | [flag_24_10q25_11q25_m27_29.qasm](flag_24_10q25_11q25_m27_29.qasm), [metadata](flag_24_10q25_11q25_m27_29.json), [receipt](flag_24_10q25_11q25_m27_29.score.json) |
| flag_24_10q25_12q25_m27_29 | 15 | 84 | extra Z flags | 5.440093e-19 | 8.223429e-05 | 3.420667e-05 | 0.000116441 | 0.5255175 | — | — | — | — | — | PASS | [flag_24_10q25_12q25_m27_29.qasm](flag_24_10q25_12q25_m27_29.qasm), [metadata](flag_24_10q25_12q25_m27_29.json), [receipt](flag_24_10q25_12q25_m27_29.score.json) |
| flag_24_10q25_13q25_m27_29 | 15 | 84 | extra Z flags | 5.440093e-19 | 8.23254e-05 | 3.431541e-05 | 0.0001166408 | 0.5253381 | — | — | — | — | — | PASS | [flag_24_10q25_13q25_m27_29.qasm](flag_24_10q25_13q25_m27_29.qasm), [metadata](flag_24_10q25_13q25_m27_29.json), [receipt](flag_24_10q25_13q25_m27_29.score.json) |
| flag_24_11q25_13q25_m27_29 | 15 | 84 | extra Z flags | 5.440093e-19 | 8.25926e-05 | 3.421744e-05 | 0.00011681 | 0.5258616 | — | — | — | — | — | PASS | [flag_24_11q25_13q25_m27_29.qasm](flag_24_11q25_13q25_m27_29.qasm), [metadata](flag_24_11q25_13q25_m27_29.json), [receipt](flag_24_11q25_13q25_m27_29.score.json) |
| flag_24_5q25_7q25_m27_29 | 14 | 84 | extra Z flags | 5.440093e-19 | 7.844304e-05 | 3.072176e-05 | 0.0001091648 | 0.5300337 | — | — | — | — | — | PASS | [flag_24_5q25_7q25_m27_29.qasm](flag_24_5q25_7q25_m27_29.qasm), [metadata](flag_24_5q25_7q25_m27_29.json), [receipt](flag_24_5q25_7q25_m27_29.score.json) |
| flag_32_4q26_12q26_m27_29 | 14 | 84 | extra Z flags | 5.440093e-19 | 7.924162e-05 | 2.991987e-05 | 0.0001091615 | 0.5355391 | — | — | — | — | — | PASS | [flag_32_4q26_12q26_m27_29.qasm](flag_32_4q26_12q26_m27_29.qasm), [metadata](flag_32_4q26_12q26_m27_29.json), [receipt](flag_32_4q26_12q26_m27_29.score.json) |
| flag_32_4q26_13q26_m27_29 | 14 | 84 | extra Z flags | 5.440093e-19 | 7.924162e-05 | 2.991987e-05 | 0.0001091615 | 0.5355391 | — | — | — | — | — | PASS | [flag_32_4q26_13q26_m27_29.qasm](flag_32_4q26_13q26_m27_29.qasm), [metadata](flag_32_4q26_13q26_m27_29.json), [receipt](flag_32_4q26_13q26_m27_29.score.json) |
| flag_32_4q26_14q26_m27_29 | 16 | 84 | extra Z flags | 5.440093e-19 | 8.468253e-05 | 3.821212e-05 | 0.0001228947 | 0.5136711 | — | — | — | — | — | PASS | [flag_32_4q26_14q26_m27_29.qasm](flag_32_4q26_14q26_m27_29.qasm), [metadata](flag_32_4q26_14q26_m27_29.json), [receipt](flag_32_4q26_14q26_m27_29.score.json) |
| flag_32_5q26_13q26_m27_29 | 14 | 84 | extra Z flags | 5.070018e-19 | 7.699068e-05 | 3.03721e-05 | 0.0001073628 | 0.5341093 | — | — | — | — | — | PASS | [flag_32_5q26_13q26_m27_29.qasm](flag_32_5q26_13q26_m27_29.qasm), [metadata](flag_32_5q26_13q26_m27_29.json), [receipt](flag_32_5q26_13q26_m27_29.score.json) |
| flag_32_5q26_14q26_m27_29 | 16 | 84 | extra Z flags | 5.070018e-19 | 8.249836e-05 | 3.872e-05 | 0.0001212184 | 0.5122984 | — | — | — | — | — | PASS | [flag_32_5q26_14q26_m27_29.qasm](flag_32_5q26_14q26_m27_29.qasm), [metadata](flag_32_5q26_14q26_m27_29.json), [receipt](flag_32_5q26_14q26_m27_29.score.json) |
| flag_33_12q27_13q27_m27_29 | 16 | 84 | extra Z flags | 5.107026e-19 | 7.80686e-05 | 3.633808e-05 | 0.0001144067 | 0.5214399 | — | — | — | — | — | PASS | [flag_33_12q27_13q27_m27_29.qasm](flag_33_12q27_13q27_m27_29.qasm), [metadata](flag_33_12q27_13q27_m27_29.json), [receipt](flag_33_12q27_13q27_m27_29.score.json) |
| flag_33_7q27_8q27_m27_29 | 14 | 84 | extra Z flags | 5.070018e-19 | 7.633964e-05 | 3.098795e-05 | 0.0001073276 | 0.5293279 | — | — | — | — | — | PASS | [flag_33_7q27_8q27_m27_29.qasm](flag_33_7q27_8q27_m27_29.qasm), [metadata](flag_33_7q27_8q27_m27_29.json), [receipt](flag_33_7q27_8q27_m27_29.score.json) |
| flag_33_7q27_9q27_m27_29 | 14 | 84 | extra Z flags | 5.107026e-19 | 7.671326e-05 | 3.101704e-05 | 0.0001077303 | 0.5291842 | — | — | — | — | — | PASS | [flag_33_7q27_9q27_m27_29.qasm](flag_33_7q27_9q27_m27_29.qasm), [metadata](flag_33_7q27_9q27_m27_29.json), [receipt](flag_33_7q27_9q27_m27_29.score.json) |
| flag_33_8q27_9q27_m27_29 | 14 | 84 | extra Z flags | 5.292063e-19 | 7.91481e-05 | 3.097937e-05 | 0.0001101275 | 0.5300664 | — | — | — | — | — | PASS | [flag_33_8q27_9q27_m27_29.qasm](flag_33_8q27_9q27_m27_29.qasm), [metadata](flag_33_8q27_9q27_m27_29.json), [receipt](flag_33_8q27_9q27_m27_29.score.json) |
| flag_34_3q28_13q28_m27_29 | 15 | 84 | extra Z flags | 4.699944e-19 | 7.226564e-05 | 3.316722e-05 | 0.0001054329 | 0.523969 | — | — | — | — | — | PASS | [flag_34_3q28_13q28_m27_29.qasm](flag_34_3q28_13q28_m27_29.qasm), [metadata](flag_34_3q28_13q28_m27_29.json), [receipt](flag_34_3q28_13q28_m27_29.score.json) |
| flag_34_4q28_13q28_m27_29 | 15 | 84 | extra Z flags | 4.699944e-19 | 7.18331e-05 | 3.317305e-05 | 0.0001050061 | 0.5239628 | — | — | — | — | — | PASS | [flag_34_4q28_13q28_m27_29.qasm](flag_34_4q28_13q28_m27_29.qasm), [metadata](flag_34_4q28_13q28_m27_29.json), [receipt](flag_34_4q28_13q28_m27_29.score.json) |
| flag_34_6q28_7q28_m27_29 | 14 | 84 | extra Z flags | 5.439846e-19 | 8.324573e-05 | 3.129235e-05 | 0.0001145381 | 0.5305579 | — | — | — | — | — | PASS | [flag_34_6q28_7q28_m27_29.qasm](flag_34_6q28_7q28_m27_29.qasm), [metadata](flag_34_6q28_7q28_m27_29.json), [receipt](flag_34_6q28_7q28_m27_29.score.json) |
| window_base_0_k78_m27_29 | 14 | 78 | base local SAT | 5.218048e-19 | 8.50864e-05 | 2.465291e-05 | 0.0001097393 | 0.5563972 | — | — | — | — | — | PASS | [window_base_0_k78_m27_29.qasm](window_base_0_k78_m27_29.qasm), [metadata](window_base_0_k78_m27_29.json), [receipt](window_base_0_k78_m27_29.score.json) |
| window_base_0_k82_m27_29 | 14 | 81 | base local SAT | 5.736152e-19 | 0.0001018229 | 2.608213e-05 | 0.000127905 | 0.5532215 | — | — | — | — | — | PASS | [window_base_0_k82_m27_29.qasm](window_base_0_k82_m27_29.qasm), [metadata](window_base_0_k82_m27_29.json), [receipt](window_base_0_k82_m27_29.score.json) |
| window_base_3_k78_m27_29 | 14 | 78 | base local SAT | 5.77316e-19 | 9.937396e-05 | 2.996223e-05 | 0.0001293362 | 0.5443542 | — | — | — | — | — | PASS | [window_base_3_k78_m27_29.qasm](window_base_3_k78_m27_29.qasm), [metadata](window_base_3_k78_m27_29.json), [receipt](window_base_3_k78_m27_29.score.json) |
| window_base_3_k82_m27_29 | 14 | 82 | base local SAT | 5.070018e-19 | 9.195527e-05 | 2.637599e-05 | 0.0001183313 | 0.5497096 | — | — | — | — | — | PASS | [window_base_3_k82_m27_29.qasm](window_base_3_k82_m27_29.qasm), [metadata](window_base_3_k82_m27_29.json), [receipt](window_base_3_k82_m27_29.score.json) |

## Loss attribution

The winning B-clean prep with q25/q27/q28/q29 measured at first use has full exact total 8.4428245e-5 and B+C-noiseless total 6.1564636e-5. Its B+C contribution is therefore **2.2863609e-5 versus 4.0329527e-5 for v14_bcm, down 43.3%**. This beats the MC benchmark, but does not remove most of the entire B+C contribution. The largest targeted interaction, prep×round, falls from 1.837e-5 to 3.029e-6 (83.5%); prep×prep is 8.719e-6 and A×prep is 3.004e-6. See `compact_clean_d14_k100_m25_28_pairs.log` and `compact_clean_d14_k100_m27_29_m25_28.no_prep.json`.

For `compact_base_d13_k82_m27_29` versus v14_bcm, exact B+C-noiseless totals are 5.5654224e-5 versus 6.1564636e-5. Subtracting those from their full totals gives B+C-attributable losses 3.1616024e-5 versus 4.0329527e-5: a 21.6% reduction, not removal of most of the share. The prep×round second-order term falls from 1.837e-5 to 1.059e-5; prep×prep rises from 7.047e-6 to 1.090e-5; A×prep falls from 4.271e-6 to 2.991e-6. Receipts: `compact_base_d13_k82_pairs.log`, `v14_pairs_reference.txt`, and `*.no_prep.json`.

## Solver receipts

All global jobs use depths 13–16 and CX caps 82 and 100. The original and primed batches use helper cells `[18,24,30,31,32,33,34,35]`. Compact and combined batches use no helpers and fix the six pivot cells to the baseline set. A timeout is not an infeasibility proof. Window jobs freeze all layers outside the named five-layer window of the baseline. Primed jobs add violations from the baseline before the first solve and explicitly encode target-basis invertibility.

| Run | Rule | Depth | CX cap | Status | Seconds | CEGAR constraints | Receipt |
|---|---|---:|---:|---|---:|---:|---|
| clean_d13_k100 | clean | 13 | 100 | TIMEOUT | 240.5347 | 0 | [clean_d13_k100.receipt.json](clean_d13_k100.receipt.json) |
| clean_d13_k82 | clean | 13 | 82 | TIMEOUT | 240.5212 | 0 | [clean_d13_k82.receipt.json](clean_d13_k82.receipt.json) |
| clean_d14_k100 | clean | 14 | 100 | TIMEOUT | 240.5859 | 0 | [clean_d14_k100.receipt.json](clean_d14_k100.receipt.json) |
| clean_d14_k82 | clean | 14 | 82 | TIMEOUT | 241.074 | 0 | [clean_d14_k82.receipt.json](clean_d14_k82.receipt.json) |
| clean_d15_k100 | clean | 15 | 100 | TIMEOUT | 240.6599 | 0 | [clean_d15_k100.receipt.json](clean_d15_k100.receipt.json) |
| clean_d15_k82 | clean | 15 | 82 | TIMEOUT | 240.6342 | 0 | [clean_d15_k82.receipt.json](clean_d15_k82.receipt.json) |
| clean_d16_k100 | clean | 16 | 100 | TIMEOUT | 240.8054 | 0 | [clean_d16_k100.receipt.json](clean_d16_k100.receipt.json) |
| clean_d16_k82 | clean | 16 | 82 | TIMEOUT | 240.6436 | 0 | [clean_d16_k82.receipt.json](clean_d16_k82.receipt.json) |
| clean_literal_d13_k100 | clean_literal | 13 | 100 | TIMEOUT | 240.5129 | 0 | [clean_literal_d13_k100.receipt.json](clean_literal_d13_k100.receipt.json) |
| clean_literal_d13_k82 | clean_literal | 13 | 82 | TIMEOUT | 240.6016 | 0 | [clean_literal_d13_k82.receipt.json](clean_literal_d13_k82.receipt.json) |
| clean_literal_d14_k100 | clean_literal | 14 | 100 | TIMEOUT | 240.6061 | 0 | [clean_literal_d14_k100.receipt.json](clean_literal_d14_k100.receipt.json) |
| clean_literal_d14_k82 | clean_literal | 14 | 82 | TIMEOUT | 240.4965 | 0 | [clean_literal_d14_k82.receipt.json](clean_literal_d14_k82.receipt.json) |
| clean_literal_d15_k100 | clean_literal | 15 | 100 | TIMEOUT | 241.2489 | 0 | [clean_literal_d15_k100.receipt.json](clean_literal_d15_k100.receipt.json) |
| clean_literal_d15_k82 | clean_literal | 15 | 82 | TIMEOUT | 240.601 | 0 | [clean_literal_d15_k82.receipt.json](clean_literal_d15_k82.receipt.json) |
| clean_literal_d16_k100 | clean_literal | 16 | 100 | TIMEOUT | 240.5334 | 0 | [clean_literal_d16_k100.receipt.json](clean_literal_d16_k100.receipt.json) |
| clean_literal_d16_k82 | clean_literal | 16 | 82 | TIMEOUT | 240.4813 | 0 | [clean_literal_d16_k82.receipt.json](clean_literal_d16_k82.receipt.json) |
| combined_allpairs_d13_k100 | allpairs | 13 | 100 | TIMEOUT | 240.6709 | 224 | [combined_allpairs_d13_k100.receipt.json](combined_allpairs_d13_k100.receipt.json) |
| combined_allpairs_d13_k82 | allpairs | 13 | 82 | TIMEOUT | 240.4663 | 224 | [combined_allpairs_d13_k82.receipt.json](combined_allpairs_d13_k82.receipt.json) |
| combined_allpairs_d14_k100 | allpairs | 14 | 100 | TIMEOUT | 240.3637 | 224 | [combined_allpairs_d14_k100.receipt.json](combined_allpairs_d14_k100.receipt.json) |
| combined_allpairs_d14_k82 | allpairs | 14 | 82 | TIMEOUT | 241.7857 | 224 | [combined_allpairs_d14_k82.receipt.json](combined_allpairs_d14_k82.receipt.json) |
| combined_allpairs_d15_k100 | allpairs | 15 | 100 | TIMEOUT | 240.5365 | 224 | [combined_allpairs_d15_k100.receipt.json](combined_allpairs_d15_k100.receipt.json) |
| combined_allpairs_d15_k82 | allpairs | 15 | 82 | TIMEOUT | 241.4103 | 352 | [combined_allpairs_d15_k82.receipt.json](combined_allpairs_d15_k82.receipt.json) |
| combined_allpairs_d16_k100 | allpairs | 16 | 100 | TIMEOUT | 240.3524 | 224 | [combined_allpairs_d16_k100.receipt.json](combined_allpairs_d16_k100.receipt.json) |
| combined_allpairs_d16_k82 | allpairs | 16 | 82 | TIMEOUT | 240.2262 | 224 | [combined_allpairs_d16_k82.receipt.json](combined_allpairs_d16_k82.receipt.json) |
| combined_both_d13_k100 | both | 13 | 100 | TIMEOUT | 240.7444 | 81 | [combined_both_d13_k100.receipt.json](combined_both_d13_k100.receipt.json) |
| combined_both_d13_k82 | both | 13 | 82 | TIMEOUT | 240.5846 | 81 | [combined_both_d13_k82.receipt.json](combined_both_d13_k82.receipt.json) |
| combined_both_d14_k100 | both | 14 | 100 | TIMEOUT | 240.2738 | 137 | [combined_both_d14_k100.receipt.json](combined_both_d14_k100.receipt.json) |
| combined_both_d14_k82 | both | 14 | 82 | TIMEOUT | 240.1651 | 112 | [combined_both_d14_k82.receipt.json](combined_both_d14_k82.receipt.json) |
| combined_both_d15_k100 | both | 15 | 100 | TIMEOUT | 240.3844 | 136 | [combined_both_d15_k100.receipt.json](combined_both_d15_k100.receipt.json) |
| combined_both_d15_k82 | both | 15 | 82 | TIMEOUT | 240.3622 | 147 | [combined_both_d15_k82.receipt.json](combined_both_d15_k82.receipt.json) |
| combined_both_d16_k100 | both | 16 | 100 | TIMEOUT | 240.391 | 116 | [combined_both_d16_k100.receipt.json](combined_both_d16_k100.receipt.json) |
| combined_both_d16_k82 | both | 16 | 82 | TIMEOUT | 240.1236 | 155 | [combined_both_d16_k82.receipt.json](combined_both_d16_k82.receipt.json) |
| compact_base_d13_k100 | base | 13 | 100 | TIMEOUT | 240.2295 | 74 | [compact_base_d13_k100.receipt.json](compact_base_d13_k100.receipt.json) |
| compact_base_d13_k82 | base | 13 | 82 | SAT | 26.65906 | 84 | [compact_base_d13_k82.receipt.json](compact_base_d13_k82.receipt.json) |
| compact_base_d14_k100 | base | 14 | 100 | SAT | 42.59962 | 63 | [compact_base_d14_k100.receipt.json](compact_base_d14_k100.receipt.json) |
| compact_base_d14_k82 | base | 14 | 82 | SAT | 38.86673 | 35 | [compact_base_d14_k82.receipt.json](compact_base_d14_k82.receipt.json) |
| compact_base_d15_k100 | base | 15 | 100 | SAT | 30.68923 | 66 | [compact_base_d15_k100.receipt.json](compact_base_d15_k100.receipt.json) |
| compact_base_d15_k82 | base | 15 | 82 | TIMEOUT | 242.3012 | 61 | [compact_base_d15_k82.receipt.json](compact_base_d15_k82.receipt.json) |
| compact_base_d16_k100 | base | 16 | 100 | SAT | 144.5701 | 67 | [compact_base_d16_k100.receipt.json](compact_base_d16_k100.receipt.json) |
| compact_base_d16_k82 | base | 16 | 82 | SAT | 223.6842 | 57 | [compact_base_d16_k82.receipt.json](compact_base_d16_k82.receipt.json) |
| compact_clean_d13_k100 | clean | 13 | 100 | UNSAT | 166.0212 | 113 | [compact_clean_d13_k100.receipt.json](compact_clean_d13_k100.receipt.json) |
| compact_clean_d13_k82 | clean | 13 | 82 | UNSAT | 206.201 | 151 | [compact_clean_d13_k82.receipt.json](compact_clean_d13_k82.receipt.json) |
| compact_clean_d14_k100 | clean | 14 | 100 | SAT | 211.2247 | 178 | [compact_clean_d14_k100.receipt.json](compact_clean_d14_k100.receipt.json) |
| compact_clean_d14_k82 | clean | 14 | 82 | TIMEOUT | 240.4326 | 136 | [compact_clean_d14_k82.receipt.json](compact_clean_d14_k82.receipt.json) |
| compact_clean_d15_k100 | clean | 15 | 100 | SAT | 87.26242 | 168 | [compact_clean_d15_k100.receipt.json](compact_clean_d15_k100.receipt.json) |
| compact_clean_d15_k82 | clean | 15 | 82 | SAT | 51.83412 | 122 | [compact_clean_d15_k82.receipt.json](compact_clean_d15_k82.receipt.json) |
| compact_clean_d16_k100 | clean | 16 | 100 | SAT | 156.8714 | 203 | [compact_clean_d16_k100.receipt.json](compact_clean_d16_k100.receipt.json) |
| compact_clean_d16_k82 | clean | 16 | 82 | TIMEOUT | 241.994 | 160 | [compact_clean_d16_k82.receipt.json](compact_clean_d16_k82.receipt.json) |
| compact_pairs_d13_k100 | pairs | 13 | 100 | TIMEOUT | 240.2208 | 224 | [compact_pairs_d13_k100.receipt.json](compact_pairs_d13_k100.receipt.json) |
| compact_pairs_d13_k82 | pairs | 13 | 82 | TIMEOUT | 240.3727 | 224 | [compact_pairs_d13_k82.receipt.json](compact_pairs_d13_k82.receipt.json) |
| compact_pairs_d14_k100 | pairs | 14 | 100 | TIMEOUT | 240.6848 | 352 | [compact_pairs_d14_k100.receipt.json](compact_pairs_d14_k100.receipt.json) |
| compact_pairs_d14_k82 | pairs | 14 | 82 | TIMEOUT | 240.4983 | 224 | [compact_pairs_d14_k82.receipt.json](compact_pairs_d14_k82.receipt.json) |
| compact_pairs_d15_k100 | pairs | 15 | 100 | TIMEOUT | 243.0094 | 480 | [compact_pairs_d15_k100.receipt.json](compact_pairs_d15_k100.receipt.json) |
| compact_pairs_d15_k82 | pairs | 15 | 82 | TIMEOUT | 242.9751 | 224 | [compact_pairs_d15_k82.receipt.json](compact_pairs_d15_k82.receipt.json) |
| compact_pairs_d16_k100 | pairs | 16 | 100 | TIMEOUT | 243.3144 | 224 | [compact_pairs_d16_k100.receipt.json](compact_pairs_d16_k100.receipt.json) |
| compact_pairs_d16_k82 | pairs | 16 | 82 | TIMEOUT | 243.946 | 352 | [compact_pairs_d16_k82.receipt.json](compact_pairs_d16_k82.receipt.json) |
| compact_robust_d13_k100 | robust | 13 | 100 | TIMEOUT | 240.1946 | 92 | [compact_robust_d13_k100.receipt.json](compact_robust_d13_k100.receipt.json) |
| compact_robust_d13_k82 | robust | 13 | 82 | TIMEOUT | 240.1002 | 103 | [compact_robust_d13_k82.receipt.json](compact_robust_d13_k82.receipt.json) |
| compact_robust_d14_k100 | robust | 14 | 100 | TIMEOUT | 240.5471 | 121 | [compact_robust_d14_k100.receipt.json](compact_robust_d14_k100.receipt.json) |
| compact_robust_d14_k82 | robust | 14 | 82 | TIMEOUT | 240.0615 | 142 | [compact_robust_d14_k82.receipt.json](compact_robust_d14_k82.receipt.json) |
| compact_robust_d15_k100 | robust | 15 | 100 | TIMEOUT | 242.0555 | 113 | [compact_robust_d15_k100.receipt.json](compact_robust_d15_k100.receipt.json) |
| compact_robust_d15_k82 | robust | 15 | 82 | SAT | 65.29413 | 122 | [compact_robust_d15_k82.receipt.json](compact_robust_d15_k82.receipt.json) |
| compact_robust_d16_k100 | robust | 16 | 100 | TIMEOUT | 242.0314 | 124 | [compact_robust_d16_k100.receipt.json](compact_robust_d16_k100.receipt.json) |
| compact_robust_d16_k82 | robust | 16 | 82 | TIMEOUT | 243.9157 | 122 | [compact_robust_d16_k82.receipt.json](compact_robust_d16_k82.receipt.json) |
| pairs_d13_k100 | pairs | 13 | 100 | TIMEOUT | 240.7209 | 0 | [pairs_d13_k100.receipt.json](pairs_d13_k100.receipt.json) |
| pairs_d13_k82 | pairs | 13 | 82 | TIMEOUT | 240.8197 | 0 | [pairs_d13_k82.receipt.json](pairs_d13_k82.receipt.json) |
| pairs_d14_k100 | pairs | 14 | 100 | TIMEOUT | 240.7752 | 0 | [pairs_d14_k100.receipt.json](pairs_d14_k100.receipt.json) |
| pairs_d14_k82 | pairs | 14 | 82 | TIMEOUT | 240.6308 | 0 | [pairs_d14_k82.receipt.json](pairs_d14_k82.receipt.json) |
| pairs_d15_k100 | pairs | 15 | 100 | TIMEOUT | 240.8378 | 0 | [pairs_d15_k100.receipt.json](pairs_d15_k100.receipt.json) |
| pairs_d15_k82 | pairs | 15 | 82 | TIMEOUT | 240.6445 | 0 | [pairs_d15_k82.receipt.json](pairs_d15_k82.receipt.json) |
| pairs_d16_k100 | pairs | 16 | 100 | TIMEOUT | 240.8498 | 0 | [pairs_d16_k100.receipt.json](pairs_d16_k100.receipt.json) |
| pairs_d16_k82 | pairs | 16 | 82 | TIMEOUT | 240.6369 | 0 | [pairs_d16_k82.receipt.json](pairs_d16_k82.receipt.json) |
| primed_clean_d13_k100 | clean | 13 | 100 | TIMEOUT | 240.6696 | 56 | [primed_clean_d13_k100.receipt.json](primed_clean_d13_k100.receipt.json) |
| primed_clean_d13_k82 | clean | 13 | 82 | TIMEOUT | 240.6007 | 56 | [primed_clean_d13_k82.receipt.json](primed_clean_d13_k82.receipt.json) |
| primed_clean_d14_k100 | clean | 14 | 100 | TIMEOUT | 240.6101 | 34 | [primed_clean_d14_k100.receipt.json](primed_clean_d14_k100.receipt.json) |
| primed_clean_d14_k82 | clean | 14 | 82 | TIMEOUT | 240.6722 | 34 | [primed_clean_d14_k82.receipt.json](primed_clean_d14_k82.receipt.json) |
| primed_clean_d15_k100 | clean | 15 | 100 | TIMEOUT | 240.7535 | 34 | [primed_clean_d15_k100.receipt.json](primed_clean_d15_k100.receipt.json) |
| primed_clean_d15_k82 | clean | 15 | 82 | TIMEOUT | 240.6749 | 34 | [primed_clean_d15_k82.receipt.json](primed_clean_d15_k82.receipt.json) |
| primed_clean_d16_k100 | clean | 16 | 100 | TIMEOUT | 240.8051 | 34 | [primed_clean_d16_k100.receipt.json](primed_clean_d16_k100.receipt.json) |
| primed_clean_d16_k82 | clean | 16 | 82 | TIMEOUT | 240.7196 | 34 | [primed_clean_d16_k82.receipt.json](primed_clean_d16_k82.receipt.json) |
| primed_pairs_d13_k100 | pairs | 13 | 100 | TIMEOUT | 240.5322 | 96 | [primed_pairs_d13_k100.receipt.json](primed_pairs_d13_k100.receipt.json) |
| primed_pairs_d13_k82 | pairs | 13 | 82 | TIMEOUT | 240.9754 | 96 | [primed_pairs_d13_k82.receipt.json](primed_pairs_d13_k82.receipt.json) |
| primed_pairs_d14_k100 | pairs | 14 | 100 | TIMEOUT | 240.6739 | 96 | [primed_pairs_d14_k100.receipt.json](primed_pairs_d14_k100.receipt.json) |
| primed_pairs_d14_k82 | pairs | 14 | 82 | TIMEOUT | 240.5803 | 96 | [primed_pairs_d14_k82.receipt.json](primed_pairs_d14_k82.receipt.json) |
| primed_pairs_d15_k100 | pairs | 15 | 100 | TIMEOUT | 240.6005 | 96 | [primed_pairs_d15_k100.receipt.json](primed_pairs_d15_k100.receipt.json) |
| primed_pairs_d15_k82 | pairs | 15 | 82 | TIMEOUT | 240.6009 | 96 | [primed_pairs_d15_k82.receipt.json](primed_pairs_d15_k82.receipt.json) |
| primed_pairs_d16_k100 | pairs | 16 | 100 | TIMEOUT | 240.6278 | 96 | [primed_pairs_d16_k100.receipt.json](primed_pairs_d16_k100.receipt.json) |
| primed_pairs_d16_k82 | pairs | 16 | 82 | TIMEOUT | 240.5164 | 96 | [primed_pairs_d16_k82.receipt.json](primed_pairs_d16_k82.receipt.json) |
| primed_robust_d13_k100 | robust | 13 | 100 | TIMEOUT | 240.6286 | 39 | [primed_robust_d13_k100.receipt.json](primed_robust_d13_k100.receipt.json) |
| primed_robust_d13_k82 | robust | 13 | 82 | TIMEOUT | 240.8975 | 39 | [primed_robust_d13_k82.receipt.json](primed_robust_d13_k82.receipt.json) |
| primed_robust_d14_k100 | robust | 14 | 100 | TIMEOUT | 240.8413 | 23 | [primed_robust_d14_k100.receipt.json](primed_robust_d14_k100.receipt.json) |
| primed_robust_d14_k82 | robust | 14 | 82 | TIMEOUT | 240.6972 | 23 | [primed_robust_d14_k82.receipt.json](primed_robust_d14_k82.receipt.json) |
| primed_robust_d15_k100 | robust | 15 | 100 | TIMEOUT | 240.8923 | 23 | [primed_robust_d15_k100.receipt.json](primed_robust_d15_k100.receipt.json) |
| primed_robust_d15_k82 | robust | 15 | 82 | TIMEOUT | 240.6811 | 23 | [primed_robust_d15_k82.receipt.json](primed_robust_d15_k82.receipt.json) |
| primed_robust_d16_k100 | robust | 16 | 100 | TIMEOUT | 240.6981 | 23 | [primed_robust_d16_k100.receipt.json](primed_robust_d16_k100.receipt.json) |
| primed_robust_d16_k82 | robust | 16 | 82 | TIMEOUT | 240.6617 | 23 | [primed_robust_d16_k82.receipt.json](primed_robust_d16_k82.receipt.json) |
| proof_independent_d13_k100 | independent | 13 | 100 | UNSAT | 0.1370632 | — | [proof_independent_d13_k100.receipt.json](proof_independent_d13_k100.receipt.json) |
| proof_independent_d13_k82 | independent | 13 | 82 | UNSAT | 0.1151568 | — | [proof_independent_d13_k82.receipt.json](proof_independent_d13_k82.receipt.json) |
| proof_independent_d14_k100 | independent | 14 | 100 | UNSAT | 0.1546814 | — | [proof_independent_d14_k100.receipt.json](proof_independent_d14_k100.receipt.json) |
| proof_independent_d14_k82 | independent | 14 | 82 | UNSAT | 0.1372241 | — | [proof_independent_d14_k82.receipt.json](proof_independent_d14_k82.receipt.json) |
| proof_independent_d15_k100 | independent | 15 | 100 | UNSAT | 0.1549135 | — | [proof_independent_d15_k100.receipt.json](proof_independent_d15_k100.receipt.json) |
| proof_independent_d15_k82 | independent | 15 | 82 | UNSAT | 0.1346017 | — | [proof_independent_d15_k82.receipt.json](proof_independent_d15_k82.receipt.json) |
| proof_independent_d16_k100 | independent | 16 | 100 | UNSAT | 0.2324267 | — | [proof_independent_d16_k100.receipt.json](proof_independent_d16_k100.receipt.json) |
| proof_independent_d16_k82 | independent | 16 | 82 | UNSAT | 0.2080131 | — | [proof_independent_d16_k82.receipt.json](proof_independent_d16_k82.receipt.json) |
| proof_literal_initial_d13_k100 | literal_initial | 13 | 100 | UNSAT | 0.000223704 | — | [proof_literal_initial_d13_k100.receipt.json](proof_literal_initial_d13_k100.receipt.json) |
| proof_literal_initial_d13_k82 | literal_initial | 13 | 82 | UNSAT | 0.0003284 | — | [proof_literal_initial_d13_k82.receipt.json](proof_literal_initial_d13_k82.receipt.json) |
| proof_literal_initial_d14_k100 | literal_initial | 14 | 100 | UNSAT | 0.000209285 | — | [proof_literal_initial_d14_k100.receipt.json](proof_literal_initial_d14_k100.receipt.json) |
| proof_literal_initial_d14_k82 | literal_initial | 14 | 82 | UNSAT | 0.0002134 | — | [proof_literal_initial_d14_k82.receipt.json](proof_literal_initial_d14_k82.receipt.json) |
| proof_literal_initial_d15_k100 | literal_initial | 15 | 100 | UNSAT | 0.000198211 | — | [proof_literal_initial_d15_k100.receipt.json](proof_literal_initial_d15_k100.receipt.json) |
| proof_literal_initial_d15_k82 | literal_initial | 15 | 82 | UNSAT | 0.000202809 | — | [proof_literal_initial_d15_k82.receipt.json](proof_literal_initial_d15_k82.receipt.json) |
| proof_literal_initial_d16_k100 | literal_initial | 16 | 100 | UNSAT | 0.000197254 | — | [proof_literal_initial_d16_k100.receipt.json](proof_literal_initial_d16_k100.receipt.json) |
| proof_literal_initial_d16_k82 | literal_initial | 16 | 82 | UNSAT | 0.000198047 | — | [proof_literal_initial_d16_k82.receipt.json](proof_literal_initial_d16_k82.receipt.json) |
| robust_d13_k100 | robust | 13 | 100 | TIMEOUT | 241.421 | 0 | [robust_d13_k100.receipt.json](robust_d13_k100.receipt.json) |
| robust_d13_k82 | robust | 13 | 82 | TIMEOUT | 240.7305 | 0 | [robust_d13_k82.receipt.json](robust_d13_k82.receipt.json) |
| robust_d14_k100 | robust | 14 | 100 | TIMEOUT | 240.8369 | 0 | [robust_d14_k100.receipt.json](robust_d14_k100.receipt.json) |
| robust_d14_k82 | robust | 14 | 82 | TIMEOUT | 240.6286 | 0 | [robust_d14_k82.receipt.json](robust_d14_k82.receipt.json) |
| robust_d15_k100 | robust | 15 | 100 | TIMEOUT | 240.6547 | 0 | [robust_d15_k100.receipt.json](robust_d15_k100.receipt.json) |
| robust_d15_k82 | robust | 15 | 82 | TIMEOUT | 240.6299 | 0 | [robust_d15_k82.receipt.json](robust_d15_k82.receipt.json) |
| robust_d16_k100 | robust | 16 | 100 | TIMEOUT | 240.6281 | 0 | [robust_d16_k100.receipt.json](robust_d16_k100.receipt.json) |
| robust_d16_k82 | robust | 16 | 82 | TIMEOUT | 240.6631 | 0 | [robust_d16_k82.receipt.json](robust_d16_k82.receipt.json) |
| window_base_0_k78 | base | 14 | 78 | SAT | 6.454359 | 0 | [window_base_0_k78.receipt.json](window_base_0_k78.receipt.json) |
| window_base_0_k82 | base | 14 | 82 | SAT | 4.5362 | 0 | [window_base_0_k82.receipt.json](window_base_0_k82.receipt.json) |
| window_base_3_k78 | base | 14 | 78 | SAT | 5.444934 | 0 | [window_base_3_k78.receipt.json](window_base_3_k78.receipt.json) |
| window_base_3_k82 | base | 14 | 82 | SAT | 2.583229 | 0 | [window_base_3_k82.receipt.json](window_base_3_k82.receipt.json) |
| window_base_6_k78 | base | 14 | 78 | UNSAT | 75.25438 | 0 | [window_base_6_k78.receipt.json](window_base_6_k78.receipt.json) |
| window_base_6_k82 | base | 14 | 82 | SAT | 25.72438 | 0 | [window_base_6_k82.receipt.json](window_base_6_k82.receipt.json) |
| window_base_9_k78 | base | 14 | 78 | TIMEOUT | 150.2181 | 0 | [window_base_9_k78.receipt.json](window_base_9_k78.receipt.json) |
| window_base_9_k82 | base | 14 | 82 | TIMEOUT | 150.2349 | 0 | [window_base_9_k82.receipt.json](window_base_9_k82.receipt.json) |
| window_clean_0_k78 | clean | 14 | 78 | UNSAT | 0.1535078 | 34 | [window_clean_0_k78.receipt.json](window_clean_0_k78.receipt.json) |
| window_clean_0_k82 | clean | 14 | 82 | UNSAT | 0.1685792 | 34 | [window_clean_0_k82.receipt.json](window_clean_0_k82.receipt.json) |
| window_clean_3_k78 | clean | 14 | 78 | UNSAT | 0.1728932 | 34 | [window_clean_3_k78.receipt.json](window_clean_3_k78.receipt.json) |
| window_clean_3_k82 | clean | 14 | 82 | UNSAT | 0.2000609 | 34 | [window_clean_3_k82.receipt.json](window_clean_3_k82.receipt.json) |
| window_clean_6_k78 | clean | 14 | 78 | UNSAT | 0.1746576 | 34 | [window_clean_6_k78.receipt.json](window_clean_6_k78.receipt.json) |
| window_clean_6_k82 | clean | 14 | 82 | UNSAT | 0.1316222 | 34 | [window_clean_6_k82.receipt.json](window_clean_6_k82.receipt.json) |
| window_clean_9_k78 | clean | 14 | 78 | TIMEOUT | 150.3043 | 34 | [window_clean_9_k78.receipt.json](window_clean_9_k78.receipt.json) |
| window_clean_9_k82 | clean | 14 | 82 | TIMEOUT | 150.2759 | 34 | [window_clean_9_k82.receipt.json](window_clean_9_k82.receipt.json) |
| window_robust_0_k78 | robust | 14 | 78 | UNSAT | 0.1803575 | 23 | [window_robust_0_k78.receipt.json](window_robust_0_k78.receipt.json) |
| window_robust_0_k82 | robust | 14 | 82 | UNSAT | 0.1643216 | 23 | [window_robust_0_k82.receipt.json](window_robust_0_k82.receipt.json) |
| window_robust_3_k78 | robust | 14 | 78 | UNSAT | 0.157238 | 23 | [window_robust_3_k78.receipt.json](window_robust_3_k78.receipt.json) |
| window_robust_3_k82 | robust | 14 | 82 | UNSAT | 0.1865752 | 23 | [window_robust_3_k82.receipt.json](window_robust_3_k82.receipt.json) |
| window_robust_6_k78 | robust | 14 | 78 | UNSAT | 0.1736821 | 23 | [window_robust_6_k78.receipt.json](window_robust_6_k78.receipt.json) |
| window_robust_6_k82 | robust | 14 | 82 | UNSAT | 0.1427938 | 23 | [window_robust_6_k82.receipt.json](window_robust_6_k82.receipt.json) |
| window_robust_9_k78 | robust | 14 | 78 | TIMEOUT | 150.2913 | 23 | [window_robust_9_k78.receipt.json](window_robust_9_k78.receipt.json) |
| window_robust_9_k82 | robust | 14 | 82 | TIMEOUT | 150.2958 | 23 | [window_robust_9_k82.receipt.json](window_robust_9_k82.receipt.json) |

## Interpretation and reproducibility

- `sat6.py` and `ft.py` are lane-local modifications of ST_BC. They include single-X faults at every layer boundary and correlated XX errors after selected CX gates. XX is one physical prep fault, not a pair.
- `clean_literal` forbids any nonempty B X support. `clean` forbids a nontrivial B X class modulo the X stabilizers. `robust` forbids dangerous B X classes with either zero C-check difference or the syndrome-plus-logical-parity signature of one C readout flip. `pairs` adds pairs of distinct prep fault locations and includes the robust single-fault rule.
- `both` requires B-clean and readout robustness together; `allpairs` adds the pair-fault condition to both. All 16 combined runs (depths 13–16, caps 82/100) timed out at 240 seconds. The independent rule predicates are also audited in `prep_rule_audit.json`.
- Literal B-clean rejects harmless propagated initial RX-pivot X stabilizers. An X component after a pivot’s first CX (XX if it was the control, X if it was the target) realizes the same propagated error. `proofs.py` records the resulting rank contradiction as a reduced SAT necessary-condition certificate, separate from the depth-bounded full-network timeouts.
- Independent encoders were tested with the necessary condition of no direct B–C CX. In the fixed L5 layout, B cell 6 has no allowed neighbor except C cell 12; C cell 5 has only B neighbors 4 and 11. The UNSAT receipts cover separate encoders with disjoint block supports and the eight free helper cells; they do not cover moving data/A or time-sharing occupied cells.
- `merge.py` reproduced ST_BC `cand_best.qasm` byte for byte before changes. `flags.py` uses the same prefix, A prep, data moves, and ALAP merger. Its extra Z flags measure deterministic two-CX parities on free helpers. Every scored flag and synthesized prep is transformed with the actual `MAIN/minit.py` for q27/q29 when those are eligible first-use resets.
- `score.py` invokes the same `exact2.Eval/run/third_order` functions as `exact2.py --third`, and calls `tprep.check` at 1e6 before MC. MC uses `fast_check.check` at seeds 0, 1000, 2000. Every exact total within 3% of 1.01894e-4, plus a small nonzero first-order contribution, is routed to MC.
- EARLY’s later `early_merge.py` was tested with the 13-layer prep (round 47) and the final winning B-clean prep (round 50). Its emitted unmeasured full circuits are byte-identical to this lane’s merger. `early_compatibility.json` and `FINAL_VERIFICATION.json` record these checks. Prep files are independent of absolute time.
- Jerry’s native CryptoMiniSat import failed on a GLIBC_2.33 dependency (host glibc 2.31). Computation was rerun in the available `fnc-build:22.04` image using the host user UID/GID. Owl uses the required Docker UID/GID and thread caps. Process counts and host load are logged before launches.
- The remaining first-use resets of both leading preps were scanned with MAIN/minit.py. The 13-layer prep selects q23/q28 in addition to q27/q29; the winning B-clean prep selects q25/q28 in addition to q27/q29. Per-site second-order generator measurements are preserved in `*.init_scan.json`; final combined variants received the full exact/MC pipeline. Rebuildable intermediate QASM files were pruned after validation.

This report is regenerated from receipts by `report.py`. A — in an MC column means the circuit was outside the requested MC screening window. `completion_audit.json` checks that no eligible MC result is missing. `best.qasm`/`best.json` are byte-for-byte aliases of the lowest-mean candidate, and `ARTIFACTS.sha256` verifies the delivered files.
