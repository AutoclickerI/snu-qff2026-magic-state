"""Combine a compact A factory with the incumbent logical-X A readout.

The data taps are staggered so the two native readout-decoder CXs fit before
the incumbent final tick. The resulting MX9 is the missing phase herald;
reading every A qubit in Z would discard it.
"""
import argparse
import contextlib
import copy
import io
import json
from pathlib import Path
from measured_assemble import assemble, HERE, ROOT
from old_b_new_a import old_b, A, B, C, D


def build(a_solution, name='compact_a_logical_read', price=False, two_heralds=False):
    solution = json.loads(Path(a_solution).read_text())
    assert solution['A'] == A
    for q in A:
        deadline = 45 if q in (7, 8) or two_heralds and q != 9 else 46
        assert max((o['time'] for o in solution['operations'] if q in o['qs']), default=-1) < deadline, (q, deadline)
    aops = copy.deepcopy(solution['operations'])
    early = {0, 1, 2, 4, 5, 6} if two_heralds else {0, 4}
    aops += [dict(kind='CX', qs=[D[i], A[i]], time=45 if i in early else 46) for i in range(7)]
    aops += [dict(kind='CX', qs=[8, 7], time=46), dict(kind='CX', qs=[9, 8], time=47)]
    if two_heralds:
        aops += [dict(kind='CX', qs=[14, 13], time=46),
                 dict(kind='CX', qs=[15, 21], time=46),
                 dict(kind='CX', qs=[14, 15], time=47)]
        aops += [dict(kind='M', qs=[q], time=47) for q in (7, 13, 21)]
        aops += [dict(kind='MX', qs=[q], time=48) for q in (9, 14)]
        aops += [dict(kind='M', qs=[q], time=48) for q in (8, 15)]
    else:
        aops += [dict(kind='M', qs=[q], time=47) for q in (14, 7, 13, 21, 15)]
        aops += [dict(kind='MX', qs=[9], time=48), dict(kind='M', qs=[8], time=48)]
    bdoc = json.loads(old_b().read_text())
    bdoc['terminal_operations'] = [('CX', [b, d], 0, None) for b, d in zip(B, D)]
    bdoc['terminal_operations'] += [('MX', [q], 1, 7 + i) for i, q in enumerate(B)]
    adoc = dict(prefix_stem=bdoc['prefix_stem'], candidates=[dict(A=A, operations=aops)],
                source_solution=str(a_solution), two_heralds=two_heralds,
                scope='Compact A plusL preparation followed by staggered data taps and logical-X readout.')
    apath = HERE / f'{name}_a_module.json'
    bpath = HERE / f'{name}_b_module.json'
    apath.write_text(json.dumps(adoc, indent=2) + '\n')
    bpath.write_text(json.dumps(bdoc, indent=2) + '\n')
    with contextlib.redirect_stdout(io.StringIO()):
        result = assemble(apath, bpath, 0, 0, name, terminal_start=47,
                          do_singles=True, do_price=price)
    path = HERE / f'{name}.result.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    out = {k: result[k] for k in ('stem', 'raw', 'cx', 'ticks')}
    out['c1'] = result.get('singles', {}).get('c1')
    if 'exact' in result:
        out['exact'] = result['exact']
    print(json.dumps(out, indent=2), flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('a_solution')
    ap.add_argument('--name', default='compact_a_logical_read')
    ap.add_argument('--price', action='store_true')
    ap.add_argument('--two-heralds', action='store_true')
    args = ap.parse_args()
    build(args.a_solution, args.name, args.price, args.two_heralds)
