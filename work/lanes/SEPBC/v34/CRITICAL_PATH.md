# R44 dependency and R43 search certificate

All times are zero-based native steps. Node ES/LS use the emitted wire order; CP receipts separately permit exact CX/control-phase commutations. A component ready slack is not an independently movable window.

## decoder0: R44; emitted-order minimum R44

| Component | Actual ready | Earliest ready | Ready slack |
|---|---:|---:|---:|
| prefix | 44 | 36 | 8 |
| wait_guard | 41 | 36 | 8 |
| encoder_bc | 44 | 39 | 5 |
| data_hops | 40 | 40 | 4 |
| encoder_a | 44 | 44 | 0 |

One longest-path suffix:

- ES 25, actual 25, slack 0: cx q[7],q[6];
- ES 26, actual 26, slack 0: cx q[1],q[7];
- ES 27, actual 27, slack 0: h q[1]; / measure q[1] -> c[11]; / h q[1];
- ES 28, actual 28, slack 0: reset q[1];
- ES 29, actual 29, slack 0: cx q[2],q[1];
- ES 30, actual 30, slack 0: cx q[3],q[2];
- ES 31, actual 31, slack 0: cx q[8],q[2];
- ES 32, actual 32, slack 0: cx q[2],q[8];
- ES 33, actual 33, slack 0: cx q[8],q[9];
- ES 34, actual 34, slack 0: cx q[9],q[8];
- ES 35, actual 35, slack 0: measure q[8] -> c[54];
- ES 36, actual 36, slack 0: reset q[8]; / h q[8];
- ES 37, actual 37, slack 0: h q[8]; / measure q[8] -> c[272]; / h q[8];
- ES 38, actual 38, slack 0: cx q[8],q[9];
- ES 39, actual 39, slack 0: cx q[14],q[8];
- ES 40, actual 40, slack 0: cx q[2],q[8];
- ES 41, actual 41, slack 0: cx q[1],q[2];
- ES 42, actual 42, slack 0: cx q[2],q[8];
- ES 43, actual 43, slack 0: cx q[1],q[2];
- ES 44, actual 44, slack 0: cx q[0],q[1];

Decoder/coupling times: `[{"pair": [10, 9], "t": 43}, {"pair": [21, 15], "t": 43}, {"pair": [0, 1], "t": 44}, {"pair": [20, 14], "t": 44}, {"pair": [7, 8], "t": 44}, {"pair": [3, 2], "t": 44}, {"pair": [22, 16], "t": 44}, {"pair": [9, 15], "t": 44}, {"pair": [8, 9], "t": 45}]`.

## reuseblue_0_R43: R43; emitted-order minimum R43

| Component | Actual ready | Earliest ready | Ready slack |
|---|---:|---:|---:|
| prefix | 43 | 35 | 8 |
| wait_guard | 40 | 36 | 7 |
| encoder_bc | 43 | 39 | 4 |
| data_hops | 39 | 39 | 4 |
| encoder_a | 43 | 43 | 0 |

One longest-path suffix:

- ES 25, actual 25, slack 0: cx q[1],q[7];
- ES 26, actual 26, slack 0: h q[1]; / measure q[1] -> c[11]; / h q[1];
- ES 27, actual 27, slack 0: reset q[1];
- ES 28, actual 28, slack 0: cx q[2],q[1];
- ES 29, actual 29, slack 0: cx q[8],q[2];
- ES 30, actual 30, slack 0: cx q[3],q[2];
- ES 31, actual 31, slack 0: cx q[2],q[8];
- ES 32, actual 32, slack 0: cx q[8],q[9];
- ES 33, actual 33, slack 0: cx q[9],q[8];
- ES 34, actual 34, slack 0: measure q[8] -> c[54];
- ES 35, actual 35, slack 0: reset q[8]; / h q[8];
- ES 36, actual 36, slack 0: h q[8]; / measure q[8] -> c[272]; / h q[8];
- ES 37, actual 37, slack 0: cx q[8],q[9];
- ES 38, actual 38, slack 0: cx q[14],q[8];
- ES 39, actual 39, slack 0: cx q[2],q[8];
- ES 40, actual 40, slack 0: cx q[1],q[2];
- ES 41, actual 41, slack 0: cx q[2],q[8];
- ES 42, actual 42, slack 0: cx q[1],q[2];
- ES 43, actual 43, slack 0: cx q[0],q[1];

