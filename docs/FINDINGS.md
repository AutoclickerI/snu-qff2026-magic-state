# Findings
Class: measured, static (counted from code/spec), model (conditional estimate), official (external verdict).
All 1-F values are at p=1e-3, 1e8 shots, seed 0 unless a seed is named. `R/` = `work/receipts/`,
`ML/` = `work/lanes/me_layout/`, `L1/` = `work/lanes/L1_cpsat_schedule/`.

| Quantity | Value ± uncertainty | Scope | Class | Receipt |
|---|---|---|---|---|
| `fast_check` vs server | bit-identical (v6, v7, v8) | official setting | official | `R/server_status_1949.json`, `R/seq_v8_*.txt` |
| MC noise of one official score | ±1.2e-6 (≈1%) | circuits near 1.2e-4 | measured | sem in every check output |
| v6 → v7 true gain | 1.3254e-4 → 1.2954e-4 (−2.3%); seed 0 alone showed −0.6% | 3-seed means | measured | `R/multiseed_v6_v7.txt` |
| Pre-cycle ALAP gain | v7 1.2954e-4 → 1.248–1.251e-4 (≈−3.5%) | A1 layout, 3-seed means | measured | `R/multiseed_v6_v7.txt`, `ML/mseed.jsonl` |
| v8 (submitted 19:05) | 1.23065e-4 seed 0; 3-seed mean 1.2481e-4; 115 CX | A1 + commuting ALAP s28 | official | `R/seq_v8_24379afac6.txt` |
| L1 interleaved cycle, v6 layout, + ALAP | 1.23188e-4 seed 0; mean 1.2339e-4; 113 CX | `alapvar/f3cd7d0e95` | measured | `R/seq_v9_f3cd7d0e95.txt`, `ML/mseed.jsonl` |
| Proxy ranks full circuits once ALAP is applied | proxy 1.1274/1.1337/1.1437/1.1839e-4 → mean 1.234/1.238/1.248/1.30e-4 | 4 schedule classes | measured | `ML/mseed.jsonl` |
| Proxy does not rank without ALAP | L1 proxy −4.8% vs v6, official 1.3078e-4 vs 1.3103e-4 | v6 layout | measured | `L1/interleaved_top5.json` |
| A1 seeded from L1 interleaved schedules | proxy 1.09799e-4 (6 chains agree); + ALAP seed-0 1.2102–1.2219e-4, 3-seed means 1.2207–1.2225e-4 | A1, lmax 9 | measured | `ML/res_A1_9b_*.json`, `ML/log_alap_A1b0.txt`, `ML/mseed.jsonl` |
| v11 true 1-F | 1.2189e-4 ± 0.012e-4 (mean of 100 re-draws; sd of one draw 1.20e-6); seed-0 draws 1.1927–1.24e-4 | v11, same noise model | measured | `R/reorder_v11.txt` |
| v11 loss by region (seed 0) | all 1.194e-4; pre-stage only (ideal final round) 1.44e-6; final round only 9.96e-5; final-round gates only 1.63e-5; data tail idle only 2.28e-5; gates + tails 6.78e-5; pre × round cross ≈ 1.8e-5 | v11 | measured | `R/region_decomp_v11.txt`, `work/region_decomp.py` |
| Tail floor with cat-member X propagation | 2.884e-5 (direct readout, all last checks X) | second order, any cat-based direct readout | model | `work/bounds.py` + 2/15 p X per data |
| Floor, any circuit | **1.116e-5** (exact over 4^7, judge decoding): only the noise after the last possible check, every other gate noiseless. One idle step on all 7 data (1.1625e-5) is not forced: a dummy CX from a checked |0⟩ partner onto each data qubit in the final step leaves X 8/15 p, Y 4/15 p, Z 4/15 p instead of p/3 each. Counting the last check CNOTs too: direct 1-step readout 2.567e-5 (pair formula; exact 2.553e-5), 2.520e-5 with dummies (needs 14 more qubits, not worth it), Bell-pair readout 5.857e-5 | second-order tails under judge noise | model | `work/bounds.py` |
| Direct-readout class floor (grid-free, data-side noise only) | 2.865e-5 if each qubit starts at its first check; 3.037e-5 if all start together (X gens {0246,1256,3456}, Z gens {3456,0235,1234}, 4-step round); X/Z orders must commute (even crossings) | final round only | model | `work/lanes/DR/relaxed.py`, `floor_*_valid.txt` |
| Direct readout with plain verified cats | proxy 2.78e-4 with all noise vs 3.28e-5 with data-side noise only: cat-member X errors before coupling land on the data after its last Z-check | grid-free prototype, 37 qubits, 54 CX | measured | `work/lanes/DR/poc.py`, `sched_valid.json` |
| Direct-readout rounds, grid-free, exact cycle proxy (v11 round = 1.098e-4) | plain verified cats 2.78e-4; X-cats with every member verified the step before coupling + plain Z-cats 9.47e-5; per-qubit Z-before-X order with: Z Bell pairs 7.48e-5 (27 ancillas peak), Z cats + 1 verifier 5.45e-5 (36), clean cats both types 4.49e-5 (48); flagged single-ancilla checks: data-side floor alone 6.34e-5 | final round only, 4-step schedules from relaxed.py | measured | `work/lanes/DR/poc.py`, `sched_*.json`, `flagsched.py` |
| Steane-type final round (grid-free, exact proxy; v11 round = 1.098e-4) | **3.20e-5**, first order 0, 28 qubits, 48 CX: data CX→|+_L⟩ block A (read Z), then |0_L⟩ block B CX→data (read X); B verified by an unverified |0_L⟩ block C via transversal CX b→c the step before B couples. Data side alone 2.567e-5 (= the direct-readout floor), B 1.9e-7, C 0. One weight-3 Z verifier instead of C: 7.85e-5; two: 6.72e-5. Input noise on the data barely matters (1e-2 per data qubit adds 2.2e-6) | final round only | measured | `work/lanes/DR/steane.py` |
| Block-A encoder on L5 cells, exhaustive (all 11,811 states; every circuit with 11–13 CX, 3.0e6 ASAP circuits) | min 11 CX, min depth 5; min danger 6.67e-4 at depth ≤ 8 (the sampled s7307 is already optimal there), 5.33e-4 at 12 CX depth 9 (`EXENC/prepA_L5_exact.json`); no encoder on these 7 cells goes lower, so the remaining A cross term needs a verifier block or other cells | L5 A cells, no helpers | measured | `work/lanes/EXENC/REPORT.md` |
| First full L5 circuit (A s7307 or exact + ST_BC joint B+C prep, 13 layers, 72 CX) | not fault tolerant: first order 7.7e-4, all from X faults inside the joint B+C prep, which leave correlated X errors on B and C so C's check cancels; second order 8.95e-5, driven by the data waiting 15 steps (round at 48, pre-stage ends 33); exp(-A1) 0.56 | L5 with a joint B+C prep | measured | `work/candidates/st_L5_*_bc13.qasm`, `lanes/EVAL/exact2.py` |
| In-place layouts with A, B, C each connected (helpers from the 8 free cells) | none found: CP-SAT UNKNOWN (5 seeds x 500 s, also for A+B alone), ~50 annealing chains never connect A and B together (A+C and B+C succeed), vertical stripes proven infeasible; with data cells as helpers: 14+ hops and no A encoder at depth <= 9. Evidence, not proof | 6x6, pre-stage data at [0,20,7,4,3,15,8] | measured | `work/lanes/ST_LAY/REPORT.md` |
| v12 loss by source, exact | 2nd order 1.122e-4, +3rd 1.143e-4 (MC mean 1.142e-4); first order 0; idle 6.7e-5, gate 3.9e-5, flip 6.3e-6; top pairs are final-cycle data idles (q0 steps 39–41, q4 40–41), none above 0.6% | v12 | measured | `work/lanes/EVAL/REPORT.md`, `v12_sens.json` |
| Why Steane-type blocks need no fault-tolerant encoder | A's Z errors land on the data before B checks them; B's X errors (X_L class included) are copied onto C and read; C's errors only flip readouts; Z errors on B only flip B's readout. Only single faults giving a zero-syndrome Z_L pattern on A are dangerous | mechanism | model | `work/lanes/DR/steane.py` |
| First grid Steane-round circuit (layout L2, v11 pre-stage, 5 data moves, blocks prepared one after another, data idle ~36 steps before the round) | 1-F 6.05e-4, acceptance 0.384 (fails 0.5). Noise in one region only: pre 4.6e-6, moves 1.9e-5, A prep 6.4e-5, B prep 0, C prep 0, round 2.8e-5 (≈ the grid-free 2.567e-5); the rest (~4.9e-4) is cross terms | full circuit, 1e7 shots | measured | `work/candidates/st_L2_v0.*`, `work/lanes/DR/regions.py` |
| Cross-term mechanism of the Steane round | a single fault in A's encoder leaving a Z error of class Z_L×(weight ≤1) on A (every weight-2 Z) plus one ordinary data Z error on the third qubit of that logical line before the round = undetected Z_L. Danger metric `synth.dangerous_z` (single faults with that Z class and an X part invisible to A's readout): standard 9-CX dual encoder 4.7e-4, L2 CP-SAT A 5.5e-3, best L5 A 6.7e-4 (11 CX, 6 layers). So: low-danger A, short data exposure before the round | mechanism + metric | model | `work/lanes/DR/synth.py` |
| Why cats fail unless clean | the last check's ancilla errors land on the data after its last check; Z-check ancillas that touch two data make weight-2 Z errors that alias a one-qubit error on the third qubit of a logical line | mechanism | model | noise isolation in `poc.py` runs |
| Loss by idle window, v8 | none 1.75e-5; pre-cycle only 2.58e-5; cycle only 1.162e-4; cycle data only 1.039e-4; all 1.231e-4 | v8 | measured | `R/idle_decomp_v8.txt` |
| v6 loss split | tail pairs 9.42e-5 (72%), partial windows 2.42e-5 (18%), outside cycle model 1.26e-5 (10%) | v6 | model | `work/decompose.py`, `L1/REPORT.md` |
| v8 final-cycle tails (idle steps after last op) | d0 3, d2 2, d3 2, d4 2, d1 1, d5 1, d6 1 | v8 | static | schedule of `work/submissions/v8_alap_cm.qasm` |
| Total idle does not predict score | corr(score, data idle) = −0.13 | 16 ALAP variants | measured | `ML/idlestats.py` |
| c1 residue | 3.70e-17 = 5 faults × 7.4e-18 roundoff; `by_instruction` empty | v6–v9 family | measured | `L1/residue_audit.json` |
| L1 CP-SAT objective vs Stim proxy | corr 1.0, max error 1.3e-17 | 152 order classes | measured | `L1/generated_complete_calibration_summary.json` |
| Z-before-X schedules, v6 layout | best proxy 1.1831e-4 (exhaustive, 45,360) | orientation [0,1,1], layers 2..7 | measured | `L1/REPORT.md` |
| Validity rules vs Stim | 0 false negatives, 2–4% false positives | 392 schedules | measured | session analysis 2026-10-23 |

