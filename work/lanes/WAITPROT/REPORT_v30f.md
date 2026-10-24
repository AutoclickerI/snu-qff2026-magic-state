# WAITPROT

Best audited candidate: `m_00_03_09_15_22_29`, **all-orders 1−F 5.380624982e-05** (8.707% below v30f), acceptance **0.501152663**, 201 CX, R48 and native depth51.

Official 1e8 scores (seeds0/1000/2000): 5.429336e-05 / 5.483353e-05 / 5.478327e-05; mean **5.463672e-05**. The 1e6 judge gate passes; speed is FAST.

Byte-identical final artifacts: [best.qasm](best.qasm), [best.json](best.json); provenance and scores: [best.metrics.json](best.metrics.json).

Best measured seed-0 key: **5.372455e-05**, acceptance **0.50368**, `m_00_03_09_19_22_29` (3-seed mean 5.395577e-05). Its audited all-orders loss is 5.419309014e-05. The expectation-ranked and seed-0 choices differ because of MC sampling.

Seed-0 artifacts: [seed0_best.qasm](seed0_best.qasm), [seed0_best.json](seed0_best.json). No submission was made.

Expectation-ranked winner recipe (all ticks are native; CX endpoint ticks identify the two applications):

| stored cell / role | protected axis | helper | preparation tick | CX ticks | readout tick / bit |
|---|---|---:|---:|---|---|
| q0, data for output0 | Z | 6 | 38 | 39, 43 | 44 / c[264] |
| q20, data for output20 | X | 19 | 17 | 18, 35 | 36 / c[265] |
| q7, data for output7 | X | 13 | 19 | 20, 23 | 24 / c[266] |
| q10, ancilla | X | 11 | 18 | 19, 26 | 27 / c[267] |
| q10, data for output10 | Z | 4 | 34 | 35, 38 | 39 / c[268] |
| q4, data for output10 | X | 5 | 17 | 18, 30 | 31 / c[269] |

Z protection uses reset+H, helper→stored-cell CX, and MX; X protection uses reset, stored-cell→helper CX, and MZ. Every new record is a deterministic zero detector.

Status: **COMPLETE**. 78/78 retained native-tick candidates have completed unchanged `EVAL/exact2.py --third` receipts. Finalist ranking uses audited all-orders expectations; cubic references and official MC provide independent checks. Gains are never added between gadgets.

Base: `MAIN/v30f`, data order `[0,20,7,10,3,22,21]`, 189 CX, R48, depth 51; exact 4.62005346e-5 + 1.20387969e-5 = **5.82393315e-5**, exp(-A1)=0.527687. Inherited 3-seed 1e8 MC: 5.90419220e-5 / 5.88640000e-5 / 5.89256e-5; mean **5.89438407e-5**.

## Native schedule and data trajectories

Every `t*` and retained `u*` circuit is checked against the base native instruction list. Every original operation stays at exactly its original tick, and every inserted reset, CX and measurement lands in a free tick. R48 and depth 51 are unchanged. Z helpers are reset+H, never randomly MX-initialized. A trailing H after the helper X readout makes its reused state explicit to the native converter.

Physical storage paths after step 16: logical output q10 uses cell4 until its 31–32 transfer to10; logical output q22 uses cell15, then16 after transfer33–34, then22 after42–43; logical output q21 uses8, then9 after34–35, then15 after36–37, then21 after38–39. Cells0,20,7,3 remain stationary. Protecting future output cell10 before31 is an ancillary-storage control, not protection of logical data10.

| line index | physical weight-3 logical lines |
|---|---|
| 0 | [0, 20, 7] |
| 1 | [0, 10, 3] |
| 2 | [20, 10, 22] |
| 3 | [7, 3, 22] |
| 4 | [7, 10, 21] |
| 5 | [20, 3, 21] |
| 6 | [0, 22, 21] |

Physical-cell idle gaps (inclusive native ticks; separate from the moving-data paths above):

| cell | idle windows | adjacent cells |
|---|---|---|
| 0 | 7–9, 11–11, 13–15, 18–31, 33–34, 37–37, 39–47 | [1, 6] |
| 20 | 11–13, 15–15, 18–38, 40–46 | [14, 19, 21, 26] |
| 7 | 5–5, 7–9, 14–15, 20–23, 27–35, 38–38, 40–47 | [1, 6, 8, 13] |
| 10 | 10–11, 19–26, 28–30, 34–47 | [4, 9, 11, 16] |
| 3 | 5–5, 7–7, 9–9, 13–15, 18–27, 31–31, 33–47 | [2, 4, 9] |
| 22 | 44–47 | [16, 21, 23, 28] |
| 21 | 40–47 | [15, 20, 22, 27] |
| 4 | 8–11, 14–15, 18–30, 34–39, 42–45, 47–47 | [3, 5, 10] |
| 15 | 4–4, 6–8, 11–11, 14–17, 20–30, 43–44, 47–47 | [9, 14, 16, 21] |
| 16 | 35–41, 46–47 | [10, 15, 17, 22] |

