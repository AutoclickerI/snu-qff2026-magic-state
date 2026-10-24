**Best verified: `v35/tightened/restore_181_182_188_40` — all-orders 4.376000682648e-05, acceptance 0.500852468; judge PASS, XTIM FAST; MC3 mean 4.377146333e-05.**

# ST2 — v35a acceptance knapsack

**Complete.** All ST2 v34/v35 jobs exited. All changes and outputs are lane-local. Base independently reproduced: 4.393527676042e-05, acceptance 0.501236938624. Candidate acceptance floor: 0.5005.

Best all-orders gain: 1.752699339e-07 (0.3989%). It has 210 CX, R44, native depth 47. The five wait guards, A flag, blue checks, and q15 terminal instrument stay. The selected bundle adds q15–q21 X (CX times 20/29, readout 30) and q20–q26 Z (CX times 20/30, readout 31), changes q19's post-guard reset at t33 to a checked Z measurement, and funds them using selected initialization checks.

Finalists (all judge PASS and XTIM FAST):

| Stem under ST2 | All-orders loss | Acceptance | Judge 1e6 acceptance / seconds | MC3 mean |
|---|---:|---:|---:|---:|
| `v35/tightened/restore_181_182_188_40` | 4.376000682648e-05 | 0.500852468 | 0.500664 / 2.566 | 4.377146333e-05 |
| `v35/tightened/restore_181_182_188` | 4.376021340833e-05 | 0.501688350 | 0.501538 / 2.410 | 4.461938667e-05 |
| `v35/selected_initial/choice_000` | 4.376390893378e-05 | 0.500865666 | 0.500570 / 2.693 | 4.491338667e-05 |

The all-orders rank is authoritative for this supported family. Three MC draws cannot resolve the small improvement. The first candidate’s MC3 mean was 2.4 standard errors above its all-orders value; it is recorded without claiming an MC-confirmed gain. Individual seeds, errors, hashes and speed probes are in each `.gate.json` / `.mc3.log`.

Physical guard removal prices, relative to v35a (positive Δloss is worse; positive Δacceptance is recovered budget):

| Guard removed | Δloss | Δacceptance | Δloss / Δacceptance |
|---|---:|---:|---:|
| `fasttrack/guard_273_off` | 2.487223959e-07 | 0.002450077 | 1.015161580e-04 |
| `fasttrack/guard_274_off` | 2.605921544e-07 | 0.008352024 | 3.120107639e-05 |
| `fasttrack/guard_275_off` | 8.640275865e-07 | 0.001943438 | 4.445871763e-04 |
| `fasttrack/guard_276_off` | 6.184680759e-07 | 0.005816765 | 1.063250974e-04 |
| `fasttrack/guard_277_off` | 9.527840679e-07 | 0.007673435 | 1.241665643e-04 |

Ported additions, relative to v35a (individual prices; combinations were separately repriced):

| Addition | Loss | Acceptance | Δloss |
|---|---:|---:|---:|
| `additions/echo_10_16_X_21_22` | 4.393441210454e-05 | 0.500467215 | -8.646558793e-10 |
| `additions/echo_10_16_X_21_27` | 4.393217315388e-05 | 0.499633390 | -3.103606541e-09 |
| `additions/echo_15_21_X_20_29` | 4.377045625047e-05 | 0.496147736 | -1.648205100e-07 |
| `additions/echo_20_26_Z_20_30` | 4.392804386242e-05 | 0.495819718 | -7.232898003e-09 |
| `additions/watch16_t30` | 4.393477314722e-05 | 0.500733542 | -5.036131991e-10 |

The five other v34 echo geometries are already the five v35a guards. The long q10–q16 echo can be funded (`repaired/long_echo_funded`: 4.3760487731311e-5, acceptance 0.5012620476), but retaining useful preparation checks ranks better. q16 watch was absent from v35a; its added t30 parity check was priced explicitly.

Coverage and selection:

- Full prices: [all_prices.csv](v35/all_prices.csv) and [all_prices.json](v35/all_prices.json): 187 alternatives, 184 numerical all-orders prices, 3 rejected instruments with reasons. Includes all 70 detector rows, every non-guard singleton known-zero measurement before R44 in omit/reset forms, all five guards, three blue branches, four terminal redundant copies, the A flag, initialization variants and all ported echoes.
- `base.detector_prices.json` uses exact reverse-contraction marginals; the base exactly matches MAIN, and the lane sparse evaluator is byte-identical to MAIN’s. All feasible ranked combinations use the 72-observable canonical all-orders contraction; cutoff error bounds are around 1.2e-14.
- Marginal knapsack proposals use CP-SAT; complete circuits are repriced. Omission of a helper’s first measurement interacts strongly with an earlier echo and invalidates additive acceptance estimates. `selected_second/` preserves those exact acceptance rejections. `refined/`, `repaired/` and `tightened/` contain the conditional correction and final selection.
- This is the best measured bundle in this search, not a proof of global optimality. A formal subset optimum was not claimed.

Carryover: the old v34 selector and physical sweep were preserved and completed. `v34/REPORT_at_v35_handoff.md` retains prior gates; `v34/physical/results.json`, `v34/selected/results.json` and `v34/exchange/results.json` retain their results. Their cheap initialization removals informed the new sweep, but every chosen change was repriced on v35a.

Best circuit differences from v35a are recorded in `v35/best_changes.json`. No submissions, commits, pushes, credentials or collaboration tools were used.
