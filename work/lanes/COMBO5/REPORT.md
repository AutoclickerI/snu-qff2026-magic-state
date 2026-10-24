# COMBO5 — clean B+C synthesis with release-aware timing

Lowest measured mean: **8.49943458e-05**, `clean_d14_late3_s0_init/clean_d14_late3_s0_m27`, seed-0 acceptance **0.55633524**.
Target mean 8.46431e-5: **not met**. No submissions were made.

The identical v16_bc2m reference text measured 8.55379233e-05 on these three seeds; its seed-0 acceptance was 0.53313237. The stricter 8.46431e-5 threshold from the brief remains the success criterion.

All MC entries are 1e8 shots at seeds 0, 1000, 2000. Each MC circuit first passed `tprep.check` at 1e6 shots. Exact totals use EVAL/exact2.py’s `--third` computation only for |c1| < 1e-12. `c1` is the contribution at p=0.001; exp(−A1) is an acceptance estimate. Wait steps are R−33, the common post-prefix interval; move operations overlap parts of this interval.

| Candidate | Prep rule | Depth | Prep CX | R | Wait | c1 | 2nd | 3rd | Exact total | exp(−A1) | MC 0 | MC 1000 | MC 2000 | Mean | Seed-0 acceptance | 1e6 judge | Files |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| clean_d14_late3_s0_init/clean_d14_late3_s0_m27 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.37361747e-05 | 2.13921507e-05 | 8.51283254e-05 | 0.55616477 | 8.48229567e-05 | 8.56489246e-05 | 8.45111559e-05 | 8.49943458e-05 | 0.55633524 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m27.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m27.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m27.score.json) |
| clean_d14_late3_k82_s4_mall | clean | 14 | 76 | 48 | 15 | 3.18263934e-19 | 6.21093364e-05 | 2.30411345e-05 | 8.51504709e-05 | 0.542488984 | 8.40513568e-05 | 8.45064262e-05 | 8.75510384e-05 | 8.53696071e-05 | 0.54270391 | PASS | [QASM](clean_d14_late3_k82_s4_mall.qasm), [metadata](clean_d14_late3_k82_s4_mall.json), [receipt](clean_d14_late3_k82_s4_mall.score.json) |
| v16_bc2m | clean | 14 | 82 | 50 | 17 | 3.18263934e-19 | 5.83953319e-05 | 2.58030841e-05 | 8.4198416e-05 | 0.533060691 | 8.61136982e-05 | 8.52861662e-05 | 8.52139056e-05 | 8.55379233e-05 | 0.53313237 | PASS | [QASM](v16_bc2m.qasm), [metadata](v16_bc2m.json), [receipt](v16_bc2m.score.json) |
| clean_d14_late3_k82_s3_mall | clean | 14 | 71 | 47 | 14 | 3.18263934e-19 | 6.29408785e-05 | 2.15873194e-05 | 8.45281979e-05 | 0.54491692 | 8.45800257e-05 | 8.64012329e-05 | 8.57298901e-05 | 8.55703829e-05 | 0.54510506 | PASS | [QASM](clean_d14_late3_k82_s3_mall.qasm), [metadata](clean_d14_late3_k82_s3_mall.json), [receipt](clean_d14_late3_k82_s3_mall.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_mall | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.29361747e-05 | 2.11634897e-05 | 8.40996644e-05 | 0.546061314 | 8.54943719e-05 | 8.65609985e-05 | 8.47102448e-05 | 8.55885384e-05 | 0.54629327 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_mall.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_mall.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_mall.score.json) |
| clean_d14_late3_s0 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.41917302e-05 | 2.14015705e-05 | 8.55933007e-05 | 0.557092485 | 8.62747636e-05 | 8.53860528e-05 | 8.60950911e-05 | 8.59186358e-05 | 0.55728927 | PASS | [QASM](clean_d14_late3_s0.qasm), [metadata](clean_d14_late3_s0.json), [receipt](clean_d14_late3_s0.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m21 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.41917302e-05 | 2.13397396e-05 | 8.55314698e-05 | 0.55616477 | 8.62172709e-05 | 8.67906828e-05 | 8.50500078e-05 | 8.60193205e-05 | 0.55632705 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m21.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m21.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m21.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m14 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.41917302e-05 | 2.13976347e-05 | 8.55893649e-05 | 0.55616477 | 8.67591734e-05 | 8.4277406e-05 | 8.70941497e-05 | 8.60435763e-05 | 0.55636768 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m14.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m14.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m14.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m25 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.40028413e-05 | 2.13893681e-05 | 8.53922094e-05 | 0.55616477 | 8.56824377e-05 | 8.78571449e-05 | 8.51939448e-05 | 8.62445091e-05 | 0.55635672 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m25.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m25.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m25.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m9 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.41917302e-05 | 2.14013766e-05 | 8.55931068e-05 | 0.55616477 | 8.67247198e-05 | 8.75459828e-05 | 8.52214838e-05 | 8.64973955e-05 | 0.55641575 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m9.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m9.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m9.score.json) |
| timed_compact_clean_d14_k100 | clean | 14 | 82 | 50 | 17 | 3.18263934e-19 | 5.91619986e-05 | 2.60827883e-05 | 8.52447869e-05 | 0.543829232 | 8.63893779e-05 | 8.62525606e-05 | 8.70724142e-05 | 8.65714509e-05 | 0.54399049 | PASS | [QASM](timed_compact_clean_d14_k100.qasm), [metadata](timed_compact_clean_d14_k100.json), [receipt](timed_compact_clean_d14_k100.score.json) |
| clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.29361747e-05 | 2.11634897e-05 | 8.40996644e-05 | 0.546972175 | 8.58275529e-05 | 8.690053e-05 | 8.74984074e-05 | 8.67421634e-05 | 0.5472019 | PASS | [QASM](clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.qasm), [metadata](clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.json), [receipt](clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m20 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.41917302e-05 | 2.14015705e-05 | 8.55933007e-05 | 0.55616477 | 8.83652711e-05 | 8.59375379e-05 | 8.59238075e-05 | 8.67422055e-05 | 0.55638374 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m20.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m20.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m20.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m22 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.41917302e-05 | 2.13402255e-05 | 8.55319557e-05 | 0.55616477 | 8.64744723e-05 | 8.78906066e-05 | 8.58924249e-05 | 8.67525012e-05 | 0.55634916 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m22.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m22.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m22.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m29 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.37806191e-05 | 2.13913288e-05 | 8.51719479e-05 | 0.55616477 | 8.67914207e-05 | 8.66686818e-05 | 8.6867731e-05 | 8.67759445e-05 | 0.55633379 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m29.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m29.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m29.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m23 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.41472858e-05 | 2.13954714e-05 | 8.55427572e-05 | 0.55616477 | 8.85236947e-05 | 8.6930555e-05 | 8.51771793e-05 | 8.6877143e-05 | 0.55634822 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m23.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m23.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m23.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m28 | — | — | — | None | — | 3.18263934e-19 | 6.39806191e-05 | 2.13909362e-05 | 8.53715553e-05 | 0.55616477 | 8.76577809e-05 | 8.72537801e-05 | 8.66756463e-05 | 8.71957358e-05 | 0.55636818 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m28.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m28.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m28.score.json) |
| clean_d14_late3_k82_s5_mall | clean | 14 | 72 | 47 | 14 | 3.18263934e-19 | 6.36368129e-05 | 2.15711851e-05 | 8.52079979e-05 | 0.545408373 | 8.71266989e-05 | 8.62163356e-05 | 8.82737473e-05 | 8.7205594e-05 | 0.54558477 | PASS | [QASM](clean_d14_late3_k82_s5_mall.qasm), [metadata](clean_d14_late3_k82_s5_mall.json), [receipt](clean_d14_late3_k82_s5_mall.score.json) |
| clean_d14_late3_k82_s3 | clean | 14 | 71 | 47 | 14 | 3.18263934e-19 | 6.39297674e-05 | 2.18351367e-05 | 8.57649041e-05 | 0.555924972 | 8.71958622e-05 | 8.71284763e-05 | 8.76525981e-05 | 8.73256455e-05 | 0.55610437 | PASS | [QASM](clean_d14_late3_k82_s3.qasm), [metadata](clean_d14_late3_k82_s3.json), [receipt](clean_d14_late3_k82_s3.score.json) |
| clean_d14_late2_s0_mall | clean | 14 | 73 | 47 | 14 | 3.18263934e-19 | 6.51836317e-05 | 2.13093372e-05 | 8.64929689e-05 | 0.544615043 | 8.62493579e-05 | 8.91265614e-05 | 8.67986177e-05 | 8.73915123e-05 | 0.54481565 | PASS | [QASM](clean_d14_late2_s0_mall.qasm), [metadata](clean_d14_late2_s0_mall.json), [receipt](clean_d14_late2_s0_mall.score.json) |
| clean_d14_split46_s1_mall | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.50651797e-05 | 2.13494313e-05 | 8.6414611e-05 | 0.546053082 | 8.77355238e-05 | 8.77351737e-05 | 8.72645044e-05 | 8.75784006e-05 | 0.54630095 | PASS | [QASM](clean_d14_split46_s1_mall.qasm), [metadata](clean_d14_split46_s1_mall.json), [receipt](clean_d14_split46_s1_mall.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m16 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.41917302e-05 | 2.13402255e-05 | 8.55319557e-05 | 0.55616477 | 8.6473961e-05 | 8.89121515e-05 | 8.74716369e-05 | 8.76192498e-05 | 0.55641027 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m16.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m16.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m16.score.json) |
| clean_d14_late3_s0_init/clean_d14_late3_s0_m2 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.41917302e-05 | 2.13990029e-05 | 8.55907331e-05 | 0.55616477 | 8.78793364e-05 | 8.9120535e-05 | 8.59857856e-05 | 8.76618857e-05 | 0.55633101 | PASS | [QASM](clean_d14_late3_s0_init/clean_d14_late3_s0_m2.qasm), [metadata](clean_d14_late3_s0_init/clean_d14_late3_s0_m2.json), [receipt](clean_d14_late3_s0_init/clean_d14_late3_s0_m2.score.json) |
| clean_d15_late5_s0_mall | clean | 15 | 75 | 47 | 14 | 3.18263934e-19 | 6.44479664e-05 | 2.19967412e-05 | 8.64447076e-05 | 0.543955377 | 8.63065657e-05 | 8.86461973e-05 | 8.82386782e-05 | 8.77304804e-05 | 0.54422279 | PASS | [QASM](clean_d15_late5_s0_mall.qasm), [metadata](clean_d15_late5_s0_mall.json), [receipt](clean_d15_late5_s0_mall.score.json) |
| timed_compact_base_d13_k82_mall | base | 13 | 73 | 47 | 14 | 3.51570624e-19 | 6.5753239e-05 | 2.06828923e-05 | 8.64361313e-05 | 0.550517794 | 8.82453426e-05 | 8.71133069e-05 | 8.83267341e-05 | 8.78951279e-05 | 0.55068062 | PASS | [QASM](timed_compact_base_d13_k82_mall.qasm), [metadata](timed_compact_base_d13_k82_mall.json), [receipt](timed_compact_base_d13_k82_mall.score.json) |
| clean_d14_late3_k82_s4 | clean | 14 | 76 | 48 | 15 | 3.18263934e-19 | 6.29760031e-05 | 2.32985238e-05 | 8.62745268e-05 | 0.553447988 | 8.77568342e-05 | 8.9206912e-05 | 8.75755675e-05 | 8.81797712e-05 | 0.55357512 | PASS | [QASM](clean_d14_late3_k82_s4.qasm), [metadata](clean_d14_late3_k82_s4.json), [receipt](clean_d14_late3_k82_s4.score.json) |
| clean_d14_late3_k82_s5 | clean | 14 | 72 | 47 | 14 | 3.18263934e-19 | 6.50034795e-05 | 2.18168498e-05 | 8.68203293e-05 | 0.556426353 | — | — | — | — | — | PASS | [QASM](clean_d14_late3_k82_s5.qasm), [metadata](clean_d14_late3_k82_s5.json), [receipt](clean_d14_late3_k82_s5.score.json) |
| timed_compact_base_d13_k82 | base | 13 | 73 | 47 | 14 | 3.51570624e-19 | 6.67754612e-05 | 2.09221581e-05 | 8.76976193e-05 | 0.561638991 | — | — | — | — | — | PASS | [QASM](timed_compact_base_d13_k82.qasm), [metadata](timed_compact_base_d13_k82.json), [receipt](timed_compact_base_d13_k82.score.json) |
| clean_d14_split46_s1 | clean | 14 | 75 | 47 | 14 | 3.18263934e-19 | 6.6698439e-05 | 2.15993125e-05 | 8.82977514e-05 | 0.557084086 | — | — | — | — | — | PASS | [QASM](clean_d14_split46_s1.qasm), [metadata](clean_d14_split46_s1.json), [receipt](clean_d14_split46_s1.score.json) |
| clean_d14_late2_s0 | clean | 14 | 73 | 47 | 14 | 3.18263934e-19 | 6.67391873e-05 | 2.15691362e-05 | 8.83083234e-05 | 0.555616996 | — | — | — | — | — | PASS | [QASM](clean_d14_late2_s0.qasm), [metadata](clean_d14_late2_s0.json), [receipt](clean_d14_late2_s0.score.json) |
| clean_d15_late5_s0 | clean | 15 | 75 | 47 | 14 | 3.18263934e-19 | 6.61367812e-05 | 2.22612478e-05 | 8.8398029e-05 | 0.554944004 | — | — | — | — | — | PASS | [QASM](clean_d15_late5_s0.qasm), [metadata](clean_d15_late5_s0.json), [receipt](clean_d15_late5_s0.score.json) |
| clean_d14_late3_k82_s2_mall | clean | 14 | 76 | 48 | 15 | 3.18263934e-19 | 6.57994071e-05 | 2.27587663e-05 | 8.85581734e-05 | 0.54291448 | — | — | — | — | — | PASS | [QASM](clean_d14_late3_k82_s2_mall.qasm), [metadata](clean_d14_late3_k82_s2_mall.json), [receipt](clean_d14_late3_k82_s2_mall.score.json) |
| clean_d15_late4_s0_mall | clean | 15 | 73 | 47 | 14 | 3.18263934e-19 | 6.6161969e-05 | 2.24161311e-05 | 8.85781e-05 | 0.539486558 | — | — | — | — | — | PASS | [QASM](clean_d15_late4_s0_mall.qasm), [metadata](clean_d15_late4_s0_mall.json), [receipt](clean_d15_late4_s0_mall.score.json) |
| clean_d14_late3_k82_s6_mall | clean | 14 | 72 | 48 | 15 | 3.18263934e-19 | 6.63974761e-05 | 2.32020714e-05 | 8.95995475e-05 | 0.54101827 | — | — | — | — | — | PASS | [QASM](clean_d14_late3_k82_s6_mall.qasm), [metadata](clean_d14_late3_k82_s6_mall.json), [receipt](clean_d14_late3_k82_s6_mall.score.json) |
| clean_d15_late3_s0_mall | clean | 15 | 79 | 49 | 16 | 3.18263934e-19 | 6.34833314e-05 | 2.63683677e-05 | 8.98516991e-05 | 0.532221069 | — | — | — | — | — | PASS | [QASM](clean_d15_late3_s0_mall.qasm), [metadata](clean_d15_late3_s0_mall.json), [receipt](clean_d15_late3_s0_mall.score.json) |
| clean_d14_late3_k82_s2 | clean | 14 | 76 | 48 | 15 | 3.18263934e-19 | 6.73215553e-05 | 2.30237323e-05 | 9.03452876e-05 | 0.55388208 | — | — | — | — | — | PASS | [QASM](clean_d14_late3_k82_s2.qasm), [metadata](clean_d14_late3_k82_s2.json), [receipt](clean_d14_late3_k82_s2.score.json) |
| clean_d15_late4_s0 | clean | 15 | 73 | 47 | 14 | 3.18263934e-19 | 6.87508579e-05 | 2.26731189e-05 | 9.14239767e-05 | 0.550384909 | — | — | — | — | — | PASS | [QASM](clean_d15_late4_s0.qasm), [metadata](clean_d15_late4_s0.json), [receipt](clean_d15_late4_s0.score.json) |
| clean_d15_late3_s0 | clean | 15 | 79 | 49 | 16 | 3.18263934e-19 | 6.52054795e-05 | 2.66564044e-05 | 9.1861884e-05 | 0.542972648 | — | — | — | — | — | PASS | [QASM](clean_d15_late3_s0.qasm), [metadata](clean_d15_late3_s0.json), [receipt](clean_d15_late3_s0.score.json) |
| clean_d14_late3_k82_s6 | clean | 14 | 72 | 48 | 15 | 3.18263934e-19 | 6.84751058e-05 | 2.34809981e-05 | 9.19561038e-05 | 0.551947564 | — | — | — | — | — | PASS | [QASM](clean_d14_late3_k82_s6.qasm), [metadata](clean_d14_late3_k82_s6.json), [receipt](clean_d14_late3_k82_s6.score.json) |
| timed_compact_clean_d15_k100 | clean | 15 | 81 | 50 | 17 | 3.18263934e-19 | 6.49541687e-05 | 2.86336407e-05 | 9.35878095e-05 | 0.536735416 | — | — | — | — | — | PASS | [QASM](timed_compact_clean_d15_k100.qasm), [metadata](timed_compact_clean_d15_k100.json), [receipt](timed_compact_clean_d15_k100.score.json) |
| timed_compact_clean_d15_k82 | clean | 15 | 82 | 51 | 18 | 3.18263934e-19 | 7.12409744e-05 | 3.03147272e-05 | 0.000101555702 | 0.532849739 | — | — | — | — | — | PASS | [QASM](timed_compact_clean_d15_k82.qasm), [metadata](timed_compact_clean_d15_k82.json), [receipt](timed_compact_clean_d15_k82.score.json) |