All helper free intervals and their preceding/following operations are in [tick_mapping.json](tick_mapping.json). [trajectory_windows.json](trajectory_windows.json) maps every idle window on the moving data paths, including cells8 and9, to each adjacent helper’s free overlaps and fitting Z/X windows. A geometrically adjacent idle cell is not free if it still stores an entangled ancilla. Helper lifetimes must include reset, two CXs and readout; when necessary a final reset restores a later deterministic MZ initialization.

## Singles

| stem | protected windows (CX endpoints, inclusive) | exact second + third = total | exp(-A1) | judge 1e6 | speed | MC seeds0/1000/2000, 1e8 each |
|---|---|---|---:|---|---|---|
| t00_zq0h6_39_43 | Z:q0/h6 CX 39,43 | 4.573830e-05 + 1.159790e-05 = **5.733620e-05** | 0.52511 | — | — | — |
| t01_xq0h6_39_43 | X:q0/h6 CX 39,43 | 4.613780e-05 + 1.191110e-05 = **5.804880e-05** | 0.52511 | — | — | — |
| t02_zq20h19_18_35 | Z:q20/h19 CX 18,35 | 4.620050e-05 + 1.257740e-05 = **5.877790e-05** | 0.51837 | — | — | — |
| t03_xq20h19_18_35 | X:q20/h19 CX 18,35 | 4.620050e-05 + 1.137670e-05 = **5.757720e-05** | 0.51837 | — | — | — |
| t04_zq20h21_18_34 | Z:q20/h21 CX 18,34 | 4.620050e-05 + 1.254190e-05 = **5.874250e-05** | 0.51887 | — | — | — |
| t05_xq20h21_18_35 | X:q20/h21 CX 18,35 | 4.620050e-05 + 1.137670e-05 = **5.757720e-05** | 0.51854 | — | — | — |
| t06_zq20h26_18_34 | Z:q20/h26 CX 18,34 | 4.620050e-05 + 1.254190e-05 = **5.874250e-05** | 0.51887 | — | — | — |
| t07_xq20h26_18_34 | X:q20/h26 CX 18,34 | 4.620050e-05 + 1.141550e-05 = **5.761610e-05** | 0.51887 | — | — | — |
| t08_zq7h13_20_23 | Z:q7/h13 CX 20,23 | 4.644600e-05 + 1.206310e-05 = **5.850910e-05** | 0.52565 | — | — | — |
| t09_xq7h13_20_23 | X:q7/h13 CX 20,23 | 4.522770e-05 + 1.194060e-05 = **5.716830e-05** | 0.52565 | — | — | — |
| t10_zq7h13_27_35 | Z:q7/h13 CX 27,35 | 4.614210e-05 + 1.157910e-05 = **5.772130e-05** | 0.52303 | — | — | — |
| t11_xq7h13_27_35 | X:q7/h13 CX 27,35 | 4.606470e-05 + 1.173730e-05 = **5.780200e-05** | 0.52303 | — | — | — |
| t12_zq7h6_40_43 | Z:q7/h6 CX 40,43 | 4.620050e-05 + 1.169890e-05 = **5.789950e-05** | 0.52564 | — | — | — |
| t13_xq7h6_40_43 | X:q7/h6 CX 40,43 | 4.620050e-05 + 1.190890e-05 = **5.810940e-05** | 0.52564 | — | — | — |
| t14_zq10h11_19_26 | Z:q10/h11 CX 19,26 | 4.641370e-05 + 1.220730e-05 = **5.862110e-05** | 0.52355 | — | — | — |
| t15_xq10h11_19_26 | X:q10/h11 CX 19,26 | 4.588220e-05 + 1.178770e-05 = **5.766990e-05** | 0.52355 | — | — | — |
| t16_zq10h16_19_26 | Z:q10/h16 CX 19,26 | 4.641370e-05 + 1.220730e-05 = **5.862110e-05** | 0.52251 | — | — | — |
| t17_xq10h16_19_26 | X:q10/h16 CX 19,26 | 4.588220e-05 + 1.178770e-05 = **5.766990e-05** | 0.52234 | — | — | — |
| t18_zq10h11_28_30 | Z:q10/h11 CX 28,30 | 4.619180e-05 + 1.202670e-05 = **5.821850e-05** | 0.52617 | — | — | — |
| t19_xq10h11_28_30 | X:q10/h11 CX 28,30 | 4.610290e-05 + 1.195980e-05 = **5.806270e-05** | 0.52617 | — | — | — |
| t20_zq10h16_28_29 | Z:q10/h16 CX 28,29 | 4.614740e-05 + 1.199390e-05 = **5.814130e-05** | 0.52670 | — | — | — |
| t21_xq10h16_28_30 | X:q10/h16 CX 28,30 | 4.610290e-05 + 1.195980e-05 = **5.806270e-05** | 0.52635 | — | — | — |
| t22_zq10h4_35_38 | Z:q10/h4 CX 35,38 | 4.564460e-05 + 1.166890e-05 = **5.731350e-05** | 0.52561 | — | — | — |
| t23_xq10h4_35_38 | X:q10/h4 CX 35,38 | 4.599990e-05 + 1.183960e-05 = **5.783960e-05** | 0.52561 | — | — | — |
| t24_zq10h11_34_35 | Z:q10/h11 CX 34,35 | 4.599310e-05 + 1.182750e-05 = **5.782050e-05** | 0.52669 | — | — | — |
| t25_xq10h11_34_35 | X:q10/h11 CX 34,35 | 4.599310e-05 + 1.182750e-05 = **5.782050e-05** | 0.52669 | — | — | — |
| t26_zq3h4_35_38 | Z:q3/h4 CX 35,38 | 4.620050e-05 + 1.172870e-05 = **5.792920e-05** | 0.52560 | — | — | — |
| t27_xq3h4_35_38 | X:q3/h4 CX 35,38 | 4.620050e-05 + 1.192910e-05 = **5.812960e-05** | 0.52560 | — | — | — |
| t28_zq4h5_18_30 | Z:q4/h5 CX 18,30 | 4.663420e-05 + 1.237830e-05 = **5.901250e-05** | 0.52096 | — | — | — |
| t29_xq4h5_18_30 | X:q4/h5 CX 18,30 | 4.566290e-05 + 1.161390e-05 = **5.727680e-05** | 0.52096 | — | — | — |
| t30_zq4h5_34_37 | Z:q4/h5 CX 34,37 | 4.620050e-05 + 1.203880e-05 = **5.823930e-05** | 0.52467 | — | — | — |
| t31_xq4h5_34_37 | X:q4/h5 CX 34,37 | 4.620050e-05 + 1.203880e-05 = **5.823930e-05** | 0.52467 | — | — | — |
| t32_zq15h16_20_29 | Z:q15/h16 CX 20,29 | 4.620050e-05 + 1.222090e-05 = **5.842140e-05** | 0.52251 | — | — | — |
| t33_xq15h16_20_30 | X:q15/h16 CX 20,30 | 4.620050e-05 + 1.171010e-05 = **5.791060e-05** | 0.52217 | — | — | — |
| t34_zq15h21_20_30 | Z:q15/h21 CX 20,30 | 4.620050e-05 + 1.224900e-05 = **5.844950e-05** | 0.52061 | — | — | — |
| t35_xq15h21_20_30 | X:q15/h21 CX 20,30 | 4.620050e-05 + 1.171010e-05 = **5.791060e-05** | 0.52044 | — | — | — |
| t36_zq16h22_35_38 | Z:q16/h22 CX 35,38 | 4.620050e-05 + 1.169900e-05 = **5.789950e-05** | 0.52564 | — | — | — |
| t37_xq16h22_35_39 | X:q16/h22 CX 35,39 | 4.620050e-05 + 1.181840e-05 = **5.801890e-05** | 0.52529 | — | — | — |

