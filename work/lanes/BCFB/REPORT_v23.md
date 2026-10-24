# BCFB

Status: COMPLETE — all 20 full feedback budgets, the 16,384-mask sweep, requested widened screens, and finalist re-draw comparisons completed. No submission, commit or push.

Best measured circuit: **[best.qasm](best_v23.qasm)** / **[best.json](best_v23.json)**, identical to `finalists/ic_fast_d15_c105_s526_00356_11_19`. Its 100-draw seed-0 mean is **6.92879166862e-05 ± 9.96e-08 SEM**, 1.400% below the completed 320-draw v23h_c2c9 mean **7.02717490625e-05 ± 5.85e-08**. Selection uses 1-F only. Close finalist differences remain subject to the SEMs below.

Lowest observed seed-0 ordering of that same circuit: [best_seed0.qasm](best_seed0.qasm) / [JSON](best_seed0.json), draw 69. An independent 1e8-shot seed-0 replay gives **6.73146230846e-05**, acceptance **0.53992726**, PASS; bit-identical to its recorded draw: True. The native noise signature is unchanged, so its true mean and exact values are those of the selected physical circuit. [Replay receipt](SEED0_VERIFICATION.json).

Exact: c1=2.92358729818e-19, second=5.16964460296e-05, cubic=1.6440723541e-05, total=6.81371695706e-05; exp(-A1)=0.539879952. Fresh 1e6-shot seed-0 judge: PASS, acceptance 0.539540. Every re-draw passed; minimum acceptance 0.53983857.

Difference from v23h_c2c9: clean BC prep 88 CX, solver depth 15, pivots `[26, 13, 4, 12, 17, 5]`; total 209 CX, R=45. Options `{"timing": "alap"}`. Additional BC initialization checks `[11, 19]`; retained prior X states `[13]`. Non-BC timing changes `{}`; check-retiming changes `[]`. HOPS and ACHECK gate edits are retained. Detailed emitted differences are in the finalist `.diff.json`.

| Finalist stem under `finalists/` | Exact second | Cubic | Exact total | exp(-A1) | 3-seed MC mean | Re-draw mean ± SEM | Draws |
|---|---:|---:|---:|---:|---:|---:|---:|
| `ic_fast_d15_c105_s526_00356_11_19` | 5.16964460296e-05 | 1.6440723541e-05 | 6.81371695706e-05 | 0.539879952 | 6.934258e-05 | 6.92879166862e-05 ± 9.96e-08 | 100 |
| `fast_d15_c105_s526_00331` | 5.18764460296e-05 | 1.64575791266e-05 | 6.83340251562e-05 | 0.541754784 | 6.886457e-05 | 6.93454650944e-05 ± 9.54e-08 | 100 |
| `fast_d15_c105_s526_00356` | 5.1729779363e-05 | 1.64614700233e-05 | 6.81912493862e-05 | 0.541682555 | 6.895613e-05 | 6.93916085424e-05 ± 1.05e-07 | 100 |
| `fb_d14_c98_s517_00020` | 5.21940905333e-05 | 1.65185509025e-05 | 6.87126414358e-05 | 0.542805360 | 6.958715e-05 | 6.95196836926e-05 ± 1.04e-07 | 100 |
| `fb_d15_c105_s506_00008` | 5.22142238074e-05 | 1.65590178273e-05 | 6.87732416347e-05 | 0.542224508 | 6.988818e-05 | 6.99584266161e-05 ± 1.03e-07 | 100 |

Every finalist above has an unmodified `EVAL/exact2.py --third` receipt, |c1|<1e-12, a 1e6-shot judge PASS, MAIN mc3 at 1e8 shots for seeds 0/1000/2000, and at least 100 verified seed-0 re-draws. Final ranking uses those re-draw means; close finalists are not statistically separated. [Full selection receipt](FINAL_SELECTION.json), [re-draw summaries](redraw_summary.json).