## Solver receipts

The solver is EARLY’s release-constrained copy of BC2 sat6, with BC2’s clean rule. An X fault invisible to C must leave B trivial modulo its X stabilizers. Single-X faults at layer boundaries and correlated XX faults from each selected CX are checked by CEGAR. Late layers are zero-indexed. UNSAT applies only to the recorded model, pivot restrictions, release constraints and CX cap; TIMEOUT is not a proof.

| Search | Depth | CX cap | Late-cell constraints | Fixed pivots | Status | Prep CX | Seconds | CEGAR fault constraints | Receipt |
|---|---:|---:|---|---|---|---:|---:|---:|---|
| clean_d13_free_late3_s1 | 13 | 100 | {'4': 3, '6': 3, '13': 3, '19': 3} | False | TIMEOUT | — | 360.420894 | 120 | [clean_d13_free_late3_s1.receipt.json](clean_d13_free_late3_s1.receipt.json) |
| clean_d13_late2_s0 | 13 | 100 | {'4': 2, '6': 2, '13': 2, '19': 2} | True | UNSAT | — | 3.77308862 | 93 | [clean_d13_late2_s0.receipt.json](clean_d13_late2_s0.receipt.json) |
| clean_d13_late3_s0 | 13 | 100 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | UNSAT | — | 0.922753184 | 56 | [clean_d13_late3_s0.receipt.json](clean_d13_late3_s0.receipt.json) |
| clean_d13_late4_s0 | 13 | 100 | {'4': 4, '6': 4, '13': 4, '19': 4} | True | UNSAT | — | 0.256825913 | 56 | [clean_d13_late4_s0.receipt.json](clean_d13_late4_s0.receipt.json) |
| clean_d14_free_late3_s1 | 14 | 100 | {'4': 3, '6': 3, '13': 3, '19': 3} | False | TIMEOUT | — | 362.109152 | 121 | [clean_d14_free_late3_s1.receipt.json](clean_d14_free_late3_s1.receipt.json) |
| clean_d14_late2_s0 | 14 | 100 | {'4': 2, '6': 2, '13': 2, '19': 2} | True | SAT | 73 | 25.0736445 | 162 | [clean_d14_late2_s0.receipt.json](clean_d14_late2_s0.receipt.json) |
| clean_d14_late3_k82_s2 | 14 | 82 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | SAT | 76 | 40.7231475 | 119 | [clean_d14_late3_k82_s2.receipt.json](clean_d14_late3_k82_s2.receipt.json) |
| clean_d14_late3_k82_s3 | 14 | 82 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | SAT | 71 | 7.9919095 | 163 | [clean_d14_late3_k82_s3.receipt.json](clean_d14_late3_k82_s3.receipt.json) |
| clean_d14_late3_k82_s4 | 14 | 82 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | SAT | 76 | 8.94131154 | 144 | [clean_d14_late3_k82_s4.receipt.json](clean_d14_late3_k82_s4.receipt.json) |
| clean_d14_late3_k82_s5 | 14 | 82 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | SAT | 72 | 8.09770066 | 152 | [clean_d14_late3_k82_s5.receipt.json](clean_d14_late3_k82_s5.receipt.json) |
| clean_d14_late3_k82_s6 | 14 | 82 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | SAT | 72 | 8.66993151 | 144 | [clean_d14_late3_k82_s6.receipt.json](clean_d14_late3_k82_s6.receipt.json) |
| clean_d14_late3_s0 | 14 | 100 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | SAT | 75 | 14.9063396 | 165 | [clean_d14_late3_s0.receipt.json](clean_d14_late3_s0.receipt.json) |
| clean_d14_late4_s0 | 14 | 100 | {'4': 4, '6': 4, '13': 4, '19': 4} | True | UNSAT | — | 4.12178095 | 113 | [clean_d14_late4_s0.receipt.json](clean_d14_late4_s0.receipt.json) |
| clean_d14_split1319_s1 | 14 | 100 | {'4': 3, '6': 3, '13': 4, '19': 4} | True | UNSAT | — | 8.75924272 | 104 | [clean_d14_split1319_s1.receipt.json](clean_d14_split1319_s1.receipt.json) |
| clean_d14_split46_s1 | 14 | 100 | {'4': 4, '6': 4, '13': 3, '19': 3} | True | SAT | 75 | 7.91911724 | 153 | [clean_d14_split46_s1.receipt.json](clean_d14_split46_s1.receipt.json) |
| clean_d15_free_late3_s1 | 15 | 100 | {'4': 3, '6': 3, '13': 3, '19': 3} | False | TIMEOUT | — | 361.390178 | 97 | [clean_d15_free_late3_s1.receipt.json](clean_d15_free_late3_s1.receipt.json) |
| clean_d15_late2_s0 | 15 | 100 | {'4': 2, '6': 2, '13': 2, '19': 2} | True | TIMEOUT | — | 361.172784 | 172 | [clean_d15_late2_s0.receipt.json](clean_d15_late2_s0.receipt.json) |
| clean_d15_late3_s0 | 15 | 100 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | SAT | 79 | 28.9818887 | 174 | [clean_d15_late3_s0.receipt.json](clean_d15_late3_s0.receipt.json) |
| clean_d15_late4_s0 | 15 | 100 | {'4': 4, '6': 4, '13': 4, '19': 4} | True | SAT | 73 | 9.94904011 | 153 | [clean_d15_late4_s0.receipt.json](clean_d15_late4_s0.receipt.json) |
| clean_d15_late5_s0 | 15 | 100 | {'4': 5, '6': 5, '13': 5, '19': 5} | True | SAT | 75 | 7.18145732 | 121 | [clean_d15_late5_s0.receipt.json](clean_d15_late5_s0.receipt.json) |
| window_clean_d14_late2_w10 | 14 | 100 | {'4': 2, '6': 2, '13': 2, '19': 2} | True | UNSAT | — | 1.09067973 | 0 | [window_clean_d14_late2_w10.receipt.json](window_clean_d14_late2_w10.receipt.json) |
| window_clean_d14_late2_w6 | 14 | 100 | {'4': 2, '6': 2, '13': 2, '19': 2} | True | UNSAT | — | 0.750347628 | 0 | [window_clean_d14_late2_w6.receipt.json](window_clean_d14_late2_w6.receipt.json) |
| window_clean_d14_late2_w8 | 14 | 100 | {'4': 2, '6': 2, '13': 2, '19': 2} | True | UNSAT | — | 0.936938518 | 0 | [window_clean_d14_late2_w8.receipt.json](window_clean_d14_late2_w8.receipt.json) |
| window_clean_d14_late3_w10 | 14 | 100 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | UNSAT | — | 0.273807555 | 0 | [window_clean_d14_late3_w10.receipt.json](window_clean_d14_late3_w10.receipt.json) |
| window_clean_d14_late3_w6 | 14 | 100 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | UNSAT | — | 0.901136402 | 0 | [window_clean_d14_late3_w6.receipt.json](window_clean_d14_late3_w6.receipt.json) |
| window_clean_d14_late3_w8 | 14 | 100 | {'4': 3, '6': 3, '13': 3, '19': 3} | True | UNSAT | — | 0.699234845 | 0 | [window_clean_d14_late3_w8.receipt.json](window_clean_d14_late3_w8.receipt.json) |

