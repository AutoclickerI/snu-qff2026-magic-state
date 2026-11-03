"""Retiming an entire native A measurement instrument by exact commutation.

Shared-target and shared-control CX gates may change order, including data
taps across A preparation. Resets, measurements, and noncommuting CX pairs
retain their per-wire order. The pure-resource boundary is not imposed.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import copy
import json
import sys
import time
from pathlib import Path
from ortools.sat.python import cp_model
from measured_assemble import HERE, ROOT
sys.path.insert(0, str(ROOT / 'work/tools'))
from qtools.evaluator import frontend as f
from old_b_new_a import D


def commute(a, b):
    if not set(a['qs']) & set(b['qs']):
        return True
    if a['kind'] == b['kind'] == 'CX':
        ac, at = a['qs']
        bc, bt = b['qs']
        return at != bc and bt != ac
    return False


def solve(path, end=48, last_tap=45, seconds=20, name='compact_instrument48', seed=1):
    doc = json.loads(Path(path).read_text())
    row = copy.deepcopy(doc['candidates'][0])
    ops = sorted(row['operations'], key=lambda o: o['time'])
    prefix = Path(doc['prefix_stem'])
    pre, _ = f.parse_current(prefix.with_suffix('.qasm').read_text())
    release = {q: max((o.time for o in pre if q in o.qs), default=-1) + 1 for q in range(36)}
    model = cp_model.CpModel()
    starts = [model.NewIntVar(max(release[q] for q in o['qs']), end - 1, f't{i}') for i, o in enumerate(ops)]
    intervals = [model.NewFixedSizeIntervalVar(t, 1, f'g{i}') for i, t in enumerate(starts)]
    used = {q for o in ops for q in o['qs']}
    for q in used:
        model.AddNoOverlap([iv for iv, o in zip(intervals, ops) if q in o['qs']])
    for i, op in enumerate(ops):
        for j in range(i):
            if not commute(ops[j], op):
                model.Add(starts[i] > starts[j])
    taps = [i for i, o in enumerate(ops) if o['kind'] == 'CX' and o['qs'][0] in D]
    for i in taps:
        model.Add(starts[i] <= last_tap)
    finish = model.NewIntVar(1, end, 'finish')
    model.AddMaxEquality(finish, [t + 1 for t in starts])
    prep = [i for i, o in enumerate(ops) if o['kind'] in ('R', 'RX')]
    model.Minimize(10000 * finish - 20 * sum(starts[i] for i in taps) - sum(starts[i] for i in prep))
    for t, o in zip(starts, ops):
        model.AddHint(t, min(end - 1, o['time']))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.random_seed = seed
    begin = time.perf_counter()
    status = solver.Solve(model)
    result = dict(status=solver.StatusName(status), source=str(path), end=end,
                  last_tap=last_tap, seconds=time.perf_counter() - begin,
                  scope='Commutation-equivalent full A instrument retiming, including data taps. No pure-preparation boundary.')
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        row['operations'] = [dict(o, time=solver.Value(t)) for o, t in zip(ops, starts)]
        row['operations'].sort(key=lambda o: o['time'])
        result.update(prefix_stem=str(prefix), candidates=[row], objective=solver.ObjectiveValue(),
                      finish=solver.Value(finish), source_release=release)
    out = HERE / f'{name}.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('candidates', 'source_release')}, indent=2), flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('module')
    ap.add_argument('--end', type=int, default=48)
    ap.add_argument('--last-tap', type=int, default=45)
    ap.add_argument('--seconds', type=float, default=20)
    ap.add_argument('--name', default='compact_instrument48')
    ap.add_argument('--seed', type=int, default=1)
    args = ap.parse_args()
    solve(args.module, args.end, args.last_tap, args.seconds, args.name, args.seed)
