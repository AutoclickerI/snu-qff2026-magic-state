# v31s and R44 critical paths

Native steps are zero based. ES/LS use the emitted per-wire operation order. Component ready slack is R minus earliest completion, not a freely movable interval. CP feasibility additionally permits the specified commuting CX/phase exchanges; it is conditional on the physical operations and measurements.

## v31s: R45; fixed-order minimum R45

| Component | Actual ready | Earliest ready | Ready slack |
|---|---:|---:|---:|
| prefix | 45 | 36 | 9 |
| data_hops | 41 | 39 | 6 |
| encoder_bc | 45 | 38 | 7 |
| encoder_a | 45 | 45 | 0 |
| terminal_Tdag | 45 | 30 | 15 |

One binding suffix (the JSON includes all nodes and representative longest paths):

- step 27, actual 27, slack 0: h q[1]; / measure q[1] -> c[11];
- step 28, actual 28, slack 0: reset q[1];
- step 29, actual 29, slack 0: cx q[2],q[1];
- step 30, actual 30, slack 0: cx q[3],q[2];
- step 31, actual 31, slack 0: cx q[8],q[2];
- step 32, actual 32, slack 0: cx q[2],q[8];
- step 33, actual 33, slack 0: cx q[8],q[9];
- step 34, actual 34, slack 0: cx q[9],q[15];
- step 35, actual 35, slack 0: cx q[9],q[8];
- step 36, actual 36, slack 0: cx q[15],q[9];
- step 37, actual 37, slack 0: measure q[9] -> c[56];
- step 38, actual 38, slack 0: reset q[9]; / h q[9];
- step 39, actual 39, slack 0: h q[9]; / measure q[9] -> c[59]; / h q[9];
- step 40, actual 40, slack 0: cx q[9],q[8];
- step 41, actual 41, slack 0: cx q[14],q[8];
- step 42, actual 42, slack 0: cx q[8],q[14];
- step 43, actual 43, slack 0: cx q[2],q[8];
- step 44, actual 44, slack 0: cx q[1],q[2];
- step 45, actual 45, slack 0: cx q[0],q[1];

## full_timing_0: R45; fixed-order minimum R45

| Component | Actual ready | Earliest ready | Ready slack |
|---|---:|---:|---:|
| prefix | 45 | 36 | 9 |
| data_hops | 41 | 39 | 6 |
| encoder_bc | 45 | 37 | 8 |
| encoder_a | 45 | 45 | 0 |
| terminal_Tdag | 45 | 31 | 14 |

One binding suffix (the JSON includes all nodes and representative longest paths):

- step 27, actual 27, slack 0: h q[1]; / measure q[1] -> c[11];
- step 28, actual 28, slack 0: reset q[1];
- step 29, actual 29, slack 0: cx q[2],q[1];
- step 30, actual 30, slack 0: cx q[3],q[2];
- step 31, actual 31, slack 0: cx q[8],q[2];
- step 32, actual 32, slack 0: cx q[2],q[8];
- step 33, actual 33, slack 0: cx q[8],q[9];
- step 34, actual 34, slack 0: cx q[9],q[15];
- step 35, actual 35, slack 0: cx q[9],q[8];
- step 36, actual 36, slack 0: cx q[15],q[9];
- step 37, actual 37, slack 0: measure q[9] -> c[56];
- step 38, actual 38, slack 0: reset q[9]; / h q[9];
- step 39, actual 39, slack 0: h q[9]; / measure q[9] -> c[59]; / h q[9];
- step 40, actual 40, slack 0: cx q[9],q[8];
- step 41, actual 41, slack 0: cx q[14],q[8];
- step 42, actual 42, slack 0: cx q[8],q[14];
- step 43, actual 43, slack 0: cx q[2],q[8];
- step 44, actual 44, slack 0: cx q[1],q[2];
- step 45, actual 45, slack 0: cx q[0],q[1];

## A44_feedback_0: R44; fixed-order minimum R44

| Component | Actual ready | Earliest ready | Ready slack |
|---|---:|---:|---:|
| prefix | 44 | 36 | 8 |
| encoder_bc | 44 | 37 | 7 |
| data_hops | 40 | 40 | 4 |
| encoder_a | 44 | 44 | 0 |
| terminal_Tdag | 44 | 31 | 13 |

