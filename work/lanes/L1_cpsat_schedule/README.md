# Reproduce L1

Run only from this lane so xtim caches stay here. Existing project modules are imported read-only; disable bytecode writes.

```bash
cd /home/jihoon/competitions/quantumn/work/lanes/L1_cpsat_schedule
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
QFF_PYTHON=/home/jihoon/competitions/quantumn/.venv/bin/python
```

Recheck the delivered five full circuits, with the explicitly documented numerical-c1 exception:

```bash
"$QFF_PYTHON" verify.py top5_schedules.json --count 5 --procs 8 --accept-roundoff --tag reproduced
```

Omit `--accept-roundoff` to enforce literal `c1 == 0`; the reference also fails that test by floating-point residue. Both strict and numerical results remain in the receipt.

Rebuild through the original builder:

```python
from common import HERE
import batch_score
circuit, data_qubits = batch_score.make({
    "kind": "gen2", "file": str(HERE / "top5_schedules.json"),
    "idx": 0, "lazy": True,
})
```

Optimize the complete objective within each delivered gate order (LMAX 9):

```bash
"$QFF_PYTHON" refine.py top5_schedules.json --lmax 9 --workers 8 --seconds 60 --tag reproduced_orders
```

Enumerate a schedule neighborhood with the exact Stim proxy as the ranking oracle:

```bash
"$QFF_PYTHON" neighborhood.py --file best_proxy.json --radius 4 --lmax 8 --strong-validity --seconds 900 --tag reproduced_neighborhood
```

The unrestricted enumerator uses `--radius 0`; `--orientation 011` fixes readout orientation. It uses one worker. Coordinate concurrent invocations to keep the aggregate at eight CPU workers or fewer.

`global_search.py` provides an unrestricted tail-surrogate candidate generator with Stim rejection and order no-goods; it is not a complete-proxy optimizer. `ordered_objective.py` implements the complete finite-noise proxy and `refine.py` solves it using probability tables and integer products. `deliver.py` rebuilds the selected measured circuits and audits their hashes before generating the report and exports.
