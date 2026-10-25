"""Reproduce the matched PCC preparation-noise diagnostic using a pinned repo.

This runs four nonphysical counterfactuals. It does not produce a legal circuit
or modify a repository source file. Use the repository's Python environment.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', required=True, type=Path)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--specs', type=Path,
                    default=Path(__file__).resolve().parent.parent / 'specs')
    ap.add_argument('--output', type=Path,
                    default=Path('pcc_matched_reproduction.json'))
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    repo = a.repo.resolve()
    lane = repo / 'work/lanes/PCC'
    driver = lane / 'ev/pcc_eval.py'
    jobs = [
        ('r0_control', 'k0', {'ins_tick': 44, 'drop_qubits': [36]}),
        ('r102_control', 'v102', {'ins_tick': 44, 'drop_qubits': [36, 37, 38, 39]}),
        ('r0_bcprep_removed', 'k0', json.loads((a.specs / 'k0_bcprep_spec.json').read_text())),
        ('r102_bcprep_removed', 'v102', json.loads((a.specs / 'bcprep_spec.json').read_text())),
    ]
    commands = []
    for label, name, spec in jobs:
        spec['name'] = label
        commands.append((label, [sys.executable, str(driver), str(lane / 's1' / name),
                                 json.dumps(spec, separators=(',', ':')), str(a.workers)]))
    if a.dry_run:
        print(json.dumps({'commands': commands, 'physical_circuit': False}, indent=2))
        return
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    result = {'implementation_reference_commit': 'f4b685ff12aed683def0697d42a6a48348efe48d',
              'physical_circuit': False,
              'limits': '48-qubit phantom counterfactuals; not a lower bound on all direct preparations or a score guarantee.',
              'rows': {}}
    files = [driver, lane / 's1/k0.qasm', lane / 's1/v102.qasm',
             lane / 'ev/sparse_walsh.py', lane / 'ev/frontend.py']
    result['source_sha256'] = {str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in files}
    for label, cmd in commands:
        proc = subprocess.run(cmd, cwd=lane / 'ev', env=env,
                              check=True, capture_output=True, text=True)
        parsed = None
        for line in proc.stdout.splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and 'loss' in obj and 'acceptance' in obj:
                parsed = obj
        if parsed is None:
            raise RuntimeError(f'No score JSON returned for {label}: {proc.stdout[-2000:]}')
        result['rows'][label] = parsed
        print(json.dumps({'label': label, 'loss': parsed['loss'],
                          'acceptance': parsed['acceptance']}), flush=True)
    r = result['rows']
    result['delta_r102_minus_r0'] = {
        'original_prep_noise': r['r102_control']['loss'] - r['r0_control']['loss'],
        'same_prep_noise_removed': r['r102_bcprep_removed']['loss'] - r['r0_bcprep_removed']['loss'],
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(a.output)


if __name__ == '__main__':
    main()
