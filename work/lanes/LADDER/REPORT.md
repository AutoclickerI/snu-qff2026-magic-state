Status: **COMPLETE** — matched forward ladder and reverse one-at-a-time prices measured; impossible fixed-R33 restorations identified. No submission, commit, or push.

**The measured 3.37363128e-05 gap is chiefly B+C preparation (+1.21097676e-05 recovered), A preparation (+6.78502417e-06), and advancing the round (+1.60413424e-05).** Prefix compaction is a prerequisite for the early round but costs 2.76969458e-06 at fixed R45. Removing hops also costs 3.51207394e-07 on this matched path. Neither is a positive recoverable grid tax.

All losses use STANDARD p=1e-3 and condition on every detector passing. “Exact” means the exact fault sum **through the stated order**, not an all-orders score. Third is the signed third-order correction, not the larger positive raw weight-3 sum. Delta means current minus previous row; negative improves. exp(-A1) is an acceptance proxy. Deltas and percentages below are arithmetic derived from measured receipts.

## Forward ladder

| Rung / output | Change | Exact 2nd | 3rd correction | Total through 3rd | Delta | exp(-A1) | CX |
|---|---|---:|---:|---:|---:|---:|---:|
| [f00_base](f00_base.exact.txt) | v23h_c2c9; R45 | 5.24923143e-05 | 1.67287255e-05 | **6.92210398e-05** | +0.00000000e+00 | 0.5408596 | 203 |
| [f01_sepBC](f01_sepBC.exact.txt) | Separate B/C, 9+9 CX; R45 | 4.38552900e-05 | 1.32559822e-05 | **5.71112722e-05** | -1.21097676e-05 | 0.5895794 | 139 |
| [a_order210](a_order210.exact.txt) | Best tested standard A, order210; R45 | 3.80983967e-05 | 1.22278513e-05 | **5.03262480e-05** | -6.78502417e-06 | 0.6014347 | 137 |
| [order210/f03_nohops](order210/f03_nohops.exact.txt) | Remove hops and guards; R45 | 3.80983967e-05 | 1.25790587e-05 | **5.06774554e-05** | +3.51207394e-07 | 0.6090760 | 125 |
| [order210/f04_prefix32_R45](order210/f04_prefix32_R45.exact.txt) | Only compact prefix to end32; R45 | 3.93831923e-05 | 1.40639577e-05 | **5.34471500e-05** | +2.76969458e-06 | 0.6193304 | 125 |
| [order210/f05_R42](order210/f05_R42.exact.txt) | Only advance suffix to R42 | 3.81015161e-05 | 1.03556662e-05 | **4.84571824e-05** | -4.98996759e-06 | 0.6322754 | 125 |
| [order210/f05_R39](order210/f05_R39.exact.txt) | Only advance suffix to R39 | 3.68146996e-05 | 7.35467156e-06 | **4.41693712e-05** | -4.28781122e-06 | 0.6455446 | 125 |
| [order210/f05_R36](order210/f05_R36.exact.txt) | Only advance suffix to R36 | 3.55227220e-05 | 4.98786453e-06 | **4.05105866e-05** | -3.65878459e-06 | 0.6591471 | 125 |
| [order210/f05_R33](order210/f05_R33.exact.txt) | Only advance suffix to R33 | 3.42255628e-05 | 3.18024482e-06 | **3.74058076e-05** | -3.10477900e-06 | 0.6730926 | 125 |
| [order210/f06_sep33_v23](order210/f06_sep33_v23.exact.txt) | Direct readout; v23 prefix, R33 | 3.41411183e-05 | 3.17065587e-06 | **3.73117742e-05** | -9.40333960e-08 | 0.6741704 | 123 |
| [order210/f07_sep33_old](order210/f07_sep33_old.exact.txt) | Older prefix; retain A210, R33 | 3.34193094e-05 | 2.09904929e-06 | **3.55183587e-05** | -1.79341548e-06 | 0.6728310 | 129 |
| [f07_sep33_old](f07_sep33_old.exact.txt) | Restore reference A012; published sep33 | 3.33884940e-05 | 2.09623306e-06 | **3.54847270e-05** | -3.36316735e-08 | 0.6728310 | 129 |

