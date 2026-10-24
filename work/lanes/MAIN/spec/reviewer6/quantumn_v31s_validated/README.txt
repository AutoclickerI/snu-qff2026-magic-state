QUANTUMN V31S — VALIDATED A DECODER
===================================

Recommended circuit: candidate/v31s_a_decode.qasm
Consolidated metadata: candidate/v31s_a_decode.json
QASM SHA256: 017b77391a55e896c1f8c51f700dbd3e68515e22d2da35c50d177bb1933464e0
Data qubits, in logical code order: [0,20,7,10,3,22,21]

Independent all-orders expected loss: 4.948545794706148e-05
Independent expected acceptance: 0.5366494669060742
191 CX; native depth48. Improvement over pinned v31s: 10.96197270%.

OFFICIAL CHECK, COMPLETED:
  shots=100000000, seed=0, p=.001
  score=4.985904918530546e-05
  SEM=8.360255733379658e-07
  acceptance=0.53661272
  local check time=244.824509 seconds
  format/class/correctness/acceptance: ALL PASS
  receipt: audit/review6_validation/v31s_a_decode.official_100000000_0.json

Read REPORT_KO.txt for the findings and SUMMARY.json for machine-readable
metrics. Official MC scores and independent expectations are different
quantities. Small-shot zero-error observations are not zero-loss claims.
Original lane metadata is an earlier snapshot; candidate/ is authoritative
for the completed official-validation status. Original receipts are unchanged.

REPRODUCE FROM THE EXTRACTED TOP DIRECTORY
----------------------------------------
Python3.12, Linux x86_64. The exact xtim wheel is pinned by SHA256.

    python3.12 -m venv .venv
    .venv/bin/python -m pip install -r audit/review6_validation/requirements.lock.txt

Independent full-order score (73 moments including acceptance):

    OPENBLAS_NUM_THREADS=1 .venv/bin/python audit/reaudit_evaluation/portable/sparse_walsh.py candidate/v31s_a_decode 72 canonical

The evaluator writes its result beside sparse_walsh.py. It performs no
Monte Carlo and no fault-order truncation. The reported sparse-cutoff
omission bound excludes arbitrary floating-point roundoff.

Official 1e6-shot validity/speed check:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python audit/review6_validation/run_official.py 1000000 0 candidate/v31s_a_decode 017b77391a55e896c1f8c51f700dbd3e68515e22d2da35c50d177bb1933464e0

Official contest-setting check (about4 minutes on this environment):

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python audit/review6_validation/run_official.py 100000000 0 candidate/v31s_a_decode 017b77391a55e896c1f8c51f700dbd3e68515e22d2da35c50d177bb1933464e0

run_official.py calls the unchanged official tprep.check, with timer wrappers
that record stages without altering algorithms or scores. Its default target
in this bundle is the recommended candidate. No judge mutation, special
simulator switch, custom noise, uncharged gate, or nonzero logical frame
is used. No submission command is included or executed.

REGENERATION AND EXPERIMENTS
---------------------------
    .venv/bin/python audit/review6_architecture/port_a_decoder.py
    .venv/bin/python audit/review6_architecture/port_certificate.py

The source controls and ports use quantumn_review6/work/lanes/MAIN inputs.
The other scripts and negative tests are documented in their lane README
or REPORT. Commands can overwrite generated same-name files and receipts;
preserve a clean archive when rerunning. The review5 backend is included
only for the equivalent Bell-probe script and prior SX runtime comparison.

The A+SX family is included as physical-model research evidence. It has
lower expected loss, but its measured official noisy sampling remains slow.
It is not the current practical recommendation. See review6_tail/XTIM_AUDIT.

PROVENANCE
----------
Pinned user repository: AutoclickerI/quantumn @ abf26aa98bede59bb07f7da838dd1b3a3fdf76f0
Official judge: SNUQuantums/snu-qff2026-problem @ 76fe47c0324f1c1f8b72a7d55af200e88043b522
Official tprep version: 3.0.3
Source hashes, exact dependencies and MIT license are included under
audit/review6_validation. Evaluator ancestry is documented in the tail README.
SHA256SUMS.json covers every bundled file except itself.
