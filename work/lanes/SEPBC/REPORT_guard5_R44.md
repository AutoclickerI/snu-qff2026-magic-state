Status: COMPLETE — R44 finalist below 5e-5. Previous delivery: [REPORT_v31s.md](REPORT_v31s.md).

## Verified finalists

| Stem | R / CX | All orders | Acceptance | exp(-A1) | 1e6 judge on zebra | MC3 mean |
|---|---:|---:|---:|---:|---|---:|
| [v31/guard5_timing_0](v31/guard5_timing_0.qasm) | 44 / 204 | 4.914301799628e-05 | 0.500663840 | 0.500811631 | 4.6s, PASS, FAST | 4.9016060e-05 |
| [v31/guard5_timing_1](v31/guard5_timing_1.qasm) | 44 / 204 | 4.914394277487e-05 | 0.501000711 | 0.501149175 | 3.9s, PASS, FAST | 4.9200150e-05 |
| [v31/guard_joint_2](v31/guard_joint_2.qasm) | 44 / 200 | 5.020949490049e-05 | 0.510658874 | 0.510779090 | 4.7s, PASS, FAST | 5.0157110e-05 |

Choose **guard5_timing_0** by all-orders loss: 11.578% below v31s. Cubic parts: second=4.207232312353e-05, third=6.755800004375e-06, total=4.882812312790e-05, c1=2.794e-19. Seed-0 acceptance is 0.500929 at 1e6 and 0.50064 at 1e8. MC seeds 0/1000/2000 give 4.970669e-5 / 4.782393e-5 / 4.951755e-5. Timing_1 has slightly higher acceptance and an all-orders loss 9.25e-10 higher.

The first fast composition, full_timing_0, completed MC at 22:54 KST, before the 23:05 target: all-orders 5.47613043144e-5, MC mean 5.520342e-5. The first R44 finalist A44_timing_10 completed MC around 23:07: all-orders 5.34509514949e-5, MC mean 5.341976e-5. The final five-guard result completed after the first deadline. MAIN decides the submission slot. No submissions, commits, pushes or credentials were used. All lane compute jobs have exited.

## Construction and acceptance budget

Data cells remain [0,20,7,10,3,22,21]; A=[1,14,8,9,2,16,15], B=[6,26,13,11,4,23,27], C=[12,25,19,17,5,29,28]. The prefix retains coherent 2-CX data hops. There are no separate-block measured teleports. The 57-CX correlated B/C resource is retained. A still uses 11 CX, but its X-input pivots change from [1,2,9,15] to [1,2,8,14]; q9/q15 reuse their source-zero measurements. The final circuit has 204 CX, 69 detectors, 86 measurements and 47 native steps.

The v30g port includes its q15 terminal instrument, four readout copies, final A14→15 readout edge, measured-Z initialization on q11/q5/q12, and exact-loss timing feedback. R48 timestamps were not copied. The instrument port completes the other commuting q9 fanout before replacing the terminal instrument. Ideal correctness and physical noise were checked on each emitted circuit.

The remaining acceptance budget is spent on five WAITPROT storage guards, repriced in actual R44 idle slots. X guards use R(h), CX(data→h), wait, CX(data→h), MZ(h). The Z guard uses RX(h), CX(h→data), wait, CX(h→data), MX(h). Each measurement is a new zero detector. Final native timings are:

| Data / helper | Axis | Reset | First / second CX | Measurement |
|---|---|---:|---|---:|
| 0 / 6 | Z | 34 | 35 / 39 | 40 |
| 20 / 19 | X | 15 | 18 / 31 | 32 |
| 7 / 13 | X | 19 | 20 / 23 | 24 |
| 10 / 11 | X | 18 | 19 / 28 | 29 |
| 4 / 5 | X | 17 | 18 / 32 | 33 |

All guard CX, reset, measurement and idle noise is included. The sixth proposed guard (data10/helper4, Z) has no native idle slot within the tested window.

| Single guard on A44_feedback_0 | Cubic saved | A1 spent | Saved / A1 spent |
|---|---:|---:|---:|
| guard_2: [7, 13, 'X', 20, 23] | 8.7791163e-07 | 0.0038720 | 2.2673379e-04 |
| guard_0: [0, 6, 'Z', 35, 39] | 7.7229311e-07 | 0.0048985 | 1.5765819e-04 |
| guard_5: [4, 5, 'X', 18, 31] | 9.4215190e-07 | 0.0148298 | 6.3531198e-05 |
| guard_3: [10, 11, 'X', 19, 27] | 5.8656397e-07 | 0.0111986 | 5.2378411e-05 |
| guard_1: [20, 19, 'X', 18, 31] | 3.6143233e-07 | 0.0138860 | 2.6028522e-05 |

