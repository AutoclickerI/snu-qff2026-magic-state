Status: COMPLETE — v30f critical-tail redesign; original R48 shortened to R45.

Previous accepted deliveries: [REPORT_v29c.md](REPORT_v29c.md), [REPORT_v28s.md](REPORT_v28s.md). No submissions, commits, pushes, credential access, or other-lane writes.

## Result

Best currently ranked circuit: [v30/sensitivity_tail.qasm](v30/sensitivity_tail.qasm) / [metadata](v30/sensitivity_tail.json). R=45, 189 CX, depth=48; exact parts 4.540620214208e-05 + 9.682136081788e-06 = **5.508833822387e-05**; c1=2.665e-19; exp(-A1)=0.5365032555.

All orders **5.557789120877e-05**, acceptance **0.5364016122**, **5.7007%** below v30f's inherited all-orders 5.893774204218e-05.
MC3 mean **5.584138000e-05**; individual seeds: 0: 5.603096000e-05 (acceptance 0.53640); 1000: 5.552060000e-05 (acceptance 0.53647); 2000: 5.597259000e-05 (acceptance 0.53633).
Judge: 1-F=np.float64(5.0376893797933825e-05) sem=8.65e-06 acc=0.53596 n_2q=189 passed=True (3.6s, 1 procs)
Speed: FAST, XTIM prediction 6.893 s/1e6.

The grid remains data `[0,20,7,10,3,22,21]`, A `[1,14,8,9,2,16,15]`, B `[6,26,13,11,4,23,27]`, C `[12,25,19,17,5,29,28]`. The original data-transfer paths and fused q4/q10 boundary remain. The winning tail variant retains every native operation and detector; timing and commuting order change. The sensitivity variant preserves that R45 order and uses existing timing slack. Initialization times and resource operations in the delivered metadata are rebuilt from the actual native plan; inherited R48 timing fields are replaced.

The bare-tail MC mean5.579558e-5 is slightly below the sensitivity mean5.584138e-5; that difference is far below sampling resolution. Applicable all-orders loss ranks the sensitivity circuit first.

## What actually forces R48

Full operation/edge/slack evidence: [v30/CRITICAL_PATH.md](v30/CRITICAL_PATH.md), [original DAG](v30/critical.json), and [R45 witness DAG](v30/commute_tail.critical.json). Original fixed native order has a zero-slack chain through the blue-check tail, the q8→q9→q15→q21 data transfer, MZ15 at40, RX15 at41, and A encoder gates42–47. The round starts48. The resource is not the binding component.

| Original chain | Earliest ready | Slack to R48 |
|---|---:|---:|
| B/C resource, including actual prefix releases | 36 | 12 |
| A preparation | 48 | 0 |
| Tail coherent transfers/source checks | 41 | 7 |
| Prefix/blue-check operations outside classified transfers | 36 | 12 |
| Terminal T† gates alone | 28 | 20 |

These component slack numbers share dependencies and are not independently shiftable. The critical source-zero measurement/reset before A15 belongs to the transfer/A boundary. Every cell release, native ES/LS and operation slack is tabulated in CRITICAL_PATH.md. Final-round offsets remain D→A/B→C atR, B→D/readout processing atR+1, final readouts atR+2. Readout offsets set total depthR+3 but do not force the original R48 start.

Legal CX reordering moves CX2→8 before CX2→3 in the blue tail, pipelines forward data propagation before coherent source uncomputation, and reorders A's commuting target-8 gates. The resulting actual schedule reaches MZ15 at38, RX15 at39, A gates40–44, and R45. CP-SAT proves R45 optimal for the modeled fixed gate/reset/measurement program even when all CX/CX and valid diagonal-phase/CX-control commutations are allowed. This is not a global architecture bound.

The R48→45 gain in the bare tail variant splits into4.94880e-7 at second order and2.25882e-6 at third order; all-orders gain is2.96245e-6. Its actual gain per removed round step differs from the grid-free sweep because the circuit has different gate/noise structure and the schedule reorders interacting operations.

## Built variants

