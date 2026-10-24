"""Bounded complete-guard removal experiments on pinned v35a.

No retiming is applied. Every variant removes a guard's initialization,
both CXs, readout, and singleton detector; subsequent resource operations
remain present and their physical noise is included by the evaluator.
"""
from pathlib import Path
import copy
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "audit/reaudit_evaluation/portable"))
import frontend as f
from circuit_io import emit

COMMIT = "948dcfdca233baceee9759b90519a8589e00bd13"
SOURCE = ROOT / "quantumn_review8/work/lanes/MAIN/v35a"
CASES = [
    ("drop_z0_h6", "RX", 6, (6, 0), 34, 35, 39, 40, "MX", 273),
    ("drop_x20_h19", "R", 19, (20, 19), 13, 18, 31, 32, "M", 274),
    ("drop_x7_h13", "R", 13, (7, 13), 19, 20, 23, 24, "M", 275),
    ("drop_x10_h11", "R", 11, (10, 11), 18, 19, 28, 29, "M", 276),
    ("drop_x4_h5", "R", 5, (4, 5), 17, 18, 32, 33, "M", 277),
]


def opkey(op):
    return op.kind, op.qs, op.time, op.bit


def verify(stem, meta):
    text = stem.with_suffix(".qasm").read_text()
    ops, rows = f.parse_current(text)
    f.DATA = meta["data_qubits"]
    model = f.make_model(ops, rows)
    engine = f.Engine(model)
    acceptance, loss_table = engine.ntable(0, 0)
    first_order = 0.0
    bad = 0
    for fault in model.faults:
        _, table = engine.ntable(fault["s"], fault["d"])
        contribution = 0.0 if table is None else fault["p"] * table[fault["e"]]
        first_order += contribution
        bad += contribution > 1e-15
    native_matches = all(
        step == op.time for op, steps in zip(ops, model.steps) for _, step in steps
    )
    grid = all(
        abs(op.qs[0] // 6 - op.qs[1] // 6) + abs(op.qs[0] % 6 - op.qs[1] % 6) == 1
        for op in ops if op.kind == "CX"
    )
    cert = {
        "qasm_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "ideal_acceptance": acceptance,
        "ideal_loss": float(loss_table[0]),
        "first_order_loss": float(first_order),
        "harmful_single_fault_count": int(bad),
        "native_schedule_matches": native_matches,
        "nearest_neighbor_CX": grid,
        "zero_frame": "// FRAME" not in text,
        "no_POSTSELECT": "// POSTSELECT" not in text,
        "CX": sum(op.kind == "CX" for op in ops),
        "native_ticks": max(op.time for op in ops) + 1,
        "instructions_in_QASM": sum(line.strip().endswith(";") for line in text.splitlines()),
        "measure_reset_count": sum(op.kind in {"R", "RX", "M", "MX"} for op in ops),
        "bytes": len(text.encode()),
        "physical_noise_scope": "All surviving operations, idle gaps, and terminal data idles; no channel ablations.",
    }
    assert acceptance > 1 - 1e-10 and abs(loss_table[0]) < 1e-10
    assert native_matches and grid
    assert cert["instructions_in_QASM"] <= 5000
    assert cert["measure_reset_count"] <= 1000 and cert["bytes"] <= 200_000
    meta["independent_verification"] = cert
    meta["qasm_sha256"] = cert["qasm_sha256"]
    meta["official_class_tested"] = False
    meta["official_runtime_tested"] = False
    stem.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
    native, _ = f.native_text(ops)
    stem.with_suffix(".native.stim").write_text(native)
    print(json.dumps({"name": stem.name, **cert}), flush=True)
    return cert


def main():
    text = SOURCE.with_suffix(".qasm").read_text()
    source_meta = json.loads(SOURCE.with_suffix(".json").read_text())
    base_meta = {
        "data_qubits": source_meta["data_qubits"],
        "source_commit": COMMIT,
        "source_path": "work/lanes/MAIN/v35a.qasm",
        "input_qasm_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_metadata_hash_is_stale": source_meta["qasm_sha256"] != hashlib.sha256(text.encode()).hexdigest(),
        "R": 44,
        "method": __doc__,
    }
    baseline = HERE / "v35a_control"
    baseline.with_suffix(".qasm").write_text(text)
    results = {baseline.name: verify(baseline, {**base_meta, "variant": "unchanged baseline"})}
    ops, detectors = f.parse_current(text)
    available = {opkey(op) for op in ops}
    for name, init_kind, helper, edge, init, first, second, meas, meas_kind, bit in CASES:
        removed = {
            (init_kind, (helper,), init, None),
            ("CX", edge, first, None),
            ("CX", edge, second, None),
            (meas_kind, (helper,), meas, bit),
        }
        assert removed <= available
        assert [row for row in detectors if bit in row] == [{bit}]
        new_ops = [copy.copy(op) for op in ops if opkey(op) not in removed]
        new_detectors = [set(row) for row in detectors if row != {bit}]
        stem = HERE / ("v35a_" + name)
        meta = {
            **base_meta,
            "variant": name,
            "removed_guard": {"helper": helper, "edge": edge, "init_tick": init,
                              "CX_ticks": [first, second], "measurement_tick": meas,
                              "measurement_bit": bit, "init_basis": init_kind, "measurement_basis": meas_kind},
        }
        emit(new_ops, new_detectors, stem, meta)
        results[stem.name] = verify(stem, meta)
    (HERE / "guard_certificates.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