The A210 choice is the lowest measured total among all six orders of the standard encoder’s three commuting CX layers at the R45 A-replacement rung. It is held fixed through the timing ladder; no global optimum over all encoders or relabellings is claimed. The last row changes A210→A012 separately so the endpoint is exactly the published sep33, without mixing an encoder-order change into the prefix comparison.

### Why these are matched

- Native provenance gives **75 prefix + 82 B+C prep + 11 A prep + 12 hop + 23 round/readout CX = 203**. `build.py` matches all 129 prefix native units against v20 provenance by statement and occurrence. The boundary-based 78/83/13/6/23 counts in GAP mix these regions; the QASM and its score agree. See [build.log](build.log) and per-rung JSON unit records.
- B+C replacement changes only its preparation package: 82→18 CX, all blocks finished at44. The existing 7-CX B→C check remains at45. Initialization basis/policy and internal preparation timing belong to this replacement; the measured gain is **not** a price per deleted CX.
- A replacement changes only its encoder/initialization/check package, 11→9 CX, still ending at44. The old MX initialization checks cannot simply be kept verbatim when the encoder’s input bases change.
- Removing hops removes their 12 CX, destination preparations, and vacated-source guards. Reset-prepared A/B/C lifetimes are relabelled onto the 21 cells unused by the prefix. This avoids overwriting unmoved data; STANDARD noise is independent of cell numbers. Other gates and their native times are preserved.
- v23’s prefix contains late couplings/readouts and four terminal T† gates through44. `f04` moves only prefix units to their latest feasible times at or before32, preserving per-cell order. The R42/R39/R36/R33 rungs then shift **only** A/B/C preparation and the round, keeping this compact prefix fixed.
- The original readout includes parity CXs 19→25 and 17→16. `f06` removes only these readout gadgets, advances the affected A/C measurements by one step, and updates detector XORs. Omitting this control would conflate readout and prefix differences.
- Empty scheduled layers are kept by unconditioned Z measurements on an already discarded prefix wire. They keep native time from collapsing; that disconnected wire cannot affect acceptance or logical loss. No noise rates are changed.

## Reverse one-at-a-time controls

All deltas in the next table are versus the same A210 R33 circuit (`order210/f05_R33`), not versus the preceding reverse row. A/B+C restore the original grid-derived preparation circuits and their offsets from R on prefix-free ancilla cells. They restore the encoder packages, **not** the original physical layout or release constraints. The original A footprint includes live unmoved data cells8/15; B includes live cell4. Those footprints cannot be restored independently of movement.

| Rung / output | Change | Exact 2nd | 3rd correction | Total through 3rd | Delta | exp(-A1) | CX |
|---|---|---:|---:|---:|---:|---:|---:|
| [order210/r_BC](order210/r_BC.exact.txt) | Restore 82-CX joint B+C preparation | 4.48846317e-05 | 4.93780279e-06 | **4.98224345e-05** | +1.24166269e-05 | 0.6174716 | 189 |
| [r_A](r_A.exact.txt) | Restore 11-CX grid A preparation/checks | 3.81801870e-05 | 3.86473902e-06 | **4.20449260e-05** | +4.63911842e-06 | 0.6610518 | 127 |
| [order210/f04_prefix32_R45](order210/f04_prefix32_R45.exact.txt) | Restore R45 suffix timing; compact prefix fixed | 3.93831923e-05 | 1.40639577e-05 | **5.34471500e-05** | +1.60413424e-05 | 0.6193304 | 125 |

The early-context B+C cost is 1.24166269e-05, versus 1.21097676e-05 on the forward path. The early-context A cost is 4.63911842e-06, versus 6.78502417e-06 forward. These interactions make a unique order-independent additive attribution impossible.

**Fixed-R33 reverse hops: infeasible for the original routes and this unchanged prefix.** q8 has T† at30, followed by three two-CX transfers: six sequential CX slots require destination readiness at37 or later. [reverse_hops_feasibility.json](order210/reverse_hops_feasibility.json) records the ASAP dependency schedule. This is a bound for those paths, not a bound on redesigned routing or a modified prefix.

The matched feasible R37 control below restores the paths while placing fresh destination initialization immediately before first use. The first ASAP construction initialized fresh destinations at0 and charged gratuitous waiting; that version is retained as `order210/r_hops_hop` but is excluded from constraint attribution. Both versions pass correctness.