Every subset of the five feasible guards was jointly screened. Untimed all-five guards fail acceptance: proxy 0.49812577, all-orders 0.49800612. Timing feedback improves loss and restores proxy acceptance to 0.50081163. Replacing the later q5/q11 initialization by the guard readout worsens loss; q19/q13 reuse gives no useful gain. Eight tested idle-slot repeats of known measured states have zero cubic gain and spend acceptance. The extra q19 measured-zero initialization saves only about 1.7e-9 all-orders on the R45 composition while spending about 0.0085 acceptance; it is not in the final circuit.

## Critical path and round pricing

See [v31/CRITICAL_PATH.md](v31/CRITICAL_PATH.md) for node-level ES/LS and conditional CP certificates. In v31s, a zero-slack suffix runs through the blue-check release and data transfer to q9 source MZ at37, RX9 at38, MX9 at39, A gates40–44 and D→A at45. Reorienting A removes that late q9 X-preparation dependency and yields R44.

The final binding suffix is MX1 at27 → R1 at28 → CX2→1 at29 → CX3→2 at30 → CX8→2 at31 → CX2→8 at32 → CX8→9 at33 → CX9→8 at34 → MZ8 at35 → RX8 at36 → MX8 at37 → A encoder38–43 → D→A at44. Final ready slack: A=0, data hops=4, B/C=5, prefix=8. The v31s emitted-order B/C slack was7; the old R48 figure of12 is not the current slack. The guards use some B/C cells earlier without delaying the round. Readout offsets remain R, R+1 and R+2.

CP-SAT proves R43 infeasible for the fixed R44 operation set under both tested tail CX-commutation and diagonal-control-phase extensions. This is not a lower bound on all architectures. Removing source checks c54/c56 reaches R43 but worsens all-orders to 5.46174068815e-5; removing c57 is much worse (~6.7e-5). A six-cell rank-three factor plus late q9 fanout needs10+2 CX in the enumerated state graph; four selected R44 witnesses score 5.55661–5.84459e-5. The 20 chosen initializations/shortest witnesses do not exhaust alternative encoders.

R45→R44 from the ported design improves all-orders from5.47613043144e-5 to5.34509514949e-5 (−1.31035e-6), including the A change. Controlled delayed-round variants below keep the gate multiset and other timings, placing one terminal resource CX in each added native layer. They measure realizable later-round exposure, not an optimized later-R architecture. Empty global layers are compressed by the native emitter; the initial empty-layer recipe was rejected as an invalid timing experiment.

| Schedule | R | All orders | Acceptance |
|---|---:|---:|---:|
| guard5_timing_0 | 44 | 4.914301799628e-05 | 0.500663840 |
| round_delay_45 | 45 | 5.432458445619e-05 | 0.486914352 |
| round_delay_46 | 46 | 6.036183551797e-05 | 0.473553540 |

## Loss mechanisms

These counterfactual channel removals are nonadditive and are not attainable circuits. Values are cubic loss ×10⁶. No measured block-teleport noise exists. Idle gaps crossing R are grouped with round; operation provenance is retained in each plan.

| Circuit | Full | No pre-round idle | No B/C noise | No A noise | No data-hop noise | Round only |
|---|---:|---:|---:|---:|---:|---:|
| full_timing_0 | 54.274718 | 37.041977 | 47.132845 | 41.448689 | 53.923138 | 28.711730 |
| A44_feedback_0 | 52.445791 | 37.339455 | 45.507288 | 40.250869 | 51.959729 | 28.711730 |
| release_54_56 | 54.226613 | 37.617647 | 47.189706 | 41.912246 | 53.140433 | 28.711730 |
| guard5_timing_0 | 48.828123 | 37.608487 | 42.012589 | 38.402795 | 48.412476 | 28.711730 |

Unchanged exact2 second-order physical-pair sums agree with the moment contraction to <1e-15. Dominant final pair classes:

| Pair class | Loss ×10⁶ |
|---|---:|
| round x round | 28.840000 |
| encoder_a x pre_round_idle | 4.077003 |
| encoder_bc x encoder_bc | 2.180000 |
| encoder_a x encoder_bc | 1.711111 |
| encoder_a x round | 1.622222 |
| encoder_bc x round | 0.817778 |
| encoder_a x prefix | 0.651111 |
| encoder_a x encoder_a | 0.613333 |

