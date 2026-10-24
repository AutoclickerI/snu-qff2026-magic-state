# COMP29 — v34m terminal decoder search

**Status: COMPLETE.** All-orders acceptance floor: **0.5005**. Ranking uses the unchanged MAIN sparse evaluator, relocated into this lane so every output stays here.

## Finalists beating v34m

| Stem | All-orders 1−F | Improvement | All-orders acceptance | Judge / measured acceptance | XTIM | MC seed 0 / 1000 / 2000 | MC mean |
|---|---:|---:|---:|---|---|---|---:|
| [g_drop43_ro_00011](g_drop43_ro_00011.qasm) | 4.64922309899e-05 | 0.294029% | 0.500902040093 | PASS / 0.500591 | FAST; 4.02 s/1e6 on tom | 4.582644e-05 / 4.773165e-05 / 4.606009e-05 | 4.653939e-05 |
| [g_ro_00010](g_ro_00010.qasm) | 4.65259850743e-05 | 0.221641% | 0.50080124775 | PASS / 0.500709 | FAST; 3.16 s/1e6 on tom | 4.753164e-05 / 4.753379e-05 / 4.597469e-05 | 4.701338e-05 |
| [g_edge_28_29](g_edge_28_29.qasm) | 4.65955808208e-05 | 0.0723879% | 0.500799569273 | PASS / 0.500704 | FAST; 2.62 s/1e6 on jerry | 4.753182e-05 / 4.760386e-05 / 4.615452e-05 | 4.709673e-05 |

Delivery: [best.qasm](best.qasm) / [best.json](best.json) = **g_drop43_ro_00011**.

## Baseline and scope

Frozen v34m (`g_base`): **4.66293348172e-05**, acceptance **0.501200443653**, 207 CX, native depth 48. This was independently reproduced by the sparse evaluator. The baseline’s inherited JSON includes older A-only counts; all new candidate metadata uses its actual emitted circuit counts and no inherited verification verdicts.

B geometric obstruction: retaining its three X-check rows requires a new B Z flag to have B support in the orthogonal code. Every nonzero such support spans at least five grid edges, even if every grid cell can be a helper. A new terminal single-qubit flag pulled back through at most three nearest-neighbor CXs cannot have that support. `v34_B_geometry_certificate.json` records all 15 nonzero codewords. This excludes the terminal 1–3-CX form, not earlier instruments or rewrites that borrow existing gates.

The complete connected search on the 21 existing terminal readout cells covered 44 one-CX, 268 two-CX and 2,364 three-CX networks. Twelve expose an independent A flag; none exposes a B flag. C’s current detector restrictions span all seven Z readouts, so their re-encoding can change noisy rejection but adds no independent ideal Z information. Every old detector row is conjugated through each decoder and re-expressed; a proposed extra flag is added only on a column absent from every retained row. The sparse frontend checks noiseless determinism and ideal loss before evaluating all 73 moments.

The alternative B/C endpoint search commutes or reverses the existing Bell readout so its parity check can occur after B→data. Retiming fixes the prefix through t40 and preserves native wire precedence inside depth 48. Variants also test removal of the two existing readout edges with exact detector repair. Infeasible schedules and blocked CX cancellations have explicit build-error receipts.

Removing the intermediate q16 Z check at t28 (c43) preserves the first checked projection at t27 (c270) and the final one at t30 (c266). Between them q16 has no interaction with another qubit. Its intervening noise is therefore an independent scalar acceptance factor; the final post-measurement state and conditional data state are unchanged. The exact predicted acceptance multiplier is **1.0010018919641532**. Four independent all-orders runs reproduce that multiplier and preserve loss within 2.3e-16 (`v34_drop43_validation.json`). This recovers about 0.000502 acceptance without claiming a fidelity gain. It pays for both useful readout edges, whose joint score is evaluated directly.

The best delivery is v34m + CX14→15 and CX28→29 at t46, their Z readouts at t47 with detector-row repair, and removal of c43 with c266’s parity simplified. It has **209 CX, native depth 48**, and 66 detectors. The full 243-case product of five readout-edge choices covers keeping/removing/reversing the existing edges and both orientations of each added edge. The unscreened joint winner originally had acceptance 0.50040069; removing c43 raises it above the requested floor.

Longer B logical-Z decoders were also built for the B6/B13/B26 representative, including cancellation against existing gates. Their ideal checks pass, but even the best tested longer decoder has loss about 3.62e-4 and acceptance below 0.5. The delayed B/C endpoint checks also worsen loss. The reversed final blue Bell readout reproduces the baseline exactly. Seven echo-readout helper copies, acceptance-recovery variants, and combinations with the leading readout pair are fully priced; none provides a better eligible result.

Independent model audit on v34m, the A14→A15 finalist and the combined delivery matches every categorical noise-channel signature, rotation axis and decoder observable against the actual judge-based EVAL model. Thirty-two quantum-table cross-checks per circuit have zero discrepancy. The unchanged sparse evaluator’s source hashes are recorded in `v34_evaluator_hashes.json`; its cutoff omission bound for the winner is 1.24e-14, excluding ordinary floating-point roundoff. The all-orders difference between finalists is much smaller than single-seed Monte Carlo noise, so the specified all-orders ranking decides.

Receipts: 374 built candidate stems; 374 complete all-orders prices; 22 prices reuse a byte-identical QASM receipt. Build failures are retained separately. Preliminary endpoint-scheduling errors used an overbroad repeated-gate selector; the occurrence-specific builder in v34_bell2 corrects it, and those earlier infeasibility messages are not used as exclusions.

## Candidate prices

