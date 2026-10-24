"""Collect the eight bounded v35a prices and their independent certificates."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
NAMES = [
    "v35a_control", "v35a_drop_z0_h6", "v35a_drop_x20_h19",
    "v35a_drop_x7_h13", "v35a_drop_x10_h11", "v35a_drop_x4_h5",
    "v35a_c_exchange_copies", "v35a_c_append_extra_tick",
]
baseline = json.loads((HERE / "v35a_control_canonical_sparse_result.json").read_text())
rows = []
for name in NAMES:
    receipt = json.loads((HERE / (name + "_canonical_sparse_result.json")).read_text())
    metadata = json.loads((HERE / (name + ".json")).read_text())
    certificate = metadata["independent_verification"]
    rows.append({
        "name": name,
        "qasm_sha256": certificate["qasm_sha256"],
        "CX": certificate["CX"],
        "native_ticks": certificate["native_ticks"],
        "moments": len(receipt["results"]),
        "loss": receipt["loss"],
        "acceptance": receipt["acceptance"],
        "absolute_loss_change": receipt["loss"] - baseline["loss"],
        "percent_loss_change": 100 * (receipt["loss"] / baseline["loss"] - 1),
        "acceptance_change": receipt["acceptance"] - baseline["acceptance"],
        "conditional_loss_kernel_omission_bound": receipt["conditional_loss_kernel_omission_bound"],
        "all_single_faults_harmless": certificate["harmful_single_fault_count"] == 0,
        "ideal_target_and_detector_test": certificate["ideal_acceptance"] == 1 and abs(certificate["ideal_loss"]) < 1e-12,
        "native_schedule_matches": certificate["native_schedule_matches"],
        "nearest_neighbor_CX": certificate["nearest_neighbor_CX"],
        "official_class_tested_by_this_lane": metadata["official_class_tested"],
        "official_runtime_tested_by_this_lane": metadata["official_runtime_tested"],
    })
out = {
    "source_commit": "948dcfdca233baceee9759b90519a8589e00bd13",
    "baseline_QASM_SHA256": rows[0]["qasm_sha256"],
    "scope": "One current baseline, five complete individual guard removals, two complete C-readout variants. All surviving physical noise is charged. No circuit is officially validated by this lane.",
    "rows": rows,
}
(HERE / "results_summary.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
