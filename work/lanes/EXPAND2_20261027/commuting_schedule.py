"""Schedule the preserved source through exact commuting-operation relations.

The source emitted here contains native operations only. Its optional terminal
diagnostic deliberately uses an ideal resource and is never a full candidate.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import copy
import json
import sys
from pathlib import Path
from ortools.sat.python import cp_model

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
sys.path.insert(0, str(ROOT / 'work/lanes/NATIVE2_20261027'))
import prefix_boundary as pb
import contract_counterfactual as cc
from source_contract import cancel, drop_dead_preparations
from joint import emit
from qtools import write_stem
from qtools.validity import raw_check
from qtools.evaluator import frontend as f


def commute(a, b):
    if not set(a.qs) & set(b.qs):
        return True
    if a.kind == 'CX' and b.kind == 'CX':
        return a.qs[0] != b.qs[1] and a.qs[1] != b.qs[0]
    if b.kind == 'CX':
        return commute(b, a)
    if a.kind == 'CX':
        return ((b.qs == (a.qs[0],) and b.kind in ('M', 'T', 'TDG', 'S', 'SDG', 'Z'))
                or (b.qs == (a.qs[1],) and b.kind in ('MX', 'X', 'SX', 'SXDG')))
    for axis in ({'M', 'T', 'TDG', 'S', 'SDG', 'Z'}, {'MX', 'X', 'SX', 'SXDG'}):
        if a.kind in axis and b.kind in axis:
            return True
    return False


def solve(ops, seconds, seed=0):
    ops = sorted(copy.deepcopy(ops), key=lambda o: o.time)
    horizon = max(o.time for o in ops) + 1
    model = cp_model.CpModel()
    times = [model.new_int_var(0, horizon - 1, f't{i}') for i in range(len(ops))]
    intervals = [model.new_fixed_size_interval_var(t, 1, f'i{i}') for i, t in enumerate(times)]
    for q in range(36):
        model.add_no_overlap([iv for iv, o in zip(intervals, ops) if q in o.qs])
    precedences = []
    for i, a in enumerate(ops):
        for j in range(i + 1, len(ops)):
            if not commute(a, ops[j]):
                model.add(times[j] >= times[i] + 1)
                precedences.append((i, j))
    end = model.new_int_var(1, horizon, 'end')
    model.add_max_equality(end, [t + 1 for t in times])
    releases = []
    for q in range(36):
        if q in pb.D:
            continue
        touching = [t + 1 for t, o in zip(times, ops) if q in o.qs]
        if touching:
            release = model.new_int_var(0, horizon, f'release{q}')
            model.add_max_equality(release, touching)
            releases.append(release)
    model.minimize(100000 * end + 100 * sum(releases) + sum(times))
    for t, o in zip(times, ops):
        model.add_hint(t, o.time)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = seed
    status = solver.solve(model)
    info = dict(status=solver.status_name(status),seconds=solver.wall_time,
                objective_bound=solver.best_objective_bound,precedence_count=len(precedences),
                objective='100000*source_ticks +100*sum(resource_release)+sum(operation_times)')
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, info
    for i, o in enumerate(ops):
        o.time = solver.value(times[i])
    info.update(source_ticks=solver.value(end),objective=solver.objective_value,
                order=[dict(kind=o.kind,qs=o.qs,time=o.time,bit=o.bit) for o in ops])
    ops.sort(key=lambda o: o.time)
    # Delay every reset to just before its next use, preserving the proven order.
    for i, o in enumerate(ops):
        if o.kind not in ('R', 'RX'):
            continue
        next_op = next((u for u in ops[i + 1:] if o.qs[0] in u.qs), None)
        if next_op is not None:
            o.time = next_op.time - 1
    return sorted(ops, key=lambda o: o.time), info


def diagnostic(ops, dets, folder, source):
    pc = cc.make_four_square_contract()
    first = max(o.time for o in ops) + 1
    prepared, round_tick = cc.ideal_prep(pc, first)
    full = copy.deepcopy(ops) + prepared
    full += [f.Op(kind, qs, round_tick + t, None if bit is None else 400 + bit)
             for kind, qs, t, bit in pc.terminal()]
    all_dets = list(dets) + [{400 + b for b in row} for row in pc.DETECTORS]
    text = emit(full, all_dets)
    raw = cc.ideal_contract_check(text, pc.D)
    assert raw['ok'], raw
    stem = folder / 'ideal_resource_diagnostic'
    stem.with_suffix('.qasm').write_text(text)
    meta = dict(data_qubits=pc.D,ideal_contract=raw,diagnostic_only=True,gate_valid=False,
                source=str(source.relative_to(ROOT)),source_noisy=True,
                first_inserted_tick=first,round=round_tick,actual_round=first,
                inserted_ticks=list(range(first,round_tick)),ideal_source_ticks=[],
                scope='Native rescheduled noisy source, ideal instantaneous four-square resource, native terminal.')
    stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return cc.evaluate(stem)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cancel',action='store_true')
    ap.add_argument('--seconds',type=float,default=60)
    ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--price',action='store_true')
    args = ap.parse_args()
    ops,dets,_ = pb.extract(True)
    if args.cancel:
        ops,_ = cancel(sorted(ops,key=lambda o:o.time))
        ops,_ = drop_dead_preparations(ops)
    scheduled, info = solve(ops,args.seconds,args.seed)
    tag = ('pairs' if args.cancel else 'original') + f'_commuting_s{args.seed}'
    folder = HERE/'source_variants'/tag
    folder.mkdir(parents=True,exist_ok=True)
    if scheduled is not None:
        text = emit(scheduled,dets)
        raw = raw_check(text,pb.D)
        assert raw['ok'],raw
        meta = dict(data_qubits=pb.D,raw=raw,cx=sum(o.kind=='CX' for o in scheduled),
                    T=sum(o.kind in ('T','TDG') for o in scheduled),
                    source_ticks=max(o.time for o in scheduled)+1,
                    release={q:1+max((o.time for o in scheduled if q in o.qs),default=-1)
                             for q in range(36) if q not in pb.D})
        source = write_stem(text,pb.D,folder,'source',source=meta)
        (folder/'release.json').write_text(json.dumps(dict(stem=str(source.relative_to(ROOT)),**meta),indent=2)+'\n')
        info.update(source=str(source.relative_to(ROOT)),metadata=meta)
        if args.price:
            info['ideal_resource'] = diagnostic(scheduled,dets,folder,source)
    (folder/'solver.json').write_text(json.dumps(info,indent=2)+'\n')
    print(json.dumps({k:v for k,v in info.items() if k!='order'}),flush=True)


if __name__ == '__main__':
    main()
