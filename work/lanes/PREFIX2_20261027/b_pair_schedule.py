"""Local fixed-wire B retiming guided by exact full-circuit fault-pair cost.

The accepted second-order numerator is quadratic in waiting durations. This
script minimizes its exact linear marginal cost inside a bounded time window,
caps first-order idle rejection, then validates the proposed complete circuit.
Only measured c2 improvements are kept; no linear estimate is treated as a score.
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
from collections import defaultdict
from pathlib import Path
from ortools.sat.python import cp_model

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/NATIVE2_20261027'))
from qtools.evaluator import frontend as f
from measured_assemble import assemble
from b_exposure import audit as exposure_audit
from pairs import audit as pair_audit


def pair_weights(stem, ledger, exposure):
    f.DATA = json.loads(Path(stem).with_suffix('.json').read_text())['data_qubits']
    m = f.make_model(*f.parse_current(Path(stem).with_suffix('.qasm').read_text()))
    values = {r['id']: r['value'] for r in ledger['fault_attribution']}
    weights = defaultdict(dict)
    # Rejection audit identifies gate/reset/postmeasurement channels. Its
    # segment keys also exclude readout flips before the measurement.
    keys = {(r['operation']['time'], r['operation']['kind'], tuple(r['operation']['qs']), r['qubit'])
            for r in exposure['segment_weights']}
    for i, fault in enumerate(m.faults):
        op = m.labels[fault['ins']]
        ch = m.chans[fault['chan']]
        response = values.get(i, 0.0) / fault['p'] / .001
        if op.kind == 'CX' and ch['name'] == 'DEPOLARIZE2':
            for pos, q in enumerate(op.qs):
                if fault['pauli'][1 - pos] == 'I':
                    weights[op.time, op.kind, tuple(op.qs), q][fault['pauli'][pos]] = response
        elif op.kind in ('R', 'RX') and ch['name'] in ('X_ERROR', 'Z_ERROR'):
            q = op.qs[0]
            axis = dict.fromkeys('XYZ', response)
            axis['Z' if op.kind == 'R' else 'X'] = 0.0
            weights[op.time, op.kind, tuple(op.qs), q] = axis
        elif ch['name'] == 'DEPOLARIZE1' and len(ch['qs']) == 1:
            q = ch['qs'][0]
            key = op.time, op.kind, tuple(op.qs), q
            if key in keys and fault['pauli'] not in weights[key]:
                # The postmeasurement/gate channel comes before any idle
                # channel attached to the same instruction.
                weights[key][fault['pauli']] = response
    assert all(set(v) == set('XYZ') for v in weights.values())
    return {k: sum(v.values()) / 3 for k, v in weights.items()}


def propose(stem, ledger, ready, end, radius, name):
    stem = Path(stem)
    integration = json.loads(stem.with_suffix('.integration.json').read_text())
    b_path = Path(integration['bc_module'])
    doc = json.loads(b_path.read_text())
    row = copy.deepcopy(doc['candidates'][integration.get('bc_index', 0)])
    ops = row['operations']
    pre, _ = f.parse_current(Path(doc['prefix_stem']).with_suffix('.qasm').read_text())
    release = {q: max((o.time for o in pre if q in o.qs), default=-1) + 1 for q in range(36)}
    exposure = exposure_audit(stem)
    reject_weights = {(r['operation']['time'], r['operation']['kind'], tuple(r['operation']['qs']), r['qubit']):
                      r['rejection'] for r in exposure['segment_weights']}
    gradient = pair_weights(stem, ledger, exposure)
    model = cp_model.CpModel()
    bset = set(doc['roles']['B'])
    starts = [model.NewIntVar(max(max(release[q] for q in o['qs']), o['time'] - radius),
                             min((ready if set(o['qs']) & bset else end) - 1, o['time'] + radius), f't{i}')
              for i, o in enumerate(ops)]
    pair_terms, reject_terms = [], []
    reference_rejection = 0
    for q in sorted({q for o in ops for q in o['qs']}):
        sequence = [i for i, o in enumerate(ops) if q in o['qs']]
        before = [o for o in pre if q in o.qs]
        old = max(before, key=lambda o: o.time) if before else None
        previous_time = old.time if old else None
        reference_time = old.time if old else None
        key = (old.time, old.kind, tuple(old.qs), q) if old else None
        for i in sequence:
            o = ops[i]
            if previous_time is not None:
                model.Add(starts[i] > previous_time)
                if o['kind'] not in ('R', 'RX'):
                    gap = starts[i] - previous_time - 1
                    pair_terms.append(round(45000 * gradient[key]) * gap)
                    reject_terms.append(round(3000 * reject_weights[key]) * gap)
                    reference_rejection += round(3000 * reject_weights[key]) * (o['time'] - reference_time - 1)
            previous_time, reference_time = starts[i], o['time']
            key = o['time'], o['kind'], tuple(o['qs']), q
        if q in bset:
            gap = ready - previous_time - 1
            pair_terms.append(round(45000 * gradient[key]) * gap)
            reject_terms.append(round(3000 * reject_weights[key]) * gap)
            reference_rejection += round(3000 * reject_weights[key]) * (ready - reference_time - 1)
    pair_cost, reject_cost = sum(pair_terms), sum(reject_terms)
    model.Add(reject_cost <= reference_rejection)
    # Lexicographic objective: pair marginal, rejection, latest schedule.
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = 10
    objectives = []
    for objective, maximize in [(pair_cost, False), (reject_cost, False), (sum(starts), True)]:
        model.Maximize(objective) if maximize else model.Minimize(objective)
        status = solver.Solve(model)
        assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE), solver.StatusName(status)
        value = round(solver.ObjectiveValue())
        objectives.append(dict(value=value, status=solver.StatusName(status)))
        model.Add(objective == value)
    changes = []
    for o, t in zip(ops, starts):
        value = solver.Value(t)
        if value != o['time']:
            changes.append(dict(kind=o['kind'], qs=o['qs'], old_time=o['time'], new_time=value,
                                original_bit=o.get('original_bit')))
        o['time'] = value
    row.update(operations=ops, pair_gradient_reference=str(stem), scheduling_changes=changes,
               pair_gradient_objectives=objectives, cx=sum(o['kind'] == 'CX' for o in ops))
    doc['candidates'] = [row]
    output = HERE / 'retimed' / f'{name}_b_module.json'
    output.write_text(json.dumps(doc, indent=2) + '\n')
    return output, integration['a_module'], changes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stem')
    ap.add_argument('--name', default='b_pair47')
    ap.add_argument('--ready', type=int, default=45)
    ap.add_argument('--end', type=int, default=46)
    ap.add_argument('--radius', type=int, default=2)
    ap.add_argument('--iterations', type=int, default=5)
    args = ap.parse_args()
    current = Path(args.stem)
    with contextlib.redirect_stdout(io.StringIO()):
        ledger = pair_audit(current, HERE / 'retimed' / f'{args.name}_base.pairs.json')
    result = dict(parent=str(current), base_c2=ledger['c2'], attempts=[])
    for i in range(args.iterations):
        name = f'{args.name}_{i}'
        module, a_module, changes = propose(current, ledger, args.ready, args.end, args.radius, name)
        if not changes:
            result['stop'] = 'No timing changes in the bounded linear objective'
            break
        with contextlib.redirect_stdout(io.StringIO()):
            full = assemble(a_module, module, 0, 0, name, do_singles=True)
            new = pair_audit(full['stem'], HERE / 'retimed' / f'{name}.pairs.json')
        row = dict(stem=full['stem'], b_module=str(module), c1=full['singles']['c1'],
                   raw=full['raw'], c2=new['c2'], changes=changes)
        result['attempts'].append(row)
        print(json.dumps(row), flush=True)
        if full['raw']['ok'] and row['c1'] < 1e-10 and row['c2'] < ledger['c2'] - 1e-10:
            current, ledger = Path(full['stem']), new
        else:
            result['stop'] = 'Proposal did not improve the exact full-circuit pair coefficient'
            break
    result.update(best_stem=str(current), best_c2=ledger['c2'])
    dest = HERE / 'retimed' / f'{args.name}.result.json'
    dest.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(receipt=str(dest), best_stem=str(current), best_c2=ledger['c2'])), flush=True)


if __name__ == '__main__':
    main()
