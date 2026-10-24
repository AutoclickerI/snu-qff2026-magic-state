# ST2

**Status: VERIFIED IMPROVEMENT — exchange candidate passes every local gate; separate-block construction remains open.**

The population is seeded from the verified v25k/final_m04_l2 family, v23/v22 controls, LNS and BCFB/BCPOL finalists, plus ST1's moving-boundary exchange candidate. Each mutation rewrites a native operation window (initialization/check, commuting schedule, transfer phase, readout edge, or timing), then applies the LNS precedence retimer and nearest-neighbour repair. Second-order exact loss is used only to screen a diverse population; retained candidates are rescored with exact third order and the unchanged judge gates.

## Best verified circuit

`seed_exchange4` (`seed_exchange4.qasm`/`seed_exchange4.json`) is v25k with a fused q4/q10 terminal cat/data exchange and its detector-frame repair. It has **214 CX**, native depth 51 and R48. Unmodified `EVAL/exact2.py --third` gives **5.04834243469e-5 + 1.40934821880e-5 = 6.45769065349e-5**, with `|c1|=2.66e-19` and `exp(-A1)=0.510800572`. This is 4.73196e-7 below v25k (0.73%). The all-orders Walsh evaluator was attempted and rejected its documented width limit (26 > 23), so no all-orders value is claimed.

The unchanged judge at 1e6 shots passes format, class, correctness and acceptance: **1-F=6.85604e-5, acceptance=0.510499, 214 CX**. The final zebra `fast_check` run is **3.5 s/1e6**, under 20 s. The three 1e8-shot MC runs (sunfish, same `fast_check` implementation) are **6.455819e-5 / 6.428290e-5 / 6.546180e-5**, mean **6.476763e-5**, with seed-0 acceptance 0.51078. Receipts: `seed_exchange4.exact.log`, `seed_exchange4.mc3.log`, `seed_exchange4.walsh.log`.

This result is immediately verified and supersedes v25k for ST2. It retains the known blue-XZ/q19 speed repair and adds the moving-boundary exchange; relative to v25k, only the terminal cat/data window and its detector/frame map change.

## Separate-block target

I read LADDER's complete report and built a ST2 copy of its standard 9-CX template with the FREELAY native teleport/retiming model. The model was run across all eight board symmetries and four translations with 2–6 block moves per wire and 3–6 data moves. The separate endpoint/round constraints were infeasible in the completed bounded runs; no physical separate-B/C QASM was emitted. This does not refute a different moving-prefix or instrument construction. The LADDER `f01_sepBC` result remains a grid-free price only. A shortest-path SWAP routing of that counterfactual was emitted as `routed_f01_sepBC`, but its 391 CX circuit fails acceptance (0.0185), so it is retained only as a negative control.

## Population method and statistics

The evolutionary search used seeds from v25k, v23/v22, LNS, BCFB, BCPOL and ST1, and mutations over whole native windows: timing retiming, initialization/check replacement, commuting swaps, phase placement and readout edges. Each mutation used LNS's precedence repair and nearest-neighbour assertions. Two generations evaluated **90** candidates (**88** exact-valid, 87 with `exp(-A1)≥0.5002`); the second-order Pareto front's best was 5.04390095321e-5 with acceptance proxy 0.509946, and the high-acceptance survivor was 5.04629184005e-5 at 0.514995. The verified exchange seed was then independently third-order priced and MC-ranked. The compressed trace is `population.jsonl.xz`; per-generation fronts are `generation_0.json` and `generation_1.json`.

The exact/MC verified candidate is independent of the separate-block relaxation. No ST2 submission, commit, push or credential access occurred.

## Verified versus inferred

Verified: exact2 third-order arithmetic with `|c1|<1e-12`; unchanged `tprep.check` at 1e6 shots; seed-0 acceptance; zebra speed; all three 1e8 MC seeds; nearest-neighbour and format assertions from the repair; and the 90-candidate population receipts. The Walsh all-orders result is a documented width rejection, not a score. The separate-block result is only a completed bounded solver screen plus a negative SWAP-routed control.

Inferred: the exchange candidate's improvement is a local macro effect, and a different dynamic separate-block embedding may still exist. No global optimum, physical separate-B/C construction, server runtime, or all-orders score is claimed.
