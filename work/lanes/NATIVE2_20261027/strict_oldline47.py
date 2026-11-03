"""A strict 11-CX old-line47 instrument after explicit q7/q13 boundary changes.

Keeps q7's source c317 check by moving its measurement earlier after deleting
one ideal-zero-control parking CX. Replaces M13 by a real RX13 and drops c318.
The known phase-guarded gate word is shifted two ticks earlier and reuses only
independently certified source product states. Full raw/F1/pair audits follow.
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
from assemble_48_solution import build as integrate
from idle_parking48 import build as park


def build():
    base = json.loads((HERE / 'cut3_rx9_38_release.json').read_text())
    bdoc = json.loads((HERE / 'cut3_rx9_38_b_module.json').read_text())
    ops, dets = f.parse_current(Path(base['stem']).with_suffix('.qasm').read_text())
    ops, dets = copy.deepcopy(ops), copy.deepcopy(dets)

    def one(kind, qs, tick):
        match = [o for o in ops if o.kind == kind and o.qs == tuple(qs) and o.time == tick]
        assert len(match) == 1, (kind, qs, tick, match)
        return match[0]

    old_park = one('CX', [7, 1], 38)
    ops.remove(old_park)
    m7 = one('M', [7], 39)
    assert m7.bit == 317
    m7.time = 38
    m13 = one('M', [13], 39)
    assert m13.bit == 318
    touched = [sorted(row) for row in dets if 318 in row]
    assert touched == [[318]], touched
    m13.kind, m13.bit = 'RX', None
    dets = [row - {318} for row in dets if row - {318}]
    assert {317} in dets
    ops.sort(key=lambda o: o.time)
    occupied = set()
    for op in ops:
        for q in op.qs:
            assert (op.time, q) not in occupied, ('Source collision', op)
            occupied.add((op.time, q))
    edits = [dict(action='remove', kind='CX', qs=[7, 1], time=38),
             dict(action='move', kind='M', qs=[7], time=39, new_time=38, retained_bit=317),
             dict(action='replace', old_kind='M', new_kind='RX', qs=[13], time=39,
                  removed_bit=318, removed_checks=touched)]
    data = base['data_qubits']
    text = emit(ops, dets)
    raw = raw_check(text, data)
    assert raw['ok'], raw
    policy = 'Changed cut3/RX9 source: keep c317 atM7@38, remove c318 when M13@39 becomes real RX13; delete CX7-to-1@38.'
    stem = write_stem(text, data, HERE / 'boundary', 'strict_oldline47_source',
                     source=dict(parent=base['stem'], edits=edits, raw=raw, acceptance_policy=policy))
    release = {q: max((o.time + 1 for o in ops if q in o.qs), default=0) for q in range(36) if q not in data}
    cert_path = HERE / 'strict_oldline47_product_states.json'
    boundary = dict(stem=str(stem), data_qubits=data, release=release, cx=sum(o.kind == 'CX' for o in ops),
                    raw=raw, edits=edits, acceptance_policy=policy, product_states=str(cert_path))
    boundary_path = HERE / 'strict_oldline47_release.json'
    boundary_path.write_text(json.dumps(boundary, indent=2) + '\n')
    with contextlib.redirect_stdout(io.StringIO()):
        certificate = certify(boundary_path, cert_path)
    cells = {row['q']: row for row in certificate['cells']}
    needed = {7: ('Z', 39), 8: ('Z', 38), 9: ('X', 39), 13: ('X', 40), 15: ('Z', 39)}
    for q, (axis, deadline) in needed.items():
        row = cells[q]
        assert row['release'] <= deadline and row['expectations'][axis] > 1 - 1e-9, (q, row)
    original = ROOT / 'work/lanes/END2_20261027/sol/a_herald_R46_early7_8_no8_jit.json'
    solution = json.loads(original.read_text())
    aops = [dict(row, time=row['time'] - 2) for row in solution['operations']]
    remove = {('R', (8,)), ('RX', (9,)), ('RX', (13,))}
    removed = [row for row in aops if (row['kind'], tuple(row['qs'])) in remove]
    assert len(removed) == 3, removed
    aops = [row for row in aops if row not in removed]
    adoc = dict(status='RETIMED_CERTIFIED_NATIVE_WORD', prefix_stem=str(stem), A=solution['A'],
                operations=aops, logical_x_herald=[7, 8, 9], early_cells=[7, 8], R=44,
                original_solution=str(original), source_product_states=str(cert_path),
                certified_reused_inputs=[dict(q=q, axis=axis, release=cells[q]['release']) for q, (axis, _) in needed.items()],
                omitted_duplicate_or_measured_preparations=removed,
                scope='Known strict11CX phase-guard/no8 word shifted two ticks earlier; actual source/input and full noise must be checked.')
    apath = HERE / 'strict_oldline47_solution.json'
    apath.write_text(json.dumps(adoc, indent=2) + '\n')
    bdoc['prefix_stem'] = str(stem)
    bdoc['source_acceptance_policy'] = policy
    bpath = HERE / 'strict_oldline47_b_module.json'
    bpath.write_text(json.dumps(bdoc, indent=2) + '\n')
    result = integrate(apath, bpath, 'strict_oldline47', end=47)
    result['source_release'] = str(boundary_path)
    result['source_certificate'] = str(cert_path)
    result['source_acceptance_policy'] = policy
    if result['raw']['ok'] and result['singles']['c1'] < 1e-12:
        result['parked'] = park(result['stem'], 3, 0, 'strict_oldline47_park')
    (HERE / 'strict_oldline47_full.result.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    build()
