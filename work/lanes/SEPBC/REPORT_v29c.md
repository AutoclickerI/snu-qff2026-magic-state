Status: COMPLETE — Task A verified; Task B emitter and witness-family diagnosis delivered.

Current delivery replaces the working journal. The earlier accepted v28s delivery is preserved in [REPORT_v28s.md](REPORT_v28s.md). No submissions, commits, pushes, credentials access, or other-lane writes.

## Task A: v29c known-state detector

Best qualified grid circuit: [sepbc_v29c_q5_both.qasm](sepbc_v29c_q5_both.qasm) / [metadata](sepbc_v29c_q5_both.json). It adds Z measurements on q5 at native steps37 and38 and their singleton detectors, inside existing idle slots. 213 CX, R48, depth51. The independent A/BC CSS-state scan, including symbolic record frames, found only q5/Z at37 and38; this does not claim an exhaustive search of arbitrary prefix observables.

Exact parts: second **4.912222799070e-05**, third **1.315771810374e-05**, total **6.227994609443e-05**; c1=2.405e-19; exp(-A1)=0.5065620103. Unchanged exact2 CLI agrees. Against v29c's 6.26263311786e-5, the cubic improvement is 0.5531%. Against LADDER sepBC/ABC210, shortfall is 5.168673894e-06/1.195369809e-05.

1e6 judge PASS: seed-0 acceptance **0.50627**, **3.1 s** on zebra. XTIM prediction **FAST**, 5.4724 s/1e6 in its concurrent timing run. MC at 1e8 shots, seeds0/1000/2000: **6.306625e-5 / 6.279701e-5 / 6.229151e-5**; mean **6.271826e-5**; seed-0 acceptance **0.50645**. The three-seed estimate is noisy; it is not used to overrule applicable all-orders ranking.

| Variant | Second | Third | Total | exp(-A1) | MC3 mean | All orders |
|---|---:|---:|---:|---:|---:|---:|
| `sepbc_v29c_q5_t37` | 4.9188894657e-05 | 1.3178580956e-05 | 6.2367475613e-05 | 0.507068826 | 6.271770e-05 | 6.317487394432e-05 |
| `sepbc_v29c_q5_t38` | 4.9122227991e-05 | 1.3157718104e-05 | 6.2279946094e-05 | 0.507068826 | 6.251170e-05 | 6.308631335471e-05 |
| `sepbc_v29c_q5_both` | 4.9122227991e-05 | 1.3157718104e-05 | 6.2279946094e-05 | 0.506562010 | 6.271826e-05 | 6.308623160921e-05 |

All-orders parent v29c: **6.343913669755e-05**; q5/t37+t38: **6.308623160921e-05**, acceptance **0.506411738152**, improvement **0.5563%**. The five-projector extension validates the complete categorical channel multiset against EVAL, direct projector sectors, and a three-channel categorical enumeration for each circuit; scope rank5, 15 rotations, width26. See adjacent `.allorders_general.validation.json` and `.allorders.log` receipts.

Layout remains data `[0,20,7,10,3,22,21]`, A `[1,14,8,9,2,16,15]`, B `[6,26,13,11,4,23,27]`, C `[12,25,19,17,5,29,28]`. The inherited v29c coherent transfers and terminal instrument are unchanged; there is no additional move. The complete native operation plan is retained. t37+t38 has no resolved cubic benefit over t38 alone and consumes more acceptance. The completed all-orders comparison changes the selection: both measurements improve on t38 alone by8.17455e-11 (6.30862316092e-5 versus6.30863133547e-5). That tiny higher-order gain is well below MC resolution, but all-orders loss is the stated ranking rule. t38 alone remains a qualified near-tie, with MC3 mean6.251170e-5, acceptance0.507344 and3.3s at1e6.

The unchanged top-pair report identifies the remaining A/data exposure: q7 X-idle at20–23 with q20 Y-idle at40–46 contributes7.731e-7; q4 X-idle at18–39 with each late A CX fault contributes2.411e-7; q0 Z/Y-idle at39–47 with late A encoder faults contributes1.989e-7 per listed pair. q5 catches BC preparation faults but leaves these A/data and round contributions. These are physical-pair examples, not an additive attribution of the LADDER reference gap.

## Task B: complete ENDSTATE attachment