## Pairs and Fano triples

All compatible helper/window assignments are screened as complete circuits with FRESH’s Fourier contraction; `subset_screen.json` records that enumeration. For each distinct protected logical subset, retain its best Z-only and best mixed-axis realization above exp(-A1)=0.5002, then price those with unchanged exact2. This enumerates subset choices and maximal helper-free windows; it does not prove optimality over every shortened subwindow, added swaps, delayed rounds, or different base circuits.

| stem | subset / family | windows | exact second + third = total | exp(-A1) | judge 1e6 | speed | MC |
|---|---|---|---|---:|---|---|---|
| u_t00_t22 | [0, 10] / Z | Z:q0/h6 CX 39,43; Z:q10/h4 CX 35,38 | 4.518240e-05 + 1.125090e-05 = **5.643320e-05** | 0.52305 | PASS 1−F=6.792685e-05, acc=0.522621 | FAST 11.057 s/1e6 | 5.756355e-05 / 5.612569e-05 / 5.720062e-05; mean **5.696329e-05** |
| u_t00_t29 | [0, 10] / mixed | Z:q0/h6 CX 39,43; X:q4/h5 CX 18,30 | 4.520070e-05 + 1.117730e-05 = **5.637790e-05** | 0.51842 | — | — | — |
| u_t00_t04 | [0, 20] / Z | Z:q0/h6 CX 39,43; Z:q20/h21 CX 18,34 | 4.573830e-05 + 1.209850e-05 = **5.783680e-05** | 0.51633 | — | — | — |
| u_t00_t03 | [0, 20] / mixed | Z:q0/h6 CX 39,43; X:q20/h19 CX 18,35 | 4.573830e-05 + 1.093890e-05 = **5.667720e-05** | 0.51583 | — | — | — |
| u_t00_t36 | [0, 22] / Z | Z:q0/h6 CX 39,43; Z:q16/h22 CX 35,38 | 4.573830e-05 + 1.127200e-05 = **5.701030e-05** | 0.52307 | — | — | — |
| u_t00_t35 | [0, 22] / mixed | Z:q0/h6 CX 39,43; X:q15/h21 CX 20,30 | 4.573830e-05 + 1.127130e-05 = **5.700960e-05** | 0.51789 | — | — | — |
| u_t00_t26 | [0, 3] / Z | Z:q0/h6 CX 39,43; Z:q3/h4 CX 35,38 | 4.573830e-05 + 1.131430e-05 = **5.705260e-05** | 0.52304 | — | — | — |
| u_t00_t26 | [0, 3] / mixed | Z:q0/h6 CX 39,43; Z:q3/h4 CX 35,38 | 4.573830e-05 + 1.131430e-05 = **5.705260e-05** | 0.52304 | — | — | — |
| u_t00_t24_t26 | [0, 3, 10] / Z | Z:q0/h6 CX 39,43; Z:q10/h11 CX 34,35; Z:q3/h4 CX 35,38 | 4.553080e-05 + 1.111440e-05 = **5.664520e-05** | 0.52204 | — | — | — |
| u_t00_t26_t29 | [0, 3, 10] / mixed | Z:q0/h6 CX 39,43; Z:q3/h4 CX 35,38; X:q4/h5 CX 18,30 | 4.520070e-05 + 1.089470e-05 = **5.609540e-05** | 0.51637 | — | — | — |
| u_t00_t10 | [0, 7] / Z | Z:q0/h6 CX 39,43; Z:q7/h13 CX 27,35 | 4.567990e-05 + 1.113830e-05 = **5.681820e-05** | 0.52048 | — | — | — |
| u_t00_t09 | [0, 7] / mixed | Z:q0/h6 CX 39,43; X:q7/h13 CX 20,23 | 4.476540e-05 + 1.149980e-05 = **5.626530e-05** | 0.52308 | — | — | — |
| u_t00_t06_t10 | [0, 7, 20] / Z | Z:q0/h6 CX 39,43; Z:q20/h26 CX 18,34; Z:q7/h13 CX 27,35 | 4.567990e-05 + 1.160060e-05 = **5.728050e-05** | 0.51178 | — | — | — |
| u_t00_t03_t09 | [0, 7, 20] / mixed | Z:q0/h6 CX 39,43; X:q20/h19 CX 18,35; X:q7/h13 CX 20,23 | 4.476540e-05 + 1.086450e-05 = **5.563000e-05** | 0.51384 | PASS 1−F=6.036190e-05, acc=0.513569 | FAST 6.492 s/1e6 | 5.619131e-05 / 5.816182e-05 / 5.674282e-05; mean **5.703198e-05** |
| u_t04_t22 | [10, 20] / Z | Z:q20/h21 CX 18,34; Z:q10/h4 CX 35,38 | 4.564460e-05 + 1.216490e-05 = **5.780950e-05** | 0.51683 | — | — | — |
| u_t03_t29 | [10, 20] / mixed | X:q20/h19 CX 18,35; X:q4/h5 CX 18,30 | 4.566290e-05 + 1.098980e-05 = **5.665270e-05** | 0.51176 | — | — | — |
| u_t06_t22_t36 | [10, 20, 22] / Z | Z:q20/h26 CX 18,34; Z:q10/h4 CX 35,38; Z:q16/h22 CX 35,38 | 4.564460e-05 + 1.183120e-05 = **5.747580e-05** | 0.51482 | — | — | — |
| u_t03_t29_t36 | [10, 20, 22] / mixed | X:q20/h19 CX 18,35; X:q4/h5 CX 18,30; Z:q16/h22 CX 35,38 | 4.566290e-05 + 1.066920e-05 = **5.633210e-05** | 0.50977 | — | — | — |
| u_t22_t36 | [10, 22] / Z | Z:q10/h4 CX 35,38; Z:q16/h22 CX 35,38 | 4.564460e-05 + 1.134480e-05 = **5.698940e-05** | 0.52357 | — | — | — |
| u_t29_t36 | [10, 22] / mixed | X:q4/h5 CX 18,30; Z:q16/h22 CX 35,38 | 4.566290e-05 + 1.128200e-05 = **5.694490e-05** | 0.51894 | — | — | — |
| u_t04_t36 | [20, 22] / Z | Z:q20/h21 CX 18,34; Z:q16/h22 CX 35,38 | 4.620050e-05 + 1.219110e-05 = **5.839160e-05** | 0.51685 | — | — | — |
| u_t03_t36 | [20, 22] / mixed | X:q20/h19 CX 18,35; Z:q16/h22 CX 35,38 | 4.620050e-05 + 1.105040e-05 = **5.725090e-05** | 0.51635 | — | — | — |
| u_t24_t26 | [3, 10] / Z | Z:q10/h11 CX 34,35; Z:q3/h4 CX 35,38 | 4.599310e-05 + 1.152210e-05 = **5.751520e-05** | 0.52461 | — | — | — |
| u_t26_t29 | [3, 10] / mixed | Z:q3/h4 CX 35,38; X:q4/h5 CX 18,30 | 4.566290e-05 + 1.130650e-05 = **5.696940e-05** | 0.51891 | — | — | — |
| u_t04_t26 | [3, 20] / Z | Z:q20/h21 CX 18,34; Z:q3/h4 CX 35,38 | 4.620050e-05 + 1.222860e-05 = **5.842910e-05** | 0.51682 | — | — | — |
| u_t03_t26 | [3, 20] / mixed | X:q20/h19 CX 18,35; Z:q3/h4 CX 35,38 | 4.620050e-05 + 1.107060e-05 = **5.727110e-05** | 0.51632 | — | — | — |
| u_t26_t36 | [3, 22] / Z | Z:q3/h4 CX 35,38; Z:q16/h22 CX 35,38 | 4.620050e-05 + 1.139870e-05 = **5.759920e-05** | 0.52357 | — | — | — |
| u_t26_t36 | [3, 22] / mixed | Z:q3/h4 CX 35,38; Z:q16/h22 CX 35,38 | 4.620050e-05 + 1.139870e-05 = **5.759920e-05** | 0.52357 | — | — | — |
| u_t10_t26 | [3, 7] / Z | Z:q7/h13 CX 27,35; Z:q3/h4 CX 35,38 | 4.614210e-05 + 1.126910e-05 = **5.741120e-05** | 0.52097 | — | — | — |
| u_t09_t26 | [3, 7] / mixed | X:q7/h13 CX 20,23; Z:q3/h4 CX 35,38 | 4.522770e-05 + 1.163050e-05 = **5.685820e-05** | 0.52357 | — | — | — |
| u_t10_t26_t36 | [3, 7, 22] / Z | Z:q7/h13 CX 27,35; Z:q3/h4 CX 35,38; Z:q16/h22 CX 35,38 | 4.614210e-05 + 1.094200e-05 = **5.708420e-05** | 0.51895 | — | — | — |
| u_t09_t26_t36 | [3, 7, 22] / mixed | X:q7/h13 CX 20,23; Z:q3/h4 CX 35,38; Z:q16/h22 CX 35,38 | 4.522770e-05 + 1.130060e-05 = **5.652830e-05** | 0.52154 | — | — | — |
| u_t10_t22 | [7, 10] / Z | Z:q7/h13 CX 27,35; Z:q10/h4 CX 35,38 | 4.558620e-05 + 1.121580e-05 = **5.680200e-05** | 0.52098 | — | — | — |
| u_t09_t29 | [7, 10] / mixed | X:q7/h13 CX 20,23; X:q4/h5 CX 18,30 | 4.469010e-05 + 1.151580e-05 = **5.620580e-05** | 0.51895 | PASS 1−F=5.983470e-05, acc=0.518094 | FAST 5.563 s/1e6 | 5.638386e-05 / 5.703086e-05 / 5.746042e-05; mean **5.695838e-05** |
| u_t06_t10 | [7, 20] / Z | Z:q20/h26 CX 18,34; Z:q7/h13 CX 27,35 | 4.614210e-05 + 1.204400e-05 = **5.818610e-05** | 0.51429 | — | — | — |
| u_t03_t09 | [7, 20] / mixed | X:q20/h19 CX 18,35; X:q7/h13 CX 20,23 | 4.522770e-05 + 1.130220e-05 = **5.652990e-05** | 0.51636 | — | — | — |
| u_t10_t36 | [7, 22] / Z | Z:q7/h13 CX 27,35; Z:q16/h22 CX 35,38 | 4.614210e-05 + 1.124230e-05 = **5.738450e-05** | 0.52100 | — | — | — |
| u_t09_t36 | [7, 22] / mixed | X:q7/h13 CX 20,23; Z:q16/h22 CX 35,38 | 4.522770e-05 + 1.160090e-05 = **5.682860e-05** | 0.52361 | — | — | — |

