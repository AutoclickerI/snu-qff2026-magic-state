# GLOBAL complete

Positive stop rule met. Finalist: cand/global_r46_m14.qasm and matching JSON.
SHA256: cdaa719694c647348ca0fc5e3b311f1586df7f974ad993c0249fef18b9ee1b0e.
Exact all-orders L=3.761821654824e-5, A=0.5007854638217537, J_tau=-2.6867975273472643e-7.
Improvement over v36h: 5.365166765909933e-7; threshold margin: 3.651667659099471e-8.
Actual seed-0 fast_check at 1e6: gates_ok=True, passed=True; sampled loss=3.090481317541957e-5, acceptance=.50154; 3.5 seconds.
Judge receipt: logs/global_r46_m14.judge1e6.txt. Full summary: finalist.json.

R46 layout moves 15 ancilla roles, routes data in 10 hops, rebuilds A and BC, and realizes two flag-gap helpers. Final data [6,20,19,10,2,22,16]. Acceptance trades and known-state guards/identity pairs repair the initial loss. Measured q5 preparations plus advancing final A14 measurement from tick48 to47 close the target. Final circuit has49 native ticks and390 CX; no separate late X stabilizer check.

REPORT.md is90 physical lines, including a collapsed exhaustive HTML table of11473 unique priced QASM hashes. results.json is keyed by full SHA256. logs/final_audit.json verifies all saved hashes, metadata metrics, J values, table row count, report length, and judge receipt hash. logs/collection.json has no missing artifacts. Metadata cleanup removed inherited stale prices/check claims while preserving lineage.

Both hosts have no remaining GLOBAL search/evaluator processes. Stopped our jobs by numeric PID and observed exit. No submission, commit, push, subagent, GPU, or forbidden host was used; writes remained under GLOBAL. No further search is required under the task's positive stop rule. Read REPORT.md for decisions and measured versus inferred family costs; negative exhaustion or global optimality is not claimed.
