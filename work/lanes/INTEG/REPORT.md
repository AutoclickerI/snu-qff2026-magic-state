# INTEG: acceptance trades and gadget integration on v36c (PLAN P75)

Result: **`integ_g1_j8` = MAIN/v36d, all-orders 4.0286189e-5 (−2.10% vs v36c), acceptance 0.505957, 282 CX**, judge 1e6
PASS, FAST (3.7 s/1e6); official seed-0 1e8 run on hippo: 4.015328e-5, acceptance 0.505936.

## Finalists (`integ_*.{qasm,json}`, data_qubits [0,20,7,10,3,22,21]; `finalists.json`)
| Finalist | All-orders 1-F | vs v36c | Acceptance | CX | Judge 1e6 seed 0 | Speed | sha256 prefix |
|---|---:|---:|---:|---:|---|---|---|
| `integ_g1_j8` | 4.0286189e-5 | −2.103% | 0.505957 | 282 | PASS (acc 0.506272) | FAST | e9c2890d667a9eef |
| `integ_g1_j6a` | 4.0305675e-5 | −2.056% | 0.509885 | 278 | PASS (acc 0.50976) | FAST | 64c4bb4b231d1fff |
| `integ_j6a` | 4.0313886e-5 | −2.036% | 0.517593 | 278 | PASS (acc 0.516874) | FAST | 9d0c37e60b07df1b |
| `integ_j5b` | 4.0340951e-5 | −1.970% | 0.519287 | 278 | PASS (acc 0.519083) | FAST | 87681bc137270792 |
`integ_j6a`/`integ_j5b` give up 0.03–0.055e-6 for +0.012–0.013 acceptance (a base for later deltas that need it).

## Acceptance-only trades on v36c (all orders, joint)
| Step | Change | 1-F | Acceptance |
|---|---|---:|---:|
| F0 | prep delay everywhere (RX moved to just before its MX) | ≈ +0 | +0.00369 |
| F1 | + omit measure-inits 39, 40, 42, 46, 271 | 4.115317e-5 | 0.51151 |
| F2 | + reset 43 | 4.115655e-5 | 0.51579 |
| F4 | + uncheck initial checks 181–188 | 4.115715e-5 | 0.51751 |
| F5 | + omit 257 | 4.116081e-5 | 0.51838 |
| F6 | + uncheck 185 | 4.116254e-5 | 0.51924 |
| F7 | F6 + late moves (q14 reset 0→1, q15 RX 0→2, q21 measure 35→36) | 4.116206e-5 | 0.52028 |
| G1 | v36c + prep delay + omit 39/40/42/46/271 + reset 43 + late moves, checks 181–188 kept | 4.11527e-5 | 0.51253 |
Too costly: omit 45 (+2.1e-7 for +0.00284), omit 280 (+1.8e-7), reset 259 (+4.65e-8), reset 270 (+7e-8), any
cultivation check (+1e-6 to +4.5e-5).

## Gadget menu (best singles on F5/F6; all 332 in `menu_singles.tsv`)
| Gadget | Δ1-F | ΔAcceptance |
|---|---:|---:|
| `pair_1_7_35` (also `pairR`) | −1.20e-7 | +0.00076 |
| `echoX_15_h21_14_17r` (or helper h16) | −8.5e-8 | −0.002 |
| `pguard16_10` (q16 RX 39→38, CX 10→16 at tick 39) | −7.7e-8 | ≈ 0 |
| `pguard16_22` | −6.7e-8 | ≈ 0 |
| `echoX_13_h12_28_30r`, `pair_13_14_28` | −4.7e-8 | −/+ |
| `pair_14_20_39`/`_40` | −4.5e-8 | + |
| `echoX_20_h26_11_13`, `echoZ_6_h12_19_24r` | −4.2e-8, −4.1e-8 | − |
| `pair_13_19_28`, `pair_14_15_2x` | −3.5e-8, −3.0 to −3.4e-8 | + |
| `echoX_21_h22_21_30r`, `pair_10_11_30` | −3.2e-8, −2.8e-8 | −/+ |
| `pair_14_20_19`–`_23`, `echoX_15_h16_21_28`, `pair_3_4` (run 19–27), `pair_0_6_34`–`_37` | −2.5 to −2.8e-8 each | ± |
Live-live CX pairs gain the same at every tick of an idle run, either orientation, and add ≈ +0.001 acceptance; echoes
cost ≈ 0.002 acceptance each.

