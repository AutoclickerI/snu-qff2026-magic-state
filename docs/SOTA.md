# SOTA

## Baseline
The organizers' starter circuit (P §4: inject one physical |T⟩, encode with H and CNOT, transpile to the
grid) scores 1-F = 0.0252 with 28 CX and acceptance 1.0 (P §4.2 sample output). Teams "Noah" and "lss"
sit exactly there. Checked 2026-10-23.

## Current best
Ours on the board (rank 1, team shown as "초정밀모델제어학회쨩"): **v37c_h2600_r43418**, server 1-F = 3.428e-5 (key 3.43e-5), 400 CX, acceptance 0.506, submitted 2026-10-26 00:40 KST (`work/receipts/seq_v37c_h2600_r43418.txt`; best raced seed-0 draw of `work/lanes/MAIN/v37c`, all-orders 3.690403e-5).

Best competitor: Placeholder 3.856e-5 (key 3.86e-5), 201 CX, acceptance 0.579, submitted 2026-10-25 22:53 KST (4.005e-5 an hour earlier); then @nize_reze 6.02e-5, Inae 7.75e-5. Board read 2026-10-26 00:12 KST; refresh with `work/submit.py board`.

## Comparisons
The submitted lineage from v4 (1.534e-4) to v36g is in `git show b9051547^:docs/SOTA.md`; its circuits are in git history under `work/submissions/` and `work/lanes/MAIN/`.
| Method | Conditions | Result | Evidence |
|---|---|---|---|
| v36h: v36g + ACCBUY known-state guards and init-check trades (raced re-draw h2513_r4852) | server | 3.53131e-5, 327 CX (all-orders 3.81547e-5) | `work/lanes/MAIN/v36h.*`, `work/lanes/ACCBUY/REPORT.md` |
| v36k: v36i + 35 edits from a greedy joint extension (each round prices every valid addition of a v36h-positive BUNDLE 2-bundle or single on top, keeps the best at A ≥ 0.5002, funds acceptance with cheap singles); raced at 19:37 (best re-draw 3.54821e-5, key unchanged) | all orders | 3.789826e-5 (−0.22% vs v36j, −0.67% vs v36h), acceptance 0.50104, 364 CX, judge 1e6 7.9 s at 1 process | git (`work/lanes/MAIN/v36k.*`) |
| v37a: GLOBAL's R46 layout (15 ancilla roles moved, data [6,20,19,10,2,22,16] routed in 10 hops), rebuilt A (11 CX) and B/C (65 CX, warm-started), both A-flag-gap helpers on the grid, acceptance trades, INTEG repair, q14 readout 48→47; raced 20:20–21:20, best re-draw 3.48009e-5 submitted at 21:39, scored 3.48009e-5 (key 3.48e-5) | all orders | **3.761822e-5 (−0.74% vs v36k, −1.41% vs v36h)**, acceptance 0.50079, 390 CX, 49 ticks, judge 1e6 gates_ok 2.6 s at 1 process | `work/lanes/MAIN/v37a.*`, `work/lanes/GLOBAL/REPORT.md` |
| v37b: v37a + POLISH's greedy edits (CX16→10 at 37, CX19→25 at 13, pair moves 2_3 at 21/23, CX12→13 at 10 removed, A reads on q7/13/15/21 one tick earlier); raced 22:20–23:20, best draw 3.50298e-5 submitted 23:40 (key unchanged) | all orders | 3.742321e-5 (−0.52% vs v37a), acceptance 0.50348, 391 CX, judge 1e6 gates_ok, same speed as v37a | `work/lanes/MAIN/v37b.*`, `work/lanes/POLISH/` |
| v37c: MERGE of the lanes' gains on v37a: COMPLETE's R45 end of the phase network (round one tick earlier), POLISH's edits regenerated on it, GLOBAL's B/C core moved one tick earlier, joint greedy repair (one CX pair dropped for judge speed); raced 23:20–00:20, best draw 3.42770e-5 submitted 00:40 (key 3.43e-5) | all orders | **3.690403e-5 (−1.39% vs v37b, −1.90% vs v37a)**, acceptance 0.50572, 400 CX, 48 ticks; judge 1e7 3.6902e-5 ± 2.4e-6, gates_ok | `work/lanes/MAIN/v37c.*`, `work/lanes/MERGE/REPORT.md` |
| v37d: v37c + MERGE pass 2 (AJOINT's q9 guard/check reorder moved to R45, source-check trades, echo protection, retiming, guard repairs; two greedy passes to convergence); racing from the 01:37 slot (race 00:20–01:20) | all orders | **3.676347e-5 (−0.38% vs v37c)**, acceptance 0.50235, 406 CX, 48 ticks; judge 1e7 3.784e-5 ± 2.3e-6, gates_ok, same speed | `work/lanes/MAIN/v37d.*`, `work/lanes/MERGE/REPORT.md` |
| v37e: v37d + MERGE pass 3 stage `bc3_sources` (GLOBAL's BC3 joint B/C sources: actual earlier releases, checked same-basis measurements, fresh measured-plus sources with propagated detector byproducts, ported onto v37d); raced 01:20–02:20 for the 02:37 slot | all orders | **3.637096e-5 (−1.07% vs v37d)**, acceptance 0.50243, 406 CX; judge 1e7 3.833e-5 ± 2.4e-6, gates_ok; judge time 1.23–1.48× v37d's | `work/lanes/MAIN/v37e.*`, `work/lanes/MERGE/REPORT.md` |
| v37f: MERGE pass 3 on v37d: GLOBAL's BC3 modules R+L+q3 transported (−3.92e-7; R alone +7.6e-8, gains only with q3), POLISH transports, six greedy rounds to convergence (last +2.8e-10); races from the 03:37 slot (race 02:20–03:20) | all orders | **3.630561e-5 (−0.18% vs v37e, −1.25% vs v37d)**, acceptance 0.50346, 405 CX, 48 ticks; judge 4e7 3.769e-5 ± 1.2e-6, gates_ok; judge time 0.72× v37e's | `work/lanes/MAIN/v37f.*`, `work/lanes/MERGE/REPORT.md` |

## Prior work
| Work | Relevance (subgoal) | Source status |
|---|---|---|
| Gidney, Shutty, Jones, "Magic state cultivation: growing T states as cheap as CNOT gates", arXiv:2409.17595 | G1: our injection, double-cat check and superdense cycle come from its d=3 stage (`upstream/magic-state-cultivation`) | abstract checked; code read |
| Chamberland & Cross, flag-based magic-state prep (cited in P references) | G1: flagged direct readout (lane L3) | from memory |
| Postler et al., "Demonstration of fault-tolerant universal quantum gate operations" (cited in P) | G1: Steane-code T-state prep | from memory |
| Bravyi & Kitaev 2005, magic state distillation (P ref 1) | background | from memory |
| Gao, Yuan, Yao, "Extremely Low-Cost Magic State Preparation toward Fault-Tolerant Quantum Computing", arXiv:2609.12698 (2026-09) | G1: RM15 \|+_L⟩, transversal T, gauge-fix to Steane; postselected 210.2 p³ (≤ 2.2e-7 at p=1e-3), acceptance 86.9%, 19 qubits, 82 CNOT, all-to-all; the unmeasured output block's final noise is excluded, and under our judge that tail is ≥ 1.1e-5 (FINDINGS floor) | paper read; reproduced exactly (RM_PROTO); under our judge grid-free best 8.52e-5, on the grid 587–700 CX (FINDINGS) |
| Goto, Sci. Rep. 6, 19578 (2016) | G1: FT Steane \|0_L⟩ with one verification ancilla; magic state with 2 + 16 ancillas | abstract checked (nature.com/articles/srep19578) |
| Chamberland & Noh, npj QI 6, 91 (2020), arXiv:2003.03049 | G1: redundant ancilla encoding + flags for color-code H-type magic states; 5e-8 at p=1e-4 with 64 qubits | abstract checked |
| Weilandt, Peham, Wille, arXiv:2601.13313; Criger et al., arXiv:2607.22498; arXiv:2610.09749 | G1: automated synthesis/reduction of FT state-prep circuits (Steane-type detection, ILP flags) | titles and abstracts checked; lane LIT |
| Daguerre & Kim, arXiv:2410.07327 | G1: two-block RM15 → Steane code switch, corrected-output fit 25.5p² (≈ 2.44e-5 at 1e-3) without idles, acceptance ≈ 0.84, 26 qubits, 100 CX | lane SEARCH summary (Eq. 23, Table VII); not reproduced |
| Weilandt et al. MQT branch `ft-stateprep-qubit-perm` (Zenodo 23183007) | G1: fault-set-guided synthesis of verified CSS state preps, a candidate generator for B/C resources | code on Zenodo 23183007 (the SEARCH lane's copy was removed in the 2026-10-25 cleanup) |
