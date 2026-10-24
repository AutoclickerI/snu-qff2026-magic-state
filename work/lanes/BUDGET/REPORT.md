# BUDGET lane report

The combined winner is unchanged v17a. Its exact through-third loss is `8.2454119e-5`; the required three-seed MC mean is `8.347295e-5`. No tested initialization, re-encoding, detector/frame, timing, or combined variant beats it.

## 1. Lever results

`delta` is exact through-third total minus v17a (`8.2454119e-5`). The re-encoding row names the best exact-second candidate; its through-third value is the quantity used for the final decision.

| Lever | Best tested variant | Exact 2nd | Exact 3rd | Exact total | exp(-A1) | delta vs v17a |
|---|---|---:|---:|---:|---:|---:|
| v17a baseline | `v17a` / `final/baseline_v17a.qasm` | 5.7077248e-5 | 2.5376870e-5 | **8.2454119e-5** | 0.5428664 | 0 |
| Initialisation | `v17a` (all 12 measure-inits); best model-frontier reset candidate `i_c80` was worse | 5.7077248e-5 | 2.5376870e-5 | **8.2454119e-5** | 0.5428664 | 0 |
| Re-encoding | `r0771`: `14:15,8:9,17:16,19:25` (best exact 2nd) | 5.6954715e-5 | 2.5651578e-5 | 8.2606293e-5 | 0.5419985 | +1.5217e-7 |
| Detector/frame | full declared detector set, empty auto frame (`v17a`) | 5.7077248e-5 | 2.5376870e-5 | **8.2454119e-5** | 0.5428664 | 0 |
| Timing | v17a release/drop schedule; barrier variants were equal | 5.7077248e-5 | 2.5376870e-5 | **8.2454119e-5** | 0.5428664 | 0 |
| Combined | `combined_best` (v17a; tested r0771 + i_c80 separately and jointly) | 5.7077248e-5 | 2.5376870e-5 | **8.2454119e-5** | 0.5428664 | 0 |

Initialization finalist checks: `i_c80` (reset q14, q2, q9, q20, q16, q23, q27, q21, q22) had exact total `8.2604096e-5`; `i_002` had `8.2456683e-5`; `i_006` had `8.2456906e-5`; `i_d9f` had `8.2696976e-5`. The exact second-order polynomial tied these candidates at `5.7077248e-5`, but their third-order terms were higher. The direct combined test `r0771` plus the `i_c80` initialization mask was also worse: exact total `8.2760305e-5` (second `5.6954715e-5`, third `2.5805591e-5`).

The zero-CX timing scan covered the two late barrier removals, both together, and dummy CXs `19->20`, `16->10`, `16->22`, their two-way combination, and all three. The barrier variants were exactly equal to v17a. Every dummy-CX candidate failed the noiseless correctness gate because the available neighbor was not a checked `|0>` partner.

## 2. Initialization polynomial fit

The 12 binary variables are reset (`1`) versus measure-init (`0`) at q = `[14,2,9,20,16,28,29,23,27,25,21,22]`. The design contains the intercept, all singles, all pairs, and all triples: `299` points and `299` coefficients. Held-out validation uses `64` exact second-order runs.

| Response fitted from exact2 | Train points | Held-out points | Max fit residual | Held-out MAE | Held-out RMSE | Held-out max |
|---|---:|---:|---:|---:|---:|---:|
| Exact second-order `1-F` | 299 | 64 | 2.71e-19 | 7.97e-18 | 1.13e-17 | 3.57e-17 |
| `A1` | 299 | 64 | 2.66e-15 | 8.69e-14 | 1.23e-13 | 4.03e-13 |
| `exp(-A1)` | 299 | 64 | 4.22e-15 | 1.53e-10 | 2.42e-10 | 8.85e-10 |

The exact through-third values above are checked directly for the baseline, the model-frontier finalists, the best re-encoding finalists, and the combined candidate; the polynomial is reported for the exact2 response it was fit to, never used alone as a final score. The top-20 polynomial masks were all exact-second screened; a 20-way third-order batch was attempted on owl but exceeded the practical runtime and was stopped, so their third-order values remain unverified. Artifacts: [`init_polynomial.json`](init_polynomial.json), [`init_pred_top100.json`](init_pred_top100.json), and [`manifest.json`](init_scan/manifest.json).

## 3. Final candidates

Every listed candidate has a paired JSON with `data_qubits`. `tprep.check` was run at `10^6` shots by `mc3.py`; the MC entries are `10^8` shots at seeds 0, 1000, and 2000.

| Candidate | Exact 1-F (through 3rd) | MC seed 0 | MC seed 1000 | MC seed 2000 | MC mean | Seed-0 acceptance | CX | Files |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **combined_best / v17a** | **8.2454119e-5** | 8.393188e-5 | 8.355687e-5 | 8.293009e-5 | **8.347295e-5** | 0.54300 | 209 | [`combined_best.qasm`](final/combined_best.qasm), [`combined_best.json`](final/combined_best.json) |
| initialization `i_c80` | 8.2604096e-5 | 8.300588e-5 | 8.525219e-5 | 8.300693e-5 | 8.375500e-5 | 0.54574 | 209 | [`init_c80.qasm`](final/init_c80.qasm), [`init_c80.json`](final/init_c80.json) |
| re-encoding `r0771` (best exact 2nd) | 8.2606293e-5 | 8.432673e-5 | 8.430665e-5 | 8.389647e-5 | 8.417662e-5 | 0.54212 | 211 | [`reenc_r0771.qasm`](final/reenc_r0771.qasm), [`reenc_r0771.json`](final/reenc_r0771.json) |

Scan coverage: all `4096` initialization combinations were emitted; the polynomial design/held-out exact2 set was `299 + 64`. The re-encoding generator emitted `1953` directed matching sets; `1216` passed the noiseless correctness check and `737` were rejected. The detector/frame scan emitted `139` variants. No submission, commit, or push was made.
