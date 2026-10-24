#!/usr/bin/env python3
import json
import multiprocessing as mp
import os
from pathlib import Path

import tprep

HERE = Path(__file__).resolve().parent


def one(qasm):
    jf = qasm.with_suffix('.json')
    meta = json.loads(jf.read_text())
    rep = tprep.check(qasm.read_text(), meta['data_qubits'], shots=10**6, seed=0)
    return {
        'name': qasm.stem,
        'passed': bool(rep.passed),
        'format': bool(rep.format_ok),
        'class': bool(rep.class_ok),
        'correctness': bool(rep.correct_ok),
        'acceptance_ok': bool(rep.acceptance_ok),
        'acceptance': rep.acceptance,
        'score': rep.score,
        'sem': rep.sem,
        'n_2q': rep.n_2q,
        'errors': rep.correctness_errors,
    }


def main():
    files = sorted(HERE.glob('*.qasm'))
    with mp.get_context('fork').Pool(min(12, len(files))) as pool:
        rows = pool.map(one, files)
    out = {'shots': 10**6, 'rows': rows}
    (HERE / 'validation.json').write_text(json.dumps(out, indent=2) + '\n')
    for r in rows:
        print(r['name'], 'PASS' if r['passed'] else 'FAIL', r['acceptance'], r['score'], r['errors'], flush=True)
    bad = [r for r in rows if not r['passed']]
    raise SystemExit(1 if bad else 0)


if __name__ == '__main__':
    main()
