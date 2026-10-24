"""Read-only local validation against the pinned, unmodified official judge."""
import dataclasses
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OFFICIAL = ROOT / 'official'
sys.path.insert(0, str(OFFICIAL))
import tprep
from tprep.qasm import to_stim
from tprep.noise import schedule

stem = Path(sys.argv[1]).resolve()
shots = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
raw = stem.with_suffix('.qasm').read_bytes()
meta = json.loads(stem.with_suffix('.json').read_text())
native, errors = to_stim(raw.decode())
assert not errors, errors
prog, steps, gaps = schedule(native)
start = time.perf_counter()
report = tprep.check(raw.decode(), meta['data_qubits'], shots=shots, seed=seed)
out = {
    'source_commit': '42afa8ff01c3999444336f5bb2fe473c1475d6f4',
    'official_commit': '76fe47c0324f1c1f8b72a7d55af200e88043b522',
    'input': str(stem), 'qasm_sha256': hashlib.sha256(raw).hexdigest(),
    'data_qubits': meta['data_qubits'], 'shots': shots, 'seed': seed,
    'native_depth': max(t for group in steps for _, t in group) + 1,
    'native_instruction_counts': {k: sum(i.name == k for i in prog) for k in sorted({i.name for i in prog})},
    'versions': {p: importlib.metadata.version(p) for p in ('xtim', 'stim', 'numpy', 'qiskit')},
    'report': dataclasses.asdict(report), 'seconds': time.perf_counter()-start,
    'gates': {k: getattr(report, k) for k in ('format_ok','class_ok','correct_ok','acceptance_ok','passed')},
}
dest = (Path(sys.argv[4]).resolve() if len(sys.argv) > 4 else
        Path(__file__).with_name(stem.name + f'.official_{shots}_{seed}.json'))
dest.write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
