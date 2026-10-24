QUANTUMN — V35A REVIEW, RULES, AND TEN OPTIMIZATION DIRECTIONS
=============================================================

Read REPORT_KO.txt for the self-contained Korean report and SUMMARY.json
for machine-readable results. The circuit snapshot is
AutoclickerI/quantumn @ 948dcfdca233baceee9759b90519a8589e00bd13.
The final source refresh also read 126b1df310a2a138a181d8dda0ae6d11fb94d236; its only change is one
WAITPROT status row in PLAN. The v35a QASM is unchanged.

BASELINE, NOT A NEWLY IMPROVED CIRCUIT
-----------------------------------
baseline/v35a.qasm is the user's original current v35a, unchanged.
Actual SHA256: b606bd3902d28000e0ee073fc50a7c0870aaa1f2e1ab8947fdb7fd70c762218e
Data qubits in code order: [0,20,7,10,3,22,21]
206 CX, 47 native ticks, R44.
All-orders expected loss: 4.393527676042078e-05
Expected acceptance: 0.5012369386242203

Completed official check: 100000000 shots, seed0, STANDARD p=.001.
All four gates PASS. Score 4.499822441045316e-05,
SEM 8.175175781417765e-07, A 0.501242.
Local check time: 244.640150 seconds.
The original JSON had an inherited hash; FINDINGS said48ticks. The exact
QASM and official parser establish the hash and47ticks above. Original
source metadata is retained in quantumn_review8/ for provenance.

The five whole-guard removals and two C readout changes are fully priced
research variants. None directly improves the baseline. They identify
specific acceptance budget trades and reject a costly extra terminal tick.
Only the baseline has a full100m official check in review8. Variant
certificates identify their independent verification scope explicitly.

REPRODUCTION FROM THIS DIRECTORY
-------------------------------
Python3.12 / Linux x86_64. The xtim wheel and dependencies are exactly pinned.

    python3.12 -m venv .venv
    .venv/bin/python -m pip install -r audit/review8_validation/requirements.lock.txt

Full modeled expectation,73moments (no Monte Carlo):

    OPENBLAS_NUM_THREADS=1 .venv/bin/python audit/reaudit_evaluation/portable/sparse_walsh.py baseline/v35a 72 canonical

Official full-setting validation:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python audit/review8_validation/run_official.py 100000000 0 baseline/v35a b606bd3902d28000e0ee073fc50a7c0870aaa1f2e1ab8947fdb7fd70c762218e

Use1000000 instead of100000000 for the short validity/speed check. The runner
uses unchanged official tprep.check; timer wrappers do not change algorithms
or seeds. Its bundled default target is baseline/v35a. Source hashes, license
and dependency lock are in audit/review8_validation/.

Bounded physical study:

    OPENBLAS_NUM_THREADS=1 .venv/bin/python audit/review8_architecture/build_guards.py
    OPENBLAS_NUM_THREADS=1 .venv/bin/python audit/review8_architecture/build_readout_exchange.py

See each script's entry point and lane REPORT.txt for pricing commands.
Scripts may overwrite their generated same-name files; preserve the original
archive before rerunning. Sparse evaluator outputs are written beside the
evaluator unless the lane wrapper copies them to its own directory.

CONTENTS AND PROOF SCOPES
------------------------
review8_architecture: v35a physical variants, full73moment prices, certificates.
review8_objective: v35a A-encoder and tracked-initialization analysis.
review8_policy: exact all-orders two-record oracle; negative results retained.
review8_rules: unchanged rule contracts, stale assumptions, source availability.
review8_screen: v35a target-check necessary class screen and stratum probabilities.
review8_validation: completed official receipts and exact official sources.

review7 directories retain fresh general-rule witnesses and prior exact
certificates. Their v32p recommendation is SUPERSEDED by v35a and is not
the current recommendation. Full-target AND/biased-selection witnesses
establish legal expressiveness, not low loss. The star-to-triangle example
establishes a four-qubit resource transformation, not full target preparation.
review5/review6 support files retain original paths for reproducible imports.
subthreshold_bound contains the universal terminal-noise proof and exact
rational certificate under the inspected STANDARD model.

The file archive includes the complete report, algorithms and negative tests.
It does not include credentials, virtual environments, wheels, temporary
progress snapshots, or a submission command. SHA256SUMS.json covers every
bundled file except itself. No remote changes were performed.
