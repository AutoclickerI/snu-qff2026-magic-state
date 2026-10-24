Status: **COMPLETE — stopping gate reached.** `best` is grid-valid, passes the judge and runtime gates, and beats v25k through third order and at all orders. **The independent 9+9-CX B/C construction remains open.** The delivered improvement uses a measured joint preparation. No submission, commit, push, credentials access, or other-lane write.

Best grid circuit: [best.qasm](best.qasm) / [best.json](best.json), byte-identical to verified `zero_endpoint_blue_q5_t37`. **213 CX**, native round boundary **R=48**, depth **51**. `c1=2.664535259100e-19`; second **5.019277595396e-05**, third increment **1.351065029854e-05**, total **6.370342625249e-05**; exp(-A1) **0.5149572232**. This is **2.0702%** below v25k's third-order 6.505010288e-5.

Validated all-orders **1-F = 6.449905264566e-05**, acceptance **0.514863477092**. v25k's independently inherited all-orders reference is 6.59136168224142e-5, so the gain is **2.1461%**. The inherited BCPOL parent is 6.476729894421287e-5; the new measurement improves it by **2.68246299e-7**. All-orders ranking resolves the small opposite fluctuation in the three-seed estimates; no seed-0 cherry-picking was used.

The unchanged 1e6-shot judge passes format, class, correctness and acceptance; seed-0 acceptance **0.514806**, zebra **2.8 s/1e6** (gate <=20 s). The byte-identical MAIN/spec/mc3.py driver, copied to inputs for the older tom mirror, passes its direct tprep.check and returns 1e8-shot seeds 0/1000/2000: **6.624655e-5 / 6.462748e-5 / 6.389037e-5**, mean **6.492147e-5**. Seed-0 acceptance at 1e8 is **0.51489**. [Exact receipt](best.exact.log), [speed](best.speed.log), [MC](best.mc.log), [all orders](best.allorders.json), [channel/sector validation](best.allorders_general.validation.json).

## What changed and what was reused

Reused BCPOL `cache_endpoint_5_902_02232` (rank-five joint endpoint), and its port of KNAP's blue XZ check and q19 RX speed repair. SEPBC adds **`measure q[5] -> c[264]` at native step37**, plus its detector, while q5 is noiselessly |0>. It fits an idle slot and changes no CX, native timing, or placement. The unchanged full judge proves the new detector deterministic. This is an internal preparation measurement, not a separate B or C encoder.

Matched parent-to-child exact gain: second **-1.866666666667e-7**, third **-7.618091165831e-8**, total **-2.628475783250e-7**. Every second-order change belongs to BC-preparation pairs. Largest removed pairs: X preparation flip at q11/t33 paired with XI on CX12→13/t45, IX on CX13→12/t46, or XX on CX12→13/t47. New post-measurement X/Y faults at q5/t37 give back part of that gain. [Complete pair difference](q5_pair_delta.json).

The non-blue port [nonblue.qasm](nonblue.qasm) has third-order **6.783652841685e-05**, all-orders **6.879909974666e-05**, 201 CX, R45, exp(-A1) **0.5447256972**; the 1e6 judge passes at acceptance **0.544293**, **3.6 s/1e6 on zebra**. Adding the KNAP blue/speed-repair package yields the best above: third-order change **-4.133102164356e-06**. This is a package comparison, including its timing and initialization policy.

## Layout and move plan

| Role | Physical cells in logical-index order |
|---|---|
| data | 0, 20, 7, 10, 3, 22, 21 |
| A | 1, 14, 8, 9, 2, 16, 15 |
| B | 6, 26, 13, 11, 4, 23, 27 |
| C | 12, 25, 19, 17, 5, 29, 28 |

The inherited six two-CX data hops remain: logical d3, **4→10**; d5, **15→16→22**; d6, **8→9→15→21**. No new block teleport is added. A retains its grid encoder. The rank-five BC preparation plus verification uses **87 CX in 15 native layers**, finishes at48, and B couples to data at49. q5's added measurement is inside that preparation. The complete native operation plan is [best.plan.json](best.plan.json).

## Built variants and the LADDER shortfall

All losses in this table are through third order at STANDARD p=1e-3. The references ignore adjacency: sepBC **5.71112722e-5**, ABC210 **5.03262480e-5**. Deltas include interactions and cannot be added as independent taxes.

| Variant | Second | Third increment | Total | exp(-A1) | Delta vs sepBC / ABC210 | Mechanism |
|---|---:|---:|---:|---:|---:|---|
| `zero_endpoint_blue_q5_t37` | 5.019277595e-05 | 1.351065030e-05 | 6.370342625e-05 | 0.5149572 | 6.592154052e-06 / 1.337717825e-05 | Transient known-zero measurement catches BC preparation faults |
| `zero_endpoint_q5_t34` | 5.198527566e-05 | 1.585125276e-05 | 6.783652842e-05 | 0.5447257 | 1.072525622e-05 / 1.751028042e-05 | Transient known-zero measurement catches BC preparation faults |
| `zero_endpoint_q4_t42` | 5.217194233e-05 | 1.590255541e-05 | 6.807449774e-05 | 0.5447252 | 1.096322554e-05 / 1.774824974e-05 | Transient known-zero measurement catches BC preparation faults |
| `zero_endpoint_q4_t41` | 5.217194233e-05 | 1.591339231e-05 | 6.808533463e-05 | 0.5447252 | 1.097406243e-05 / 1.775908663e-05 | Transient known-zero measurement catches BC preparation faults |
| `interleave_r45_k4_s3_w0` | 9.106628990e-05 | 7.520213366e-05 | 1.662684236e-04 | 0.3323696 | 1.091571514e-04 / 1.159421756e-04 | Separate B/C: 48 moves and long live-state exposure |
| `amb_d8_c11_s2_000` | 5.258120322e-05 | 1.769491863e-05 | 7.027612185e-05 | 0.5454898 | 1.316484965e-05 / 1.994987385e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `mblns_s1_000_orig` | 5.334995878e-05 | 1.697345735e-05 | 7.032341613e-05 | 0.5403939 | 1.321214393e-05 / 1.999716813e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `control_original` | 5.339009211e-05 | 1.676437037e-05 | 7.015446248e-05 | 0.5415451 | 1.304319028e-05 / 1.982821448e-05 | Reset/init and readout control |
| `mb_control` | 5.389009211e-05 | 1.702257370e-05 | 7.091266581e-05 | 0.5455310 | 1.380139361e-05 / 2.058641781e-05 | Reset/init and readout control |

