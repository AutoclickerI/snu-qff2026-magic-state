"""All-orders loss with chosen noise channels made perfect (counterfactual, not a gate deletion).

usage: region.py <stem> <spec.json> <procs>
spec: {"name", "units": [[time,[qs]],...], "kinds": [...], "idle_only": bool, "qubits_idle": [[q, t0, t1], ...],
       "scale": x}
 - units: channels attached to the native op at (time, qs) (its gate/measure/reset noise, a first-use init error before
   it, and the idle run after it) are dropped; only those of op.kind in "kinds" if given; idle runs only if idle_only.
 - qubits_idle: idle runs on qubit q whose run STARTS at a step in [t0, t1] are dropped.
 - scale: multiply the selected channels' probabilities by x instead of dropping them.
"""
import sys, json, time
from pathlib import Path
import sparse_walsh as sw
import frontend as fa


def run(stem, spec, procs):
    start = time.perf_counter()
    m, eng, groups, nd, ks, psi, where, dense = sw.prepare(Path(stem), True)
    keyset = {(t, tuple(qs)) for t, qs in spec.get('units', [])}
    idle_only = spec.get('idle_only', False)
    qidle = spec.get('qubits_idle', [])
    kinds = spec.get('kinds')
    prog, blocks = fa.noise_blocks(m.native, .001, first_order=False)
    _, steps, gaps = fa.schedule(m.native)
    kidx = [b.index(ins.text) for ins, b in zip(prog, blocks)]
    # idle run start step per (ins, qubit)
    gapstart = {(i, q): (t0, n) for i, q, t0, n in gaps}
    dropped = 0
    keep = {}
    for c, fs in groups.items():
        ch = m.chans[c]
        ii = ch['ins']
        op = m.labels[ii]
        is_idle = ch['name'] == 'DEPOLARIZE1' and ch['jl'] >= kidx[ii] + 2
        hit = (op.time, tuple(op.qs)) in keyset and (is_idle or not idle_only)
        if hit and kinds:
            hit = op.kind in kinds
        if not hit and is_idle and qidle:
            q = ch['qs'][0]
            g = gapstart.get((ii, q))
            if g is not None:
                hit = any(q == qq and t0 <= g[0] <= t1 for qq, t0, t1 in qidle)
        scale = spec.get('scale')
        if hit and scale is not None:
            ch['p'] = ch['p'] * scale
            fs = [dict(f, p=f['p'] * scale) for f in fs]
            dropped += 1
            keep[c] = fs
            continue
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
