# PRE: acceptance spent on cultivation

Added double-cat checks do not pay in the measured families. The best one-addition candidate raises exact second-order loss by 8.96% and the three-seed judge mean by 13.20%. Its A1 increment is 0.15878, inside the proposed spare budget. The scheduling winner lowers second-order loss by 0.7567% for only ΔA1=0.00393, but the requested Monte Carlo runs do not establish a true-mean improvement over v12. Retain v12 on the measured three-seed criterion.

Baseline reproduced before variant scoring: **loss2=1.1219494706696269e-4, loss1=4.9032383092e-19, A1=0.370303793945133**, exp(-A1)=0.690524522. The supplied rounded targets match. `v12_reference.qasm` reconstructs v12 byte for byte.

25 full circuits have exact CLI receipts and judge checks at 1e6 shots; 21 pass, including the reference. Every row below passes format, class, correctness and acceptance. Four other two-addition schedules fail acceptance (0.490202–0.497099) and are excluded; their exact/check/split receipts remain available. The two valid two-addition circuits consume almost all acceptance and leave no room for the proposed next round.

All tables use the native judge schedule, with zero-based steps. **End** is the last cultivation operation; **D** is full circuit depth. v12 overlaps cultivation and its final cycle, so its cultivation ends at step 37 rather than the cited v11 boundary at 33. The ALAP winner delays some cultivation readouts until step 40 while keeping total depth 42. The saved LNS `npre=148` was an optimization cutoff: the actual final cycle begins at construction node 137. All 25 emitted native suffixes were compared against v12 for identical gates and relative timing (`suffix_audit.json`); classical bits were shifted for added checks.

## Exact results

Each name links to its QASM; the matching `.json` contains `data_qubits`, construction schedule, native schedule, source and hash. `.exact.log`/`.exact.json` are uncached `exact2.py` CLI output. First-order values below 9e-18, including tiny negative values, are floating-point zero. Δ is relative to the reproduced v12 loss2.

| Variant | CX | End / D | Exact loss2 | First order | Pre A1 | Total A1 | exp(-A1) | Judge acceptance | Δ loss2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [v12_reference](v12_reference.qasm) | 115 | 37 / 42 | 1.12194947e-04 | 4.90e-19 | 0.322040 | 0.370304 | 0.690525 | 0.690309 | +0.000% |
| [extra1_s0](extra1_s0.qasm) | 139 | 50 / 56 | 1.27214362e-04 | 1.60e-18 | 0.498784 | 0.548382 | 0.577884 | 0.577095 | +13.387% |
| [extra1_s1](extra1_s1.qasm) | 139 | 51 / 57 | 1.24560021e-04 | 1.60e-18 | 0.502174 | 0.551771 | 0.575929 | 0.575400 | +11.021% |
| [extra1_s4](extra1_s4.qasm) | 139 | 49 / 55 | 1.25336272e-04 | 1.92e-18 | 0.489398 | 0.538995 | 0.583334 | 0.582422 | +11.713% |
| [extra1_s8](extra1_s8.qasm) | 139 | 50 / 56 | 1.24919028e-04 | 1.60e-18 | 0.502357 | 0.551954 | 0.575823 | 0.575058 | +11.341% |
| [extra1_pinned_s0](extra1_pinned_s0.qasm) | 139 | 50 / 55 | 1.24129287e-04 | 1.60e-18 | 0.490214 | 0.538478 | 0.583636 | 0.583202 | +10.637% |
| [extra1_pinned_s4](extra1_pinned_s4.qasm) | 139 | 49 / 54 | 1.22251219e-04 | 5.03e-19 | 0.480821 | 0.529085 | 0.589144 | 0.588485 | +8.963% |
| [extra2_s4](extra2_s4.qasm) | 163 | 61 / 67 | 1.34319580e-04 | 8.29e-18 | 0.635441 | 0.685039 | 0.504071 | 0.503466 | +19.720% |
| [extra2_pinned_s4](extra2_pinned_s4.qasm) | 163 | 62 / 67 | 1.32793512e-04 | 8.39e-18 | 0.641037 | 0.689301 | 0.501927 | 0.502015 | +18.360% |
| [alap_ordered](alap_ordered.qasm) | 115 | 40 / 45 | 1.14021835e-04 | 4.92e-19 | 0.362742 | 0.412340 | 0.662099 | 0.661758 | +1.628% |
| [alap_commuting](alap_commuting.qasm) | 115 | 38 / 43 | 1.11699258e-04 | 4.90e-19 | 0.333399 | 0.381663 | 0.682725 | 0.681751 | -0.442% |
| [alap_best](alap_best.qasm) | 115 | 40 / 42 | 1.11345944e-04 | -3.14e-18 | 0.326636 | 0.374233 | 0.687816 | 0.686784 | -0.757% |
| [central_verify_s0](central_verify_s0.qasm) | 115 | 38 / 44 | 1.17904338e-04 | 4.92e-19 | 0.353190 | 0.402788 | 0.668454 | 0.667533 | +5.089% |
| [central_verify_s4](central_verify_s4.qasm) | 115 | 37 / 43 | 1.15943911e-04 | 4.92e-19 | 0.343778 | 0.393375 | 0.674776 | 0.673999 | +3.341% |
| [central_retain_s0](central_retain_s0.qasm) | 115 | 37 / 43 | 1.16696699e-04 | 4.92e-19 | 0.339662 | 0.389259 | 0.677559 | 0.676996 | +4.012% |
| [central_retain_s4](central_retain_s4.qasm) | 115 | 36 / 42 | 1.14604932e-04 | 4.92e-19 | 0.330246 | 0.379843 | 0.683969 | 0.683751 | +2.148% |
| [central_retain_pinned](central_retain_pinned.qasm) | 115 | 37 / 42 | 1.12194947e-04 | 4.90e-19 | 0.323373 | 0.371637 | 0.689604 | 0.688692 | +0.000% |
| [late_verify_s0](late_verify_s0.qasm) | 115 | 38 / 44 | 1.19082090e-04 | 4.92e-19 | 0.356611 | 0.406209 | 0.666171 | 0.665558 | +6.139% |
| [late_verify_s4](late_verify_s4.qasm) | 115 | 37 / 43 | 1.16868286e-04 | 4.92e-19 | 0.347197 | 0.396795 | 0.672472 | 0.671817 | +4.165% |
| [all_verify_s0](all_verify_s0.qasm) | 115 | 39 / 45 | 1.20317322e-04 | 4.92e-19 | 0.371471 | 0.421069 | 0.656345 | 0.655380 | +7.240% |
| [all_verify_s4](all_verify_s4.qasm) | 115 | 38 / 44 | 1.18246109e-04 | 4.92e-19 | 0.362061 | 0.411659 | 0.662550 | 0.661982 | +5.393% |

