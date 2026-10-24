"""All-orders pricing of INTEG circuits: ev.py PROCS name... (names under c/).

One stem: keys in parallel. Several stems: stems in parallel, keys serial. Results go to
res/<name>.json (loss, acceptance, qasm sha256) and one line per stem on stdout.
--acc: acceptance only (key None, ~1 s per stem).
"""
import os, sys, json, hashlib, time, io, contextlib
from pathlib import Path
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
sys.dont_write_bytecode = True
H = Path(__file__).resolve().parent
SP = H.parent / 'MAIN' / 'sparse'
sys.path.insert(0, str(SP))
os.chdir(SP)
import sparse_walsh as sw

RES = H / 'res'
RES.mkdir(exist_ok=True)


def one(args):
    name, procs, acc = args
    st = H / 'c' / name
    sha = hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()
    out = RES / (name + ('.acc' if acc else '') + '.json')
    if out.exists():
        r = json.loads(out.read_text())
        if r.get('sha') == sha:
            return r
    t = time.time()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            o = sw.run(st, 0 if acc else 72, True, procs)
        r = dict(name=name, sha=sha, seconds=time.time() - t)
        if acc:
            r['acceptance'] = o['results'][0]['value']
        else:
            r.update(loss=o['loss'], acceptance=o['acceptance'], bound=o['conditional_loss_kernel_omission_bound'])
        (SP / (st.name + '_canonical_sparse_result.json')).unlink(missing_ok=True)
    except Exception as e:
        r = dict(name=name, sha=sha, error=repr(e))
    out.write_text(json.dumps(r))
    return r


if __name__ == '__main__':
    a = sys.argv[1:]
    acc = '--acc' in a
    a = [x for x in a if x != '--acc']
    procs = int(a[0])
    names = a[1:]
    if len(names) == 1:
        rs = [one((names[0], procs, acc))]
        print(json.dumps(rs[0]), flush=True)
    else:
        import multiprocessing as mp
        with mp.get_context('fork').Pool(procs) as pool:
            for r in pool.imap_unordered(one, [(n, 1, acc) for n in names]):
                print(json.dumps(r), flush=True)
