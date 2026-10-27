"""Native one-T Steane encoder on the connected incumbent A footprint.

The four initial random-bit labels are solved, not fixed to a systematic
encoder. Exactly one occupied input has label 8, the logical variable, so a
single T at that input produces |T_L>. The other three labels may be any
independent basis of the remaining input variables. Rank is preserved by
CNOT and is certified by the final four-dimensional CSS generator matrix.

This is an input module, not a fault-tolerant preparation on its own.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
from ortools.sat.python import cp_model
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit

A = [7, 14, 13, 9, 8, 21, 15]
D = [6, 20, 19, 10, 2, 22, 16]
GENERATORS = [85, 102, 120, 7]
TARGET = {q: sum(((g >> i) & 1) << j for j, g in enumerate(GENERATORS))
          for i, q in enumerate(A)}
EDGES = [(a, b) for a in A for b in A
         if abs(a // 6 - b // 6) + abs(a % 6 - b % 6) == 1]


def solve(depth=6, seconds=30, seed=1):
    m = cp_model.CpModel()
    gates = [{e: m.NewBoolVar(f'cx_{t}_{e[0]}_{e[1]}') for e in EDGES}
             for t in range(depth)]
    state = [{q: [m.NewBoolVar(f'x_{t}_{q}_{k}') for k in range(4)] for q in A}
             for t in range(depth + 1)]
    pivots = {q: m.NewBoolVar(f'p_{q}') for q in A}
    magic = {q: m.NewBoolVar(f'magic_{q}') for q in A}
    for q in A:
        m.AddMaxEquality(pivots[q], state[0][q])
        m.Add(sum(state[0][q][:3]) == 0).OnlyEnforceIf(magic[q])
        m.Add(state[0][q][3] == 1).OnlyEnforceIf(magic[q])
        m.AddBoolOr(state[0][q][:3] + [state[0][q][3].Not(), magic[q]])
        for k, bit in enumerate(state[-1][q]):
            m.Add(bit == ((TARGET[q] >> k) & 1))
    m.Add(sum(pivots.values()) == 4)
    m.Add(sum(magic.values()) == 1)
    for t in range(depth):
        for q in A:
            m.AddAtMostOne(v for e, v in gates[t].items() if q in e)
            incoming = [e for e in EDGES if e[1] == q]
            active = m.NewBoolVar(f'incoming_{t}_{q}')
            m.AddMaxEquality(active, [gates[t][e] for e in incoming])
            for k in range(4):
                m.Add(state[t + 1][q][k] == state[t][q][k]).OnlyEnforceIf(active.Not())
                for a, b in incoming:
                    carry = m.NewBoolVar('')
                    m.Add(state[t + 1][b][k] + state[t][b][k] + state[t][a][k]
                          == 2 * carry).OnlyEnforceIf(gates[t][a, b])
    ncx = sum(v for row in gates for v in row.values())
    m.Minimize(ncx)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = seed
    status = solver.Solve(m)
    out = dict(status=solver.StatusName(status), depth_bound=depth,
               seconds=solver.WallTime(), seed=seed, A=A, D=D,
               css_generators=GENERATORS,
               scope='Native exact one-T input module; standalone fault tolerance is not claimed.')
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        layers = [[list(e) for e, v in row.items() if solver.Value(v)] for row in gates]
        layers = [row for row in layers if row]
        initial = {q: sum(solver.Value(v) << k for k, v in enumerate(state[0][q])) for q in A}
        root = next(q for q, v in magic.items() if solver.Value(v))
        actual = initial.copy()
        for row in layers:
            for a, b in row:
                actual[b] ^= actual[a]
        assert actual == TARGET and initial[root] == 8
        operations = [dict(time=0, kind='RX' if initial[q] else 'R', qs=[q]) for q in A]
        operations.append(dict(time=1, kind='T', qs=[root]))
        operations += [dict(time=t + 2, kind='CX', qs=e) for t, row in enumerate(layers) for e in row]
        # Coherent transfer onto the disconnected output footprint. D starts
        # at zero; the two-CX map is |psi>_A|0>_D -> |0>_A|psi>_D.
        move = len(layers) + 2
        operations += [dict(time=move - 1, kind='R', qs=[q]) for q in D]
        operations += [dict(time=move, kind='CX', qs=[a, d]) for a, d in zip(A, D)]
        operations += [dict(time=move + 1, kind='CX', qs=[d, a]) for a, d in zip(A, D)]
        operations.sort(key=lambda o: (o['time'], o['kind'], o['qs']))
        ops = [f.Op(o['kind'], tuple(o['qs']), o['time']) for o in operations]
        f.DATA = D
        text = emit(ops, [])
        out.update(initial_rows=initial, magic_input=root, encoding_cx=solver.Value(ncx),
                   cx=solver.Value(ncx) + 14, encoding_layers=layers,
                   operations=operations, data_ready=move + 2,
                   cleared_cells=A, raw=raw_check(text, D),
                   data_qubits=D, qasm_sha256=hashlib.sha256(text.encode()).hexdigest())
        assert out['raw']['ok'], out['raw']
        stem = HERE / 'encoder' / f'depth{depth}_seed{seed}'
        stem.parent.mkdir(parents=True, exist_ok=True)
        stem.with_suffix('.qasm').write_text(text)
        out['stem'] = str(stem.relative_to(ROOT))
    folder = HERE / 'encoder'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f'depth{depth}_seed{seed}.json').write_text(json.dumps(out, indent=2) + '\n')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--depth', type=int, default=6)
    ap.add_argument('--seconds', type=float, default=30)
    ap.add_argument('--seed', type=int, default=1)
    args = ap.parse_args()
    started = time.perf_counter()
    result = solve(args.depth, args.seconds, args.seed)
    print(json.dumps({k: result.get(k) for k in ('status', 'encoding_cx', 'cx', 'data_ready', 'magic_input', 'seconds', 'stem', 'raw')}), flush=True)
    (HERE / 'encoder' / f'depth{args.depth}_seed{args.seed}.process.json').write_text(
        json.dumps(dict(completed=True, returncode=0, seconds=time.perf_counter() - started), indent=2) + '\n')
