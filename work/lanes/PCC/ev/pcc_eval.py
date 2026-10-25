"""All-orders loss of a PCC build with chosen channels removed exactly (counterfactual driver, based on region.py).

usage: pcc_eval.py <stem> <spec.json | '{json}'> <procs>
spec keys (all optional):
  ins_tick: T      every non-idle channel of an op at native step T is dropped, and every idle run that spans step T is
                   shortened by one step (dropped if it becomes empty): the tick is removed from the noise model.
  drop_qubits: [q] every channel whose qubits meet this set is dropped (idle runs included).
  drop_ops: [[t, [qs]], ...]   non-idle channels (gate, init, measurement flip, after-measurement) of the native op at
                   step t on exactly these qubits are dropped; idle runs are kept.
  drop_idle: [[q, t], ...]     the idle run of qubit q that spans step t is dropped.
  keep_ops: [[t, [qs]], ...]   non-idle channels of these ops are kept whatever the rules above say.
Prints one JSON line with acceptance and loss.  Idle channels are identified exactly from the schedule's gap list.
"""
import sys, json, time
from pathlib import Path
import sparse_walsh as sw
import frontend as fa
from judge_subset.noise import _repeated


def run(stem, spec, procs):
    start = time.perf_counter()
    m, eng, groups, nd, ks, psi, where, dense = sw.prepare(Path(stem), True)
    prog, blocks = fa.noise_blocks(m.native, .001, first_order=False)
    _, steps, gaps = fa.schedule(m.native)
    for ii, groups_ in enumerate(steps):
        for _, st in groups_:
            assert m.labels[ii].time == st, ('parse time != native step', ii, m.labels[ii], st)
    gby = {}
    for i, q, t0, n in gaps:                 # noise_blocks appends idle lines in sorted gap order
        gby.setdefault(i, []).append((q, t0, n))
    T = spec.get('ins_tick')
    dq = set(spec.get('drop_qubits', []))
    dops = {(t, tuple(qs)) for t, qs in spec.get('drop_ops', [])}
    didle = {(q, t) for q, t in spec.get('drop_idle', [])}
    kops = {(t, tuple(qs)) for t, qs in spec.get('keep_ops', [])}   # overrides every drop rule for these ops
    keep, stats = {}, dict(dropped=0, shortened=0)
    for c, fs in groups.items():
        ch = m.chans[c]
        ii, jl = ch['ins'], ch['jl']
        op = m.labels[ii]
        ng = len(gby.get(ii, []))
        idle = None
        if jl >= len(blocks[ii]) - ng:
            q, t0, n = gby[ii][jl - (len(blocks[ii]) - ng)]
            assert ch['name'] == 'DEPOLARIZE1' and ch['qs'] == [q], (ch, q)
            idle = (q, t0, n)
        if idle is None and (op.time, tuple(op.qs)) in kops:
            keep[c] = fs
            continue
        if set(ch['qs']) & dq:
            stats['dropped'] += 1
            continue
        if idle is None:
            if (T is not None and op.time == T) or (op.time, tuple(op.qs)) in dops:
                stats['dropped'] += 1
                continue
            keep[c] = fs
            continue
        q, t0, n = idle
        if any(qq == q and t0 <= tt < t0 + n for qq, tt in didle):
            stats['dropped'] += 1
            continue
        if T is not None and t0 <= T < t0 + n:
            if n == 1:
                stats['dropped'] += 1
                continue
            p_new = _repeated(.001, n - 1, False)
            assert abs(ch['p'] - _repeated(.001, n, False)) < 1e-15
            ch['p'] = p_new
            fs = [dict(f, p=p_new / len(fs)) for f in fs]
            stats['shortened'] += 1
        keep[c] = fs
    compiled, elim = sw.compile_best(m, eng, keep, nd, ks)
    keys = [None] + eng.keys
    sw._CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
    import multiprocessing as mp
    with mp.get_context('fork').Pool(procs) as pool:
        rows = list(pool.imap(sw._row, keys))
    A = rows[0]['value']
    obs = sum(w * b * r['value'] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
    out = dict(stem=str(stem), spec=spec.get('name'), channels=len(groups), **stats,
               acceptance=A, loss=(A - obs) / (2 * A), seconds=time.perf_counter() - start)
    print(json.dumps(out), flush=True)
    return out


if __name__ == '__main__':
    a = sys.argv[2]
    spec = json.loads(a) if a.lstrip().startswith('{') else json.loads(Path(a).read_text())
    run(sys.argv[1], spec, int(sys.argv[3]))
