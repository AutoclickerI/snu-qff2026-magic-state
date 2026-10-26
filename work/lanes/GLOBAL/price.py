"""Saved-circuit all-orders prices and a content-addressed experiment ledger."""
import argparse, hashlib, json, os, subprocess, sys,threading,contextlib,traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TAU = 3.761821654835085e-5
LOCK=threading.Lock()
INLINE_MODULE=None
INLINE_PATH=None

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def price(stem, workers=6, phantom=False):
    global INLINE_MODULE,INLINE_PATH
    stem = Path(stem).resolve()
    qasm = stem.with_suffix('.qasm')
    meta = json.loads(stem.with_suffix('.json').read_text())
    digest = sha(qasm)
    ev = ROOT / ('sparse40' if phantom else os.environ.get('GLOBAL_EVALUATOR','sparse'))
    hashes = {f: sha(ev / f) for f in ['sparse_walsh.py', 'frontend.py', 'fastfill.py', 'basis_warm.json']}
    receipts=ROOT/'priced';receipts.mkdir(exist_ok=True)
    previous=json.loads((receipts/f'{digest}.json').read_text()) if (receipts/f'{digest}.json').exists() else None
    if previous and previous['data_qubits']==meta['data_qubits'] and previous.get('tau')==TAU:
        old=previous['evaluator'];compatible=old==hashes
        proof=ROOT/'basis_equivalence.json'
        if not compatible and proof.exists() and all(old.get(f)==hashes[f] for f in hashes if f!='basis_warm.json'):
            pair={old.get('basis_warm.json'),hashes['basis_warm.json']}
            compatible=any(pair==set(p) for p in json.loads(proof.read_text())['pairs'])
        if compatible:return previous
    logfile = ROOT / 'logs' / (stem.name + '_' + digest[:12] + '.allorders.txt')
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
    with logfile.open('w') as out:
        if os.environ.get('GLOBAL_INLINE_PRICE')=='1':
            assert workers==1
            failed=0
            with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
                try:
                    if INLINE_MODULE is None:
                        sys.path.insert(0,str(ev));import sparse_walsh
                        INLINE_MODULE=sparse_walsh;INLINE_PATH=ev
                    assert INLINE_PATH==ev,'one evaluator namespace per serial process'
                    INLINE_MODULE.run(stem,72,True,1)
                except Exception:
                    traceback.print_exc();failed=1
        else:
            run = subprocess.run([sys.executable, str(ev / 'sparse_walsh.py'), str(stem), '72', 'canonical', str(workers)], stdout=out, stderr=subprocess.STDOUT, env=env)
            failed=run.returncode
    if failed:
        print(json.dumps(dict(name=stem.name, error=failed, log=str(logfile))), flush=True)
        return None
    result = json.loads(logfile.read_text().splitlines()[-1])
    record = dict(path=str(qasm.relative_to(ROOT)), sha256=digest, data_qubits=meta['data_qubits'],
                  evaluator=hashes, phantom=phantom, loss=result['loss'], acceptance=result['acceptance'],
                  J_tau=result['acceptance'] * (result['loss'] - TAU), tau=TAU,
                  seconds=result['seconds'], log=str(logfile.relative_to(ROOT)),
                  moved=meta.get('global_change', 'control' if stem.name == 'v36h' else 'phantom reference'))
    record['phase']=2
    if meta.get('reference_only'):record['reference_only']=True
    receipt=receipts/f'{digest}.{os.getpid()}.{threading.get_ident()}.tmp'
    receipt.write_text(json.dumps(record,indent=2)+'\n');receipt.replace(receipts/f'{digest}.json')
    # Receipts are the write-ahead record. collect.py materializes results.json after a batch;
    # rewriting the whole multi-megabyte ledger per candidate serialized parallel evaluators.
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
    if args.jobs==args.workers==1:os.environ['GLOBAL_INLINE_PRICE']='1'
    assert (args.jobs*(args.workers+1)+1 if args.workers>1 else args.jobs+1)<=24
    with ThreadPoolExecutor(args.jobs) as pool:
        list(pool.map(lambda name:price(name,args.workers,args.phantom),args.stems))