Reusable CLI: [endstate_emit.py](endstate_emit.py), with [input contract and examples](EMITTER.md). It consumes native operations/detectors, uses the independently extracted real v23/v29 cultivation prefix, searches geometry and common code automorphisms, routes data by coherent two-CX transfers with source-zero checks, and schedules physical lifetimes. Prefix reset intervals are jointly movable; borrowing before implicit |0> input inserts a real noisy restoring reset. Each emitted circuit retains operation provenance for ablations. The v29 core omits its later blue-check package; an earlier pilot preserving that package is listed separately.

Best attachment through third order: [es_joint_a12_v29_2.qasm](es_joint_a12_v29_2.qasm) / [metadata](es_joint_a12_v29_2.json); second **8.206600708642e-05**, third **1.273896326420e-04**, total **2.094556397285e-04**; c1=-2.591e-20, exp(-A1)=0.4242861755. It has 174 CX, R=55. 1e6 diagnostic: acceptance **0.42449**, **4.9 s**; fails acceptance. No Task B circuit reaches the 6.2e-5 trigger for 1e8 MC. This negative does not close the broader end-state family.

Original witness has A10/B11/C11 and 20 block teleports. C-final equals B-initial in code order, so after B vacates its cells C can use the same 11-CX encoder directly: six C teleports disappear. EXENC on the same A cells reduces danger from 73 p/15 units at10 CX to 16 at 11 CX and 10 at 12 CX. The A12 derivative intentionally exceeds the original witness's <=11 property; no contest limit is exceeded. Canonical path/ASAP enumeration counts are 184 at 10 CX, 6794 at 11, 125472 at 12; this is not an exhaustive claim over arbitrary schedules.

Final attachment layout and coherent data paths are in the best stem's JSON. It uses the transpose of the fragment, prefix shifted two rows, common code permutation `[1,2,0,4,6,5,3]`, 12 data hops and 14 A/B teleports; C is stationary. Data paths: `12→13→7→1`, `32`, `19→18→12`, `22→16→10`, `15→9→3→4→5`, `28`, `20→14`.

### Built circuits

Every unique full circuit below is priced by unchanged exact2 --third --top30. Byte-identical QASM and identical data metadata share a verified receipt; aliases are listed in [current_results.json](current_results.json). All c1 satisfy abs(c1)<1e-12. Delta columns compare with LADDER sepBC=5.71112722e-5 / ABC210=5.03262480e-5. These deltas include interactions and are not additive taxes.

