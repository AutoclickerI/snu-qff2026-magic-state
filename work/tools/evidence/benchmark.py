"""Reproduce controls and shared prices serially; save every completed measurement."""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from qtools import price, write_stem, judge_check
from qtools.storage import atomic_json
from qtools.version import EVALUATOR_VERSION


def main():
    fixture = HERE / 'tests/fixtures'
    output = HERE / 'evidence' / ('benchmark_' + socket.gethostname() + '.json')
    records = dict(host=socket.gethostname(), load=os.getloadavg(), version=EVALUATOR_VERSION,
                   started=time.time(), legacy=[], shared=[], judge=[])
    if output.exists():
        saved = json.loads(output.read_text())
        records['legacy'] = saved['legacy']
    for lane, width, basis in [('MAIN/sparse', '9', 'main'), ('MERGE/sparse_v37', '12', 'merge_active')]:
        for name in ('v37h', 'v37i'):
            if any(r['source'] == lane and Path(r['stem']).name == name for r in records['legacy']):
                continue
            command = [sys.executable, str(HERE / 'evidence/probe_legacy.py'), lane,
                       str(fixture / name), width, str(fixture / 'bases' / (basis + '.json'))]
            print('START', lane, name, flush=True)
            completed = subprocess.run(command, text=True, capture_output=True)
            if completed.returncode:
                raise RuntimeError(completed.stderr)
            record = json.loads(completed.stdout)
            records['legacy'].append(record)
            atomic_json(output, records)
            print(json.dumps(record), flush=True)
    for name in ('v37h', 'v37i'):
        record = dict(price(fixture / name, 1, use_cache=False), name=name)
        records['shared'].append(record)
        hit = price(fixture / name, 1)
        records.setdefault('cache_hits', []).append(dict(name=name, seconds=hit['seconds']))
        atomic_json(output, records)
        print(json.dumps(record), flush=True)
    qasm = (fixture / 'v37i.qasm').read_text()
    assert qasm.count('// DETECTOR c[309]\n') == 1
    edited = qasm.replace('// DETECTOR c[309]\n', '')
    data = json.loads((fixture / 'v37i.json').read_text())['data_qubits']
    stem = write_stem(edited, data, HERE / 'cache/candidates', 'v37i_remove_det309')
    record = dict(price(stem, 1, use_cache=False), name='v37i minus detector 309')
    records['shared'].append(record)
    atomic_json(output, records)
    print(json.dumps(record), flush=True)
    for name in ('v37h', 'v37i'):
        record = dict(judge_check(fixture / name), name=name)
        records['judge'].append(record)
        atomic_json(output, records)
        print(json.dumps(record), flush=True)
    records['completed'] = time.time()
    atomic_json(output, records)


if __name__ == '__main__':
    main()
