# SOTA

## Baseline
The organizers' starter circuit (P §4: inject one physical |T⟩, encode with H and CNOT, transpile to the
grid) scores 1-F = 0.0252 with 28 CX and acceptance 1.0 (P §4.2 sample output). Teams "Noah" and "lss"
sit exactly there. Checked 2026-10-23.

## Current best
Ours: **v8**, server 1-F = 0.000123064924290441 (key 0.000123), acceptance 0.6831, 115 CX, submitted
2026-10-23 19:05 KST (`work/receipts/server_status_1949.json`). Its true mean is about 1.248e-4
([FINDINGS](FINDINGS.md)).

Leaderboard on 2026-10-23 19:1x KST (`work/submit.py board`):

| Rank | Team | 1-F | 2q | Acceptance | Submitted (KST) |
|---|---|---|---|---|---|
| 1 | 초정밀모델제어학회쨩 (us) | 0.0001231 | 115 | 0.683 | 10-23 19:05 |
| 2 | Placeholder | 0.0001293 | 103 | 0.676 | 10-23 18:36 |
| 3 | omg | 0.007938 | 9 | 1.000 | 10-23 04:20 |
| 4 | Noah | 0.02517 | 28 | 1.000 | 10-23 12:56 |
| 5 | lss | 0.02517 | 28 | 1.000 | 10-23 17:17 |

Placeholder went from 4.22e-4 to 1.29e-4 between 16:03 and 18:36 KST. Its 103 CX would win a tie on the
key.

## Comparisons
| Method | Conditions | Result | Evidence |
|---|---|---|---|
| v4: Gidney d3 injection + double cat check + superdense cycle, permuted | official | 1.534e-4, 111 CX | `work/submissions/v4_perm_lazy.*` |
| v5: final cycle annealed with `proxy2` | official | 1.425e-4, 111 CX | `work/submissions/v5_gen_anneal.*` |
| v6: + X-only extra cat members (1,3), (4,2) | server | 1.310e-4, 113 CX (mean 1.325e-4) | `work/submissions/v6_gen2_extras.*` |
| v7: A1 layout (d1 moved, (2,3) reused as an extra) | server | 1.303e-4, 115 CX (mean 1.295e-4) | `work/submissions/v7_move_d1.*` |
| v8: v7 + commuting ALAP pre-cycle | server | 1.231e-4, 115 CX (mean 1.248e-4) | `work/submissions/v8_alap_cm.*` |
| v9: L1 CP-SAT interleaved cycle on the v6 layout + ALAP | local official | 1.232e-4, 113 CX (mean 1.234e-4) | `work/submissions/v9_L1i0_alap.*` |
| v10: A1 + interleaved cycle seeded from L1 orders + ALAP | local official | 1.2111e-4, 115 CX (mean 1.2208e-4) | `work/submissions/v10_A1i_alap.*`, `work/lanes/me_layout/mseed.jsonl` |

## Prior work
| Work | Relevance (subgoal) | Source status |
|---|---|---|
| Gidney, Shutty, Jones, "Magic state cultivation: growing T states as cheap as CNOT gates", arXiv:2409.17595 | G1: our injection, double-cat check and superdense cycle come from its d=3 stage (`upstream/magic-state-cultivation`) | abstract checked; code read |
| Chamberland & Cross, flag-based magic-state prep (cited in P references) | G1: flagged direct readout (lane L3) | from memory |
| Postler et al., "Demonstration of fault-tolerant universal quantum gate operations" (cited in P) | G1: Steane-code T-state prep | from memory |
| Bravyi & Kitaev 2005, magic state distillation (P ref 1) | background | from memory |
