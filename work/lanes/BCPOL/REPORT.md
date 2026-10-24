# BCPOL — v35a B/C resource search

Status: ACTIVE — wider joint encoder/transfer and acceptance-budget searches; completed prices are listed below.

## Finalists below v35a — judge, FAST and MC3 passed

| Stem (`v35/finalists/`) | All-orders 1−F | Δ1−F vs v35a | Acceptance | Judge / FAST | s per 1e6 | MC 0 / 1000 / 2000 | MC mean |
|---|---:|---:|---:|---|---:|---|---:|
| `outer_extend` | 4.37480577931e-05 | -1.87219e-07 | 0.5005058231 | PASS / FAST | 3.4 (jerry) | 4.476147e-05 / 4.458626e-05 / 4.470433e-05 | 4.468402e-05 |
| `fresh_finish_reverse` | 4.377101217416e-05 | -1.642646e-07 | 0.50067078776 | PASS / FAST | 2.8 (hippo) | 4.520521e-05 / 4.242432e-05 / 4.359626e-05 | 4.374193e-05 |
| `sat_3511_exterior_000004` | 4.393028392368e-05 | -4.992837e-09 | 0.50124147912 | PASS / FAST | 4.6 (hippo) | 4.425358e-05 / 4.34746e-05 / 4.393879e-05 | 4.388899e-05 |

Best complete circuit in this campaign: `v35/finalists/outer_extend`. Exact CLI status: completed and agrees with the independent vector contraction. Second 3.812122791415e-05 + third 5.387985507819e-06 = 4.350921342197e-05; exp(−A1)=0.50069572924; ΔA1=+0.00141861406.

## Baseline and scope

Frozen `v35/inputs/v35a`: all-orders **4.39352767604208e-05**, acceptance **0.50123693862422**, 206 CX, R44, native depth47 (ticks0–46). Its independently reproduced third-order loss is 4.3677625703385e-05, exp(−A1)=0.501406527295. The budget is all-orders acceptance ≥0.5005; judge seed-0 acceptance must independently pass0.5. Ranking uses all-orders; MC remains a cross-check.

The first fully re-priced B/C improvement, `sat_3511_exterior_000004`, reverses only CX13→19 at t34 to CX19→13. Both inputs are ideally zero, so the ideal resource is unchanged. It scores4.393028392367847e-5, acceptance.501241479120574: Δloss=−4.99283674231e-9 and Δacceptance=+4.5404963534e-6. Deleting that CX instead scores4.39372052432986e-5; the direction controls how two-fault combinations reach the q13 flag and the boundary. The full prices establish the gain; the detailed pair attribution is not isolated.

FRESH owns the whole-circuit timing coordinates and SX/echo search. Its completed timing schedule frees acceptance (4.39321315046e-5/.513033240437); `finish_long` is a separately verified4.37759843683e-5/.500670701215 circuit. Our ports preserve those exterior changes and identify the B/C contribution separately. COMP29 owns terminal decoder constructions. Its geometric certificate excludes a new B Z flag made from only1–3 nearest-neighbor terminal CXs on the unchanged B geometry; we reuse that exclusion and its detector-conjugation construction.

## Full all-orders prices

These rows are full evaluator prices, not claims of completed MC gates. ΔA1 is available where the independent cubic screen is valid. Finalists above also have judge1e6, XTIM FAST, exact CLI and three100M-shot seeds.

