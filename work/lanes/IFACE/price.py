"""Saved-circuit all-orders prices and a content-addressed experiment ledger."""
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TAU = 3.815473322483099e-5

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def price(stem, workers=2, phantom=False):
    stem = Path(stem).resolve()
    qasm = stem.with_suffix('.qasm')
    meta = json.loads(stem.with_suffix('.json').read_text())
    digest = sha(qasm)
    ev = ROOT / ('sparse40' if phantom else 'sparse')
    hashes = {f: sha(ev / f) for f in ['sparse_walsh.py', 'frontend.py', 'fastfill.py', 'basis_warm.json']}
    logfile = ROOT / 'logs' / (stem.name + '_' + digest[:12] + '.allorders.txt')
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    with logfile.open('w') as out:
        run = subprocess.run([sys.executable, str(ev / 'sparse_walsh.py'), str(stem), '72', 'canonical', str(workers)], stdout=out, stderr=subprocess.STDOUT, env=env)
    if run.returncode:
        print(json.dumps(dict(name=stem.name, error=run.returncode, log=str(logfile))), flush=True)
        return None
    result = json.loads(logfile.read_text().splitlines()[-1])
    record = dict(path=str(qasm.relative_to(ROOT)), sha256=digest, data_qubits=meta['data_qubits'],
                  evaluator=hashes, phantom=phantom, loss=result['loss'], acceptance=result['acceptance'],
                  J_tau=result['acceptance'] * (result['loss'] - TAU),
                  seconds=result['seconds'], log=str(logfile.relative_to(ROOT)),
                  moved=meta.get('iface_change', 'control' if stem.name == 'v36h' else 'unspecified'))
    ledger = ROOT / 'results.json'
    records = json.loads(ledger.read_text()) if ledger.exists() else {}
    records[digest] = record
    ledger.write_text(json.dumps(records, indent=2) + '\n')
    print(json.dumps(record), flush=True)
    return record

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('stems', nargs='+')
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--phantom', action='store_true')
    args = ap.parse_args()
    for name in args.stems:
        price(name, args.workers, args.phantom)
