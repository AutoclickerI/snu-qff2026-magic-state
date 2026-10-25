"""Saved-circuit all-orders prices and a content-addressed experiment ledger."""
import argparse, hashlib, json, os, subprocess, sys,threading,fcntl
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TAU = 3.815473322483099e-5
LOCK=threading.Lock()

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def price(stem, workers=6, phantom=False):
    stem = Path(stem).resolve()
    qasm = stem.with_suffix('.qasm')
    meta = json.loads(stem.with_suffix('.json').read_text())
    digest = sha(qasm)
    ev = ROOT / ('sparse40' if phantom else os.environ.get('GLOBAL_EVALUATOR','sparse'))
    hashes = {f: sha(ev / f) for f in ['sparse_walsh.py', 'frontend.py', 'fastfill.py', 'basis_warm.json']}
    ledger = ROOT / 'results.json'
    with LOCK:
        previous=json.loads(ledger.read_text()).get(digest) if ledger.exists() else None
    if previous and previous['evaluator']==hashes and previous['data_qubits']==meta['data_qubits']:
        return previous
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
                  moved=meta.get('global_change', 'control' if stem.name == 'v36h' else 'phantom reference'))
    receipts=ROOT/'priced';receipts.mkdir(exist_ok=True)
    receipt=receipts/f'{digest}.{os.getpid()}.tmp'
    receipt.write_text(json.dumps(record,indent=2)+'\n');receipt.replace(receipts/f'{digest}.json')
    with LOCK, (ROOT/'results.lock').open('a') as lockfile:
        fcntl.flock(lockfile,fcntl.LOCK_EX)
        records = json.loads(ledger.read_text()) if ledger.exists() else {}
        records[digest] = record
        temporary=ROOT/f'results.{os.getpid()}.tmp.json'
        temporary.write_text(json.dumps(records, indent=2) + '\n')
        temporary.replace(ledger)
        fcntl.flock(lockfile,fcntl.LOCK_UN)
    meta.update(allorders=dict(loss=record['loss'],acceptance=record['acceptance'],J_tau=record['J_tau'],qasm_sha256=digest))
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k not in ['evaluator','moved','data_qubits']}), flush=True)
    return record

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('stems', nargs='+')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--phantom', action='store_true')
    ap.add_argument('--jobs',type=int,default=1)
    args = ap.parse_args()
    assert (args.jobs*(args.workers+1)+1 if args.workers>1 else args.jobs+1)<=24
    with ThreadPoolExecutor(args.jobs) as pool:
        list(pool.map(lambda name:price(name,args.workers,args.phantom),args.stems))
