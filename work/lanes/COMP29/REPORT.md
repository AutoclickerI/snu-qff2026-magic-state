# COMP29 — v35b acceptance recovery and composition

**Status: RUNNING.** Acceptance floor: **0.5005**. Finalist threshold: v35a, **4.39352767604e-05**. Source of v35b is ST2’s `restore_181_182_188`; the supplied v35b QASM is frozen as `h_base`.

## Finalists below v35a

| Stem | All-orders 1−F | Acceptance | Judge | Speed | MC seed 0 / 1000 / 2000 | MC mean |
|---|---:|---:|---|---|---|---:|
| [h_star_111_joint_122_103](h_star_111_joint_122_103.qasm) | 4.30256023783e-05 | 0.507607910617 | PASS / 0.508023 | FAST / 3.19s per 1e6 | 4.442356e-05 / 4.295143e-05 / 4.137187e-05 | 4.291562e-05 |
| [h_seed_joint_84_122_103](h_seed_joint_84_122_103.qasm) | 4.32017714556e-05 | 0.507237697103 | PASS / 0.506784 | FAST / 2.89s per 1e6 | 4.331762e-05 / 4.159654e-05 / 4.293993e-05 | 4.261803e-05 |
| [h_port_084](h_port_084.qasm) | 4.34058634491e-05 | 0.504428688656 | PASS / 0.504179 | FAST / 2.61s per 1e6 | 4.346023e-05 / 4.146027e-05 / 4.304441e-05 | 4.265497e-05 |
| [h_prep_07](h_prep_07.qasm) | 4.37602134086e-05 | 0.50369486102 | PASS / 0.503391 | FAST / 2.91s per 1e6 | 4.414601e-05 / 4.372788e-05 / 4.416652e-05 | 4.401347e-05 |

## Acceptance-only handoff for ST2

Rows below preserve all-orders conditional loss within 1e-15 and every normalized acceptance/decoder moment within 3e-13. Detector/check removals are distinguished from reset timing. Numerical singleton neutrality is not assumed to compose: every exported joint is repriced. Physical factorization certificates are recorded separately where established.

| Stem | Method | Removed check / timing | Loss delta | Acceptance recovered | Final acceptance | Max normalized moment delta |
|---|---|---|---:|---:|---:|---:|
| [h_prep_07](h_prep_07.qasm) | prep_timing | ["delay isolated preparation resets", [{"index": 243, "qubit": 1, "old": 38, "new": 39, "check_time": 40, "bit": 180, "basis": "MX", "idles_removed": 1, "predicted_acceptance_ratio": 1.0006657749613892}, {"index": 8, "qubit": 4, "old": 2, "new": 4, "check_time": 5, "bit": 188, "basis": "MX", "idles_removed": 2, "predicted_acceptance_ratio": 1.0013315475518352}, {"index": 58, "qubit": 6, "old": 9, "new": 12, "check_time": 13, "bit": 185, "basis": "MX", "idles_removed": 3, "predicted_acceptance_ratio": 1.0019973171787664}]] | 2.99e-16 | 0.0020065112143 | 0.50369486102 | 5.55e-16 |
| [h_prep_06](h_prep_06.qasm) | prep_timing | ["delay isolated preparation resets", [{"index": 8, "qubit": 4, "old": 2, "new": 4, "check_time": 5, "bit": 188, "basis": "MX", "idles_removed": 2, "predicted_acceptance_ratio": 1.0013315475518352}, {"index": 58, "qubit": 6, "old": 9, "new": 12, "check_time": 13, "bit": 185, "basis": "MX", "idles_removed": 3, "predicted_acceptance_ratio": 1.0019973171787664}]] | 1.89e-16 | 0.00167138690503 | 0.503359736711 | 4.44e-16 |
| [h_prep_05](h_prep_05.qasm) | prep_timing | ["delay isolated preparation resets", [{"index": 243, "qubit": 1, "old": 38, "new": 39, "check_time": 40, "bit": 180, "basis": "MX", "idles_removed": 1, "predicted_acceptance_ratio": 1.0006657749613892}, {"index": 58, "qubit": 6, "old": 9, "new": 12, "check_time": 13, "bit": 185, "basis": "MX", "idles_removed": 3, "predicted_acceptance_ratio": 1.0019973171787664}]] | -1.65e-16 | 0.00133670942817 | 0.503025059234 | 3.33e-16 |
| [h_prep_03](h_prep_03.qasm) | prep_timing | ["delay isolated preparation resets", [{"index": 243, "qubit": 1, "old": 38, "new": 39, "check_time": 40, "bit": 180, "basis": "MX", "idles_removed": 1, "predicted_acceptance_ratio": 1.0006657749613892}, {"index": 8, "qubit": 4, "old": 2, "new": 4, "check_time": 5, "bit": 188, "basis": "MX", "idles_removed": 2, "predicted_acceptance_ratio": 1.0013315475518352}]] | -2.49e-16 | 0.00100247818794 | 0.502690827994 | 7.77e-16 |
| [h_prep_04](h_prep_04.qasm) | prep_timing | ["delay isolated preparation resets", [{"index": 58, "qubit": 6, "old": 9, "new": 12, "check_time": 13, "bit": 185, "basis": "MX", "idles_removed": 3, "predicted_acceptance_ratio": 1.0019973171787664}]] | -1.66e-17 | 0.00100203075945 | 0.502690380565 | 3.33e-16 |
| [h_prep_02](h_prep_02.qasm) | prep_timing | ["delay isolated preparation resets", [{"index": 8, "qubit": 4, "old": 2, "new": 4, "check_time": 5, "bit": 188, "basis": "MX", "idles_removed": 2, "predicted_acceptance_ratio": 1.0013315475518352}]] | -1.12e-16 | 0.000668021893968 | 0.5023563717 | 5.55e-16 |
| [h_prep_01](h_prep_01.qasm) | prep_timing | ["delay isolated preparation resets", [{"index": 243, "qubit": 1, "old": 38, "new": 39, "check_time": 40, "bit": 180, "basis": "MX", "idles_removed": 1, "predicted_acceptance_ratio": 1.0006657749613892}]] | -2.04e-16 | 0.000334011541721 | 0.502022361348 | 6.66e-16 |

Reproduced v35b: **4.37602134083e-05**, acceptance **0.501688349806**, 210 CX, native depth **47** (actual source schedule). Its available acceptance over the floor is 0.00118835.

## Candidate prices

594 built stems; 457 completed prices. Sparse code is copied unchanged from MAIN, with output confined to this lane. No gain additivity is assumed.

