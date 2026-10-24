# INIT measurement variants

Exact values use `work/lanes/EVAL/exact2.py` at p=1e-3. Every emitted QASM passed `tprep.check` at 1e6 shots; see `validation.json`.

v12 first-use ordinary Z resets: q2,q9,q14,q16,q20. cand14: q2,q9,q12,q14,q16,q17,q20,q21,q22,q23,q26,q27. The cand14 reset screen keeps every singleton and q16 paired with each other site; the remaining subsets follow the measured additivity pattern.

## v12

| Variant | Sites | Exact 2nd | Exact 3rd | First order | exp(-A1) |
|---|---|---:|---:|---:|---:|
| `v12_combo_r16_ret8_rx0` | combined | 1.09182932e-04 | 1.11134000e-04 | 1.42e-19 | 0.698549 |
| `v12_r_q14_q16_q20` | Z reset q14,q16,q20 | 1.10384576e-04 | — | 1.42e-19 | 0.686852 |
| `v12_r_q2_q14_q16` | Z reset q2,q14,q16 | 1.10384576e-04 | — | 1.42e-19 | 0.686852 |
| `v12_r_q2_q14_q16_q20` | Z reset q2,q14,q16,q20 | 1.10384576e-04 | — | 1.42e-19 | 0.685708 |
| `v12_r_q2_q16_q20` | Z reset q2,q16,q20 | 1.10384576e-04 | — | 1.42e-19 | 0.686852 |
| `v12_r_q2_q9_q14_q16` | Z reset q2,q9,q14,q16 | 1.10384576e-04 | — | 1.42e-19 | 0.685708 |
| `v12_r_q2_q9_q14_q16_q20` | Z reset q2,q9,q14,q16,q20 | 1.10384576e-04 | — | 1.42e-19 | 0.684566 |
| `v12_r_q2_q9_q16` | Z reset q2,q9,q16 | 1.10384576e-04 | — | 1.42e-19 | 0.686852 |
| `v12_r_q2_q9_q16_q20` | Z reset q2,q9,q16,q20 | 1.10384576e-04 | — | 1.42e-19 | 0.685708 |
| `v12_r_q9_q14_q16` | Z reset q9,q14,q16 | 1.10384576e-04 | — | 1.42e-19 | 0.686852 |
| `v12_r_q9_q14_q16_q20` | Z reset q9,q14,q16,q20 | 1.10384576e-04 | — | 1.42e-19 | 0.685708 |
| `v12_r_q9_q16_q20` | Z reset q9,q16,q20 | 1.10384576e-04 | — | 1.42e-19 | 0.686852 |
| `v12_q16_measure` | baseline | 1.10384576e-04 | 1.12530000e-04 | 1.42e-19 | 0.689145 |
| `v12_r_q14_q16` | Z reset q14,q16 | 1.10384576e-04 | — | 1.42e-19 | 0.687997 |
| `v12_r_q16` | Z reset q16 | 1.10384576e-04 | — | 1.42e-19 | 0.689145 |
| `v12_r_q16_q20` | Z reset q16,q20 | 1.10384576e-04 | — | 1.42e-19 | 0.687997 |
| `v12_r_q2_q16` | Z reset q2,q16 | 1.10384576e-04 | — | 1.42e-19 | 0.687997 |
| `v12_r_q9_q16` | Z reset q9,q16 | 1.10384576e-04 | — | 1.42e-19 | 0.687997 |
| `v12_ret_q1_q8` | retain q1,q8 | 1.10993302e-04 | — | 1.42e-19 | 0.699715 |
| `v12_ret_q1_q8_q9` | retain q1,q8,q9 | 1.10993302e-04 | — | 1.42e-19 | 0.699481 |
| `v12_ret_q8` | retain q8 | 1.10993302e-04 | — | 1.42e-19 | 0.699948 |
| `v12_ret_q8_q9` | retain q8,q9 | 1.10993302e-04 | — | 1.42e-19 | 0.699715 |
| `v12_ret_q1` | retain q1 | 1.12194947e-04 | — | 1.42e-19 | 0.690294 |
| `v12_ret_q9` | retain q9 | 1.12194947e-04 | — | 1.42e-19 | 0.690294 |
| `v12_r_q14` | Z reset q14 | 1.12194947e-04 | — | 1.42e-19 | 0.689375 |
| `v12_r_q14_q20` | Z reset q14,q20 | 1.12194947e-04 | — | 1.42e-19 | 0.688227 |
| `v12_r_q2` | Z reset q2 | 1.12194947e-04 | — | 1.42e-19 | 0.689375 |
| `v12_r_q20` | Z reset q20 | 1.12194947e-04 | — | 1.42e-19 | 0.689375 |
| `v12_r_q2_q14` | Z reset q2,q14 | 1.12194947e-04 | — | 1.42e-19 | 0.688227 |
| `v12_r_q2_q14_q20` | Z reset q2,q14,q20 | 1.12194947e-04 | — | 1.42e-19 | 0.687081 |
| `v12_r_q2_q20` | Z reset q2,q20 | 1.12194947e-04 | — | 1.42e-19 | 0.688227 |
| `v12_r_q2_q9` | Z reset q2,q9 | 1.12194947e-04 | — | 1.42e-19 | 0.688227 |
| `v12_r_q2_q9_q14` | Z reset q2,q9,q14 | 1.12194947e-04 | — | 1.42e-19 | 0.687081 |
| `v12_r_q2_q9_q14_q20` | Z reset q2,q9,q14,q20 | 1.12194947e-04 | — | 1.42e-19 | 0.685936 |
| `v12_r_q2_q9_q20` | Z reset q2,q9,q20 | 1.12194947e-04 | — | 1.42e-19 | 0.687081 |
| `v12_r_q9` | Z reset q9 | 1.12194947e-04 | — | 1.42e-19 | 0.689375 |
| `v12_r_q9_q14` | Z reset q9,q14 | 1.12194947e-04 | — | 1.42e-19 | 0.688227 |
| `v12_r_q9_q14_q20` | Z reset q9,q14,q20 | 1.12194947e-04 | — | 1.42e-19 | 0.687081 |
| `v12_r_q9_q20` | Z reset q9,q20 | 1.12194947e-04 | — | 1.42e-19 | 0.688227 |
| `v12_ret_q1_q9` | retain q1,q9 | 1.12194947e-04 | — | 1.42e-19 | 0.690064 |
| `v12_rx_all` | RX→MX q4,q10,q19 | 1.12194947e-04 | — | 1.42e-19 | 0.691215 |
| `v12_rx_q10` | RX→MX q10 | 1.12194947e-04 | — | 1.42e-19 | 0.690755 |
| `v12_rx_q19` | RX→MX q19 | 1.12194947e-04 | — | 1.42e-19 | 0.690755 |
| `v12_rx_q4` | RX→MX q4 | 1.12194947e-04 | — | 1.42e-19 | 0.690755 |
| `v12_base` | baseline | 1.12194947e-04 | 1.14313000e-04 | 1.42e-19 | 0.690525 |
| `v12_r0` | Z reset none | 1.12194947e-04 | — | 1.42e-19 | 0.690525 |

