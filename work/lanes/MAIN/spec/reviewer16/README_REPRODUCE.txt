quantumn optimization review — reproducibility bundle

Repository snapshot: AutoclickerI/quantumn
Pinned commit: 7f5a18cf386c850ad8a59e195edb14df087f6457
Official judge source inspected separately: snu-qff2026-problem commit 76fe47c.

The full Korean report is REPORT_KO.txt. This README describes
the supplied reproducibility artifacts. Copied quantumn_snapshot source
files are unmodified files from the pinned repository commit. The review
scripts, receipts and analysis notes are newly generated local review work.
STAGING_MANIFEST.json records SHA-256 hashes of the staged source and artifacts.

WORKING DIRECTORY AND DEPENDENCIES

Run every command below from the root of this extracted bundle. Tested with
Python 3.12 and a NumPy installation that provides numpy.bitwise_count.
NumPy is needed for the all-orders evaluator, the logical stabilizer probe,
and the graph-resource statevector verification. The rational certificate and
the small scheduling/terminal toy use Python's standard library.

For predictable runtime, set these environment variables before running:

  export OPENBLAS_NUM_THREADS=1
  export OMP_NUM_THREADS=1
  export MKL_NUM_THREADS=1

None of the following commands contacts a compute host, calls SSH, changes a
GitHub repository, or submits a contest entry. The copied MERGE sources are
included for inspection and AST extraction; do not execute their production
entry points. The supplied audit extracts only named pure functions from them.

1. CODE AUDIT AND BASELINE RECEIPT

  python quantumn_code_audit.py --output code_audit_reproduced.json

This executes the fixed-tau ranking counterexample, the output-metadata stem
collision counterexample, and the exact noiseless code-space witness. It also
checks the included v37d baseline receipt. Synthetic score/metadata examples
are labelled as such and are not claimed to be physical circuit improvements.

To recompute the baseline's complete 73 moments instead of loading the receipt:

  python quantumn_code_audit.py --recompute-baseline --output code_audit_recomputed.json

Reference: L=3.676346632406467e-5, A=0.5023547642585299. The 1-process run took
about 22 seconds in the review environment; runtime depends on the machine.
The evaluator writes a fresh v37d_canonical_sparse_result.json beside its code.
quantumn_code_audit_notes.txt contains scope, source locations and interpretation.

2. TERMINAL/SCHEDULING TOY AND LOGICAL-RESOURCE ENUMERATION

These scripts print JSON to stdout; redirect it to a receipt file:

  python architecture_probe.py > architecture_probe_reproduced.json
  python architecture_stabilizer_probe.py > architecture_stabilizer_reproduced.json

architecture_probe_results.json and architecture_probe_rechecked.json preserve
the review's recorded toy results. architecture_stabilizer_results.json records
the logical-level exhaustive stabilizer-resource check and the branchwise
Pauli-frame witness. These are scoped ideal/toy constructions, not full noisy
6x6 contest submissions. Read the scope and fault-response fields in each file.

3. BARRIER/SCHEDULE PROBES

The bundle includes the baseline plus the five actually priced variants:
remove_all, remove_11, remove_after_36, remove_after_40, remove_after_43.
schedule_probes/schedule_summary.json records the broader schedule-only scan;
schedule_probes/prices.json contains only the five variant all-orders prices.

To regenerate the schedule-only scan and all its candidate files:

  python audit_schedule.py > schedule_scan_reproduced.json

To reprice the five included variants (three local worker processes):

  python price_schedule_probes.py > schedule_prices_reproduced.jsonl

That command overwrites schedule_probes/prices.json and creates per-variant
logs and full evaluator receipts. Repricing is optional and was not repeated
when staging this bundle. Removing every barrier was worse and failed the
acceptance target; the tiny remove_11 loss difference is not presented as a
meaningful new performance improvement.

4. EXACT LOWER-BOUND CERTIFICATE

  python bounds_check/verify_certificate.py > bound_verification_reproduced.json

This independently checks all 2,187 assignments and 64 syndrome sectors for
the supplied certificate using integer arithmetic. It overwrites the local
bounds_check/verification.json with its verification result.

To regenerate the certificate and its summary before verifying them:

  python bounds_check/strengthened.py > bound_summary_reproduced.json
  python bounds_check/verify_certificate.py > bound_verification_reproduced.json

The certificate is a bound for its documented physical/noise assumptions,
not a demonstration that a full circuit attains the relaxation optimum.

5. DISCONNECTED-OUTPUT GRAPH-RESOURCE WITNESS

The included lc_hit.json is the final disconnected-output example. Reproduce
the search and then its constructive statevector verification in this order:

  python bounds_check/lc_disconnected_probe.py > lc_disconnected_reproduced.txt
  python bounds_check/lc_witness.py > lc_witness_reproduced.json

The second command also writes bounds_check/lc_witness.json and the legal-gate
resource snippet bounds_check/lc_c_resource.qasm. This snippet prepares only
a C resource; it is not a complete T-state submission. Outcome-dependent
physical Pauli byproducts still need incorporation into the enclosing square
instrument's detector records. All Clifford operations, measurements and
native noise must be priced in a full implementation.

Do not run lc_probe.py by itself after this sequence if you intend to retain
the final disconnected witness: its broader preliminary search may overwrite
lc_hit.json with an earlier example. It is included because the final graph
scripts import its graph operations. Intermediate lc_orbit.json and the stale
earlier lc_witness_run.log have intentionally not been included.

LIMITS OF THESE CHECKS

No official xtim Monte Carlo scoring run was performed in this review
environment. No new complete circuit is claimed to outperform v37d. The
checks distinguish mathematical identities, exact ideal-state witnesses,
reproduced all-orders expectation values, synthetic code counterexamples,
and untested full-circuit performance proposals. Read the report and each
receipt's explicit scope before interpreting a number as a contest result.

Exact finite-p tail comparison (perfect boundary, no physical preparation):
  python architecture_toy_allorders.py > architecture_toy_allorders_rerun.json
The script imports architecture_probe.py and suppresses its stdout internally.
This verifies the two relaxed tails only; it is not a full v37d improvement.

Full Korean report: REPORT_KO.txt
All numerical statements distinguish local probes from repository-reported campaigns.
