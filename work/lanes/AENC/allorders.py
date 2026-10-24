"""All-orders loss/acceptance of a stem with MAIN/sparse's evaluator (same functions as sparse_walsh.run, no file write).
usage: allorders.py <stem> [procs]  -> prints one JSON line"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/MAIN/sparse')
import sparse_walsh as sw


def run(stem, procs=16):
    t = time.time()
    m, eng, groups, nd, ks, psi, where, dense = sw.prepare(Path(stem), True)
    compiled, elim = sw.compile_best(m, eng, groups, nd, ks)
    keys = [None] + eng.keys
    sw._CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
    import multiprocessing as mp
    with mp.get_context('fork').Pool(procs) as pool:
        rows = list(pool.imap(sw._row, keys))
    A = rows[0]['value']
    obs = sum(w * b * r['value'] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
    return dict(stem=str(stem), loss=(A - obs) / (2 * A), acceptance=A, width=elim['width'], seconds=time.time() - t)


if __name__ == '__main__':
    print(json.dumps(run(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 16)), flush=True)
