"""All-orders loss with a chosen set of noise channels made perfect (counterfactual, not a gate deletion).

usage: region.py <stem> <spec.json> <procs>
spec.json: {"name": str, "units": [[time, [qubits...]], ...]}  -- every channel attached to a native op at that
(time, qubit tuple) is dropped: its gate/measure/reset noise, a first-use init error before it, and the idle run
that starts after it.  Optionally "idle_only": true drops only the idle runs.
"""
import sys, json, time
from pathlib import Path
import sparse_walsh as sw


def run(stem, spec, procs):
    start = time.perf_counter()
    m, eng, groups, nd, ks, psi, where, dense = sw.prepare(Path(stem), True)
    keyset = {(t, tuple(qs)) for t, qs in spec['units']}
    kinds = spec.get('kinds')
    dropped = 0
    keep = {}
    for c, fs in groups.items():
        ch = m.chans[c]
        op = m.labels[ch['ins']]
        hit = (op.time, tuple(op.qs)) in keyset
        if kinds and hit:
            hit = op.kind in kinds
        if hit:
            dropped += 1
            continue
        keep[c] = fs
    compiled, elim = sw.compile_best(m, eng, keep, nd, ks)
    keys = [None] + eng.keys
    sw._CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
    import multiprocessing as mp
    with mp.get_context('fork').Pool(procs) as pool:
        rows = list(pool.imap(sw._row, keys))
    A = rows[0]['value']
    obs = sum(w * b * r['value'] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
    out = dict(stem=str(stem), name=spec.get('name'), dropped_channels=dropped, channels=len(groups),
               acceptance=A, loss=(A - obs) / (2 * A), seconds=time.perf_counter() - start)
    print(json.dumps(out), flush=True)
    return out


if __name__ == '__main__':
    run(sys.argv[1], json.loads(Path(sys.argv[2]).read_text()), int(sys.argv[3]))