| Stem | All-orders 1−F | Δ1−F | Acceptance | ΔA1 | Status |
|---|---:|---:|---:|---:|---|
| `outer_extend` | 4.37480577931e-05 | -1.87219e-07 | 0.5005058231 | +0.001418614 | VERIFIED_FINALIST |
| `nested_extend_fuse_r12_fixed` | 4.37486445072e-05 | -1.86632e-07 | 0.50084232 | — | below v35a; gates pending |
| `nested_extend_fuse_r12_23_fixed` | 4.37523958426e-05 | -1.82881e-07 | 0.5016783266 | — | below v35a; gates pending |
| `fresh_finish_bcopt` | 4.37663179891e-05 | -1.68959e-07 | 0.5010048018 | — | below v35a; gates pending |
| `fusion_only_r12_fixed` | 4.37676092903e-05 | -1.67667e-07 | 0.5015079027 | — | below v35a; gates pending |
| `fresh_finish_reverse` | 4.37710121742e-05 | -1.64265e-07 | 0.5006707878 | +0.001097169 | VERIFIED_FINALIST |
| `fusion_only_r12_23_fixed` | 4.37713606859e-05 | -1.63916e-07 | 0.5023450202 | — | below v35a; gates pending |
| `fresh_echo_bcopt` | 4.37845779651e-05 | -1.50699e-07 | 0.5025048425 | — | below v35a; gates pending |
| `fresh_echo_reverse` | 4.37892717376e-05 | -1.46005e-07 | 0.5021698284 | — | below v35a; gates pending |
| `joint_3612_000033` | 4.39224655888e-05 | -1.28112e-08 | 0.5133755907 | — | below v35a; gates pending |
| `v35_bcopt` | 4.39255594224e-05 | -9.71734e-09 | 0.504244798 | — | below v35a; gates pending |
| `fresh_timing_reverse` | 4.39271564493e-05 | -8.12031e-09 | 0.5130333291 | — | below v35a; gates pending |
| `relaxed_3514_exterior_000004` | 4.39302839237e-05 | -4.99284e-09 | 0.5012414791 | -0 | below v35a; gates pending |
| `sat_3511_exterior_000004` | 4.39302839237e-05 | -4.99284e-09 | 0.5012414791 | -0 | VERIFIED_FINALIST |
| `joint_3618_000015` | 4.39307915544e-05 | -4.48521e-09 | 0.5137859801 | — | below v35a; gates pending |
| `flex_control_q13_t25` | 4.3932182892e-05 | -3.09387e-09 | 0.5103132654 | — | below v35a; gates pending |
| `init_19_measure` | 4.39336151763e-05 | -1.66158e-09 | 0.5005688831 | +0.001333333 | below v35a; gates pending |
| `joint_3613_exterior_000003` | 4.39343936586e-05 | -8.83102e-10 | 0.5126920445 | -0.02259569 | below v35a; gates pending |
| `init_13_measure` | 4.39352735453e-05 | -3.21511e-12 | 0.5005682423 | +0.001333333 | below v35a; gates pending |
| `copy25_to24` | 4.39352767604e-05 | +0 | 0.5012369386 | — | priced |
| `joint_3622_exterior_000109` | 4.3936467487e-05 | +1.19073e-09 | 0.5111930159 | -0.01966236 | priced |
| `init_12_reset` | 4.39365966654e-05 | +1.3199e-09 | 0.5020730951 | -0.001666667 | priced |
| `delete_cx_185` | 4.39372052433e-05 | +1.92848e-09 | 0.5009770059 | — | priced |
| `relaxed_3514_exterior_000002` | 4.39372052433e-05 | +1.92848e-09 | 0.5009770059 | +0.0005182979 | priced |
| `sat_3512_exterior_000004` | 4.39372052433e-05 | +1.92848e-09 | 0.5009770059 | +0.0005182979 | priced |
| `init_23_reset` | 4.39389592234e-05 | +3.68246e-09 | 0.5020735589 | -0.001666667 | priced |
| `joint_3619_exterior_000010` | 4.39395328294e-05 | +4.25607e-09 | 0.5113301665 | -0.01993435 | priced |
| `flex_control_q12_t32` | 4.39453041474e-05 | +1.00274e-08 | 0.5113309099 | — | priced |
| `ro_02_none` | 4.39458698496e-05 | +1.05931e-08 | 0.5023085074 | -0.002133333 | priced |
| `joint_3621_exterior_000008` | 4.39497117353e-05 | +1.4435e-08 | 0.5092261431 | -0.01581609 | priced |
| `ro_03_19-25` | 4.39500058827e-05 | +1.47291e-08 | 0.5036503029 | -0.0048 | priced |
| `ro_04_none` | 4.39525995771e-05 | +1.73228e-08 | 0.5023089006 | -0.002133333 | priced |
| `init_28_reset` | 4.39617447231e-05 | +2.6468e-08 | 0.5010711401 | +0.0003333333 | priced |
| `init_17_reset` | 4.39618535478e-05 | +2.65768e-08 | 0.5010713733 | +0.0003333333 | priced |
| `ro_06_none` | 4.39631967993e-05 | +2.792e-08 | 0.5033827611 | -0.004266667 | priced |
| `ro_07_19-25` | 4.39673343157e-05 | +3.20576e-08 | 0.5047274262 | -0.006933333 | priced |
| `init_26_reset` | 4.39741322914e-05 | +3.88555e-08 | 0.5010710983 | +0.0003333333 | priced |
| `flag13_t35` | 4.4004382558e-05 | +6.91058e-08 | 0.5012371418 | — | priced |
| `flag13_t33` | 4.40375618202e-05 | +1.02285e-07 | 0.5012384162 | — | priced |
| `flag13_t32` | 4.40415431259e-05 | +1.06266e-07 | 0.501237354 | — | priced |
| `flag13_t31` | 4.4045524413e-05 | +1.10248e-07 | 0.5012367379 | — | priced |
| `flag13_t30` | 4.40495056777e-05 | +1.14229e-07 | 0.501236568 | — | priced |
| `flag13_t29` | 4.4053486917e-05 | +1.1821e-07 | 0.5012368442 | — | priced |
| `flag13_t28` | 4.40574681269e-05 | +1.22191e-07 | 0.5012375665 | — | priced |
| `flag13_t27` | 4.40614493046e-05 | +1.26173e-07 | 0.5012387349 | — | priced |
| `flag13_t26` | 4.40654304451e-05 | +1.30154e-07 | 0.5012403495 | — | priced |
| `copy12_1` | 4.41095379391e-05 | +1.74261e-07 | 0.5012371936 | — | priced |
| `flex_control_q17_t28` | 4.41444936388e-05 | +2.09217e-07 | 0.5116820591 | — | priced |
| `joint_3700_000003` | 4.41794923803e-05 | +2.44216e-07 | 0.5162973974 | — | priced |
| `copy12_0` | 4.42726620548e-05 | +3.37385e-07 | 0.5009042073 | — | priced |
| `delete_cx_250` | 4.43979082979e-05 | +4.62632e-07 | 0.5008708585 | — | priced |
| `joint_3711_000012` | 4.45454557466e-05 | +6.10179e-07 | 0.5189869886 | — | priced |
| `joint_3711_000011` | 4.45490932375e-05 | +6.13816e-07 | 0.519748374 | — | priced |
| `joint_3711_exterior_000015` | 4.4549245968e-05 | +6.13969e-07 | 0.518226717 | -0.03331168 | priced |
| `joint_3710_exterior_000007` | 4.45552689531e-05 | +6.19992e-07 | 0.5179522135 | -0.03278012 | priced |
| `joint_3616_exterior_000007` | 4.45863543531e-05 | +6.51078e-07 | 0.512627997 | -0.02245969 | priced |
| `joint_3700_exterior_000038` | 4.48964921943e-05 | +9.61215e-07 | 0.5142775625 | -0.02569289 | priced |
| `joint_3701_exterior_000018` | 4.51365222499e-05 | +1.20125e-06 | 0.5088755658 | -0.01511995 | priced |
| `joint_3615_exterior_000246` | 4.52864769083e-05 | +1.3512e-06 | 0.5040769465 | -0.005606351 | priced |
| `joint_3720_000012` | 4.54986303918e-05 | +1.56335e-06 | 0.5269397364 | — | priced |
| `joint_3720_000009` | 4.55022716028e-05 | +1.56699e-06 | 0.527712789 | — | priced |
| `joint_3720_exterior_000024` | 4.5505879725e-05 | +1.5706e-06 | 0.5265892008 | -0.04924389 | priced |
| `joint_3721_exterior_000007` | 4.55318298054e-05 | +1.59655e-06 | 0.5202626258 | -0.03717698 | priced |
| `late_check_6_forward` | 4.63999106001e-05 | +2.46463e-06 | 0.5017733197 | — | priced |
| `late_check_6_reverse` | 4.63999106001e-05 | +2.46463e-06 | 0.5017733197 | — | priced |
| `joint_3802_exterior_000044` | 4.68642711218e-05 | +2.92899e-06 | 0.5008630367 | +0.0007863823 | priced |
| `joint_3731_000015` | 4.69232938693e-05 | +2.98802e-06 | 0.538314754 | — | priced |
| `joint_3730_000001` | 4.6946460551e-05 | +3.01118e-06 | 0.5397883472 | — | priced |
| `joint_3731_exterior_000077` | 4.69563913187e-05 | +3.02111e-06 | 0.5292390654 | -0.0543064 | priced |
| `late_check_3_forward` | 4.72931295087e-05 | +3.35785e-06 | 0.5004400583 | — | priced |
| `late_check_3_reverse` | 4.72931295088e-05 | +3.35785e-06 | 0.5004400583 | — | priced |
| `late_check_3_6_forward` | 5.01321674247e-05 | +6.19689e-06 | 0.5015421708 | — | priced |
| `late_check_3_6_reverse` | 5.01321674247e-05 | +6.19689e-06 | 0.5015421708 | — | priced |
| `joint_3611_exterior_000027` | 5.05238903064e-05 | +6.58861e-06 | 0.5101892551 | -0.01768499 | priced |
| `joint_3617_exterior_000001` | 5.17661689001e-05 | +7.83089e-06 | 0.51261135 | -0.02240146 | priced |
| `joint_3801_exterior_000011` | 5.36976032932e-05 | +9.76233e-06 | 0.5128707492 | -0.0229268 | priced |
| `joint_3730_exterior_000057` | 5.82982233075e-05 | +1.43629e-05 | 0.5392645595 | -0.07303375 | priced |
| `relaxed_3533_exterior_001082` | 6.05997868796e-05 | +1.66645e-05 | 0.5021943052 | -0.00187108 | priced |
| `joint_3545_exterior_001815` | 6.19472025762e-05 | +1.80119e-05 | 0.5023007101 | -0.00208307 | priced |
| `joint_3541_exterior_000694` | 6.55421238088e-05 | +2.16068e-05 | 0.5027711397 | -0.003003969 | priced |

