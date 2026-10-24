"""Bounded v35a c272 initialization/terminal-flag parity probe.

This leaves every quantum instruction unchanged. It replaces independent
c272=0 and terminal-flag=0 acceptance by tracked initialization parities.
The emitted candidate is experimental; no performance claim is assumed.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "audit/review6_tail"))
import frontend as f

source = ROOT / "quantumn_review8/work/lanes/MAIN/v35a"
text = source.with_suffix(".qasm").read_text()
metadata = json.loads(source.with_suffix(".json").read_text())
operations, detectors = f.parse_current(text)
assert detectors[19] == {31, 32, 33, 34, 260}
assert detectors[69] == {16}
assert detectors.count({272}) == 1

# Track a real sign flip of the newly measured X input through the remainder.
x, z, flipped_records = set(), {8}, set()
for operation in operations:
    if operation.time <= 37:
        continue
    if operation.kind == "CX":
        control, target = operation.qs
        if control in x:
            x.symmetric_difference_update({target})
        if target in z:
            z.symmetric_difference_update({control})
    elif operation.kind in {"M", "MX"}:
        if operation.qs[0] in (x if operation.kind == "M" else z):
            flipped_records.add(operation.bit)
    elif operation.kind in {"R", "RX"}:
        for qubit in operation.qs:
            x.discard(qubit)
            z.discard(qubit)
    elif operation.kind in {"T", "TDG"}:
        assert not x.intersection(operation.qs)
    else:
        raise ValueError(operation)

affected_rows = [index for index, row in enumerate(detectors)
                 if len(row & flipped_records) % 2]
assert flipped_records == {16, 29, 30, 32}
assert affected_rows == [19, 69]
output_z = sorted(z & set(metadata["data_qubits"]))
assert output_z == [3, 7, 20]
for index in affected_rows:
    detectors[index].symmetric_difference_update({272})
detectors.remove({272})
lines = [line for line in text.splitlines() if not line.startswith("// DETECTOR")]
lines.extend("// DETECTOR " + " ".join(f"c[{bit}]" for bit in sorted(row))
             for row in detectors)
candidate = HERE / "v35a_tracked_c272"
candidate.with_suffix(".qasm").write_text("\n".join(lines) + "\n")
metadata.update({
    "source_commit": "948dcfdca233baceee9759b90519a8589e00bd13",
    "variant": "tracked c272 initialization with A flag and B syndrome offsets",
    "source_qasm_sha256": hashlib.sha256(text.encode()).hexdigest(),
    "qasm_sha256": hashlib.sha256(candidate.with_suffix(".qasm").read_bytes()).hexdigest(),
    "scope": __doc__,
})
candidate.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")

f.DATA = metadata["data_qubits"]
model = f.make_model(operations, detectors)
engine = f.Engine(model)
ideal_acceptance, ideal_loss = engine.ntable(0, 0)
harmful = []
total = 0.0
for fault in model.faults:
    accepted, numerator = engine.ntable(fault["s"], fault["d"])
    contribution = 0.0 if numerator is None else fault["p"] * numerator[fault["e"]]
    total += contribution
    if contribution > 1e-15:
        harmful.append({"contribution": float(contribution), "label": fault["label"]})

result = {
    "source_commit": metadata["source_commit"],
    "source_qasm_sha256": metadata["source_qasm_sha256"],
    "candidate_qasm_sha256": hashlib.sha256(candidate.with_suffix(".qasm").read_bytes()).hexdigest(),
    "quantum_instruction_changes": 0,
    "exact_propagation": {
        "input_phase_fault": "Z8 after MX8 c272 at native tick37",
        "record_flips": sorted(flipped_records),
        "original_detector_rows_flipped": affected_rows,
        "output_Z_cells": output_z,
        "output_code_indices": [1, 2, 4],
        "equivalent_single_Z_code_index": 3,
        "stabilizer_difference": [1, 2, 3, 4],
    },
    "numerical_ideal_acceptance": float(ideal_acceptance),
    "numerical_ideal_loss": float(ideal_loss[0]),
    "numerical_first_order_loss": float(total),
    "harmful_single_fault_count": len(harmful),
    "harmful_single_examples": harmful[:10],
    "limitation": "Exact binary propagation; ideal and fault-order screen use floating arithmetic. Full finite-p acceptance/loss and official runtime still required.",
}
(HERE / "tracked_init_probe.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2), flush=True)
