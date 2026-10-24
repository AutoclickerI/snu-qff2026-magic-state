# BCFB

Status: RUNNING: long-budget feedback and expanded screens; no stopping on a win.

Baseline `../MAIN/v23h_c2c9`: c1 = 2.92358729818e-19, second = 5.24923143353e-5, cubic = 1.67287254875e-5, total = **6.92210398228e-05**, exp(-A1) = 0.540859577712. Independently replayed to 7e-19 in total; both 1e6-shot judge checks PASS.

Best verified exact circuit: **`finalists/ic_fast_d15_c105_s526_00356_11_19`**, exact **6.81371695706e-05** (-1.566%), exp(-A1) **0.539879952**. MC mean 6.93425767e-05, seed-0 acceptance 0.53994.

Difference from v23h_c2c9: 209 total CX; BC prep 88 CX, solver depth 15; initialization / timing options `{"timing": "alap"}`. R=45; non-BC time edits `{}`; retained preceding X states `[13]`. Repeated BC init checks `[11, 19]`; bounded-retiming changes `[]`. Hop and A gate edits are retained.

| Verified improvement stem (under finalists/) | c1 | Second | Cubic | Exact total | exp(-A1) | Judge acc, 1e6 | MC mean / seed-0 acc |
|---|---:|---:|---:|---:|---:|---:|---|
| `ic_fast_d15_c105_s526_00356_11_19` | 2.924e-19 | 5.16964460296e-05 | 1.6440723541e-05 | 6.81371695706e-05 | 0.539879952 | 0.539540 | 6.93425767e-05 / 0.53994 |
| `fast_d15_c105_s526_00356` | 2.924e-19 | 5.1729779363e-05 | 1.64614700233e-05 | 6.81912493862e-05 | 0.541682555 | 0.542001 | 6.89561267e-05 / 0.54173 |
| `fast_d15_c105_s526_00331` | 2.924e-19 | 5.18764460296e-05 | 1.64575791266e-05 | 6.83340251562e-05 | 0.541754784 | 0.541762 | 6.886457e-05 / 0.54180 |
| `fb_d14_c98_s517_00020` | 2.924e-19 | 5.21940905333e-05 | 1.65185509025e-05 | 6.87126414358e-05 | 0.542805360 | 0.542274 | 6.95871467e-05 / 0.54283 |
| `fb_d15_c105_s506_00008` | 2.924e-19 | 5.22142238074e-05 | 1.65590178273e-05 | 6.87732416347e-05 | 0.542224508 | 0.541922 | 6.988818e-05 / 0.54232 |

Completed baseline re-draw reference: 320 draws, mean **7.02717490625e-05**, SEM 5.85e-08, read from MAIN logs (rounded printed scores).

Re-draw counts below include only completed 1e8-shot seed-0 samples. Fewer than 100 draws remain provisional.

| Circuit | Completed draws | Mean | SEM | Minimum acceptance | ≥100 complete |
|---|---:|---:|---:|---:|---|
| `fast_d15_c105_s526_00331` | 43 | 6.90889489634e-05 | 1.47e-07 | 0.54169172 | False |
| `ic_fast_d15_c105_s526_00356_11_19` | 28 | 6.92096935527e-05 | 1.82e-07 | 0.53987472 | False |
| `fast_d15_c105_s526_00356` | 33 | 6.92614699098e-05 | 1.55e-07 | 0.54162784 | False |
| `fb_d14_c98_s517_00020` | 100 | 6.95196836926e-05 | 1.04e-07 | 0.54276326 | True |
| `fb_d15_c105_s506_00008` | 100 | 6.99584266161e-05 | 1.03e-07 | 0.54217084 | True |

