"""Joint native input preparation on A+D, avoiding a fixed transfer boundary.

Searches the entire 14-cell connected graph, with four random inputs and one
T input. The solved final A cells are exact zeros and D is the Steane target.
The existing 24-CX encoder+transfer supplies a reproducible feasible hint.
"""
import argparse
import hashlib
import json
from pathlib import Path

from encoder import A, D, GENERATORS, HERE, ROOT, cp_model, emit, f, raw_check


def solve(depth=7, seconds=45, seed=1):
    cells = A + D
    target = {q: 0 for q in A}
    target.update({q: sum(((g >> i) & 1) << j for j, g in enumerate(GENERATORS))
                   for i, q in enumerate(D)})
    edges = [(a, b) for a in cells for b in cells
             if abs(a // 6 - b // 6) + abs(a % 6 - b % 6) == 1]
    m = cp_model.CpModel()
    gates = [{e: m.NewBoolVar(f'c_{t}_{e}') for e in edges} for t in range(depth)]
    state = [{q: [m.NewBoolVar(f'x_{t}_{q}_{k}') for k in range(4)] for q in cells}
             for t in range(depth + 1)]
    pivots = {q: m.NewBoolVar(f'p_{q}') for q in cells}
    magic = {q: m.NewBoolVar(f'magic_{q}') for q in cells}
    for q in cells:
        m.AddMaxEquality(pivots[q], state[0][q])
        m.Add(sum(state[0][q][:3]) == 0).OnlyEnforceIf(magic[q])
        m.Add(state[0][q][3] == 1).OnlyEnforceIf(magic[q])
        m.AddBoolOr(state[0][q][:3] + [state[0][q][3].Not(), magic[q]])
        for k, bit in enumerate(state[-1][q]):
            m.Add(bit == ((target[q] >> k) & 1))
    m.Add(sum(pivots.values()) == 4)
    m.Add(sum(magic.values()) == 1)
    for t in range(depth):
        for q in cells:
            m.AddAtMostOne(v for e, v in gates[t].items() if q in e)
            incoming = [e for e in edges if e[1] == q]
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
    hint = json.loads((HERE / 'encoder/depth5_seed1.json').read_text())
    hlayers = hint['encoding_layers'] + [list(map(list, zip(A, D))), list(map(list, zip(D, A)))]
    if depth >= len(hlayers):
        hstate = {q: int(hint['initial_rows'].get(str(q), 0)) for q in cells}
        for q in cells:
            m.AddHint(pivots[q], int(bool(hstate[q])))
            m.AddHint(magic[q], int(q == hint['magic_input']))
        for t in range(depth + 1):
            for q in cells:
                for k, bit in enumerate(state[t][q]):
                    m.AddHint(bit, (hstate[q] >> k) & 1)
            if t < depth:
                layer = {tuple(e) for e in hlayers[t]} if t < len(hlayers) else set()
                for e, variable in gates[t].items():
                    m.AddHint(variable, int(e in layer))
                for a, b in layer:
                    hstate[b] ^= hstate[a]
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.random_seed = seed
    status = solver.Solve(m)
    out = dict(status=solver.StatusName(status), depth_bound=depth, seconds=solver.WallTime(),
               seed=seed, A=A, D=D, css_generators=GENERATORS, objective_lower_bound=solver.BestObjectiveBound(),
               scope='Exact native one-T input module, all14 cells jointly synthesized; standalone fault tolerance is not claimed.')
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        layers = [[list(e) for e, v in row.items() if solver.Value(v)] for row in gates]
        layers = [row for row in layers if row]
        initial = {q: sum(solver.Value(v) << k for k, v in enumerate(state[0][q])) for q in cells}
        root = next(q for q, v in magic.items() if solver.Value(v))
        actual = initial.copy()
        for row in layers:
            for a, b in row:
                actual[b] ^= actual[a]
        assert actual == target and initial[root] == 8
        operations = [dict(time=t + 2, kind='CX', qs=e) for t, row in enumerate(layers) for e in row]
        operations.append(dict(time=1, kind='T', qs=[root]))
        for q in cells:
            first = min((o['time'] for o in operations if q in o['qs']), default=2)
            operations.append(dict(time=first - 1, kind='RX' if initial[q] else 'R', qs=[q]))
        operations.sort(key=lambda o: (o['time'], o['kind'], o['qs']))
        ops = [f.Op(o['kind'], tuple(o['qs']), o['time']) for o in operations]
        f.DATA = D
        text = emit(ops, [])
        out.update(initial_rows=initial, magic_input=root, encoding_cx=solver.Value(ncx),
                   cx=solver.Value(ncx), encoding_layers=layers, operations=operations,
                   data_ready=len(layers) + 2, cleared_cells=A, raw=raw_check(text, D),
                   data_qubits=D, qasm_sha256=hashlib.sha256(text.encode()).hexdigest())
        assert out['raw']['ok'], out['raw']
        stem = HERE / 'encoder' / f'joint_depth{depth}_seed{seed}'
        stem.with_suffix('.qasm').write_text(text)
        out['stem'] = str(stem.relative_to(ROOT))
    (HERE / 'encoder' / f'joint_depth{depth}_seed{seed}.json').write_text(json.dumps(out, indent=2) + '\n')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--depth', type=int, default=7)
    ap.add_argument('--seconds', type=float, default=45)
    ap.add_argument('--seed', type=int, default=1)
    args = ap.parse_args()
    out = solve(args.depth, args.seconds, args.seed)
    print(json.dumps({k: out.get(k) for k in ('status', 'cx', 'data_ready', 'seconds', 'objective_lower_bound', 'stem', 'raw')}), flush=True)
    (HERE / 'encoder' / f'joint_depth{args.depth}_seed{args.seed}.process.json').write_text(
        json.dumps(dict(completed=True, returncode=0), indent=2) + '\n')