Finalists (exact third-order ranking):

| Variant | Seed 0 | Seed 1000 | Seed 2000 | 3-seed mean ± SEM |
|---|---:|---:|---:|---:|
| `v12_combo_r16_ret8_rx0` | 1.09836500e-04 | 1.12657414e-04 | 1.12431073e-04 | 1.11641662e-04 ± 9.04943072e-07 |
| `v12_q16_measure` | 1.14553745e-04 | 1.12078781e-04 | 1.12570934e-04 | 1.13067820e-04 ± 7.56424502e-07 |

## cand14

| Variant | Sites | Exact 2nd | Exact 3rd | First order | exp(-A1) |
|---|---|---:|---:|---:|---:|
| `cand14_combo_r23_ret8_rx29` | combined | 7.80572395e-05 | 1.08628000e-04 | 4.40e-19 | 0.550176 |
| `cand14_combo_r23_ret8_rx0` | combined | 7.81239062e-05 | 1.08811000e-04 | 4.40e-19 | 0.549993 |
| `cand14_r_q23` | Z reset q23 | 7.88731053e-05 | — | 4.40e-19 | 0.542587 |
| `cand14_r_q16_q23` | Z reset q16,q23 | 7.88731053e-05 | — | 4.40e-19 | 0.541684 |
| `cand14_ret_q8` | retain q8 | 7.96683507e-05 | — | 4.59e-19 | 0.551094 |
| `cand14_ret_q2_q8` | retain q2,q8 | 7.96683507e-05 | — | 4.59e-19 | 0.546201 |
| `cand14_ret_q2_q8_q9` | retain q2,q8,q9 | 7.96683507e-05 | — | 4.59e-19 | 0.546019 |
| `cand14_ret_q8_q9` | retain q8,q9 | 7.96683507e-05 | — | 4.59e-19 | 0.550911 |
| `cand14_r_q26` | Z reset q26 | 8.00731053e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_r_q16_q26` | Z reset q16,q26 | 8.00731053e-05 | — | 4.59e-19 | 0.541864 |
| `cand14_r_q16_q17` | Z reset q16,q17 | 8.02619942e-05 | — | 4.59e-19 | 0.541864 |
| `cand14_r_q17` | Z reset q17 | 8.02619942e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_rx_q29` | RX→MX q29 | 8.03508831e-05 | — | 4.59e-19 | 0.543855 |
| `cand14_rx_all` | RX→MX q4,q5,q10,q11,q25,q28,q29 | 8.03508831e-05 | — | 4.59e-19 | 0.544944 |
| `cand14_r_q12` | Z reset q12 | 8.03619942e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_r_q12_q16` | Z reset q12,q16 | 8.03619942e-05 | — | 4.59e-19 | 0.541864 |
| `cand14_r_q21` | Z reset q21 | 8.04175497e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_r_q22` | Z reset q22 | 8.04175497e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_r_q27` | Z reset q27 | 8.04175497e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_r_q2_q16` | Z reset q2,q16 | 8.04175497e-05 | — | 4.59e-19 | 0.541864 |
| `cand14_r_q9` | Z reset q9 | 8.04175497e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_r_q9_q16` | Z reset q9,q16 | 8.04175497e-05 | — | 4.59e-19 | 0.541864 |
| `cand14_rx_q25` | RX→MX q25 | 8.04175497e-05 | — | 4.59e-19 | 0.543855 |
| `cand14_rx_q28` | RX→MX q28 | 8.04175497e-05 | — | 4.59e-19 | 0.543855 |
| `cand14_rx_q4` | RX→MX q4 | 8.04175497e-05 | — | 4.59e-19 | 0.543855 |
| `cand14_rx_q5` | RX→MX q5 | 8.04175497e-05 | — | 4.59e-19 | 0.543855 |
| `cand14_ret_q2` | retain q2 | 8.04175497e-05 | — | 4.59e-19 | 0.538846 |
| `cand14_ret_q2_q9` | retain q2,q9 | 8.04175497e-05 | — | 4.59e-19 | 0.538666 |
| `cand14_ret_q9` | retain q9 | 8.04175497e-05 | — | 4.59e-19 | 0.543492 |
| `cand14_rx_q10` | RX→MX q10 | 8.04175497e-05 | — | 4.59e-19 | 0.543855 |
| `cand14_rx_q11` | RX→MX q11 | 8.04175497e-05 | — | 4.59e-19 | 0.543855 |
| `cand14_base` | baseline | 8.04175497e-05 | 1.11987000e-04 | 4.59e-19 | 0.543673 |
| `cand14_r0` | Z reset none | 8.04175497e-05 | — | 4.59e-19 | 0.543673 |
| `cand14_r_q14` | Z reset q14 | 8.04175497e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_r_q14_q16` | Z reset q14,q16 | 8.04175497e-05 | — | 4.59e-19 | 0.541864 |
| `cand14_r_q16` | Z reset q16 | 8.04175497e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_r_q16_q20` | Z reset q16,q20 | 8.04175497e-05 | — | 4.59e-19 | 0.541864 |
| `cand14_r_q16_q21` | Z reset q16,q21 | 8.04175497e-05 | — | 4.59e-19 | 0.541864 |
| `cand14_r_q16_q22` | Z reset q16,q22 | 8.04175497e-05 | — | 4.59e-19 | 0.541864 |
| `cand14_r_q16_q27` | Z reset q16,q27 | 8.04175497e-05 | — | 4.59e-19 | 0.541864 |
| `cand14_r_q2` | Z reset q2 | 8.04175497e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_r_q20` | Z reset q20 | 8.04175497e-05 | — | 4.59e-19 | 0.542768 |
| `cand14_ret_q1_q1_q2_q8_q9` | retain q1,q1,q2,q8,q9 | 8.15831247e-05 | — | 4.59e-19 | 0.540636 |
| `cand14_ret_q1_q1_q2_q8` | retain q1,q1,q2,q8 | 8.15831247e-05 | — | 4.59e-19 | 0.540816 |
| `cand14_ret_q1_q1_q8` | retain q1,q1,q8 | 8.15831247e-05 | — | 4.59e-19 | 0.545661 |
| `cand14_ret_q1_q1_q8_q9` | retain q1,q1,q8,q9 | 8.15831247e-05 | — | 4.59e-19 | 0.545480 |
| `cand14_ret_q1_q2_q8` | retain q1,q2,q8 | 8.15831247e-05 | — | 4.59e-19 | 0.540996 |
| `cand14_ret_q1_q2_q8_q9` | retain q1,q2,q8,q9 | 8.15831247e-05 | — | 4.59e-19 | 0.540816 |
| `cand14_ret_q1_q8` | retain q1,q8 | 8.15831247e-05 | — | 4.59e-19 | 0.545843 |
| `cand14_ret_q1_q8_q9` | retain q1,q8,q9 | 8.15831247e-05 | — | 4.59e-19 | 0.545661 |
| `cand14_ret_q1` | retain q1 | 8.23323238e-05 | — | 4.59e-19 | 0.538493 |
| `cand14_ret_q1_q1` | retain q1,q1 | 8.23323238e-05 | — | 4.59e-19 | 0.538314 |
| `cand14_ret_q1_q1_q2` | retain q1,q1,q2 | 8.23323238e-05 | — | 4.59e-19 | 0.533534 |
| `cand14_ret_q1_q1_q2_q9` | retain q1,q1,q2,q9 | 8.23323238e-05 | — | 4.59e-19 | 0.533356 |
| `cand14_ret_q1_q1_q9` | retain q1,q1,q9 | 8.23323238e-05 | — | 4.59e-19 | 0.538134 |
| `cand14_ret_q1_q2` | retain q1,q2 | 8.23323238e-05 | — | 4.59e-19 | 0.533711 |
| `cand14_ret_q1_q2_q9` | retain q1,q2,q9 | 8.23323238e-05 | — | 4.59e-19 | 0.533534 |
| `cand14_ret_q1_q9` | retain q1,q9 | 8.23323238e-05 | — | 4.59e-19 | 0.538314 |

Finalists (exact third-order ranking):

| Variant | Seed 0 | Seed 1000 | Seed 2000 | 3-seed mean ± SEM |
|---|---:|---:|---:|---:|
| `cand14_combo_r23_ret8_rx29` | 1.12533583e-04 | 1.09786828e-04 | 1.12184767e-04 | 1.11501726e-04 ± 8.63341418e-07 |
| `cand14_combo_r23_ret8_rx0` | — | — | — | — ± — |

RX folds accepted by the noiseless judge: v12 q4,q10,q19; cand14 q4,q5,q10,q11,q25,q28,q29. Other fresh RX sites were rejected after exact detector folding because the output was no longer in the code space.
The cand14 q29 finalist has all three 1e8-shot seeds. The near-tied q29-free combined candidate is fully judge-validated at 1e6 and has exact third-order data; its 1e8-shot run was stopped after the q29 finalist completed because the cand14 sampler exceeded the available run window.