One binding suffix (the JSON includes all nodes and representative longest paths):

- step 27, actual 27, slack 0: h q[1]; / measure q[1] -> c[11];
- step 28, actual 28, slack 0: reset q[1];
- step 29, actual 29, slack 0: cx q[2],q[1];
- step 30, actual 30, slack 0: cx q[3],q[2];
- step 31, actual 31, slack 0: cx q[8],q[2];
- step 32, actual 32, slack 0: cx q[2],q[8];
- step 33, actual 33, slack 0: cx q[8],q[9];
- step 34, actual 34, slack 0: cx q[9],q[8];
- step 35, actual 35, slack 0: measure q[8] -> c[54];
- step 36, actual 36, slack 0: reset q[8]; / h q[8];
- step 37, actual 37, slack 0: h q[8]; / measure q[8] -> c[272]; / h q[8];
- step 38, actual 38, slack 0: cx q[8],q[9];
- step 39, actual 39, slack 0: cx q[14],q[8];
- step 40, actual 40, slack 0: cx q[2],q[8];
- step 41, actual 41, slack 0: cx q[1],q[2];
- step 42, actual 42, slack 0: cx q[2],q[8];
- step 43, actual 43, slack 0: cx q[1],q[2];
- step 44, actual 44, slack 0: cx q[0],q[1];

## guard_joint_2: R44; fixed-order minimum R44

| Component | Actual ready | Earliest ready | Ready slack |
|---|---:|---:|---:|
| prefix | 44 | 36 | 8 |
| wait_guard | 41 | 36 | 8 |
| encoder_bc | 44 | 39 | 5 |
| data_hops | 40 | 40 | 4 |
| encoder_a | 44 | 44 | 0 |
| terminal_Tdag | 44 | 31 | 13 |

One binding suffix (the JSON includes all nodes and representative longest paths):

- step 27, actual 27, slack 0: h q[1]; / measure q[1] -> c[11];
- step 28, actual 28, slack 0: reset q[1];
- step 29, actual 29, slack 0: cx q[2],q[1];
- step 30, actual 30, slack 0: cx q[3],q[2];
- step 31, actual 31, slack 0: cx q[8],q[2];
- step 32, actual 32, slack 0: cx q[2],q[8];
- step 33, actual 33, slack 0: cx q[8],q[9];
- step 34, actual 34, slack 0: cx q[9],q[8];
- step 35, actual 35, slack 0: measure q[8] -> c[54];
- step 36, actual 36, slack 0: reset q[8]; / h q[8];
- step 37, actual 37, slack 0: h q[8]; / measure q[8] -> c[272]; / h q[8];
- step 38, actual 38, slack 0: cx q[8],q[9];
- step 39, actual 39, slack 0: cx q[14],q[8];
- step 40, actual 40, slack 0: cx q[2],q[8];
- step 41, actual 41, slack 0: cx q[1],q[2];
- step 42, actual 42, slack 0: cx q[2],q[8];
- step 43, actual 43, slack 0: cx q[1],q[2];
- step 44, actual 44, slack 0: cx q[0],q[1];

R43 feasibility on A44_feedback_0, commuting control phases=False: `{"status": "INFEASIBLE", "bound": 0.0, "seconds": 0.08178159900000001, "cut": 27, "seed": 0, "commuting_phases": false}`.
R43 feasibility on A44_feedback_0, commuting control phases=True: `{"status": "INFEASIBLE", "bound": 0.0, "seconds": 0.082501927, "cut": 27, "seed": 0, "commuting_phases": true}`.

## Final guard5_timing_0

Same q8/A binding suffix, minimum R44 in the emitted wire order. Current component ready/slack (the full node ledger is guard5_timing_0.critical.json):

| Component | Actual ready | Earliest ready | Ready slack |
|---|---:|---:|---:|
| prefix | 44 | 36 | 8 |
| wait_guard | 41 | 36 | 8 |
| encoder_bc | 44 | 39 | 5 |
| data_hops | 40 | 40 | 4 |
| encoder_a | 44 | 44 | 0 |
