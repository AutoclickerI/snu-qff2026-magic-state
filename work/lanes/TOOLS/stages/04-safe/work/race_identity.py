"""Strict identities for exact means and resumable chunks; no path-name identity."""
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from functools import lru_cache
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(None)
def environment():
    import numpy
    import tprep
    import xtim
    files = {}
    for module in (numpy, tprep, xtim):
        root = Path(module.__file__).resolve().parent
        for path in sorted(root.rglob('*')):
            if path.is_file() and (path.suffix in ('.py', '.so')):
                files[f'{module.__name__}/{path.relative_to(root)}'] = file_hash(path)
    cpu = Path('/proc/cpuinfo').read_text()
    flags = next(line for line in cpu.splitlines() if line.startswith('flags'))
    result = dict(python=sys.version,platform=platform.platform(),machine=platform.machine(),
                  cpu_flags=flags, packages={p:importlib.metadata.version(p) for p in ('numpy','xtim','stim','qiskit')},
                  threads={k:os.environ.get(k) for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')},
                  files=files)
    return result


def mean_identity(text, data):
    return dict(qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),data_qubits=list(data),
                noise='tprep.STANDARD',p=float(1e-3).hex(),environment_sha256=digest(environment()))


def load_mean(path, text, data):
    obj = json.loads(Path(path).read_text())
    if obj['identity'] != mean_identity(text, data):
        raise ValueError('exact mean identity mismatch (QASM/data/noise/build/environment)')
    a, n = float.fromhex(obj['A']), float.fromhex(obj['N'])
    if not (0 < a <= 1 and 0 <= n <= a):
        raise ValueError('invalid exact moments')
    return a, n