Compared with A44_feedback_0, guards/timing reduce A × pre-round-idle pairs from5.763664e-6 to4.077003e-6, and idle × idle from0.774158e-6 to0.111037e-6. Removing the guards’ own physical noise would save about0.53e-6 cubic. R43 source-check removal mainly admits prefix × idle pairs (0.376757e-6→1.394842e-6) and data-hop × idle pairs (+0.398345e-6); its shorter round does not compensate.

## Built-variant ledger

All emitted physical variants have all-orders prices. Non-emitted subset screens are in guard_subsets.json and four_guards.json. Nonfinal plans are archived in v31/nonfinal_plans.json.gz; numeric receipts remain individual files. Gate/MC absent means not run on that comparator; only the selected finalists require all delivery gates. Δ is all-orders loss minus parent v31s, ×10⁶.

| Variant | R | Cubic | exp(-A1) | All orders | Δ ×10⁶ | Gate / MC |
|---|---:|---:|---:|---:|---:|---|
| guard5_timing_0 | 44 | 4.8828123128e-05 | 0.50081163 | 4.914301799628e-05 | -6.434873 | PASS/FAST / 4.9016060e-05 |
| guard5_timing_1 | 44 | 4.8827201939e-05 | 0.50114918 | 4.914394277487e-05 | -6.433948 | PASS/FAST / 4.9200150e-05 |
| reuse_13 | 44 | 4.8827201939e-05 | 0.50098570 | 4.914394607835e-05 | -6.433945 | not run / not selected |
| reuse_19 | 44 | 4.8828798976e-05 | 0.50098215 | 4.914565010071e-05 | -6.432241 | not run / not selected |
| guards_01235 | 44 | 4.8967798709e-05 | 0.49812577 | 4.928421815756e-05 | -6.293673 | acceptance fails / not selected |
| reuse_5 | 44 | 4.9107616094e-05 | 0.50165102 | 4.942505039894e-05 | -6.152841 | not run / not selected |
| guards_0235 | 44 | 4.9269102308e-05 | 0.50509100 | 4.960840730925e-05 | -5.969484 | PASS/FAST / not selected |
| guards_0125 | 44 | 4.9537363967e-05 | 0.50373542 | 4.986783956678e-05 | -5.710052 | not run / not selected |
| reuse_11 | 44 | 4.9744591523e-05 | 0.50165191 | 5.006285529965e-05 | -5.515036 | not run / not selected |
| guards_1235 | 44 | 4.9735459606e-05 | 0.50057184 | 5.006645774889e-05 | -5.511433 | not run / not selected |
| guards_0135 | 44 | 4.9830077373e-05 | 0.50005825 | 5.015062856606e-05 | -5.427263 | acceptance fails / not selected |
| guard_joint_2 | 44 | 4.9854828633e-05 | 0.51077909 | 5.020949490049e-05 | -5.368396 | PASS/FAST / 5.0157110e-05 |
| guards_025 | 44 | 4.9854828633e-05 | 0.51077909 | 5.020949490049e-05 | -5.368396 | not run / not selected |
| guards_0123 | 44 | 4.9882621205e-05 | 0.50556790 | 5.022198987753e-05 | -5.355901 | not run / not selected |
| reuse_5_11 | 44 | 5.0025360286e-05 | 0.50215426 | 5.034433865630e-05 | -5.233553 | not run / not selected |
| guards_235 | 44 | 5.0039163132e-05 | 0.50757127 | 5.039349698724e-05 | -5.184394 | not run / not selected |
| guards_035 | 44 | 5.0146963287e-05 | 0.50705050 | 5.049081651901e-05 | -5.087075 | not run / not selected |
| guards_023 | 44 | 5.0209910223e-05 | 0.51263719 | 5.057432717470e-05 | -5.003564 | not run / not selected |
| guards_125 | 44 | 5.0305862512e-05 | 0.50620904 | 5.065143908645e-05 | -4.926452 | not run / not selected |
| guards_015 | 44 | 5.0399642632e-05 | 0.50568966 | 5.073439483063e-05 | -4.843496 | not run / not selected |
| guards_012 | 44 | 5.0452186463e-05 | 0.51126136 | 5.080612017106e-05 | -4.771771 | not run / not selected |
| guards_135 | 44 | 5.0597788919e-05 | 0.50251381 | 5.093296024690e-05 | -4.644931 | not run / not selected |
| guards_25 | 44 | 5.0625727105e-05 | 0.51328729 | 5.099594553204e-05 | -4.581946 | not run / not selected |
| guard_joint_1 | 44 | 5.0625727105e-05 | 0.51328729 | 5.099594553204e-05 | -4.581946 | not run / not selected |
| guard_5 | 44 | 5.1503638733e-05 | 0.51527859 | 5.187859958417e-05 | -3.699292 | not run / not selected |
| guard_joint_0 | 44 | 5.1503638733e-05 | 0.51527859 | 5.187859958417e-05 | -3.699292 | not run / not selected |
| guard_2 | 44 | 5.1567879010e-05 | 0.52095594 | 5.196452157888e-05 | -3.613370 | not run / not selected |
| guard_0 | 44 | 5.1673497527e-05 | 0.52042143 | 5.205870456470e-05 | -3.519187 | not run / not selected |
| guard_3 | 44 | 5.1859226664e-05 | 0.51715306 | 5.224431042301e-05 | -3.333581 | not run / not selected |
| guard_1 | 44 | 5.2084358311e-05 | 0.51576511 | 5.245875155602e-05 | -3.119140 | not run / not selected |
| A44_feedback_mz19 | 44 | 5.2432470212e-05 | 0.50717564 | 5.283368791940e-05 | -2.744203 | PASS/FAST / not selected |
| A44_feedback_2 | 44 | 5.2434067249e-05 | 0.51525084 | 5.283541328258e-05 | -2.742478 | not run / not selected |
| A44_feedback_1 | 44 | 5.2438335157e-05 | 0.51883490 | 5.283875645850e-05 | -2.739135 | not run / not selected |
| A44_feedback_0 | 44 | 5.2445790638e-05 | 0.52297699 | 5.284740863457e-05 | -2.730483 | not run / not selected |
| A44_timing_10 | 44 | 5.3036110022e-05 | 0.52819114 | 5.345095149492e-05 | -2.126940 | PASS/FAST / 5.3419760e-05 |
| A44_port_10 | 44 | 5.3066882055e-05 | 0.53559989 | 5.348152290448e-05 | -2.096368 | PASS/FAST / not selected |
| A44_timing_11 | 44 | 5.3293764156e-05 | 0.52782520 | 5.370662895559e-05 | -1.871262 | not run / not selected |
| A44_port_11 | 44 | 5.3324172020e-05 | 0.53522882 | 5.373681961006e-05 | -1.841072 | not run / not selected |
| A44_timing_00 | 44 | 5.3434253380e-05 | 0.52819044 | 5.386239258986e-05 | -1.715499 | not run / not selected |
| A44_port_00 | 44 | 5.3466416694e-05 | 0.53560108 | 5.389430503851e-05 | -1.683586 | not run / not selected |
| release_54 | 44 | 5.3772549653e-05 | 0.52903622 | 5.421524350855e-05 | -1.362648 | not run / not selected |
| round_delay_45 | 45 | 5.3879741781e-05 | 0.48701124 | 5.432458445619e-05 | -1.253307 | acceptance fails / not selected |
| release_54_x14 | 44 | 5.4030517350e-05 | 0.52866969 | 5.447115897075e-05 | -1.106732 | not run / not selected |
| release_54_56 | 43 | 5.4226613248e-05 | 0.53608187 | 5.461740688152e-05 | -0.960484 | not run / not selected |
| full_timing_mz19 | 45 | 5.4273156701e-05 | 0.51227431 | 5.475959820945e-05 | -0.818293 | PASS/FAST / not selected |
| full_timing_0 | 45 | 5.4274718182e-05 | 0.52076772 | 5.476130431437e-05 | -0.816587 | PASS/FAST / 5.5203420e-05 |
| checks_joint_0 | 45 | 5.4311135364e-05 | 0.51980622 | 5.479768608097e-05 | -0.780205 | not run / not selected |
| check_08_q19 | 45 | 5.4311135364e-05 | 0.51980622 | 5.479768608097e-05 | -0.780205 | not run / not selected |
| check_05_q21 | 45 | 5.4312696846e-05 | 0.52789588 | 5.479897186006e-05 | -0.778919 | not run / not selected |
| check_06_q22 | 45 | 5.4312696846e-05 | 0.52789588 | 5.479903608248e-05 | -0.778855 | not run / not selected |
| check_03_q16 | 45 | 5.4312696846e-05 | 0.52789635 | 5.479926451838e-05 | -0.778627 | not run / not selected |
| check_00_q20 | 45 | 5.4312696846e-05 | 0.52789588 | 5.479939051873e-05 | -0.778501 | not run / not selected |
| check_01_q19 | 45 | 5.4312696846e-05 | 0.51996949 | 5.479939260014e-05 | -0.778499 | not run / not selected |
| check_02_q13 | 45 | 5.4312696846e-05 | 0.52200263 | 5.479939260019e-05 | -0.778499 | not run / not selected |
| full_port | 45 | 5.4312696846e-05 | 0.52842451 | 5.479939260033e-05 | -0.778499 | PASS/FAST / not selected |
| check_04_q6 | 45 | 5.4312696846e-05 | 0.52371553 | 5.479939260037e-05 | -0.778499 | not run / not selected |
| check_07_q1 | 45 | 5.4312696846e-05 | 0.52754454 | 5.479939260047e-05 | -0.778499 | not run / not selected |
| readout_mz | 45 | 5.4614003862e-05 | 0.52788192 | 5.510381152040e-05 | -0.474080 | not run / not selected |
| instrument | 45 | 5.4780929960e-05 | 0.53705470 | 5.526735824424e-05 | -0.310533 | not run / not selected |
| mz11_5_12 | 45 | 5.4899013666e-05 | 0.53382743 | 5.538795108566e-05 | -0.189940 | not run / not selected |
| copy4 | 45 | 5.4934528380e-05 | 0.53095254 | 5.542229772191e-05 | -0.155593 | not run / not selected |
| edge14 | 45 | 5.4954438263e-05 | 0.53607422 | 5.544660612981e-05 | -0.131285 | not run / not selected |
| mz5_12 | 45 | 5.5014911280e-05 | 0.53471789 | 5.550409037205e-05 | -0.073801 | not run / not selected |
| factor_A_2 | 44 | 5.5072664279e-05 | 0.55118327 | 5.556613453132e-05 | -0.011757 | not run / not selected |
| factor_A_13 | 44 | 5.5890396658e-05 | 0.55169477 | 5.636950556660e-05 | +0.791614 | not run / not selected |
| A_late_10 | 44 | 5.6566912954e-05 | 0.56026084 | 5.700117099335e-05 | +1.423280 | not run / not selected |
| A_late_11 | 44 | 5.6966499547e-05 | 0.55932785 | 5.740305765604e-05 | +1.825166 | not run / not selected |
| A_late_00 | 44 | 5.7501157084e-05 | 0.56126945 | 5.794507336019e-05 | +2.367182 | not run / not selected |
| factor_A_4 | 44 | 5.7880816744e-05 | 0.55228548 | 5.832433426428e-05 | +2.746443 | not run / not selected |
| factor_A_1 | 44 | 5.8004199281e-05 | 0.55210215 | 5.844589486554e-05 | +2.868004 | not run / not selected |
| round_delay_46 | 46 | 5.9740105000e-05 | 0.47360751 | 6.036183551797e-05 | +4.783944 | acceptance fails / not selected |
| release_54_56_57 | 43 | 6.6443583423e-05 | 0.53661822 | 6.686226465144e-05 | +11.284373 | not run / not selected |
| release_54_57 | 44 | 6.6638048799e-05 | 0.52956599 | 6.710870537913e-05 | +11.530814 | not run / not selected |