## Combined storage windows

A forward/backward search of complete circuits combines useful windows, including multiple separated windows on one data trajectory and ancillary storage controls. Every combination is fully re-evaluated; no gains are added. `multi_screen.json` records 68 tested sets.

| stem | windows | exact second + third = total | exp(-A1) | judge 1e6 | speed | MC |
|---|---|---|---:|---|---|---|
| m_00_03_09_15_22_29 | Z:q0/h6 CX 39,43; X:q20/h19 CX 18,35; X:q7/h13 CX 20,23; X:q10/h11 CX 19,26; Z:q10/h4 CX 35,38; X:q4/h5 CX 18,30 | 4.335350e-05 + 9.919120e-06 = **5.327260e-05** | 0.50134 | PASS 1−F=5.689940e-05, acc=0.500884 | FAST 6.222 s/1e6 | 5.429336e-05 / 5.483353e-05 / 5.478327e-05; mean **5.463672e-05** |
| m_00_03_09_10_22_29 | Z:q0/h6 CX 39,43; X:q20/h19 CX 18,35; X:q7/h13 CX 20,23; Z:q7/h13 CX 27,35; Z:q10/h4 CX 35,38; X:q4/h5 CX 18,30 | 4.361350e-05 + 9.765610e-06 = **5.337910e-05** | 0.50084 | PASS 1−F=5.494747e-05, acc=0.500478 | FAST 7.682 s/1e6 | 5.380023e-05 / 5.103414e-05 / 5.354882e-05; mean **5.279440e-05** |
| m_00_03_09_22_29_36 | Z:q0/h6 CX 39,43; X:q20/h19 CX 18,35; X:q7/h13 CX 20,23; Z:q10/h4 CX 35,38; X:q4/h5 CX 18,30; Z:q16/h22 CX 35,38 | 4.367190e-05 + 9.852080e-06 = **5.352400e-05** | 0.50334 | PASS 1−F=5.672443e-05, acc=0.502429 | FAST 4.869 s/1e6 | 5.457393e-05 / 5.304928e-05 / 5.225984e-05; mean **5.329435e-05** |
| m_00_03_09_19_22_29 | Z:q0/h6 CX 39,43; X:q20/h19 CX 18,35; X:q7/h13 CX 20,23; X:q10/h11 CX 28,30; Z:q10/h4 CX 35,38; X:q4/h5 CX 18,30 | 4.357430e-05 + 1.007390e-05 = **5.364820e-05** | 0.50385 | PASS 1−F=5.855952e-05, acc=0.503761 | FAST 6.649 s/1e6 | 5.372455e-05 / 5.285803e-05 / 5.528473e-05; mean **5.395577e-05** |