## Search and mechanisms

The baseline R44 resource leaves exactly six schedules in the tested commuting-CX order model with all other operations fixed; all six were cache priced, and none improved loss. The solver exhausted this specific model. This does not exclude changed encoder networks, initializations, or exterior timing.

FRESH’s reverse-state/signature SAT synthesizer is copied into this lane. The broader search synthesizes either the correlated resource or the entire preparation plus B→C transfer. For the joint contract, the target is B=|0_L>, C=|0^7>, with harmful accepted B X classes forbidden and correctable boundary errors allowed. It preserves the measured-MX frame map and the ideal-zero q13 interior measurement. Candidates are rebuilt on the actual native schedule and checked by the full judge Model before cache extraction. Gate counts are search bounds, not the objective.

Structural branches cover measured/reset B/C initializations, removal of subsets of the four C readout-copy flags, compatible C19/C25 and C28/C29 readout encodings, q13 flag relocation across a control-CX, state-equivalent CX deletions, and changing the C output copied into q18. Moving the q25 copy helper from q31 to q24 is exactly price-neutral. Moving the q18 flag from C19 to C12 loses; advancing the newly unencumbered C19 measurement partly recovers the cost but remains worse. These close only their exact recipes.

Measured-init budget trades: resetting q12 instead of measuring it frees about.000836 acceptance for an all-orders loss cost of1.32e-9. Removing q12 and q23 init flags frees about.001674 for a5.00e-9 cost. Wider removals were measured rather than inferred: all seven tested reset replacements score4.44059128e-5/.508133461. Each instrument profile needs its own cache.

