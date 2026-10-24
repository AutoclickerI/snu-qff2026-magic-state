# KNAP

Status: **complete for this lane**. The retained finalist passes the format, class, correctness, acceptance, and zebra speed gates. No submission, commit, or push was made.

## Best circuit

`final_m04_l2` is the best verified fast circuit retained here.

| Circuit | Exact second | Net cubic term | Exact 1-F through third order | exp(-A1) | CX | Native depth | zebra s / 1e6 | MC seeds 0/1000/2000 | MC mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `final_m04_l2` | 5.069981463e-5 | 1.435028825e-5 | **6.505010288e-5** | **0.510621553** | 215 | 51 | **3.65** | 6.750413e-5 / 6.457010e-5 / 6.597002e-5 | **6.601475e-5** |

The 1e6-shot judge run returned `PASS`, acceptance `0.5100`, and score `5.3925e-5` for its seed-0 sample. The exact third-order calculation has `c1 = 2.66e-19`, so the third-order screen is valid. The finalist is below the blue-v23 exact result and stays well below the 20 s/1e6 speed gate. The validated WALSH evaluator was attempted, but this 54-detector blue circuit has elimination width 26, above that evaluator's width-23 limit; no all-orders value is claimed.

`final_m04_l2` is the blue-XZ v23 circuit with the q19 MX initialization changed to reset+H, plus the KNAP timing/check pack. The older `final_m2c_l2` also has the same exact third-order value and is fast (`3.17 s/1e6`), but its three-seed mean was `6.632082e-5`; q19-only `final_m04_l2` was selected by the required MC ranking.

## Item prices

Deltas below use the v23 base `v23h_c2c9` (`6.922103982e-5`, exp(-A1) `0.540859578`). Positive loss is worse. `ΔA1` is the change in `A1`, so positive values spend acceptance.

| Item / circuit | Δ 1-F | Δ A1 | Exact 1-F | exp(-A1) | Speed effect on zebra |
|---|---:|---:|---:|---:|---|
| Blue XZ `blue_xz_e21_r1` | -3.336273e-6 (-4.82%) | +0.0771915 | 6.588476655e-5 | 0.500680494 | **fails**: v24/KNAP base exceeded 24 s; known v24 timing is about 116 s/1e6 |
| Reviewer item 1, v23 readout copy4 | -4.503243e-7 (-0.651%) | +0.0104000 | 6.877071550e-5 | 0.535263787 | 5.7 s, pass |
| Reviewer item 2, q26→q32 helper | +7.894946e-7 (+1.14%) | +0.0018667 | 7.001053438e-5 | 0.539850915 | 5.0 s, pass |
| Reviewer item 2, q12→q18 helper | +7.649537e-7 (+1.11%) | +0.0018667 | 6.998599354e-5 | 0.539850915 | 4.3 s, pass |
| Reviewer item 2, q19→q18 helper | +7.649537e-7 (+1.11%) | +0.0018667 | 6.998599354e-5 | 0.539850915 | 4.0 s, pass |
| Reviewer item 2, q26+q12 helpers | +1.554448e-6 (+2.25%) | +0.0037333 | 7.077548810e-5 | 0.538844133 | 4.1 s, pass |
| q19 MX→reset+H only on blue base | +1.213084e-7 | +0.0003333 | 6.600607498e-5 | 0.500513629 | 3.0 s, pass |
| Final q19 reset + timing/check pack (`final_m04_l2`) | -8.346637e-7 vs blue base | -0.0196606 vs blue base | **6.505010288e-5** | **0.510621553** | 3.65 s, pass |

The v23 helper constructions are physical, noiselessly correct, and pass the 1e6-shot judge, but they do not reproduce reviewer item 2's v22 gain on the MX-initialized v23 layout. The q26+q12 combination is strictly worse than either single construction.

## Verified combinations

- `final_m04_l2`: exact third-order receipt in `final_m04_l2.exact.stdout`, 1e6-shot judge pass, and three-seed MC mean `6.601475e-5`.
- `final_m2c_l2`: independent prior KNAP receipt, exact `6.505010288e-5`, speed `3.17 s/1e6`, MC mean `6.632082e-5`.
- q19 reset is the necessary speed repair: every tested blue-prep subset without q19 reset timed out beyond the 20 s gate; q19-reset subsets completed around 3–6 s/1e6.
- Reviewer item 1 was reproduced on v23 exactly: `6.922103982e-5 → 6.877071550e-5` through third order, with no depth increase and 206 CX.
- Reviewer item 2 was re-derived on the v23 MX layout. q26↔q32, q12↔q18, q19↔q18, and q26+q12 all pass the judge but lose on exact conditional 1-F.
- A direct item-1 port onto the blue base was rejected: its detector set has anti-deterministic detectors (#37, #38, #43, #46, #47), so it is not a candidate.

## Slow-judge diagnosis

The slow circuit is the blue-XZ check placed on the v23 B+C preparation. v22 and v23 alone take about 2.5 s and 4.0 s per 1e6 shots on zebra, while the blue-v23 circuit branches far more slowly in xtim. The empirical discriminator is the six B+C MX initializations from `fb_s401_0035`: q26, q12, q19, q17, q5, and q4. Replacing q19's early MX initialization by reset+H removes the slow branch while preserving the blue check and produces a 3.0–3.7 s/1e6 circuit. This identifies q19's random measurement frame ahead of the late suffix as the necessary trigger in the tested family. The causal explanation involving xtim's per-shot plan branching is inferred from the timing pattern, not proved from xtim internals.

## Reviewer items 1 and 2

Item 1 was reproduced on the v23 base, including its exact third-order delta and speed gate. Item 2 was not reproduced on v23: the v22 reset/RX positions become MX initializations, and the feasible adjacent-helper rewrites all increase loss. q17's only adjacent candidate q16 remains live later, and q4/q5 have no fresh adjacent helper in this schedule, so those positions were not claimed as valid ports.

## Verified versus inferred

Verified: QASM format and nearest-neighbour CX legality; native schedule metadata; noiseless correctness; exact `c1`, second- and third-order loss; exp(-A1); 1e6-shot judge checks; zebra timing; and the finalist's three required MC seeds. The WALSH all-orders check is unverified for this finalist because its documented width limit rejects the circuit. The exact and judge receipts are local to this lane, and the compact measurements are in `item_measurements.json`.

Inferred: q19 MX/frame branching is the underlying xtim slowdown mechanism, and the tested q19 repair is necessary for this blue-v23 family. No global optimality claim is made. The finalist has not been submitted.
