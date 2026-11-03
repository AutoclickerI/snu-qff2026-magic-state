"""Retain the incumbent B factory and synthesize a disjoint native A block."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import contextlib
import io
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
import a_factory as af
import a_factory_search as search
from qtools.evaluator import frontend as f
from measured_assemble import assemble

D = [6, 20, 19, 10, 2, 22, 16]
A = [7, 14, 13, 9, 8, 21, 15]
B = [12, 26, 25, 11, 3, 28, 17]
C = [18, 27, 24, 5, 4, 29, 23]


def old_b():
    boundary = json.loads((HERE / 'prefix_release.json').read_text())
    prefix = Path(boundary['stem']).with_suffix('.qasm').read_text()
    pre, _ = f.parse_current(prefix)
    old, _ = f.parse_current((ROOT / 'work/lanes/MAIN/v37j.qasm').read_text())
    keys = {(o.time, o.kind, o.qs, o.bit) for o in pre}
    cells = set(B + C) | {31, 32, 33}
    # The three lower flag cells are part of the old verified B factory.
    selected = [o for o in old if set(o.qs) <= cells and o.time <= 47
                and o.kind not in ('T', 'TDG')
                and (o.time, o.kind, o.qs, o.bit) not in keys]
    assert not any(o.kind == 'MX' and o.qs[0] in B and o.time == 48 for o in selected)
    operations = [dict(time=o.time, kind=o.kind, qs=list(o.qs),
                       original_bit=o.bit) for o in selected]
    term = [('CX', [d, a], 0, None) for d, a in zip(D, A)]
    term += [('CX', [b, d], 1, None) for b, d in zip(B, D)]
    term += [('M', [q], 2, i) for i, q in enumerate(A)]
    term += [('MX', [q], 2, 7 + i) for i, q in enumerate(B)]
    doc = dict(prefix_stem=boundary['stem'], roles=dict(D=D, A=A, B=B, C=C),
               square_mask=0, terminal_operations=term,
               allow_record_faults=[dict(original_bit=352, time=31, kind='MX', qubits=[26], channel='Z_ERROR', pauli='Z'),
                                    dict(original_bit=376, time=42, kind='M', qubits=[31], channel='X_ERROR', pauli='X')],
               record_contract_note='Preserve the two benign physical record modes accepted by the incumbent: phase before MX26@31 and bit flip before M31@42, including their later record correlations.',
               candidates=[dict(operations=operations,
                               cx=sum(o['kind'] == 'CX' for o in operations),
                               scope='Exact original native B preparation and readout flags, before B-to-data.')])
    path = HERE / 'old_b_module.json'
    path.write_text(json.dumps(doc, indent=2) + '\n')
    return path


def search_a(trials, seed, helpers, output):
    af.A = A
    af.CELLS = sorted(set(A + helpers))
    af.ADJ = {q: [v for v in af.CELLS if abs(q // 6 - v // 6) + abs(q % 6 - v % 6) == 1] for q in af.CELLS}
    af.TARGET = {q: A.index(q) + 1 if q in A else 0 for q in af.CELLS}
    boundary = json.loads((HERE / 'prefix_release.json').read_text())
    release = {int(q): t for q, t in boundary['release'].items()}
    states = {r['q']: r for r in json.loads((HERE / 'prefix_product_states.json').read_text())['cells']}
    rng = random.Random(seed)
    candidates, seen = [], set()
    started = time.perf_counter()
    for i in range(trials):
        direct = bool(i % 2)
        out = search.construct(rng, direct)
        if out is None:
            continue
        initial, gates = out
        row = search.schedule(initial, gates, release, states, rng, direct)
        key = (row['a_ready'], row['cx'], tuple(tuple(e) for e in gates), direct)
        if key in seen:
            continue
        seen.add(key)
        row.update(A=A, trial=i)
        candidates.append(row)
        if len(candidates) > 200:
            candidates.sort(key=lambda r: (r['a_ready'], r['cx']))
            candidates = candidates[:80]
    candidates.sort(key=lambda r: (r['a_ready'], r['cx']))
    for row in candidates[:15]:
        gates = [tuple(o['qs']) for o in row['operations'] if o['kind'] == 'CX']
        initial = {int(q): v for q, v in row['initial_rows'].items()}
        opt = search.schedule(initial, gates, release, states, rng, row['direct'], 1.5)
        if opt['a_ready'] <= row['a_ready']:
            row.update(opt)
    candidates.sort(key=lambda r: (r['a_ready'], r['cx']))
    doc = dict(prefix_stem=boundary['stem'], seed=seed, trials=trials,
               seconds=time.perf_counter() - started, cells=af.CELLS, candidates=candidates[:40])
    output.write_text(json.dumps(doc, indent=2) + '\n')
    print(json.dumps(dict(output=str(output), seconds=doc['seconds'], best=[{k: r[k] for k in ('a_ready', 'cx', 'direct', 'helpers', 'plus_inputs')} for r in candidates[:10]])), flush=True)
    return doc


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--trials', type=int, default=10000)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--helpers', default='0,1')
    ap.add_argument('--screen', type=int, default=0)
    args = ap.parse_args()
    bpath = old_b()
    apath = HERE / f'old_footprint_a_s{args.seed}.json'
    doc = search_a(args.trials, args.seed, [int(q) for q in args.helpers.split(',') if q], apath)
    results = []
    for i in range(min(args.screen, len(doc['candidates']))):
        with contextlib.redirect_stdout(io.StringIO()):
            result = assemble(apath, bpath, i, 0, f'old_b_new_a_s{args.seed}_{i}', do_singles=True)
        results.append(result)
        print(json.dumps(dict(index=i, stem=result['stem'], raw=result['raw'], cx=result['cx'], ticks=result['ticks'], c1=result.get('singles', {}).get('c1'))), flush=True)
    if results:
        (HERE / f'old_b_new_a_screen_s{args.seed}.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
