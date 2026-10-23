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
| Loss by idle window, v8 | none 1.75e-5; pre-cycle only 2.58e-5; cycle only 1.162e-4; cycle data only 1.039e-4; all 1.231e-4 | v8 | measured | `R/idle_decomp_v8.txt` |
| Tail-pair floor, any circuit | direct 1-step readout 2.567e-5; Bell-pair readout 5.857e-5 (all last checks X) | second-order tails under judge noise | model | `work/bounds.py` |
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
