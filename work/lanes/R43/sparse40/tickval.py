"""All-orders loss with idle runs shortened/lengthened and chosen gate channels dropped (counterfactual).

usage: tickval.py <stem> <spec.json> <procs>
spec: {"name",
       "idle": [[q, t, k], ...]   # the idle run of qubit q that contains native step t gets k steps added
                                  # (k < 0 removes steps; a run reduced to 0 steps is dropped). The judge places
                                  # a run's DEPOLARIZE1 right after the op that starts it, so this equals the
                                  # same circuit with that wait k steps longer.
       "drop": [[t, [qs]], ...]   # non-idle channels (gate, measure, reset, first-use init) of the op at (t, qs)
       "variants": {name: {"idle":..., "drop":...}}  # optional: several counterfactuals sharing one prepare
      }
Prints one JSON line per variant (plus "base" when "variants" is given).
"""
import sys, json, time, copy
from pathlib import Path
import sparse_walsh as sw
import frontend as fa


def rep(p, n):
    return 0.75 * (1 - (1 - 4 * p / 3) ** n) if n > 0 else 0.0


def evaluate(m, eng, groups, nd, ks, psi, where, procs, mods, name):
    start = time.perf_counter()
    prog, blocks = fa.noise_blocks(m.native, .001, first_order=False)
    _, steps, gaps = fa.schedule(m.native)
    kidx = [b.index(ins.text) for ins, b in zip(prog, blocks)]
    runs = {}
    for i, q, t0, n in gaps:
        runs[(i, q)] = (t0, n)
    want = {}
    for q, t, k in mods.get('idle', []):
        hit = [(i, qq) for (i, qq), (t0, n) in runs.items() if qq == q and t0 <= t < t0 + n]
        if not hit:
            raise ValueError(f'no idle run on q{q} containing step {t}')
        want[hit[0]] = want.get(hit[0], 0) + k
    dropset = {(t, tuple(qs)) for t, qs in mods.get('drop', [])}
    keep, changed, restore = {}, [], {}
    for c, fs in groups.items():
        ch = m.chans[c]
        ii = ch['ins']
        op = m.labels[ii]
        is_idle = ch['name'] == 'DEPOLARIZE1' and ch['jl'] >= kidx[ii] + 2
        if is_idle:
            key = (ii, ch['qs'][0])
            if key in want:
                t0, n = runs[key]
                n2 = n + want[key]
                assert n2 >= 0, (key, n, want[key])
                s = rep(.001, n2) / rep(.001, n)
                changed.append((ch['qs'][0], t0, n, n2))
                if n2 == 0:
                    continue
                keep[c] = [dict(f, p=f['p'] * s) for f in fs]
                restore[c] = ch['p']
                ch['p'] = ch['p'] * s
                continue
        elif (op.time, tuple(op.qs)) in dropset:
            changed.append(('drop', op.time, tuple(op.qs), ch['name']))
            continue
        keep[c] = fs
    compiled, elim = sw.compile_best(m, eng, keep, nd, ks)
    for c, p in restore.items():
        m.chans[c]['p'] = p
    keys = [None] + eng.keys
    sw._CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
    import multiprocessing as mp
    with mp.get_context('fork').Pool(procs) as pool:
        rows = list(pool.imap(sw._row, keys))
    A = rows[0]['value']
    obs = sum(w * b * r['value'] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
    out = dict(name=name, changed=len(changed), acceptance=A, loss=(A - obs) / (2 * A),
               seconds=time.perf_counter() - start, detail=changed)
    print(json.dumps(out), flush=True)
    return out


def main():
    stem, spec, procs = sys.argv[1], json.loads(Path(sys.argv[2]).read_text()), int(sys.argv[3])
    m, eng, groups, nd, ks, psi, where, dense = sw.prepare(Path(stem), True)
    if 'variants' in spec:
        evaluate(m, eng, groups, nd, ks, psi, where, procs, {}, 'base')
        for name, mods in spec['variants'].items():
            evaluate(m, eng, groups, nd, ks, psi, where, procs, mods, name)
    else:
        evaluate(m, eng, groups, nd, ks, psi, where, procs, spec, spec.get('name'))


if __name__ == '__main__':
    main()
