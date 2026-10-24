# Final repository update

The delivery-time HEAD check at 2026-10-24 18:24 UTC found a new commit, `e31cec14e20f5d9fec9da759ef0d61cd4a5358ab`, authored at 18:23:37 UTC. It adds exactly three files relative to the analysis pin `42afa8ff01c3999444336f5bb2fe473c1475d6f4`:

- `work/submissions/v36b_r580.qasm`
- `work/submissions/v36b_r580.json`
- `work/receipts/seq_v36b_r580.txt`

All three are included under `latest_update/`. No v36c, sparse evaluator, competition rule, or current planning file changed in this delta. The report's independently evaluated baseline remains the exact v36c bytes at the analysis pin.

The new receipt reports a one-hundred-million-shot seed-0 score of **3.8779486220169754e-5**, acceptance **0.5014249**, and 211 two-qubit gates, with the official checks marked PASS. Its JSON describes the candidate as v36b reordered with RNG 580. This is a repository-reported selected sample, not a new expected-loss result measured in this review.

`latest_update/check_reorder.py` verifies that the original v36b and the new submission have the same per-wire instruction order, barriers and measurement destinations, directive multiset, output order, native scheduled instruction multiset, and physical idle intervals using the pinned official converter/scheduler. The insertion index of an idle-noise instruction may change in serialization; it is not part of the physical interval comparison. `latest_update/reorder_equivalence.json` records the result.

This update changes the latest recorded candidate score but does not invalidate the ten implementation tasks or the v36c baseline. New sampled minima should continue to be reported separately from expected physical loss.

Sources: [commit delta](https://github.com/AutoclickerI/quantumn/compare/42afa8ff01c3999444336f5bb2fe473c1475d6f4...e31cec14e20f5d9fec9da759ef0d61cd4a5358ab), [receipt](https://github.com/AutoclickerI/quantumn/blob/e31cec14e20f5d9fec9da759ef0d61cd4a5358ab/work/receipts/seq_v36b_r580.txt).