All losses are conditional 1−F at STANDARD p=1e-3. The screen is a full categorical cubic contraction using unchanged EVAL's model; independent CLI receipts are required separately. All-orders uses the unmodified MAIN/sparse arithmetic (72 canonical), copied locally so outputs stay in SEPBC. MAIN added independent per-key parallel dispatch during this run; all mathematical kernel functions are AST-identical, and the winner is replayed against the current implementation row for row. The software hashes and dispatch diff are retained. Barriers cover every used qubit; no FRAME/POSTSELECT lines. The 64-detector COMP29 composition uses its proven invertible detector-row rewrite only for the unchanged exact2 reference, with complete gate/noise/decoder equivalence checks.

| Stem | R | CX | Second | Third | All orders | Proxy | 1e6 gate | FAST | MC3 mean |
|---|---:|---:|---:|---:|---:|---:|---|---|---:|
| `sensitivity_tail` | 45 | 189 | 4.540620214e-05 | 9.682136082e-06 | 5.5577891209e-05 | 0.5365033 | PASS | FAST | 5.5841380e-05 |
| `commute_tail` | 45 | 189 | 4.570565433e-05 | 9.779979340e-06 | 5.5975290245e-05 | 0.5473150 | PASS | FAST | 5.5795580e-05 |
| `commute_all` | 45 | 189 | 4.755846252e-05 | 9.666479009e-06 | 5.7701794564e-05 | 0.5511451 | PASS | FAST | 5.8498990e-05 |
| `commute_mid` | 45 | 189 | 4.696492125e-05 | 1.095177000e-05 | 5.8442719516e-05 | 0.5538519 | PASS | FAST | 5.7635470e-05 |
| `phase_tail` | 45 | 189 | 4.717947712e-05 | 1.092031316e-05 | 5.8627891373e-05 | 0.5533949 | PASS | FAST | 5.8097960e-05 |
| `critical_comp29` | 45 | 194 | 4.730076847e-05 | 1.082230214e-05 | 5.8644235005e-05 | 0.5445247 | PASS | FAST | 5.9041140e-05 |
| `release_instrument` | 45 | 190 | 4.776552425e-05 | 1.083724655e-05 | 5.9123893945e-05 | 0.5534178 | PASS | FAST | not triggered |
| `release_instrument_drop129` | 45 | 190 | 4.793395687e-05 | 1.079405429e-05 | 5.9250455020e-05 | 0.5539547 | PASS | FAST | not triggered |
| `release_drop129` | 45 | 189 | 4.793395687e-05 | 1.089072572e-05 | 5.9353616598e-05 | 0.5539214 | PASS | FAST | not triggered |
| `release_drop9` | 45 | 189 | 4.798718433e-05 | 1.086553067e-05 | 5.9379140387e-05 | 0.5531899 | PASS | FAST | not triggered |
| `phase_all` | 45 | 189 | 5.022370522e-05 | 9.684641881e-06 | 6.0389704999e-05 | 0.5510826 | PASS | FAST | not triggered |
| `a_depth5` | 45 | 189 | 5.820515091e-05 | 1.009891126e-05 | 6.8793055159e-05 | 0.5524421 | PASS | FAST | not triggered |

Mechanisms: `commute_tail` is the constructive R48→45 improvement. Moving commuting choices into the earlier prefix (`commute_mid`, `commute_all`, phase variants) gives no further R gain and changes harmful pair/triple exposure. Removing A initialization checks (`release_drop9`, `release_drop129`) does not shorten R; it exposes preparation faults. The imported q15 instrument also does not shorten R. EXENC's five-layer A encoder remains R45 after real cell releases and increases its dangerous-Z tally from10 to25 units of p/15; its full circuit loses. Retiming COMP29's composition toR45 does not preserve all of its original local gains; full scoring determines the result. `sensitivity_tail` spends existing R45 timing slack using the exact pair/triple derivative and reprices all channels.

## Loss split

Noise-removal rows are counterfactual diagnostics; differences interact and cannot be added as independent taxes. A preparation includes its source-zero initialization checks, B/C preparation includes its native resource checks, and idle noise is classified by whether its interval ends beforeR. The complete provenance is in each retained plan and the consolidated numerical ledger.