## Validated boundary cache and API

The initial14-bit cache reproduces v35a within7e-17, but most new encoders change the boundary component carried by rejected initialization flags. Reusing that cache would be invalid. The wider cache normalizes those correlations exactly and exposes the interior q13 flag as a fifteenth bit:32,768 classes,98 varying channels, compile99.48s, approximately0.05–0.07s per prepared-region score.

The normalization retains every flag. Each selected flag has ideal reduced projector+I and accepted value0. XORing a linear function of these flag bits into other detector/decoder signatures is therefore identity on every accepted total error. It commutes with XOR composition of faults and preserves the categorical channel probabilities, so both the all-orders numerator and acceptance are unchanged. Interior-flag noise is included explicitly in the region distribution. The exterior fingerprint is recomputed from the normalized distributions and the complete ideal response; mismatches still require a new cache.

Baseline and three different encoder controls were independently evaluated with the unchanged full sparse contraction; maximum loss discrepancy8.56e-16, maximum acceptance discrepancy3.34e-15 (`v35/gauge.full_validation.json`). The unreduced detector mask must be mapped through the judge’s chronological detector order; raw comment order is not that order.

```python
import os, sys
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
os.environ["XTIM_TWIRL_CACHE_DIR"] = "/absolute/path/to/your_lane/.xtim_cache"
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/BCPOL/v35")
from boundary35 import prepare_candidate
from boundary_api import AllOrdersCache
region = prepare_candidate("/absolute/path/to/candidate_stem")
cache = AllOrdersCache(
    "/home/jihoon/competitions/quantumn/work/lanes/BCPOL/v35/inputs/"
    "cache_open_v35a.boundary_allorders.npz")
result = cache.score(region)  # loss, numerator, acceptance, score_seconds
feasible = result["acceptance"] >= 0.5005
```