## Audited all-orders ranking

The sparse evaluator is copied from MAIN’s validated implementation. Before each contraction, the independent frontend is compared with the official exact2 Model: every channel probability/qubit, Pauli component, rotation-sign signature, final logical signature and detector signature (after ordering permutation), plus every rotation, projector and decoder observable must match. All-orders results use zero frame, no POSTSELECT, diagonal projectors and native schedules with barriers covering every used qubit; assertions enforce this scope. The baseline reproduces MAIN’s 5.8937742042181006e-5 exactly.

| stem | all-orders 1−F | exact acceptance | vs baseline | kernel omission bound | channel/fault audit |
|---|---:|---:|---:|---:|---|
| m_00_03_09_15_22_29 | **5.3806249824e-05** | 0.501152663 | -8.707% | 1.17e-14 | 517 channels, 3699 faults: all match |
| m_00_03_09_10_22_29 | **5.3910467522e-05** | 0.500670610 | -8.530% | 1.17e-14 | 517 channels, 3699 faults: all match |
| m_00_03_09_22_29_36 | **5.4056420254e-05** | 0.503164058 | -8.282% | 1.17e-14 | 518 channels, 3702 faults: all match |
| m_00_03_09_19_22_29 | **5.4193090142e-05** | 0.503669735 | -8.050% | 1.17e-14 | 517 channels, 3699 faults: all match |
| u_t00_t03_t09 | **5.6243022069e-05** | 0.513668009 | -4.572% | 1.14e-14 | 497 channels, 3579 faults: all match |
| u_t09_t29 | **5.6859515049e-05** | 0.518752834 | -3.526% | 1.13e-14 | 489 channels, 3535 faults: all match |
| u_t00_t22 | **5.7073881011e-05** | 0.522922428 | -3.162% | 1.12e-14 | 492 channels, 3544 faults: all match |
| baseline | **5.8937742042e-05** | 0.527524506 | +0.000% | 1.11e-14 | 477 channels, 3459 faults: all match |