| Stem | Family / edit | CX | All-orders 1−F | Acceptance | Judge / speed | MC mean |
|---|---|---:|---:|---:|---|---:|
| `h_pguard_joint_002` | preparation_guard_combination | 219 | 4.29618165043e-05 | 0.50733516462 | pending | pending |
| `h_pguard_joint_001` | preparation_guard_combination | 219 | 4.29618772302e-05 | 0.506997325458 | pending | pending |
| `h_pguard_000` | preparation_guard | 218 | 4.297236993e-05 | 0.507639990655 | pending | pending |
| `h_pguard_002` | preparation_guard | 218 | 4.30150484384e-05 | 0.507303103844 | pending | pending |
| `h_pguard_001` | preparation_guard | 218 | 4.30151091673e-05 | 0.506965286031 | pending | pending |
| `h_star_111_joint_122_103` | guard_combination | 217 | 4.30256023783e-05 | 0.507607910617 | PASS / FAST | 4.291562e-05 |
| `h_star_331_joint_122_103` | guard_combination | 217 | 4.30256023783e-05 | 0.507607910617 | pending | pending |
| `h_star_133_joint_122_103` | guard_combination | 217 | 4.30256023783e-05 | 0.507607910617 | pending | pending |
| `h_star_111_joint_122` | guard_combination | 215 | 4.30473120502e-05 | 0.508390193712 | pending | pending |
| `h_star_331_joint_122` | guard_combination | 215 | 4.30473120502e-05 | 0.508390193712 | pending | pending |
| `h_star_133_joint_122` | guard_combination | 215 | 4.30473120502e-05 | 0.508390193712 | pending | pending |
| `h_seed_joint_84_122_103` | seed_guard_combination | 216 | 4.32017714556e-05 | 0.507237697103 | PASS / FAST | 4.261803e-05 |
| `h_seed_joint_69_122_103` | seed_guard_combination | 216 | 4.32180180576e-05 | 0.507067955289 | pending | pending |
| `h_seed_joint_84_122` | seed_guard_combination | 214 | 4.32237264578e-05 | 0.508019409901 | pending | pending |
| `h_star_111` | idle_star | 213 | 4.3227004188e-05 | 0.510868853661 | pending | pending |
| `h_star_133` | idle_star | 213 | 4.3227004188e-05 | 0.510868853661 | pending | pending |
| `h_star_331` | idle_star | 213 | 4.3227004188e-05 | 0.510868853661 | pending | pending |
| `h_seed_joint_69_122` | seed_guard_combination | 214 | 4.32395410595e-05 | 0.507849406038 | pending | pending |
| `h_star_211` | idle_star | 213 | 4.33406133308e-05 | 0.51086952405 | pending | pending |
| `h_star_233` | idle_star | 213 | 4.33406133308e-05 | 0.51086952405 | pending | pending |
| `h_star_112` | idle_star | 213 | 4.33422185542e-05 | 0.510869249856 | pending | pending |
| `h_star_332` | idle_star | 213 | 4.33422185542e-05 | 0.510869249856 | pending | pending |
| `h_star_121` | idle_star | 213 | 4.33431178116e-05 | 0.510869140164 | pending | pending |
| `h_seed_joint_70_122` | seed_guard_combination | 214 | 4.33446241819e-05 | 0.508287567193 | pending | pending |
| `h_seed_joint_84_103` | seed_guard_combination | 214 | 4.33808938226e-05 | 0.509710738162 | pending | pending |
| `h_seed_joint_69_103` | seed_guard_combination | 214 | 4.33970695085e-05 | 0.509540168519 | pending | pending |
| `h_star_511` | idle_star | 212 | 4.34000402109e-05 | 0.509986060431 | pending | pending |
| `h_star_533` | idle_star | 212 | 4.34000402109e-05 | 0.509986060431 | pending | pending |
| `h_star_115` | idle_star | 212 | 4.34021610874e-05 | 0.509986008721 | pending | pending |
| `h_star_335` | idle_star | 212 | 4.34021610874e-05 | 0.509986008721 | pending | pending |
| `h_star_011` | idle_star | 212 | 4.34024353501e-05 | 0.510496693477 | pending | pending |
| `h_star_033` | idle_star | 212 | 4.34024353501e-05 | 0.510496693477 | pending | pending |
| `h_star_110` | idle_star | 212 | 4.34024353501e-05 | 0.510496693477 | pending | pending |
| `h_star_330` | idle_star | 212 | 4.34024353501e-05 | 0.510496693477 | pending | pending |
| `h_star_151` | idle_star | 212 | 4.34039193985e-05 | 0.509985520881 | pending | pending |
| `h_seed_guard_084` | seed_guard | 212 | 4.34044008692e-05 | 0.510496262736 | pending | pending |
| `h_star_101` | idle_star | 212 | 4.34044008692e-05 | 0.510496262736 | pending | pending |
| `h_port_084` | guard_port | 212 | 4.34058634491e-05 | 0.504428688656 | PASS / FAST | 4.265497e-05 |
| `h_seed_guard_069` | seed_guard | 212 | 4.34201445462e-05 | 0.510325429767 | pending | pending |
| `h_star_303` | idle_star | 212 | 4.34201445462e-05 | 0.510325429767 | pending | pending |
| `h_port_069` | guard_port | 212 | 4.34215857972e-05 | 0.504259886123 | pending | pending |
| `h_star_221` | idle_star | 213 | 4.34607446872e-05 | 0.510868667126 | pending | pending |
| `h_star_441` | idle_star | 213 | 4.34607446872e-05 | 0.510868667126 | pending | pending |
| `h_star_212` | idle_star | 213 | 4.34615201714e-05 | 0.510868557553 | pending | pending |
| `h_star_122` | idle_star | 213 | 4.34617786659e-05 | 0.510868521028 | pending | pending |
| `h_star_144` | idle_star | 213 | 4.34617786659e-05 | 0.510868521028 | pending | pending |
| `h_star_251` | idle_star | 212 | 4.35172629059e-05 | 0.509986169496 | pending | pending |
| `h_star_512` | idle_star | 212 | 4.35194427365e-05 | 0.509985459042 | pending | pending |
| `h_star_521` | idle_star | 212 | 4.3519470633e-05 | 0.509985459053 | pending | pending |
| `h_star_215` | idle_star | 212 | 4.35197537426e-05 | 0.509985847453 | pending | pending |
| `h_star_201` | idle_star | 212 | 4.35200488962e-05 | 0.510496532327 | pending | pending |
| `h_star_210` | idle_star | 212 | 4.35210189737e-05 | 0.510496395361 | pending | pending |
| `h_star_152` | idle_star | 212 | 4.35210320559e-05 | 0.509985400047 | pending | pending |
| `h_star_125` | idle_star | 212 | 4.35210741884e-05 | 0.509985637545 | pending | pending |
| `h_star_021` | idle_star | 212 | 4.35214893766e-05 | 0.510496146785 | pending | pending |
| `h_star_120` | idle_star | 212 | 4.35222836837e-05 | 0.510496185221 | pending | pending |
| `h_star_012` | idle_star | 212 | 4.35228655583e-05 | 0.51049593669 | pending | pending |
| `h_star_102` | idle_star | 212 | 4.35231889181e-05 | 0.510495891034 | pending | pending |
| `h_seed_guard_070` | seed_guard | 212 | 4.3525022815e-05 | 0.510765727189 | pending | pending |
| `h_seed_guard_085` | seed_guard | 212 | 4.3525022815e-05 | 0.510765727189 | pending | pending |
| `h_port_070` | guard_port | 212 | 4.35264702057e-05 | 0.504694950336 | pending | pending |
| `h_port_085` | guard_port | 212 | 4.35264702057e-05 | 0.504694950336 | pending | pending |
| `h_seed_joint_122_103` | seed_guard_combination | 214 | 4.35536453683e-05 | 0.506499781215 | pending | pending |
| `h_star_222` | idle_star | 213 | 4.35707286541e-05 | 0.510869693035 | pending | pending |
| `h_star_244` | idle_star | 213 | 4.35707286541e-05 | 0.510869693035 | pending | pending |
| `h_star_442` | idle_star | 213 | 4.35707286541e-05 | 0.510869693035 | pending | pending |
| `h_seed_guard_122` | seed_guard | 212 | 4.35760898752e-05 | 0.507280357286 | pending | pending |
| `h_port_122` | guard_port | 212 | 4.35774577846e-05 | 0.503922681182 | pending | pending |
| `h_star_551` | idle_star | 211 | 4.35792726366e-05 | 0.509104338282 | pending | pending |
| `h_star_515` | idle_star | 211 | 4.35792726367e-05 | 0.509104338282 | pending | pending |
| `h_star_051` | idle_star | 211 | 4.35793884876e-05 | 0.509614047602 | pending | pending |
| `h_star_510` | idle_star | 211 | 4.35794413238e-05 | 0.509614000474 | pending | pending |
| `h_star_501` | idle_star | 211 | 4.35794858213e-05 | 0.50961388793 | pending | pending |
| `h_star_155` | idle_star | 211 | 4.35829490309e-05 | 0.509104510867 | pending | pending |
| `h_star_150` | idle_star | 211 | 4.35829490314e-05 | 0.509614351789 | pending | pending |
| `h_star_015` | idle_star | 211 | 4.3583278061e-05 | 0.509613929259 | pending | pending |
| `h_star_001` | idle_star | 211 | 4.35836070909e-05 | 0.510124084408 | pending | pending |
| `h_star_105` | idle_star | 211 | 4.35849765234e-05 | 0.509614174165 | pending | pending |
| `h_star_010` | idle_star | 211 | 4.35853944574e-05 | 0.510124104472 | pending | pending |
| `h_star_100` | idle_star | 211 | 4.35870040106e-05 | 0.510124574711 | pending | pending |
| `h_star_522` | idle_star | 212 | 4.36331738287e-05 | 0.509985941926 | pending | pending |
| `h_star_544` | idle_star | 212 | 4.36331738287e-05 | 0.509985941926 | pending | pending |
| `h_star_252` | idle_star | 212 | 4.36331794805e-05 | 0.509986171377 | pending | pending |
| `h_star_225` | idle_star | 212 | 4.36332908733e-05 | 0.509986136576 | pending | pending |
| `h_star_445` | idle_star | 212 | 4.36332908733e-05 | 0.509986136576 | pending | pending |
| `h_star_220` | idle_star | 212 | 4.36334634321e-05 | 0.510496821265 | pending | pending |
| `h_star_440` | idle_star | 212 | 4.36334634321e-05 | 0.510496821265 | pending | pending |
| `h_seed_guard_088` | seed_guard | 212 | 4.36334634322e-05 | 0.510496821265 | pending | pending |
| `h_star_022` | idle_star | 212 | 4.36334634322e-05 | 0.510496821265 | pending | pending |
| `h_star_044` | idle_star | 212 | 4.36334634322e-05 | 0.510496821265 | pending | pending |
| `h_star_202` | idle_star | 212 | 4.36334634322e-05 | 0.510496821265 | pending | pending |
| `h_port_088` | guard_port | 212 | 4.36349189658e-05 | 0.504429240539 | pending | pending |
| `h_seed_guard_073` | seed_guard | 212 | 4.36412801988e-05 | 0.510326073812 | pending | pending |
| `h_star_404` | idle_star | 212 | 4.36412801988e-05 | 0.510326073812 | pending | pending |
| `h_port_073` | guard_port | 212 | 4.36427124772e-05 | 0.504260522504 | pending | pending |
| `h_seed_guard_120` | seed_guard | 212 | 4.36642028194e-05 | 0.507276683153 | pending | pending |
| `h_seed_guard_121` | seed_guard | 212 | 4.36644277133e-05 | 0.506771408063 | pending | pending |
| `h_port_120` | guard_port | 212 | 4.36655685705e-05 | 0.503919031316 | pending | pending |
| `h_port_121` | guard_port | 212 | 4.36657935364e-05 | 0.503417100629 | pending | pending |
| `h_port_075` | guard_port | 212 | 4.36834526136e-05 | 0.504700553814 | pending | pending |
| `h_port_090` | guard_port | 212 | 4.36834526136e-05 | 0.504700553814 | pending | pending |
| `h_port_081` | guard_port | 212 | 4.36889879547e-05 | 0.50470093055 | pending | pending |
| `h_port_096` | guard_port | 212 | 4.36889879547e-05 | 0.50470093055 | pending | pending |
| `h_port_080` | guard_port | 212 | 4.36893621532e-05 | 0.504429381765 | pending | pending |
| `h_port_095` | guard_port | 212 | 4.36893621532e-05 | 0.504429381765 | pending | pending |
| `h_star_250` | idle_star | 211 | 4.36957164331e-05 | 0.509615061282 | pending | pending |
| `h_star_255` | idle_star | 211 | 4.36957164331e-05 | 0.509105219651 | pending | pending |
| `h_star_205` | idle_star | 211 | 4.36958000575e-05 | 0.509615313792 | pending | pending |
| `h_star_525` | idle_star | 211 | 4.36958107489e-05 | 0.509104278788 | pending | pending |
| `h_star_552` | idle_star | 211 | 4.36958107492e-05 | 0.509104278788 | pending | pending |
| `h_star_520` | idle_star | 211 | 4.36958793655e-05 | 0.509613940734 | pending | pending |
| `h_star_200` | idle_star | 211 | 4.36958836818e-05 | 0.510126146041 | pending | pending |
| `h_star_502` | idle_star | 211 | 4.36958997567e-05 | 0.509613828082 | pending | pending |
| `h_star_025` | idle_star | 211 | 4.36959223223e-05 | 0.509614638333 | pending | pending |
| `h_star_052` | idle_star | 211 | 4.36959276314e-05 | 0.509613987927 | pending | pending |
| `h_star_020` | idle_star | 211 | 4.36960466877e-05 | 0.510125244604 | pending | pending |
| `h_star_002` | idle_star | 211 | 4.36961282116e-05 | 0.510124793773 | pending | pending |
| `h_seed_guard_103` | seed_guard | 212 | 4.37347263885e-05 | 0.508969225843 | pending | pending |
| `h_port_103` | guard_port | 212 | 4.37358269093e-05 | 0.504260090165 | pending | pending |
| `h_port_000` | guard_port | 212 | 4.37368601066e-05 | 0.504261170311 | pending | pending |
| `h_port_006` | guard_port | 212 | 4.37426623646e-05 | 0.504768310487 | pending | pending |
| `h_port_007` | guard_port | 212 | 4.37426623646e-05 | 0.504768310487 | pending | pending |
| `h_port_124` | guard_port | 212 | 4.37519247951e-05 | 0.502250724714 | pending | pending |
| `h_port_021` | guard_port | 212 | 4.37576291172e-05 | 0.499256926705 | pending | pending |
| `h_port_023` | guard_port | 212 | 4.37576291172e-05 | 0.499256926705 | pending | pending |
| `h_port_022` | guard_port | 212 | 4.37578784428e-05 | 0.498427744219 | pending | pending |
| `h_port_130` | guard_port | 212 | 4.37581172584e-05 | 0.499255502198 | pending | pending |
| `h_star_555` | idle_star | 210 | 4.37583721834e-05 | 0.508224912212 | pending | pending |
| `h_star_500` | idle_star | 210 | 4.37583721837e-05 | 0.509243568642 | pending | pending |
| `h_star_505` | idle_star | 210 | 4.37583721838e-05 | 0.508733872263 | pending | pending |
| `h_star_550` | idle_star | 210 | 4.37583721838e-05 | 0.508733872263 | pending | pending |
| `h_star_055` | idle_star | 210 | 4.37584891165e-05 | 0.508733741063 | pending | pending |
| `h_star_050` | idle_star | 210 | 4.37584891166e-05 | 0.509243210679 | pending | pending |
| `h_star_005` | idle_star | 210 | 4.3758606049e-05 | 0.509243305978 | pending | pending |
| `h_ST2_feedback` | population_seed | 210 | 4.37587229812e-05 | 0.507722961402 | pending | pending |
| `h_ST2_feedback_prep` | population_seed | 210 | 4.37587229813e-05 | 0.509753608149 | pending | pending |
| `h_seed_guard_118` | seed_guard | 212 | 4.3758791988e-05 | 0.505227026044 | pending | pending |
| `h_port_067` | guard_port | 210 | 4.37591140205e-05 | 0.507722160859 | pending | pending |
| `h_seed_guard_117` | seed_guard | 212 | 4.3759126614e-05 | 0.50388642793 | pending | pending |
| `h_port_066` | guard_port | 210 | 4.37591653757e-05 | 0.505030342064 | pending | pending |
| `h_port_123` | guard_port | 212 | 4.37593745201e-05 | 0.502419417813 | pending | pending |
| `h_port_107` | guard_port | 212 | 4.37594163167e-05 | 0.502252571719 | pending | pending |
| `h_port_018` | guard_port | 212 | 4.37594653522e-05 | 0.500087467815 | pending | pending |
| `h_port_020` | guard_port | 212 | 4.37594653522e-05 | 0.500087467815 | pending | pending |
| `h_port_105` | guard_port | 212 | 4.37595481002e-05 | 0.500088625894 | pending | pending |
| `h_port_019` | guard_port | 212 | 4.37597159875e-05 | 0.499260519994 | pending | pending |
| `h_port_004` | guard_port | 210 | 4.37597751142e-05 | 0.503525820139 | pending | pending |
| `h_port_001` | guard_port | 210 | 4.37597751145e-05 | 0.503191256172 | pending | pending |
| `h_port_005` | guard_port | 210 | 4.37598238575e-05 | 0.505037221697 | pending | pending |
| `h_port_129` | guard_port | 212 | 4.37598346955e-05 | 0.500588551107 | pending | pending |
| `h_port_003` | guard_port | 210 | 4.37598725026e-05 | 0.503525239796 | pending | pending |
| `h_port_104` | guard_port | 212 | 4.37598765742e-05 | 0.500422592785 | pending | pending |
| `h_port_059` | guard_port | 210 | 4.3759897782e-05 | 0.50285760469 | pending | pending |
| `h_port_046` | guard_port | 210 | 4.37599608862e-05 | 0.503862600839 | pending | pending |
| `h_port_002` | guard_port | 210 | 4.3759969891e-05 | 0.503525107627 | pending | pending |
| `h_port_052` | guard_port | 210 | 4.37600154445e-05 | 0.502859235082 | pending | pending |
| `h_port_039` | guard_port | 210 | 4.37600822753e-05 | 0.503023875731 | pending | pending |
| `h_port_065` | guard_port | 210 | 4.37601620531e-05 | 0.506379561683 | pending | pending |
| `h_port_024` | guard_port | 210 | 4.37601646662e-05 | 0.50268854391 | pending | pending |
| `h_port_026` | guard_port | 210 | 4.37601646662e-05 | 0.50268854391 | pending | pending |
| `h_port_140` | guard_port | 210 | 4.37601715257e-05 | 0.50035239493 | pending | pending |
| `h_port_133` | guard_port | 210 | 4.37602101952e-05 | 0.503022885705 | pending | pending |
| `h_prep_03` | prep_timing | 210 | 4.37602134081e-05 | 0.502690827994 | pending | pending |
| `h_prep_01` | prep_timing | 210 | 4.37602134081e-05 | 0.502022361348 | pending | pending |
| `h_prep_05` | prep_timing | 210 | 4.37602134082e-05 | 0.503025059234 | pending | pending |
| `h_prep_02` | prep_timing | 210 | 4.37602134082e-05 | 0.5023563717 | pending | pending |
| `h_prep_04` | prep_timing | 210 | 4.37602134083e-05 | 0.502690380565 | pending | pending |
| `h_prep_06` | prep_timing | 210 | 4.37602134085e-05 | 0.503359736711 | pending | pending |
| `h_prep_07` | prep_timing | 210 | 4.37602134086e-05 | 0.50369486102 | PASS / FAST | 4.401347e-05 |
| `h_port_053` | guard_port | 210 | 4.37602134086e-05 | 0.50369486102 | pending | pending |
| `h_port_060` | guard_port | 210 | 4.37602134086e-05 | 0.50369486102 | pending | pending |
| `h_port_138` | guard_port | 210 | 4.37602166146e-05 | 0.50352818384 | pending | pending |
| `h_port_030` | guard_port | 210 | 4.37602166903e-05 | 0.502857112328 | pending | pending |
| `h_port_118` | guard_port | 212 | 4.37602824342e-05 | 0.499222080233 | pending | pending |
| `h_port_040` | guard_port | 210 | 4.37603442779e-05 | 0.503528593111 | pending | pending |
| `h_port_031` | guard_port | 210 | 4.37603595367e-05 | 0.503193152598 | pending | pending |
| `h_port_029` | guard_port | 210 | 4.37604226517e-05 | 0.502858063655 | pending | pending |
| `h_omit_274` | omit | 210 | 4.37604754088e-05 | 0.50219323641 | pending | pending |
| `h_port_117` | guard_port | 212 | 4.37606171535e-05 | 0.497897415984 | pending | pending |
| `h_reset_181` | reset | 210 | 4.37607958479e-05 | 0.502525505028 | pending | pending |
| `h_reset_182` | reset | 210 | 4.37607958479e-05 | 0.502525505028 | pending | pending |
| `h_reset_188` | reset | 210 | 4.37608058527e-05 | 0.503194978208 | pending | pending |
| `h_reset_187` | reset | 210 | 4.37608058527e-05 | 0.502525841155 | pending | pending |
| `h_reset_186` | reset | 210 | 4.37608058529e-05 | 0.502525841155 | pending | pending |
| `h_port_032` | guard_port | 210 | 4.37608118537e-05 | 0.502857129215 | pending | pending |
| `h_det_55` | detector | 210 | 4.37608685351e-05 | 0.501695922283 | pending | pending |
| `h_port_033` | guard_port | 210 | 4.37611672553e-05 | 0.501521681707 | pending | pending |
| `h_port_028` | guard_port | 210 | 4.37611705374e-05 | 0.500687547462 | pending | pending |
| `h_port_110` | guard_port | 212 | 4.37613626479e-05 | 0.50055225091 | pending | pending |
| `h_port_111` | guard_port | 212 | 4.37613626479e-05 | 0.50055225091 | pending | pending |
| `h_port_109` | guard_port | 212 | 4.37613626482e-05 | 0.500719101326 | pending | pending |
| `h_omit_3` | omit | 210 | 4.37614195946e-05 | 0.502996338168 | pending | pending |
| `h_reset_3` | reset | 210 | 4.37614195946e-05 | 0.502996338168 | pending | pending |
| `h_det_03` | detector | 210 | 4.37614195948e-05 | 0.502996338168 | pending | pending |
| `h_omit_277` | omit | 210 | 4.37614746367e-05 | 0.502194353293 | pending | pending |
| `h_omit_271` | omit | 210 | 4.37614908479e-05 | 0.502525259187 | pending | pending |
| `h_reset_271` | reset | 210 | 4.37614908479e-05 | 0.502525259187 | pending | pending |
| `h_omit_276` | omit | 210 | 4.37617955055e-05 | 0.502195873818 | pending | pending |
| `h_reset_540` | reset | 210 | 4.37618739249e-05 | 0.502357899345 | pending | pending |
| `h_omit_181` | omit | 210 | 4.3761959557e-05 | 0.502191724222 | pending | pending |
| `h_omit_182` | omit | 210 | 4.3761959557e-05 | 0.502191724222 | pending | pending |
| `h_omit_186` | omit | 210 | 4.37619895493e-05 | 0.502192731259 | pending | pending |
| `h_omit_187` | omit | 210 | 4.37619895493e-05 | 0.502192731259 | pending | pending |
| `h_port_119` | guard_port | 212 | 4.37621707503e-05 | 0.498395875811 | pending | pending |
| `h_reset_185` | reset | 210 | 4.37622045756e-05 | 0.503528962474 | pending | pending |
| `h_reset_272` | reset | 210 | 4.37623197132e-05 | 0.502525374206 | pending | pending |
| `h_det_57` | detector | 210 | 4.37623889744e-05 | 0.50169751942 | pending | pending |
| `h_det_58` | detector | 210 | 4.37624208565e-05 | 0.501696189471 | pending | pending |
| `h_reset_183` | reset | 210 | 4.37625367474e-05 | 0.502525538674 | pending | pending |
| `h_reset_184` | reset | 210 | 4.37625367477e-05 | 0.502525538674 | pending | pending |
| `h_omit_264` | omit | 210 | 4.37632866742e-05 | 0.502190500646 | pending | pending |
| `h_det_41` | detector | 210 | 4.37634580756e-05 | 0.501688356178 | pending | pending |
| `h_omit_540` | omit | 210 | 4.3763531116e-05 | 0.502191023074 | pending | pending |
| `h_det_45` | detector | 210 | 4.37635583583e-05 | 0.501689491057 | pending | pending |
| `h_det_63` | detector | 210 | 4.3763705691e-05 | 0.501691720576 | pending | pending |
| `h_det_64` | detector | 210 | 4.3763705691e-05 | 0.501691720576 | pending | pending |
| `h_det_34` | detector | 210 | 4.37637656679e-05 | 0.501693732636 | pending | pending |
| `h_det_35` | detector | 210 | 4.37637656679e-05 | 0.501693732636 | pending | pending |
| `h_seed_joint_84_122_103_reset55` | guard_check_trade | 216 | 4.3763833187e-05 | 0.507860606916 | pending | pending |
| `h_omit_257` | omit | 210 | 4.37638932046e-05 | 0.502525723559 | pending | pending |
| `h_reset_257` | reset | 210 | 4.37638932046e-05 | 0.502525723559 | pending | pending |
| `h_omit_188` | omit | 210 | 4.37643569113e-05 | 0.502195651487 | pending | pending |
| `h_det_65` | detector | 210 | 4.3766132994e-05 | 0.50169731997 | pending | pending |
| `h_omit_272` | omit | 210 | 4.37665280958e-05 | 0.502191332282 | pending | pending |
| `h_omit_184` | omit | 210 | 4.37671787588e-05 | 0.502191825026 | pending | pending |
| `h_omit_183` | omit | 210 | 4.37671787588e-05 | 0.502191825026 | pending | pending |
| `h_det_52` | detector | 210 | 4.37678729005e-05 | 0.50169024897 | pending | pending |
| `h_det_62` | detector | 210 | 4.37685093128e-05 | 0.50169039337 | pending | pending |
| `h_reset_266` | reset | 210 | 4.37695215655e-05 | 0.502827786541 | pending | pending |
| `h_omit_266` | omit | 210 | 4.37695215656e-05 | 0.502827786541 | pending | pending |
| `h_det_47` | detector | 210 | 4.37695215659e-05 | 0.502827786541 | pending | pending |
| `h_omit_532` | omit | 210 | 4.37700562714e-05 | 0.504356521911 | pending | pending |
| `h_reset_532` | reset | 210 | 4.37700562714e-05 | 0.504356521911 | pending | pending |
| `h_det_61` | detector | 210 | 4.37700562715e-05 | 0.504356521911 | pending | pending |
| `h_det_53` | detector | 210 | 4.37728427385e-05 | 0.501690937479 | pending | pending |
| `h_det_33` | detector | 210 | 4.37741440456e-05 | 0.501691921981 | pending | pending |
| `h_det_36` | detector | 210 | 4.37741440456e-05 | 0.501691921981 | pending | pending |
| `h_omit_267` | omit | 210 | 4.37758752565e-05 | 0.502828142971 | pending | pending |
| `h_reset_267` | reset | 210 | 4.37758752565e-05 | 0.502828142971 | pending | pending |
| `h_det_48` | detector | 210 | 4.37758752567e-05 | 0.502828142971 | pending | pending |
| `h_reset_22` | reset | 210 | 4.37768874948e-05 | 0.502326546736 | pending | pending |
| `h_omit_22` | omit | 210 | 4.37768874948e-05 | 0.502326546736 | pending | pending |
| `h_port_043` | guard_port | 210 | 4.37773054914e-05 | 0.505534172431 | pending | pending |
| `h_omit_185` | omit | 210 | 4.37781178324e-05 | 0.502191890613 | pending | pending |
| `h_det_37` | detector | 210 | 4.37822772591e-05 | 0.501693028705 | pending | pending |
| `h_det_32` | detector | 210 | 4.3784087201e-05 | 0.50169215889 | pending | pending |
| `h_seed_guard_137` | seed_guard | 210 | 4.37851489495e-05 | 0.50958499245 | pending | pending |
| `h_seed_guard_136` | seed_guard | 210 | 4.37852506512e-05 | 0.509585229629 | pending | pending |
| `h_port_137` | guard_port | 210 | 4.37866411944e-05 | 0.503528249429 | pending | pending |
| `h_port_136` | guard_port | 210 | 4.37867420995e-05 | 0.503528483787 | pending | pending |
| `h_omit_26` | omit | 210 | 4.37882691074e-05 | 0.502327184588 | pending | pending |
| `h_reset_26` | reset | 210 | 4.37882691075e-05 | 0.502327184588 | pending | pending |
| `h_port_083` | guard_port | 212 | 4.37887420138e-05 | 0.504937945208 | pending | pending |
| `h_port_068` | guard_port | 212 | 4.37889740263e-05 | 0.504937277298 | pending | pending |
| `h_seed_guard_135` | seed_guard | 210 | 4.37975304388e-05 | 0.509584947222 | pending | pending |
| `h_port_135` | guard_port | 210 | 4.37990237123e-05 | 0.503528204759 | pending | pending |
| `h_port_035` | guard_port | 210 | 4.38061285762e-05 | 0.504198871106 | pending | pending |
| `h_port_036` | guard_port | 210 | 4.38061285762e-05 | 0.504198871106 | pending | pending |
| `h_reset_259` | reset | 210 | 4.38066825241e-05 | 0.502525327539 | pending | pending |
| `h_omit_259` | omit | 210 | 4.38066825244e-05 | 0.502525327539 | pending | pending |
| `h_port_079` | guard_port | 212 | 4.38104884392e-05 | 0.504763896826 | pending | pending |
| `h_port_094` | guard_port | 212 | 4.38104884392e-05 | 0.504763896826 | pending | pending |
| `h_reset_60` | reset | 210 | 4.38178614881e-05 | 0.502526683665 | pending | pending |
| `h_reset_180` | reset | 210 | 4.38182185798e-05 | 0.5028610193 | pending | pending |
| `h_port_008` | guard_port | 212 | 4.38200184163e-05 | 0.504763899515 | pending | pending |
| `h_port_009` | guard_port | 212 | 4.38200184163e-05 | 0.504763899515 | pending | pending |
| `h_port_010` | guard_port | 212 | 4.38200184163e-05 | 0.504763899515 | pending | pending |
| `h_port_063` | guard_port | 210 | 4.38259203682e-05 | 0.504195865709 | pending | pending |
| `h_port_062` | guard_port | 210 | 4.38259203683e-05 | 0.503860520071 | pending | pending |
| `h_port_056` | guard_port | 210 | 4.38262099875e-05 | 0.504197573381 | pending | pending |
| `h_port_055` | guard_port | 210 | 4.38262099882e-05 | 0.503862675078 | pending | pending |
| `h_reset_263` | reset | 210 | 4.38276051445e-05 | 0.502499665418 | pending | pending |
| `h_reset_270` | reset | 210 | 4.38303705234e-05 | 0.502692403806 | pending | pending |
| `h_omit_261` | omit | 210 | 4.38515481317e-05 | 0.502525296404 | pending | pending |
| `h_reset_261` | reset | 210 | 4.38515481317e-05 | 0.502525296404 | pending | pending |
| `h_port_034` | guard_port | 210 | 4.38521345327e-05 | 0.504703781409 | pending | pending |
| `h_port_037` | guard_port | 210 | 4.38521345327e-05 | 0.504703781409 | pending | pending |
| `h_Cuncopy_28_29` | readout | 209 | 4.38631763019e-05 | 0.506119357213 | pending | pending |
| `h_reset_269` | reset | 210 | 4.38749339439e-05 | 0.503361605722 | pending | pending |
| `h_reset_264` | reset | 210 | 4.38853990736e-05 | 0.502730270982 | pending | pending |
| `h_omit_263` | omit | 210 | 4.38960821547e-05 | 0.50219722224 | pending | pending |
| `h_C_uncopy` | readout | 208 | 4.38974706399e-05 | 0.506524536003 | pending | pending |
| `h_omit_258` | omit | 210 | 4.39020955355e-05 | 0.502525783402 | pending | pending |
| `h_reset_258` | reset | 210 | 4.39020955355e-05 | 0.502525783402 | pending | pending |
| `h_omit_54` | omit | 210 | 4.3906012807e-05 | 0.502328159484 | pending | pending |
| `h_reset_54` | reset | 210 | 4.3906012807e-05 | 0.502328159484 | pending | pending |
| `h_det_24` | detector | 210 | 4.39060128072e-05 | 0.502328159484 | pending | pending |
| `h_reset_56` | reset | 210 | 4.39071849052e-05 | 0.502161229778 | pending | pending |
| `h_omit_60` | omit | 210 | 4.39330410405e-05 | 0.502195255419 | pending | pending |
| `h_omit_0` | omit | 210 | 4.39453692581e-05 | 0.502709041936 | pending | pending |
| `h_reset_0` | reset | 210 | 4.39453692581e-05 | 0.502709041936 | pending | pending |
| `h_det_00` | detector | 210 | 4.39453692582e-05 | 0.502709041936 | pending | pending |
| `h_det_23` | detector | 210 | 4.39533010394e-05 | 0.501689267221 | pending | pending |
| `h_reset_55` | reset | 210 | 4.39605596555e-05 | 0.503168835516 | pending | pending |
| `h_omit_528` | omit | 210 | 4.39751789881e-05 | 0.504186267213 | pending | pending |
| `h_reset_528` | reset | 210 | 4.39751789881e-05 | 0.504186267213 | pending | pending |
| `h_det_60` | detector | 210 | 4.39751789882e-05 | 0.504186267213 | pending | pending |
| `h_det_49` | detector | 210 | 4.39818947606e-05 | 0.502828044189 | pending | pending |
| `h_omit_268` | omit | 210 | 4.39818947606e-05 | 0.502828044189 | pending | pending |
| `h_reset_268` | reset | 210 | 4.39818947606e-05 | 0.502828044189 | pending | pending |
| `h_det_44` | detector | 210 | 4.39998345705e-05 | 0.501696452808 | pending | pending |
| `h_seed_guard_141` | seed_guard | 208 | 4.40064799597e-05 | 0.512245314081 | pending | pending |
| `h_port_141` | guard_port | 208 | 4.40079824324e-05 | 0.506156951447 | pending | pending |
| `h_Cuncopy_29_28` | readout | 209 | 4.40260025455e-05 | 0.50611927863 | pending | pending |
| `h_port_048` | guard_port | 210 | 4.4028505364e-05 | 0.504198872164 | pending | pending |
| `h_port_049` | guard_port | 210 | 4.4028505364e-05 | 0.504198872164 | pending | pending |
| `h_det_39` | detector | 210 | 4.40388406955e-05 | 0.501690658129 | pending | pending |
| `h_omit_270` | omit | 210 | 4.4040560351e-05 | 0.502191247039 | pending | pending |
| `h_omit_180` | omit | 210 | 4.40500033838e-05 | 0.502197229997 | pending | pending |
| `h_reset_265` | reset | 210 | 4.40678793706e-05 | 0.502828135557 | pending | pending |
| `h_omit_265` | omit | 210 | 4.40678793707e-05 | 0.502828135557 | pending | pending |
| `h_det_46` | detector | 210 | 4.40678793708e-05 | 0.502828135557 | pending | pending |
| `h_port_072` | guard_port | 212 | 4.40867937396e-05 | 0.505101307535 | pending | pending |
| `h_port_011` | guard_port | 212 | 4.40874544885e-05 | 0.504697982633 | pending | pending |
| `h_port_012` | guard_port | 212 | 4.40874544886e-05 | 0.504697982633 | pending | pending |
| `h_port_087` | guard_port | 212 | 4.4090094161e-05 | 0.505099976715 | pending | pending |
| `h_port_057` | guard_port | 210 | 4.40906471831e-05 | 0.506217404064 | pending | pending |
| `h_port_054` | guard_port | 210 | 4.40906471835e-05 | 0.504540681709 | pending | pending |
| `h_det_28` | detector | 210 | 4.41058647346e-05 | 0.501698775906 | pending | pending |
| `h_omit_273` | omit | 210 | 4.41068580367e-05 | 0.503339938094 | pending | pending |
| `h_reset_273` | reset | 210 | 4.41068580367e-05 | 0.503339938094 | pending | pending |
| `h_det_54` | detector | 210 | 4.41068580368e-05 | 0.503339938094 | pending | pending |
| `h_reset_57` | reset | 210 | 4.41176232473e-05 | 0.502167227092 | pending | pending |
| `h_port_076` | guard_port | 212 | 4.41279501156e-05 | 0.504762852619 | pending | pending |
| `h_port_091` | guard_port | 212 | 4.41279501156e-05 | 0.504762852619 | pending | pending |
| `h_port_142` | guard_port | 208 | 4.41389311558e-05 | 0.505374950052 | pending | pending |
| `h_reset_274` | reset | 210 | 4.41494331143e-05 | 0.506059215046 | pending | pending |
| `h_omit_27` | omit | 210 | 4.4157320196e-05 | 0.502327007811 | pending | pending |
| `h_reset_27` | reset | 210 | 4.41573201962e-05 | 0.502327007811 | pending | pending |
| `h_port_061` | guard_port | 210 | 4.42211406589e-05 | 0.504868640727 | pending | pending |
| `h_port_064` | guard_port | 210 | 4.4221140659e-05 | 0.507220718162 | pending | pending |
| `h_det_31` | detector | 210 | 4.42238957419e-05 | 0.501700383482 | pending | pending |
| `h_det_51` | detector | 210 | 4.42508891438e-05 | 0.501690758183 | pending | pending |
| `h_port_047` | guard_port | 210 | 4.42969771737e-05 | 0.504703781289 | pending | pending |
| `h_port_050` | guard_port | 210 | 4.42969771737e-05 | 0.504703781289 | pending | pending |
| `h_det_40` | detector | 210 | 4.43078535662e-05 | 0.501690471753 | pending | pending |
| `h_omit_23` | omit | 210 | 4.43113478332e-05 | 0.50232717132 | pending | pending |
| `h_reset_23` | reset | 210 | 4.43113478334e-05 | 0.50232717132 | pending | pending |
| `h_port_086` | guard_port | 212 | 4.43150380837e-05 | 0.504846443535 | pending | pending |
| `h_reset_276` | reset | 210 | 4.43501748556e-05 | 0.50401960061 | pending | pending |
| `h_port_144` | guard_port | 208 | 4.43702007069e-05 | 0.509540130481 | pending | pending |
| `h_omit_10` | omit | 210 | 4.4387549715e-05 | 0.504178368224 | pending | pending |
| `h_reset_10` | reset | 210 | 4.4387549715e-05 | 0.504178368224 | pending | pending |
| `h_det_10` | detector | 210 | 4.4387549715e-05 | 0.504178368224 | pending | pending |
| `h_omit_2` | omit | 210 | 4.44635982951e-05 | 0.502677649873 | pending | pending |
| `h_reset_2` | reset | 210 | 4.44635982951e-05 | 0.502677649873 | pending | pending |
| `h_det_02` | detector | 210 | 4.44635982952e-05 | 0.502677649873 | pending | pending |
| `h_omit_275` | omit | 210 | 4.45142974628e-05 | 0.503164291445 | pending | pending |
| `h_reset_275` | reset | 210 | 4.45142974628e-05 | 0.503164291445 | pending | pending |
| `h_det_56` | detector | 210 | 4.45142974632e-05 | 0.503164291445 | pending | pending |
| `h_port_074` | guard_port | 212 | 4.45385283201e-05 | 0.504897612605 | pending | pending |
| `h_port_089` | guard_port | 212 | 4.45385283201e-05 | 0.504897612605 | pending | pending |
| `h_det_38` | detector | 210 | 4.46109301056e-05 | 0.501693386926 | pending | pending |
| `h_port_143` | guard_port | 208 | 4.46207300063e-05 | 0.505647823893 | pending | pending |
| `h_det_11` | detector | 210 | 4.46714613619e-05 | 0.504176041838 | pending | pending |
| `h_omit_11` | omit | 210 | 4.46714613619e-05 | 0.504176041838 | pending | pending |
| `h_reset_11` | reset | 210 | 4.46714613619e-05 | 0.504176041838 | pending | pending |
| `h_omit_269` | omit | 210 | 4.46770520251e-05 | 0.50219248687 | pending | pending |
| `h_reset_277` | reset | 210 | 4.46992294276e-05 | 0.504877311904 | pending | pending |
| `h_port_145` | guard_port | 208 | 4.47001411084e-05 | 0.511405895319 | pending | pending |
| `h_port_051` | guard_port | 210 | 4.48233876173e-05 | 0.503884436607 | pending | pending |
| `h_port_045` | guard_port | 210 | 4.48371229316e-05 | 0.503697487918 | pending | pending |
| `h_det_42` | detector | 210 | 4.49400343047e-05 | 0.501690455393 | pending | pending |
| `h_det_50` | detector | 210 | 4.50209755272e-05 | 0.501692866598 | pending | pending |
| `h_port_071` | guard_port | 212 | 4.51057011358e-05 | 0.504931586001 | pending | pending |
| `h_port_093` | guard_port | 212 | 4.51351161516e-05 | 0.504692067069 | pending | pending |
| `h_det_43` | detector | 210 | 4.51608182328e-05 | 0.50169091177 | pending | pending |
| `h_port_097` | guard_port | 212 | 4.5230080833e-05 | 0.504696904027 | pending | pending |
| `h_port_078` | guard_port | 212 | 4.52710150279e-05 | 0.504695173502 | pending | pending |
| `h_port_082` | guard_port | 212 | 4.5308362941e-05 | 0.504697870776 | pending | pending |
| `h_omit_56` | omit | 210 | 4.53352207136e-05 | 0.502193886093 | pending | pending |
| `h_det_26` | detector | 210 | 4.54096691842e-05 | 0.501696134432 | pending | pending |
| `h_port_058` | guard_port | 210 | 4.54753691665e-05 | 0.503897196148 | pending | pending |
| `h_omit_5` | omit | 210 | 4.55251290274e-05 | 0.50437707593 | pending | pending |
| `h_reset_5` | reset | 210 | 4.55251290274e-05 | 0.50437707593 | pending | pending |
| `h_det_05` | detector | 210 | 4.55251290274e-05 | 0.50437707593 | pending | pending |
| `h_omit_1` | omit | 210 | 4.61529895924e-05 | 0.502880351681 | pending | pending |
| `h_reset_1` | reset | 210 | 4.61529895924e-05 | 0.502880351681 | pending | pending |
| `h_det_01` | detector | 210 | 4.61529895926e-05 | 0.502880351681 | pending | pending |
| `h_port_077` | guard_port | 212 | 4.61677114514e-05 | 0.504928550453 | pending | pending |
| `h_port_092` | guard_port | 212 | 4.61766870706e-05 | 0.504929423274 | pending | pending |
| `h_star_111_joint_122_103_reset55` | guard_check_trade | 217 | 4.62374731627e-05 | 0.508158990112 | pending | pending |
| `h_star_111_reset55` | guard_check_trade | 213 | 4.6522701206e-05 | 0.511423559182 | pending | pending |
| `h_star_111_joint_122_103_omit55` | guard_check_trade | 217 | 4.6710958199e-05 | 0.508125286081 | pending | pending |
| `h_star_111_omit55` | guard_check_trade | 213 | 4.6986435582e-05 | 0.511389628109 | pending | pending |
| `h_omit_7` | omit | 210 | 4.71184796135e-05 | 0.511493004114 | pending | pending |
| `h_reset_7` | reset | 210 | 4.72625958586e-05 | 0.502403664843 | pending | pending |
| `h_det_21` | detector | 210 | 4.76157550247e-05 | 0.501695480681 | pending | pending |
| `h_omit_6` | omit | 210 | 4.82948333652e-05 | 0.502297824734 | pending | pending |
| `h_reset_6` | reset | 210 | 4.82948333652e-05 | 0.502297824734 | pending | pending |
| `h_det_06` | detector | 210 | 4.82948333657e-05 | 0.502297824734 | pending | pending |
| `h_omit_12` | omit | 210 | 4.84622383078e-05 | 0.504019796233 | pending | pending |
| `h_reset_12` | reset | 210 | 4.84622383078e-05 | 0.504019796233 | pending | pending |
| `h_det_12` | detector | 210 | 4.84622383081e-05 | 0.504019796233 | pending | pending |
| `h_omit_9` | omit | 210 | 4.87445114806e-05 | 0.503106476 | pending | pending |
| `h_reset_9` | reset | 210 | 4.87445114806e-05 | 0.503106476 | pending | pending |
| `h_det_09` | detector | 210 | 4.87445114807e-05 | 0.503106476 | pending | pending |
| `h_omit_13` | omit | 210 | 4.88283573399e-05 | 0.502976431741 | pending | pending |
| `h_reset_13` | reset | 210 | 4.88283573399e-05 | 0.502976431741 | pending | pending |
| `h_det_13` | detector | 210 | 4.88283573402e-05 | 0.502976431741 | pending | pending |
| `h_omit_55` | omit | 210 | 4.88366810281e-05 | 0.502836871939 | pending | pending |
| `h_det_25` | detector | 210 | 4.8908444535e-05 | 0.502339091612 | pending | pending |
| `h_omit_21` | omit | 210 | 4.99776753068e-05 | 0.503098806632 | pending | pending |
| `h_reset_21` | reset | 210 | 4.9977675307e-05 | 0.503098806632 | pending | pending |
| `h_seed_joint_84_122_103_omit55` | guard_check_trade | 216 | 5.01765874548e-05 | 0.508395311151 | pending | pending |
| `h_omit_16` | omit | 210 | 5.10265932903e-05 | 0.502615134189 | pending | pending |
| `h_det_59` | detector | 210 | 5.10265932904e-05 | 0.502615134189 | pending | pending |
| `h_reset_16` | reset | 210 | 5.10265932904e-05 | 0.502615134189 | pending | pending |
| `h_omit_8` | omit | 210 | 5.12789388176e-05 | 0.502913807494 | pending | pending |
| `h_reset_8` | reset | 210 | 5.12789388176e-05 | 0.502913807494 | pending | pending |
| `h_det_08` | detector | 210 | 5.12789388176e-05 | 0.502913807494 | pending | pending |
| `h_reset_24` | reset | 210 | 5.18930277061e-05 | 0.502344919426 | pending | pending |
| `h_omit_24` | omit | 210 | 5.18930277062e-05 | 0.502344919426 | pending | pending |
| `h_omit_57` | omit | 210 | 5.31952946726e-05 | 0.502206720619 | pending | pending |
| `h_det_27` | detector | 210 | 5.32420789335e-05 | 0.501708032715 | pending | pending |
| `h_omit_64` | omit | 210 | 5.41882306097e-05 | 0.50245443789 | pending | pending |
| `h_reset_64` | reset | 210 | 5.41882306097e-05 | 0.50245443789 | pending | pending |
| `h_det_29` | detector | 210 | 5.41882306102e-05 | 0.50245443789 | pending | pending |
| `h_omit_25` | omit | 210 | 5.64194312741e-05 | 0.504025462285 | pending | pending |
| `h_reset_25` | reset | 210 | 5.64194312743e-05 | 0.504025462285 | pending | pending |
| `h_omit_67` | omit | 210 | 6.35289859828e-05 | 0.502906263357 | pending | pending |
| `h_reset_67` | reset | 210 | 6.35289859828e-05 | 0.502906263357 | pending | pending |
| `h_det_30` | detector | 210 | 6.35289859829e-05 | 0.502906263357 | pending | pending |
| `h_omit_4` | omit | 210 | 6.39484124845e-05 | 0.502405910149 | pending | pending |
| `h_reset_4` | reset | 210 | 6.39484124845e-05 | 0.502405910149 | pending | pending |
| `h_det_04` | detector | 210 | 6.39484124845e-05 | 0.502405910149 | pending | pending |
| `h_det_14` | detector | 210 | 8.99255929395e-05 | 0.505060440907 | pending | pending |
| `h_det_07` | detector | 210 | 9.15170237843e-05 | 0.502593001834 | pending | pending |
| `h_Cadd_28_29` | readout | 211 | 9.26483420143e-05 | 0.503292110548 | pending | pending |
| `h_Cadd_29_28` | readout | 211 | 9.26487080629e-05 | 0.50329211037 | pending | pending |
| `h_det_20` | detector | 210 | 0.000115423263014 | 0.501866631342 | pending | pending |
| `h_det_16` | detector | 210 | 0.000117397807868 | 0.505989219474 | pending | pending |
| `h_det_17` | detector | 210 | 0.000122206698332 | 0.50619685092 | pending | pending |
| `h_det_18` | detector | 210 | 0.000158992476987 | 0.506063554277 | pending | pending |
| `h_Aold_06` | readout | 212 | 0.000162220440752 | 0.501938633987 | pending | pending |
| `h_Aold_07` | readout | 212 | 0.000162220440752 | 0.501938633987 | pending | pending |
| `h_Aold_04` | readout | 212 | 0.00016224013346 | 0.501939501694 | pending | pending |
| `h_Aold_05` | readout | 212 | 0.00016224013346 | 0.501939501694 | pending | pending |
| `h_det_15` | detector | 210 | 0.000205168196832 | 0.505536479367 | pending | pending |
| `h_Anew_02` | readout | 213 | 0.000252526530218 | 0.500605931454 | pending | pending |
| `h_Anew_03` | readout | 213 | 0.000252526530218 | 0.500605931454 | pending | pending |
| `h_Anew_04` | readout | 213 | 0.000252526530218 | 0.500605931454 | pending | pending |
| `h_Anew_05` | readout | 213 | 0.000252526530218 | 0.500605931454 | pending | pending |
| `h_Anew_00` | readout | 213 | 0.000252527197686 | 0.500606501613 | pending | pending |
| `h_Anew_01` | readout | 213 | 0.000252527197686 | 0.500606501613 | pending | pending |
| `h_Anew_06` | readout | 213 | 0.000252527197686 | 0.500606501613 | pending | pending |
| `h_Anew_07` | readout | 213 | 0.000252527197686 | 0.500606501613 | pending | pending |
| `h_Aold_10` | readout | 212 | 0.000255618639898 | 0.4999406179 | pending | pending |
| `h_Aold_11` | readout | 212 | 0.000255618639898 | 0.4999406179 | pending | pending |
| `h_Aold_00` | readout | 212 | 0.000255660234553 | 0.499942214627 | pending | pending |
| `h_Aold_01` | readout | 212 | 0.000255660234553 | 0.499942214627 | pending | pending |
| `h_Aold_08` | readout | 212 | 0.000255701229864 | 0.499941866514 | pending | pending |
| `h_Aold_09` | readout | 212 | 0.000255701229864 | 0.499941866514 | pending | pending |
| `h_Aold_02` | readout | 212 | 0.000255721468446 | 0.499942597846 | pending | pending |
| `h_Aold_03` | readout | 212 | 0.000255721468446 | 0.499942597846 | pending | pending |
| `h_det_22` | detector | 210 | 0.000280052332544 | 0.501929926556 | pending | pending |
| `h_det_19` | detector | 210 | 0.00041193176485 | 0.50556390274 | pending | pending |
| `h_port_038` | guard_port | 210 | pending | pending | AssertionError('detector 20 not deterministic: 0.0') | pending |
| `h_port_041` | guard_port | 210 | pending | pending | AssertionError('detector 20 not deterministic: 0.0') | pending |
| `h_port_044` | guard_port | 210 | pending | pending | AssertionError('detector 20 not deterministic: 0.0') | pending |
| `h_star_003` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_004` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_013` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_014` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_023` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_024` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_030` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_031` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_032` | idle_star | 212 | pending | pending | AssertionError('detector 19 not deterministic: 0.0') | pending |
| `h_star_034` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_035` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_040` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_041` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_042` | idle_star | 212 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_043` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_045` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_053` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_054` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_103` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_104` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_113` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_114` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_123` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_124` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_130` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_131` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_132` | idle_star | 213 | pending | pending | AssertionError('detector 19 not deterministic: 0.0') | pending |
| `h_star_134` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_135` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_140` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_141` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_142` | idle_star | 213 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_143` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_145` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_153` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_154` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_203` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_204` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_213` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_214` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_223` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_224` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_230` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_231` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_232` | idle_star | 213 | pending | pending | AssertionError('detector 19 not deterministic: 0.0') | pending |
| `h_star_234` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_235` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_240` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_241` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_242` | idle_star | 213 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_243` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_245` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_253` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_254` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_300` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_301` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_302` | idle_star | 212 | pending | pending | AssertionError('detector 19 not deterministic: 0.0') | pending |
| `h_star_304` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_305` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_310` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_311` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_312` | idle_star | 213 | pending | pending | AssertionError('detector 16 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_313` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_314` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -1.9510990197797354e-16') | pending |
| `h_star_315` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_320` | idle_star | 212 | pending | pending | AssertionError('detector 19 not deterministic: 0.0') | pending |
| `h_star_321` | idle_star | 213 | pending | pending | AssertionError('detector 16 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_322` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_323` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_324` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_325` | idle_star | 212 | pending | pending | AssertionError('detector 19 not deterministic: 0.0') | pending |
| `h_star_333` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_334` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_340` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_341` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -2.2204460492503146e-16') | pending |
| `h_star_342` | idle_star | 213 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_343` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_344` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_345` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_350` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_351` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_352` | idle_star | 212 | pending | pending | AssertionError('detector 19 not deterministic: 0.0') | pending |
| `h_star_353` | idle_star | 212 | pending | pending | AssertionError('detector 19 not deterministic: 0.0') | pending |
| `h_star_354` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_355` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_400` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_401` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_402` | idle_star | 212 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_403` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_405` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_410` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_411` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_412` | idle_star | 213 | pending | pending | AssertionError('detector 16 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_413` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 9.664620247661655e-19') | pending |
| `h_star_414` | idle_star | 213 | pending | pending | AssertionError('detector 16 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_415` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_420` | idle_star | 212 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_421` | idle_star | 213 | pending | pending | AssertionError('detector 16 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_422` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_423` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_424` | idle_star | 213 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_425` | idle_star | 212 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_430` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_431` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: -2.2204460492503146e-16') | pending |
| `h_star_432` | idle_star | 213 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_433` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_434` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_435` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_443` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_444` | idle_star | 213 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_450` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_451` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_452` | idle_star | 212 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_453` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_454` | idle_star | 212 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_455` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_503` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_504` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_513` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_514` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_523` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_524` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_530` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_531` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -8.309290850140435e-18') | pending |
| `h_star_532` | idle_star | 212 | pending | pending | AssertionError('detector 19 not deterministic: 0.0') | pending |
| `h_star_534` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_535` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_540` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_541` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -2.7755575615628926e-17') | pending |
| `h_star_542` | idle_star | 212 | pending | pending | AssertionError('detector 18 not deterministic: 0.0') | pending |
| `h_star_543` | idle_star | 212 | pending | pending | AssertionError('detector 15 not deterministic: -1.450576286728263e-16') | pending |
| `h_star_545` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_553` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |
| `h_star_554` | idle_star | 211 | pending | pending | AssertionError('detector 15 not deterministic: 0.0') | pending |

## Verified acceptance timing

`h_prep_07` delays RX q1 from t38 to t39 before MX c180 at t40, RX q4 from t2 to t4 before MX c188 at t5, and RX q6 from t9 to t12 before MX c185 at t13. No interactions occur in these intervals. The accepted post-MX state is unchanged; the changes remove only preparation idle noise from the check likelihood. The joint recovers **0.00200651121430** acceptance, from **0.501688349806** to **0.503694861020**, with unchanged all-orders conditional loss. See `v35_prep_certificate.json`. These are timing changes, not detector deletions.

All 66 detector-only removals have been priced by ST2’s exact reverse-contraction marginal algorithm (only imports relocated); none preserves loss within 1e-15. Three direct whole-circuit confirmations match the reverse-contraction prices; see v35_marginal_validation.json. All 120 physical omission/reset variants of the 60 known-zero readouts are also priced. None qualifies as an acceptance-only removal at the requested 1e-15 tolerance. c43 is already absent from v35b. The exact recovered budget above is a reset-timing result, not a deletion claim.

The WAITPROT guard276/guard277 reset omissions (`h_port_053`, `h_port_060`) exactly match their parent `h_prep_07` in both loss and acceptance. They remove redundant explicit first-use Z resets, but recover **zero additional acceptance**; their parent’s timing gain is not attributed to the omissions.


Earlier rounds are archived in REPORT_v34m.md, REPORT_v30f.md and REPORT_v29c.md. No credentials, submissions, commits, pushes or collaboration tools are used.

Best finalist: **h_star_111_joint_122_103**.
