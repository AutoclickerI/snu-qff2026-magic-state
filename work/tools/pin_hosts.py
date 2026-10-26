#!/usr/bin/env python3
"""Mirror this toolset, then verify the source manifest on one host at a time."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from qtools.version import EVALUATOR_VERSION, source_manifest
from qtools.storage import atomic_json

ROOT = HERE.parents[1]
SSH = ['ssh', '-q']
ENV = ['env', 'OMP_NUM_THREADS=1', 'OPENBLAS_NUM_THREADS=1', 'MKL_NUM_THREADS=1',
       'PYTHONDONTWRITEBYTECODE=1']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('hosts', nargs='*')
    args = parser.parse_args()
    args.hosts = args.hosts or ['owl', 'tom', 'jerry', 'hippo', 'sunfish']
    if any(h not in {'owl', 'tom', 'jerry', 'hippo', 'sunfish'} for h in args.hosts):
        parser.error('hosts must be owl, tom, jerry, hippo or sunfish')
    results = []
    for host in args.hosts:
        # One rsync/SSH process at a time; no credentials, generated caches or bytecode.
        command = ['rsync', '-a', '--exclude', '.submit_credentials', '--exclude', 'cache/',
                   '--exclude', '__pycache__/', '--exclude', '*.lock', '--exclude', '*.tmp',
                   '-e', shlex.join(SSH), '--relative', str(ROOT / 'work') + '/./tools/',
                   f'{host}:{ROOT}/work/']
        subprocess.run(command, stdin=subprocess.DEVNULL, check=True)
        code = ("import json,os; from qtools.version import EVALUATOR_VERSION,source_manifest; "
                "print(json.dumps(dict(evaluator_version=EVALUATOR_VERSION,files=source_manifest(),"
                "cores=os.cpu_count(),load=os.getloadavg()[0])))")
        python = str(ROOT / '.venv/bin/python')
        if host == 'owl':
            run = ['docker', 'run', '--rm', '-u', '1010:1012', '-e', 'HOME=/home/jihoon',
                   '-v', '/home/jihoon:/home/jihoon', '-w', str(HERE), '--cpus=1',
                   'fnc-build:22.04', *ENV, python, '-c', code]
        else:
            run = [*ENV, python, '-c', code]
        remote = 'cd ' + shlex.quote(str(HERE)) + ' && ' + shlex.join(run)
        output = subprocess.run([*SSH, host, remote], stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, check=True)
        record = dict(json.loads(output.stdout), host=host)
        record['verified'] = (record['evaluator_version'] == EVALUATOR_VERSION
                              and record['files'] == source_manifest())
        if not record['verified']:
            raise RuntimeError(f'{host}: source manifest mismatch')
        results.append(record)
        atomic_json(HERE / 'evidence/hosts.json', results)
        print(json.dumps({k: v for k, v in record.items() if k != 'files'}), flush=True)


if __name__ == '__main__':
    main()
