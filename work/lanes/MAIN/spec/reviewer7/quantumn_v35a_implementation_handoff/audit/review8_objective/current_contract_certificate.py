"""Current pinned v35a native schedule and A-instrument certificate.

Run with audit/review6_validation/venv/bin/python. Exact GF(2) assertions
are separated from floating ideal-state checks and the local EXENC proxy.
"""
from pathlib import Path
from itertools import combinations
import ast
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "audit/review6_validation/official"))
from tprep.qasm import convert
from tprep.noise import schedule
sys.path.insert(0, str(ROOT / "audit/review6_tail"))
import frontend as f

source = ROOT / "quantumn_review8/work/lanes/MAIN/v35a"
text = source.with_suffix(".qasm").read_text()
metadata = json.loads(source.with_suffix(".json").read_text())
operations, detectors = f.parse_current(text)
native, labels, errors = convert(text)
assert not errors, errors
program, scheduled, gaps = schedule(native)
quantum_schedule = [(instruction, entries) for instruction, entries
                    in zip(program, scheduled) if instruction.qubits]
assert len(quantum_schedule) == len(operations), (len(quantum_schedule), len(operations))
assert all(operation.time == tick
           for operation, (instruction, entries) in zip(operations, quantum_schedule)
           for qubits, tick in entries)
depth = max(tick for entries in scheduled for qubits, tick in entries) + 1
cx_count = sum(len(instruction.qubits) // 2 for instruction in program
               if instruction.name == "CX")
assert (depth, cx_count) == (47, 206)

cells = [1, 14, 8, 9, 2, 16, 15]
cell_set = set(cells)
prep = [operation for operation in operations if operation.kind == "CX"
        and 38 <= operation.time <= 43 and set(operation.qs) <= cell_set]
layers = [[list(operation.qs) for operation in prep if operation.time == tick]
          for tick in range(38, 44)]
assert len(prep) == 11
flag = {8}
decoder = [(9, 15), (8, 9)]
for control, target in reversed(decoder):
    if control in flag:
        flag.symmetric_difference_update({target})
assert flag == {8, 9, 15}
input_flag = set(flag)
for operation in reversed(prep):
    control, target = operation.qs
    if control in input_flag:
        input_flag.symmetric_difference_update({target})
assert input_flag == {8}
assert any(operation.kind == "MX" and operation.qs == (8,)
           and operation.time == 37 and operation.bit == 272
           for operation in operations)
assert any(operation.kind == "MX" and operation.qs == (8,)
           and operation.time == 46 and operation.bit == 16
           for operation in operations)

def span(words):
    result = {0}
    for word in words:
        result |= {old ^ word for old in tuple(result)}
    return result

def mask(indices):
    return sum(1 << index for index in indices)

checks = [mask(indices) for indices in
          [{0, 2, 4, 6}, {1, 2, 5, 6}, {3, 4, 5, 6}]]
stabilizers = span(checks)
flag_indices = {cells.index(qubit) for qubit in flag}
flag_mask = mask(flag_indices)
assert flag_indices == {2, 3, 6}
assert flag_mask ^ 127 in stabilizers
assert flag_mask not in stabilizers
pivots = [1, 14, 8, 2]
images = {}
for pivot in pivots:
    image = {pivot}
    for operation in prep:
        control, target = operation.qs
        if control in image:
            image.symmetric_difference_update({target})
    images[pivot] = sorted(image)
assert span([mask([cells.index(q) for q in image]) for image in images.values()]) == span(checks + [127])

phase_pairs = []
for i, j in combinations(range(7), 2):
    completion = ((i + 1) ^ (j + 1)) - 1
    assert mask([i, j, completion]) ^ 127 in stabilizers
    detected = bool((mask([i, j]) & flag_mask).bit_count() % 2)
    assert detected == (completion not in flag_indices)
    phase_pairs.append({"code_indices": [i, j], "completion": completion,
                        "flag_detected": detected})
