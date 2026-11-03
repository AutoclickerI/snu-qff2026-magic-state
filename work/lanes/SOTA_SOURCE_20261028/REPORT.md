# Native source, resource geometry and architecture audit

**No new native SOTA candidate was produced in this lane.** Its results include complete compact-source experiments, actual native source and route boundaries, ideal-resource headroom controls, and an all-to-all Gao reconstruction with coherent output-frame correction. The best completed compact-family candidate has exact expected loss 6.81755565e-5; the best Gao circuit has exact expected loss 4.52150400e-5 with adjacency relaxed. Neither is competitive with the combined native circuit's exact expectation **3.566732196898089e-5**.

The latest reported leading board draw is **2.86759593420732e-5**, observed 2026-10-27 16:23:30 UTC. It is a sampled board score; the native figure above is an all-orders expectation, so their numerical difference is not a comparison of two true means. No submission or external publication was performed.

## Moving-Bell source and physical preverification

This is a completed negative experiment, not a competitive candidate. All listed circuits include the actual native encoder, moving Bell logical-check source, terminal A/B instruments, and every reset, measurement and idle channel. Ordered data wires are [6,20,19,10,2,22,16]. Results are all-orders at p=0.001, with raw Steane-space validity checked before decoding.

| Input precheck | CX | ticks | raw correct | harmful singles c1 | loss | acceptance |
|---|---:|---:|---|---:|---:|---:|
| none | 170 | 35 | yes | 0.0833333333 | 0.0008776662671 | 0.5819690047 |
| A-only physical precheck | 189 | 44 | yes | 0 | 0.001341852710 | 0.5047664361 |
| physical A/B precheck | 291 | 59 | yes | 0 | 0.0006508226905 | 0.4356740452 |

The first circuit is `boundary/full_low_cx_efa38e1209a705ce_d6_20_19_10_2_22_16`; the A-only circuit is `boundary/full_aonly_low_cx_d4564042bd67faa8_d6_20_19_10_2_22_16`; and the A/B circuit is `boundary/full_low_cx_0e5aaeb61a7b8c78_d6_20_19_10_2_22_16`. Each stem has QASM, output JSON and integration JSON with the complete exact and single-fault receipts. The A/B circuit is below the 0.5002 acceptance margin. No listed circuit is close to the current combined native expectation 3.566732196898089e-5.

The source is the previously verified 25-CX A-footprint two-Bell moving check, `CATGEOM3_20261027/native_bell_a.py`; its encoder is `CATNATIVE3_20261027/encoder/depth5_seed1.json`; the terminal A/B modules are from NATIVE2. The no-precheck assembly reveals harmful encoder fault components that were outside the original source-only Bell audit. Both prechecks remove those harmful singles, but even the A-only version with acceptable acceptance has much higher exact loss. No inference is made that all native Bell sources fail; the tested encoder, check, factory and scheduling combination fails.

Reusing the old B factory immediately after a prior A/B instrument without fresh resets produced a raw-invalid circuit: the factory implicitly depends on initial states of cells that the earlier instrument has measured. Explicitly resetting non-A/non-data cells repaired raw correctness. Those resets are included in the A/B row above. This is an input-contract observation, not a claim that all those resets are necessary or optimal.

Reproduction, from repository root with thread caps:

```
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/SOTA_SOURCE_20261028/build_prev.py low_cx
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/SOTA_SOURCE_20261028/a_precheck.py
POSTCHECK=1 AONLY=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/SOTA_SOURCE_20261028/build.py low_cx
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/SOTA_SOURCE_20261028/build.py low_cx
POSTCHECK=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/SOTA_SOURCE_20261028/build.py low_cx
```

The first command uses the earlier scheduler, retained to reproduce the no-precheck result. Scripts use existing shared helpers without modifying them. No submission or shared tool change was made.

## Targeted flags, source timing, and fault-pair analysis

The table above is superseded as a judgment about the no-precheck schedule: `aonly_pairs.json` shows c2=1266.8022, with an outsized contribution from waiting errors on the early B factory. Moving that factory 24 clocks later, without changing its operations or the A instrument, yields raw-correct `boundary/lateb24_f6dd3ccd0077a848_d6_20_19_10_2_22_16`, c1=0, L=0.0002401154506 and A=0.5633005304. Its pair audit `late24_pairs.json` has c2=200.9356. The highest remaining pairs involve the terminal B-to-data layer and data waiting during the source, so this timing repair alone is far from enough.

The six harmful encoder components in the original no-precheck circuit all involve an X component on q14 at specific encoder locations. Two physical targeted encoder checks were built and fully integrated:

- Depth-5 encoder: an even-parity two-cell Bell meter measures Z14 Z13 Z9 Z8 after encoder clock 6. The native preparation, seven CXs, two M reads, and reuse resets are in `flag_source.py`; the raw-valid complete low-CX moving-Bell circuit `boundary/full_flagbell_low_cx_a78dbe9d0bde0088_d6_20_19_10_2_22_16` has c1=0, L=0.0003456817444, A=0.5869694551, 177 CX and 41 clocks.
- Depth-6 encoder: a five-CX meter measures Z14 Z9 Z8, whose relation is valid after its sixth encoder clock. `flag_depth6.py` emits that source. Complete circuit `boundary/full_asap_shorter_68ab2f3b8a0a5046_d6_20_19_10_2_22_16` is raw-valid with c1=0, L=0.0003788757772, A=0.5958808745, 177 CX and 41 clocks.

A native cat meter was also placed between the interleaved logical checks at a cut where the specified Z stabilizer commutes with both partially completed rounds. `zmeter.py` constructs all 6x6-local cat preparation, bridge reads, four data couplings and even-parity detector. The optimized-root mask-102 circuit `boundary/full_zmeter102_low_cx_f0b6a2bb5f74a99e_d6_20_19_10_2_22_16` is raw-valid, 187 CX and 44 clocks, with L=0.0004591311118 and A=0.5237109122. Mask 120 plus explicit factory-cell cleanup is raw-valid but has L=0.0005393745284 and A=0.4555296071 (`boundary/full_zmeter120_low_cx_52502b3485063d60_d6_20_19_10_2_22_16`). The extra meter's physical preparation and delayed reuse of B cells exceed its benefit in these schedules. These results do not rule out a different geometry or a jointly redesigned terminal resource.

The shorter native Bell path with an ASAP reordering that preserves each wire's operation order gave `boundary/full_asap_shorter_cf398ff440cdd6d3_d6_20_19_10_2_22_16`, c1=0, L=0.0003204515712, A=0.5957182477, 179 CX/39 clocks. All figures are exact full-noise prices. No candidate approaches the incumbent, and no promotion is recommended.

## Higher-quality source and joint geometry

The original source from `NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16` is 251 CX and 41 ticks; its previously constructed contracted variant uses 243 CX. Both retain the actual source measurements and detector relations. These are source boundaries; neither has a terminal resource or a complete score.

An exact labeled tile-geometry CP-SAT model, with four square interactions, connected seven-cell A, and B/C permitted to use free bridge cells, found a horizontal reflection whose source-to-target Manhattan distance is **2**, with an optimal bound of 2 for this model. The actual reflected source and two coherent nearest-neighbor moves use **four CX** and retain raw output correctness. Retiming one deterministic source M from clock40 to39 lets both moves occur at clocks40–41. The preferred earlier original-source boundary is `tile_boundary/reflected_source_early_original_reuse_92ac872b958465a1_d10_21_28_7_3_19_13`: 255 CX, 42 ticks, ordered outputs `[10,21,28,7,3,19,13]`. Its exact A/B/C roles, per-cell releases, detector contract and route operations are in `tile_boundary/reflected_source_early_original_reuse.release.json`. Original/contracted and reset/reuse alternatives are preserved. The preference for earlier release is architectural; actual full-noise selection remains outstanding.

That four-square geometry has four induced B/C connected components. Exhaustive subsets of the eight free cells give the unique minimum bridge set `[0,6,24,34,35]`. A separate fixed-data CP-SAT model verifies five helpers as the minimum within the specified connected-A/native-tile model. A geometry with connected A and directly connected B/C at source movement cost at most two is infeasible within that same tile model. These are graph results, not prepared-resource circuits.

Six- and seven-square tile models are infeasible when A must be connected solely through its seven output cells and B/C may use free bridges. Allowing each block to use free-cell bridges produces actual raw-correct source+route boundaries: seven squares with 10 route CX and 44 ticks, and six squares with 12 route CX and 44 ticks. The seven-square distance-five geometry needs all eight free cells to connect B/C and shares two minimum A bridge cells with B/C; the six-square distance-six geometry requires five A and four B/C bridges sharing one cell. Independent graph connectivity does not establish a simultaneous resource preparation. The source+route files and release metadata are in `tile_boundary/seven_source_*` and `tile_boundary/six_source_*`.