## Verified versus inferred

Verified: ideal detector/output contract and |c1|<1e-12 for every screened circuit; nearest-neighbor gates and exact emitted schedules; complete all-orders evaluation within its full-barrier, zero-FRAME/no-POSTSELECT scope; final million-shot judge checks, FAST classifications and 3×10⁸-shot MC; conditional R43 CP infeasibility; selected physical-pair sums and noise-removal ablations.

Cubic method: unchanged EVAL Model/Engine and exact categorical moment contraction. At69 detectors an active projector reaches bit64 and the engine’s signed-int64 batch input overflows. Lane-local wide_moments.py checks every identity-projector rejection bit as a Python integer and batches the unchanged active-projector engine. No detector constraint or noise channel is removed. It agrees with original lane moments where supported and with256 unmodified scalar Engine.table cases on each of two circuits (max difference <1e-31); see wide_validation.json. No unchanged exact2 --third CLI receipt is claimed for these >64-detector circuits. Independent all-orders and full judge/MC validate the finalists.

Not established: a global R43 impossibility, all possible helper/encoder designs, an official submission score or leaderboard result. Neighboring MC differences are statistical; all-orders ranks the candidates. Judge speed is measured on zebra. All-orders omission bounds exclude floating-point roundoff and remain in the result JSON.

Reusable tools: build.py, earlier_A.py, near_A.py, feedback.py, waitport.py, guard_subsets.py, four_guards.py, critical_analysis.py and restore_variant.py. Metadata is derived from actual plans, not inherited v30f times. The previous reusable ENDSTATE emitter and mechanism closure remain documented in REPORT_v29c.md.