## Closed recipes
A negative closes only the recipe tested. "Leaves open" names what the result does not rule out.
| Recipe tested | Result | Mechanism | Leaves open | Receipt |
|---|---|---|---|---|
| Remove all pre-cycle/cycle barriers (ASAP everything) | 1.94e-4, worse | cycle CNOTs start before the check stage settles, more window pairs | partial overlaps | `work/lanes/L5_precycle/REPORT.md` |
| Two-hop extra cat members (d2, d3) | worse than v6 | 2 extra CNOTs per hop add more than they save | other hop geometries | session 2026-10-23 |
| One idealized extra on any data, adjacency ignored | no gain | tail already near its floor for those qubits | extras on moved layouts | `work/ceiling_extras.py`, `work/ceil*.log` |
| Uniform input noise added to the proxy | no ranking gain | pre-cycle errors are not uniform | a full-circuit evaluator (P5) | session 2026-10-23 |
| Measurement-based flagged prep (Codex) | 0.162, c1 = 188 | not FT at first order | flag schedules searched on the grid | `work/codex/NOTES.md` |
| Min-total-idle pre-cycle schedule as objective | not pursued | idle total uncorrelated with score (above) | weighted idle by location | `ML/idlestats.py` |

## Failures
| Symptom | Cause | Avoid / fix | Cost | Receipt |
|---|---|---|---|---|
| Shell dies with exit 144 | `pkill -f <pattern>` matched the shell running the command | kill by PID from `pgrep -f "[x]yz"` (bracket trick) | twice, 2026-10-23 | session |
| Submission refused "Next submission allowed in 3 seconds" | the slot was timed from the clock, 2 s before 1 h after the last `submitted_at` | `submit_when_ready.sh` waits 3605 s from the server's last `submitted_at` | one retry, 2026-10-23 20:05 | `work/receipts/submit_v10.txt` |
| A wait never ended | waited for an output file that a crashed job never wrote | wait on process exit (`while pgrep ...`), then read the log | 20 min | `ML/log_A1r9.txt` |
| `RANDSTART=1` anneal: "no feasible start" | random schedules almost never pass Stim validity | start from a valid schedule (`BASE=`) | one run | `ML/log_A1r9.txt` |
| OR-Tools presolve said INFEASIBLE on a feasible model | presolve bug in 9.15 for table/product models | disable presolve for complete-objective models | earlier certificates void | `L1/infeasible_reproducer.pbtxt` |
| T→S Clifford surrogate has random detectors | the T/T† sign pattern is not a valid S pattern | use another surrogate (T→I for X_L) | L4 time | L4 Codex log |