| Stem | R | CX | Second | Third | Total | exp(-A1) | Delta sepBC / ABC210 | Mechanism |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `endstate_w12_v23_c0` | 75 | 166 | 3.37478977e-04 | 6.49829717e-04 | 9.87308694e-04 | 0.287901 | 9.3019742e-04 / 9.3698245e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `endstate_w12_v29_c0` | 77 | 182 | 3.44745502e-04 | 6.37010253e-04 | 9.81755755e-04 | 0.266958 | 9.2464448e-04 / 9.3142951e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_ca11_v29_0` | 55 | 167 | 7.99488663e-05 | 1.33252448e-04 | 2.13201314e-04 | 0.429718 | 1.5609004e-04 / 1.6287507e-04 | Stationary C, lower-danger A11; serialized A/B exposure dominates |
| `es_ca11_v29_1` | 55 | 171 | 7.71314913e-05 | 1.40806869e-04 | 2.17938360e-04 | 0.435384 | 1.6082709e-04 / 1.6761211e-04 | Stationary C, lower-danger A11; serialized A/B exposure dominates |
| `es_ca11_v29_2` | 55 | 173 | 8.09226540e-05 | 1.39030303e-04 | 2.19952957e-04 | 0.436670 | 1.6284169e-04 / 1.6962671e-04 | Stationary C, lower-danger A11; serialized A/B exposure dominates |
| `es_ca12_target_0` | 60 | 196 | 7.35820466e-05 | 1.42127119e-04 | 2.15709165e-04 | 0.400685 | 1.5859789e-04 / 1.6538292e-04 | Best relaxed-R geometry costs 24 actual data hops; exposure remains |
| `es_ca12_v29_0` | 55 | 168 | 7.70485848e-05 | 1.35460964e-04 | 2.12509549e-04 | 0.430875 | 1.5539828e-04 / 1.6218330e-04 | Stationary C, lower-danger A12; serialized A/B exposure dominates |
| `es_ca12_v29_0_noguard` | 55 | 168 | 7.80152327e-05 | 1.47147606e-04 | 2.25162839e-04 | 0.435390 | 1.6805157e-04 / 1.7483659e-04 | Removing coherent-hop source checks leaves extra undetected faults; R unchanged |
| `es_ca12_v29_1` | 55 | 172 | 7.51193235e-05 | 1.37479335e-04 | 2.12598658e-04 | 0.432783 | 1.5548739e-04 / 1.6227241e-04 | Stationary C, lower-danger A12; serialized A/B exposure dominates |
| `es_cdirect_v29_0` | 54 | 166 | 1.91680012e-04 | 1.27869159e-04 | 3.19549171e-04 | 0.438306 | 2.6243790e-04 / 2.6922292e-04 | Six C teleports removed; original A10 encoder pairs with idle noise |
| `es_cdirect_v29_1` | 54 | 170 | 1.93241725e-04 | 1.27493489e-04 | 3.20735214e-04 | 0.438430 | 2.6362394e-04 / 2.7040897e-04 | Six C teleports removed; original A10 encoder pairs with idle noise |
| `es_cdirect_v29_2` | 54 | 176 | 1.92770226e-04 | 1.26015415e-04 | 3.18785642e-04 | 0.437138 | 2.6167437e-04 / 2.6845939e-04 | Six C teleports removed; original A10 encoder pairs with idle noise |
| `es_cdirect_v29_3` | 55 | 168 | 2.06467201e-04 | 1.37790382e-04 | 3.44257583e-04 | 0.438398 | 2.8714631e-04 / 2.9393134e-04 | Six C teleports removed; original A10 encoder pairs with idle noise |
| `es_joint_a12_v29_2` | 55 | 174 | 8.20660071e-05 | 1.27389633e-04 | 2.09455640e-04 | 0.424286 | 1.5234437e-04 / 1.5912939e-04 | Joint prefix/reset lifetimes; A/B storage still dominates |
| `es_w12_core_v23_0` | 71 | 166 | 3.38890353e-04 | 5.64258772e-04 | 9.03149125e-04 | 0.293557 | 8.4603785e-04 / 8.5282288e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_core_v23_1` | 71 | 172 | 3.23400410e-04 | 5.65088282e-04 | 8.88488692e-04 | 0.294513 | 8.3137742e-04 / 8.3816244e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_core_v23_2` | 71 | 172 | 3.28793032e-04 | 5.79660744e-04 | 9.08453776e-04 | 0.296358 | 8.5134250e-04 / 8.5812753e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_core_v23_3` | 71 | 172 | 3.33821514e-04 | 5.66040474e-04 | 8.99861988e-04 | 0.294103 | 8.4275072e-04 / 8.4953574e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_core_v29_0` | 69 | 172 | 3.24496065e-04 | 5.53394852e-04 | 8.77890917e-04 | 0.291616 | 8.2077964e-04 / 8.2756467e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_core_v29_1` | 69 | 176 | 3.23320456e-04 | 5.60558096e-04 | 8.83878552e-04 | 0.292796 | 8.2676728e-04 / 8.3355230e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_core_v29_2` | 69 | 178 | 3.30656549e-04 | 5.62718410e-04 | 8.93374959e-04 | 0.294214 | 8.3626369e-04 / 8.4304871e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_core_v29_3` | 69 | 178 | 3.30747665e-04 | 5.71595868e-04 | 9.02343533e-04 | 0.294722 | 8.4523226e-04 / 8.5201729e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_v23_0` | 72 | 174 | 3.29506060e-04 | 5.84637560e-04 | 9.14143620e-04 | 0.291975 | 8.5703235e-04 / 8.6381737e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_v23_1` | 73 | 172 | 3.33565178e-04 | 6.05368275e-04 | 9.38933453e-04 | 0.290607 | 8.8182218e-04 / 8.8860721e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_v23_2` | 73 | 174 | 3.24639621e-04 | 6.01768988e-04 | 9.26408609e-04 | 0.289881 | 8.6929734e-04 / 8.7608236e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |
| `es_w12_v23_3` | 73 | 178 | 3.35356830e-04 | 5.95549231e-04 | 9.30906061e-04 | 0.289031 | 8.7379479e-04 / 8.8057981e-04 | Original A/B/C one-hop fragment serializes preparation; large idle pairs and cubic loss |

### Noise ablation of the best attachment

Counterfactual removals preserve all other physical channels and the complete categorical cubic calculation. They are diagnostic, not attainable circuits or lower bounds.

| Channels retained/removed | Second | Third | Total |
|---|---:|---:|---:|
| all | 8.2066007086e-05 | 1.2738963264e-04 | 2.0945563973e-04 |
| no_pre_round_idle | 3.7132777778e-05 | 3.0091922407e-06 | 4.0141970019e-05 |
| no_teleport_noise | 7.8597340247e-05 | 1.0375343797e-04 | 1.8235077822e-04 |
| no_encoder_noise | 5.5226439583e-05 | 1.0364622664e-04 | 1.5887266622e-04 |
| no_data_hop_noise | 8.1763784864e-05 | 1.1905442535e-04 | 2.0081821022e-04 |
| no_prefix_noise | 7.7423326137e-05 | 1.1162135989e-04 | 1.8904468602e-04 |
| only_round_noise | 2.8840000000e-05 | -1.2706192593e-07 | 2.8712938074e-05 |
| no_idle_or_teleport | 3.5206666667e-05 | 1.1845402963e-06 | 3.6391206963e-05 |
| no_idle_or_encoder | 2.9404444444e-05 | 1.2607438148e-06 | 3.0665188259e-05 |

Dominant physical second-order pair classes:

| Pair class | Contribution |
|---|---:|
| round x round | 2.8840000000e-05 |
| pre_round_idle x pre_round_idle | 1.9582536067e-05 |
| encoder_a x pre_round_idle | 1.6203114427e-05 |
| pre_round_idle x prefix | 3.3099031718e-06 |
| encoder_b x encoder_c | 2.4755555556e-06 |
| block_teleport x encoder_a | 1.7600000000e-06 |
| encoder_c x pre_round_idle | 1.5873932049e-06 |
| block_teleport x pre_round_idle | 1.5425557279e-06 |

The round alone is 2.87129e-5. Removing pre-round idle noise gives 4.01420e-5; removing teleport noise alone leaves 1.82351e-4. Thus the main shortfall is exposure during serialized A/B preparation and its cubic interactions. The idle-scaling diagnostic reaches 5e-5 at 0.16366 of current pre-round idle probability. This does not prove an achievable schedule or imply that exactly 83.6% of physical waiting steps must disappear. All variants have their own ablation rows and top-pair examples in the ledger.

## Verified versus inferred

Verified: unchanged exact2 receipts and full categorical screens; native adjacency/timing and upstream ideal correctness for emitted circuits; complete Task A 1e6 gates/FAST/MC3; diagnostic acceptance failure for the best attachments; identical-file receipt aliases; the current ENDSTATE catalog contains only witness12_h1 as a full native fragment. Numerical evidence remains in `current_results.json` and adjacent retained receipts. Nonfinal complete-circuit QASM/metadata/plans have been removed; the three qualified Task A variants and the best Task B diagnostic remain, alongside the previous accepted delivery and source fragments.

Scope: the final joint search covers 48 relative geometries, two low-Manhattan common automorphisms and two routes per geometry (192 fixed-route scheduling models, all OPTIMAL for R, minimum55). R is a proposal objective; full loss ranks emitted candidates. It does not prove optimal fidelity or routes. The earlier free-data scheduling bounds R>=63 (original) and R>=51 (directC+A12) apply only to the pilot final-prefix-release model, not the expanded joint-lifetime model. A separate 336-model search over all 168 automorphisms/two routes on the minimum-bound geometry reached R60 and worsened the real score.

Inferred: new end-states need substantially shorter harmful A/B storage, through interleaving or helper-assisted preparation. Native extra block moves, tagged helper reuse and explicit round offsets are supported by the emitter, but no new <=2-move/helper ENDSTATE fragment was present to validate those families. Fragment-internal data relocation requires a separate lifetime adapter and is rejected explicitly. No global impossibility or sub5e-5 feasibility claim is made.