Fixed-pivot clean depth 13 was UNSAT at late splits 2, 3 and 4. Allowing arbitrary pivots at depths 13, 14 and 15 timed out at 360 seconds. The six `window_` searches held the original BC2 winner’s suffix fixed while freeing its first 6, 8 or 10 layers, with late split 2 or 3; all were UNSAT. These results leave other pivots, helpers, layouts and broader synthesis models open.


## Measurement initialization

`minit_scan.py` invokes MAIN/minit.py’s copied transform at every eligible first-use Z-reset site and on all sites together. Sites are selected by the full exact total, not second order. All variants within 3% of 8.41984e-5 are required to have all three MC seeds.

- `clean_d14_late3_s0.minit_scan.json`: selected sites [14, 16, 2, 21, 22, 23, 25, 27, 28, 29, 9]; baseline exact 8.55933007e-05.

## Loss attribution

These runs use MAIN/ablate.py with `--pre-end 32`, the candidate’s actual R, A cells 1,14,8,9,2,16,15, and both `--pairs` and `--wait-scale 0,0.5,1`. Region names follow the tool’s time-based definition: preparation operations that overlap the prefix before step 33 are included in `pre`. Removing or scaling a noise region is a diagnostic, not a physically constructed faster circuit.

| Circuit | Wait-noise scale | 2nd | 3rd | Exact total | exp(−A1), estimate | Receipt |
|---|---:|---:|---:|---:|---:|---|
| clean_d14_late3_s0_m27 | 0.000 | 5.6960e-05 | 6.9094e-06 | 6.3870e-05 | 0.6003 | [clean_d14_late3_s0_m27.waitscale.log](clean_d14_late3_s0_init/clean_d14_late3_s0_m27.waitscale.log) |
| clean_d14_late3_s0_m27 | 0.500 | 6.0363e-05 | 1.2826e-05 | 7.3189e-05 | 0.5777 | [clean_d14_late3_s0_m27.waitscale.log](clean_d14_late3_s0_init/clean_d14_late3_s0_m27.waitscale.log) |
| clean_d14_late3_s0_m27 | 1.000 | 6.3736e-05 | 2.1392e-05 | 8.5128e-05 | 0.5562 | [clean_d14_late3_s0_m27.waitscale.log](clean_d14_late3_s0_init/clean_d14_late3_s0_m27.waitscale.log) |
| clean_d14_late3_s0_mall | 0.000 | 5.6160e-05 | 6.7965e-06 | 6.2957e-05 | 0.5894 | [clean_d14_late3_s0_mall.waitscale.log](clean_d14_late3_s0_init/clean_d14_late3_s0_mall.waitscale.log) |
| clean_d14_late3_s0_mall | 0.500 | 5.9563e-05 | 1.2661e-05 | 7.2224e-05 | 0.5672 | [clean_d14_late3_s0_mall.waitscale.log](clean_d14_late3_s0_init/clean_d14_late3_s0_mall.waitscale.log) |
| clean_d14_late3_s0_mall | 1.000 | 6.2936e-05 | 2.1163e-05 | 8.4100e-05 | 0.5461 | [clean_d14_late3_s0_mall.waitscale.log](clean_d14_late3_s0_init/clean_d14_late3_s0_mall.waitscale.log) |
| clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9 | 0.000 | 5.6160e-05 | 6.7965e-06 | 6.2957e-05 | 0.5904 | [clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.waitscale.log](clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.waitscale.log) |
| clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9 | 0.500 | 5.9563e-05 | 1.2661e-05 | 7.2224e-05 | 0.5682 | [clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.waitscale.log](clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.waitscale.log) |
| clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9 | 1.000 | 6.2936e-05 | 2.1163e-05 | 8.4100e-05 | 0.5470 | [clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.waitscale.log](clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.waitscale.log) |
| v16_bc2m | 0.000 | 4.9858e-05 | 6.7608e-06 | 5.6619e-05 | 0.5845 | [v16_bc2m.waitscale.log](v16_bc2m.waitscale.log) |
| v16_bc2m | 0.500 | 5.4150e-05 | 1.4323e-05 | 6.8473e-05 | 0.5581 | [v16_bc2m.waitscale.log](v16_bc2m.waitscale.log) |
| v16_bc2m | 1.000 | 5.8395e-05 | 2.5803e-05 | 8.4198e-05 | 0.5331 | [v16_bc2m.waitscale.log](v16_bc2m.waitscale.log) |

