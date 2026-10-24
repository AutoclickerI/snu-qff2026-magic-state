"""A readout-tail edits on a base stem: remove terminal edges, rebuild detectors (dets.complete), price all orders."""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/T14')
import qcirc, dets, allorders


def edit(base, stem, remove=(), move=()):
    units, rows = qcirc.parse(Path(base).with_suffix('.qasm').read_text())
    data = json.loads(Path(base).with_suffix('.json').read_text())['data_qubits']
    nb = max(u['b'] for u in units if u['b'] is not None) + 1
    out = []
    for u in units:
        if (u['k'], u['q'], u['t']) in remove: continue
        for (k, q, t, t2) in move:
            if (u['k'], u['q'], u['t']) == (k, q, t): u = dict(u, t=t2)
        out.append(u)
    out.sort(key=lambda u: u['t'])
    qcirc.save(stem, out, rows, data, meta=dict(source=f'{base} tail edit', remove=list(remove), move=list(move), R=44), nbits=nb)
    newrows, g = dets.complete(stem, rows, base)
    qcirc.save(stem, out, newrows, data, meta=dict(source=f'{base} tail edit', remove=list(remove), move=list(move), R=44), nbits=nb)
    return stem, len(rows), len(newrows)


if __name__ == '__main__':
    base, procs = sys.argv[1], int(sys.argv[2])
    (HERE / 'tail').mkdir(exist_ok=True)
    E = {
        'no1415': dict(remove=[('CX', (14, 15), 45)]),
        'no1716': dict(remove=[('CX', (17, 16), 45)]),
        'no_both': dict(remove=[('CX', (14, 15), 45), ('CX', (17, 16), 45)]),
        'no1415_m14at45': dict(remove=[('CX', (14, 15), 45)], move=[('M', (14,), 46, 45)]),
    }
    b0 = allorders.run(base, procs)
    print(json.dumps(dict(base=b0['loss'], acc=b0['acceptance'])), flush=True)
    for n, e in E.items():
        stem, r0, r1 = edit(base, HERE / 'tail' / n, **e)
        try:
            r = allorders.run(stem, procs)
            print(json.dumps(dict(name=n, rows=[r0, r1], loss=r['loss'], acceptance=r['acceptance'], dloss=r['loss'] - b0['loss'])), flush=True)
        except Exception as ex:
            print(json.dumps(dict(name=n, rows=[r0, r1], error=repr(ex)[:300])), flush=True)


def drop_new_rows(base, stem, procs):
    """Price the edited stem with each row that is not in the base set removed (and all of them)."""
    _, base_rows = qcirc.parse(Path(base).with_suffix('.qasm').read_text())
    units, rows = qcirc.parse(Path(stem).with_suffix('.qasm').read_text())
    meta = json.loads(Path(stem).with_suffix('.json').read_text())
    bs = {tuple(sorted(r)) for r in base_rows}
    new = [r for r in rows if tuple(sorted(r)) not in bs]
    nb = max(u['b'] for u in units if u['b'] is not None) + 1
    out = []
    for k, sub in [(f'drop{i}', [r]) for i, r in enumerate(new)] + [('dropall', new)]:
        rr = [r for r in rows if r not in sub]
        s2 = Path(str(stem) + '_' + k)
        qcirc.save(s2, units, rr, meta['data_qubits'], meta=dict(meta, dropped_rows=sub), nbits=nb)
        try:
            r = allorders.run(s2, procs)
            out.append(dict(name=s2.name, dropped=sub, loss=r['loss'], acceptance=r['acceptance']))
        except Exception as ex:
            out.append(dict(name=s2.name, dropped=sub, error=repr(ex)[:200]))
        print(json.dumps(out[-1]), flush=True)
    return out
