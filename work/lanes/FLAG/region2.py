"""All-orders loss with several channel groups scaled independently (counterfactual, not a rebuild).

usage: region2.py <stem> <spec.json> <procs>      (run from anywhere; imports MAIN/sparse)
spec: {"name": str, "groups": [{"units": [[t,[qs]],...], "kinds": [...], "idle_only": bool,
                                 "qubits_idle": [[q, t0, t1], ...], "scale": x}, ...]}
Selectors are those of MAIN/sparse/region.py; a channel takes the scale of the first group that selects it
(scale 0 drops it). Prints one JSON line.
"""
import sys, json, time
from pathlib import Path
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/MAIN/sparse')
import sparse_walsh as sw
import frontend as fa


def run(stem, spec, procs):
    start = time.perf_counter()
    m, eng, groups, nd, ks, psi, where, dense = sw.prepare(Path(stem), True)
    prog, blocks = fa.noise_blocks(m.native, .001, first_order=False)
    _, steps, gaps = fa.schedule(m.native)
    kidx = [b.index(ins.text) for ins, b in zip(prog, blocks)]
    gapstart = {(i, q): (t0, n) for i, q, t0, n in gaps}
    sel = []
    for g in spec['groups']:
        sel.append(({(t, tuple(qs)) for t, qs in g.get('units', [])}, g.get('idle_only', False),
                    g.get('qubits_idle', []), g.get('kinds'), float(g.get('scale', 0.0))))
    hits = [0] * len(sel)
    keep = {}
    for c, fs in groups.items():
        ch = m.chans[c]
        ii = ch['ins']
        op = m.labels[ii]
        is_idle = ch['name'] == 'DEPOLARIZE1' and ch['jl'] >= kidx[ii] + 2
        scale = None
        for k, (keyset, idle_only, qidle, kinds, sc) in enumerate(sel):
            hit = (op.time, tuple(op.qs)) in keyset and (is_idle or not idle_only)
            if hit and kinds:
                hit = op.kind in kinds
            if not hit and is_idle and qidle:
                q = ch['qs'][0]
                gs = gapstart.get((ii, q))
                if gs is not None:
                    hit = any(q == qq and t0 <= gs[0] <= t1 for qq, t0, t1 in qidle)
            if hit:
                scale = sc
                hits[k] += 1
                break
        if scale is None:
            keep[c] = fs
        elif scale > 0:
            keep[c] = [dict(f, p=f['p'] * scale) for f in fs]
    compiled, elim = sw.compile_best(m, eng, keep, nd, ks)
    keys = [None] + eng.keys
    sw._CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
    import multiprocessing as mp
    with mp.get_context('fork').Pool(procs) as pool:
        rows = list(pool.imap(sw._row, keys))
    A = rows[0]['value']
    obs = sum(w * b * r['value'] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
    out = dict(stem=str(stem), name=spec.get('name'), hits=hits, channels=len(groups),
               acceptance=A, loss=(A - obs) / (2 * A), seconds=time.perf_counter() - start)
    print(json.dumps(out), flush=True)
    return out


if __name__ == '__main__':
    run(sys.argv[1], json.loads(Path(sys.argv[2]).read_text()), int(sys.argv[3]))
