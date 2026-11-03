"""Screen native identity interactions in vacant slots of a complete 48-tick circuit.

Plus-state spare targets preserve the ideal data channel and are read in X.
Two repeated data-to-A CXs also preserve the channel exactly; every inserted
gate retains its full noise. The full raw/single/pair tests rank the experiment.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import contextlib
import io
import json
import sys
from pathlib import Path
from measured_assemble import HERE, ROOT
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/PREFIX2_20261027'))
sys.path.insert(0, str(ROOT / 'work/lanes/REBUILD20261027'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit
from record_contract import singles
from pairs import audit


def build(stem, ancilla_mask=3, pair_mask=0, name=None, herald_mask=None):
    stem = Path(stem)
    data = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    ops, dets = f.parse_current(stem.with_suffix('.qasm').read_text())
    occupied = {(o.time, q) for o in ops for q in o.qs}
    end = max(o.time for o in ops) + 1
    assert end in (47, 48), end
    record = max(o.bit or 0 for o in ops) + 1
    added = []
    if herald_mask is None:
        herald_mask = ancilla_mask
    assert herald_mask & ~ancilla_mask == 0
    for i, (d, q, reset) in enumerate([(6, 0, 37), (2, 1, 40)]):
        if not (ancilla_mask >> i & 1):
            continue
        assert not any((t, q) in occupied for t in range(reset, end - 1)), (q, reset)
        added.append(f.Op('RX', (q,), reset))
        for tick in range(reset + 1, end - 2):
            if (tick, d) not in occupied:
                added.append(f.Op('CX', (d, q), tick))
        added.append(f.Op('MX', (q,), end - 2, record))
        if herald_mask >> i & 1:
            dets.append({record})
        record += 1
    for i, (d, a) in enumerate([(19, 13), (20, 14), (22, 21)]):
        if not (pair_mask >> i & 1):
            continue
        for tick in (end - 5, end - 4):
            assert (tick, d) not in occupied and (tick, a) not in occupied, (d, a, tick)
            added.append(f.Op('CX', (d, a), tick))
    for op in added:
        for q in op.qs:
            assert (op.time, q) not in occupied, (op, q)
            occupied.add((op.time, q))
    ops += added
    ops.sort(key=lambda o: o.time)
    text = emit(ops, dets)
    raw = raw_check(text, data)
    name = name or f'park48_a{ancilla_mask}_p{pair_mask}_h{herald_mask}'
    out = write_stem(text, data, HERE / 'boundary', name,
                     source=dict(parent=str(stem), ancilla_mask=ancilla_mask, pair_mask=pair_mask, herald_mask=herald_mask,
                                 added=[dict(kind=o.kind, qs=list(o.qs), time=o.time, bit=o.bit) for o in added],
                                 policy='Retain the parent detector subspace; additionally check selected plus spare X reads per herald_mask.'))
    result = dict(stem=str(out), parent=str(stem), raw=raw,
                  cx=sum(o.kind == 'CX' for o in ops), ticks=max(o.time for o in ops) + 1,
                  ancilla_mask=ancilla_mask, pair_mask=pair_mask, herald_mask=herald_mask,
                  added_cx=sum(o.kind == 'CX' for o in added))
    if raw['ok']:
        f.DATA = data
        result['singles'] = singles(f.make_model(*f.parse_current(text)))
        if result['singles']['c1'] < 1e-12:
            with contextlib.redirect_stdout(io.StringIO()):
                pair = audit(out, HERE / f'{name}.pairs.json')
            result['c2'] = pair['c2']
    (HERE / f'{name}.result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stem')
    ap.add_argument('--ancilla-mask', type=int, default=3)
    ap.add_argument('--pair-mask', type=int, default=0)
    ap.add_argument('--name')
    ap.add_argument('--herald-mask', type=int)
    args = ap.parse_args()
    build(args.stem, args.ancilla_mask, args.pair_mask, args.name, args.herald_mask)
