# TOOLS — verified handoff

Completed entirely within `work/tools`; no submissions, commits, pushes or lane edits.
Final evaluator: `94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f`.
Full file hashes: [manifest.json](manifest.json). Usage: [README.md](README.md) (36 lines).

## Measurements
Serial, one-process sunfish runs; cold = unchanged MAIN evaluator with its original bases;
warm = shared package, cache bypassed, including organizer raw correctness.

| Circuit | Cold seconds | Warm seconds | Speedup | Warm L | Warm A |
|---|---:|---:|---:|---:|---:|
| v37h | 77.646 | 3.384 | 22.94× | 3.611954991483112e-5 | 0.5015489333258327 |
| v37i | 447.401 | 2.728 | 164.00× | 3.591182404106096e-5 | 0.5003576309837842 |
| v37i minus DETECTOR c[309] | — | 2.765 | — | 3.591950797809682e-5 | 0.5014939046476842 |

Warm/cold absolute differences: v37h ΔL=1.1066993675645787e-16, ΔA=1.1102230246251565e-16;
v37i ΔL=6.776263578034403e-21, ΔA=1.1102230246251565e-16.
Versus the brief's reference losses, differences are 1.107e-16 and 1.110e-16 respectively.
These pass the main session's corrected |ΔL|≤1e-15, |ΔA|≤1e-12 absolute criteria; the fast v37h
basis does **not** satisfy the original 1e-15 relative loss criterion (relative drift 3.06e-12).
Cache hits: 0.782/0.752 ms. Both warm circuits have width 10 and require no training.
Judge `gates_ok=True` for both, at 1e6 shots/one process: 1.794/1.782 s, same host/minutes.
v37i's sampled A was below 0.5; exact A passes 0.5002, as the policy requires.
Evidence: [benchmark_sunfish.json](evidence/benchmark_sunfish.json).

## Checks and decisions
- **11 tests passed** with `.venv/bin/python -m pytest -q work/tools/tests` (109.90 s on loaded zebra).
  Tests cover both reference prices and independent cold controls, ordered-output identity, actual cache
  misses across QASM/output/version keys, source-hash changes, concurrent cache/stem/registry writers,
  promotion policy, empty Fourier support, and unsupported parser syntax.
- The H·T⁴·H regression has decoded noiseless loss zero, negative raw stabilizers, and is rejected by `price`.
  Both good circuits pass the organizer's exact check with all six stabilizers +1 within its tolerance.
- Copied MAIN's evaluator and all local imports; the only MERGE evaluator diff refines the cheapest replay
  once. EARLIER imports MAIN and adds empty-support/raw checks in its adapters. Source hashes/diff and
  separately executed MAIN/MERGE results are retained in `evidence/`; losses agree within corrected limits.
- The named `basis_warm.json` files omit the fastest live bases. Imported MERGE's pass-4 and circuit-specific
  v37h programs and EARLIER's route programs, yielding 12 distinct registry entries. This fixes the actual
  bottleneck without changing contraction arithmetic. A selector-cost probe did not reliably rank runtimes;
  that proposed optimizer change was not adopted. Threshold 12 follows MERGE's active configuration.
- Every saved basis is replayed; newly trained programs use a locked atomic registry update. Result keys
  include full QASM SHA256, ordered outputs and all package source hashes. Basis changes do not invalidate
  mathematical results. Per-key locks deduplicate concurrent computations; writes use fsync and atomic rename.
- Source edits require a worker restart; `seconds` measures the current call, `evaluation_seconds` the miss.
  The process budget includes the caller. Unsupported QASM syntax is rejected before it can be mispriced.
- Final source manifests match on owl (Docker), tom, jerry, hippo and sunfish: [hosts.json](evidence/hosts.json).
  Pinning is sequential and uses plain `ssh -q` with rsync credential/cache exclusions, per the correction.
- Zebra exceeded 64 cores of load (peak observed ≈125); numerical jobs were reduced to one process.
  Only short concurrency tests used two workers. Sunfish benchmarks used one numerical process; tom,
  also overloaded during pinning, received only the lightweight manifest check. No other jobs were signaled.

## Scope and remaining limits
Verified for the supplied v37h/v37i circuits and the recorded single edit; speed varies with host load
and circuit width. Cold/warm measurements share a host but were sequential, not controlled load trials.
The evaluator retains MAIN's numerical kernel cutoff (reported omission bound ≈3.7e-14, excluding roundoff).
Scope remains full barriers, zero frame/no POSTSELECT, supported H/T/Tdg/CX/reset/measure/id gates, ≤20 T,
and one QASM statement per line. Tests of general architectures and multi-host cache sharing are not claimed.
Lanes can adopt the package at their next restart; their running copies were deliberately left untouched.