This all-orders expectation resolves close MC ordering within the audited scope. The omission bound covers the sparse-kernel threshold and excludes floating-point roundoff. Cubic values and the requested official three-seed samples are retained independently.


Logical output21 has no room for this four-operation storage gadget along its native moving trajectory. Each adjacent cell is live, or its free interval ends too early. Thus Fano lines (7,10,21), (20,3,21), (0,22,21) are excluded in this fixed-schedule construction. The other four Fano lines are tested, including (0,20,7); the initial no-Fano claim was a builder error and is withdrawn.

## Loss mechanisms and diagnostic decomposition

The isolated-storage coefficients from the reviewer are reproduced by `ideal_count.py`: 14 → 11 → 10 → 10 → 28 for none/one/two/Fano-three/all-seven. For a logical line L, the coefficient is 0.5·2^|L∩P| + 1.5·1[L∩P=∅], summing over seven lines. This model removes protected Z/Y and doubles protected X exposure. It omits preparation/readout/CX faults and prefix/round correlations, which are included in the full circuit prices. Several windows sit inside cultivation, between T/T† layers and checks; the isolated storage coefficient alone cannot rank them. In the same uniform toy, the X dual gives14/14/16/20/56. Its measured benefit here therefore comes from the nonuniform prefix and cross-fault structure, especially the leading X-idle pair, not a universal reduction of isolated wait triples.

A Z gadget detects data Z/Y inside its entangled window and admits helper X faults onto that data. The X dual detects X/Y and admits helper Z faults. Which helps depends on propagated logical signatures, not the number of idle ticks. On v30f the leading 7.731e-7 pair is X on cell7 during20–23 with Y on cell20 during40–46; Z protection leaves its X component, while X protection detects it.

