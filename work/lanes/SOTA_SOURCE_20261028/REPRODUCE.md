# Reproduction

Run commands from the quantumn repository root. Use the project `.venv/bin/python`, Python 3.12.14, `PYTHONPATH=work/tools`, and `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`. The source and compact-circuit builders import the existing repository helpers named in `publish_manifest.json`; the manifest records their SHA-256 hashes. The qtools evaluator version in the exact receipts is `94d0bfed2b6ff678c667dd24a5e57a249e01da0febc72bec4adf0d987fb9c83f`. The local snapshot did not expose a resolvable git HEAD, so no repository commit hash is asserted.

## Gao circuit and measurements

```bash
export PYTHONPATH=work/tools
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/gao/build.py
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/gao/parallel.py
TIGHT=1 .venv/bin/python work/lanes/SOTA_SOURCE_20261028/gao/retime.py
TIGHT=1 LATE=1 .venv/bin/python work/lanes/SOTA_SOURCE_20261028/gao/retime.py
PYTHONPATH=work/tools .venv/bin/python work/lanes/PREFIX2_20261027/pairs.py \
  work/lanes/SOTA_SOURCE_20261028/gao/gao_abstract_retimed_late \
  work/lanes/SOTA_SOURCE_20261028/gao/late_pairs.reproduced.json
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/gauge_frames.py
```

The serial and parallel generators emit complete abstract circuits, check raw Steane correctness, scan all single faults and evaluate the full all-orders loss. `retime.py` starts from the parallel QASM and retains all operations and detector bits. It allows only pairwise commuting changes, enforces one operation per physical wire per clock, and with `TIGHT=1` keeps the final two transversal layers and reads aligned. Its makespan result is solver-optimal within that DAG. With `LATE=1`, a 60-second weighted solve favors late reset and phase operations while prioritizing minimum depth; because that solve is time-limited, a rerun can yield a different feasible schedule. The selected QASM and exact receipt are retained with SHA-256 in the manifest. All Gao circuits deliberately relax adjacency and are not submissions.

`gauge_frames.py` is a separate exact mathematical calculation on the normalized Steane magic state. Its uniform-frame and no-record-dependent-recovery assumptions are included in its JSON output; it is not a gate-level simulation of IBM's complete gauging circuit.

## Actual source boundaries

```bash
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/reflected_route_early.py
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/reflected_seven.py
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/reflected_six.py
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/tile_route.py
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/tile_route_six.py
```

The reflected four-square source retimes one deterministic source measurement and routes two data cells, while the six/seven-square boundaries use explicit additional native coherent moves. These outputs are valid source boundaries rather than full scored circuits. Each builder checks raw correctness and writes per-cell releases, source record identities, route operations, output order and a QASM hash. The original and contracted sources are shared project dependencies in the manifest.

Geometry scripts produce native tile witnesses and bounds, not preparation circuits. A bounded solver can return a different equally valid witness; use the saved JSONs to reproduce the reported roles. The 6/7-square models that allow both A and B/C to borrow free cells independently do not guarantee those borrowed cells can be used simultaneously.

## Ideal-resource headroom diagnostics

```bash
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/unmoved_six_headroom.py
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/seven_headroom.py
```

Each script uses at most two processes. These two experiments use the actual noisy source, terminal gates, measurements, and all real idle time. They insert explicitly marked synthetic encoder clocks, zero resource-preparation noise only, and remove only those synthetic clocks from idle channels. Identity gates model otherwise collapsed real all-idle clocks; each carries the same depolarizing channel as the idle it replaces. The script asserts the scheduler's physical clock for every operation. These nonlocal, ideal-resource circuits are counterfactuals and cannot be submitted.

## Full-noise teleportation control

```bash
.venv/bin/python work/lanes/SOTA_SOURCE_20261028/teleport_probe.py
```

This uses the lane-local affine-frame evaluator with an abstract raw-state check that bypasses adjacency only. The destination encoder and all other operations are noisy. It is not a native submission; the full receipt includes the harmful single-fault labels. See `TELEPORT.md`.

The generated exact results and all-order omission intervals are in the manifest-selected JSON receipts. Expected losses, acceptance, source definitions and the limits of counterfactual interpretation are in `REPORT.md` and `HEADROOM.md`.
