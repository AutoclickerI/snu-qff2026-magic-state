# PRE scheduling lane

Generated 40 distinct greedy schedules (forward/reverse, ordered/commuting) and 400 local/LNS proposals. Only cultivation operations 0..136 were mutable; v12 final-cycle operations 137..183 and their relative timing were fixed. All gates, data-qubit indices and detectors are unchanged. Metadata assertions verify the fixed suffix.

All 440 proposals were scored with exact2.Eval/run. Search batches precompute identical Engine XOR-class tables with batch_n, then use unmodified run pair/probability accounting. Baseline loss2 reproduced as 1.1219494706696269e-4, A1 0.370303793945133. All retained candidates were independently rerun with the uncached exact2.py CLI and pass actual tprep.check with 1e6 shots.

| Candidate | CX | Exact loss2 | Δ vs v12 | First order | Total A1 | exp(-A1) | Check |
|---|---:|---:|---:|---:|---:|---:|---|
| alap_ordered | 115 | 0.00011402183477 | +1.6283% | 4.9217e-19 | 0.412339825 | 0.662099240 | PASS |
| alap_commuting | 115 | 0.000111699257841 | -0.4418% | 4.9032e-19 | 0.381662640 | 0.682725338 | PASS |
| alap_best | 115 | 0.000111345943883 | -0.7567% | -3.1409e-18 | 0.374233218 | 0.687816482 | PASS |

alap_best is source alap_lns_0387, selected by minimum A1 among loss2 ties within 1e-15. Its exact loss is 0.7567% lower than v12 for ΔA1=0.003929424; the earlier raw-float winner spent more A1 for a difference of only ~1e-19 in the objective. The small negative first-order value is floating-point roundoff, not physical negative infidelity.

Native pre-stage end step and loss/A1 decomposition are delegated to main measure.py because empty scheduler layers collapse in emitted barriers. The requested 1e8-shot seeds 0, 1000, 2000 are delegated to main. No MC claim is made from the 1e6-shot validation.

Files: alap_{ordered,commuting,best}.qasm/.json, .exact.json/.exact.log. Search artifacts are under alap_search/. Search scripts are alap_search.py and alap_validate.py.
