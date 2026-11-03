"""Find a verified B module at an earlier deadline using exact commutation.

Source rewrites are supplied as explicit raw-checked prefixes. Before changing
the B gate order, the rewritten source is assembled with the old B schedule and
audited. The optional final pair deletion removes two identical CX4->5 gates
with only disjoint operations between them. Every emitted witness gets full
raw, mixed-Pauli single-fault and pair checks.
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
from ortools.sat.python import cp_model

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/NATIVE2_20261027'))
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from measured_assemble import assemble
from pairs import audit as pair_audit


def commute(a, b, measurements=False):
    if not set(a['qs']) & set(b['qs']):
        return True
    if a['kind'] == b['kind'] == 'CX':
        ac, at = a['qs']
        bc, bt = b['qs']
        return at != bc and bt != ac
    if measurements:
        if a['kind'] == 'CX':
            a, b = b, a
        if b['kind'] == 'CX' and a['kind'] in ('M', 'MX'):
            q = a['qs'][0]
            return q == b['qs'][0 if a['kind'] == 'M' else 1]
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source')
    ap.add_argument('--parent', default=str(ROOT / 'work/lanes/NATIVE2_20261027/full47_q15_early39_cut3.result.json'))
    ap.add_argument('--name', default='b44_commute')
    ap.add_argument('--ready', type=int, default=44)
    ap.add_argument('--end', type=int, default=45)
    ap.add_argument('--seconds', type=float, default=30)
    ap.add_argument('--drop-end-pair', action='store_true')
    ap.add_argument('--measure-commute', action='store_true')
    args = ap.parse_args()
    parent = json.loads(Path(args.parent).read_text())
    adoc = json.loads(Path(parent['a_module']).read_text())
    bdoc = json.loads(Path(parent['bc_module']).read_text())
    source = str(Path(args.source).resolve())
    text = Path(source).with_suffix('.qasm').read_text()
    raw = raw_check(text, bdoc['roles']['D'])
    assert raw['ok'], raw
    pre, _ = f.parse_current(text)
    release = {q: max((o.time for o in pre if q in o.qs), default=-1) + 1 for q in range(36)}
    adoc['prefix_stem'] = bdoc['prefix_stem'] = source
    a_path = HERE / 'retimed' / f'{args.name}_a_module.json'
    old_b_path = HERE / 'retimed' / f'{args.name}_old_b_module.json'
    a_path.write_text(json.dumps(adoc, indent=2) + '\n')
    old_b_path.write_text(json.dumps(bdoc, indent=2) + '\n')
    result = dict(source=source, source_raw=raw, release=release, parent=args.parent)
    with contextlib.redirect_stdout(io.StringIO()):
        control = assemble(a_path, old_b_path, 0, 0, args.name + '_source_control', do_singles=True)
        if control['raw']['ok'] and control['singles']['c1'] < 1e-10:
            control['pairs'] = pair_audit(control['stem'], HERE / 'retimed' / f'{args.name}_source_control.pairs.json')
    result['source_control'] = control
    assert control['raw']['ok'] and control['singles']['c1'] < 1e-10, 'Source rewrite failed complete circuit validation'
    row = copy.deepcopy(bdoc['candidates'][0])
    ops = row['operations']
    removed = []
    if args.drop_end_pair:
        indexes = [i for i, o in enumerate(ops) if o['kind'] == 'CX' and o['qs'] == [4, 5]
                   and o.get('original_time') in (43, 45)]
        assert len(indexes) == 2, indexes
        assert all(not set(o['qs']) & {4, 5} for o in ops[indexes[0] + 1:indexes[1]])
        removed = [ops[i] for i in indexes]
        ops = [o for i, o in enumerate(ops) if i not in indexes]
    model = cp_model.CpModel()
    bset = set(bdoc['roles']['B'])
    starts = [model.NewIntVar(max(release[q] for q in o['qs']),
                             (args.ready if set(o['qs']) & bset else args.end) - 1, f't{i}')
              for i, o in enumerate(ops)]
    intervals = [model.NewFixedSizeIntervalVar(t, 1, f'g{i}') for i, t in enumerate(starts)]
    for q in {q for o in ops for q in o['qs']}:
        model.AddNoOverlap([iv for iv, o in zip(intervals, ops) if q in o['qs']])
    precedences = 0
    for i, op in enumerate(ops):
        for j in range(i):
            other = ops[j]
            if (not commute(other, op, args.measure_commute)
                    or (other['kind'], other['qs']) == (op['kind'], op['qs'])):
                model.Add(starts[i] > starts[j])
                precedences += 1
        if op.get('original_time') == 46:
            model.Add(starts[i] == args.ready - 1)
        if op.get('original_time') == 47:
            model.Add(starts[i] == args.end - 1)
        model.AddHint(starts[i], min(op['time'], (args.ready if set(op['qs']) & bset else args.end) - 1))
    model.Maximize(sum(starts))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = args.seconds
    status = solver.Solve(model)
    result.update(status=solver.StatusName(status), solve_seconds=solver.WallTime(),
                  precedences=precedences, source_release=release, removed_b_pair=removed,
                  measurement_commutation=args.measure_commute,
                  scope='Fixed rewritten source, native gates, exact commuting gate reorderings; source and full emitted circuit separately audited.')
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for o, t in zip(ops, starts):
            o['time'] = solver.Value(t)
        # The serialized list must itself be a valid circuit order for later
        # per-wire scheduling, so put the solved operations in clock order.
        ops.sort(key=lambda o: o['time'])
        row.update(operations=ops, cx=sum(o['kind'] == 'CX' for o in ops),
                   resource_ready=args.ready, module_end=args.end, removed_end_pair=removed)
        bdoc['candidates'] = [row]
        b_path = HERE / 'retimed' / f'{args.name}_b_module.json'
        b_path.write_text(json.dumps(bdoc, indent=2) + '\n')
        with contextlib.redirect_stdout(io.StringIO()):
            full = assemble(a_path, b_path, 0, 0, args.name, do_singles=True)
            if full['raw']['ok'] and full['singles']['c1'] < 1e-10:
                full['pairs'] = pair_audit(full['stem'], HERE / 'retimed' / f'{args.name}.pairs.json')
        result.update(a_module=str(a_path), b_module=str(b_path), full=full)
    out = HERE / 'retimed' / f'{args.name}.result.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    summary = {k: result[k] for k in ('status', 'solve_seconds', 'a_module', 'b_module') if k in result}
    summary.update(receipt=str(out), source_control_c1=control['singles']['c1'],
                   source_control_c2=control.get('pairs', {}).get('c2'))
    if 'full' in result:
        full = result['full']
        summary['full'] = dict(stem=full['stem'], raw=full['raw'], cx=full['cx'], ticks=full['ticks'],
                               c1=full['singles']['c1'], c2=full.get('pairs', {}).get('c2'))
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
