#!/usr/bin/env python3
"""Check package integrity and source provenance without executing project code."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


def require(value, message):
    if not value:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def safe_file(root, relative):
    part = PurePosixPath(relative)
    require(not part.is_absolute() and '..' not in part.parts,
            f'Unsafe package path: {relative!r}')
    result = root.joinpath(*part.parts)
    require(result.is_file() and not result.is_symlink(),
            f'Missing or linked file: {relative}')
    require(result.resolve().is_relative_to(root.resolve()),
            f'Path escapes package: {relative}')
    return result


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'MANIFEST.json').read_text())
    rows = manifest['files']
    paths = [row['path'] for row in rows]
    require(len(paths) == len(set(paths)), 'Duplicate manifest paths')
    for row in rows:
        data = safe_file(root, row['path']).read_bytes()
        require(len(data) == row['bytes'], f'Size mismatch: {row["path"]}')
        require(sha256(data) == row['sha256'], f'Hash mismatch: {row["path"]}')

    expected_names = set(paths) | {'MANIFEST.json', 'CHECKSUMS.sha256'}
    actual_names = {str(p.relative_to(root)).replace('\\', '/')
                    for p in root.rglob('*') if p.is_file()
                    and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    require(actual_names == expected_names,
            f'File-set mismatch: {sorted(actual_names ^ expected_names)}')

    checksum_names = []
    for line in (root / 'CHECKSUMS.sha256').read_text().splitlines():
        digest, name = line.split('  ', 1)
        checksum_names.append(name)
        require(sha256(safe_file(root, name).read_bytes()) == digest,
                f'Checksum mismatch: {name}')
    require(len(checksum_names) == len(set(checksum_names)), 'Duplicate checksums')
    require(set(checksum_names) == set(paths) | {'MANIFEST.json'},
            'Checksum coverage differs from manifest')

    provenance = json.loads((root / 'SOURCE_PROVENANCE.json').read_text())
    for row in provenance['files']:
        data = safe_file(root, row['path']).read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == row['git_blob_sha1'], f'Git blob mismatch: {row["path"]}')

    python_files = [p for p in paths if p.endswith('.py')]
    for name in python_files:
        ast.parse(safe_file(root, name).read_text(), filename=name)
    json_files = [p for p in paths if p.endswith('.json')]
    for name in json_files:
        json.loads(safe_file(root, name).read_text())

    tasks = json.loads((root / 'TASKS.json').read_text())
    require([task['id'] for task in tasks['tasks']] ==
            [f'M{i:02d}' for i in range(1, 11)], 'Expected M01 through M10')
    baseline = json.loads((root / 'EVIDENCE_SUMMARY.json').read_text())
    qasm = root / 'quantumn_review10/work/lanes/MAIN/v36c.qasm'
    require(sha256(qasm.read_bytes()) == baseline['baseline_qasm_sha256'],
            'Baseline QASM pin mismatch')
    require(tasks['common']['source_commit'] == provenance['quantumn_commit'] ==
            baseline['source_commit'], 'Source pin disagreement')
    require(tasks['common']['official_commit'] == provenance['official_commit'] ==
            baseline['official_commit'], 'Judge pin disagreement')
    require(baseline['basis_validation']['passed'], 'Basis validation did not pass')
    print(json.dumps({
        'passed': True, 'payload_files': len(rows),
        'source_git_blobs': len(provenance['files']),
        'python_files_parsed': len(python_files), 'json_files_parsed': len(json_files),
        'tasks': len(tasks['tasks']), 'qasm_sha256': baseline['baseline_qasm_sha256'],
        'scope': 'Integrity, syntax and stored evidence consistency; not a fresh physics run.',
    }, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, SyntaxError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        raise SystemExit(1)