Diagnostic region definitions: wait = data idle channels in the mapped storage trajectories, ticks18–47; round = original operations at48 onward and final idles; helper = all inserted gate/reset/readout noise and helper idles inside the protected lifetime; other = remaining channels. The 16 full-model region masks retain all joint cross terms. Pure wait triples mean the positive weight-three term with only wait noise. Pair×others normalization is reported separately.

| stem | wait-only weight-three | wait × final-round pairs | wait × prefix/preparation pairs | helper-containing pairs | helper-containing weight-three | full minus helper-noiseless, through3 |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 1.1528566e-06 | 2.5504490e-07 | 5.0149546e-06 | 0.0000000e+00 | 0.0000000e+00 | 0.0000000e+00 |
| m_00_03_09_15_22_29 | 6.5155721e-07 | -3.3881318e-21 | 3.0039760e-06 | 5.4604583e-07 | 8.9102139e-07 | 1.1010362e-06 |
| m_00_03_09_22_29_36 | 5.7920295e-07 | -3.3881318e-21 | 3.0039760e-06 | 5.1049027e-07 | 1.0555659e-06 | 1.2306051e-06 |
| t02_zq20h19_18_35 | 1.1303418e-06 | 2.5504490e-07 | 5.0149546e-06 | -5.5565361e-19 | 7.0173509e-07 | 6.4937448e-07 |
| t04_zq20h21_18_34 | 1.1305308e-06 | 2.5504490e-07 | 5.0149546e-06 | -1.0570971e-18 | 6.6358519e-07 | 6.1122458e-07 |
| t06_zq20h26_18_34 | 1.1305308e-06 | 2.5504490e-07 | 5.0149546e-06 | -1.9989978e-18 | 6.6358519e-07 | 6.1122458e-07 |
| t08_zq7h13_20_23 | 1.1435701e-06 | 1.2769259e-07 | 4.9208247e-06 | 8.5297624e-07 | 2.0362731e-07 | 9.4196407e-07 |
| t14_zq10h11_19_26 | 1.1528566e-06 | 2.5504490e-07 | 5.0149546e-06 | 3.0133491e-07 | 3.1410003e-07 | 5.4089457e-07 |
| t16_zq10h16_19_26 | 1.1528566e-06 | 2.5504490e-07 | 5.0149546e-06 | 3.0133491e-07 | 3.1440096e-07 | 5.4089457e-07 |
| t28_zq4h5_18_30 | 1.1352328e-06 | 2.5504490e-07 | 4.9274192e-06 | 5.2119819e-07 | 5.0549458e-07 | 9.3842745e-07 |
| t32_zq15h16_20_29 | 1.0876345e-06 | 2.5504490e-07 | 5.0149546e-06 | -1.0503209e-18 | 3.6203505e-07 | 3.0967444e-07 |
| t34_zq15h21_20_30 | 1.0830349e-06 | 2.5504490e-07 | 5.0149546e-06 | 3.3881318e-20 | 3.9646064e-07 | 3.4410004e-07 |
| u_t00_t03_t09 | 8.0569566e-07 | -3.3881318e-21 | 4.2753163e-06 | 3.3271249e-07 | 4.8681339e-07 | 6.4256474e-07 |
| u_t00_t22 | 9.2329610e-07 | 2.5504490e-07 | 3.7656656e-06 | 2.3111111e-07 | 6.0528526e-07 | 7.1614228e-07 |
| u_t09_t29 | 1.0188591e-06 | -3.3881318e-21 | 4.2532651e-06 | 2.7937916e-07 | 1.8711224e-07 | 3.4455239e-07 |

## Negative and neutral results

| stem | change in second order | change in third order | net change | mechanism |
|---|---:|---:|---:|---|
| t02_zq20h19_18_35 | 0 (rounded) | +5.38603e-07 | +5.38568e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q20/h19 CX 18,35 |
| t04_zq20h21_18_34 | 0 (rounded) | +5.03103e-07 | +5.03169e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q20/h21 CX 18,34 |
| t06_zq20h26_18_34 | 0 (rounded) | +5.03103e-07 | +5.03169e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q20/h26 CX 18,34 |
| t08_zq7h13_20_23 | +2.45465e-07 | +2.43031e-08 | +2.69768e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q7/h13 CX 20,23 |
| t14_zq10h11_19_26 | +2.13165e-07 | +1.68503e-07 | +3.81769e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q10/h11 CX 19,26 |
| t16_zq10h16_19_26 | +2.13165e-07 | +1.68503e-07 | +3.81769e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q10/h16 CX 19,26 |
| t28_zq4h5_18_30 | +4.33665e-07 | +3.39503e-07 | +7.73168e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q4/h5 CX 18,30 |
| t30_zq4h5_34_37 | 0 (rounded) | 0 (rounded) | 0 (rounded) | The state is discarded by the later reset; the extra detector spends acceptance without reducing logical loss. |
| t31_xq4h5_34_37 | 0 (rounded) | 0 (rounded) | 0 (rounded) | The state is discarded by the later reset; the extra detector spends acceptance without reducing logical loss. |
| t32_zq15h16_20_29 | 0 (rounded) | +1.82103e-07 | +1.82069e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q15/h16 CX 20,29 |
| t34_zq15h21_20_30 | 0 (rounded) | +2.10203e-07 | +2.10168e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q15/h21 CX 20,30 |
| u_t04_t36 | 0 (rounded) | +1.52303e-07 | +1.52268e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q20/h21 CX 18,34 |
| u_t04_t26 | 0 (rounded) | +1.89803e-07 | +1.89768e-07 | Early Z protection admits helper X errors. In this prefix these recreate costly pair/triple combinations; the reduced Z exposure does not cover that cost. Helpers/windows: Z:q20/h21 CX 18,34 |