| Stem | Edits | CX | All-orders 1−F | All-orders acceptance | Judge | Speed | MC mean |
|---|---|---:|---:|---:|---|---|---:|
| `g_combo_echo_264` | ["best terminal readout pair + middle-check removal", "echo copy", {"bit": 264, "helper": 17}] | 210 | 4.64920399885e-05 | 0.499500390208 | not a finalist | — | — |
| `g_combo_echo_265` | ["best terminal readout pair + middle-check removal", "echo copy", {"bit": 265, "helper": 12}] | 210 | 4.64920721263e-05 | 0.499501253582 | not a finalist | — | — |
| `g_combo_echo_272` | ["best terminal readout pair + middle-check removal", "echo copy", {"bit": 272, "helper": 27}] | 210 | 4.64921186247e-05 | 0.49983285602 | not a finalist | — | — |
| `g_combo_echo_269` | ["best terminal readout pair + middle-check removal", "echo copy", {"bit": 269, "helper": 32}] | 210 | 4.64922217128e-05 | 0.499500263223 | not a finalist | — | — |
| `g_combo_echo_270` | ["best terminal readout pair + middle-check removal", "echo copy", {"bit": 270, "helper": 17}] | 210 | 4.64922288817e-05 | 0.499833328691 | not a finalist | — | — |
| `g_drop43_ro_00011` | ["g_ro_00011", "remove scalar-only intermediate q16 check c43"] | 209 | 4.64922309899e-05 | 0.500902040093 | PASS | FAST | 4.653939e-05 |
| `g_ro_00011` | [["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.64922309901e-05 | 0.50040069266 | not a finalist | — | — |
| `g_combo_echo_268` | ["best terminal readout pair + middle-check removal", "echo copy", {"bit": 268, "helper": 18}] | 210 | 4.65193685677e-05 | 0.499998276261 | not a finalist | — | — |
| `g_ro_00010` | [["add", [14, 15]]] | 208 | 4.65259850743e-05 | 0.50080124775 | PASS | FAST | 4.701338e-05 |
| `g_drop43_ro_00010` | ["g_ro_00010", "remove scalar-only intermediate q16 check c43"] | 208 | 4.65259850745e-05 | 0.501302996496 | not a finalist | — | — |
| `g_combo_echo_271` | ["best terminal readout pair + middle-check removal", "echo copy", {"bit": 271, "helper": 11}] | 210 | 4.65618019167e-05 | 0.499997306757 | not a finalist | — | — |
| `g_ro_00111` | [["add", [1, 2]], ["add", [14, 15]], ["add", [28, 29]]] | 210 | 4.65712571225e-05 | 0.500004600804 | not a finalist | — | — |
| `g_ro_00211` | [["add", [2, 1]], ["add", [14, 15]], ["add", [28, 29]]] | 210 | 4.65730411539e-05 | 0.500005294152 | not a finalist | — | — |
| `g_drop43_ro_00001` | ["g_ro_00001", "remove scalar-only intermediate q16 check c43"] | 208 | 4.65955808206e-05 | 0.501301316337 | not a finalist | — | — |
| `g_edge_28_29` | ["terminal readout encoding", [[28, 29]]] | 208 | 4.65955808208e-05 | 0.500799569273 | PASS | FAST | 4.709673e-05 |
| `g_ro_00001` | [["add", [28, 29]]] | 208 | 4.65955808208e-05 | 0.500799569273 | not a finalist | — | — |
| `g_ro_00110` | [["add", [1, 2]], ["add", [14, 15]]] | 209 | 4.66050092151e-05 | 0.500404838834 | not a finalist | — | — |
| `g_ro_00210` | [["add", [2, 1]], ["add", [14, 15]]] | 209 | 4.66067921497e-05 | 0.500405532737 | not a finalist | — | — |
| `g_echoD_0_264` | ["remove intermediate c43", "echo copy", {"bit": 264, "helper": 17, "removed_edges": []}] | 208 | 4.66291447813e-05 | 0.50029870232 | not a finalist | — | — |
| `g_echo_0_264` | ["echo readout copy", {"bit": 264, "helper": 17, "remove_edges": []}] | 208 | 4.66291447813e-05 | 0.499797958761 | not a finalist | — | — |
| `g_echoD_0_265` | ["remove intermediate c43", "echo copy", {"bit": 265, "helper": 12, "removed_edges": []}] | 208 | 4.66291579934e-05 | 0.500299567054 | not a finalist | — | — |
| `g_echo_0_265` | ["echo readout copy", {"bit": 265, "helper": 12, "remove_edges": []}] | 208 | 4.66291579935e-05 | 0.49979882263 | not a finalist | — | — |
| `g_echo_0_272` | ["echo readout copy", {"bit": 272, "helper": 27, "remove_edges": []}] | 208 | 4.66292233905e-05 | 0.500130622633 | not a finalist | — | — |
| `g_echoD_0_272` | ["remove intermediate c43", "echo copy", {"bit": 272, "helper": 27, "removed_edges": []}] | 208 | 4.66292233907e-05 | 0.500631699485 | not a finalist | — | — |
| `g_echo_0_269` | ["echo readout copy", {"bit": 269, "helper": 32, "remove_edges": []}] | 208 | 4.66293255253e-05 | 0.499797831693 | not a finalist | — | — |
| `g_echoD_0_269` | ["remove intermediate c43", "echo copy", {"bit": 269, "helper": 32, "removed_edges": []}] | 208 | 4.66293255253e-05 | 0.500298575124 | not a finalist | — | — |
| `g_echo_0_270` | ["echo readout copy", {"bit": 270, "helper": 17, "remove_edges": []}] | 208 | 4.66293327166e-05 | 0.50013131816 | not a finalist | — | — |
| `g_echoD_0_270` | ["remove intermediate c43", "echo copy", {"bit": 270, "helper": 17, "removed_edges": []}] | 208 | 4.66293327168e-05 | 0.50063217291 | not a finalist | — | — |
| `g_blue_reverse` | ["reverse the final blue Bell-readout orientation, retain XX/ZZ record meaning"] | 207 | 4.66293348172e-05 | 0.501200443653 | not a finalist | — | — |
| `g_ro_00000` | [] | 207 | 4.66293348172e-05 | 0.501200443653 | not a finalist | — | — |
| `g_drop43_base` | ["g_base", "remove scalar-only intermediate q16 check c43"] | 207 | 4.66293348174e-05 | 0.50170259235 | not a finalist | — | — |
| `g_ro_00012` | [["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.66542887806e-05 | 0.500400447718 | not a finalist | — | — |
| `g_echoD_0_268` | ["remove intermediate c43", "echo copy", {"bit": 268, "helper": 18, "removed_edges": []}] | 208 | 4.66565872628e-05 | 0.500797443745 | not a finalist | — | — |
| `g_echo_0_268` | ["echo readout copy", {"bit": 268, "helper": 18, "remove_edges": []}] | 208 | 4.66565872629e-05 | 0.500296201001 | not a finalist | — | — |
| `g_ro_10011` | [["remove", [19, 25]], ["add", [14, 15]], ["add", [28, 29]]] | 208 | 4.66603551805e-05 | 0.500800353647 | not a finalist | — | — |
| `g_ro_00101` | [["add", [1, 2]], ["add", [28, 29]]] | 209 | 4.66746204114e-05 | 0.500402992757 | not a finalist | — | — |
| `g_ro_00201` | [["add", [2, 1]], ["add", [28, 29]]] | 209 | 4.66763469476e-05 | 0.500404315477 | not a finalist | — | — |
| `g_ro_10010` | [["remove", [19, 25]], ["add", [14, 15]]] | 207 | 4.66940335062e-05 | 0.501201228574 | not a finalist | — | — |
| `g_echo_0_271` | ["echo readout copy", {"bit": 271, "helper": 11, "remove_edges": []}] | 208 | 4.66985498554e-05 | 0.500295170798 | not a finalist | — | — |
| `g_echoD_0_271` | ["remove intermediate c43", "echo copy", {"bit": 271, "helper": 11, "removed_edges": []}] | 208 | 4.66985498554e-05 | 0.50079641251 | not a finalist | — | — |
| `g_ro_00021` | [["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.66989489502e-05 | 0.500403113612 | not a finalist | — | — |
| `g_ro_00100` | [["add", [1, 2]]] | 208 | 4.67083724145e-05 | 0.500803549689 | not a finalist | — | — |
| `g_ro_00200` | [["add", [2, 1]]] | 208 | 4.67100978566e-05 | 0.500804873468 | not a finalist | — | — |
| `g_ro_20011` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.67291394505e-05 | 0.500401129716 | not a finalist | — | — |
| `g_ro_00020` | [["add", [15, 14]]] | 208 | 4.67327049727e-05 | 0.500803670641 | not a finalist | — | — |
| `g_ro_00112` | [["add", [1, 2]], ["add", [14, 15]], ["add", [29, 28]]] | 210 | 4.6733307375e-05 | 0.500004356053 | not a finalist | — | — |
| `g_ro_00212` | [["add", [2, 1]], ["add", [14, 15]], ["add", [29, 28]]] | 210 | 4.67350901849e-05 | 0.500005049401 | not a finalist | — | — |
| `g_ro_10111` | [["remove", [19, 25]], ["add", [1, 2]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.67393742585e-05 | 0.50040394544 | not a finalist | — | — |
| `g_ro_10211` | [["remove", [19, 25]], ["add", [2, 1]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.67411632943e-05 | 0.500404639341 | not a finalist | — | — |
| `g_edge_29_28` | ["terminal readout encoding", [[29, 28]]] | 208 | 4.67576390316e-05 | 0.500799324137 | not a finalist | — | — |
| `g_ro_00002` | [["add", [29, 28]]] | 208 | 4.67576390316e-05 | 0.500799324137 | not a finalist | — | — |
| `g_ro_20010` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [14, 15]]] | 208 | 4.67628926319e-05 | 0.500801685367 | not a finalist | — | — |
| `g_ro_10001` | [["remove", [19, 25]], ["add", [28, 29]]] | 207 | 4.67637060378e-05 | 0.501199548834 | not a finalist | — | — |
| `g_ro_10110` | [["remove", [19, 25]], ["add", [1, 2]], ["add", [14, 15]]] | 208 | 4.67730505918e-05 | 0.500804503054 | not a finalist | — | — |
| `g_ro_10210` | [["remove", [19, 25]], ["add", [2, 1]], ["add", [14, 15]]] | 208 | 4.6774838532e-05 | 0.500805197511 | not a finalist | — | — |
| `g_ro_00121` | [["add", [1, 2]], ["add", [15, 14]], ["add", [28, 29]]] | 210 | 4.67779627314e-05 | 0.500007022144 | not a finalist | — | — |
| `g_ro_00221` | [["add", [2, 1]], ["add", [15, 14]], ["add", [28, 29]]] | 210 | 4.67799308827e-05 | 0.500007716429 | not a finalist | — | — |
| `g_echo_1_264` | ["echo readout copy", {"bit": 264, "helper": 17, "remove_edges": [[19, 25]]}] | 207 | 4.67971942421e-05 | 0.500197138275 | not a finalist | — | — |
| `g_echoD_1_264` | ["remove intermediate c43", "echo copy", {"bit": 264, "helper": 17, "removed_edges": [[19, 25]]}] | 207 | 4.67971942422e-05 | 0.500698281768 | not a finalist | — | — |
| `g_echoD_1_265` | ["remove intermediate c43", "echo copy", {"bit": 265, "helper": 12, "removed_edges": [[19, 25]]}] | 207 | 4.67972074537e-05 | 0.500699147193 | not a finalist | — | — |
| `g_echo_1_265` | ["echo readout copy", {"bit": 265, "helper": 12, "remove_edges": [[19, 25]]}] | 207 | 4.67972074537e-05 | 0.500198002833 | not a finalist | — | — |
| `g_echo_1_272` | ["echo readout copy", {"bit": 272, "helper": 27, "remove_edges": [[19, 25]]}] | 207 | 4.67972728523e-05 | 0.500530067839 | not a finalist | — | — |
| `g_echoD_1_272` | ["remove intermediate c43", "echo copy", {"bit": 272, "helper": 27, "removed_edges": [[19, 25]]}] | 207 | 4.67972728525e-05 | 0.501031544892 | not a finalist | — | — |
| `g_echo_1_269` | ["echo readout copy", {"bit": 269, "helper": 32, "remove_edges": [[19, 25]]}] | 207 | 4.67973749833e-05 | 0.500197011105 | not a finalist | — | — |
| `g_echoD_1_269` | ["remove intermediate c43", "echo copy", {"bit": 269, "helper": 32, "removed_edges": [[19, 25]]}] | 207 | 4.67973749836e-05 | 0.50069815447 | not a finalist | — | — |
| `g_echo_1_270` | ["echo readout copy", {"bit": 270, "helper": 17, "remove_edges": [[19, 25]]}] | 207 | 4.67973821761e-05 | 0.500530763922 | not a finalist | — | — |
| `g_echoD_1_270` | ["remove intermediate c43", "echo copy", {"bit": 270, "helper": 17, "removed_edges": [[19, 25]]}] | 207 | 4.67973821765e-05 | 0.501032018695 | not a finalist | — | — |
| `g_remove_1` | ["remove readout edges", [[19, 25]]] | 206 | 4.67973842768e-05 | 0.501600743305 | not a finalist | — | — |
| `g_ro_10000` | [["remove", [19, 25]]] | 206 | 4.67973842768e-05 | 0.501600743305 | not a finalist | — | — |
| `g_ro_20111` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [1, 2]], ["add", [14, 15]], ["add", [28, 29]]] | 210 | 4.68081656273e-05 | 0.500005037514 | not a finalist | — | — |
| `g_ro_20211` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [2, 1]], ["add", [14, 15]], ["add", [28, 29]]] | 210 | 4.68099497448e-05 | 0.500005730863 | not a finalist | — | — |
| `g_ro_00120` | [["add", [1, 2]], ["add", [15, 14]]] | 209 | 4.68117167631e-05 | 0.500407262114 | not a finalist | — | — |
| `g_ro_00220` | [["add", [2, 1]], ["add", [15, 14]]] | 209 | 4.68136838193e-05 | 0.500407956954 | not a finalist | — | — |
| `g_ro_10012` | [["remove", [19, 25]], ["add", [14, 15]], ["add", [29, 28]]] | 208 | 4.68223092503e-05 | 0.500800108403 | not a finalist | — | — |
| `g_echo_1_268` | ["echo readout copy", {"bit": 268, "helper": 18, "remove_edges": [[19, 25]]}] | 207 | 4.68246364978e-05 | 0.500695778451 | not a finalist | — | — |
| `g_echoD_1_268` | ["remove intermediate c43", "echo copy", {"bit": 268, "helper": 18, "removed_edges": [[19, 25]]}] | 207 | 4.6824636498e-05 | 0.501197421528 | not a finalist | — | — |
| `g_ro_20001` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [28, 29]]] | 208 | 4.68324916933e-05 | 0.500800006677 | not a finalist | — | — |
| `g_ro_00102` | [["add", [1, 2]], ["add", [29, 28]]] | 209 | 4.68366710826e-05 | 0.500402747814 | not a finalist | — | — |
| `g_ro_00202` | [["add", [2, 1]], ["add", [29, 28]]] | 209 | 4.68383964044e-05 | 0.500404070533 | not a finalist | — | — |
| `g_ro_20110` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [1, 2]], ["add", [14, 15]]] | 209 | 4.68419168164e-05 | 0.500405276104 | not a finalist | — | — |
| `g_ro_10101` | [["remove", [19, 25]], ["add", [1, 2]], ["add", [28, 29]]] | 208 | 4.68427385678e-05 | 0.50080265558 | not a finalist | — | — |
| `g_ro_20210` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [2, 1]], ["add", [14, 15]]] | 209 | 4.68436998382e-05 | 0.500405970008 | not a finalist | — | — |
| `g_ro_10201` | [["remove", [19, 25]], ["add", [2, 1]], ["add", [28, 29]]] | 208 | 4.68444701107e-05 | 0.500803979355 | not a finalist | — | — |
| `g_ro_00022` | [["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.68610035117e-05 | 0.500402868669 | not a finalist | — | — |
| `g_ro_20000` | [["remove", [19, 25]], ["add", [25, 19]]] | 207 | 4.68662447856e-05 | 0.501200881618 | not a finalist | — | — |
| `g_echo_1_271` | ["echo readout copy", {"bit": 271, "helper": 11, "remove_edges": [[19, 25]]}] | 207 | 4.68665987761e-05 | 0.500694747426 | not a finalist | — | — |
| `g_echoD_1_271` | ["remove intermediate c43", "echo copy", {"bit": 271, "helper": 11, "removed_edges": [[19, 25]]}] | 207 | 4.68665987762e-05 | 0.50119638947 | not a finalist | — | — |
| `g_ro_10021` | [["remove", [19, 25]], ["add", [15, 14]], ["add", [28, 29]]] | 208 | 4.68670699771e-05 | 0.50080277653 | not a finalist | — | — |
| `g_ro_10100` | [["remove", [19, 25]], ["add", [1, 2]]] | 207 | 4.6876414813e-05 | 0.50120353235 | not a finalist | — | — |
| `g_ro_10200` | [["remove", [19, 25]], ["add", [2, 1]]] | 207 | 4.68781452629e-05 | 0.501204857185 | not a finalist | — | — |
| `g_ro_20012` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.6891194369e-05 | 0.50040088477 | not a finalist | — | — |
| `g_ro_10020` | [["remove", [19, 25]], ["add", [15, 14]]] | 207 | 4.69007502411e-05 | 0.501203653397 | not a finalist | — | — |
| `g_ro_10112` | [["remove", [19, 25]], ["add", [1, 2]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.690132079e-05 | 0.500403700388 | not a finalist | — | — |
| `g_ro_10212` | [["remove", [19, 25]], ["add", [2, 1]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.69031086057e-05 | 0.500404394289 | not a finalist | — | — |
| `g_ro_20101` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [1, 2]], ["add", [28, 29]]] | 209 | 4.69115313295e-05 | 0.500403429815 | not a finalist | — | — |
| `g_ro_20201` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [2, 1]], ["add", [28, 29]]] | 209 | 4.69132579517e-05 | 0.500404752536 | not a finalist | — | — |
| `g_ro_10002` | [["remove", [19, 25]], ["add", [29, 28]]] | 207 | 4.69256605291e-05 | 0.501199303396 | not a finalist | — | — |
| `g_ro_20021` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.69358605016e-05 | 0.500403550669 | not a finalist | — | — |
| `g_ro_00122` | [["add", [1, 2]], ["add", [15, 14]], ["add", [29, 28]]] | 210 | 4.69400097562e-05 | 0.500006777393 | not a finalist | — | — |
| `g_ro_00222` | [["add", [2, 1]], ["add", [15, 14]], ["add", [29, 28]]] | 210 | 4.69419766826e-05 | 0.500007471678 | not a finalist | — | — |
| `g_ro_20100` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [1, 2]]] | 208 | 4.69452824289e-05 | 0.500803987308 | not a finalist | — | — |
| `g_ro_10121` | [["remove", [19, 25]], ["add", [1, 2]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.69460767074e-05 | 0.500406368711 | not a finalist | — | — |
| `g_ro_20200` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [2, 1]]] | 208 | 4.69470079577e-05 | 0.500805311087 | not a finalist | — | — |
| `g_ro_10221` | [["remove", [19, 25]], ["add", [2, 1]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.69480498589e-05 | 0.50040706355 | not a finalist | — | — |
| `g_ro_20020` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [15, 14]]] | 208 | 4.69696156203e-05 | 0.500804108259 | not a finalist | — | — |
| `g_ro_20112` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [1, 2]], ["add", [14, 15]], ["add", [29, 28]]] | 210 | 4.69702130072e-05 | 0.50000479276 | not a finalist | — | — |
| `g_ro_20212` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [2, 1]], ["add", [14, 15]], ["add", [29, 28]]] | 210 | 4.6971995904e-05 | 0.500005486109 | not a finalist | — | — |
| `g_ro_10120` | [["remove", [19, 25]], ["add", [1, 2]], ["add", [15, 14]]] | 208 | 4.69797549801e-05 | 0.500806928266 | not a finalist | — | — |
| `g_ro_10220` | [["remove", [19, 25]], ["add", [2, 1]], ["add", [15, 14]]] | 208 | 4.69817270369e-05 | 0.500807623661 | not a finalist | — | — |
| `g_ro_20002` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [29, 28]]] | 208 | 4.6994547033e-05 | 0.500799761538 | not a finalist | — | — |
| `g_ro_10102` | [["remove", [19, 25]], ["add", [1, 2]], ["add", [29, 28]]] | 208 | 4.7004685519e-05 | 0.500802410334 | not a finalist | — | — |
| `g_ro_10202` | [["remove", [19, 25]], ["add", [2, 1]], ["add", [29, 28]]] | 208 | 4.70064158488e-05 | 0.500803734109 | not a finalist | — | — |
| `g_ro_20121` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [1, 2]], ["add", [15, 14]], ["add", [28, 29]]] | 210 | 4.7014874329e-05 | 0.500007458856 | not a finalist | — | — |
| `g_ro_20221` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [2, 1]], ["add", [15, 14]], ["add", [28, 29]]] | 210 | 4.70168425682e-05 | 0.500008153141 | not a finalist | — | — |
| `g_ro_10022` | [["remove", [19, 25]], ["add", [15, 14]], ["add", [29, 28]]] | 208 | 4.70290208178e-05 | 0.500802531285 | not a finalist | — | — |
| `g_ro_20120` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [1, 2]], ["add", [15, 14]]] | 209 | 4.70486274571e-05 | 0.500407699385 | not a finalist | — | — |
| `g_ro_20220` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [2, 1]], ["add", [15, 14]]] | 209 | 4.70505946012e-05 | 0.500408394227 | not a finalist | — | — |
| `g_ro_20102` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [1, 2]], ["add", [29, 28]]] | 209 | 4.70735791288e-05 | 0.500403184868 | not a finalist | — | — |
| `g_ro_20202` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [2, 1]], ["add", [29, 28]]] | 209 | 4.70753045372e-05 | 0.500404507589 | not a finalist | — | — |
| `g_ro_20022` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.7097912191e-05 | 0.500403305723 | not a finalist | — | — |
| `g_ro_10122` | [["remove", [19, 25]], ["add", [1, 2]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.71080200111e-05 | 0.500406123659 | not a finalist | — | — |
| `g_ro_10222` | [["remove", [19, 25]], ["add", [2, 1]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.71099919385e-05 | 0.500406818497 | not a finalist | — | — |
| `g_ro_01011` | [["remove", [17, 16]], ["add", [14, 15]], ["add", [28, 29]]] | 208 | 4.71535588904e-05 | 0.500801759645 | not a finalist | — | — |
| `g_ro_20122` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [1, 2]], ["add", [15, 14]], ["add", [29, 28]]] | 210 | 4.71769184811e-05 | 0.500007214101 | not a finalist | — | — |
| `g_ro_20222` | [["remove", [19, 25]], ["add", [25, 19]], ["add", [2, 1]], ["add", [15, 14]], ["add", [29, 28]]] | 210 | 4.71788854958e-05 | 0.500007908387 | not a finalist | — | — |
| `g_ro_01010` | [["remove", [17, 16]], ["add", [14, 15]]] | 207 | 4.71874128616e-05 | 0.501202635616 | not a finalist | — | — |
| `g_ro_01111` | [["remove", [17, 16]], ["add", [1, 2]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.72324818376e-05 | 0.500405349129 | not a finalist | — | — |
| `g_ro_01211` | [["remove", [17, 16]], ["add", [2, 1]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.72342752488e-05 | 0.500406043249 | not a finalist | — | — |
| `g_ro_01001` | [["remove", [17, 16]], ["add", [28, 29]]] | 207 | 4.72569244314e-05 | 0.501200956356 | not a finalist | — | — |
| `g_ro_01110` | [["remove", [17, 16]], ["add", [1, 2]], ["add", [14, 15]]] | 208 | 4.72663338209e-05 | 0.500805907785 | not a finalist | — | — |
| `g_ro_01210` | [["remove", [17, 16]], ["add", [2, 1]], ["add", [14, 15]]] | 208 | 4.72681261361e-05 | 0.500806602462 | not a finalist | — | — |
| `g_echoD_2_264` | ["remove intermediate c43", "echo copy", {"bit": 264, "helper": 17, "removed_edges": [[17, 16]]}] | 207 | 4.72905887218e-05 | 0.500699687802 | not a finalist | — | — |
| `g_echo_2_264` | ["echo readout copy", {"bit": 264, "helper": 17, "remove_edges": [[17, 16]]}] | 207 | 4.7290588722e-05 | 0.500198542901 | not a finalist | — | — |
| `g_echo_2_265` | ["echo readout copy", {"bit": 265, "helper": 12, "remove_edges": [[17, 16]]}] | 207 | 4.72906015201e-05 | 0.500199407461 | not a finalist | — | — |
| `g_echoD_2_265` | ["remove intermediate c43", "echo copy", {"bit": 265, "helper": 12, "removed_edges": [[17, 16]]}] | 207 | 4.72906015201e-05 | 0.500700553228 | not a finalist | — | — |
| `g_echoD_2_272` | ["remove intermediate c43", "echo copy", {"bit": 272, "helper": 27, "removed_edges": [[17, 16]]}] | 207 | 4.72906686507e-05 | 0.50103295196 | not a finalist | — | — |
| `g_echo_2_272` | ["echo readout copy", {"bit": 272, "helper": 27, "remove_edges": [[17, 16]]}] | 207 | 4.72906686509e-05 | 0.500531473499 | not a finalist | — | — |
| `g_echo_2_269` | ["echo readout copy", {"bit": 269, "helper": 32, "remove_edges": [[17, 16]]}] | 207 | 4.72907690386e-05 | 0.50019841573 | not a finalist | — | — |
| `g_echoD_2_269` | ["remove intermediate c43", "echo copy", {"bit": 269, "helper": 32, "removed_edges": [[17, 16]]}] | 207 | 4.72907690389e-05 | 0.500699560503 | not a finalist | — | — |
| `g_echo_2_270` | ["echo readout copy", {"bit": 270, "helper": 17, "remove_edges": [[17, 16]]}] | 207 | 4.72907762192e-05 | 0.500532169485 | not a finalist | — | — |
| `g_echoD_2_270` | ["remove intermediate c43", "echo copy", {"bit": 270, "helper": 17, "removed_edges": [[17, 16]]}] | 207 | 4.72907762194e-05 | 0.501033425666 | not a finalist | — | — |
| `g_remove_2` | ["remove readout edges", [[17, 16]]] | 206 | 4.72907783161e-05 | 0.501602151873 | not a finalist | — | — |
| `g_ro_01000` | [["remove", [17, 16]]] | 206 | 4.72907783161e-05 | 0.501602151873 | not a finalist | — | — |
| `g_ro_01012` | [["remove", [17, 16]], ["add", [14, 15]], ["add", [29, 28]]] | 208 | 4.73154465726e-05 | 0.500801514066 | not a finalist | — | — |
| `g_echoD_2_268` | ["remove intermediate c43", "echo copy", {"bit": 268, "helper": 18, "removed_edges": [[17, 16]]}] | 207 | 4.73179012055e-05 | 0.501198828748 | not a finalist | — | — |
| `g_echo_2_268` | ["echo readout copy", {"bit": 268, "helper": 18, "remove_edges": [[17, 16]]}] | 207 | 4.73179012056e-05 | 0.500697184263 | not a finalist | — | — |
| `g_ro_11011` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [14, 15]], ["add", [28, 29]]] | 207 | 4.73217356763e-05 | 0.50120174101 | not a finalist | — | — |
| `g_ro_01101` | [["remove", [17, 16]], ["add", [1, 2]], ["add", [28, 29]]] | 208 | 4.73358594465e-05 | 0.500804060637 | not a finalist | — | — |
| `g_ro_01201` | [["remove", [17, 16]], ["add", [2, 1]], ["add", [28, 29]]] | 208 | 4.73375957893e-05 | 0.500805384671 | not a finalist | — | — |
| `g_ro_11010` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [14, 15]]] | 206 | 4.73555138904e-05 | 0.501602937074 | not a finalist | — | — |
| `g_ro_02011` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.73577123178e-05 | 0.500399240414 | not a finalist | — | — |
| `g_echoD_2_271` | ["remove intermediate c43", "echo copy", {"bit": 271, "helper": 11, "removed_edges": [[17, 16]]}] | 207 | 4.73598309325e-05 | 0.501197796695 | not a finalist | — | — |
| `g_echo_2_271` | ["echo readout copy", {"bit": 271, "helper": 11, "remove_edges": [[17, 16]]}] | 207 | 4.73598309326e-05 | 0.500696153243 | not a finalist | — | — |
| `g_ro_01021` | [["remove", [17, 16]], ["add", [15, 14]], ["add", [28, 29]]] | 208 | 4.73602815367e-05 | 0.50080418247 | not a finalist | — | — |
| `g_ro_01100` | [["remove", [17, 16]], ["add", [1, 2]]] | 207 | 4.73697113413e-05 | 0.501204938451 | not a finalist | — | — |
| `g_ro_01200` | [["remove", [17, 16]], ["add", [2, 1]]] | 207 | 4.73714465908e-05 | 0.501206263546 | not a finalist | — | — |
| `g_ro_21011` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [14, 15]], ["add", [28, 29]]] | 208 | 4.73905398791e-05 | 0.500802197124 | not a finalist | — | — |
| `g_ro_02010` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [14, 15]]] | 208 | 4.73916021982e-05 | 0.50079979412 | not a finalist | — | — |
| `g_ro_01020` | [["remove", [17, 16]], ["add", [15, 14]]] | 207 | 4.73941374448e-05 | 0.501205060382 | not a finalist | — | — |
| `g_ro_01112` | [["remove", [17, 16]], ["add", [1, 2]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.73943619923e-05 | 0.500405103742 | not a finalist | — | — |
| `g_ro_01212` | [["remove", [17, 16]], ["add", [2, 1]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.73961541839e-05 | 0.500405797863 | not a finalist | — | — |
| `g_ro_11111` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [14, 15]], ["add", [28, 29]]] | 208 | 4.74006515711e-05 | 0.500805013888 | not a finalist | — | — |
| `g_ro_11211` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [14, 15]], ["add", [28, 29]]] | 208 | 4.74024499854e-05 | 0.500805708562 | not a finalist | — | — |
| `g_ro_01002` | [["remove", [17, 16]], ["add", [29, 28]]] | 207 | 4.74188125348e-05 | 0.501200710583 | not a finalist | — | — |
| `g_ro_21010` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [14, 15]]] | 207 | 4.74243929472e-05 | 0.501203073657 | not a finalist | — | — |
| `g_ro_11001` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [28, 29]]] | 206 | 4.7425102243e-05 | 0.50160125655 | not a finalist | — | — |
| `g_ro_11110` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [14, 15]]] | 207 | 4.74344277966e-05 | 0.501205892384 | not a finalist | — | — |
| `g_ro_11210` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [14, 15]]] | 207 | 4.74362251156e-05 | 0.501206587615 | not a finalist | — | — |
| `g_ro_02111` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [14, 15]], ["add", [28, 29]]] | 210 | 4.74364276436e-05 | 0.500003145352 | not a finalist | — | — |
| `g_ro_02211` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [14, 15]], ["add", [28, 29]]] | 210 | 4.74382199381e-05 | 0.500003839493 | not a finalist | — | — |
| `g_ro_01121` | [["remove", [17, 16]], ["add", [1, 2]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.74391897833e-05 | 0.500407772072 | not a finalist | — | — |
| `g_ro_01221` | [["remove", [17, 16]], ["add", [2, 1]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.7441168492e-05 | 0.500408467265 | not a finalist | — | — |
| `g_echo_3_264` | ["echo readout copy", {"bit": 264, "helper": 17, "remove_edges": [[19, 25], [17, 16]]}] | 206 | 4.74586907783e-05 | 0.500598042407 | not a finalist | — | — |
| `g_echoD_3_264` | ["remove intermediate c43", "echo copy", {"bit": 264, "helper": 17, "removed_edges": [[19, 25], [17, 16]]}] | 206 | 4.74586907783e-05 | 0.501099587563 | not a finalist | — | — |
| `g_echoD_3_265` | ["remove intermediate c43", "echo copy", {"bit": 265, "helper": 12, "removed_edges": [[19, 25], [17, 16]]}] | 206 | 4.74587035755e-05 | 0.501100453681 | not a finalist | — | — |
| `g_echo_3_265` | ["echo readout copy", {"bit": 265, "helper": 12, "remove_edges": [[19, 25], [17, 16]]}] | 206 | 4.74587035756e-05 | 0.500598907658 | not a finalist | — | — |
| `g_echoD_3_272` | ["remove intermediate c43", "echo copy", {"bit": 272, "helper": 27, "removed_edges": [[19, 25], [17, 16]]}] | 206 | 4.74587707074e-05 | 0.501433117893 | not a finalist | — | — |
| `g_echo_3_272` | ["echo readout copy", {"bit": 272, "helper": 27, "remove_edges": [[19, 25], [17, 16]]}] | 206 | 4.74587707074e-05 | 0.50093123891 | not a finalist | — | — |
| `g_echo_3_269` | ["echo readout copy", {"bit": 269, "helper": 32, "remove_edges": [[19, 25], [17, 16]]}] | 206 | 4.7458871092e-05 | 0.500597915134 | not a finalist | — | — |
| `g_echoD_3_269` | ["remove intermediate c43", "echo copy", {"bit": 269, "helper": 32, "removed_edges": [[19, 25], [17, 16]]}] | 206 | 4.74588710923e-05 | 0.501099460163 | not a finalist | — | — |
| `g_echoD_3_270` | ["remove intermediate c43", "echo copy", {"bit": 270, "helper": 17, "removed_edges": [[19, 25], [17, 16]]}] | 206 | 4.74588782742e-05 | 0.501433591977 | not a finalist | — | — |
| `g_echo_3_270` | ["echo readout copy", {"bit": 270, "helper": 17, "remove_edges": [[19, 25], [17, 16]]}] | 206 | 4.74588782742e-05 | 0.500931935452 | not a finalist | — | — |
| `g_remove_3` | ["remove readout edges", [[19, 25], [17, 16]]] | 205 | 4.74588803707e-05 | 0.502002772416 | not a finalist | — | — |
| `g_ro_11000` | [["remove", [19, 25]], ["remove", [17, 16]]] | 205 | 4.74588803707e-05 | 0.502002772416 | not a finalist | — | — |
| `g_ro_02001` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [28, 29]]] | 208 | 4.74610919406e-05 | 0.500798117348 | not a finalist | — | — |
| `g_ro_21111` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.74694628699e-05 | 0.500405786261 | not a finalist | — | — |
| `g_ro_02110` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [14, 15]]] | 209 | 4.74703155258e-05 | 0.500403381996 | not a finalist | — | — |
| `g_ro_21211` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.7471256367e-05 | 0.500406480383 | not a finalist | — | — |
| `g_ro_02210` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [14, 15]]] | 209 | 4.74721067233e-05 | 0.500404076693 | not a finalist | — | — |
| `g_ro_01120` | [["remove", [17, 16]], ["add", [1, 2]], ["add", [15, 14]]] | 208 | 4.74730437038e-05 | 0.500808332669 | not a finalist | — | — |
| `g_ro_01220` | [["remove", [17, 16]], ["add", [2, 1]], ["add", [15, 14]]] | 208 | 4.74750213179e-05 | 0.500809028419 | not a finalist | — | — |
| `g_ro_11012` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [14, 15]], ["add", [29, 28]]] | 207 | 4.74835196385e-05 | 0.501201495128 | not a finalist | — | — |
| `g_echoD_3_268` | ["remove intermediate c43", "echo copy", {"bit": 268, "helper": 18, "removed_edges": [[19, 25], [17, 16]]}] | 206 | 4.74860030351e-05 | 0.501599127164 | not a finalist | — | — |
| `g_echo_3_268` | ["echo readout copy", {"bit": 268, "helper": 18, "remove_edges": [[19, 25], [17, 16]]}] | 206 | 4.74860030355e-05 | 0.501097082024 | not a finalist | — | — |
| `g_ro_21001` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [28, 29]]] | 207 | 4.74939078317e-05 | 0.501201394183 | not a finalist | — | — |
| `g_ro_02000` | [["remove", [17, 16]], ["add", [16, 17]]] | 207 | 4.7494981734e-05 | 0.501198990344 | not a finalist | — | — |
| `g_ro_01102` | [["remove", [17, 16]], ["add", [1, 2]], ["add", [29, 28]]] | 208 | 4.74977400205e-05 | 0.500803815056 | not a finalist | — | — |
| `g_ro_01202` | [["remove", [17, 16]], ["add", [2, 1]], ["add", [29, 28]]] | 208 | 4.74994751508e-05 | 0.500805139091 | not a finalist | — | — |
| `g_ro_21110` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [14, 15]]] | 208 | 4.750331395e-05 | 0.500806345479 | not a finalist | — | — |
| `g_ro_11101` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [28, 29]]] | 207 | 4.75040301989e-05 | 0.501204043838 | not a finalist | — | — |
| `g_ro_21210` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [14, 15]]] | 208 | 4.75051063513e-05 | 0.500807040156 | not a finalist | — | — |
| `g_ro_11201` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [28, 29]]] | 207 | 4.75057715474e-05 | 0.501205368929 | not a finalist | — | — |
| `g_ro_02012` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.75195387113e-05 | 0.500398994865 | not a finalist | — | — |
| `g_ro_01022` | [["remove", [17, 16]], ["add", [15, 14]], ["add", [29, 28]]] | 208 | 4.75221659891e-05 | 0.500803936891 | not a finalist | — | — |
| `g_ro_12011` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [14, 15]], ["add", [28, 29]]] | 208 | 4.75259111055e-05 | 0.500798900315 | not a finalist | — | — |
| `g_ro_21000` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]]] | 206 | 4.75277608117e-05 | 0.501602590262 | not a finalist | — | — |
| `g_echo_3_271` | ["echo readout copy", {"bit": 271, "helper": 11, "remove_edges": [[19, 25], [17, 16]]}] | 206 | 4.75279324481e-05 | 0.501096050181 | not a finalist | — | — |
| `g_echoD_3_271` | ["remove intermediate c43", "echo copy", {"bit": 271, "helper": 11, "removed_edges": [[19, 25], [17, 16]]}] | 206 | 4.75279324484e-05 | 0.501598094287 | not a finalist | — | — |
| `g_ro_11021` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [15, 14]], ["add", [28, 29]]] | 207 | 4.75284551595e-05 | 0.501204165768 | not a finalist | — | — |
| `g_ro_11100` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [1, 2]]] | 206 | 4.75378063369e-05 | 0.501605241747 | not a finalist | — | — |
| `g_ro_11200` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [2, 1]]] | 206 | 4.75395465926e-05 | 0.501606567899 | not a finalist | — | — |
| `g_ro_02101` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [28, 29]]] | 209 | 4.75398206037e-05 | 0.500401537061 | not a finalist | — | — |
| `g_ro_02201` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [28, 29]]] | 209 | 4.75415557158e-05 | 0.500402860711 | not a finalist | — | — |
| `g_ro_21012` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [14, 15]], ["add", [29, 28]]] | 208 | 4.75524246899e-05 | 0.500801951542 | not a finalist | — | — |
| `g_ro_12010` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [14, 15]]] | 207 | 4.75597252284e-05 | 0.501199773857 | not a finalist | — | — |
| `g_ro_11020` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [15, 14]]] | 206 | 4.75622353101e-05 | 0.501605363774 | not a finalist | — | — |
| `g_ro_11112` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [14, 15]], ["add", [29, 28]]] | 208 | 4.75624280053e-05 | 0.500804768199 | not a finalist | — | — |
| `g_ro_11212` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [14, 15]], ["add", [29, 28]]] | 208 | 4.75642252014e-05 | 0.500805462874 | not a finalist | — | — |
| `g_ro_02021` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.75644119256e-05 | 0.500401661122 | not a finalist | — | — |
| `g_ro_21101` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [28, 29]]] | 208 | 4.75728428909e-05 | 0.500804498118 | not a finalist | — | — |
| `g_ro_02100` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]]] | 208 | 4.75737083982e-05 | 0.500802092606 | not a finalist | — | — |
| `g_ro_21201` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [28, 29]]] | 208 | 4.75745793194e-05 | 0.500805822154 | not a finalist | — | — |
| `g_ro_02200` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]]] | 208 | 4.75754424157e-05 | 0.500803417316 | not a finalist | — | — |
| `g_ro_11002` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [29, 28]]] | 206 | 4.75868866271e-05 | 0.501601010474 | not a finalist | — | — |
| `g_ro_22011` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.75947201191e-05 | 0.50039967757 | not a finalist | — | — |
| `g_ro_21021` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [15, 14]], ["add", [28, 29]]] | 208 | 4.75972656149e-05 | 0.500804619951 | not a finalist | — | — |
| `g_ro_02112` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [14, 15]], ["add", [29, 28]]] | 210 | 4.75982465034e-05 | 0.500002899995 | not a finalist | — | — |
| `g_ro_02020` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [15, 14]]] | 208 | 4.75983037414e-05 | 0.500802216767 | not a finalist | — | — |
| `g_ro_02212` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [14, 15]], ["add", [29, 28]]] | 210 | 4.76000375741e-05 | 0.500003594137 | not a finalist | — | — |
| `g_ro_01122` | [["remove", [17, 16]], ["add", [1, 2]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.76010667096e-05 | 0.500407526684 | not a finalist | — | — |
| `g_ro_01222` | [["remove", [17, 16]], ["add", [2, 1]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.76030441953e-05 | 0.500408221878 | not a finalist | — | — |
| `g_ro_12111` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.76046193835e-05 | 0.500402488898 | not a finalist | — | — |
| `g_ro_12211` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [14, 15]], ["add", [28, 29]]] | 209 | 4.76064166787e-05 | 0.500403183594 | not a finalist | — | — |
| `g_ro_21100` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [1, 2]]] | 207 | 4.76066938819e-05 | 0.501205376493 | not a finalist | — | — |
| `g_ro_11121` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [15, 14]], ["add", [28, 29]]] | 208 | 4.76073563568e-05 | 0.500807438763 | not a finalist | — | — |
| `g_ro_21200` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [2, 1]]] | 207 | 4.76084292172e-05 | 0.501206701589 | not a finalist | — | — |
| `g_ro_11221` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [15, 14]], ["add", [28, 29]]] | 208 | 4.76093400647e-05 | 0.500808134512 | not a finalist | — | — |
| `g_ro_02002` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [29, 28]]] | 208 | 4.76229187516e-05 | 0.500797871605 | not a finalist | — | — |
| `g_ro_22010` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [14, 15]]] | 208 | 4.7628609095e-05 | 0.500800231837 | not a finalist | — | — |
| `g_ro_12001` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [28, 29]]] | 207 | 4.76292917515e-05 | 0.501198095822 | not a finalist | — | — |
| `g_ro_21020` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [15, 14]]] | 207 | 4.76311206189e-05 | 0.501205498424 | not a finalist | — | — |
| `g_ro_21112` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.76313401524e-05 | 0.500405540871 | not a finalist | — | — |
| `g_ro_21212` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.76331324308e-05 | 0.500406234993 | not a finalist | — | — |
| `g_ro_12110` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [14, 15]]] | 208 | 4.76384315079e-05 | 0.500803045125 | not a finalist | — | — |
| `g_ro_12210` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [14, 15]]] | 208 | 4.76402277073e-05 | 0.500803740377 | not a finalist | — | — |
| `g_ro_11120` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [15, 14]]] | 207 | 4.76411345195e-05 | 0.501208319202 | not a finalist | — | — |
| `g_ro_02121` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [15, 14]], ["add", [28, 29]]] | 210 | 4.76431150257e-05 | 0.500005565455 | not a finalist | — | — |
| `g_ro_11220` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [15, 14]]] | 207 | 4.76431171338e-05 | 0.501209015507 | not a finalist | — | — |
| `g_ro_02221` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [15, 14]], ["add", [28, 29]]] | 210 | 4.76450913628e-05 | 0.500006261029 | not a finalist | — | — |
| `g_ro_21002` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [29, 28]]] | 207 | 4.76557930639e-05 | 0.501201148407 | not a finalist | — | — |
| `g_ro_12000` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]]] | 206 | 4.76631057886e-05 | 0.501599288909 | not a finalist | — | — |
| `g_ro_11102` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [29, 28]]] | 207 | 4.76658070539e-05 | 0.501203797955 | not a finalist | — | — |
| `g_ro_11202` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [29, 28]]] | 207 | 4.76675471911e-05 | 0.501205123047 | not a finalist | — | — |
| `g_ro_22111` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [14, 15]], ["add", [28, 29]]] | 210 | 4.76734354861e-05 | 0.500003582161 | not a finalist | — | — |
| `g_ro_22211` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [14, 15]], ["add", [28, 29]]] | 210 | 4.76752278653e-05 | 0.500004276304 | not a finalist | — | — |
| `g_ro_21121` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.76761739067e-05 | 0.500408209206 | not a finalist | — | — |
| `g_ro_02120` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [15, 14]]] | 209 | 4.76770048453e-05 | 0.500405804037 | not a finalist | — | — |
| `g_ro_21221` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.76781527026e-05 | 0.500408904401 | not a finalist | — | — |
| `g_ro_02220` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [15, 14]]] | 209 | 4.76789800862e-05 | 0.500406500168 | not a finalist | — | — |
| `g_ro_12012` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [14, 15]], ["add", [29, 28]]] | 208 | 4.76876337785e-05 | 0.500798654464 | not a finalist | — | — |
| `g_ro_11022` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [15, 14]], ["add", [29, 28]]] | 207 | 4.76902358918e-05 | 0.501203919886 | not a finalist | — | — |
| `g_ro_22001` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [28, 29]]] | 208 | 4.76981021523e-05 | 0.500798554852 | not a finalist | — | — |
| `g_ro_02102` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [29, 28]]] | 209 | 4.77016398793e-05 | 0.500401291511 | not a finalist | — | — |
| `g_ro_02202` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [29, 28]]] | 209 | 4.77033737749e-05 | 0.500402615161 | not a finalist | — | — |
| `g_ro_22110` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [14, 15]]] | 209 | 4.77073224641e-05 | 0.500403819365 | not a finalist | — | — |
| `g_ro_12101` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [28, 29]]] | 208 | 4.77080133605e-05 | 0.500801198794 | not a finalist | — | — |
| `g_ro_22210` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [14, 15]]] | 209 | 4.7709113747e-05 | 0.500404514064 | not a finalist | — | — |
| `g_ro_12201` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [28, 29]]] | 208 | 4.77097534758e-05 | 0.500802523501 | not a finalist | — | — |
| `g_ro_21120` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [15, 14]]] | 208 | 4.77100269234e-05 | 0.500808770364 | not a finalist | — | — |
| `g_ro_21220` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [15, 14]]] | 208 | 4.77120046257e-05 | 0.500809466115 | not a finalist | — | — |
| `g_ro_02022` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.77262350895e-05 | 0.500401415573 | not a finalist | — | — |
| `g_ro_22000` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]]] | 207 | 4.77319910404e-05 | 0.501199428409 | not a finalist | — | — |
| `g_ro_12021` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [15, 14]], ["add", [28, 29]]] | 208 | 4.77326075547e-05 | 0.500801322954 | not a finalist | — | — |
| `g_ro_21102` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [29, 28]]] | 208 | 4.77347205939e-05 | 0.500804252534 | not a finalist | — | — |
| `g_ro_21202` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [29, 28]]] | 208 | 4.77364558108e-05 | 0.50080557657 | not a finalist | — | — |
| `g_ro_12100` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]]] | 207 | 4.7741825398e-05 | 0.501202074177 | not a finalist | — | — |
| `g_ro_12200` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]]] | 207 | 4.77435644196e-05 | 0.501203399944 | not a finalist | — | — |
| `g_ro_22012` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.77565436413e-05 | 0.500399432018 | not a finalist | — | — |
| `g_ro_21022` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [15, 14]], ["add", [29, 28]]] | 208 | 4.77591471955e-05 | 0.500804374368 | not a finalist | — | — |
| `g_ro_12112` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.77663345227e-05 | 0.50040224324 | not a finalist | — | — |
| `g_ro_12020` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [15, 14]]] | 207 | 4.77664236135e-05 | 0.501202198436 | not a finalist | — | — |
| `g_ro_12212` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [14, 15]], ["add", [29, 28]]] | 209 | 4.77681305957e-05 | 0.500402937935 | not a finalist | — | — |
| `g_ro_11122` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [15, 14]], ["add", [29, 28]]] | 208 | 4.77691295632e-05 | 0.500807193074 | not a finalist | — | — |
| `g_ro_11222` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [15, 14]], ["add", [29, 28]]] | 208 | 4.7771112049e-05 | 0.500807888823 | not a finalist | — | — |
| `g_ro_22101` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [28, 29]]] | 209 | 4.77768308578e-05 | 0.500401974218 | not a finalist | — | — |
| `g_ro_22201` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [28, 29]]] | 209 | 4.77785660543e-05 | 0.50040329787 | not a finalist | — | — |
| `g_ro_12002` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [29, 28]]] | 207 | 4.77910148432e-05 | 0.501197849777 | not a finalist | — | — |
| `g_ro_22021` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.7801422817e-05 | 0.50040209828 | not a finalist | — | — |
| `g_ro_02122` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [15, 14]], ["add", [29, 28]]] | 210 | 4.78049306575e-05 | 0.500005320098 | not a finalist | — | — |
| `g_ro_02222` | [["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [15, 14]], ["add", [29, 28]]] | 210 | 4.78069057672e-05 | 0.500006015672 | not a finalist | — | — |
| `g_ro_22100` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]]] | 208 | 4.78107177472e-05 | 0.500802530324 | not a finalist | — | — |
| `g_ro_12121` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.78113036108e-05 | 0.500404910932 | not a finalist | — | — |
| `g_ro_22200` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]]] | 208 | 4.78124518498e-05 | 0.500803855036 | not a finalist | — | — |
| `g_ro_12221` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [15, 14]], ["add", [28, 29]]] | 209 | 4.78132849442e-05 | 0.500405607061 | not a finalist | — | — |
| `g_ro_22112` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [14, 15]], ["add", [29, 28]]] | 210 | 4.78352514739e-05 | 0.500003336801 | not a finalist | — | — |
| `g_ro_22020` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [15, 14]]] | 208 | 4.78353137281e-05 | 0.500802654485 | not a finalist | — | — |
| `g_ro_22212` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [14, 15]], ["add", [29, 28]]] | 210 | 4.78370426304e-05 | 0.500004030944 | not a finalist | — | — |
| `g_ro_21122` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [1, 2]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.7838047961e-05 | 0.500407963815 | not a finalist | — | — |
| `g_ro_21222` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [2, 1]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.78400255349e-05 | 0.50040865901 | not a finalist | — | — |
| `g_ro_12120` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [15, 14]]] | 208 | 4.78451176726e-05 | 0.500805469098 | not a finalist | — | — |
| `g_ro_12220` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [15, 14]]] | 208 | 4.7847097911e-05 | 0.500806165785 | not a finalist | — | — |
| `g_ro_22002` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [29, 28]]] | 208 | 4.78599260929e-05 | 0.500798309106 | not a finalist | — | — |
| `g_ro_12102` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [29, 28]]] | 208 | 4.78697289173e-05 | 0.500800952942 | not a finalist | — | — |
| `g_ro_12202` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [29, 28]]] | 208 | 4.7871467817e-05 | 0.500802277648 | not a finalist | — | — |
| `g_ro_22121` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [15, 14]], ["add", [28, 29]]] | 210 | 4.78801259606e-05 | 0.500006002266 | not a finalist | — | — |
| `g_ro_22221` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [15, 14]], ["add", [28, 29]]] | 210 | 4.78821023837e-05 | 0.500006697841 | not a finalist | — | — |
| `g_ro_12022` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [15, 14]], ["add", [29, 28]]] | 208 | 4.78943269983e-05 | 0.500801077102 | not a finalist | — | — |
| `g_ro_22120` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [15, 14]]] | 209 | 4.7914014875e-05 | 0.500406241408 | not a finalist | — | — |
| `g_ro_22220` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [15, 14]]] | 209 | 4.79159902033e-05 | 0.500406937541 | not a finalist | — | — |
| `g_ro_22102` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [29, 28]]] | 209 | 4.79386472626e-05 | 0.500401728665 | not a finalist | — | — |
| `g_ro_22202` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [29, 28]]] | 209 | 4.79403812435e-05 | 0.500403052316 | not a finalist | — | — |
| `g_ro_22022` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.79632431094e-05 | 0.500401852727 | not a finalist | — | — |
| `g_ro_12122` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.79730155223e-05 | 0.500404665273 | not a finalist | — | — |
| `g_ro_12222` | [["remove", [19, 25]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [15, 14]], ["add", [29, 28]]] | 209 | 4.79749956296e-05 | 0.500405361402 | not a finalist | — | — |
| `g_ro_22122` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [1, 2]], ["add", [15, 14]], ["add", [29, 28]]] | 210 | 4.80419387205e-05 | 0.500005756906 | not a finalist | — | — |
| `g_ro_22222` | [["remove", [19, 25]], ["add", [25, 19]], ["remove", [17, 16]], ["add", [16, 17]], ["add", [2, 1]], ["add", [15, 14]], ["add", [29, 28]]] | 210 | 4.80439139176e-05 | 0.500006452481 | not a finalist | — | — |
| `g_bell2_0_6_forward` | ["late BC check", {"index": 6, "kind": "forward", "removed_edges": []}] | 207 | 4.91110252996e-05 | 0.500898834058 | not a finalist | — | — |
| `g_bell_0_6_reverse` | ["late BC check", {"index": 6, "kind": "reverse", "removed_edges": []}] | 207 | 4.91110252998e-05 | 0.500898834058 | not a finalist | — | — |
| `g_bell2_0_6_reverse` | ["late BC check", {"index": 6, "kind": "reverse", "removed_edges": []}] | 207 | 4.91110252998e-05 | 0.500898834058 | not a finalist | — | — |
| `g_bell_1_6_reverse` | ["late BC check", {"index": 6, "kind": "reverse", "removed_edges": [[19, 25]]}] | 206 | 4.92789723727e-05 | 0.501298892759 | not a finalist | — | — |
| `g_bell2_1_6_forward` | ["late BC check", {"index": 6, "kind": "forward", "removed_edges": [[19, 25]]}] | 206 | 4.92789723727e-05 | 0.501298892759 | not a finalist | — | — |
| `g_bell2_1_6_reverse` | ["late BC check", {"index": 6, "kind": "reverse", "removed_edges": [[19, 25]]}] | 206 | 4.92789723727e-05 | 0.501298892759 | not a finalist | — | — |
| `g_bell_2_6_reverse` | ["late BC check", {"index": 6, "kind": "reverse", "removed_edges": [[17, 16]]}] | 206 | 4.97725666498e-05 | 0.501300300679 | not a finalist | — | — |
| `g_bell2_2_6_reverse` | ["late BC check", {"index": 6, "kind": "reverse", "removed_edges": [[17, 16]]}] | 206 | 4.97725666498e-05 | 0.501300300679 | not a finalist | — | — |
| `g_bell2_2_6_forward` | ["late BC check", {"index": 6, "kind": "forward", "removed_edges": [[17, 16]]}] | 206 | 4.97725666499e-05 | 0.501300300679 | not a finalist | — | — |
| `g_bell_3_6_reverse` | ["late BC check", {"index": 6, "kind": "reverse", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 4.99405663144e-05 | 0.501700680077 | not a finalist | — | — |
| `g_bell2_3_6_forward` | ["late BC check", {"index": 6, "kind": "forward", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 4.99405663144e-05 | 0.501700680077 | not a finalist | — | — |
| `g_bell2_3_6_reverse` | ["late BC check", {"index": 6, "kind": "reverse", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 4.99405663144e-05 | 0.501700680077 | not a finalist | — | — |
| `g_bell_2_3_forward` | ["late BC check", {"index": 3, "kind": "forward", "removed_edges": [[17, 16]]}] | 206 | 5.00785963732e-05 | 0.501301048601 | not a finalist | — | — |
| `g_bell_2_3_reverse` | ["late BC check", {"index": 3, "kind": "reverse", "removed_edges": [[17, 16]]}] | 206 | 5.00785963732e-05 | 0.501301048601 | not a finalist | — | — |
| `g_bell2_2_3_forward` | ["late BC check", {"index": 3, "kind": "forward", "removed_edges": [[17, 16]]}] | 206 | 5.00785963732e-05 | 0.501301048601 | not a finalist | — | — |
| `g_bell2_2_3_reverse` | ["late BC check", {"index": 3, "kind": "reverse", "removed_edges": [[17, 16]]}] | 206 | 5.00785963732e-05 | 0.501301048601 | not a finalist | — | — |
| `g_bell_3_3_forward` | ["late BC check", {"index": 3, "kind": "forward", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 5.02467185387e-05 | 0.501701428721 | not a finalist | — | — |
| `g_bell_3_3_reverse` | ["late BC check", {"index": 3, "kind": "reverse", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 5.02467185387e-05 | 0.501701428721 | not a finalist | — | — |
| `g_bell2_3_3_forward` | ["late BC check", {"index": 3, "kind": "forward", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 5.02467185387e-05 | 0.501701428721 | not a finalist | — | — |
| `g_bell2_3_3_reverse` | ["late BC check", {"index": 3, "kind": "reverse", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 5.02467185387e-05 | 0.501701428721 | not a finalist | — | — |
| `g_bell_0_5_forward` | ["late BC check", {"index": 5, "kind": "forward", "removed_edges": []}] | 207 | 5.02564345399e-05 | 0.501230278027 | not a finalist | — | — |
| `g_bell_0_5_reverse` | ["late BC check", {"index": 5, "kind": "reverse", "removed_edges": []}] | 207 | 5.02564345399e-05 | 0.501230278027 | not a finalist | — | — |
| `g_bell2_0_5_forward` | ["late BC check", {"index": 5, "kind": "forward", "removed_edges": []}] | 207 | 5.02564345399e-05 | 0.501230278027 | not a finalist | — | — |
| `g_bell2_0_5_reverse` | ["late BC check", {"index": 5, "kind": "reverse", "removed_edges": []}] | 207 | 5.02564345399e-05 | 0.501230278027 | not a finalist | — | — |
| `g_bell_1_5_forward` | ["late BC check", {"index": 5, "kind": "forward", "removed_edges": [[19, 25]]}] | 206 | 5.04242119299e-05 | 0.50163060151 | not a finalist | — | — |
| `g_bell_1_5_reverse` | ["late BC check", {"index": 5, "kind": "reverse", "removed_edges": [[19, 25]]}] | 206 | 5.04242119299e-05 | 0.50163060151 | not a finalist | — | — |
| `g_bell2_1_5_forward` | ["late BC check", {"index": 5, "kind": "forward", "removed_edges": [[19, 25]]}] | 206 | 5.04242119299e-05 | 0.50163060151 | not a finalist | — | — |
| `g_bell2_1_5_reverse` | ["late BC check", {"index": 5, "kind": "reverse", "removed_edges": [[19, 25]]}] | 206 | 5.04242119299e-05 | 0.50163060151 | not a finalist | — | — |
| `g_bell_2_5_forward` | ["late BC check", {"index": 5, "kind": "forward", "removed_edges": [[17, 16]]}] | 206 | 5.09186313626e-05 | 0.50163201213 | not a finalist | — | — |
| `g_bell_2_5_reverse` | ["late BC check", {"index": 5, "kind": "reverse", "removed_edges": [[17, 16]]}] | 206 | 5.09186313626e-05 | 0.50163201213 | not a finalist | — | — |
| `g_bell2_2_5_forward` | ["late BC check", {"index": 5, "kind": "forward", "removed_edges": [[17, 16]]}] | 206 | 5.09186313626e-05 | 0.50163201213 | not a finalist | — | — |
| `g_bell2_2_5_reverse` | ["late BC check", {"index": 5, "kind": "reverse", "removed_edges": [[17, 16]]}] | 206 | 5.09186313626e-05 | 0.50163201213 | not a finalist | — | — |
| `g_bell_3_5_forward` | ["late BC check", {"index": 5, "kind": "forward", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 5.10864612315e-05 | 0.502032656525 | not a finalist | — | — |
| `g_bell_3_5_reverse` | ["late BC check", {"index": 5, "kind": "reverse", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 5.10864612315e-05 | 0.502032656525 | not a finalist | — | — |
| `g_bell2_3_5_forward` | ["late BC check", {"index": 5, "kind": "forward", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 5.10864612315e-05 | 0.502032656525 | not a finalist | — | — |
| `g_bell2_3_5_reverse` | ["late BC check", {"index": 5, "kind": "reverse", "removed_edges": [[19, 25], [17, 16]]}] | 205 | 5.10864612315e-05 | 0.502032656525 | not a finalist | — | — |
| `g_edge_27_26` | ["terminal readout encoding", [[27, 26]]] | 208 | 9.57206601524e-05 | 0.50080533259 | not a finalist | — | — |
| `g_edge_26_27` | ["terminal readout encoding", [[26, 27]]] | 208 | 9.57531473395e-05 | 0.500806179391 | not a finalist | — | — |
| `g_Aflag_06` | ["A extra stabilizer flag", [[15, 14], [15, 16], [9, 15]]] | 210 | 0.000165065190521 | 0.499052212923 | not a finalist | — | — |
| `g_Aflag_07` | ["A extra stabilizer flag", [[15, 14], [15, 16], [15, 9]]] | 210 | 0.000165065190521 | 0.499052212923 | not a finalist | — | — |
| `g_Aflag_04` | ["A extra stabilizer flag", [[15, 14], [15, 9], [15, 16]]] | 210 | 0.00016508220738 | 0.499053103156 | not a finalist | — | — |
| `g_Aflag_05` | ["A extra stabilizer flag", [[15, 14], [15, 9], [16, 15]]] | 210 | 0.00016508220738 | 0.499053103156 | not a finalist | — | — |
| `g_Aflag_10` | ["A extra stabilizer flag", [[15, 16], [15, 14], [9, 15]]] | 210 | 0.00025865972914 | 0.497066336493 | not a finalist | — | — |
| `g_Aflag_11` | ["A extra stabilizer flag", [[15, 16], [15, 14], [15, 9]]] | 210 | 0.00025865972914 | 0.497066336493 | not a finalist | — | — |
| `g_Aflag_00` | ["A extra stabilizer flag", [[15, 9], [15, 14], [15, 16]]] | 210 | 0.000258695534597 | 0.497067788862 | not a finalist | — | — |
| `g_Aflag_01` | ["A extra stabilizer flag", [[15, 9], [15, 14], [16, 15]]] | 210 | 0.000258695534597 | 0.497067788862 | not a finalist | — | — |
| `g_Aflag_08` | ["A extra stabilizer flag", [[15, 16], [15, 9], [14, 15]]] | 210 | 0.00025879081509 | 0.497067430048 | not a finalist | — | — |
| `g_Aflag_09` | ["A extra stabilizer flag", [[15, 16], [15, 9], [15, 14]]] | 210 | 0.00025879081509 | 0.497067430048 | not a finalist | — | — |
| `g_Aflag_02` | ["A extra stabilizer flag", [[15, 9], [15, 16], [14, 15]]] | 210 | 0.000258807816446 | 0.497067994556 | not a finalist | — | — |
| `g_Aflag_03` | ["A extra stabilizer flag", [[15, 9], [15, 16], [15, 14]]] | 210 | 0.000258807816446 | 0.497067994556 | not a finalist | — | — |
| `g_Bflag_0_1` | ["B logical-Z partial decoder", {"root": 13, "network": [[6, 12], [12, 13], [6, 12], [26, 25], [25, 19], [19, 13], [25, 19], [26, 25]], "cancel_existing": true}] | 211 | 0.000361556577025 | 0.493817696671 | not a finalist | — | — |
| `g_Bflag_1_1` | ["B logical-Z partial decoder", {"root": 13, "network": [[26, 25], [25, 19], [19, 13], [25, 19], [26, 25], [6, 12], [12, 13], [6, 12]], "cancel_existing": true}] | 211 | 0.000361856973506 | 0.491365000303 | not a finalist | — | — |
| `g_Bflag_0_0` | ["B logical-Z partial decoder", {"root": 13, "network": [[6, 12], [12, 13], [6, 12], [26, 25], [25, 19], [19, 13], [25, 19], [26, 25]], "cancel_existing": false}] | 215 | 0.000495656511401 | 0.49335206241 | not a finalist | — | — |
| `g_Bflag_1_0` | ["B logical-Z partial decoder", {"root": 13, "network": [[26, 25], [25, 19], [19, 13], [25, 19], [26, 25], [6, 12], [12, 13], [6, 12]], "cancel_existing": false}] | 215 | 0.000495980224368 | 0.490901217913 | not a finalist | — | — |
| `g_Bflag_2_1` | ["B logical-Z partial decoder", {"root": 6, "network": [[26, 25], [25, 19], [19, 13], [25, 19], [26, 25], [13, 12], [12, 6], [13, 12]], "cancel_existing": true}] | 213 | 0.000496124174615 | 0.491424941316 | not a finalist | — | — |
| `g_Bflag_3_1` | ["B logical-Z partial decoder", {"root": 26, "network": [[6, 12], [12, 13], [6, 12], [13, 19], [19, 25], [25, 26], [19, 25], [13, 19]], "cancel_existing": true}] | 213 | 0.000651456227888 | 0.491490110371 | not a finalist | — | — |
| `g_Bflag_2_0` | ["B logical-Z partial decoder", {"root": 6, "network": [[26, 25], [25, 19], [19, 13], [25, 19], [26, 25], [13, 12], [12, 6], [13, 12]], "cancel_existing": false}] | 215 | 0.000651618418723 | 0.48992285811 | not a finalist | — | — |
| `g_Bflag_3_0` | ["B logical-Z partial decoder", {"root": 26, "network": [[6, 12], [12, 13], [6, 12], [13, 19], [19, 25], [25, 26], [19, 25], [13, 19]], "cancel_existing": false}] | 215 | 0.000828077260568 | 0.490085194383 | not a finalist | — | — |

Older campaigns are superseded and preserved in `REPORT_v29c.md` and `REPORT_v30f.md`. Their cancelled jobs are not confirmations. No credentials, submission, commit, push or agent delegation were used.

Best finalist: **g_drop43_ro_00011**.
