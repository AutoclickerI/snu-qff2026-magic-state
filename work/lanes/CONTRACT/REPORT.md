# CONTRACT — P114

Status: measured-obstacle milestone complete; no <3.4e-5 full circuit found.
No submissions, commits, other-lane writes, or subagents. cand/ is empty because no build meets the finalist criterion.
Target: complete noisy preparation + contraction at exact A >= 0.5002; L <= 2.8e-5 (stretch 2.5e-5).
Audit verdict: reviewer 18 reduction holds under the inspected judge; no counterexample found. Exact floor 2.1892512824770078e-5. Case-by-case review: AUDIT.md.
Certificate and dense checks reproduced from isolated copies; C4 tail independently reproduced by the saved-circuit evaluator with six raw stabilizers +1.
Numerical receipts below are complete all-orders evaluations; cuts are explicitly counterfactual and are not additive budgets or universal bounds.

| Experiment | Exact L | Exact A | Scope |
|---|---:|---:|---|
| incumbent | 3.61195499148e-05 | 0.501548933326 | full noise |
| tail_perfect | 2.19209639186e-05 | 0.978760616214 | noise from tick 9 only |
| encoder_003_oracle | 8.71700284773e-05 | 0.958003929391 | perfect incoming 7-qubit state |
| late_full | 0.000136583137351 | 0.480485848908 | full noise |
| grid_late_full | 0.00033176718922 | 0.480485848908 | full noise |
| early_c4_KD_full | 0.000227887106195 | 0.451735929303 | full noise |
| early_c4_KD_HL_full | 0.00039973651929 | 0.44862357813 | full noise |
| early_storage_full | 0.000110514349297 | 0.37233131862 | full noise |
| early_storage_outer_tail | 5.15580332542e-05 | 0.928724155296 | noise from tick 58 only |
| early_zz_DK_full | 8.66103016618e-05 | 0.478515266872 | full noise |
| early_zz_DK_outer_tail | 5.50512140513e-05 | 0.958311034865 | noise from tick 47 only |
| c3_incumbent_full | 8.4107148849e-05 | 0.485979900341 | full noise |
| compact_c3_reset_full | 4.83899065549e-05 | 0.506856153824 | full noise |
| compact_c3_reset_jit_full | 4.36799568012e-05 | 0.521146680962 | full noise |
| compact_c3_ideal_oracle | 3.25968970118e-05 | 0.942854705062 | noise from tick 10 only |
| compact_c3_perfect_resource | 3.61082230277e-05 | 0.566868897302 | resource preparation made perfect |
| incumbent_cut_44 | 2.90459073567e-05 | 0.940389831208 | noise from tick 44 only |
| incumbent_cut_45 | 2.8473938227e-05 | 0.960978631043 | noise from tick 45 only |
| incumbent_cut_46 | 2.27581381195e-05 | 0.972833965125 | noise from tick 46 only |

All listed prices passed six raw noiseless stabilizers +1; exact kernel omission bounds and QASM SHA256 are in results.json and logs/<name>.json.
Evaluator copied into the lane. The default basis gave width 14 and a slow incumbent replay; MERGE's v37h-trained basis reduces width to 10 and reproduces L within 1.2e-16, A within 1.2e-16.
Option (a): exhausted 24 distinct ASAP schedules for every three-CX CSS isometry into the required C4 code (all four input positions, all X/Z auxiliary preparations, all ordered directed CX triples). Best noisy preparation + contraction with a perfect input is 8.71700284773147e-5; its full circuit is late_full. This closes that minimal-encoder class, not larger verified encoders.
Late growth also has a complete 36-qubit grid-native witness with unchanged outputs, 448 CX, 53 ticks: grid_late_full. It passes organizer format/class/raw correctness but fails acceptance and loss.
Early growth: tested both orders of the encoded B logical-X interaction, plus the alternate H/L logical support. The outer-check/tail counterfactual distinguishes checking cost from old resource/preparation cost.
Option (b): early_storage grows before BOTH outer checks, reuses the A cells for B, and verifies all four independent Z constraints of B using four readout ancillas (39 total qubits). Full L=1.105143493e-4, A=0.3723313; the last encoded B check + contraction alone costs 5.155803325e-5. Waiting faults and the two physical interactions per inner logical remain expensive.
Option (c): ZZ repetition saves qubits but loses; reusing C as the unmeasured-helper checker gives the best complete alternative after new 21-CX correlated B/C preparation and 9-CX verified A, ready at tick 44. It remains 4.367995680e-5 at A=0.521146681. Making only its resource preparation perfect gives 3.610822303e-5; this particular optimistic diagnostic still misses 3.4e-5.
Geometry: fixed incumbent D admits path-tile packing but no connected 8-cell free bus; allowing D to move admits a connected bus touching all seven non-square tiles (geometry.json). This is occupancy feasibility only, not a prepared circuit.
K/L checks do not measure the inner XXXX stabilizer. Code distance alone does not establish protection against all waiting faults.
Independent organizer exact verification: tail, grid_late, early_storage and compact_c3_reset_jit all have raw infidelity 0 and no errors (raw_verification.json). For 39/40-qubit phantoms its explicit n_qubits parameter is used; this is not a format/grid pass.
Same zebra host, sequential same-period 1e6-shot/1-process judge controls: v37h 24.0 s, gates_ok=True; grid_late 22.6 s, gates_ok=True, A_MC=0.480174 and passed=False. Shared host load was heavy; these are observed paired times, not server extrapolations.
Boundary repair: v37h's M1@28 reuse leaves all three Z syndromes tied to c366 before its original round. Fresh resources initially failed a deterministic-detector check. Replacing that M by R at the SAME tick and transporting the blue parity from c64 XOR c366 to c64 restores all six raw stabilizers, with its real reset noise charged. Invalid witnesses are retained in logs/invalid_builds.json.
Limits: these negatives close the priced preparations. Larger/direct verified C4 preparation, other inner codes, movable path layouts, and a complete incumbent-equivalent polishing search remain untested. No universal preparation no-go or polished-family ranking is claimed.
Evidence: results.json contains every completed exact price, its saved QASM SHA256, ordered outputs, evaluator omission bound, scope and Pareto front; logs/ receipts additionally hash evaluator sources. No active lane jobs remain at handoff.
