"""Move commuting phase gates on a fixed rank-six native network.

Raw-state and single-fault checks precede full all-orders pricing. This is a
bounded implementation experiment, not a claim that the topology is optimal.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import hashlib
import json
import sys
from pathlib import Path
import rank6
import analytic_price

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/lanes/REBUILD20261027'))
from record_contract import model, singles
from qtools.validity import raw_check


def run(network, count, finalists):
    rec = json.loads(Path(network).read_text())
    seen = set()
    rows = []
    for i in range(count + 2):
        mode = 'first' if i == 0 else 'last' if i == 1 else 'random'
        seed = max(0, i - 2)
        stem = rank6.build(rec, f'phase23_{mode}_{seed}', mode, seed)
        text = stem.with_suffix('.qasm').read_text()
        digest = hashlib.sha256(text.encode()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        raw = raw_check(text, rank6.D)
        if not raw['ok']:
            raise ValueError(raw)
        m, _ = model(text, rank6.D)
        audit = singles(m)
        row = dict(stem=str(stem.relative_to(ROOT)), phase_mode=mode,
                   phase_seed=seed, qasm_sha256=digest, c1=audit['c1'],
                   harmful_single_components=len(audit['harmful_faults']))
        rows.append(row)
        print('screen', json.dumps(row), flush=True)
        (HERE / 'phase_sweep_results.json').write_text(json.dumps(rows, indent=2) + '\n')
    order = sorted(range(len(rows)), key=lambda j: (rows[j]['c1'], rows[j]['harmful_single_components']))
    for j in order[:finalists]:
        stem = ROOT / rows[j]['stem']
        result = analytic_price.price(stem)
        rows[j]['price'] = result
        print('price', json.dumps(rows[j]), flush=True)
        (HERE / 'phase_sweep_results.json').write_text(json.dumps(rows, indent=2) + '\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('network')
    ap.add_argument('--count', type=int, default=32)
    ap.add_argument('--finalists', type=int, default=5)
    args = ap.parse_args()
    run(args.network, args.count, args.finalists)