The best retains routing and the old A package, so its shortfall remains **6.592154052e-06 / 1.337717825e-05** against the two LADDER rungs. Dominant second-order contributions: final round × round **2.884e-5**; BC-region pairs **6.81917e-6**; A-region × data-idle **4.32804e-6**; A-region × BC **2.49307e-6**. Net cubic is **1.351065e-5**. The top A/data pair is Z idle on q10/t35–47 with a late A-encoder CX fault at45. These region bins are physical-cell/time diagnostics, not an order-independent attribution of the reference gap. Exact fault labels are retained in [best.price.json](best.price.json).

The complete separate-block witness has **18 encoder CX + 48 measured teleports**, 185 total CX, R45. B=[6,26,13,11,4,28,27], C=[12,32,19,17,5,34,33], with A and data retained. It passes correctness and speed (**7.2 s/1e6**) but fails acceptance (**0.334859**, versus exp(-A1)=0.332370); exact 1-F **1.66268423558e-4**. Emitted-provenance pair sums: BC prep/moves × themselves **2.84595534e-5**, A prep × BC prep/moves **2.06536687e-5**, plus cubic **7.52021337e-5**. One dominant pair is q25's preparation X flip/t16 with X idle on q13/t19–30; another is Z idle on a C wire q32/t16–44 with a late A-encoder fault. This measured negative closes that exact routing witness only. [Provenance receipt](separate_provenance.json), [judge receipt](separate_speed.json).

Measured-helper searches used the eight spare cells, final X projections, and then intermediate MX+reset operations, with explicit frame derivation and single-X-fault cuts. LNS found a 67-CX preparation, but fewer CX did not rank better: its extra exposure and residual accepted fault pairs outweigh the savings. Independent A instruments on the seven A cells also failed to improve this baseline; cap10/depth6 is UNSAT, while larger time-limited cases remain open. Exact model bounds and timeouts are in [solver_receipts.json](solver_receipts.json).

## Static-layout result

There is **no stationary 6×6 placement with connected seven-cell B and C, all seven B–C pairs adjacent, and a distinct neighboring data cell for every B qubit**. A need not be connected; the independent enumeration reaches the contradiction before choosing A or a complete data matching. Each B vertex needs two external neighbors (C and data), so its degree within connected B is at most two; a seven-cycle is impossible on the bipartite grid, hence B is a path. Enumerating all such physical paths leaves **1584 path descriptions, 656 eligible B sets, 59,568 C assignments, and zero connected C assignments**. An independent unlabelled CP-SAT formulation is also INFEASIBLE. A 7×7 positive control finds a valid placement. [Certificate](static_certificate.json), [enumerator](static_certificate.py), [7×7 control](static_certificate_7.json).

This closes the stationary row-style version of approach (b), without a fourth connected-block assumption. It does **not** close moving blocks, helper-assisted disconnected final blocks, endpoint reuse, staggered data positions, or other joint instruments.

## Verified and inferred

- Verified: every listed completed circuit's native adjacency/timing; noiseless correctness in the EVAL frontend; exact2 pair/third-order sums; |c1| gates; full judge, seed-0 acceptance, zebra runtime, MC and all-orders results for the delivery; the static obstruction and positive control.
- The original four-projector reviewer evaluator was used unchanged in arithmetic for the non-blue candidate. The blue circuit has five active projectors and uses BCPOL's extension: complete physical-channel multiset equality, 1024 projector-sector checks (max error 3.33e-16), and all 4096 outcomes of three correlated channels with nonzero loss (numerator error 1.32e-16). It contracts at width26. It uses no boundary-response cache across changed exteriors.
- Exact2 CLI validation uses algebraically zero-acceptance pruning, with unchanged surviving arithmetic. The unmodified control's third-order output agrees at its printed precision; the pruned calculation and fast categorical contraction agree to <=5e-18 on that control. Equivalent circuits may reuse a completed third-order term only after exact equality of the complete reduced engine and every unrounded categorical noise channel; each retains its own physical pair/top analysis. 212 receipts used that equivalence.
- Timing correction: v23h_c2c9 has four terminal T-dagger gates at **native step44**, not32. Measurements after32 alone do not guarantee the fast judge path. Actual runtimes, rather than that assumption, decide the gate.
- Inferred: live-state exposure is the general obstacle suggested by these routed witnesses. Only the stationary geometric obstruction is proved globally within its stated domain. SAT timeouts are not impossibility claims. The ideal 5.711e-5/5.033e-5 separate-encoder packages have not been realized.
- Build failures were repaired before physics conclusions: the remote mirror lacked a copied evaluator module; a redundant helper reset followed by MX changed native H folding; the cache seeder initially used a shared temporary filename between threads. These failures were not counted as circuit negatives. Cache writes now use process/thread-specific temporary files and atomic replacement; completed equal-key receipts were checked for numerical equality.
- The lane stops because the explicit below-v25k gate was reached, not because all approaches are closed. Local judge results are not an official submission; no server result is claimed.

All **457 built variants** and exact measurements are also available in [built_variants.csv](built_variants.csv) and [measurements.jsonl](measurements.jsonl). Nonfinal circuit files are removed after consolidation; generators, solver receipts, and numerical evidence remain.

<details><summary>Complete built-variant table (457 circuits)</summary>

