# SOTA

## Baseline
The organizers' starter circuit (P §4: inject one physical |T⟩, encode with H and CNOT, transpile to the
grid) scores 1-F = 0.0252 with 28 CX and acceptance 1.0 (P §4.2 sample output). Teams "Noah" and "lss"
sit exactly there. Checked 2026-10-23.

## Current best
Ours on the board (rank 1, team shown as "초정밀모델제어학회쨩"): **v36h_h2513_r4852**, server 1-F = 3.53130699502577e-5
(= local seed-0, key 3.53e-5), acceptance 0.50166, 327 CX, submitted 2026-10-25 13:38:55 KST
(`work/receipts/seq_v36h_h2513_r4852.txt`; best raced seed-0 draw of `work/lanes/MAIN/v36h`, all-orders 3.81547e-5).

Best competitor: Placeholder 4.906e-5, 201 CX, acceptance 0.521 (submitted 2026-10-25 13:26 KST). Board read
2026-10-25 13:45 KST; refresh with `work/submit.py board`.

## Comparisons
Evidence paths no longer in HEAD resolve through git (FINDINGS header): `git show b2a5243:<path>` for the lanes removed at 04:10 on 2026-10-25, `git show a58eca7:<path>` for `work/candidates/` and earlier removals.
| Method | Conditions | Result | Evidence |
|---|---|---|---|
| v4: Gidney d3 injection + double cat check + superdense cycle, permuted | official | 1.534e-4, 111 CX | `work/submissions/v4_perm_lazy.*` |
| v5: final cycle annealed with `proxy2` | official | 1.425e-4, 111 CX | `work/submissions/v5_gen_anneal.*` |
| v6: + X-only extra cat members (1,3), (4,2) | server | 1.310e-4, 113 CX (mean 1.325e-4) | `work/submissions/v6_gen2_extras.*` |
| v7: A1 layout (d1 moved, (2,3) reused as an extra) | server | 1.303e-4, 115 CX (mean 1.295e-4) | `work/submissions/v7_move_d1.*` |
| v8: v7 + commuting ALAP pre-cycle | server | 1.231e-4, 115 CX (mean 1.248e-4) | `work/submissions/v8_alap_cm.*` |
| v9: L1 CP-SAT interleaved cycle on the v6 layout + ALAP | local official | 1.232e-4, 113 CX (mean 1.234e-4) | `work/submissions/v9_L1i0_alap.*` |
| v10: A1 + interleaved cycle seeded from L1 orders + ALAP | server | 1.2111e-4, 115 CX (mean 1.2208e-4) | `work/submissions/v10_A1i_alap.*`, `work/lanes/me_layout/mseed.jsonl` |
| v11: v10's cycle, ALAP priority seed 45 | server | 1.1940e-4, 115 CX (mean of 100 re-draws 1.2189e-4) | `work/submissions/v11_A1i_alap45.*`, `work/receipts/reorder_v11.txt` |
| v12: v11 + L5-lane pre-stage gains | server | 1.1269e-4, 115 CX (3-seed 1.133e-4, 12-seed 1.1422e-4) | `work/submissions/v12_L5lns12.*` (submitted text: seed-0 re-draw `v12_L5lns12_r86.*`), `work/lanes/L5_precycle/REPORT.md`, `work/receipts/submit_v12.txt` |
| v13: v12 + first-use `q[16]` measured instead of reset (re-draw r70) | server | 1.0977e-4, 115 CX (100 re-draws 1.1257e-4) | `work/submissions/v13_m16_r70.*`, `work/candidates/v13_m16.*`, `work/receipts/seq_v13_m16_r70.txt` |
| v14: Steane-type round on L5 (A s7307, FT joint B+C sat6 82 CX) + first-use q27, q29 measured (re-draw r100) | server | 1.00638e-4, 207 CX (100 re-draws 1.0382e-4) | `work/submissions/v14_bcm_r100.*`, `work/candidates/v14_bcm.*`, `work/receipts/seq_v14_bcm_r100.txt`, `work/receipts/submit_v14.txt` |
| v15: LAYOUT2 parity check on A (cat 27–28–29, R=54) + measure-init at all 13 sites (re-draw r33) | server | 9.66371e-5, 212 CX (110 re-draws 9.871e-5) | `work/submissions/v15_l2m_r33.*`, `work/candidates/v15_l2m.*`, `work/receipts/seq_v15_l2m_r33.txt` |
| v16: L5 with BC2's clean B+C prep (82 CX, R=50) + measure-init at all sites (re-draw r147) | server | 8.28792e-5, 207 CX (245 re-draws 8.584e-5) | `work/submissions/v16_bc2m_r147.*`, `work/candidates/v16_bc2m.*`, `work/receipts/seq_v16_bc2m_r147.txt`, `work/receipts/submit_v16.txt` |
| v17: v16 + q19/q13 released early + readout re-encoding CX 17→16, 19→25 (re-draw r37) | server | 7.92666e-5, 209 CX (3-seed 8.306e-5) | `work/submissions/v17_r37.*`, `work/receipts/seq_v17_r37.txt` |
| v18: TREP's 19-CX injection encoder, pre-stage ALAP and interleaved with the suffix, round at 46 (re-draw r174) | server | 7.49754e-5, 203 CX (280 re-draws 7.730e-5) | `work/submissions/v18_r174.*`, `work/receipts/seq_v18_r174.txt`, `work/lanes/TREP/REPORT.md` |
| v20: v18 + q10 \|+⟩ reuse + third-order-checked timing, round at 45 (TREP2 reuse19_tuned, re-draw r126) | server | 7.14115e-5, 203 CX (290 re-draws 7.430e-5) | `work/submissions/v20_r126.*`, `work/receipts/seq_v20_r126.txt`, `work/lanes/TREP2/REPORT.md` |
| v22: v20 + HOPS hop_early (earlier final pre-stage CXs and transfer chain, watched sources) + MX checks after the RX init of q2, q9 (re-draw r155) | server | 6.95468e-5, 203 CX (380 re-draws 7.2405e-5) | `work/submissions/v22_r155.*`, `work/lanes/MAIN/v22h_c2c9.*` |
| v23h_c2c9: BCSYN2's fb_s401_0035 B+C prep + HOPS hop_early + ACHECK MX checks on q2, q9 (re-draw r290) | server | 6.75337e-5, 203 CX (320 re-draws 7.0272e-5) | `work/submissions/v23h_c2c9_r290.*`, `work/lanes/MAIN/v23h_c2c9.*` |
| v25k: v23h_c2c9 + PRESYN's blue XZ check + q19 reset+H + KNAP timing/check pack (re-draw r262) | server | 6.32297e-5, 215 CX (300 re-draws 6.5912e-5) | `work/submissions/v25k_r262.*`, `work/lanes/MAIN/v25k.*`, `work/lanes/KNAP/REPORT.md` |
| v26n: v25k + reviewer #1 readout copy, LNS2 `safe_best` (re-draw r115) | server | 6.18621e-5, 219 CX (120 re-draws 6.5202e-5) | `work/submissions/v26n_r115.*`, `work/lanes/LNS2/REPORT.md` |
| v30f: FRESH correlated rank-3 B/C resource (57 CX) on the older prefix (re-draw r454) | server | 5.62881e-5, 189 CX (385 re-draws ≈ 5.888e-5; all-orders 5.89377e-5) | `work/submissions/v30f_r454.*`, `work/lanes/FRESH/REPORT.md` |
| v30g: v30f + exact-loss timing feedback + measured-Z inits on q5, q12 (COMP29/ST2; re-draw r146) | server | 5.48190e-5, 194 CX (all-orders 5.68689e-5) | `work/submissions/v30g_r146.*`, `work/lanes/COMP29/REPORT.md` |
| v32p: v31s (SEPBC R45) + ST2's eight echoed parity checks on waiting data + q16 watch (re-draw r13) | server | 4.93405e-5, 205 CX (all-orders 5.14432e-5) | `work/submissions/v32p_r13.*`, `work/lanes/ST2/REPORT.md` |
| v35a: SEPBC R44 guard5_timing_1 (reoriented A, five storage guards, v30g edits) + reviewer 6's A partial decoder rebuilt by FRESH (re-draw r188) | server | 4.17026e-5, 206 CX (all-orders 4.39353e-5) | `work/submissions/v35a_r188.*`, `work/lanes/FRESH/REPORT.md`, `work/lanes/SEPBC/REPORT.md` |
| v35b: v35a + ST2's knapsack (two echoes funded by init changes; re-draw r1007) | server | 4.12926e-5, 210 CX (all-orders 4.37602e-5) | `work/submissions/v35b_r1007.*`, `work/lanes/ST2/REPORT.md` |
| v36a: SEPBC `checked16_timing_0` (12-CX release-aware A encoder, A decoder, q16 known-X check; re-draw r665) | server | 3.90052e-5, 207 CX (all-orders 4.14605e-5) | `work/submissions/v36a_r665.*`, `work/lanes/SEPBC/REPORT.md` |
| v36b: FRESH `r35/sepbc_reset_40_41_42` (v36a + timing, echo and reset trades; re-draw r580) | server | 3.87795e-5, 211 CX (all-orders 4.12933e-5) | `work/submissions/v36b_r580.*`, `work/lanes/MAIN/v36b.*` |
| v36c: ST2 population edits on v36b (raced re-draw h2505_r4508) | server | 3.84302e-5, 213 CX (all-orders 4.11516e-5) | `work/submissions/v36c_h2505_r4508.*`, `work/lanes/MAIN/v36c.*` |
| v36d: v36c + INTEG's acceptance trades and 34 pair/echo/guard gadgets (raced re-draw h2506_r53) | server | 3.75483e-5, 282 CX (all-orders 4.02862e-5) | `work/submissions/v36d_h2506_r53.*`, `work/lanes/INTEG/REPORT.md` |
| v36e: v36d with BFLAG's 56-CX B/C resource r3 (raced re-draw h2507_r449) | server | 3.67131e-5, 281 CX (all-orders 3.92343e-5) | `work/submissions/v36e_h2507_r449.*`, `work/lanes/BFLAG/REPORT.md` |
| v36f: v36e + PRECELL's continuous guards, echo ends and late B/C guards (raced re-draws h2508_r8782, h2509_r154749, h2510_r252072) | server | 3.62209e-5, then 3.58239e-5 and 3.56477e-5 with the κ-rule racer, 293 CX (all-orders 3.83761e-5) | `work/submissions/v36f_h25{08,09,10}_r*.*`, `work/lanes/PRECELL/REPORT.md` |
| v36g: v36f + INTEG2 re-integration (raced re-draws h2511_r42271, h2512_r151914; neither lowered the key) | server | 3.57728e-5, 3.55529e-5, 320 CX (all-orders 3.83605e-5) | `work/submissions/v36g_h2511_r42271.*`, `work/submissions/v36g_h2512_r151914.*`, `work/lanes/INTEG2/REPORT.md` |
| v36h: v36g + ACCBUY known-state guards and init-check trades (raced re-draw h2513_r4852) | server | 3.53131e-5, 327 CX (all-orders 3.81547e-5) | `work/submissions/v36h_h2513_r4852.*`, `work/lanes/ACCBUY/REPORT.md` |
| v36i: v36h + APROC's joint A-side guard witness (CX22→16 at 40 replaces CX10→16 at 39 and MX16 at 40) and greedy guard/echo repairs; racing from the 19:37 slot | all orders | 3.809138e-5, acceptance 0.50673, 353 CX, judge 1e6 6.1 s at 1 process | `work/lanes/MAIN/v36i.*`, `work/lanes/APROC/REPORT.md` |

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