Joint builds: J4a 4.035313e-5 (0.51095) → J5b 4.034095e-5 (0.51929) → J6a 4.031389e-5 (0.51759) → G1__J6a 4.030568e-5
(0.50989) → G1__J7b (echoes first, 34 gadgets) 4.029151e-5 (0.50589) → G1__J8 (+2 guard extensions) 4.028619e-5
(0.50596). Leave-one-out on J7b: removing any gadget loses (`loo_G1__J7b.txt`).

## What failed and why
- Late-window pairs with A or B partners cut partner correlations: `pair_1_7_41` +1.86e-6, `pair_1_2_42` +1.4e-6,
  `pair_0_1_41` +7.9e-7, `pair_16_22_42` +7.6e-7, `pair_7_8_14` +1.16e-6, `pair_6_7_36` +2.8e-7, `pair_3_4_38`/`_42`,
  `pair_4_10_38` positive.
- Late data-data pairs: 20_21 at ticks 39–41 +2.0e-6, 21_22 +2.1e-6 (early 20_21 only −7e-9).
- One q6 echo shared onto q7: +1.07% (W2a), +4.56% (W2b). `star16_10` +1.7e-8; detected CX q13→q7 instead of
  `pair_1_7_35` +6.5e-8; pairs on top of J4a ≈ 0 (helpers already live); guard extensions −5.2e-9 at best.
- Acceptance is not the limit: G1__J8 sits 0.0058 above 0.5002 and the greedy took every positive gadget; re-tuning
  acceptance trades is worth ≤ 1e-9. J3_26 failed the judge's 1e6 acceptance (0.499975) and was dropped.
- Captured ≈ 0.87e-6 of the 6.18e-6 prefix/wait cap. The rest is mostly late data idles (adjoint on F6: q20 1.24e-6,
  q7 1.07e-6, q3 1.05e-6, q10 0.9e-6, q22 0.67e-6, q21 0.44e-6, q0 0.42e-6) with no free helper: their neighbours are
  A and B partners, and every pair or echo with them lost. Needs a layout that frees a neighbour (EARLY).
- Builder bugs fixed: a trailing reset before an MX-init cell merged into an RX made `joint.py` drop echoes; ranking by
  gain per acceptance chose small pairs over larger echoes (now by gain); an over-tight acceptance estimate skipped
  `echoX_15_h16_21_28` (floor now 0.480, real acceptance checked by pricing).

## Verification
All-orders loss and acceptance for every circuit; judge 1e6 PASS and FAST for the four finalists; 1e8 seed 0 for
`integ_g1_j8`; leave-one-out on J7b. Main session: `integ_g1_j8` and `integ_j6a` reproduced with `MAIN/sparse`
(4.0286189316763174e-5 / 0.50596; 4.031388572017179e-5 / 0.51759), judge 1e6 PASS, speed FAST 3.73 s/1e6.
Not run: 3-seed means and ≥ 100 re-draws; 1e8 for the other three. Prices for unpriced pair ticks were copied from a
priced tick of the same idle run; every joint was priced whole.

## Code
`lib.py` (native-tick plans, edits, emission; imports SCHED/BCSYN2 `schedule`/`util`), `gadgets.py`, `joint.py`,
`p1_trades.py`, `p2_singles.py`, `p3_joint.py`, `p4_fill.py`, `fund.py`, `loo.py`, `rank.py`, `posall.py`,
`finalize.py` (judge + FRESH `general_atoms.py`), `ev.py PROCS name...` (all orders through `MAIN/sparse`, candidates in
`c/`, results in `res/`, both rebuildable), `adjmap.py`. Data: `p1_rows.json`, `menu_singles.tsv`, `finalists.json`.