| Rung / output | Change | Exact 2nd | 3rd correction | Total through 3rd | Delta | exp(-A1) | CX |
|---|---|---:|---:|---:|---:|---:|---:|
| [order210/r_hops_nohop](order210/r_hops_nohop.exact.txt) | No-hop control at R37 | 3.59539560e-05 | 5.71092530e-06 | **4.16648813e-05** | +0.00000000e+00 | 0.6545753 | 125 |
| [order210/r_hops_hop_alap](order210/r_hops_hop_alap.exact.txt) | Restore hops; destination init immediately before use | 3.59539560e-05 | 5.49622645e-06 | **4.14501824e-05** | -2.14698846e-07 | 0.6469003 | 137 |

At R37 the restored hops improve total loss by 2.14698846e-07; second-order loss is unchanged to numerical precision, and the difference is third order. This agrees in sign with the R45 removal rung. The reduced acceptance proxy is measured; this is not a free noisy operation.

**Original prefix timing at R33: infeasible.** Its terminal T† at44 cannot precede R33. At matched R45, restoring the delayed prefix (`f04`→`f03`) improves loss by 2.76969458e-06. Readout restoration at R33 is the inverse of `f05_R33`→`f06`, costing 9.40333960e-08.

## Attribution of the endpoint gap

6.9221039823e-05 − 3.5484727022e-05 = **3.3736312801e-05**. Positive entries are loss recovered by relaxing the named constraint/package; negative entries worsen it. They telescope exactly along the forward path.

| Change | Recovered 1−F | Fraction of gap | What recovery would require on the grid (inference) |
|---|---:|---:|---|
| Joint B+C preparation package | +1.21097676e-05 | +35.895% | A smaller/cleaner preparation preserving rejection of dangerous B faults, with its finish time and acceptance maintained. Fewer CX alone is not sufficient. |
| Grid A preparation package → standard A210 | +6.78502417e-06 | +20.112% | A short, clean Steane logical plus encoder or economical verification that removes its dangerous Z-hook interactions without delaying the round. |
| Remove data hops/guards | -3.51207394e-07 | -1.041% | No gain on this path. A no-hop layout must improve timing or another package to compensate; deleting the transfers alone loses. |
| Compact delayed prefix | -2.76969458e-06 | -8.210% | No standalone gain at fixed R. Earlier releases must be paired with an earlier round; delayed checks otherwise protect part of the wait. |
| Advance suffix R45→R33 | +1.60413424e-05 | +47.549% | Ancillas ready immediately after the compact prefix on genuinely available cells; this couples placement, release times, encoder depth, and movement. |
| Direct readout instead of two parity gadgets | +9.40333960e-08 | +0.279% | Equivalent detector information with direct A/C measurement. The measured benefit is small. |
| v23 prefix → older prefix, matched A210 | +1.79341548e-06 | +5.316% | Recover the older prefix’s better early-round fault distribution; the six additional prefix CX do not prevent it from winning here. |
| Reference A-order bridge A210→A012 | +3.36316735e-08 | +0.100% | An ordering detail of the reference, not a grid-imposed constraint. |

Prefix compaction plus round advancement together recover **1.32716478e-05 (39.339% of the gap)**. Quoting only the R45→R33 gain would overstate the benefit of the complete scheduling change.

### Direct sep33 prefix control

| Rung / output | Change | Exact 2nd | 3rd correction | Total through 3rd | Delta | exp(-A1) | CX |
|---|---|---:|---:|---:|---:|---:|---:|
| [f06_sep33_v23](f06_sep33_v23.exact.txt) | Published A012/B/C/round rebuilt on compact v23 prefix | 3.43361055e-05 | 3.16628010e-06 | **3.75023856e-05** | +0.00000000e+00 | 0.6741704 | 123 |
| [f07_sep33_old](f07_sep33_old.exact.txt) | Published older prefix, identical suffix | 3.33884940e-05 | 2.09623306e-06 | **3.54847270e-05** | -2.01765857e-06 | 0.6728310 | 129 |

With the literal reference A012 encoder, v23’s prefix costs **2.01765857e-06**: second-order difference 9.47611539e-07, third-order difference 1.07004703e-06. The A210 matched-prefix difference is 1.79341548e-06. Thus the prefix price itself depends on the ancillary encoder.

## Mechanisms

