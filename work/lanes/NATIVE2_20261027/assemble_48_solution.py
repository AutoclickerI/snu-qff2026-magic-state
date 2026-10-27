"""Integrate a certified early A solution with a complete 48-tick B module."""
import argparse
import contextlib
import copy
import io
import json
import sys
from pathlib import Path
from measured_assemble import HERE, ROOT, assemble
from old_b_new_a import A, D
sys.path.insert(0, str(ROOT / 'work/lanes/PREFIX2_20261027'))
from pairs import audit


def build(a_solution, b_module, name, do_price=False, prefix_boundary=None, end=48):
    solution = json.loads(Path(a_solution).read_text())
    bdoc = json.loads(Path(b_module).read_text())
    assert solution['A'] == A
    before = Path(solution['prefix_stem'])
    after = Path(bdoc['prefix_stem'])
    if not before.is_absolute():
        before = ROOT / before
    if not after.is_absolute():
        after = ROOT / after
    assert before.with_suffix('.qasm').read_bytes() == after.with_suffix('.qasm').read_bytes(), 'Different source prefixes'
    operations = copy.deepcopy(solution['operations'])
    shift = end - 48
    adaptation = None
    if prefix_boundary:
        boundary = json.loads(Path(prefix_boundary).read_text())
        certificate = json.loads(Path(boundary['product_states']).read_text())
        cells = {row['q']: row for row in certificate['cells']}
        inputs = []
        for q in A:
            ordered = sorted((o for o in operations if q in o['qs']), key=lambda o: o['time'])
            assert ordered and ordered[0]['time'] >= int(boundary['release'][str(q)]), (q, ordered)
            if ordered[0]['kind'] in ('R', 'RX'):
                continue
            want = 'X' if int(solution['initial_rows'][str(q)]) else 'Z'
            cell = cells[q]
            assert cell['product_axis'] == want and not cell['phase_xor'] and cell['phase_constant'] == 0, (q, want, cell)
            inputs.append(dict(q=q, axis=want, expectation=cell['expectations'][want]))
        adaptation = dict(original_prefix=str(before), boundary=str(prefix_boundary),
                          certificate=boundary['product_states'], reused_inputs=inputs,
                          note='Changed physical source; certify all unreinitialized A inputs, then recheck complete native output and faults.')
        after = Path(boundary['stem'])
        bdoc['prefix_stem'] = str(after)
    herald = set(solution.get('logical_x_herald', [7, 8, 9]))
    if herald == {7, 8, 9}:
        early, decoder, root, last_z = {7, 8}, [(8, 7), (9, 8)], 9, 8
    elif herald == {8, 14, 15}:
        early, decoder, root, last_z = {8, 14}, [(14, 8), (15, 14)], 15, 14
    else:
        raise ValueError(('Unsupported two-layer logical readout', herald))
    for q in A:
        ready = max((o['time'] + 1 for o in operations if q in o['qs']), default=0)
        assert ready <= (44 if q in early else 45) + shift, (q, ready)
    operations += [dict(kind='CX', qs=[d, a], time=(44 if a in early else 45) + shift) for d, a in zip(D, A)]
    operations += [dict(kind='CX', qs=list(edge), time=45 + shift + i) for i, edge in enumerate(decoder)]
    operations += [dict(kind='M', qs=[q], time=46 + shift) for q in A if q not in (root, last_z)]
    operations += [dict(kind='MX', qs=[root], time=47 + shift), dict(kind='M', qs=[last_z], time=47 + shift)]
    adoc = dict(prefix_stem=str(after), source_solution=str(a_solution),
                candidates=[dict(A=A, operations=operations)],
                logical_x_herald=sorted(herald), early_data_cells=sorted(early),
                boundary_adaptation=adaptation,
                scope=f'Native A plusL preparation with selected early data taps and logical-X readout by tick{end-1}.')
    apath = HERE / f'{name}_a_module.json'
    bpath = HERE / f'{name}_b_module.json'
    apath.write_text(json.dumps(adoc, indent=2) + '\n')
    bpath.write_text(json.dumps(bdoc, indent=2) + '\n')
    with contextlib.redirect_stdout(io.StringIO()):
        result = assemble(apath, bpath, 0, 0, name, terminal_start=46 + shift,
                          do_singles=True, do_price=do_price)
    if result['raw']['ok'] and result['singles']['c1'] < 1e-12:
        with contextlib.redirect_stdout(io.StringIO()):
            pairs = audit(result['stem'], HERE / f'{name}.pairs.json')
        result['c2'] = pairs['c2']
    (HERE / f'{name}.result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('stem', 'raw', 'cx', 'ticks', 'singles', 'c2', 'exact') if k in result}, indent=2), flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('a_solution')
    ap.add_argument('b_module')
    ap.add_argument('--name', required=True)
    ap.add_argument('--price', action='store_true')
    ap.add_argument('--prefix-boundary')
    ap.add_argument('--end', type=int, default=48)
    args = ap.parse_args()
    build(args.a_solution, args.b_module, args.name, args.price, args.prefix_boundary, args.end)
