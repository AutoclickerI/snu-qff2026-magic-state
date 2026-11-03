"""Advance the source's q9-to-q15-to-q16 transfer and certify q15 zero at39.

Preserves the B-ready45 source changes. The data transfer is reordered on its
exact linear map; selected identity parking gates are physically removed and
their full noisy effect is assessed only after complete native integration.
"""
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
from measured_assemble import HERE, ROOT
sys.path.insert(0, str(ROOT / 'work/tools'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit
from boundary_product import certify
from assemble_48_solution import build as assemble_solution


def build(extra_zero_cuts=False, integrate=False):
    bbase = ROOT / 'work/lanes/PREFIX2_20261027/retimed/b45_alap_b_module.json'
    bdoc = json.loads(bbase.read_text())
    parent = Path(bdoc['prefix_stem'])
    ops, dets = f.parse_current(parent.with_suffix('.qasm').read_text())
    ops, dets = copy.deepcopy(ops), copy.deepcopy(dets)
    edits = []

    def find(kind, qs, tick):
        match = [o for o in ops if o.kind == kind and o.qs == tuple(qs) and o.time == tick]
        assert len(match) == 1, (kind, qs, tick, match)
        return match[0]

    def drop(qs, tick):
        op = find('CX', qs, tick)
        ops.remove(op)
        edits.append(dict(action='remove', kind='CX', qs=qs, time=tick))

    def move(kind, qs, tick, new_tick):
        op = find(kind, qs, tick)
        op.time = new_tick
        edits.append(dict(action='move', kind=kind, qs=qs, time=tick, new_time=new_tick, bit=op.bit))

    drop([15, 21], 35)
    drop([10, 16], 36)
    drop([10, 16], 37)
    if extra_zero_cuts:
        drop([16, 15], 34)
        drop([16, 10], 35)
    move('CX', [9, 15], 36, 35)
    move('CX', [9, 8], 35, 36)
    move('M', [8], 36, 37)
    move('CX', [15, 16], 38, 36)
    move('CX', [16, 15], 39, 38)
    seen = set()
    for op in ops:
        for q in op.qs:
            assert (op.time, q) not in seen, ('Source collision', op)
            seen.add((op.time, q))
    ops.sort(key=lambda o: o.time)
    data = bdoc['roles']['D']
    text = emit(ops, dets)
    raw = raw_check(text, data)
    assert raw['ok'], raw
    name = f'q15_early39_cut{5 if extra_zero_cuts else 3}'
    stem = write_stem(text, data, HERE / 'boundary', name + '_source',
                     source=dict(parent=str(parent), edits=edits, raw=raw,
                                 scope='Source transfer and real identity-gate deletions. NativeB45 changes retained.'))
    release = {q: max((o.time + 1 for o in ops if q in o.qs), default=0) for q in range(36) if q not in data}
    cert_path = HERE / f'{name}_product_states.json'
    boundary = dict(stem=str(stem), data_qubits=data, release=release, cx=sum(o.kind == 'CX' for o in ops),
                    raw=raw, edits=edits, product_states=str(cert_path))
    boundary_path = HERE / f'{name}_release.json'
    boundary_path.write_text(json.dumps(boundary, indent=2) + '\n')
    with contextlib.redirect_stdout(io.StringIO()):
        certificate = certify(boundary_path, cert_path)
    q15 = next(r for r in certificate['cells'] if r['q'] == 15)
    assert q15['release'] == 39 and q15['product_axis'] == 'Z' and q15['expectations']['Z'] > 1 - 1e-9
    bdoc['prefix_stem'] = str(stem)
    bpath = HERE / f'{name}_b_module.json'
    bpath.write_text(json.dumps(bdoc, indent=2) + '\n')
    out = dict(name=name, source=str(stem), boundary=str(boundary_path), certificate=str(cert_path),
               b_module=str(bpath), source_cx=boundary['cx'], q15=q15,
               a_release={q: release[q] for q in bdoc['roles']['A']})
    print(json.dumps(out, indent=2), flush=True)
    if integrate:
        original = ROOT / 'work/lanes/END2_20261027/sol/a_herald_R45_early8_14_no8_earlysource_hx8_14_15_native_m9_h82.json'
        adoc = json.loads(original.read_text())
        adoc['prefix_stem'] = str(stem)
        adoc['source_original_solution'] = str(original)
        adoc['product_states'] = str(cert_path)
        adoc['R'] -= 1
        adoc['t0'] -= 1
        for row in adoc['operations']:
            row['time'] -= 1
        adoc['actual_ready'] = {q: value - 1 for q, value in adoc['actual_ready'].items()}
        adoc['a_ready'] -= 1
        apath = HERE / f'{name}_a9_R44.json'
        apath.write_text(json.dumps(adoc, indent=2) + '\n')
        result = assemble_solution(apath, bpath, f'full47_{name}', end=47)
        out['full'] = result
    (HERE / f'{name}.result.json').write_text(json.dumps(out, indent=2) + '\n')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--extra-zero-cuts', action='store_true')
    ap.add_argument('--integrate', action='store_true')
    args = ap.parse_args()
    build(args.extra_zero_cuts, args.integrate)
