# MERGE — pass 5 on v37h

Status: running. wide_r6 completed.
Baseline reproduced: L=3.6119549914941787e-05, A=0.5015489333258328; six raw output stabilizers +1.
Current selected: L=3.605846790297287e-05, A=0.50021418491203051; SHA256 `a449e1a694c1075595337f356865ab61dd26ce545de5670a8dc07788926f7cd6`.
Gain from v37h: 6.10820119689e-08; finalist threshold >3e-8; exact acceptance floor 0.5002.
Full receipts: res37h/*.jsonl (22506); saved circuits v37h/; new artifacts cand/merge5_*.
Detector surrogate latest: {"measurements": 85, "detector_rank": 67, "kernel_dimension": 73, "extra": [[3], [373], [368], [281], [312], [352]], "surrogate": "T/TDG -> I, 20000 noiseless samples; all proposals independently exact-validated"}
Every reset/RX has a herald attempt; busy cells use predecessor cascades and CP-SAT commuting reschedules (at most eight moved CX/M units, +/-2 ticks). Echo/check ejections unlock otherwise blocked heralds. Initial preparations get a prepended tick.
Redundant repeated preparations also allow replacing the later preparation with a matching measurement of the earlier one.
Every detector subset (up to eight residual directions) and every herald/detector pair is exact-priced without second-order pruning.
Pass-4 moves, historical ejections and signature pairs are retained. Funding uses up to four buyers and preserves the full measured buyer and seed Pareto fronts; intermediate frontiers are not truncated.
Selection: minimum exact loss among feasible judge-valid builds. Tau follows the current circuit. Judge uses 1e6 shots, one process, paired with v37h on hippo; time penalty is reported for main-session expected-key selection.
Reviewer screens located at MAIN/spec/reviewer17/results/ (the supplied unz path was stale); no reviewer code executed.
Decisions apply to this pass only; no standing rule changed. No submission, commit, push, subagent or other-lane write.
Checked: saved QASM/output identities, all-orders raw code-space assertion and exact acceptance. Final completion and any unverified scope are stated below.
