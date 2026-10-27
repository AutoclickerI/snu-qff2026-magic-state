"""Release completed dynamic-flag source wires without a global source wait."""
import json, os, sys
from pathlib import Path
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H.parent / 'PREFIX20261027'))
sys.path.insert(0, str(H.parent / 'T14'))
import synth
from qcirc import parse, save
from search_phase import singles
from qtools import price
from qtools.validity import raw_check
A, D = synth.A, synth.D


def build(stem, name, early=True, dead=True):
    meta = json.loads(stem.with_suffix('.json').read_text())
    cells = meta['synthesis']['cells']
    original, original_dets = parse(stem.with_suffix('.qasm').read_text())
    flagt = next(u['t'] for u in original if u['b'] == 500)
    units = [dict(u) for u in original if u['t'] < flagt and set(u['q']) <= set(cells)]
    _, suffix, dets, _ = synth.split_suffix()
    omit = set()
    removed = []
    for q in cells:
        wire = [u for u in units if q in u['q']]
        if len(wire) >= 2 and wire[0]['k'] in ('R', 'RX') and wire[1]['k'] in ('R', 'RX'):
            units.remove(wire[0]); removed.append(dict(reason='reset before fresh preparation', **wire[0]))
            wire = wire[1:]
        if dead and q not in A + [3] and len(wire) >= 2 and wire[-1]['k'] == 'R' and wire[-2]['k'] == 'MX' and wire[-2]['b'] >= 900:
            future = sorted([u for u in suffix if q in u['q']], key=lambda u: u['t'])
            if q in D or not future or future[0]['k'] in ('R', 'RX'):
                units.remove(wire[-1]); omit.add(q)
                removed.append(dict(reason='discarded state is reset before every later interaction', **wire[-1]))
    # ASAP preserves every remaining per-wire operation order.
    last = {q: -1 for q in range(36)}
    for u in units:
        u['t'] = max(last[q] for q in u['q']) + 1
        for q in u['q']:
            last[q] = u['t']
    for q in cells:
        wire = [u for u in units if q in u['q']]
        if len(wire) >= 2 and wire[0]['k'] in ('R', 'RX'):
            wire[0]['t'] = wire[1]['t'] - 1
    global_read = max(last.values()) + 1
    zero_cells = [q for q in cells if q not in A + [3]]
    final_records = [(3, 'MX', 500)] + [(q, 'M', 600 + j) for j, q in enumerate(zero_cells) if q not in omit]
    for q, k, b in final_records:
        tick = last[q] + 1 if early else global_read
        units.append(dict(k=k, q=(q,), t=tick, b=b)); last[q] = tick
    source_bits = {u['b'] for u in units if u['b'] is not None}
    dets += [d for d in original_dets if set(d) <= source_bits]
    end = {}
    for a, d in zip(A, D):
        tick = max(last[a] + 1, last[d] + 2) if early else global_read + 2
        units += [dict(k='R', q=(d,), t=tick - 1, b=None),
                  dict(k='CX', q=(a, d), t=tick, b=None),
                  dict(k='CX', q=(d, a), t=tick + 1, b=None)]
        last[a] = last[d] = tick + 1
        end[a] = tick + 1
    busy = {q: min(u['t'] for u in suffix if q in u['q']) for q in {q for u in suffix for q in u['q']}}
    shift = max([last[q] + 1 - busy[q] for q in set(cells + D) if q in busy]
                + [-min(u['t'] for u in suffix)])
    for u in suffix:
        u['t'] += shift
    for j, a in enumerate(A):
        if end[a] + 1 < busy.get(a, 999) + shift:
            units.append(dict(k='M', q=(a,), t=end[a] + 1, b=502 + j)); dets.append([502 + j])
    units += suffix
    return save(H / 'cand' / name, units, dets, D,
                dict(source='Dynamic flag with individual wire release', parent=str(stem),
                     early=early, omit_dead_reset=dead, removed=removed,
                     parent_synthesis=meta['synthesis']))


def main():
    out = []
    best = 1.
    for family in ('dynamic9', 'dynamic11'):
        path = H / f'{family}_best.json'
        if not path.exists():
            continue
        stem = Path(json.loads(path.read_text())['stem'])
        for early, dead in ((False, False), (True, False), (False, True), (True, True)):
            name = f'{family}_schedule_e{int(early)}_d{int(dead)}'
            try:
                st = build(stem, name, early, dead)
                raw = raw_check(st.with_suffix('.qasm').read_text(), D)
                row = dict(stem=str(st), parent=str(stem), early=early, dead=dead, raw=raw)
                if raw['ok']:
                    c1, harmful = singles(st); row.update(c1=c1, harmful=harmful)
                    if c1 < 1e-5:
                        p = price(st, 1); row.update(loss=p['loss'], acceptance=p['acceptance'])
                        if p['acceptance'] >= .5002 and p['loss'] < best:
                            best = p['loss']; (H / 'dynamic_schedule_best.json').write_text(json.dumps(row, indent=2) + '\n')
                print(json.dumps(row), flush=True); out.append(row)
            except Exception as ex:
                print('ERROR', name, repr(ex), flush=True); out.append(dict(name=name, error=repr(ex)))
            (H / 'dynamic_schedule_results.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
