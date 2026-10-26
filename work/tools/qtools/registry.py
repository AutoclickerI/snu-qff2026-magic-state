"""Saved row-XOR programs are speed hints, never result-cache identities."""
import hashlib
import json
from pathlib import Path
from .storage import atomic_json, locked
from .version import TOOLS

REGISTRY = TOOLS / 'bases.json'


def basis_id(ops):
    return hashlib.sha256(json.dumps(ops, separators=(',', ':')).encode()).hexdigest()


def load_registry(path=REGISTRY):
    with Path(path).open() as stream:
        registry = json.load(stream)
    if registry['schema'] != 1 or not registry['bases']:
        raise ValueError('unsupported or empty basis registry')
    for key, ops in registry['bases'].items():
        if basis_id(ops) != key:
            raise ValueError('basis registry digest mismatch')
    return registry


def add_basis(ops, *, source, path=REGISTRY):
    path = Path(path)
    key = basis_id(ops)
    with locked(path.with_suffix('.lock')):
        registry = load_registry(path)
        if key not in registry['bases']:
            registry['bases'][key] = ops
            registry['origins'][key] = [source]
            atomic_json(path, registry)
    return key