Pair decompositions:

[clean_d14_late3_s0_m27.pairs.log](clean_d14_late3_s0_init/clean_d14_late3_s0_m27.pairs.log)
```text
2nd order 6.3736e-05 by region pair:
  roundxround    2.884e-05  45.2%   e.g. L384 idle Y@q0 t=49..49 + L385 idle Z@q20 t=49..49
  prepxprep      1.427e-05  22.4%   e.g. L238 flip X@q13 t=35 + L243 idle X@q29 t=36..36
  Axwait         4.235e-06   6.6%   e.g. L191 idle Z@q0 t=33..46 + L329 gate2 IZ@q8,14 t=44
  Axprep         3.129e-06   4.9%   e.g. L247 flip Z@q6 t=36 + L329 gate2 IZ@q8,14 t=44
  prexwait       2.541e-06   4.0%   e.g. L155 idle X@q7 t=25..28 + L189 idle X@q20 t=33..46
  Axpre          2.409e-06   3.8%   e.g. L143 idle X@q0 t=23..30 + L329 gate2 XZ@q8,14 t=44
  prexprep       2.178e-06   3.4%   e.g. L208 gate1 X@q27 t=32 + L220 flip X@q29 t=33
  prepxround     1.811e-06   2.8%   e.g. L257 flip X@q4 t=37 + L380 flip X@q17 t=48
  AxA            1.727e-06   2.7%   e.g. L297 idle Z@q9 t=42..46 + L328 gate2 IZ@q1,2 t=44
  Axround        1.484e-06   2.3%   e.g. L329 gate2 IZ@q8,14 t=44 + L393 flip Z@q6 t=49
  prexround      4.878e-07   0.8%   e.g. L155 idle X@q7 t=25..28 + L371 flip X@q14 t=48
  prexpre        3.406e-07   0.5%   e.g. L155 idle X@q7 t=25..28 + L189 gate1 X@q20 t=32
  Axmoves        2.844e-07   0.4%   e.g. L233 gate2 IZ@q4,10 t=35 + L328 gate2 IZ@q1,2 t=44
weight-3 term 2.5626e-05 by region (each triple split in thirds; kept triples cover 2.4834e-05):
  wait     6.836e-06  27.5%
  pre      5.424e-06  21.8%
  round    4.573e-06  18.4%
  A        3.912e-06  15.8%
  prep     3.503e-06  14.1%
  moves    5.862e-07   2.4%
```

