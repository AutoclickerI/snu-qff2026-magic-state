"""All-orders pricing through MAIN/sparse: ev.py PROCS stem... (stems are paths; results cached in res/<name>.json).
One stem: keys in parallel over PROCS. Several: stems in parallel (one process each, PROCS at a time)."""
import os, sys, json, hashlib, time, io, contextlib
from pathlib import Path
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
sys.dont_write_bytecode = True
H = Path(__file__).resolve().parent
SP = H.parent / 'MAIN' / 'sparse'
sys.path.insert(0, str(SP))
import sparse_walsh as sw
RES = H / 'res'
RES.mkdir(exist_ok=True)


def one(args):
    st, procs = args
    st = Path(st).resolve()
    name = st.name
    sha = hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()
    out = RES / (name + '.json')
    if out.exists():
        r = json.loads(out.read_text())
        if r.get('sha') == sha:
            return r
    t = time.time()
    try:
        cwd = os.getcwd(); os.chdir(SP)
        with contextlib.redirect_stdout(io.StringIO()):
            o = sw.run(st, 72, True, procs)
        os.chdir(cwd)
        r = dict(name=name, sha=sha, seconds=time.time() - t, loss=o['loss'], acceptance=o['acceptance'],
                 bound=o['conditional_loss_kernel_omission_bound'])
    except Exception as e:
        r = dict(name=name, sha=sha, error=repr(e))
    finally:
        (SP / (name + '_canonical_sparse_result.json')).unlink(missing_ok=True)
    out.write_text(json.dumps(r))
    return r


if __name__ == '__main__':
    procs = int(sys.argv[1])
    stems = sys.argv[2:]
    if len(stems) == 1:
        print(json.dumps(one((stems[0], procs))), flush=True)
    else:
        import multiprocessing as mp
        with mp.get_context('fork').Pool(procs) as pool:
            for r in pool.imap_unordered(one, [(s, 1) for s in stems]):
                print(json.dumps(r), flush=True)