The exact counterfactual comparison of these source geometries with instantaneous perfect resources is in `HEADROOM.md`. In particular, the actual noisy unmoved source with the mask63 six-square ending gives ideal-resource loss 2.74984615e-5 at terminal tick41, 2.84558503e-5 at tick44 and 2.92991017e-5 at tick46. The reflected seven-square source plus its actual route yields 3.08421857e-5 at tick44. These are full-source-and-terminal noise diagnostics with resource preparation artificially perfect, not legal submissions or monotone global bounds.

## Gauging and Gao–Yuan–Yao architectures

Primary sources are the 29 September 2026 version of Hetényi, Brown and Williamson, [Constant-depth magic state cultivation with Clifford measurements by gauging](https://arxiv.org/html/2603.05429v2), and Gao, Yuan and Yao, [Extremely Low-Cost Magic State Preparation toward Fault-Tolerant Quantum Computing](https://arxiv.org/html/2609.12698v1), 11 September 2026. The former's authors point to [IBM's Apache-2.0 repository](https://github.com/IBM/gauging_clifford_measurement); no third-party source was copied into this lane. The Gao paper says numerical data are available from its authors on reasonable request; no circuit repository was identified in the checked paper or search. Its quoted 2.2e-7 bound and 86.9% acceptance are for a destructive error-detection diagnostic, not for the live unmeasured output checked here.

For the literal d=3 gauging measurement, the paper describes record-dependent local Clifford byproducts. `gauge_frames.py` enumerates the exact 128-dimensional Steane magic state and the 64 complementary gauge-frame classes. Assuming the standard uniform ideal gauge records, only one class yields the target raw state with no correction: ideal conditional acceptance 1/64. Maximizing over all four logical Pauli frames leaves exactly one raw-correct class. Even perfect code-space projection has acceptance 11/256 conditioned on the positive logical outcome: eight classes have nonzero projection, each already gives the target, and the best logical Pauli frame does not increase the total. These values are a concrete blocker to the literal frame-free realization, not a general impossibility for a redesigned coherent recovery circuit.

The Gao source was independently reconstructed from its explicit grouped-check equations and table. A generic exact rank-five qRM CSS plus-state encoder uses 32 CX here; the published source encoder uses 25. The 15-T source has the paper's two triple and two pair flag gadgets and the seven-CX logical-X verifier. Its three bulk-X-record-dependent output Z frames are physically compiled *before* the bulk X reads into 16 data-to-bulk CX gates after XOR cancellation. This uses ordinary gates and no record-conditioned operation. The live Steane output is raw-correct. The terminal is an actual noisy full-square three-resource ending. All source, preparation, terminal, readout and idle channels are noisy; only adjacency is relaxed.

| Abstract complete Gao construction | CX | Clocks | Exact loss | Acceptance | Harmful singles |
|---|---:|---:|---:|---:|---:|
| Serial reused flag rails | 160 | 84 | 9.78539681e-4 | 0.301103 | 0 |
| Parallel independent rails | 160 | 64 | 4.52069117e-4 | 0.377650 | 0 |
| Whole-circuit commutation DAG, unrestricted terminal times | 160 | 23 | 1.33269577e-4 | 0.635781 | 0 |
| Same DAG, aligned transversal terminal layers | 160 | 23 | 5.92035405e-5 | 0.619595 | 0 |
| Aligned terminal, late T and just-in-time resets | 160 | 23 | **4.52150399681e-5** | **0.724118** | **0** |

The 23-clock aligned schedule is optimal only within the stated pairwise-commutation dependency graph. The late-reset/late-T schedule is a feasible 23-clock solution of a weighted objective, not a proof of global noise optimality. Exact second-order coefficients are 51.47556 for the first aligned schedule and 42.42222 for the late schedule. The late result remains worse than the combined native expectation 3.566732196898089e-5 even before grid routing. It therefore supplies no SOTA candidate. A different qRM encoder, geometry, grouped-check order or terminal resource could behave differently.

All jobs in this lane have exited. No submission, production change, judge change, shared-tool change, or external message was made.

## Output relocation and affine-frame audit

A full-noise abstract one-bit output-teleportation control uses the native source, a real generic plus-resource encoder, seven final CX gates, source Z measurements and a legal affine `FRAME_X`. It is raw-correct, but its exact loss is **0.00103241383309** at acceptance **0.61345949035**, with seven harmful single-fault components in the unverified plus-resource encoder. Its source-to-output interactions are native for the selected footprint; its resource encoder is not, so the complete control remains diagnostic. `TELEPORT.md` records the construction, limitations, frame distinction and the physically motivated alternatives. This rejects the tested unverified implementation, not all verified teleportation or joint source/resource designs.
