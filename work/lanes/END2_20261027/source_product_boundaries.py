"""Build concrete source boundaries and certify the products supplied to A.

These are changed source circuits for complete native assembly, not a claim
that removing a deterministic measurement preserves noisy fault detection.
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
sys.path.insert(0, str(HERE.parent / 'NATIVE2_20261027'))
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from boundary_product import certify
from joint import emit

D = [6, 20, 19, 10, 2, 22, 16]


def save(name, ops, dets, parent, changes):
    ops.sort(key=lambda op: op.time)
    occupied = set()
    for op in ops:
        for q in op.qs:
            assert (op.time, q) not in occupied, (op.time, q)
            occupied.add((op.time, q))
    text = emit(ops, dets)
    raw = raw_check(text, D)
    assert raw['ok'], raw
    stem = HERE / 'boundary' / f'source_{name}'
    stem.with_suffix('.qasm').write_text(text)
    stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=D,
        source=dict(parent=str(parent), changes=changes, raw=raw)), indent=2) + '\n')
    boundary = dict(stem=str(stem), data_qubits=D,
        release={q: max((op.time + 1 for op in ops if q in op.qs), default=0)
                 for q in range(36) if q not in D},
        cx=sum(op.kind == 'CX' for op in ops), raw=raw, changes=changes,
        product_states=str(HERE / f'{name}_product_states.json'))
    receipt = HERE / f'prefix_{name}.json'
    receipt.write_text(json.dumps(boundary, indent=2) + '\n')
    products = certify(receipt, boundary['product_states'])
    assert products['all_cells_have_certified_product_axis'], products
    print(json.dumps(dict(name=name, boundary=str(receipt), cx=boundary['cx'],
                         raw=raw, product_states=boundary['product_states'])), flush=True)
    return boundary


def main():
    # Isolate the originally proposed one-measurement change on the 251-CX
    # source. This is not mixed with the separate B-route pruning experiment.
    base = json.loads((HERE / 'prefix_early_reads.json').read_text())
    parent = Path(base['stem'])
    ops, dets = f.parse_current(parent.with_suffix('.qasm').read_text())
    m15 = next(op for op in ops if (op.kind, op.qs, op.time) == ('M', (15,), 40))
    ops.remove(m15)
    dets = [row - {m15.bit} for row in dets if row - {m15.bit}]
    save('reuse15', ops, dets, parent,
         [dict(action='remove', kind='M', qs=[15], time=40, bit=m15.bit)])

    # Native's construction keeps source record c321 with a noisy H at38 and
    # native MX at39; its exact product at40 is plus9. Keep this source fixed
    # and compare the qubit15 measurement being retained or omitted.
    native = HERE.parent / 'NATIVE2_20261027'
    module = json.loads((native / 'strong48_m9_herald_a_module.json').read_text())
    parent = Path(module['prefix_stem'])
    ops, dets = f.parse_current(parent.with_suffix('.qasm').read_text())
    save('native_m9_drop15', copy.deepcopy(ops), copy.deepcopy(dets), parent, [])
    assert not any(op.bit == 322 for op in ops)
    ops.append(f.Op('M', (15,), 40, 322))
    dets.append({322})
    save('native_m9_keep15', ops, dets, parent,
         [dict(action='restore', kind='M', qs=[15], time=40, bit=322)])

    # The alternate logical-X line permits an encoder which resets q9/q13
    # itself at41. It only needs the q15 measurement omitted; keep the rest of
    # the retimed243-CX source, including the original source heralds/gates.
    base = json.loads((HERE.parent / 'PREFIX2_20261027/retimed/source_release.json').read_text())
    parent = Path(base['stem'])
    ops, dets = f.parse_current(parent.with_suffix('.qasm').read_text())
    m15 = next(op for op in ops if (op.kind, op.qs, op.time) == ('M', (15,), 40))
    ops.remove(m15)
    dets = [row - {m15.bit} for row in dets if row - {m15.bit}]
    save('retimed_drop15', ops, dets, parent,
         [dict(action='remove', kind='M', qs=[15], time=40, bit=m15.bit)])


if __name__ == '__main__':
    main()