Each row’s `.exact.txt` contains exact2 `--top 40` fault pairs and the largest triple sets; `.price.json` contains aggregate pair classes, examples, raw weight-3 sum, normalization correction, and retained triple classes. Regions follow unit provenance. `data_cell_idle` follows suffix data-token movement and includes long runs beginning before32; it is deliberately broader than a post32 waiting window.

| Transition | Largest pair-class deltas, current minus previous | Third-order delta |
|---|---|---:|
| 0→1: Separate B/C, 9+9 CX; R45 | BC x BC: -6.748935e-06; BC x round: -1.395556e-06; A x BC: -4.925339e-07 | -3.47274331e-06 |
| 1→2: Best tested standard A, order210; R45 | A x data_cell_idle: -1.894787e-06; A x BC: -1.377778e-06; A x A: -1.224299e-06 | -1.02813089e-06 |
| 2→3: Remove hops and guards; R45 | All pair-class sums unchanged (within 1e-18) | +3.51207394e-07 |
| 3→4: Only compact prefix to end32; R45 | data_cell_idle x data_cell_idle: +6.843293e-07; A x data_cell_idle: +5.551457e-07; data_cell_idle x prefix: +1.994335e-07 | +1.48489902e-06 |
| 4→5: Only advance suffix to R42 | A x data_cell_idle: -6.578313e-07; data_cell_idle x data_cell_idle: -4.100496e-07; data_cell_idle x prefix: -2.137952e-07 | -3.70829146e-06 |
| 5→6: Only advance suffix to R39 | A x data_cell_idle: -6.604697e-07; data_cell_idle x data_cell_idle: -4.116942e-07; data_cell_idle x prefix: -2.146526e-07 | -3.00099468e-06 |
| 6→7: Only advance suffix to R36 | A x data_cell_idle: -6.631186e-07; data_cell_idle x data_cell_idle: -4.133454e-07; data_cell_idle x prefix: -2.155135e-07 | -2.36680703e-06 |
| 7→8: Only advance suffix to R33 | A x data_cell_idle: -6.657782e-07; data_cell_idle x data_cell_idle: -4.150032e-07; data_cell_idle x prefix: -2.163779e-07 | -1.80761972e-06 |
| 8→9: Direct readout; v23 prefix, R33 | BC x round: -8.444444e-08; A x data_cell_idle: +0.000000e+00; A x A: +0.000000e+00 | -9.58895158e-09 |
| 9→10: Older prefix; retain A210, R33 | A x data_cell_idle: -4.368504e-07; data_cell_idle x prefix: -1.384821e-07; A x prefix: -6.645985e-08 | -1.07160658e-06 |
| 10→11: Restore reference A012; published sep33 | A x BC: +1.777778e-07; A x data_cell_idle: -1.775486e-07; A x A: -2.222222e-08 | -2.81622742e-09 |

The second-order round×round contribution stays **2.88400e-5** throughout the matched ladder, including direct readout. The direct-readout benefit here comes from cross-region faults, not lowering that tail. At R33 the remaining largest triples involve prefix idle faults and a final readout fault rather than three long post-prefix data waits.

| Rung | Largest retained weight-3 set | Contribution |
|---|---|---:|
| v23h_c2c9; R45 | L182 idle Z@q10 t=31..44 + L162 idle Z@q3 t=28..43 + L172 idle Z@q0 t=30..43 | 1.13019773e-07 |
| Separate B/C, 9+9 CX; R45 | L182 idle Z@q10 t=31..44 + L162 idle Z@q3 t=28..43 + L172 idle Z@q0 t=30..43 | 1.13019773e-07 |
| Best tested standard A, order210; R45 | L182 idle Z@q10 t=31..44 + L162 idle Z@q3 t=28..43 + L172 idle Z@q0 t=30..43 | 1.13019773e-07 |
| Remove hops and guards; R45 | L165 idle Z@q4 t=29..44 + L162 idle Z@q3 t=28..43 + L172 idle Z@q0 t=30..43 | 1.28993808e-07 |
| Only compact prefix to end32; R45 | L165 idle Z@q4 t=29..44 + L174 idle Z@q15 t=30..44 + L192 idle Z@q20 t=33..44 | 1.03862757e-07 |
| Only advance suffix to R42 | L165 idle Z@q4 t=29..41 + L174 idle Z@q15 t=30..41 + L192 idle Z@q20 t=33..41 | 5.09371369e-08 |
| Only advance suffix to R39 | L165 idle Z@q4 t=29..38 + L174 idle Z@q15 t=30..38 + L192 idle Z@q20 t=33..38 | 1.97089273e-08 |
| Only advance suffix to R36 | L165 idle Z@q4 t=29..35 + L174 idle Z@q15 t=30..35 + L299 flip Z@q23 t=38 | 4.63257547e-09 |
| Only advance suffix to R33 | L134 idle Z@q3 t=20..26 + L146 idle Z@q15 t=22..27 + L298 flip Z@q24 t=35 | 4.63257547e-09 |
| Direct readout; v23 prefix, R33 | L134 idle Z@q3 t=20..26 + L146 idle Z@q15 t=22..27 + L296 flip Z@q24 t=35 | 4.63257547e-09 |
| Older prefix; retain A210, R33 | L144 idle Z@q3 t=23..29 + L156 idle Z@q15 t=25..30 + L305 flip Z@q24 t=35 | 4.63257547e-09 |
| Restore reference A012; published sep33 | L144 idle Z@q3 t=23..29 + L156 idle Z@q15 t=25..30 + L305 flip Z@q24 t=35 | 4.63257547e-09 |