assert sum(row["flag_detected"] for row in phase_pairs) == 12

# Run the exact score() function from the current pinned primary source,
# without importing its compiler, OR-Tools, or long synthesis entry point.
source_file = HERE / "sources/work/lanes/EXENC/exenc.py"
parsed = ast.parse(source_file.read_text())
score_definition = next(node for node in parsed.body
                        if isinstance(node, ast.FunctionDef) and node.name == "score")
namespace = {}
exec(compile(ast.Module(body=[score_definition], type_ignores=[]),
             str(source_file), "exec"), namespace)
vector = namespace["score"](layers, pivots, cells, cells)
assert vector == [0, 3, 4, 0, 4, 0, 0, 0]
blind = sum(vector[index + 1] for index in flag_indices)
assert blind == 4

f.DATA = metadata["data_qubits"]
ideal_cases = []
for stem in [source, HERE / "v35a_tracked_c272"]:
    ops, rows = f.parse_current(stem.with_suffix(".qasm").read_text())
    model = f.make_model(ops, rows)
    engine = f.Engine(model)
    phi = engine.phi(0)
    def expect(pauli):
        x, z, coefficient = pauli
        return float(engine.expect(phi, (engine.B.express(x), engine._w(z), coefficient)).real)
    stabilizer_means = [expect(pauli) for pauli in model.gen_m]
    assert all(abs(value - 1) < 1e-10 for value in stabilizer_means)
    logical_means = {pauli: expect(model.Q[(pauli, 0, 0)]) for pauli in ["X", "Y"]}
    ideal_cases.append({"source": str(stem.relative_to(ROOT)),
                        "before_decoder_output_stabilizer_means": stabilizer_means,
                        "before_decoder_logical_XY_means": logical_means,
                        "ideal_acceptance": engine.A0})

result = {
    "source_commit": "948dcfdca233baceee9759b90519a8589e00bd13",
    "source_qasm_sha256": hashlib.sha256(text.encode()).hexdigest(),
    "stored_metadata_qasm_sha256": metadata.get("qasm_sha256"),
    "scope": __doc__,
    "official_native_schedule": {"CX": cx_count, "depth": depth,
                                 "ticks": [0, depth - 1],
                                 "every_operation_matches_independent_frontend_tick": True,
                                 "format_errors": errors},
    "A_encoder": {"CX": len(prep), "ticks": [38, 43], "layers": layers,
                  "plus_pivot_cells": pivots, "plus_pivot_X_images": images,
                  "exact_output_X_stabilizer_space_matches_plus_L": True},
    "A_flag": {"terminal_measurement": {"cell": 8, "bit": 16, "tick": 46},
               "decoder_CX": [[9, 15, 44], [8, 9, 45]],
               "at_encoder_output_X_cells": sorted(flag),
               "code_support": sorted(flag_indices),
               "at_encoder_input_X_cells": sorted(input_flag),
               "input_measurement": {"cell": 8, "bit": 272, "tick": 37},
               "ideal_relation": "c16 XOR c272 = 0",
               "pure_weight_two_Z_pairs": len(phase_pairs),
               "detected_pairs": 12, "blind_pairs": 9},
    "EXENC_local_proxy_only": {"current_vector_units_p_over_15": vector,
                               "old_scalar_total_units": sum(vector),
                               "flag_blind_units": blind,
                               "limitations": "Original EXENC local reset/idle convention; not the current full noisy instrument, real init/readout noise, or conditional logical loss."},
    "numeric_ideal_state_checks": ideal_cases,
    "limitations": "GF(2) identities and native schedule are exact; quantum expectation calculations use floating arithmetic. No new encoder or overall performance improvement is claimed here.",
}
(HERE / "current_contract_certificate.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: result[key] for key in ["source_qasm_sha256", "official_native_schedule", "A_flag", "EXENC_local_proxy_only", "numeric_ideal_state_checks"]}, indent=2))
