"""region.py with a Pauli-type filter: within the selected units' channels, drop only the fault components that
match spec['drop'] ('zpart': any Z or Y factor; 'xonly': only I/X factors; 'xpart': any X or Y; 'zonly': only I/Z).
The channel's no-error weight absorbs the dropped probability (counterfactual noise model, not a gate deletion)."""
import sys, json, time
from pathlib import Path
import sparse_walsh as sw

def keep(f, mode):
    P = f['pauli']
    z = any(c in 'ZY' for c in P); x = any(c in 'XY' for c in P)
    return not {'zpart': z, 'xpart': x, 'xonly': x and not z, 'zonly': z and not x}[mode]

def run(stem, spec, procs):
    start = time.perf_counter()
    m, eng, groups, nd, ks, psi, where, dense = sw.prepare(Path(stem), True)
    keyset = {(t, tuple(qs)) for t, qs in spec['units']}
    newg = {}; touched = 0
    for c, fs in groups.items():
        op = m.labels[m.chans[c]['ins']]
        if (op.time, tuple(op.qs)) in keyset:
            fs = [f for f in fs if keep(f, spec['drop'])]
            m.chans[c]['p'] = sum(f['p'] for f in fs); touched += 1
        if fs: newg[c] = fs
    compiled, elim = sw.compile_best(m, eng, newg, nd, ks)
    keys = [None] + eng.keys
    sw._CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
    import multiprocessing as mp
    with mp.get_context('fork').Pool(procs) as pool:
        rows = list(pool.imap(sw._row, keys))
    A = rows[0]['value']
    obs = sum(w * b * r['value'] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
    out = dict(stem=str(stem), name=spec.get('name'), drop=spec['drop'], touched_channels=touched, acceptance=A,
               loss=(A - obs) / (2 * A), seconds=time.perf_counter() - start)
    print(json.dumps(out), flush=True)

if __name__ == '__main__':
    run(sys.argv[1], json.loads(Path(sys.argv[2]).read_text()), int(sys.argv[3]))