| Circuit / diagnostic | Full cubic | No pre-round idle | No A noise | No B/C noise | Only round noise |
|---|---:|---:|---:|---:|---:|
| v30f (unchanged input) | 5.823933151e-05 | 3.734955422e-05 | 4.506984557e-05 | 5.011445165e-05 | 2.871251970e-05 |
| a_depth5 | 6.830406217e-05 | 4.208732967e-05 | 4.501021951e-05 | 5.780263899e-05 | 2.871251970e-05 |
| commute_all | 5.722494153e-05 | 3.822960367e-05 | 4.447305825e-05 | 4.911379709e-05 | 2.871251970e-05 |
| commute_mid | 5.791669125e-05 | 3.747998402e-05 | 4.479163913e-05 | 5.010376774e-05 | 2.871251970e-05 |
| commute_tail | 5.548563367e-05 | 3.745555163e-05 | 4.253477649e-05 | 4.792771588e-05 | 2.871251970e-05 |
| critical_comp29 | 5.812307061e-05 | 3.712226774e-05 | 4.506284632e-05 | 5.027352221e-05 | 2.871172978e-05 |
| phase_all | 5.990834710e-05 | 3.831061096e-05 | 4.668832498e-05 | 5.166995632e-05 | 2.871251970e-05 |
| phase_tail | 5.809979028e-05 | 3.743668019e-05 | 4.518836608e-05 | 4.988467416e-05 | 2.871251970e-05 |
| release_drop129 | 5.882468260e-05 | 3.792832144e-05 | 4.544784457e-05 | 5.068941289e-05 | 2.871251970e-05 |
| release_drop9 | 5.885271501e-05 | 3.774517885e-05 | 4.553003655e-05 | 5.070685055e-05 | 2.871251970e-05 |
| release_instrument | 5.860277080e-05 | 3.749959096e-05 | 4.554772073e-05 | 5.041525757e-05 | 2.871251970e-05 |
| release_instrument_drop129 | 5.872801116e-05 | 3.793911759e-05 | 4.536349212e-05 | 5.060609908e-05 | 2.871251970e-05 |
| sensitivity_tail | 5.508833822e-05 | 3.745555163e-05 | 4.222959711e-05 | 4.759463138e-05 | 2.871251970e-05 |

Largest physical second-order pair classes in the selected circuit:

| Pair class | Contribution |
|---|---:|
| round x round | 2.8840000000e-05 |
| encoder_a x pre_round_idle | 6.3334013066e-06 |
| encoder_bc x encoder_bc | 2.3355555556e-06 |
| encoder_a x encoder_bc | 1.5911111111e-06 |
| encoder_a x round | 1.5022222222e-06 |
| encoder_bc x round | 9.6222222222e-07 |
| pre_round_idle x pre_round_idle | 7.7415771222e-07 |
| encoder_a x encoder_a | 6.7555555556e-07 |

## Verified versus inferred

Verified: original dependency/slack certificate; legal nearest-neighbour R45 schedules; upstream noiseless correctness and abs(c1)<1e-12 for all emitted variants; actual 1e6 judge and XTIM speed receipts; unchanged exact2 and sparse all-orders results when marked complete; all improved all-orders candidates receive MC3. Source SHA, full numerical receipts and failures remain in [v30/results.json](v30/results.json). Nonfinal complete-circuit artifacts are archived in v30/nonfinal_plans.json.gz and removed as loose files; the bare R45 and sensitivity finalists remain. Initialization metadata is derived from the final native operations. One COMP29 preparation-reset attribution was corrected and its ablation rerun; gate/noise physics and scores did not change. No job is left running at final delivery.

Inference and scope: a shallower B/C resource, including helper-assisted preparation or pipelined B→h→C verification, cannot remove this particular A/data release chain by itself. The eight spare cells are not direct neighbours of the binding A15/9 inputs. Dirty-bus UVUV is a valid identity but needs a new binding interaction/placement to help here; no new helper resource is claimed as built or ruled out. Going belowR45 needs a different measured boundary/data route/A synthesis or prefix program, beyond the proven fixed-operation commutation model. Those broader families remain open.
