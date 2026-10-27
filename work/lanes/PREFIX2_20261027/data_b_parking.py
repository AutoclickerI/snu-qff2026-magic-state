"""Screen physical identity CX pairs between terminal data and B qubits.

The two identical CX gates surround only operations that commute with them.
Their noiseless action is therefore exactly identity, including arbitrary
source states. All inserted gates, waits and measurement back-action remain
noisy in the full-circuit single-Pauli and order-two evaluations.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import contextlib
import io
import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
sys.path.insert(0, str(ROOT / 'work/lanes/REBUILD20261027'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit
from record_contract import singles
from pairs import audit as pair_audit

D = [6, 20, 19, 10, 2, 22, 16]
B = [12, 26, 25, 11, 3, 28, 17]


def commute(gate, op):
    if not set(gate) & set(op.qs):
        return True
    if op.kind == 'CX':
        c, t = gate
        a, b = op.qs
        return t != a and b != c
    return False


def search(stem, name='data_b_parking', start=35, end=45):
    stem = Path(stem)
    ops, dets = f.parse_current(stem.with_suffix('.qasm').read_text())
    data = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    assert data == D
    f.DATA = data
    occupied = {(o.time, q) for o in ops for q in o.qs}
    output = HERE / 'retimed' / name
    output.mkdir(parents=True, exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        base = pair_audit(stem, output / 'base.pairs.json')
    result = dict(parent=str(stem), baseline_c2=base['c2'], start=start, end=end,
                  scope='Paired native CX identity under exact commutation; full source c1 and c2 audit.', candidates=[])
    best = base['c2']
    for d, b in zip(D, B):
        for gate in ((d, b), (b, d)):
            free = [t for t in range(start, end + 1) if all((t, q) not in occupied for q in gate)]
            for t1, t2 in combinations(free, 2):
                if any(not commute(gate, o) for o in ops if t1 < o.time < t2):
                    continue
                new = sorted(ops + [f.Op('CX', gate, t1), f.Op('CX', gate, t2)], key=lambda o: o.time)
                text = emit(new, dets)
                ss = singles(f.make_model(*f.parse_current(text)))
                row = dict(gate=list(gate), times=[t1, t2], c1=ss['c1'],
                           fault_components=ss['fault_components'])
                if ss['c1'] < 1e-10:
                    dest = write_stem(text, data, output, f'pair_{gate[0]}_{gate[1]}_{t1}_{t2}',
                                      source=dict(parent=str(stem), identity_pair=row))
                    with contextlib.redirect_stdout(io.StringIO()):
                        pp = pair_audit(dest)
                    row.update(stem=str(dest), c2=pp['c2'])
                    if row['c2'] < best - 1e-10:
                        raw = raw_check(text, data)
                        assert raw['ok'], raw
                        row['raw'] = raw
                        best = row['c2']
                        print(json.dumps(dict(improved=row)), flush=True)
                result['candidates'].append(row)
    result['best_c2'] = best
    result['candidates'].sort(key=lambda r: (r['c1'] > 1e-10, r.get('c2', 1e9), r['c1']))
    receipt = output / 'results.json'
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(receipt=str(receipt), baseline_c2=base['c2'], best_c2=best,
                         tested=len(result['candidates']), best=result['candidates'][:3]), indent=2), flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stem')
    ap.add_argument('--name', default='data_b_parking')
    ap.add_argument('--start', type=int, default=35)
    ap.add_argument('--end', type=int, default=45)
    args = ap.parse_args()
    search(args.stem, args.name, args.start, args.end)