| Variant | Second | Third increment | Total | exp(-A1) | Delta vs sepBC / ABC210 | Mechanism |
|---|---:|---:|---:|---:|---:|---|
| `amb_d6_c11_s4_000` | 6.741108330e-05 | 1.968345128e-05 | 8.709453458e-05 | 0.5357744 | 2.998326238e-05 / 3.676828658e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_001` | 6.478604817e-05 | 1.696771572e-05 | 8.175376389e-05 | 0.5470886 | 2.464249169e-05 / 3.142751589e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_002` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_003` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_004` | 6.863687870e-05 | 1.975731477e-05 | 8.839419346e-05 | 0.5357409 | 3.128292126e-05 / 3.806794546e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_005` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_006` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_007` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_008` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_009` | 6.863687870e-05 | 1.975731477e-05 | 8.839419346e-05 | 0.5357409 | 3.128292126e-05 / 3.806794546e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_010` | 6.478604817e-05 | 1.696771572e-05 | 8.175376389e-05 | 0.5470886 | 2.464249169e-05 / 3.142751589e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_011` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_012` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_013` | 7.254242683e-05 | 2.332639036e-05 | 9.586881719e-05 | 0.5235984 | 3.875754499e-05 / 4.554256919e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_014` | 7.254242683e-05 | 2.332639036e-05 | 9.586881719e-05 | 0.5235984 | 3.875754499e-05 / 4.554256919e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_015` | 7.254242683e-05 | 2.332639036e-05 | 9.586881719e-05 | 0.5235984 | 3.875754499e-05 / 4.554256919e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_016` | 7.254242683e-05 | 2.332639036e-05 | 9.586881719e-05 | 0.5235984 | 3.875754499e-05 / 4.554256919e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_017` | 7.254242683e-05 | 2.332639036e-05 | 9.586881719e-05 | 0.5235984 | 3.875754499e-05 / 4.554256919e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_018` | 7.254242683e-05 | 2.332639036e-05 | 9.586881719e-05 | 0.5235984 | 3.875754499e-05 / 4.554256919e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_019` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_020` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_021` | 6.863687870e-05 | 1.975731477e-05 | 8.839419346e-05 | 0.5357409 | 3.128292126e-05 / 3.806794546e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_022` | 6.478604817e-05 | 1.696771572e-05 | 8.175376389e-05 | 0.5470886 | 2.464249169e-05 / 3.142751589e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_023` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_024` | 7.248257478e-05 | 2.283400908e-05 | 9.531658386e-05 | 0.5246431 | 3.820531166e-05 / 4.499033586e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_025` | 9.117247687e-05 | 2.748798713e-05 | 1.186604640e-04 | 0.5117775 | 6.154919179e-05 / 6.833421599e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_026` | 9.117247687e-05 | 2.748798713e-05 | 1.186604640e-04 | 0.5117775 | 6.154919179e-05 / 6.833421599e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_027` | 7.974770935e-05 | 2.354113057e-05 | 1.032888399e-04 | 0.5231078 | 4.617756771e-05 / 5.296259191e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_028` | 7.974770935e-05 | 2.354113057e-05 | 1.032888399e-04 | 0.5231078 | 4.617756771e-05 / 5.296259191e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_029` | 7.974770935e-05 | 2.354113057e-05 | 1.032888399e-04 | 0.5231078 | 4.617756771e-05 / 5.296259191e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_030` | 7.974770935e-05 | 2.354113057e-05 | 1.032888399e-04 | 0.5231078 | 4.617756771e-05 / 5.296259191e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_031` | 7.974770935e-05 | 2.354113057e-05 | 1.032888399e-04 | 0.5231078 | 4.617756771e-05 / 5.296259191e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_032` | 7.974770935e-05 | 2.354113057e-05 | 1.032888399e-04 | 0.5231078 | 4.617756771e-05 / 5.296259191e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_033` | 7.974770935e-05 | 2.354113057e-05 | 1.032888399e-04 | 0.5231078 | 4.617756771e-05 / 5.296259191e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_034` | 7.974770935e-05 | 2.354113057e-05 | 1.032888399e-04 | 0.5231078 | 4.617756771e-05 / 5.296259191e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_035` | 7.974770935e-05 | 2.354113057e-05 | 1.032888399e-04 | 0.5231078 | 4.617756771e-05 / 5.296259191e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_036` | 7.974770935e-05 | 2.354113057e-05 | 1.032888399e-04 | 0.5231078 | 4.617756771e-05 / 5.296259191e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_037` | 5.357061396e-05 | 1.757959774e-05 | 7.115021170e-05 | 0.5460349 | 1.403893950e-05 / 2.082396370e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_038` | 5.917911200e-05 | 2.357007963e-05 | 8.274919163e-05 | 0.5236326 | 2.563791943e-05 / 3.242294363e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_039` | 5.357061396e-05 | 1.757959774e-05 | 7.115021170e-05 | 0.5460349 | 1.403893950e-05 / 2.082396370e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_040` | 5.917911200e-05 | 2.357007963e-05 | 8.274919163e-05 | 0.5236326 | 2.563791943e-05 / 3.242294363e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_041` | 5.917911200e-05 | 2.357007963e-05 | 8.274919163e-05 | 0.5236326 | 2.563791943e-05 / 3.242294363e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_042` | 5.357061396e-05 | 1.757959774e-05 | 7.115021170e-05 | 0.5460349 | 1.403893950e-05 / 2.082396370e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_043` | 5.357061396e-05 | 1.757959774e-05 | 7.115021170e-05 | 0.5460349 | 1.403893950e-05 / 2.082396370e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_044` | 5.917911200e-05 | 2.357007963e-05 | 8.274919163e-05 | 0.5236326 | 2.563791943e-05 / 3.242294363e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_045` | 5.917911200e-05 | 2.357007963e-05 | 8.274919163e-05 | 0.5236326 | 2.563791943e-05 / 3.242294363e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_046` | 5.357061396e-05 | 1.757959774e-05 | 7.115021170e-05 | 0.5460349 | 1.403893950e-05 / 2.082396370e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_047` | 5.357061396e-05 | 1.757959774e-05 | 7.115021170e-05 | 0.5460349 | 1.403893950e-05 / 2.082396370e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_048` | 5.917911200e-05 | 2.357007963e-05 | 8.274919163e-05 | 0.5236326 | 2.563791943e-05 / 3.242294363e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_049` | 5.917911200e-05 | 2.357007963e-05 | 8.274919163e-05 | 0.5236326 | 2.563791943e-05 / 3.242294363e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_050` | 5.917911200e-05 | 2.357007963e-05 | 8.274919163e-05 | 0.5236326 | 2.563791943e-05 / 3.242294363e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_051` | 5.917911200e-05 | 2.357007963e-05 | 8.274919163e-05 | 0.5236326 | 2.563791943e-05 / 3.242294363e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_052` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_053` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_054` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_055` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_056` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_057` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_058` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_059` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_060` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_061` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_062` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_063` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_064` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_065` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_066` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_067` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_068` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_069` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_070` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_071` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_072` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_073` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_074` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_075` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_076` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_077` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_078` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_079` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_080` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_081` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_082` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_083` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_084` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_085` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_086` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_087` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_088` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_089` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_090` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_091` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_092` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_093` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_094` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_095` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_096` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_097` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_098` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_099` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_100` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_101` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_102` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_103` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_104` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_105` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_106` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_107` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_108` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_109` | 5.399110824e-05 | 2.056816809e-05 | 7.455927634e-05 | 0.5341710 | 1.744800414e-05 / 2.423302834e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_110` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_111` | 5.677155988e-05 | 2.373816988e-05 | 8.050972976e-05 | 0.5231058 | 2.339845756e-05 / 3.018348176e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_112` | 6.741108330e-05 | 1.968345128e-05 | 8.709453458e-05 | 0.5357744 | 2.998326238e-05 / 3.676828658e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_113` | 7.119020161e-05 | 2.275662557e-05 | 9.394682718e-05 | 0.5246760 | 3.683555498e-05 / 4.362057918e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_114` | 7.119020161e-05 | 2.275662557e-05 | 9.394682718e-05 | 0.5246760 | 3.683555498e-05 / 4.362057918e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_115` | 6.741108330e-05 | 1.968345128e-05 | 8.709453458e-05 | 0.5357744 | 2.998326238e-05 / 3.676828658e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_116` | 6.741108330e-05 | 1.968345128e-05 | 8.709453458e-05 | 0.5357744 | 2.998326238e-05 / 3.676828658e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_117` | 7.119020161e-05 | 2.275662557e-05 | 9.394682718e-05 | 0.5246760 | 3.683555498e-05 / 4.362057918e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_118` | 7.119020161e-05 | 2.275662557e-05 | 9.394682718e-05 | 0.5246760 | 3.683555498e-05 / 4.362057918e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d6_c11_s4_119` | 6.741108330e-05 | 1.968345128e-05 | 8.709453458e-05 | 0.5357744 | 2.998326238e-05 / 3.676828658e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_000` | 5.258120322e-05 | 1.769491863e-05 | 7.027612185e-05 | 0.5454898 | 1.316484965e-05 / 1.994987385e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_001` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_002` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_003` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_004` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_005` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_006` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_007` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_008` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_009` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_010` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_011` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_012` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_013` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_014` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_015` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_016` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_017` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_018` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_019` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_020` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_021` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_022` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_023` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_024` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_025` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_026` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_027` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_028` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_029` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_030` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_031` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_032` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_033` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_034` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_035` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_036` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_037` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_038` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_039` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_040` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_041` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_042` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_043` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_044` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_045` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_046` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_047` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_048` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_049` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_050` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_051` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_052` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_053` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_054` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_055` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_056` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_057` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_058` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_059` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_060` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_061` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_062` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_063` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_064` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_065` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_066` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_067` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_068` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_069` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_070` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_071` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_072` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_073` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_074` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_075` | 9.401625874e-05 | 3.206801020e-05 | 1.260842689e-04 | 0.5001687 | 6.897299674e-05 / 7.575802094e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_076` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_077` | 8.528400487e-05 | 2.467731348e-05 | 1.099613183e-04 | 0.5215089 | 5.285004614e-05 / 5.963507034e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_078` | 1.223191365e-04 | 3.891979956e-05 | 1.612389360e-04 | 0.4864746 | 1.041276638e-04 / 1.109126880e-04 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_079` | 1.223191365e-04 | 3.891979956e-05 | 1.612389360e-04 | 0.4864746 | 1.041276638e-04 / 1.109126880e-04 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_080` | 1.223191365e-04 | 3.891979956e-05 | 1.612389360e-04 | 0.4864746 | 1.041276638e-04 / 1.109126880e-04 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_081` | 1.223191365e-04 | 3.891979956e-05 | 1.612389360e-04 | 0.4864746 | 1.041276638e-04 / 1.109126880e-04 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_082` | 1.223191365e-04 | 3.891979956e-05 | 1.612389360e-04 | 0.4864746 | 1.041276638e-04 / 1.109126880e-04 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_083` | 1.223191365e-04 | 3.891979956e-05 | 1.612389360e-04 | 0.4864746 | 1.041276638e-04 / 1.109126880e-04 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_084` | 1.223191365e-04 | 3.891979956e-05 | 1.612389360e-04 | 0.4864746 | 1.041276638e-04 / 1.109126880e-04 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_085` | 1.223191365e-04 | 3.891979956e-05 | 1.612389360e-04 | 0.4864746 | 1.041276638e-04 / 1.109126880e-04 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_086` | 1.223191365e-04 | 3.891979956e-05 | 1.612389360e-04 | 0.4864746 | 1.041276638e-04 / 1.109126880e-04 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_087` | 1.223191365e-04 | 3.891979956e-05 | 1.612389360e-04 | 0.4864746 | 1.041276638e-04 / 1.109126880e-04 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_088` | 5.336707884e-05 | 1.715511805e-05 | 7.052219689e-05 | 0.5470915 | 1.341092469e-05 / 2.019594889e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_089` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_090` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_091` | 5.621790936e-05 | 1.995574718e-05 | 7.617365654e-05 | 0.5357437 | 1.906238434e-05 / 2.584740854e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_092` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_093` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_094` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_095` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_096` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_097` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_098` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_099` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_100` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_101` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_102` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_103` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_104` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_105` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_106` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_107` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_108` | 5.621790936e-05 | 1.995574718e-05 | 7.617365654e-05 | 0.5357437 | 1.906238434e-05 / 2.584740854e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_109` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_110` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_111` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_112` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_113` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_114` | 6.474761455e-05 | 3.011207534e-05 | 9.485968989e-05 | 0.5031774 | 3.774841769e-05 / 4.453344189e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_115` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_116` | 5.621790936e-05 | 1.995574718e-05 | 7.617365654e-05 | 0.5357437 | 1.906238434e-05 / 2.584740854e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_117` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_118` | 5.906493878e-05 | 2.304141197e-05 | 8.210635075e-05 | 0.5246459 | 2.499507855e-05 / 3.178010275e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c11_s2_119` | 5.621790936e-05 | 1.995574718e-05 | 7.617365654e-05 | 0.5357437 | 1.906238434e-05 / 2.584740854e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_000` | 7.254242683e-05 | 2.332639036e-05 | 9.586881719e-05 | 0.5235984 | 3.875754499e-05 / 4.554256919e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_001` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_002` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_003` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_004` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_005` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_006` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_007` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_008` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_009` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_010` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_011` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_012` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_013` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_014` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_015` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_016` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_017` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_018` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_019` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_020` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_021` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_022` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_023` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_024` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_025` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_026` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_027` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_028` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_029` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_030` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_031` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_032` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_033` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_034` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_035` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_036` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_037` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_038` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_039` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_040` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_041` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_042` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_043` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_044` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_045` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_046` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_047` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_048` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_049` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_050` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_051` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_052` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_053` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_054` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_055` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_056` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_057` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_058` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_059` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_060` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_061` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_062` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_063` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_064` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_065` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_066` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_067` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_068` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_069` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_070` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_071` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_072` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_073` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_074` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_075` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_076` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_077` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_078` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_079` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_080` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_081` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_082` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_083` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_084` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_085` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_086` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_087` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_088` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_089` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_090` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_091` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_092` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_093` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_094` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_095` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_096` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_097` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_098` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_099` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_100` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_101` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_102` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_103` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_104` | 8.967800962e-05 | 3.150906829e-05 | 1.211870779e-04 | 0.5002067 | 6.407580571e-05 / 7.086082991e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_105` | 9.638503598e-05 | 2.861856651e-05 | 1.250036025e-04 | 0.5087852 | 6.789233029e-05 / 7.467735449e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_106` | 1.078980806e-04 | 3.686202144e-05 | 1.447601021e-04 | 0.4879929 | 8.764882985e-05 / 9.443385405e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_107` | 1.078980806e-04 | 3.686202144e-05 | 1.447601021e-04 | 0.4879929 | 8.764882985e-05 / 9.443385405e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_108` | 9.638503598e-05 | 2.861856651e-05 | 1.250036025e-04 | 0.5087852 | 6.789233029e-05 / 7.467735449e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_109` | 9.638503598e-05 | 2.861856651e-05 | 1.250036025e-04 | 0.5087852 | 6.789233029e-05 / 7.467735449e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_110` | 1.078980806e-04 | 3.686202144e-05 | 1.447601021e-04 | 0.4879929 | 8.764882985e-05 / 9.443385405e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_111` | 1.078980806e-04 | 3.686202144e-05 | 1.447601021e-04 | 0.4879929 | 8.764882985e-05 / 9.443385405e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_112` | 9.638503598e-05 | 2.861856651e-05 | 1.250036025e-04 | 0.5087852 | 6.789233029e-05 / 7.467735449e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_113` | 9.638503598e-05 | 2.861856651e-05 | 1.250036025e-04 | 0.5087852 | 6.789233029e-05 / 7.467735449e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_114` | 1.078980806e-04 | 3.686202144e-05 | 1.447601021e-04 | 0.4879929 | 8.764882985e-05 / 9.443385405e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_115` | 1.078980806e-04 | 3.686202144e-05 | 1.447601021e-04 | 0.4879929 | 8.764882985e-05 / 9.443385405e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_116` | 9.638503598e-05 | 2.861856651e-05 | 1.250036025e-04 | 0.5087852 | 6.789233029e-05 / 7.467735449e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_117` | 9.638503598e-05 | 2.861856651e-05 | 1.250036025e-04 | 0.5087852 | 6.789233029e-05 / 7.467735449e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_118` | 1.078980806e-04 | 3.686202144e-05 | 1.447601021e-04 | 0.4879929 | 8.764882985e-05 / 9.443385405e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `amb_d8_c12_s5_119` | 1.078980806e-04 | 3.686202144e-05 | 1.447601021e-04 | 0.4879929 | 8.764882985e-05 / 9.443385405e-05 | Independent A encoder: extra live-state exposure and A/data fault pairs |
| `control_original` | 5.339009211e-05 | 1.676437037e-05 | 7.015446248e-05 | 0.5415451 | 1.304319028e-05 / 1.982821448e-05 | Reset/init and readout control |
| `interleave_r45_k4_s3_w0` | 9.106628990e-05 | 7.520213366e-05 | 1.662684236e-04 | 0.3323696 | 1.091571514e-04 / 1.159421756e-04 | Separate B/C: 48 moves and long live-state exposure |
| `mb_control` | 5.389009211e-05 | 1.702257370e-05 | 7.091266581e-05 | 0.5455310 | 1.380139361e-05 / 2.058641781e-05 | Reset/init and readout control |
| `mblns_s0_000` | 5.404929247e-05 | 1.711278033e-05 | 7.116207280e-05 | 0.5447342 | 1.405080060e-05 / 2.083582480e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_000_orig` | 5.334995878e-05 | 1.697345735e-05 | 7.032341613e-05 | 0.5403939 | 1.321214393e-05 / 1.999716813e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_001` | 5.435329878e-05 | 1.721898000e-05 | 7.157227878e-05 | 0.5443051 | 1.446100658e-05 / 2.124603078e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_001_orig` | 5.390774879e-05 | 1.716875658e-05 | 7.107650536e-05 | 0.5394328 | 1.396523316e-05 / 2.075025736e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_002` | 5.435992100e-05 | 1.741260106e-05 | 7.177252207e-05 | 0.5436530 | 1.466124987e-05 / 2.144627407e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_002_orig` | 5.391437101e-05 | 1.730254229e-05 | 7.121691330e-05 | 0.5389663 | 1.410564110e-05 / 2.089066530e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_003` | 5.465760989e-05 | 1.743980737e-05 | 7.209741726e-05 | 0.5436175 | 1.498614506e-05 / 2.177116926e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_003_orig` | 5.450103768e-05 | 1.735272777e-05 | 7.185376545e-05 | 0.5385712 | 1.474249325e-05 / 2.152751745e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_004_orig` | 5.724963955e-05 | 1.794013354e-05 | 7.518977309e-05 | 0.5355017 | 1.807850089e-05 / 2.486352509e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_005_orig` | 5.997215887e-05 | 1.786756209e-05 | 7.783972096e-05 | 0.5348260 | 2.072844876e-05 / 2.751347296e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_006_orig` | 6.316241122e-05 | 1.850265021e-05 | 8.166506143e-05 | 0.5321493 | 2.455378923e-05 / 3.133881343e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_007_orig` | 6.159734131e-05 | 1.864031473e-05 | 8.023765604e-05 | 0.5339391 | 2.312638384e-05 / 2.991140804e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_007_original` | 6.159734131e-05 | 1.864031473e-05 | 8.023765604e-05 | 0.5339391 | 2.312638384e-05 / 2.991140804e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_008` | 6.224724125e-05 | 1.785847409e-05 | 8.010571534e-05 | 0.5414061 | 2.299444314e-05 / 2.977946734e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_008_orig` | 6.460467378e-05 | 1.820755161e-05 | 8.281222540e-05 | 0.5328225 | 2.570095320e-05 / 3.248597740e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_009_orig` | 6.850070045e-05 | 1.834671244e-05 | 8.684741289e-05 | 0.5313001 | 2.973614069e-05 / 3.652116489e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_010_orig` | 6.268318252e-05 | 1.794424948e-05 | 8.062743200e-05 | 0.5341997 | 2.351615980e-05 / 3.030118400e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_011_orig` | 6.286587892e-05 | 1.801951392e-05 | 8.088539284e-05 | 0.5328410 | 2.377412064e-05 / 3.055914484e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s0_012_orig` | 6.286587892e-05 | 1.810342677e-05 | 8.096930569e-05 | 0.5325924 | 2.385803349e-05 / 3.064305769e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_000` | 5.404929247e-05 | 1.711278033e-05 | 7.116207280e-05 | 0.5447342 | 1.405080060e-05 / 2.083582480e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_000_orig` | 5.334995878e-05 | 1.697345735e-05 | 7.032341613e-05 | 0.5403939 | 1.321214393e-05 / 1.999716813e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_001_orig` | 5.812941695e-05 | 1.703956835e-05 | 7.516898529e-05 | 0.5389612 | 1.805771309e-05 / 2.484273729e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_002_orig` | 5.820483027e-05 | 1.753405411e-05 | 7.573888438e-05 | 0.5376384 | 1.862761218e-05 / 2.541263638e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_003` | 5.530391509e-05 | 1.736888004e-05 | 7.267279512e-05 | 0.5432144 | 1.556152292e-05 / 2.234654712e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_003_orig` | 5.466938732e-05 | 1.717583303e-05 | 7.184522035e-05 | 0.5390702 | 1.473394815e-05 / 2.151897235e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_004` | 5.530924802e-05 | 1.764589193e-05 | 7.295513995e-05 | 0.5428136 | 1.584386775e-05 / 2.262889195e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_004_orig` | 5.537584026e-05 | 1.783624556e-05 | 7.321208582e-05 | 0.5358043 | 1.610081362e-05 / 2.288583782e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_005_orig` | 5.627721843e-05 | 1.805109110e-05 | 7.432830953e-05 | 0.5350576 | 1.721703733e-05 / 2.400206153e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_006` | 6.325809604e-05 | 1.910882875e-05 | 8.236692480e-05 | 0.5366680 | 2.525565260e-05 / 3.204067680e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_006_orig` | 6.234926327e-05 | 1.906545901e-05 | 8.141472228e-05 | 0.5313243 | 2.430345008e-05 / 3.108847428e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_007` | 6.147386377e-05 | 1.935663302e-05 | 8.083049679e-05 | 0.5348992 | 2.371922459e-05 / 3.050424879e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_007_orig` | 6.045330016e-05 | 1.926106782e-05 | 7.971436797e-05 | 0.5299279 | 2.260309577e-05 / 2.938811997e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_008_orig` | 6.932251067e-05 | 1.839992826e-05 | 8.772243892e-05 | 0.5309938 | 3.061116672e-05 / 3.739619092e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s1_009_orig` | 6.299416033e-05 | 1.840444186e-05 | 8.139860219e-05 | 0.5324220 | 2.428732999e-05 / 3.107235419e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_000` | 5.397644779e-05 | 1.755109267e-05 | 7.152754046e-05 | 0.5437910 | 1.441626826e-05 / 2.120129246e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_000_orig` | 5.347644779e-05 | 1.723218534e-05 | 7.070863312e-05 | 0.5399978 | 1.359736092e-05 / 2.038238512e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_001` | 5.449840954e-05 | 1.734991219e-05 | 7.184832173e-05 | 0.5444127 | 1.473704953e-05 / 2.152207373e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_001_orig` | 5.454117101e-05 | 1.714326924e-05 | 7.168444024e-05 | 0.5397185 | 1.457316804e-05 / 2.135819224e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_002_orig` | 5.991906258e-05 | 1.765256435e-05 | 7.757162692e-05 | 0.5359653 | 2.046035472e-05 / 2.724537892e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_003_orig` | 5.918207494e-05 | 1.764006213e-05 | 7.682213707e-05 | 0.5353532 | 1.971086487e-05 / 2.649588907e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_004_orig` | 6.316241122e-05 | 1.850265021e-05 | 8.166506143e-05 | 0.5321493 | 2.455378923e-05 / 3.133881343e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_005` | 6.025763599e-05 | 1.849803965e-05 | 7.875567565e-05 | 0.5401836 | 2.164440345e-05 / 2.842942765e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_005_orig` | 5.924555621e-05 | 1.837988806e-05 | 7.762544428e-05 | 0.5355274 | 2.051417208e-05 / 2.729919628e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_006` | 5.941737469e-05 | 1.820159767e-05 | 7.761897236e-05 | 0.5414151 | 2.050770016e-05 / 2.729272436e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_006_orig` | 5.791882509e-05 | 1.806798372e-05 | 7.598680881e-05 | 0.5370999 | 1.887553661e-05 / 2.566056081e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_007` | 5.989129707e-05 | 1.872682646e-05 | 7.861812353e-05 | 0.5391086 | 2.150685133e-05 / 2.829187553e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s2_007_orig` | 5.863326458e-05 | 1.879715759e-05 | 7.743042216e-05 | 0.5333974 | 2.031914996e-05 / 2.710417416e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_000` | 5.404929247e-05 | 1.711278033e-05 | 7.116207280e-05 | 0.5447342 | 1.405080060e-05 / 2.083582480e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_000_orig` | 5.334995878e-05 | 1.697345735e-05 | 7.032341613e-05 | 0.5403939 | 1.321214393e-05 / 1.999716813e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_001` | 5.434707025e-05 | 1.713985342e-05 | 7.148692366e-05 | 0.5446979 | 1.437565146e-05 / 2.116067566e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_001_orig` | 5.393662545e-05 | 1.702310572e-05 | 7.095973116e-05 | 0.5399978 | 1.384845896e-05 / 2.063348316e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_002` | 5.412902592e-05 | 1.744938934e-05 | 7.157841526e-05 | 0.5436480 | 1.446714306e-05 / 2.125216726e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_002_orig` | 5.349635890e-05 | 1.739555122e-05 | 7.089191012e-05 | 0.5400359 | 1.378063792e-05 / 2.056566212e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_003` | 5.465760989e-05 | 1.743980737e-05 | 7.209741726e-05 | 0.5436175 | 1.498614506e-05 / 2.177116926e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_003_orig` | 5.450103768e-05 | 1.735272777e-05 | 7.185376545e-05 | 0.5385712 | 1.474249325e-05 / 2.152751745e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_004_orig` | 5.836966256e-05 | 1.812699926e-05 | 7.649666183e-05 | 0.5363034 | 1.938538963e-05 / 2.617041383e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_005` | 5.900591674e-05 | 1.824765301e-05 | 7.725356975e-05 | 0.5385690 | 2.014229755e-05 / 2.692732175e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_005_orig` | 5.923730507e-05 | 1.829675918e-05 | 7.753406425e-05 | 0.5326853 | 2.042279205e-05 / 2.720781625e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_006_orig` | 6.076360111e-05 | 1.832396311e-05 | 7.908756422e-05 | 0.5325830 | 2.197629202e-05 / 2.876131622e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_007` | 6.123637789e-05 | 1.804152477e-05 | 7.927790265e-05 | 0.5397631 | 2.216663045e-05 / 2.895165465e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_007_orig` | 6.098537823e-05 | 1.849406203e-05 | 7.947944026e-05 | 0.5320885 | 2.236816806e-05 / 2.915319226e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_008_orig` | 7.015397688e-05 | 1.833088370e-05 | 8.848486059e-05 | 0.5310950 | 3.137358839e-05 / 3.815861259e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_009` | 6.373654592e-05 | 1.735823242e-05 | 8.109477834e-05 | 0.5429296 | 2.398350614e-05 / 3.076853034e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_009_orig` | 6.908179715e-05 | 1.819041757e-05 | 8.727221472e-05 | 0.5322041 | 3.016094252e-05 / 3.694596672e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_010_orig` | 6.319999412e-05 | 1.811031819e-05 | 8.131031231e-05 | 0.5334777 | 2.419904011e-05 / 3.098406431e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_011` | 5.844688093e-05 | 1.711096315e-05 | 7.555784408e-05 | 0.5452496 | 1.844657188e-05 / 2.523159608e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_011_orig` | 6.276577250e-05 | 1.807368896e-05 | 8.083946145e-05 | 0.5339412 | 2.372818925e-05 / 3.051321345e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s3_012_orig` | 6.534181632e-05 | 1.814286017e-05 | 8.348467649e-05 | 0.5334787 | 2.637340429e-05 / 3.315842849e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s4_000_orig` | 5.659306672e-05 | 1.721607745e-05 | 7.380914418e-05 | 0.5382462 | 1.669787198e-05 / 2.348289618e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s4_001` | 5.785391215e-05 | 1.767862534e-05 | 7.553253749e-05 | 0.5415574 | 1.842126529e-05 / 2.520628949e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s4_001_orig` | 5.659968894e-05 | 1.735108333e-05 | 7.395077228e-05 | 0.5377806 | 1.683950008e-05 / 2.362452428e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s4_002_orig` | 5.959861222e-05 | 1.779695743e-05 | 7.739556965e-05 | 0.5361754 | 2.028429745e-05 / 2.706932165e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s4_003_orig` | 5.926083444e-05 | 1.758839584e-05 | 7.684923028e-05 | 0.5363919 | 1.973795808e-05 / 2.652298228e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s4_004_orig` | 5.991906258e-05 | 1.765256435e-05 | 7.757162692e-05 | 0.5359653 | 2.046035472e-05 / 2.724537892e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s4_005_orig` | 7.047542742e-05 | 1.909389224e-05 | 8.956931966e-05 | 0.5300405 | 3.245804746e-05 / 3.924307166e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s4_006` | 6.600423458e-05 | 1.875595180e-05 | 8.476018638e-05 | 0.5387600 | 2.764891418e-05 / 3.443393838e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s4_006_orig` | 6.494738971e-05 | 1.904258026e-05 | 8.398996997e-05 | 0.5299020 | 2.687869777e-05 / 3.366372197e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s4_007_orig` | 6.593219078e-05 | 1.873384579e-05 | 8.466603657e-05 | 0.5306080 | 2.755476437e-05 / 3.433978857e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_000` | 5.397644779e-05 | 1.755109267e-05 | 7.152754046e-05 | 0.5437910 | 1.441626826e-05 / 2.120129246e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_000_orig` | 5.347644779e-05 | 1.723695729e-05 | 7.071340508e-05 | 0.5408985 | 1.360213288e-05 / 2.038715708e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_001` | 5.449840954e-05 | 1.734991219e-05 | 7.184832173e-05 | 0.5444127 | 1.473704953e-05 / 2.152207373e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_001_orig` | 5.454117101e-05 | 1.714882757e-05 | 7.168999858e-05 | 0.5406187 | 1.457872638e-05 / 2.136375058e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_002_orig` | 5.728977288e-05 | 1.773330296e-05 | 7.502307583e-05 | 0.5375376 | 1.791180363e-05 / 2.469682783e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_003_orig` | 5.724963955e-05 | 1.794683349e-05 | 7.519647304e-05 | 0.5363949 | 1.808520084e-05 / 2.487022504e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_004_orig` | 6.331723484e-05 | 2.237996475e-05 | 8.569719959e-05 | 0.5228350 | 2.858592739e-05 / 3.537095159e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_005_orig` | 7.451279495e-05 | 2.367529490e-05 | 9.818808985e-05 | 0.5176741 | 4.107681765e-05 / 4.786184185e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_006_orig` | 7.254486251e-05 | 2.328020881e-05 | 9.582507131e-05 | 0.5181326 | 3.871379911e-05 / 4.549882331e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_007_orig` | 6.424061001e-05 | 2.357688372e-05 | 8.781749373e-05 | 0.5217978 | 3.070622153e-05 / 3.749124573e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_008_orig` | 6.693685177e-05 | 2.435156354e-05 | 9.128841531e-05 | 0.5173716 | 3.417714311e-05 / 4.096216731e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `mblns_s5_009_orig` | 6.356871347e-05 | 1.933010719e-05 | 8.289882066e-05 | 0.5333762 | 2.578754846e-05 / 3.257257266e-05 | Measured-helper BC: routing/fault correlations exceed saved CX cost |
| `zero_endpoint_blue_q5_t37` | 5.019277595e-05 | 1.351065030e-05 | 6.370342625e-05 | 0.5149572 | 6.592154052e-06 / 1.337717825e-05 | Transient known-zero measurement catches BC preparation faults |
| `zero_endpoint_q4_t41` | 5.217194233e-05 | 1.591339231e-05 | 6.808533463e-05 | 0.5447252 | 1.097406243e-05 / 1.775908663e-05 | Transient known-zero measurement catches BC preparation faults |
| `zero_endpoint_q4_t42` | 5.217194233e-05 | 1.590255541e-05 | 6.807449774e-05 | 0.5447252 | 1.096322554e-05 / 1.774824974e-05 | Transient known-zero measurement catches BC preparation faults |
| `zero_endpoint_q5_t34` | 5.198527566e-05 | 1.585125276e-05 | 6.783652842e-05 | 0.5447257 | 1.072525622e-05 / 1.751028042e-05 | Transient known-zero measurement catches BC preparation faults |