Single-gadget negative mechanisms are also isolated by helper-noiseless diagnostics in the preceding table. In particular, q20’s early Z variant has no second-order change: its loss increase is entirely cubic. Differences below 1e-10 are displayed as zero because the reference CLI prints six significant digits.


These ablations use the exact2 model and FRESH moment contraction for diagnosis; complete-circuit cubic prices come from the unchanged exact2 receipts, and finalist ranking uses the audited all-orders expectations. Effects cannot be added between gadgets. The final-round-only loss is identical for baseline and best:2.87125197037e-5 through third order. Its operations and timing were preserved. Pair ledgers sum to the full second-order result and the four-region cubic interaction vanishes to<1e-15, as required; see `decomposition_audit.json`.

## Initial insertion experiment and corrections

The first second-order batch mistakenly nested multiprocessing pools; Python rejected daemon children. It was corrected to one process per candidate. Duplicate pilot pools were subsequently stopped by their owning-host PIDs. Completed receipts are preserved in the initial-attempt archive; the final queue uses tracked subprocess exits and source hashes.

The initial `s*`/`p*` builder inserted operations at textual boundaries and lengthened the circuit. It was replaced after native-schedule audit. Its best measured q7 X variant `s021_x_q7_h13_20_23` had exact **5.80435e-5**, exp(-A1)=0.511292, PASS at1e6, FAST 7.219s/1e6 on tom, and MC5.789242e-5 / 6.027351e-5 / 5.988296e-5 (mean **5.934963e-5**, +0.69% vs inherited base mean). The cubic increase erased most pair-order benefit; the MC difference is unresolved at this sample size. Those results do not price tick-preserving protection.

The earlier pair failures at acceptance≈0.44–0.497 were largely insertion-delay artifacts. No exclusion or final design decision uses them. Their QASM, builders, receipts and validation failures are preserved in `initial_attempt.tar.gz`.
Three seven-window extensions reached the evaluator’s signed-64-bit detector-mask limit. An independent singles/A1 audit (which does not require cubic detector masks) gave exp(-A1)=0.496919, 0.496099 and 0.499395, all below the requested screen. They are acceptance rejects, not correctness failures. `multi_capacity_audit.json` preserves the error and audit; the search now checks acceptance before cubic contraction.

## Verified and limitations

New finalist gates, speed probes and MC run on tom with OMP/OPENBLAS/MKL threads=1. Speed numbers are the requested XTIM probe estimates scaled to1e6; actual1e6 wall times are in `.gates.json`. The inherited2.8s baseline timing was on zebra and is not a direct host-to-host speed comparison.

- No submissions, commits, pushes or credential access. All deliverables are under this lane.
- No-noise correctness uses exact2’s unchanged judge/Stim path; separate assertions verify exact native scheduling and helper ownership. Exported `best` and `seed0_best` artifacts were also judged again on zebra, reproducing their original1e6 scores and acceptance; hashes and native checks are in `final_artifact_check.json`.
- Complete-reference status and return codes are retained in `.ref.exit.json`; the CLI `.ref.sensitivity.json` contains pair sensitivity only, so cubic totals are parsed from `.ref.log`.
- The three-seed MC measures all noise orders. Close MC ordering can remain statistically unresolved; use the audited all-orders expectation above to rank the finalists. No global optimum over altered schedules or additional gates is claimed.

[final_audit.json](final_audit.json) verifies all 78 reference source hashes and zero exit codes, agreement with the independent moment screens at CLI printed precision, all seven finalist gates/FAST probes/three-seed MC runs, and both exported artifact pairs. [process_exit_audit.json](process_exit_audit.json) records no remaining WAITPROT computation jobs on either host.


Primary sources: [official noise/scheduling](../../../upstream/snu-qff2026-problem/tprep/noise.py), [official judge](../../../upstream/snu-qff2026-problem/tprep/check.py), [Steane supports](../../../upstream/snu-qff2026-problem/tprep/grid.py), [unchanged cubic evaluator](../EVAL/exact2.py), [validated sparse evaluator](../MAIN/sparse/sparse_walsh.py). All WAITPROT numbers are this lane’s receipts unless explicitly marked inherited.
