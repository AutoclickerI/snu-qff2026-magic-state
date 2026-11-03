"""Release q9 in plus at39 with a real RX38 and explicitly drop source c321.

Starts from the certified q15-early39 cut3 source and the rejection-optimized
B-ready45 module. This replaces two physical operations by one noisy reset;
it does not invoke a free standalone H or claim unchanged acceptance.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
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


def build():
    base = json.loads((HERE / 'q15_early39_cut3_release.json').read_text())
    bdoc = json.loads((HERE / 'q15_early39_cut3_b_reject_module.json').read_text())
    parent = Path(base['stem'])
    ops, dets = f.parse_current(parent.with_suffix('.qasm').read_text())
    ops, dets = copy.deepcopy(ops), copy.deepcopy(dets)
    h = [o for o in ops if o.kind == 'H' and o.qs == (9,) and o.time == 38]
    m = [o for o in ops if o.kind == 'MX' and o.qs == (9,) and o.time == 39]
    assert len(h) == len(m) == 1
    bit = m[0].bit
    assert bit == 321
    touched = [sorted(row) for row in dets if bit in row]
    assert touched == [[321]], touched
    h[0].kind = 'RX'
    ops.remove(m[0])
    dets = [row - {bit} for row in dets if row - {bit}]
    ops.sort(key=lambda o: o.time)
    occupied = set()
    for op in ops:
        for q in op.qs:
            assert (op.time, q) not in occupied, ('Collision', op)
            occupied.add((op.time, q))
    data = base['data_qubits']
    text = emit(ops, dets)
    raw = raw_check(text, data)
    assert raw['ok'], raw
    from tprep.qasm import convert
    from tprep.noise import schedule, noise_blocks
    native, _, errors = convert(text)
    assert not errors, errors
    program, times, _ = schedule(native)
    _, blocks = noise_blocks(native, 0.001)
    rows = []
    for op, places, block in zip(program, times, blocks):
        if 9 not in op.qubits:
            continue
        tick = next(t for qs, t in places if 9 in qs)
        if tick >= 38:
            rows.append(dict(kind=op.name, qs=list(op.qubits), time=tick,
                             noise_block=[line.split('#')[0].strip() for line in block]))
    assert len(rows) == 1 and rows[0]['kind'] == 'RX' and rows[0]['time'] == 38, rows
    assert 'Z_ERROR(0.001) 9' in rows[0]['noise_block'], rows
    edits = [dict(action='replace', old_kind='H', new_kind='RX', qs=[9], time=38),
             dict(action='remove', kind='MX', qs=[9], time=39, bit=bit, removed_checks=touched)]
    policy = 'Changed source postselection: omit source c321 herald; keep the actual noisy RX9 at38 and all other cut3 operations.'
    stem = write_stem(text, data, HERE / 'boundary', 'cut3_rx9_38_source',
                     source=dict(parent=str(parent), edits=edits, raw=raw,
                                 acceptance_policy=policy, official_native_q9=rows))
    release = {q: max((o.time + 1 for o in ops if q in o.qs), default=0) for q in range(36) if q not in data}
    path = HERE / 'cut3_rx9_38_release.json'
    cert_path = HERE / 'cut3_rx9_38_product_states.json'
    boundary = dict(stem=str(stem), data_qubits=data, release=release, cx=sum(o.kind == 'CX' for o in ops),
                    raw=raw, edits=edits, acceptance_policy=policy, official_native_q9=rows,
                    product_states=str(cert_path))
    path.write_text(json.dumps(boundary, indent=2) + '\n')
    with contextlib.redirect_stdout(io.StringIO()):
        certificate = certify(path, cert_path)
    q9 = next(row for row in certificate['cells'] if row['q'] == 9)
    assert q9['release'] == 39 and q9['product_axis'] == 'X' and q9['expectations']['X'] > 1 - 1e-9, q9
    bdoc['prefix_stem'] = str(stem)
    bdoc['source_acceptance_policy'] = policy
    bpath = HERE / 'cut3_rx9_38_b_module.json'
    bpath.write_text(json.dumps(bdoc, indent=2) + '\n')
    result = dict(source=str(stem), boundary=str(path), certificate=str(cert_path), b_module=str(bpath),
                  source_cx=boundary['cx'], raw=raw, q9=q9, official_native_q9=rows,
                  a_release={q: release[q] for q in bdoc['roles']['A']})
    (HERE / 'cut3_rx9_38.result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == '__main__':
    build()
