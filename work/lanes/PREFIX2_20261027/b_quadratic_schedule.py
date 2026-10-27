"""Optimize the full quadratic accepted-pair cost of fixed-order B waiting.

All non-idle operations and all physical wire orders are fixed. Fault signatures
are consequently fixed, and each waiting segment contributes its duration times
one depolarizing channel. The complete order-two numerator is an explicit
quadratic polynomial in those durations. Its reference value and each emitted
solution are checked against the independent full fault-pair ledger.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import contextlib
import copy
import io
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from ortools.sat.python import cp_model

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/NATIVE2_20261027'))
from qtools.evaluator import frontend as f
from qtools.evaluator import sparse_walsh as sw
from measured_assemble import assemble
from pairs import audit as pair_audit


def op_key(o):
    return o.time, o.kind, tuple(o.qs)


def construct(stem, ready=45, end=46):
    stem = Path(stem)
    integration = json.loads(stem.with_suffix('.integration.json').read_text())
    doc = json.loads(Path(integration['bc_module']).read_text())
    row = copy.deepcopy(doc['candidates'][integration.get('bc_index', 0)])
    ops = row['operations']
    pre, _ = f.parse_current(Path(doc['prefix_stem']).with_suffix('.qasm').read_text())
    release = {q: max((o.time for o in pre if q in o.qs), default=-1) + 1 for q in range(36)}
    used = {q for o in ops for q in o['qs']}
    bset = set(doc['roles']['B'])
    free = dict(release)
    early = []
    for o in ops:
        t = max(free[q] for q in o['qs'])
        early.append(t)
        for q in o['qs']:
            free[q] = t + 1
    free = {q: ready if q in bset else end for q in range(36)}
    late = [None] * len(ops)
    for i in reversed(range(len(ops))):
        o = ops[i]
        t = min(free[q] for q in o['qs']) - 1
        late[i] = t
        assert early[i] <= t, (i, o, early[i], t)
        for q in o['qs']:
            free[q] = t

    segments = []
    for q in sorted(used):
        sequence = [i for i, o in enumerate(ops) if q in o['qs']]
        old = [o for o in pre if q in o.qs]
        previous = max(old, key=lambda o: o.time) if old else None
        previous_index = None
        for i in sequence:
            o = ops[i]
            if previous is not None and o['kind'] not in ('R', 'RX'):
                minprev = previous.time if previous_index is None else early[previous_index]
                maximum = late[i] - minprev - 1
                segments.append(dict(qubit=q, previous=op_key(previous), previous_index=previous_index,
                                     next_index=i, reference=o['time'] - previous.time - 1,
                                     maximum=maximum))
            previous = f.Op(o['kind'], tuple(o['qs']), o['time'])
            previous_index = i
        if q in bset:
            segments.append(dict(qubit=q, previous=op_key(previous), previous_index=previous_index,
                                 next_index=None, reference=ready - previous.time - 1,
                                 maximum=ready - early[previous_index] - 1))
    # A segment whose upper bound is zero has no variable noise channel.
    segments = [s for s in segments if s['maximum'] > 0]

    full_ops, dets = f.parse_current(stem.with_suffix('.qasm').read_text())
    f.DATA = doc['roles']['D']
    m = f.make_model(full_ops, dets)
    eng = f.Engine(m)
    sw.canonicalize_detector_rows(m, eng)
    eng = f.Engine(m)
    active = sum(1 << i for i, p in enumerate(eng.projs) if p[:2] != (0, 0))
    inactive = ((1 << len(dets)) - 1) ^ active
    tables = {}

    def kernel(a, b):
        s, d, e = (a[i] ^ b[i] for i in range(3))
        if d & inactive:
            return 0.0
        if (s, d) not in tables:
            tables[s, d] = eng.ntable(s, d)
        _, n = tables[s, d]
        return 0.0 if n is None else max(0.0, float(n[e]))

    _, _, gaps = f.schedule(m.native)
    gaps_by_ins, channels_by_ins = defaultdict(list), defaultdict(list)
    for ins, q, start, length in gaps:
        gaps_by_ins[ins].append((q, start, length))
    for cid, ch in enumerate(m.chans):
        channels_by_ins[ch['ins']].append(cid)
    idle_channels = {}
    for ins, gs in gaps_by_ins.items():
        for cid, gap in zip(channels_by_ins[ins][-len(gs):], gs):
            assert m.chans[cid]['name'] == 'DEPOLARIZE1' and m.chans[cid]['qs'] == [gap[0]]
            idle_channels[cid] = op_key(m.labels[ins]), gap[0], gap[2]
    segment_by_key = {(tuple(s['previous']), s['qubit']): i for i, s in enumerate(segments)}
    removed_channels = set()
    for cid, (prev, q, length) in idle_channels.items():
        if (prev, q) in segment_by_key:
            i = segment_by_key[prev, q]
            assert segments[i]['reference'] == length
            removed_channels.add(cid)

    axes = defaultdict(dict)
    const_groups = defaultdict(lambda: defaultdict(float))
    for fault in m.faults:
        sig = fault['s'], fault['d'], fault['e']
        ch = m.chans[fault['chan']]
        op = m.labels[fault['ins']]
        if fault['chan'] not in removed_channels:
            const_groups[sig][fault['chan']] += fault['p'] / .001
        if fault['chan'] in idle_channels:
            continue
        if op.kind == 'CX' and ch['name'] == 'DEPOLARIZE2':
            for pos, q in enumerate(op.qs):
                if fault['pauli'][1 - pos] == 'I':
                    axes[op_key(op), q][fault['pauli'][pos]] = sig
        elif op.kind in ('R', 'RX') and ch['name'] in ('X_ERROR', 'Z_ERROR'):
            q = op.qs[0]
            axes[op_key(op), q] = dict.fromkeys('XYZ', sig)
            axes[op_key(op), q]['Z' if op.kind == 'R' else 'X'] = (0, 0, 0)
        elif ch['name'] == 'DEPOLARIZE1':
            q = ch['qs'][0]
            axes[op_key(op), q][fault['pauli']] = sig
    virtual = []
    for seg in segments:
        values = axes[tuple(seg['previous']), seg['qubit']]
        assert set(values) == set('XYZ'), seg
        groups = defaultdict(float)
        for sig in values.values():
            groups[sig] += 1 / 3
        # Two errors at this same Pauli location reduce to an allowed single.
        assert all(kernel(a, b) < 1e-10 for a in groups for b in groups), seg
        virtual.append(dict(groups))

    const = [(sig, sum(chs.values()), chs) for sig, chs in const_groups.items()]
    buckets = defaultdict(list)
    for i, (sig, _, _) in enumerate(const):
        buckets[sig[1] & inactive].append(i)
    constant = 0.0
    for ids in buckets.values():
        for ai, i in enumerate(ids):
            a, wa, ca = const[i]
            for j in ids[ai + 1:]:
                b, wb, cb = const[j]
                loss = kernel(a, b)
                if loss:
                    same = sum(w * cb.get(c, 0) for c, w in ca.items())
                    constant += (wa * wb - same) * loss
    linear, rejection = [], []
    acceptance_cache = {}
    for groups in virtual:
        cost = 0.0
        reject = 0.0
        for a, wa in groups.items():
            for j in buckets.get(a[1] & inactive, []):
                b, wb, _ = const[j]
                cost += wa * wb * kernel(a, b)
            if a[:2] not in acceptance_cache:
                out = eng.table(*a[:2])
                acceptance_cache[a[:2]] = 0.0 if out is None else float(out[0])
            reject += wa * (1 - acceptance_cache[a[:2]])
        linear.append(cost)
        rejection.append(reject)
    quadratic = []
    for i, a in enumerate(virtual):
        for j in range(i + 1, len(virtual)):
            b = virtual[j]
            cost = sum(wa * wb * kernel(sa, sb) for sa, wa in a.items() for sb, wb in b.items())
            if cost > 1e-12:
                quadratic.append((i, j, cost))
    return dict(stem=str(stem), integration=integration, document=doc, candidate=row,
                operations=ops, early=early, late=late, segments=segments,
                constant=constant, linear=linear, quadratic=quadratic,
                rejection=rejection, tables=len(tables))


def polynomial(problem, lengths):
    return problem['constant'] + sum(a * x for a, x in zip(problem['linear'], lengths)) + sum(
        c * lengths[i] * lengths[j] for i, j, c in problem['quadratic'])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stem')
    ap.add_argument('--name', default='b_quadratic47')
    ap.add_argument('--ready', type=int, default=45)
    ap.add_argument('--end', type=int, default=46)
    ap.add_argument('--seconds', type=float, default=60)
    args = ap.parse_args()
    problem = construct(args.stem, args.ready, args.end)
    with contextlib.redirect_stdout(io.StringIO()):
        baseline = pair_audit(args.stem, HERE / 'retimed' / f'{args.name}_base.pairs.json')
    reference = [s['reference'] for s in problem['segments']]
    predicted = polynomial(problem, reference)
    assert abs(predicted - baseline['c2']) < 1e-8, ('quadratic model mismatch', predicted, baseline['c2'])
    print(json.dumps(dict(phase='model_verified', c2=predicted, segments=len(reference),
                          couplings=len(problem['quadratic']), tables=problem['tables'])), flush=True)
    model = cp_model.CpModel()
    starts = [model.NewIntVar(a, b, f't{i}') for i, (a, b) in enumerate(zip(problem['early'], problem['late']))]
    ops = problem['operations']
    previous = {}
    for i, op in enumerate(ops):
        for q in op['qs']:
            if q in previous:
                model.Add(starts[i] > starts[previous[q]])
            previous[q] = i
    lengths = []
    for i, seg in enumerate(problem['segments']):
        length = model.NewIntVar(0, seg['maximum'], f'w{i}')
        a = starts[seg['previous_index']] if seg['previous_index'] is not None else seg['previous'][0]
        b = starts[seg['next_index']] if seg['next_index'] is not None else args.ready
        model.Add(length == b - a - 1)
        model.AddHint(length, seg['reference'])
        lengths.append(length)
    denominators = [Fraction(c).limit_denominator(10**5).denominator
                    for c in problem['linear'] + [c for _, _, c in problem['quadratic']] if c > 1e-12]
    scale = math.lcm(*denominators) if denominators else 1
    if scale > 10**9:
        scale = 10**7
    rounding_bound = sum(abs(round(scale * c) / scale - c) * s['maximum']
                         for c, s in zip(problem['linear'], problem['segments']))
    rounding_bound += sum(abs(round(scale * c) / scale - c) * problem['segments'][i]['maximum'] * problem['segments'][j]['maximum']
                          for i, j, c in problem['quadratic'])
    terms = [round(scale * c) * v for c, v in zip(problem['linear'], lengths)]
    for i, j, c in problem['quadratic']:
        product = model.NewIntVar(0, problem['segments'][i]['maximum'] * problem['segments'][j]['maximum'], f'p{i}_{j}')
        model.AddMultiplicationEquality(product, [lengths[i], lengths[j]])
        terms.append(round(scale * c) * product)
    rejection = sum(round(3000 * c) * v for c, v in zip(problem['rejection'], lengths))
    max_rejection = sum(round(3000 * c) * v for c, v in zip(problem['rejection'], reference))
    model.Add(rejection <= max_rejection)
    score = sum(terms)
    model.Minimize(score)
    for t, o in zip(starts, ops):
        model.AddHint(t, o['time'])
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = 1
    status = solver.Solve(model)
    result = dict(parent=args.stem, baseline_c2=baseline['c2'], model_reference_c2=predicted,
                  model_segments=problem['segments'], linear_coefficients=problem['linear'],
                  quadratic_coefficients=problem['quadratic'], constant_coefficient=problem['constant'],
                  status=solver.StatusName(status), seconds=solver.WallTime(),
                  objective_scale=scale, coefficient_rounding_error_bound=rounding_bound,
                  scope='Global CP over unchanged B per-wire order and fixed source/A/terminal times, with first-order rejection capped at the reference. Integer coefficient error is explicitly bounded; full polynomial and emitted-circuit validation required.')
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        primary = round(solver.ObjectiveValue())
        result['solver_bound_c2'] = problem['constant'] + solver.BestObjectiveBound() / scale - rounding_bound
        model.Add(score == primary)
        model.Minimize(10000 * rejection - sum(starts))
        solver.parameters.max_time_in_seconds = min(args.seconds, 20)
        second_status = solver.Solve(model)
        assert second_status in (cp_model.OPTIMAL, cp_model.FEASIBLE), solver.StatusName(second_status)
        new_lengths = [solver.Value(v) for v in lengths]
        result['predicted_c2'] = polynomial(problem, new_lengths)
        changes = []
        for o, t in zip(ops, starts):
            nt = solver.Value(t)
            if nt != o['time']:
                changes.append(dict(kind=o['kind'], qs=o['qs'], old_time=o['time'], new_time=nt))
            o['time'] = nt
        row = problem['candidate']
        row.update(operations=ops, scheduling='quadratic waiting cost', scheduling_changes=changes)
        doc = problem['document']
        doc['candidates'] = [row]
        module = HERE / 'retimed' / f'{args.name}_b_module.json'
        module.write_text(json.dumps(doc, indent=2) + '\n')
        with contextlib.redirect_stdout(io.StringIO()):
            full = assemble(problem['integration']['a_module'], module, 0, 0, args.name, do_singles=True)
            pp = pair_audit(full['stem'], HERE / 'retimed' / f'{args.name}.pairs.json')
        assert abs(pp['c2'] - result['predicted_c2']) < 1e-8, ('emitted circuit mismatch', pp['c2'], result['predicted_c2'])
        result.update(stem=full['stem'], b_module=str(module), raw=full['raw'], c1=full['singles']['c1'],
                      exact_c2=pp['c2'], changes=changes, final_lengths=new_lengths)
    dest = HERE / 'retimed' / f'{args.name}.result.json'
    dest.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('model_segments', 'linear_coefficients',
                      'quadratic_coefficients', 'final_lengths')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