| Formulation | Budget / status | Stored witnesses or prices | Best in-situ exact |
|---|---|---:|---:|
| Clean shared-signature SAT feedback, depth 14, cap 82 | 5 × 7200 s requested; all BUDGET_FINISHED, measured wall 7200.5–7217.1 s/seed | 12118 | 6.83096390558e-05 |
| Clean shared-signature SAT feedback, depth 14, cap 98 | 5 × 7200 s requested; all BUDGET_FINISHED, measured wall 7200.8–7209.7 s/seed | 10838 | 6.83096390558e-05 |
| Clean shared-signature SAT feedback, depth 15, cap 90 | 5 × 7200 s requested; all BUDGET_FINISHED, measured wall 7201.3–7213.4 s/seed | 10001 | 6.83704553041e-05 |
| Clean shared-signature SAT feedback, depth 15, cap 105 | 5 × 7200 s requested; all BUDGET_FINISHED, measured wall 7200.6–7205.2 s/seed | 11213 | 6.81912493862e-05 |
| `feedback` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 46615 (35425 scored) | 6.81912493862e-05 |
| `feedback_retime` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 10085 (5457 scored) | 6.87655619929e-05 |
| `identity_ablation` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 4 (4 scored) | 6.87732416347e-05 |
| `identity_pairs` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 2 (2 scored) | 6.88116214255e-05 |
| `init` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 1420 (515 scored) | 6.91762073839e-05 |
| `init_best` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 16492 (16492 scored) | 6.81371695706e-05 |
| `init_checks` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 1519 (600 scored) | 6.81371695706e-05 |
| `joint_order` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 48 (15 scored) | 8.15451188675e-05 |
| `late_feedback` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 1511 (1422 scored) | 7.26302449692e-05 |
| `order` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 32 (8 scored) | 6.92210398228e-05 |
| `retime_probe` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 12 (10 scored) | 6.92533893703e-05 |
| `retry_fold` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 1600 (548 scored) | 6.87626783152e-05 |
| `retry_retime` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 1202 (766 scored) | 6.91676609858e-05 |
| `round_shift` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 72 (36 scored) | 6.81912493862e-05 |
| `timing` | completed finite screen or stored feedback prices; exact coverage in RUN_SUMMARY | 317 (312 scored) | 6.87126414358e-05 |
| B/C cell automorphisms | complete induced-grid enumeration; 2 automorphisms, only identity preserves target and clean predicate | 1 valid | base |

Stored witnesses count distinct recorded proposals, including initialization/timing variants and rejected schedules; they are not a count of globally unique networks. The 20 long budgets continued after MC improvements. Brief resource pauses and earlier parser/validated-evaluator-upgrade stops are preserved separately and are not called timeouts or UNSAT. The initialization sweep covers all 16,384 masks on the 88-CX prep. [Measured run summary](RUN_SUMMARY.json), [complete price table](search.csv), [single compressed witness/evidence archive](witnesses.tar.xz).

Mechanisms: changing the clean network and its pivots lowers in-situ pair and cubic loss without delaying the round. In the strongest exact network, 88 prep CX beat the original 82; the network accounts for 1.02979e-6 of the exact gain, and q11/q19 checks add 5.40798e-8. In the first 86-CX prep, deleting either added canceling CX pair raises loss; deleting both gives 6.93103e-5 instead of 6.87732e-5. The measured benefit is real under the judge model; replacing idle channels with less harmful joint gate channels is the inferred mechanism. CX/depth were never ranking objectives.

Negative scope: individual prep timing moves, geometric cell automorphisms and altered B→C check orders did not improve the selected family. Explicit R42–R47 tests found no gain. A sample of 1500 distinct previously infeasible feedback witnesses at R46/R47 had best 7.26302449692e-5. The fixed-order dependency path through the prefix/A encoder requires R45; this is a bound only for that operation order, not a global architectural bound.

Verified: complete Stim stabilizer target; BC2 clean predicate including actual-CX XX faults; emitted native timing and grid adjacency; full judge gates; unmodified exact CLI; official MC and schedule-preserving re-draw signatures; byte identity of the delivery circuit. Fourier decoder moments agree with unaggregated exact arithmetic in the prior validation, and batched decoder tables agree with the original Fourier evaluator within 8e-19 on five circuits (batch_validation.json). MAIN/spec/mc3.py was absent on owl, so the byte-identical lane copy inputs/mc3.py was used.

Inferred or unverified: no global optimum or UNSAT certificate; third-order numbers omit higher orders, while the reported re-draw means sample the full judge noise. Small finalist gaps are not claims of statistical certainty. The earlier BCSYN2 logs were recovered from tom, read in full and archived; their winning circuit appeared after 447 s, without exhaustion evidence. No other lane was edited and no external submission was made.