Decoder/coupling times: `[{"pair": [10, 9], "t": 42}, {"pair": [21, 15], "t": 42}, {"pair": [0, 1], "t": 43}, {"pair": [20, 14], "t": 43}, {"pair": [7, 8], "t": 43}, {"pair": [3, 2], "t": 43}, {"pair": [22, 16], "t": 43}, {"pair": [9, 15], "t": 43}, {"pair": [8, 9], "t": 44}]`.

## checked16_timing_0: R44; emitted-order minimum R44

| Component | Actual ready | Earliest ready | Ready slack |
|---|---:|---:|---:|
| prefix | 44 | 36 | 8 |
| wait_guard | 41 | 36 | 8 |
| encoder_bc | 44 | 39 | 5 |
| data_hops | 40 | 40 | 4 |
| encoder_a | 44 | 44 | 0 |

One longest-path suffix:

- ES 25, actual 25, slack 0: cx q[7],q[6];
- ES 26, actual 26, slack 0: cx q[1],q[7];
- ES 27, actual 27, slack 0: h q[1]; / measure q[1] -> c[11]; / h q[1];
- ES 28, actual 28, slack 0: reset q[1];
- ES 29, actual 29, slack 0: cx q[2],q[1];
- ES 30, actual 30, slack 0: cx q[7],q[1];
- ES 31, actual 31, slack 0: cx q[0],q[1];
- ES 32, actual 32, slack 0: cx q[1],q[0];
- ES 33, actual 33, slack 0: cx q[1],q[7];
- ES 34, actual 34, slack 0: cx q[2],q[1];
- ES 35, actual 35, slack 0: h q[2]; / measure q[2] -> c[67]; / h q[2];
- ES 36, actual 36, slack 0: reset q[2];
- ES 37, actual 37, slack 0: cx q[8],q[2];
- ES 38, actual 38, slack 0: cx q[2],q[1];
- ES 39, actual 39, slack 0: cx q[1],q[2];
- ES 40, actual 40, slack 0: cx q[8],q[2];
- ES 41, actual 41, slack 0: cx q[8],q[9];
- ES 42, actual 42, slack 0: cx q[9],q[8];
- ES 43, actual 43, slack 0: cx q[14],q[8];
- ES 44, actual 44, slack 0: cx q[20],q[14];

Decoder/coupling times: `[{"pair": [10, 9], "t": 43}, {"pair": [21, 15], "t": 43}, {"pair": [0, 1], "t": 44}, {"pair": [20, 14], "t": 44}, {"pair": [7, 8], "t": 44}, {"pair": [3, 2], "t": 44}, {"pair": [22, 16], "t": 44}, {"pair": [9, 15], "t": 44}, {"pair": [8, 9], "t": 45}]`.

## Scope and diagnosis

The source-check-free R43 branches were not revisited. Reset-free pre-blue q2 reuse advances Bell preparation by one tick, but is SLOW in both tested A-encoder contexts (169.1 and146.3 seconds per million predicted). Retiming remains SLOW. The ordinary reset-bearing operation sets are CP-INFEASIBLE atR43 even with global tested CX/control-phase commutations.

The complete finite unitary search has11811 rank-four subspaces,35 coordinate input sets and95 matching layers including the empty layer. It has no CX-count cap. For two transfer routes, five initialization modes and their recorded per-cell release bounds, noR42/R43 target exists;120 R44 witnesses independently replay correctly. This excludes that finite model, not all prefix reorderings, helpers or general Clifford instruments.

The one-dirty-bus scan covers132 specified UVUV timing/direction recipes through data3/7/10. Endpoints are conservatively reserved during the bus; it does not exclude all interleavings or multiple buses. The measurement scan covers one rank-five→four Z measurement, or rank-four→three Z measurement followed by one X initialization, with fresh-input modes1/2. Neither has an R43 witness;41 R44 calibration witnesses independently replay. Multi-measurement/helper-assisted architectures remain outside this certificate.

The joint-coupling scan checks168 invertible binary syndrome maps HM=NH on one chosen schedule per unitary witness. No R43 coupling assignment is found for the tested witnesses. This does not exclude different gate paths with the same input choice. Four simple staggered branch recipes are infeasible; no global staggered-round bound is claimed.

A route-rewrite bookkeeping error was corrected: the old late q14 prefix release must precede its new data-hop reuse. All final route witnesses and full circuits use the corrected order. Invalid blue-gate permutations were rejected by the unchanged ideal checks. No detector was deleted to pass a failed test.
