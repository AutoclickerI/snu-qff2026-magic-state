"""Retiming the verified B module to a fixed terminal deadline.

Preserve every operation and every physical wire order. Late scheduling avoids
preparing independent helper cells long before their neighbors are released by
the source. Full raw, single-Pauli and exact noisy validation remains required.
"""
import os
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
import argparse
import contextlib
import copy
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/NATIVE2_20261027'))
from qtools.evaluator import frontend as f
from measured_assemble import assemble
from b_exposure import audit


def weighted_times(doc, ops, pre, release, ready, end, reference, seconds=20):
    """Minimize the exact first-order idle rejection for a fixed wire order."""
    from ortools.sat.python import cp_model
    diagnostic = audit(reference)
    weights = {(r['operation']['time'], r['operation']['kind'], tuple(r['operation']['qs']), r['qubit']):
               r['rejection'] for r in diagnostic['segment_weights']}
    model = cp_model.CpModel()
    bset = set(doc['roles']['B'])
    starts = [model.NewIntVar(max(release[q] for q in o['qs']),
                             (ready if set(o['qs']) & bset else end) - 1, f't{i}')
              for i, o in enumerate(ops)]
    terms = []
    for q in sorted({q for o in ops for q in o['qs']}):
        sequence = [i for i, o in enumerate(ops) if q in o['qs']]
        before = [o for o in pre if q in o.qs]
        previous = max(before, key=lambda o: o.time) if before else None
        previous_time = previous.time if previous else None
        previous_key = (previous.time, previous.kind, tuple(previous.qs), q) if previous else None
        for i in sequence:
            o = ops[i]
            if previous_time is not None:
                model.Add(starts[i] > previous_time)
                if o['kind'] not in ('R', 'RX'):
                    w = weights[previous_key]
                    terms.append(round(3000 * w) * (starts[i] - previous_time - 1))
            previous_time = starts[i]
            previous_key = o['time'], o['kind'], tuple(o['qs']), q
        if q in bset:
            # The B-to-data interaction is fixed at `ready`; before it, every
            # last B operation has an exposed waiting interval.
            w = weights[previous_key]
            terms.append(round(3000 * w) * (ready - previous_time - 1))
    model.Minimize(1000 * sum(terms) - sum(starts))
    for t, o in zip(starts, ops):
        model.AddHint(t, o['time'])
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = seconds
    status = solver.Solve(model)
    assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE), solver.StatusName(status)
    return [solver.Value(t) for t in starts], dict(
        objective=solver.ObjectiveValue(), status=solver.StatusName(status),
        reference=str(reference), reference_rejection=diagnostic['rejection_coefficient'],
        scope='Exact first-order waiting-noise rejection with unchanged per-wire operation order; late-time tie break.')


def schedule(path, ready=46, end=47, name='b_alap46', method='alap', reference=None):
    doc = json.loads(Path(path).read_text())
    assert doc.get('allow_record_faults') and not doc.get('ignore_original_records')
    row = copy.deepcopy(doc['candidates'][0])
    ops = row['operations']
    prefix = Path(doc['prefix_stem'])
    pre, _ = f.parse_current(prefix.with_suffix('.qasm').read_text())
    release = {q: max((o.time for o in pre if q in o.qs), default=-1) + 1 for q in range(36)}
    # The input list is a valid circuit order. The original_bit selectors stay
    # attached to their measurements when their time changes.
    optimization = None
    if method == 'rejection':
        assert reference, 'Weighted scheduling needs the full-circuit reference matching this B module'
        times, optimization = weighted_times(doc, ops, pre, release, ready, end, reference)
        for o, t in zip(ops, times):
            o.setdefault('schedule_parent_time', o['time'])
            o['time'] = t
    else:
        deadline = {q: ready if q in doc['roles']['B'] else end for q in range(36)}
        for o in reversed(ops):
            o.setdefault('schedule_parent_time', o['time'])
            o['time'] = min(deadline[q] for q in o['qs']) - 1
            assert o['time'] >= max(release[q] for q in o['qs']), ('infeasible fixed-order deadline', o, release)
            for q in o['qs']:
                deadline[q] = o['time']
    actual_ready = max(o['time'] + 1 for o in ops if set(o['qs']) & set(doc['roles']['B']))
    row.update(operations=ops, cx=sum(o['kind'] == 'CX' for o in ops), scheduling=method + ' with unchanged per-wire order',
               resource_ready=actual_ready, module_end=max(o['time'] for o in ops) + 1,
               schedule_parent=str(path), fixed_ready_deadline=ready, fixed_module_deadline=end,
               optimization=optimization)
    doc['candidates'] = [row]
    dest = HERE / 'retimed' / f'{name}.json'
    dest.write_text(json.dumps(doc, indent=2) + '\n')
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('b_module')
    ap.add_argument('--a-module')
    ap.add_argument('--ready', type=int, default=46)
    ap.add_argument('--end', type=int, default=47)
    ap.add_argument('--name', default='b_alap46')
    ap.add_argument('--method', choices=['alap', 'rejection'], default='alap')
    ap.add_argument('--reference')
    ap.add_argument('--price', action='store_true')
    ap.add_argument('--singles', action='store_true')
    args = ap.parse_args()
    out = schedule(args.b_module, args.ready, args.end, args.name, args.method, args.reference)
    result = dict(b_module=str(out))
    if args.a_module:
        with contextlib.redirect_stdout(io.StringIO()):
            result['full'] = assemble(args.a_module, out, 0, 0, args.name,
                                      do_price=args.price, do_singles=args.singles)
    dest = out.with_suffix('.result.json')
    dest.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(receipt=str(dest), b_module=str(out),
                         **({k: result['full'][k] for k in ('stem', 'raw', 'cx', 'ticks', 'singles', 'exact')
                             if k in result['full']} if 'full' in result else {})), indent=2), flush=True)


if __name__ == '__main__':
    main()