## Stage attribution

A1 is summed directly from `ev.fp * (1 - ev.a_single)`. A fault pair contributes half its loss to each fault location, using `exact2.run` channel sensitivities. Gate/reset/readout channels belong to their construction stage. An idle interval is split using the steps returned by `ev.chan_label`, at the last cultivation operation on that wire. This handles the interleaved boundary without assigning all early final-cycle gates to cultivation. Cross-stage pairs are shared; these are additive attributions, not standalone-circuit infidelities. Same-channel normalization is below 8e-20 here.

| Variant | Pre A1 | Suffix A1 | Pre loss2 | Suffix loss2 |
|---|---:|---:|---:|---:|
| v12_reference | 0.322040 | 0.048264 | 1.46389699e-05 | 9.75559772e-05 |
| extra1_s0 | 0.498784 | 0.049597 | 2.03424523e-05 | 1.06871910e-04 |
| extra1_s1 | 0.502174 | 0.049597 | 1.87679841e-05 | 1.05792037e-04 |
| extra1_s4 | 0.489398 | 0.049597 | 1.92179219e-05 | 1.06118350e-04 |
| extra1_s8 | 0.502357 | 0.049597 | 1.89539752e-05 | 1.05965052e-04 |
| extra1_pinned_s0 | 0.490214 | 0.048264 | 2.11356477e-05 | 1.02993639e-04 |
| extra1_pinned_s4 | 0.480821 | 0.048264 | 1.99966915e-05 | 1.02254528e-04 |
| extra2_s4 | 0.635441 | 0.049597 | 2.40000729e-05 | 1.10319507e-04 |
| extra2_pinned_s4 | 0.641037 | 0.048264 | 2.56345291e-05 | 1.07158983e-04 |
| alap_ordered | 0.362742 | 0.049597 | 1.31269189e-05 | 1.00894916e-04 |
| alap_commuting | 0.333399 | 0.048264 | 1.43675834e-05 | 9.73316744e-05 |
| alap_best | 0.326636 | 0.047597 | 1.56328376e-05 | 9.57131062e-05 |
| central_verify_s0 | 0.353190 | 0.049597 | 1.53560682e-05 | 1.02548270e-04 |
| central_verify_s4 | 0.343778 | 0.049597 | 1.41737399e-05 | 1.01770171e-04 |
| central_retain_s0 | 0.339662 | 0.049597 | 1.46997405e-05 | 1.01996959e-04 |
| central_retain_s4 | 0.330246 | 0.049597 | 1.34000311e-05 | 1.01204901e-04 |
| central_retain_pinned | 0.323373 | 0.048264 | 1.46389699e-05 | 9.75559772e-05 |
| late_verify_s0 | 0.356611 | 0.049597 | 1.60447251e-05 | 1.03037364e-04 |
| late_verify_s4 | 0.347197 | 0.049597 | 1.46230232e-05 | 1.02245262e-04 |
| all_verify_s0 | 0.371471 | 0.049597 | 1.67286459e-05 | 1.03588676e-04 |
| all_verify_s4 | 0.362061 | 0.049597 | 1.54355321e-05 | 1.02810577e-04 |