| Formulation | Budget | Status | Witnesses | Best in-situ exact screen |
|---|---|---|---:|---:|
| Exact feedback SAT, clean BC2, depth 14/15, caps 82/90/98/105 | 20 seeds × 7200 s fresh budget, plus initial runs; host-capacity pauses recorded separately | 0/20 budgets completed | database counts below | database minimum below |
| feedback | see per-run receipts | running/completed per receipt | 37519 | 6.819124938624815e-05 |
| feedback_retime | see per-run receipts | running/completed per receipt | 7521 | 6.877616042255625e-05 |
| identity_ablation | see per-run receipts | running/completed per receipt | 4 | 6.87732416347355e-05 |
| identity_pairs | see per-run receipts | running/completed per receipt | 2 | 6.881162142551298e-05 |
| init | see per-run receipts | running/completed per receipt | 1420 | 6.917620738388794e-05 |
| init_best | see per-run receipts | running/completed per receipt | 8070 | 6.813716957061176e-05 |
| init_checks | see per-run receipts | running/completed per receipt | 1519 | 6.813716957061092e-05 |
| joint_order | see per-run receipts | running/completed per receipt | 48 | 8.154511886754059e-05 |
| late_feedback | see per-run receipts | running/completed per receipt | 1511 | 7.263024496922348e-05 |
| order | see per-run receipts | running/completed per receipt | 32 | 6.9221039822787e-05 |
| retime_probe | see per-run receipts | running/completed per receipt | 12 | 6.925338937032347e-05 |
| retry_fold | see per-run receipts | running/completed per receipt | 1600 | 6.876267831522352e-05 |
| retry_retime | see per-run receipts | running/completed per receipt | 1202 | 6.916766098583346e-05 |
| round_shift | see per-run receipts | running/completed per receipt | 72 | 6.819124938624817e-05 |
| timing | see per-run receipts | running/completed per receipt | 317 | 6.871264143581615e-05 |
| `check_retime.receipt` | 558 | COMPLETE | — | 6.858389515193274e-05 |
| `init.receipt` | — | COMPLETE | 1420 | — |
| `initbest_fast_d15_c105_s526_00356.receipt` | 108 | COMPLETE | — | 6.813716957061176e-05 |
| `initbest_fb_d14_c98_s517_00020.receipt` | 108 | COMPLETE | — | 6.865916901245245e-05 |
| `initchecks_fast_d15_c105_s526_00356.receipt` | 106 | COMPLETE | — | 6.813716957061092e-05 |
| `initchecks_fast_d15_c105_s526_00356_wide.receipt` | 859 | COMPLETE | — | 6.813716957061114e-05 |
| `joint_order.receipt` | 48 | COMPLETE | — | 8.154511886754059e-05 |
| `late_feedback.receipt` | 1500 | COMPLETE | — | 7.263024496922348e-05 |
| `order.receipt` | — | COMPLETE | — | — |
| `pairs_fb_d14_c98_s517_00020.receipt` | 2 | COMPLETE | — | 6.881162142551298e-05 |
| `retry_fold.receipt` | 1600 | COMPLETE | — | — |
| `retry_retime.receipt` | 1202 | COMPLETE | — | — |
| `round_scan.receipt` | 72 | COMPLETE | — | 6.819124938624817e-05 |
| `timing_fb_d14_c98_s517_00020.receipt` | 146 | COMPLETE | — | 6.871264143581969e-05 |
| `timing_replay.receipt` | 145 | COMPLETE | — | 6.9221039822787e-05 |
| Cell automorphisms | complete induced-graph enumeration | 2 graph automorphisms, only identity preserves target and clean predicate | 1 valid | base |

Mechanisms: SAT repair prices full-circuit X/Z correlations and idle exposure, with complete BC2-clean single-fault constraints. Depth 14/15 and CX caps 82/90/98/105 diversify the search; CX count is not a ranking objective. The transplant removes owned old initialization bits, then propagates replacement MX frames into the existing detector span. Native timing is checked after emission; strict builds retain all non-BC times, while explicitly tagged retime_window variants minimize retained-unit displacement with R fixed. Initialization masks and prep timing remain independent dimensions. In the first 207-CX winner, removing either of its added canceling CX pairs raises loss (6.89704e-5 or 6.91092e-5); removing both yields 6.93103e-5. This directly shows a benefit from the identities under the noisy schedule. The inferred mechanism is replacing idle channels with less harmful joint gate channels.

The strongest confirmed SAT network lowers loss by 1.02979e-6 relative to the base; the q11/q19 initialization checks add a 5.40798e-8 reduction. Thus about 95% of the confirmed exact gain comes from the prep network and 5% from those checks. The network uses 88 CX instead of 82 without delaying the round. These are arithmetic differences of the verified exact values, not an independent fault attribution.

R45 was initially held as a scheduling choice, then explicitly widened. The 72-case R42–R47 screen found no gain, and 1500 uniformly sampled distinct failed feedback representatives priced at R46/R47 had best 7.26302449692e-5. The fixed-order dependency path through the prefix and A encoder independently requires R45 (critical_path.json); this is not a bound on other operation orders or architectures. No extra round-time hard gate is imposed on eligibility.

Verified: deterministic full stabilizer targets; BC2 clean predicate including actual-CX XX faults; matching baseline Fourier arithmetic; native grid/timing assertions; unmodified exact2 --third for rows above (|c1|<1e-12); 1e6-shot judge and, when shown, MAIN/spec/mc3.py at 1e8 shots, seeds 0/1000/2000. Owl lacks the MAIN/spec path, so its byte-identical copy inputs/mc3.py is used (SHA-256 in mc3_provenance.log). Batched exact decoder tables agree with the original Fourier evaluator within 8e-19 on five circuits (batch_validation.json), cutting contraction ~4.9 s to .7–1.2 s. The absolute precision of CLI totals is 5.1e-11; full-precision components in the table are Fourier results cross-checked against that CLI.

Inferred/limits: third-order arithmetic is a screen, not the all-orders MC mean. No global optimum or UNSAT claim follows from a bounded search. The BCSYN2 feedback logs were absent locally and on owl, then recovered from tom and read in full (201 lines, 106 JSON records; hashes in prior_feedback_audit.json). Complete original text is preserved in the compressed witness archive. The winning old seed-401 circuit appeared after 447.0 s; the logs contain no exhaustion certificate. The initial 501–508 batch exposed a copied Unit parser bug on a single H; its errors/stops are preserved, and the corrected long batch starts at 511. Search witnesses are stored compressed in the lane database while workers run, then packaged into one tar.xz; bulk QASM files are not retained. No submission, credentials, commits or pushes; no other lane files edited.
