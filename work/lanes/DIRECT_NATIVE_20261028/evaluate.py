"""Price the actual native cultivation source without an assumed terminal.

This control retains all source gates, records, and noise. It asks whether the
additional final instrument is necessary for this particular source; it is not
an ideal-resource or decoded-only validity test.
"""
import os
for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "work/tools")]
from qtools import price, write_stem
from qtools.validity import raw_check
from qtools.evaluator import frontend as f

parent = ROOT / "work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16"
text = parent.with_suffix(".qasm").read_text()
data = json.loads(parent.with_suffix(".json").read_text())["data_qubits"]
ops, dets = f.parse_current(text)
result = {
    "parent": str(parent.relative_to(ROOT)),
    "scope": "Complete native source only, without resource preparation or a final verification instrument; every source noise channel retained.",
    "cx": sum(op.kind == "CX" for op in ops),
    "clocks": max(op.time for op in ops) + 1,
    "raw": raw_check(text, data),
}
stem = write_stem(text, data, HERE, "source_only", source=result)
result["stem"] = str(stem.relative_to(ROOT))
print(json.dumps(result), flush=True)
if result["raw"]["ok"]:
    result["exact"] = price(stem, processes=1)
(HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result), flush=True)
