"""Restore identified source parking gates without extending the B deadline."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import contextlib
import copy
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
sys.path.insert(0, str(ROOT / 'work/lanes/NATIVE2_20261027'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit
from measured_assemble import assemble
from pairs import audit as pair_audit


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--a-module', default=str(ROOT / 'work/lanes/NATIVE2_20261027/strong48_m9_herald_a_module.json'))
    ap.add_argument('--b-module', default=str(HERE / 'retimed/strong48_m9_b_reject46.json'))
    ap.add_argument('--source', help='Use an independently verified source with the same data roles')
    ap.add_argument('--variant', choices=['none', 'q12_pair'], default='q12_pair')
    ap.add_argument('--name', default='strong48_restore_q12')
    ap.add_argument('--price', action='store_true')
    args = ap.parse_args()
    adoc = json.loads(Path(args.a_module).read_text())
    bdoc = json.loads(Path(args.b_module).read_text())
    assert adoc['prefix_stem'] == bdoc['prefix_stem']
    old_source = Path(args.source or adoc['prefix_stem'])
    ops, dets = f.parse_current(old_source.with_suffix('.qasm').read_text())
    changes = []
    if args.variant == 'q12_pair':
        matches = [o for o in ops if o.kind == 'MX' and o.qs == (12,) and o.time == 29]
        assert len(matches) == 1
        matches[0].time = 31
        for t in (29, 30):
            ops.append(f.Op('CX', (12, 13), t))
        changes = [dict(kind='MX', qs=[12], old_time=29, new_time=31),
                   dict(kind='CX', qs=[12, 13], restored_times=[29, 30], original_times=[29, 31])]
    occupied = set()
    for o in ops:
        for q in o.qs:
            assert (o.time, q) not in occupied, ('source collision', o, q)
            occupied.add((o.time, q))
    ops.sort(key=lambda o: o.time)
    data = bdoc['roles']['D']
    text = emit(ops, dets)
    raw = raw_check(text, data)
    assert raw['ok'], raw
    source = write_stem(text, data, HERE / 'retimed', args.name + '_source',
                        source=dict(parent=str(old_source), changes=changes, raw=raw))
    for label, doc in [('a', adoc), ('b', bdoc)]:
        doc['prefix_stem'] = str(source)
        (HERE / 'retimed' / f'{args.name}_{label}_module.json').write_text(json.dumps(doc, indent=2) + '\n')
    with contextlib.redirect_stdout(io.StringIO()):
        result = assemble(HERE / 'retimed' / f'{args.name}_a_module.json',
                          HERE / 'retimed' / f'{args.name}_b_module.json',
                          0, 0, args.name, do_singles=True, do_price=args.price)
        if result['raw']['ok'] and result['singles']['c1'] < 1e-10:
            result['pairs'] = pair_audit(result['stem'], HERE / 'retimed' / f'{args.name}.pairs.json')
    receipt = HERE / 'retimed' / f'{args.name}.result.json'
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(receipt=str(receipt), stem=result['stem'], source=str(source),
                         raw=result['raw'], cx=result['cx'], ticks=result['ticks'],
                         singles=result.get('singles'), c2=result.get('pairs', {}).get('c2'),
                         exact=result.get('exact')), indent=2), flush=True)


if __name__ == '__main__':
    main()