Inputs are QASM and JSON with data_qubits, R, init_times, region_qubits and boundary_step. This interface uses the current14 B/C cells and a chronological cut45. Model extraction is outside the hot path. Searches with independently audited signature maps may construct PreparedRegion directly. Compile a new compatible exterior with `v35/cache35.py <stem>`; the current implementation limits the response to16 bits.

## Verification and evidence

Full prices use MAIN’s unchanged sparse evaluator,72 canonical moments, copied into this lane to confine outputs. The older exact batch engine overflowed on v35a’s70 detector bits. `v35/wide_masks.py` changes only their storage/bit extraction to Python integers, preserving all projection arithmetic. Wide-mask batch results matched scalar tables exactly on75 signatures, including bits above63. `exact_cli35.py` runs the original exact2 CLI with this representation repair. Third-order shortcuts are used only when |c1|<1e-12.

A screen-output formatting error occurred after results had been computed; the corrected entire structural screening queue was rerun. Full evaluator receipts are independent of those screens. No detector or correctness check was weakened.

Verified versus open: full prices and completed gates are explicitly distinguished above. Finite SAT budgets do not prove impossibility. Cache cut-off error is bounded separately from floating-point roundoff. Organizer-server runtime is inferred from local calibration; only local timings were measured. No submission, commit, push, credentials or subagents were used. Previous completed campaigns remain in [REPORT_v30.md](REPORT_v30.md) and [REPORT_v25.md](REPORT_v25.md).
