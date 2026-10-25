TOOLS: isolated patches, measurements and hour-boundary handoff, 2026-10-25.
All paths below are relative to this directory. `patched/` contains the cumulative proposals;
install only the adopted bundles identified below. No installation was performed.

1. **adopt — official comparator threshold.** Binary search over positive binary64 values,
   using the published three-significant-digit formatter, CX count and submission order.
   Against key 3.53e-5 / 327 CX, the first losing float is 3.5350000000000005e-5 at 326 CX,
   or 3.525e-5 at >=327 CX. At key 1e-5 / equal CX it is 9.995e-6.
   Checked 7,200 keys, 43,200 boundaries and 648,000 neighboring doubles: zero mismatches.
   Includes candidate-CX plumbing, full-precision relay logs and actual sequential-receipt wiring.
   A new local PASS pick appeared during final checks: v36h_h2517_r342819, key 3.49e-5 / 327 CX;
   the helper picked it up and returned 3.485e-5. Its board status was not checked.
   Test: `tests/test_threshold.py`; receipts: `receipts/01_threshold.json`, `receipts/integration.json`.
   Swap: `swaps/01.md`, exact diff `swaps/01.diff`; standalone bundle `stages/01/`.

2. **reject — observable-unified selector deployment.** All 73 moments match on all nine required
   circuits; maximum absolute difference 1.6653345369377348e-16. The denominator stays 2^K.
   Three alternating paired end-to-end runs per circuit: 1 worker = 1.85–3.98x speedup
   (median 2.67x); 7 workers = 0.87–1.18x (median 1.13x), including three regressions.
   v36h: 8.402→3.153 s at 1 worker; 1.496→1.271 s at 7. Startup is included; host load varied.
   **16-process times: unmeasured.** That test conflicts with the zebra <=8 process limit;
   the requested adoption criterion is unmet. v29c was read from MAIN/sparse/examples/v29c.
   Test: `tests/test_selector.py`; receipt: `receipts/02_selector.json`, all raw `selector_*.log`.
   Swap: `swaps/02.md`, exact diff `swaps/02.diff`; code in `patched/work/lanes/MAIN/sparse/`.

3. **reject — exact-mean drop-policy deployment.** Implemented R=S-tau*K with exact E[S]=m*N,
   E[K]=m*A, N=A*L; samples estimate residual variance. Certificates bind QASM, ordered data,
   noise, judge/xtim/numpy build, CPU/thread environment; mismatches are rejected.
   24 scalar probability checks pass. Historical audit: 102 logs, 205,238 drop records,
   2,352 completions, zero JSONL chunk traces. Existing outputs omit per-chunk S,K and censor
   dropped outcomes: equal-compute hits/chunk and any gain are **unmeasurable**, not zero.
   The complete-trace replay harness is provided; the reviewer's model gain is not claimed.
   Test: `tests/test_policy.py`; receipt: `receipts/03_policy.json`; mean: `receipts/v36h.exact.json`.
   Swap: `swaps/03.md`, exact diff `swaps/03.diff`; isolated policy in `stages/03/work/race.py`.

4. **adopt — checkpoint/resume with the existing fresh-race drop policy.** Install `stages/04-safe/`,
   which includes item 1 and excludes the rejected item-3 pruning change. The cumulative
   `patched/work/race.py` contains both proposals and is not the adoption bundle.
   Real xtim: 8 x 1e6 shots uninterrupted versus 3+5 across separate processes; all nine final
   count/sum/score/SEM/acceptance/status fields are bit-identical. Reused 3 chunks = 3M shots.
   Durable chunk writes: 0.178 s / 49.726 s full test = 0.36%; hourly net gain is unmeasured.
   Main()/Pool SIGUSR1 cut, actual process exit, hour-name change, resume indices and full-only
   promotion all pass. Environment mismatch/corruption reject; good/bad finite-threshold choices pass.
   Atomic checksummed float.hex snapshots preserve indices and seed rule. Resume compares predicted
   win/remaining cost against fresh work including pruning; uncalibrated finite-threshold prefixes defer.
   Tests: `tests/test_checkpoint.py`, `tests/test_main_race.py`, `tests/test_integration.py`.
   Receipts: `receipts/04_checkpoint.json`, `receipts/04_main_race.json`, `receipts/integration.json`.
   Swap: `swaps/04.md`, exact diff `swaps/04.diff`. Only zebra is verified; other hosts need pidfd
   support checked by main (Linux >=5.3); Owl also needs the supplied --pid=host launch change.

5. **reject — lease allocation without measured idle gaps.** The forced minimum is already removed.
   Audited 12 logs across all six racer hosts for h2516/h2517. No historical CPU counters,
   allocation timeline or lane-release events exist: idle core-minutes are **unknown** on each host.
   No lease design is proposed. Telemetry-only patched copies record allocation/cut CPU counters;
   system idle and reclaimable team capacity remain distinct. Allocation arithmetic is unchanged.
   Test: `tests/test_capacity.py`; receipt: `receipts/05_capacity.json` (per-host observed chunks).
   Swap: `swaps/05.md`, exact proposed diff `swaps/05.diff`; telemetry helper in `patched/work/`.

Reproduction: from repository root, prefix each test with
`env PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python`.
Checkpoint tests default to the independently adoptable bundle. Full-proposal receipts are retained with `proposal_` prefixes.
All writes stayed under TOOLS; no remote execution, submission, git mutation or credential access occurred.
Read-only source hashes at entry and delivery match: `receipts/manifest.json`; only test-owned PIDs were signaled.
The public submit.html link returned 404; the cited [official site](https://snuquantums.github.io/snu-qff2026/hackathon.html)
and local `upstream/snu-qff2026-problem/problem.md` §2.3 confirm the comparator; formatter source is tprep/check.py:82.
Historical tail-performance and idle-capacity claims remain explicitly unverified. All swap actions belong to main.