[clean_d14_late3_s0_mall.pairs.log](clean_d14_late3_s0_init/clean_d14_late3_s0_mall.pairs.log)
```text
2nd order 6.2936e-05 by region pair:
  roundxround    2.884e-05  45.8%   e.g. L384 idle Y@q0 t=49..49 + L385 idle Z@q20 t=49..49
  prepxprep      1.402e-05  22.3%   e.g. L238 flip X@q13 t=35 + L243 idle X@q29 t=36..36
  Axwait         4.235e-06   6.7%   e.g. L191 idle Z@q0 t=33..46 + L329 gate2 IZ@q8,14 t=44
  Axprep         3.129e-06   5.0%   e.g. L247 flip Z@q6 t=36 + L329 gate2 IZ@q8,14 t=44
  prexwait       2.541e-06   4.0%   e.g. L155 idle X@q7 t=25..28 + L189 idle X@q20 t=33..46
  Axpre          2.409e-06   3.8%   e.g. L143 idle X@q0 t=23..30 + L329 gate2 XZ@q8,14 t=44
  prepxround     1.811e-06   2.9%   e.g. L257 flip X@q4 t=37 + L380 flip X@q17 t=48
  AxA            1.727e-06   2.7%   e.g. L297 idle Z@q9 t=42..46 + L328 gate2 IZ@q1,2 t=44
  prexprep       1.644e-06   2.6%   e.g. L208 gate1 X@q27 t=32 + L220 gate1 X@q29 t=33
  Axround        1.484e-06   2.4%   e.g. L329 gate2 IZ@q8,14 t=44 + L393 flip Z@q6 t=49
  prexround      4.656e-07   0.7%   e.g. L155 idle X@q7 t=25..28 + L371 flip X@q14 t=48
  prexpre        3.406e-07   0.5%   e.g. L155 idle X@q7 t=25..28 + L189 gate1 X@q20 t=32
  Axmoves        2.844e-07   0.5%   e.g. L233 gate2 IZ@q4,10 t=35 + L328 gate2 IZ@q1,2 t=44
weight-3 term 2.5573e-05 by region (each triple split in thirds; kept triples cover 2.4780e-05):
  wait     6.798e-06  27.4%
  pre      5.397e-06  21.8%
  round    4.618e-06  18.6%
  A        3.909e-06  15.8%
  prep     3.504e-06  14.1%
  moves    5.540e-07   2.2%
```

[clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.pairs.log](clean_d14_late3_s0_m14_16_2_21_22_23_25_27_28_29_9.pairs.log)
```text
2nd order 6.2936e-05 by region pair:
  roundxround    2.884e-05  45.8%   e.g. L384 idle Y@q0 t=49..49 + L385 idle Z@q20 t=49..49
  prepxprep      1.402e-05  22.3%   e.g. L238 flip X@q13 t=35 + L243 idle X@q29 t=36..36
  Axwait         4.235e-06   6.7%   e.g. L191 idle Z@q0 t=33..46 + L329 gate2 IZ@q8,14 t=44
  Axprep         3.129e-06   5.0%   e.g. L247 flip Z@q6 t=36 + L329 gate2 IZ@q8,14 t=44
  prexwait       2.541e-06   4.0%   e.g. L155 idle X@q7 t=25..28 + L189 idle X@q20 t=33..46
  Axpre          2.409e-06   3.8%   e.g. L143 idle X@q0 t=23..30 + L329 gate2 XZ@q8,14 t=44
  prepxround     1.811e-06   2.9%   e.g. L257 flip X@q4 t=37 + L380 flip X@q17 t=48
  AxA            1.727e-06   2.7%   e.g. L297 idle Z@q9 t=42..46 + L328 gate2 IZ@q1,2 t=44
  prexprep       1.644e-06   2.6%   e.g. L208 gate1 X@q27 t=32 + L220 gate1 X@q29 t=33
  Axround        1.484e-06   2.4%   e.g. L329 gate2 IZ@q8,14 t=44 + L393 flip Z@q6 t=49
  prexround      4.656e-07   0.7%   e.g. L155 idle X@q7 t=25..28 + L371 flip X@q14 t=48
  prexpre        3.406e-07   0.5%   e.g. L155 idle X@q7 t=25..28 + L189 gate1 X@q20 t=32
  Axmoves        2.844e-07   0.5%   e.g. L233 gate2 IZ@q4,10 t=35 + L328 gate2 IZ@q1,2 t=44
weight-3 term 2.5552e-05 by region (each triple split in thirds; kept triples cover 2.4759e-05):
  wait     6.797e-06  27.5%
  pre      5.389e-06  21.8%
  round    4.611e-06  18.6%
  A        3.907e-06  15.8%
  prep     3.501e-06  14.1%
  moves    5.540e-07   2.2%
```

