# SOTA

## Baseline
The organizers' starter circuit (P §4: inject one physical |T⟩, encode with H and CNOT, transpile to the
grid) scores 1-F = 0.0252 with 28 CX and acceptance 1.0 (P §4.2 sample output). Teams "Noah" and "lss"
sit exactly there. Checked 2026-10-23.

## Current best
Ours on the board: **v12**, server 1-F = 0.000112689151876909, acceptance 0.6905, 115 CX, submitted
2026-10-23 22:10:44 KST (`work/receipts/submit_v12.txt`); 3-seed mean 1.133e-4 (PLAN); 12-seed mean 1.1422e-4 (`work/lanes/EVAL/REPORT.md`).

Best competitor: Placeholder 7.604e-5, 161 CX, acceptance 0.590 (board 2026-10-23 23:30 KST). Refresh with
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
| v12: v11 + L5-lane pre-stage gains | server | 1.1269e-4, 115 CX (3-seed 1.133e-4, 12-seed 1.1422e-4) | `work/submissions/v12_L5lns12.*`, `work/lanes/L5_precycle/REPORT.md`, `work/receipts/submit_v12.txt` |

## Prior work
| Work | Relevance (subgoal) | Source status |
|---|---|---|
| Gidney, Shutty, Jones, "Magic state cultivation: growing T states as cheap as CNOT gates", arXiv:2409.17595 | G1: our injection, double-cat check and superdense cycle come from its d=3 stage (`upstream/magic-state-cultivation`) | abstract checked; code read |
| Chamberland & Cross, flag-based magic-state prep (cited in P references) | G1: flagged direct readout (lane L3) | from memory |
| Postler et al., "Demonstration of fault-tolerant universal quantum gate operations" (cited in P) | G1: Steane-code T-state prep | from memory |
| Bravyi & Kitaev 2005, magic state distillation (P ref 1) | background | from memory |