| Transition | Delta raw weight-3 sum | Delta pair-times-others correction | Largest retained triple-class deltas (partial sums) |
|---|---:|---:|---|
| 0→1 | -5.95951163e-06 | +2.48676832e-06 | BC x round x round: -6.603822e-07; BC x data_cell_idle x data_cell_idle: -5.982496e-07 |
| 1→2 | -1.46057190e-06 | +4.32441012e-07 | A x data_cell_idle x data_cell_idle: -3.710946e-07; A x data_cell_idle x prefix: -3.242309e-07 |
| 2→3 | +1.23499280e-06 | -8.83785403e-07 | data_cell_idle x data_cell_idle x data_cell_idle: +5.246775e-07; prefix x round x round: +5.223005e-07 |
| 3→4 | +1.81768268e-06 | -3.32783661e-07 | data_cell_idle x data_cell_idle x data_cell_idle: +5.893011e-07; data_cell_idle x data_cell_idle x round: +3.363976e-07 |
| 4→5 | -4.02948913e-06 | +3.21197675e-07 | data_cell_idle x data_cell_idle x data_cell_idle: -1.062083e-06; data_cell_idle x data_cell_idle x prefix: -6.279349e-07 |
| 5→6 | -3.31475575e-06 | +3.13761073e-07 | data_cell_idle x data_cell_idle x data_cell_idle: -7.036959e-07; data_cell_idle x data_cell_idle x prefix: -5.331535e-07 |
| 6→7 | -3.30361356e-06 | +9.36806529e-07 | prefix x round x round: -5.695520e-07; data_cell_idle x data_cell_idle x prefix: -4.454057e-07 |
| 7→8 | -1.87813340e-06 | +7.05136891e-08 | data_cell_idle x data_cell_idle x prefix: -3.318975e-07; data_cell_idle x data_cell_idle x data_cell_idle: -2.210475e-07 |
| 8→9 | -2.81120637e-08 | +1.85231121e-08 | round x round x round: -9.253333e-09; data_cell_idle x prefix x round: -4.142726e-09 |
| 9→10 | -8.80673157e-07 | -1.90933419e-07 | prefix x round x round: +1.881902e-07; data_cell_idle x data_cell_idle x prefix: -1.653644e-07 |
| 10→11 | -4.34888417e-09 | +1.53265676e-09 | A x data_cell_idle x round: -9.684526e-09; A x data_cell_idle x prefix: -6.539867e-09 |

The full third-order correction includes **all** weight-3 contributions and the signed pair-times-others correction. Individual triple examples are retained only above exact2’s threshold, so retained triple-class totals are partial and are never substituted for the exact total.

## A-encoder order control