</details>

- `sepbc_v29c_q5_t37`: {"T3a": 1.7450908017869903e-05, "c1": 2.405483220021123e-19, "exp_minus_A1": 0.5070688256450283, "pair_seconds": 0.4101205580518581, "pairs": 883, "second": 4.918889465736463e-05, "seconds": 0.617368373030331, "seconds_total": 0.9929148760274984, "sha256": "d077c94db9f8b673a5d019caf99f5abdf38aa739c884f8b57d5d285bbc33ac25", "t3bc": -4.272327062275195e-06, "table_keys": 4942, "third": 1.3178580955594709e-05, "total": 6.236747561295933e-05, "triples": 21007} Mechanism/scope: Known-zero B/C intermediate wire measured during an idle slot, with its own detector; full physical noisy instrument.

- `sepbc_v29c_q5_t38`: {"T3a": 1.742417440761327e-05, "c1": 2.405483220021123e-19, "exp_minus_A1": 0.5070688256450282, "pair_seconds": 0.2339994790381752, "pairs": 883, "second": 4.9122227990697964e-05, "seconds": 0.3898120970115997, "seconds_total": 0.6524964810232632, "sha256": "1319ba3cc85d668d50b201bb4655b15f73e560e3c49f1fbf4698da2a96e45564", "t3bc": -4.266456303878016e-06, "table_keys": 4942, "third": 1.3157718103735255e-05, "total": 6.227994609443323e-05, "triples": 21007} Mechanism/scope: Known-zero B/C intermediate wire measured during an idle slot, with its own detector; full physical noisy instrument.

- `sepbc_v29c_z5_t37`: {"T3a": 1.7450908017869903e-05, "c1": 2.405483220021123e-19, "exp_minus_A1": 0.5070688256450283, "pair_seconds": 0.27890094299800694, "pairs": 883, "second": 4.918889465736463e-05, "seconds": 0.47500399401178584, "seconds_total": 0.7014865110395476, "sha256": "d077c94db9f8b673a5d019caf99f5abdf38aa739c884f8b57d5d285bbc33ac25", "t3bc": -4.272327062275195e-06, "table_keys": 4942, "third": 1.3178580955594709e-05, "total": 6.236747561295933e-05, "triples": 21007} Mechanism/scope: Exact known-state check with symbolic preparation record frame.
