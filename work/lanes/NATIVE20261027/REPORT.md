# Rebuilt logical-check architecture — 2026-10-27

## Result

No native finalist. A new, reproducible abstract architecture shares GHZ hook
checks with the existing Steane precheck readouts. It removes a substantial
accepted fault-pair term, but the completed nearest-neighbor control fails the
acceptance requirement. None of these results establishes SOTA.

| Saved design | Geometry | CX | Native ticks | Exact loss | Acceptance |
|---|---|---:|---:|---:|---:|
| Fresh encoded injection, full precheck, two GHZ checks, square ending | Ideal connectivity | 127 | 20 | 5.21029676124e-5 | 0.720573115409 |
| Same circuit, second GHZ check delayed four ticks | Ideal connectivity | 127 | 20 | 4.67938718912e-5 | 0.720523089576 |
| GHZ flags extracted through precheck readouts; final A/B roles exchanged | Ideal connectivity | 139 | 21 | **3.26709931735e-5** | **0.685301817118** |
| Seven native terminal squares plus exact bridge synthesis of the preceding circuit | 6×6 grid | 724 | 391 | **0.182684182153** | **0.000334707071** |

The abstract joint-flag result is worse than the repository's documented DEEP
result, 2.7185e-5. It is useful because the generator and measurement contract
are present and reproducible. The documented DEEP circuit was absent from the
checked repository snapshot.

## What changed physically

`build_joint_flags` prepares an encoded T state, performs both Steane prechecks,
and measures the logical magic-state axis twice using seven-qubit GHZ states.
The two measurements share the transversal T/T† basis changes (15 T gates in
total, including injection).

Three two-body Z parities of each GHZ state are copied into the precheck blocks
after those blocks have interacted with the data. The first block is already
read in Z. A transversal H on the second block changes its pending X readout
to Z, permitting the second set of parity checks to use the same measurement
records. No separate flag qubits or extra measurement records are added.
The two precheck blocks exchange their roles in the final resource preparation;
the block released earlier prepares the verified terminal B resource.

The raw noiseless checks pass: all six output stabilizers equal +1 to numerical
precision, accepted infidelity is about 1.1e-16, and rotation rank is five.

## Why this change helps

`pairs.py` enumerates distinct-channel fault pairs and uses exact non-Clifford
conditional-state tables. Idle probabilities are linearized only for this
Taylor-coefficient calculation. The all-orders prices above use the full
noise channels.

| Circuit | First-order coefficient | Second-order coefficient |
|---|---:|---:|
| Unverified GHZ control with the second check delayed | 2.89e-16 (roundoff) | 43.4166666667 |
| Joint GHZ flags | 2.89e-16 (roundoff) | 28.06 |

The control's cat-preparation faults paired with terminal-resource and
terminal-round faults contribute 13.1633333333 p². Flag sharing removes almost
all of those pairs. The complete second-order reduction is 15.3566666667 p².
Higher orders remain material: the joint circuit's full loss is 3.2671e-5,
not its second-order estimate 2.806e-5.

## Native control and its precise limitation

`native_control.py` jointly chooses seven terminal tiles, code labels, tile
orientations, and helper positions. It minimizes precursor bridge CX cost and
keeps both final transversal CX layers nearest-neighbor. Earlier nonlocal CXs
are implemented by exact bridge circuits that restore arbitrary intermediate
quantum states. Disjoint bridge supports run in parallel. The bridge identities
are checked as binary linear maps, including unknown intermediate inputs.

The resulting saved grid circuit passes adjacency and raw state correctness,
but 391 ticks and 724 CX gates destroy acceptance. The physical routes also
introduce fault paths absent from the abstract circuit. This is a measured
failure of this compiler and placement family, not a geometry impossibility
proof or a rejection of shared GHZ flags. A useful native design must choose
encoders, cat trees, cell lifetimes, and their terminal interfaces together.

An initial compiler control overlapped two bridge supports and was rejected
by raw correctness; the compiler was fixed before generating the reported
seed-612 circuit. That rejected control is excluded from the selected files.

## Reproduce

Run from the repository root after the pinned dependency setup:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/NATIVE20261027/rebuild.py --joint-flags --round 18 --cat2-time 12 --price
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/NATIVE20261027/pairs.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/NATIVE20261027/pairs.py --joint-flags
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 .venv/bin/python work/lanes/NATIVE20261027/native_control.py --seed 612 --steps 30000 --price
```

Abstract pricing temporarily relaxes adjacency inside that Python process,
explicitly labels the result `grid_free`, restores the original function, and
does not write to the shared grid-valid price cache. Judge sources are never
edited. The native control uses the normal grid-valid evaluator.

Outcome: measured abstract mechanism; measured native compiler failure.
All experiment processes have exited. `selected_files.json` lists the handoff.
