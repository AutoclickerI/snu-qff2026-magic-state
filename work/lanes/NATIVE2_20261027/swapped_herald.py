"""Reverse the verification order and retain a logical-Z readout on B.

The connected B factory is the physical Hadamard dual of the compact A
factory. Its sole reused zero input q15 becomes a positive X input by an
explicit replacement of the final source M15 with RX15 in the same slot.
"""
import contextlib
import copy
import io
import json
import argparse
import sys
from pathlib import Path
from measured_assemble import assemble, HERE, ROOT
from old_b_new_a import D, A as CONNECTED, B as SPARSE, C
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
from qtools.evaluator import frontend as f
from qtools import write_stem
from qtools.validity import raw_check
from joint import emit


def build(solution=None, name='swapped_logical_herald'):
    adoc = json.loads((HERE / 'dual_old_a_module.json').read_text())
    source = Path(adoc['prefix_stem'])
    if solution:
        new_source = source
        sol = json.loads(Path(solution).read_text())
        bops = copy.deepcopy(sol['operations'])
        source_change = None
    else:
        ops, dets = f.parse_current(source.with_suffix('.qasm').read_text())
        op = next(o for o in ops if o.bit == 322)
        assert op.kind == 'M' and op.qs == (15,) and op.time == 40
        op.kind, op.bit = 'RX', None
        dets = [r - {322} for r in dets if r - {322}]
        text = emit(ops, dets)
        raw = raw_check(text, D)
        assert raw['ok'], raw
        new_source = write_stem(text, D, HERE / 'boundary', 'swapped_herald_source',
                                source=dict(original=str(source), replace_record=322, operation='RX15@40', raw=raw))
        sol = json.loads((HERE.parent / 'END2_20261027/sol/a_plus_R45.json').read_text())
        dual = {'R': 'RX', 'RX': 'R', 'M': 'MX', 'MX': 'M'}
        bops = []
        for row in sol['operations']:
            r = copy.deepcopy(row)
            if r['kind'] == 'CX':
                r['qs'].reverse()
            else:
                r['kind'] = dual.get(r['kind'], r['kind'])
            bops.append(r)
        source_change = 'Final deterministic source M15@40 is replaced with RX15@40; record322 is removed from detector parities.'
    bops += [dict(kind='CX', qs=[CONNECTED[i], D[i]], time=45 if i in (0, 4) else 46) for i in range(7)]
    bops += [dict(kind='CX', qs=[7, 8], time=46), dict(kind='CX', qs=[8, 9], time=47)]
    bops += [dict(kind='MX', qs=[q], time=47) for q in (14, 7, 13, 21, 15)]
    bops += [dict(kind='M', qs=[9], time=48), dict(kind='MX', qs=[8], time=48)]
    term = [('CX', [d, a], 0, None) for d, a in zip(D, SPARSE)]
    term += [('M', [q], 1, i) for i, q in enumerate(SPARSE)]
    bdoc = dict(prefix_stem=str(new_source), roles=dict(D=D, A=SPARSE, B=CONNECTED, C=C),
                square_mask=0, terminal_operations=term, candidates=[dict(operations=bops)],
                source_change=source_change, solution=str(solution) if solution else None,
                scope='Complete reversed-order B instrument with logical-Z herald.')
    adoc['prefix_stem'] = str(new_source)
    apath = HERE / f'{name}_a_module.json'
    bpath = HERE / f'{name}_b_module.json'
    apath.write_text(json.dumps(adoc, indent=2) + '\n')
    bpath.write_text(json.dumps(bdoc, indent=2) + '\n')
    with contextlib.redirect_stdout(io.StringIO()):
        result = assemble(apath, bpath, 0, 0, name, terminal_start=47, do_singles=True)
    (HERE / f'{name}.result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({**{k: result[k] for k in ('stem', 'raw', 'cx', 'ticks')},
                      'c1': result.get('singles', {}).get('c1')}, indent=2), flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--solution')
    ap.add_argument('--name', default='swapped_logical_herald')
    args = ap.parse_args()
    build(args.solution, args.name)
