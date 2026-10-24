# v30f round-start certificate

Times are zero-based native steps. ES/LS and slack refer to the original per-wire dependency graph, with the final round fixed at R48. This graph includes every shared-cell exclusion. Slack=LS−ES; it is not the delay chosen by the old ALAP schedule.

Original fixed order requires R48. Legal commuting-tail reordering constructs R45; all-CX commutation and diagonal-phase/CX-control commutation CP models also prove minimum R45 under their fixed operations, measurements, resets and final-round offsets. These are conditional scheduling bounds, not architecture lower bounds.

## Binding original chain

After the unchanged cultivation path reaches MX1 at27: R1/RX2 at28; CX2→1 at29; CX3→2 at30; CX8→2 at31; CX2→3 at32; CX2→8 at33; CX8→9 at34; CX9→8 at35; CX9→15 at36; CX15→9 at37; CX15→21 at38; CX21→15 at39; MZ15 at40; RX15 at41; CX15→14 at42; CX14→8 at43; CX2→8 at44; CX1→2 / CX8→14 at45; CX2→8 at46; final CX1→2 / CX8→14 at47; D→A at48. Every listed critical operation has zero slack. There are parallel critical branches; `critical.json` contains every node/edge/slack and representative longest paths.

## Ancilla input releases

The release row is the last operation before that A input is initialized. Ready times include one native step after the operation.

| A cell | Prefix/data-source release: old / ES | Initial native operation: old / ES / LS | Init slack |
|---|---|---|---:|
| 1 | 42 / 36 | 43 / 36 / 43 (reset q[1];/h q[1];) | 7 |
| 2 | 42 / 36 | 42 / 36 / 42 (reset q[2];/h q[2];) | 6 |
| 8 | 36 / 36 | 41 / 36 / 41 (measure q[8] -> c[54];) | 5 |
| 9 | 39 / 39 | 40 / 39 / 40 (reset q[9];/h q[9];) | 1 |
| 14 | 41 / 28 | 41 / 28 / 41 (reset q[14];) | 13 |
| 15 | 41 / 41 | 41 / 41 / 41 (reset q[15];/h q[15];) | 0 |
| 16 | 44 / 32 | 44 / 32 / 44 (measure q[16] -> c[55];) | 12 |

## B/C resource cell release

| Cell | Last prefix use | Release old / ES | Initialization old / ES / LS | Init slack |
|---|---|---|---|---:|
| 4 | h q[4];/measure q[4] -> c[8];/h q[4]; | 34 / 28 | 40 / 28 / 40 | 12 |
| 5 | virgin | 0 / 0 | 39 / 0 / 39 | 39 |
| 6 | h q[6];/measure q[6] -> c[13]; | 34 / 28 | 45 / 28 / 45 | 17 |
| 11 | virgin | 0 / 0 | 37 / 0 / 37 | 37 |
| 12 | virgin | 0 / 0 | 41 / 0 / 41 | 41 |
| 13 | h q[13];/measure q[13] -> c[6]; | 15 / 15 | 37 / 15 / 37 | 22 |
| 17 | virgin | 0 / 0 | 36 / 0 / 36 | 36 |
| 19 | measure q[19] -> c[3]; | 11 / 9 | 37 / 9 / 37 | 28 |
| 23 | virgin | 0 / 0 | 36 / 0 / 36 | 36 |
| 25 | virgin | 0 / 0 | 37 / 0 / 37 | 37 |
| 26 | virgin | 0 / 0 | 36 / 0 / 36 | 36 |
| 27 | virgin | 0 / 0 | 36 / 0 / 36 | 36 |
| 28 | virgin | 0 / 0 | 36 / 0 / 36 | 36 |
| 29 | virgin | 0 / 0 | 36 / 0 / 36 | 36 |

## Chain completion and slack

These are component ready times after all of their original-order operations; actual completion and earliest completion are distinct. Component slack here is R48 minus earliest ready time. It does not allow arbitrary independent shifts of the components.

| Chain | Old ready | Earliest ready | Ready slack |
|---|---:|---:|---:|
| encoder_bc | 48 | 36 | 12 |
| encoder_a | 48 | 48 | 0 |
| data_hops | 44 | 41 | 7 |
| prefix | 48 | 36 | 12 |
| Terminal T† gates | 48 | 28 | 20 |

The `encoder_a` region includes source-zero measurements reused as A input preparation. `data_hops` contains the remaining tail transfers/source checks; `prefix` includes cultivation and blue checks. These explicit operation tags define the noise split as well.

B/C finishes at47 only because its 11 resource layers are placed just before the48 check. All fourteen cells can follow their original gate order and be resource-ready by36, so the binding suffix leaves12 steps of resource scheduling slack. The eight spare cells therefore cannot shorten R48 merely by accelerating B/C. The pipelined measured-bus check also retains the D→A and B→D times; it supplies geometry freedom but does not remove this A/data release dependency. The UVUV dirty-bus identity similarly has no gain without replacing a binding A/data interaction. Neither statement is a blanket rejection of helper-assisted synthesis.

Readout: D→A and B→C start atR; B→D and C readout-processing CXs are atR+1; the remaining readouts finish atR+2. In this task these offsets are preserved. They set final depthR+3 and post-round idle exposure, but impose no later start than the A/input chain.

## Constructive R45 schedule

The blue-tail inverse CX2→8 moves before CX2→3; forward data propagation 9→15→21 overlaps the coherent source uncomputation. A's commuting target-8 gates are reordered so CX2→8 runs before CX9→8 and CX14→8. The resulting chain reaches MZ15 at38, RX15 at39, A gates40–44, and D→A at45. This uses the same189 CX, final cells, measurement detector predicate, and T count; physical noise changes are fully repriced.

The five-layer EXENC A replacement does not reachR44 with its actual input-release constraints and worsens dangerous A noise. Dropping A checks and the existing q15 instrument also do not reduce the modeled minimum below45. These negatives close only their exact recipes.