For a literal single-time cutoff at each circuit’s End, the `.split.json` fields `pre_A1`/`suffix_A1` and `pre_loss2`/`suffix_loss2` provide that alternative temporal split; `construction_*` fields are the stage attribution above. For v12 the temporal split is A1=0.344106/0.026198 and loss2=3.306604e-5/7.912891e-5. Its construction split attributes 86.95% of loss2 to final-cycle locations. The temporal split changes sharply when harmless readouts move late, so it should not be interpreted as an isolated cultivation error rate. Every channel’s steps, A1, loss contribution and split fractions are saved.

## Judge Monte Carlo, 1e8 shots per seed

All four circuits pass every judge gate at seeds 0, 1000 and 2000 through unchanged `work/fast_check.py`. Means rank candidates; the seed-0 key is the score rounded to three significant figures. SEM below is the standard error of the three-seed mean.

| Variant | Seed 0 | Seed 1000 | Seed 2000 | Mean ± SEM | Mean acceptance | Seed-0 key |
|---|---:|---:|---:|---:|---:|---:|
| v12_reference | 1.14650959e-04 | 1.13226173e-04 | 1.11935016e-04 | 1.13270716e-04 ± 6.33e-07 | 0.690455 | 0.000115 |
| extra1_pinned_s4 | 1.28924076e-04 | 1.27428475e-04 | 1.28315376e-04 | 1.28222642e-04 ± 7.24e-07 | 0.589041 | 0.000129 |
| alap_commuting | 1.13938022e-04 | 1.13961542e-04 | 1.15648187e-04 | 1.14515917e-04 ± 6.41e-07 | 0.682700 | 0.000114 |
| alap_best | 1.13327958e-04 | 1.13924677e-04 | 1.14619912e-04 | 1.13957516e-04 ± 6.38e-07 | 0.687756 | 0.000113 |

The best exact ALAP candidate’s mean is 0.606% worse than v12 in these samples; the difference is only 0.76 combined standard errors if estimated as independent, so its true-mean advantage remains unresolved. Its seed-0 key improves from 1.15e-4 to 1.13e-4. The added-check mean is 13.20% worse, a clear loss. No submissions were made.

## Constructions and reproducibility

- `extra1_*` adds one upstream `make_chunk_d3_double_cat_check`; `extra2_*` adds two. These reuse `cultiv_port.run_chunk(..., s_to="Tswap")`. Non-pinned schedules repack the full cultivation prefix against fixed suffix deadlines; pinned schedules additionally preserve v12’s original last-check timing, isolating the effect of inserting an earlier check. `build_extra.py` and `build_pinned.py` generate them.
- `central_verify` repeats the central cat MX with a parity detector before the existing reset. `central_retain` replaces that reset with a second native MX and retains the accepted X state; the pinned version changes exactly that operation at its existing time. `late_verify` repeats all six terminal cat readouts; `all_verify` repeats both central and terminal readouts. `build_readouts.py` generates the scheduled versions. The pinned central replacement leaves loss2 unchanged and spends ΔA1=0.001333.
- `alap_ordered`, `alap_commuting` and `alap_best` are the winners of ordered reverse scheduling, commuting reverse scheduling, and subsequent local/LNS search. Forty distinct greedy schedules and 400 local proposals were exactly screened with `Eval/run`, batching identical Engine tables; all reported shortlist circuits were then rechecked through uncached `exact2.py`. `alap_best` comes from `alap_lns_0387`, selected for minimum A1 among loss2 ties within 1e-15. This is a finite search, not an optimality proof.
- `measure.py` validates and decomposes saved exact CLI output; `audit_suffix.py` checks the compiled suffix; `monte.py` runs all requested seeds; `write_report.py` creates this report. Use the repository `.venv/bin/python`, cwd `work/lanes/PRE`, bytecode disabled, numerical threads=1, and `nice -n 5`. Main exact and MC pools used eight workers, the scheduling lane four. Caches and all writes remain inside PRE.

Example exact command from PRE: `nice -n 5 /home/jihoon/competitions/quantumn/.venv/bin/python ../EVAL/exact2.py alap_best.qasm --procs 8 --top 0 --json alap_best.exact.json`. MC: `nice -n 5 /home/jihoon/competitions/quantumn/.venv/bin/python monte.py alap_best --procs 8` with `PYTHONDONTWRITEBYTECODE=1` and thread caps set.

Primary implementation sources: [cultiv_port](../../cultiv_port.py), [upstream double-cat construction](../../../upstream/magic-state-cultivation/src/cultiv/_construction/_cultivation_stage.py), [judge schedule/noise](../../../upstream/snu-qff2026-problem/tprep/noise.py), [exact evaluator](../EVAL/exact2.py), and [v12 source schedule](../L5_precycle/combined_lns_0012.json). These are local source inspections and measured results; no literature-only performance claims are used.
