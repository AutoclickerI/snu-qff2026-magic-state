"""Restore the source's q19->q25 parking pair while releasing q25 at30.

All source operations retain their order on every physical wire relative to
the source with the original pair restored at29/30. Only independent operations
cross in the resulting schedule. No source gate or record is removed.
"""
import copy
import json
import os
import sys
from pathlib import Path

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit


def main():
    parent_module = HERE.parent / 'NATIVE2_20261027/strong48_m9_herald_b_module.json'
    parent = Path(json.loads(parent_module.read_text())['prefix_stem'])
    ops, dets = f.parse_current(parent.with_suffix('.qasm').read_text())
    for time in (29, 30):
        assert not any(op.kind == 'CX' and op.qs == (19, 25) and op.time == time for op in ops)
        ops.append(f.Op('CX', (19, 25), time))
    ops.sort(key=lambda op: op.time)
    reference = copy.deepcopy(ops)
    moves = [((24, 25), 23, 22), ((24, 25), 24, 23),
             ((19, 25), 25, 24), ((19, 25), 26, 25),
             ((24, 30), 26, 25), ((24, 25), 27, 26),
             ((24, 25), 28, 27), ((19, 25), 29, 28),
             ((19, 25), 30, 29)]
    # Select all source operations before changing any timestamps.
    selected = []
    for qs, before, after in moves:
        matches = [op for op in ops if (op.kind, op.qs, op.time) == ('CX', qs, before)]
        assert len(matches) == 1, (qs, before, matches)
        selected.append((matches[0], after))
    for op, after in selected:
        op.time = after
    ops.sort(key=lambda op: op.time)
    occupied = set()
    for op in ops:
        for q in op.qs:
            assert (op.time, q) not in occupied, ('collision', q, op.time)
            occupied.add((op.time, q))
    preserved = []
    for q in range(36):
        def history(source):
            return [(op.kind, op.qs, op.bit) for op in source if q in op.qs]
        assert history(reference) == history(ops), ('wire order changed', q)
        preserved.append(q)
    assert max(op.time for op in ops if 25 in op.qs) == 29
    text = emit(ops, dets)
    data = [6, 20, 19, 10, 2, 22, 16]
    raw = raw_check(text, data)
    assert raw['ok'], raw
    changes = [dict(kind='CX', qs=list(qs), before=before, after=after)
               for qs, before, after in moves]
    metadata = dict(parent=str(parent), restored=[dict(kind='CX', qs=[19, 25], time=t) for t in (29, 30)],
                    moves=changes, all_wire_orders_preserved=preserved, raw=raw,
                    q25_release=30, source_records_unchanged=True,
                    scope='Noisy source schedule witness only; full native B/A integration and price are separate.')
    stem = write_stem(text, data, HERE / 'boundary', 'source_restore25_early', source=metadata)
    result = dict(stem=str(stem), cx=sum(op.kind == 'CX' for op in ops), **metadata)
    (HERE / 'restore25_schedule.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