[v16_bc2m.pairs.log](v16_bc2m.pairs.log)
```text
2nd order 5.8395e-05 by region pair:
  roundxround    2.884e-05  49.4%   e.g. L394 idle Y@q0 t=52..52 + L395 idle Z@q20 t=52..52
  prepxprep      8.719e-06  14.9%   e.g. L215 gate1 X@q28 t=35 + L287 idle X@q12 t=43..43
  Axwait         5.458e-06   9.3%   e.g. L191 idle Z@q0 t=33..49 + L337 gate2 IZ@q8,14 t=47
  prexwait       3.080e-06   5.3%   e.g. L155 idle X@q7 t=25..28 + L189 idle X@q20 t=33..49
  prepxround     3.029e-06   5.2%   e.g. L284 idle X@q4 t=43..44 + L390 flip X@q17 t=51
  Axprep         3.004e-06   5.1%   e.g. L223 flip Z@q26 t=35 + L337 gate2 IZ@q8,14 t=47
  Axpre          2.009e-06   3.4%   e.g. L143 idle X@q0 t=23..30 + L337 gate2 XZ@q8,14 t=47
  AxA            1.727e-06   3.0%   e.g. L305 idle Z@q9 t=45..49 + L336 gate2 IZ@q1,2 t=47
  Axround        1.484e-06   2.5%   e.g. L337 gate2 IZ@q8,14 t=47 + L403 flip Z@q6 t=52
  prexround      4.212e-07   0.7%   e.g. L155 idle X@q7 t=25..28 + L381 flip X@q14 t=51
  prexpre        3.406e-07   0.6%   e.g. L155 idle X@q7 t=25..28 + L189 gate1 X@q20 t=32
  Axmoves        2.844e-07   0.5%   e.g. L207 gate2 IZ@q4,10 t=34 + L336 gate2 IZ@q1,2 t=47
weight-3 term 3.0108e-05 by region (each triple split in thirds; kept triples cover 2.9386e-05):
  wait     9.333e-06  31.8%
  pre      5.423e-06  18.5%
  round    5.115e-06  17.4%
  A        5.100e-06  17.4%
  prep     3.775e-06  12.8%
  moves    6.401e-07   2.2%
```

The measured diagnostic shows why the gains do not simply add: the selected R=47 circuit has zero-wait-noise exact loss 6.2957e-5 versus 5.6619e-5 for v16. The wait contribution falls from about 2.7579e-5 to 2.1143e-5, while the remaining contribution rises by about 6.338e-6. The second-order prep×prep term grows from 8.719e-6 to 1.402e-5; round×round remains 2.884e-5. These are exact-model diagnostics with the tool’s region convention, not MC measurements of physically modified circuits.


## Verification and limitations

MC audit: 0 eligible candidates still missing full MC. All eligible circuits have all three seeds.
All candidate QASM files have adjacent metadata containing `data_qubits`. No first-order diagnostic is used as a judge gate. All files are lane-local. Host capacity receipts are in `capacity.jsonl`; solver limits and failures are preserved in individual logs.
