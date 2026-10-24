"""Two bounded C-readout tests on v35a with every physical cost charged.

1. Exchange the two q28/q29 readout copies for CX28->29 in their tick 45.
2. Retain both copies and append CX28->29 at 46, delaying MZs to 47.

The second test explicitly prices its additional terminal data-idle tick.
Both invertibly substitute old c26 = new c26 XOR c27 in retained detectors.
"""
from pathlib import Path
import copy
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_guards import ROOT, f, emit, verify, opkey
from judge_subset.noise import noise_blocks


def build(mode):
    source = HERE / "v35a_control"
    meta = json.loads(source.with_suffix(".json").read_text())
    meta = {key: value for key, value in meta.items() if key not in
            {"independent_verification", "qasm_sha256", "official_class_tested", "official_runtime_tested"}}
    ops, detectors = f.parse_current(source.with_suffix(".qasm").read_text())
    original_rows = [set(row) for row in detectors]
    if mode == "exchange_copies":
        removed = {
            ("R", (34,), 44, None), ("R", (35,), 44, None),
            ("CX", (28, 34), 45, None), ("CX", (29, 35), 45, None),
            ("M", (34,), 46, 268), ("M", (35,), 46, 267),
        }
        assert removed <= {opkey(op) for op in ops}
        assert [row for row in detectors if 267 in row or 268 in row] == [{26, 267}, {27, 268}]
        ops = [op for op in ops if opkey(op) not in removed]
        detectors = [row for row in detectors if row not in ({26, 267}, {27, 268})]
        tick = 45
    else:
        assert mode == "append_extra_tick"
        for q, bit in ((28, 27), (29, 26)):
            matches = [op for op in ops if opkey(op) == ("M", (q,), 46, bit)]
            assert len(matches) == 1
            matches[0].time = 47
        tick = 46
    assert not any(op.time == tick and set(op.qs) & {28, 29} for op in ops)
    retained_old_rows = [set(row) for row in detectors]
    ops.append(f.Op("CX", (28, 29), tick))
    ops.sort(key=lambda op: op.time)
    for row in detectors:
        if 26 in row:
            row.symmetric_difference_update({27})
    for old, new in zip(retained_old_rows, detectors):
        expected = old ^ ({27} if 26 in old else set())
        assert expected == new
    meta.update({
        "method": __doc__, "variant": mode,
        "added_CX": {"edge": [28, 29], "tick": tick},
        "removed_copy_helpers": [34, 35] if mode == "exchange_copies" else [],
        "new_terminal_idle_tick": mode == "append_extra_tick",
        "retained_detector_rows_exactly_rewritten": True,
    })
    target = HERE / ("v35a_c_" + mode)
    emit(ops, detectors, target, meta)
    cert = verify(target, meta)
    native, _ = f.native_text(ops)
    instructions, blocks = noise_blocks(native, .001)
    counted = 0
    for instruction, block in zip(instructions, blocks):
        if instruction.name == "CX" and tuple(instruction.qubits) == (28, 29):
            assert block[block.index(instruction.text) + 1] == "DEPOLARIZE2(0.001) 28 29"
            counted += 1
    assert counted > 0
    return cert


if __name__ == "__main__":
    result = {mode: build(mode) for mode in ("exchange_copies", "append_extra_tick")}
    (HERE / "readout_certificates.json").write_text(json.dumps(result, indent=2) + "\n")