| Rung / output | Change | Exact 2nd | 3rd correction | Total through 3rd | Delta | exp(-A1) | CX |
|---|---|---:|---:|---:|---:|---:|---:|
| [f02_stdA](f02_stdA.exact.txt) | 012 | 3.86591701e-05 | 1.22186776e-05 | **5.08778478e-05** | +0.00000000e+00 | 0.6014347 | 137 |
| [a_order021](a_order021.exact.txt) | 021 | 3.81387042e-05 | 1.22059994e-05 | **5.03447035e-05** | -5.33144249e-07 | 0.6014347 | 137 |
| [a_order102](a_order102.exact.txt) | 102 | 3.94317613e-05 | 1.22314026e-05 | **5.16631639e-05** | +7.85316152e-07 | 0.6014347 | 137 |
| [a_order120](a_order120.exact.txt) | 120 | 3.82475083e-05 | 1.22114918e-05 | **5.04590001e-05** | -4.18847662e-07 | 0.6014347 | 137 |
| [a_order201](a_order201.exact.txt) | 201 | 3.91159646e-05 | 1.22364113e-05 | **5.13523760e-05** | +4.74528189e-07 | 0.6014347 | 137 |
| [a_order210](a_order210.exact.txt) | 210 | 3.80983967e-05 | 1.22278513e-05 | **5.03262480e-05** | -5.51599754e-07 | 0.6014347 | 137 |

These six rows differ only in A’s three layer order, with every other operation and native time fixed. Delta is versus012. This establishes the chosen standard encoder order for the forward rung, not a global synthesis optimum.

## Verification, execution, and limitations

- **Measured:** every reported rung passes exact2’s real noiseless judge path, has noiseless acceptance ≈1, and c1 below1e-12. Native times and per-layer cell exclusivity are checked by `build.py` against `tprep.noise.schedule`, not just requested metadata. `.command.json` records the command, process exit, environment, and launch load. The original v23 control is also measured by unmodified exact2 in [f00_base.exact.txt](f00_base.exact.txt).
- **Exact evaluator:** the task brief’s statement that exact2 ignores adjacency is false for this checkout: Model calls the adjacency-checking QASM converter. `price.py` applies the existing grid-free override from MAIN/gf/exact_gf.py. Noise, correctness, conditional acceptance, decoder, and error probabilities remain unchanged.
- **Performance change:** `filtered_price.py` uses dependent detector-projector identities to remove classes with mathematically zero postselected amplitude, then runs exact2’s original surviving fault enumeration and third-order normalization. It does not threshold surviving contributions. [pruning_validation.json](pruning_validation.json) shows zero difference in second, third, total, raw weight3, normalization, and exp(-A1) against unmodified exact2 on both v23 and the no-hop control. The exact2 function source hash is printed in pruned receipts.
- **Execution:** initial unpruned B+C/A jobs on zebra were terminated by PID and rerun to completion on sunfish. Zebra’s capacity guard rejected subsequent launches when shared usage rose; those required runs were routed to sunfish. All reported values have successful completed receipts. The early-initialized reverse-hop construction is retained and explicitly excluded as described above. No worker is intentionally left running.
- **Inferred:** proposed grid changes are implications of counterfactual prices. No new on-grid circuit, static/dynamic embedding feasibility claim, global lower bound, or measured noisy-judge Monte Carlo score is supplied. Original cell-release constraints couple the encoders and hops, so these independent package savings cannot simply be pasted into a grid circuit.
- **Scope:** writes are confined to this lane; Other lanes were read only; submission credentials were never read. No submission, commit, push, or sub-agent was used.

## Reproduction

From the repository root, use Python `.venv/bin/python` and set `PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` for every invocation.

1. `work/lanes/LADDER/build.py` builds the standard012 controls; `work/lanes/LADDER/build_best.py` builds the selected A210 family; `work/lanes/LADDER/fix_hop_init.py` makes the corrected R37 reverse-hop comparison.
2. `.venv/bin/python work/lanes/LADDER/price.py work/lanes/LADDER/<stem>.qasm --third --top 40 --procs 1 --json work/lanes/LADDER/<stem>.sens.json > work/lanes/LADDER/<stem>.exact.txt` writes the exact receipt and `.price.json`. Set `LADDER_PRUNE=0` for unmodified exact2 enumeration; it is slower but gives the same numbers.
3. `run.py <stem> ...` runs a finite batch, checks host headroom before every launch, and waits on process exit. Use `LADDER_JOBS` within the task’s host limits. All exact commands used are in adjacent `.command.json` files.
4. `report.py` regenerates this report only from passing completed receipts. [source_receipts.json](source_receipts.json) records original source hashes; rung JSON contains all native units and their provenance.
