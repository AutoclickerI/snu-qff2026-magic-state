# qtools
Shared zero-frame all-orders evaluator for full-barrier circuits with at most 20 T gates.
Use the repository venv; restart long-running lanes when the source version changes.

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/work/tools"
.venv/bin/python -m qtools price work/lanes/MAIN/v37i --processes 1
.venv/bin/python -m qtools validate work/lanes/MAIN/v37i
.venv/bin/python -m qtools version
.venv/bin/python work/tools/pin_hosts.py
.venv/bin/python -m pytest -q work/tools/tests
```

```python
from qtools import write_stem, identity, price, validate, is_finalist
stem = write_stem(qasm_text, data_qubits, "work/tools/cache/candidates", "trial")
sha256, ordered_outputs = identity(stem)
result = price(stem, processes=1)   # InvalidCircuit carries the organizer's raw report
checked = validate(stem)          # adds 1e6-shot, one-process fast_check timing/gates
promote = is_finalist(checked, incumbent_checked)
```

Stem names include the QASM hash and ordered physical outputs. Metadata is immutable.
Cache keys include full QASM SHA256, output order, and every qtools Python source hash.
`seconds` is call wall time; `evaluation_seconds` retains miss time on cache hits.
The cache and basis updates use advisory file locks and atomic replacement on one host.
`bases.json` merges MAIN/MERGE programs plus EARLIER's route bases; only width >12 trains.
Newly trained programs are saved there; basis metadata identifies the actual coordinates.
Bases affect contraction order and roundoff, not the mathematical expectation.
Regression tolerances: |ΔL|≤1e-15 and |ΔA|≤1e-12 absolute (main session's criterion).
`processes` includes the caller; use independent processes for concurrent lane searches.
Finalists require lower exact L, exact A≥0.5002, raw validity, judge gates, positive
expected-key delta, and judge time ≤20 s. Compare timings on the same host/minutes.
`pin_hosts.py` checks owl, tom, jerry, hippo, sunfish sequentially and excludes caches.
See REPORT.md and evidence/ for measured precision, speed, source diffs and host receipts.
