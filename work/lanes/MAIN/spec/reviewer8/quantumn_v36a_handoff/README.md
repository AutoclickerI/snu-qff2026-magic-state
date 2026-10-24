# quantumn v36a implementation handoff

Read REPORT_KO.md first. It contains the full audit, ten candidate methodologies, rule distinctions, mathematical qualifications, and first/stop experiments.

## Pinned inputs

- quantumn: e438fb60c3da53584fc336fda76bd1fe46a5a6e2
- official judge: 76fe47c0324f1c1f8b72a7d55af200e88043b522
- v36a QASM SHA-256: 8faa1fa93b210c16c5dd9ec2fb8b31057c036f6ec657a33f56c9defda65795cf
- Independently reproduced expected loss: 4.1460519583256424e-5
- Independently reproduced acceptance: 0.500832514460435
- 207 CX, 47 native ticks, 68 detector rows, 538 effective noise channels.
- This package does not claim a new physical circuit with lower expected loss.
- The detector-basis and POSTSELECT variants preserve the accepted physical result.

## Start here

1. Read IMPLEMENTATION_AGENT.md and TASKS.json.
2. Inspect EVIDENCE_SUMMARY.json and audit/review9_resumed/v36a_adjoint_72.json.
3. Verify CHECKSUMS.sha256 with tools/verify_bundle.py.
4. Use the pinned original circuit as control; rebase every physical change on the actual current incumbent.
5. If the upstream repository has advanced, rerun the baseline and ledger before using these prices.

## Reproduction

Python 3.12 on Linux x86-64 was used. Create an isolated environment and install requirements.lock.txt. The exact official xtim wheel URL and SHA-256 are in that file. The wheel is not bundled.

Run from this extracted directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python tools/verify_bundle.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python audit/review9_resumed/evaluator/sparse_walsh.py "$(pwd)/audit/review9_resumed/inputs/v36a" 72 canonical 8
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python audit/review9_resumed/adjoint_ablation.py "$(pwd)/audit/review9_resumed/inputs/v36a" 72
.venv/bin/python audit/review9_resumed/run_official.py 1000000 0 audit/review9_resumed/inputs/v36a
.venv/bin/python audit/review9_resumed/search_reachability_certificate.py
.venv/bin/python tools/regenerate_annotations.py
```

Reduce the evaluator worker count to fit the host's available compute budget. The scripts run local validation only. No submission, remote worker launch, git push, or credential is included.

## Evidence scope

- v36a and v35b all-orders results are independently reproduced.
- Official receipts use 1,000,000 shots: enough for validity checks, not precision ranking.
- v36a all-channel adjoint completed 73 moments, including 12 direct counterfactual checks.
- The adjoint algorithm already existed in the older v30f audit. This package ports it to v36a and supplies a complete current ledger; it is not claimed as a newly invented algorithm.
- Public ST2 restrictions are reproduced from actual AST-extracted committed functions. The newer documented pop35/knapsack engine was not present in the accessible GitHub snapshot.
- No runtime speedup is established by the detector basis test. The original and the two annotation variants passed the official checker and produced the same recorded score/acceptance in the recorded run.
- The archived v35b time-cut census and interrupted derivative experiment described during the review are not supplied as newly recovered files. Their limited findings are explicitly historical in the report. Current numeric conclusions use the actual receipts included here.
- Source files under reference/ are a selected pinned snapshot, not a full repository clone.
