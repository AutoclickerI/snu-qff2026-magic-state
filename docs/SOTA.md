# SOTA

## Baseline
The organizers' starter circuit (P §4: inject one physical |T⟩, encode with H and CNOT, transpile to the
grid) scores 1-F = 0.0252 with 28 CX and acceptance 1.0 (P §4.2 sample output). Teams "Noah" and "lss"
sit exactly there. Checked 2026-10-23.

## Current best
Ours on the board: **v13**, server 1-F = 0.000109770366545957 (bit-identical to `fast_check`), acceptance 0.6891, 115 CX,
submitted 2026-10-24 02:01:09 KST (`work/receipts/submit_v13.txt`); mean of 100 seed-0 re-draws 1.1257e-4 (v12's 49: 1.1460e-4).

Best competitor: Placeholder 6.286e-5, 169 CX, acceptance 0.546 (submitted 2026-10-24 01:57 KST; board at 02:12). Refresh with
`work/submit.py board`.

## Comparisons
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

## Prior work
| Work | Relevance (subgoal) | Source status |
|---|---|---|
| Gidney, Shutty, Jones, "Magic state cultivation: growing T states as cheap as CNOT gates", arXiv:2409.17595 | G1: our injection, double-cat check and superdense cycle come from its d=3 stage (`upstream/magic-state-cultivation`) | abstract checked; code read |
| Chamberland & Cross, flag-based magic-state prep (cited in P references) | G1: flagged direct readout (lane L3) | from memory |
| Postler et al., "Demonstration of fault-tolerant universal quantum gate operations" (cited in P) | G1: Steane-code T-state prep | from memory |
| Bravyi & Kitaev 2005, magic state distillation (P ref 1) | background | from memory |
| Gao, Yuan, Yao, "Extremely Low-Cost Magic State Preparation toward Fault-Tolerant Quantum Computing", arXiv:2609.12698 (2026-09) | G1: RM15 \|+_L⟩, transversal T, gauge-fix to Steane; postselected 210.2 p³ (≤ 2.2e-7 at p=1e-3), acceptance 86.9%, 19 qubits, 82 CNOT, all-to-all; the unmeasured output block's final noise is excluded, and under our judge that tail is ≥ 1.1e-5 (FINDINGS floor) | abstract checked; lanes RM_PROTO, RM_GRID |
| Goto, Sci. Rep. 6, 19578 (2016) | G1: FT Steane \|0_L⟩ with one verification ancilla; magic state with 2 + 16 ancillas | abstract checked (nature.com/articles/srep19578) |
| Chamberland & Noh, npj QI 6, 91 (2020), arXiv:2003.03049 | G1: redundant ancilla encoding + flags for color-code H-type magic states; 5e-8 at p=1e-4 with 64 qubits | abstract checked |
| Weilandt, Peham, Wille, arXiv:2601.13313; Criger et al., arXiv:2607.22498; arXiv:2610.09749 | G1: automated synthesis/reduction of FT state-prep circuits (Steane-type detection, ILP flags) | titles and abstracts checked; lane LIT |
