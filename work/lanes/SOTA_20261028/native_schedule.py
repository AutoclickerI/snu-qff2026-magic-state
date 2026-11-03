"""Search whole native schedules with complete noisy evaluation.

Every operation and measurement relation is retained. Commuting operations may
change order, and local windows are scheduled jointly. No clock or noise channel
is removed from the evaluator. This is a bounded lifetime/schedule search, not
an architecture optimality claim.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import concurrent.futures
import copy
import hashlib
import json
import random
import sys
import time
from pathlib import Path
from ortools.sat.python import cp_model

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
sys.path.insert(0, str(ROOT / 'work/lanes/EXPAND2_20261027'))
import frontend_axis as f
from joint import emit
from axis_echo import exact
from qtools.validity import raw_check
from qtools import write_stem

BASE = ROOT / 'work/lanes/EXPAND2_20261027/release_phase/native_incumbent_phase_late'


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


def solve(base, window, seed, seconds, mode):
    ops, dets = f.parse_current(base.with_suffix('.qasm').read_text())
    ops = sorted(copy.deepcopy(ops), key=lambda x: x.time)
    lo, hi = window
    rng = random.Random(seed)
    model = cp_model.CpModel()
    times = []
    movable = []
    for i, op in enumerate(ops):
        free = lo <= op.time <= hi
        t = model.new_int_var(lo if free else op.time, hi if free else op.time, f't{i}')
        times.append(t)
        if free:
            movable.append(i)
        model.add_hint(t, op.time)
    intervals = [model.new_fixed_size_interval_var(t, 1, f'i{i}') for i,t in enumerate(times)]
    for q in range(36):
        uses = [i for i,o in enumerate(ops) if q in o.qs]
        model.add_no_overlap([intervals[i] for i in uses])
        for k,i in enumerate(uses):
            for j in uses[k+1:]:
                if not commute(ops[i], ops[j]):
                    model.add(times[j] >= times[i] + 1)
    # Joint stochastic objectives explore different feasible lifetimes. The
    # objective is a proposal mechanism; exact L/A alone selects a winner.
    weights = []
    for i in movable:
        o = ops[i]
        if mode == 'random':
            w = rng.randint(-20, 20)
        elif mode == 'lateprep':
            w = -rng.randint(10, 40) if o.kind in ('R', 'RX') else rng.randint(-5, 5)
        elif mode == 'earlyread':
            w = rng.randint(10, 40) if o.kind in ('M', 'MX') else rng.randint(-5, 5)
        elif mode == 'resource':
            resource = set((12,26,25,11,3,28,17,18,27,24,5,4,29,23))
            w = -rng.randint(5, 25) if set(o.qs) <= resource and o.time >= 29 else rng.randint(-5, 5)
        elif mode == 'early':
            w = rng.randint(1, 20)
        else:
            raise ValueError(mode)
        weights.append(w * times[i])
    end = model.new_int_var(1, max(o.time for o in ops)+1, 'end')
    model.add_max_equality(end, [t+1 for t in times])
    model.minimize(100000 * end + sum(weights))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = seed
    status = solver.solve(model)
    info = dict(status=solver.status_name(status), window=window, seed=seed,
                mode=mode, solver_seconds=solver.wall_time, movable=len(movable))
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, info
    changed = []
    for i,op in enumerate(ops):
        t = solver.value(times[i])
        if t != op.time:
            changed.append(dict(operation=i, kind=op.kind, qs=op.qs, old=op.time, new=t))
        op.time = t
    ops.sort(key=lambda o:o.time)
    info.update(changed=changed, clocks=solver.value(end), objective=solver.objective_value,
                objective_bound=solver.best_objective_bound)
    return (ops,dets), info


def run(job):
    base, window, seed, seconds, mode, folder = job
    base,folder = Path(base),Path(folder)
    began=time.perf_counter()
    data=json.loads(base.with_suffix('.json').read_text())['data_qubits']
    row=dict(base=str(base.relative_to(ROOT)),window=window,seed=seed,mode=mode)
    try:
        result,info=solve(base,window,seed,seconds,mode)
        row.update(solver=info)
        if result is None:
            return row
        ops,dets=result
        text=emit(ops,dets)
        row.update(raw=raw_check(text,data),cx=sum(o.kind=='CX' for o in ops),clocks=max(o.time for o in ops)+1)
        stem=write_stem(text,data,folder,f'{mode}_{window[0]}_{window[1]}_{seed}',source=dict(base=row['base'],schedule=info))
        row['stem']=str(stem.relative_to(ROOT))
        if row['raw']['ok']:
            row['exact']=exact(stem)
        stem.with_suffix('.result.json').write_text(json.dumps(row,indent=2)+'\n')
    except Exception as exc:
        import traceback
        row.update(error=str(exc),traceback=traceback.format_exc())
    row['seconds']=time.perf_counter()-began
    return row


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--base',type=Path,default=BASE)
    parser.add_argument('--count',type=int,default=40)
    parser.add_argument('--start',type=int,default=0)
    parser.add_argument('--seconds',type=float,default=5)
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--tag',default='schedule')
    args=parser.parse_args()
    folder=HERE/args.tag;folder.mkdir(parents=True,exist_ok=True)
    windows=[(29,48),(0,48),(20,45),(0,25),(30,46),(10,40),(39,48),(0,48)]
    modes=['random','lateprep','earlyread','resource','early']
    jobs=[(str(args.base.resolve()),windows[k%len(windows)],k,args.seconds,
           modes[(k//len(windows))%len(modes)],str(folder)) for k in range(args.start,args.start+args.count)]
    rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for row in pool.map(run,jobs):
            rows.append(row)
            (folder/'results.json').write_text(json.dumps(dict(completed=False,results=rows),indent=2)+'\n')
            print(json.dumps({k:row[k] for k in ('seed','mode','window','stem','exact','error','seconds') if k in row}),flush=True)
    (folder/'results.json').write_text(json.dumps(dict(completed=True,results=rows),indent=2)+'\n')


if __name__ == '__main__':
    main()
