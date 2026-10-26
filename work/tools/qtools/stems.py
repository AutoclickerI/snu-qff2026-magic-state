"""QASM bytes and ordered physical outputs jointly identify a circuit."""
import hashlib
import json
from pathlib import Path
import re
from .storage import atomic_json, atomic_write, locked


def outputs(data_qubits):
    data = tuple(data_qubits)
    if len(data) != 7 or any(type(q) is not int or not 0 <= q < 36 for q in data) or len(set(data)) != 7:
        raise ValueError('data_qubits must be seven distinct integers in 0..35, in code order')
    return data


def read_stem(stem):
    stem = Path(stem)
    qasm = stem.with_suffix('.qasm').read_bytes()
    data = outputs(json.loads(stem.with_suffix('.json').read_bytes())['data_qubits'])
    return qasm, data


def identity(stem):
    qasm, data = read_stem(stem)
    return hashlib.sha256(qasm).hexdigest(), data


def write_stem(qasm_text, data_qubits, outdir, prefix, *, source=None):
    data = outputs(data_qubits)
    if not re.fullmatch(r'[A-Za-z0-9_-]+', prefix):
        raise ValueError('prefix must contain only letters, digits, underscore or hyphen')
    qasm = qasm_text.encode('utf-8')
    sha = hashlib.sha256(qasm).hexdigest()
    stem = Path(outdir) / f"{prefix}_{sha[:16]}_d{'_'.join(map(str, data))}"
    with locked(stem.with_suffix('.lock')):
        if stem.with_suffix('.qasm').exists():
            if read_stem(stem) != (qasm, data):
                raise ValueError(f'stem collision or damaged metadata: {stem}')
        else:
            meta = {'data_qubits': list(data)}
            if source is not None:
                meta['source'] = source
            atomic_json(stem.with_suffix('.json'), meta)
            # Publish QASM last; existence marks a completed pair.
            atomic_write(stem.with_suffix('.qasm'), qasm)
    return stem
