"""Conjugate the old B factory into a phase-protected sparse A factory.

This is a new noisy circuit, not a noise-equivalence claim. Two final source
Z heralds are replaced by RX, and two old state-identity factory CXs become
RX boundary preparations. All changes are explicit and independently replayed.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import copy
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
sys.path.insert(0, str(ROOT / 'work/lanes/REBUILD20261027'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from tprep.qasm import to_stim
from tprep.exact import run
from joint import emit
from record_contract import complete
from old_b_new_a import old_b, A as CONNECTED, B as SPARSE, C, D


def build():
    old_doc = json.loads(old_b().read_text())
    source = Path(old_doc['prefix_stem'])
    prefix, dets = f.parse_current(source.with_suffix('.qasm').read_text())
    removed, source_changes = [], []
    for q in (11, 5):
        op = max((o for o in prefix if q in o.qs), key=lambda o: o.time)
        assert op.kind == 'M' and op.qs == (q,), op
        removed.append(op.bit)
        source_changes.append(dict(qubit=q, time=op.time, original_kind=op.kind,
                                   original_bit=op.bit, new_kind='RX'))
        op.kind, op.bit = 'RX', None
    dets = [r - set(removed) for r in dets if r - set(removed)]
    text = emit(prefix, dets)
    source_raw = raw_check(text, D)
    assert source_raw['ok'], source_raw
    new_source = write_stem(text, D, HERE / 'boundary', 'dual_factory_source',
                            source=dict(original=str(source), changes=source_changes, raw=source_raw))
    operations, changes = [], []
    dual = {'R': 'RX', 'RX': 'R', 'M': 'MX', 'MX': 'M'}
    for row in old_doc['candidates'][0]['operations']:
        r = copy.deepcopy(row)
        if (r['time'], r['kind'], tuple(r['qs'])) in ((39, 'CX', (3, 4)), (33, 'CX', (24, 18))):
            q = r['qs'][0]
            changes.append(dict(original=r, new_kind='RX', qubit=q))
            r = dict(time=r['time'], kind='RX', qs=[q])
        elif r['kind'] == 'CX':
            r['qs'] = list(reversed(r['qs']))
        else:
            r['kind'] = dual.get(r['kind'], r['kind'])
        operations.append(r)
    doc = dict(prefix_stem=str(new_source), roles=dict(D=D, A=SPARSE, B=CONNECTED, C=C),
               source_changes=source_changes, factory_boundary_changes=changes,
               target='A plusL up to harmless recorded X shifts, obtained by dualizing the old B factory.',
               candidates=[dict(A=SPARSE, operations=operations,
                               cx=sum(o['kind'] == 'CX' for o in operations),
                               resource_ready=47, module_end=48)])
    path = HERE / 'dual_old_a_module.json'
    path.write_text(json.dumps(doc, indent=2) + '\n')
    ops = copy.deepcopy(prefix)
    first = max((o.bit for o in ops if o.bit is not None), default=-1) + 1
    bit = first
    for row in operations:
        rec = bit if row['kind'] in ('M', 'MX') else None
        ops.append(f.Op(row['kind'], tuple(row['qs']), row['time'], rec))
        bit += rec is not None
    seen = set()
    for o in ops:
        for q in o.qs:
            assert (o.time, q) not in seen, ('collision', o)
            seen.add((o.time, q))
    ops.sort(key=lambda o: o.time)
    f.DATA = D
    affine = complete(f.make_model(*f.parse_current(emit(ops, dets))), dets)
    rows = [r for r in affine['missing'] if any(b >= first for b in r['bits'])]
    assert all(not r['reference'] for r in rows)
    dets += [set(r['bits']) for r in rows]
    text = emit(ops, dets)
    raw = raw_check(text, D)
    native, errors = to_stim(text)
    assert not errors, errors
    state, inverse, records, detectors, wires = run(native, 36)
    checks = []
    for mask in (85, 102, 120, 7):
        p = state.stim.PauliString(state.n)
        for i, q in enumerate(SPARSE):
            if mask >> i & 1:
                p[wires[q]] = 'X'
        checks.append(dict(mask=mask, value=float(state.expectation(p, inverse))))
    result = dict(module=str(path), raw=raw, resource_x_stabilizers=checks,
                  phase_resource_ok=all(abs(c['value'] - 1) < 1e-9 for c in checks),
                  cx=doc['candidates'][0]['cx'], source_changes=source_changes,
                  factory_boundary_changes=changes, extra_record_checks=rows,
                  scope='Raw source and A phase-stabilizer certificate only. Full swapped terminal and noise still require a native B factory.')
    stem = write_stem(text, D, HERE / 'boundary', 'dual_old_a_verified', source=result)
    result['stem'] = str(stem)
    path.with_suffix('.certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == '__main__':
    build()
