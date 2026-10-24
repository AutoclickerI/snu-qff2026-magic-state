"""LNS on the B/C resource with the resource-level proxy as objective.

state: dict(T0, ops=[layer: [[u,v],...]], pivots={q: vec}) (pivot vectors at layer 0)
move: free a window of layers [a, b), enumerate sub-circuits (CP-SAT, presolve off) mapping the actual
cell vectors at a to those at b, score every completion by J = X2 + KZ*RZ + KA*acc1 (c1 must be 0).
usage: lns.py <start.json> <out_prefix> <seconds> <seed> [K]
"""
import sys, json, random, time, math
from pathlib import Path
from ortools.sat.python import cp_model
from qcirc import adjacent
import mkcand, splice, proxy

CELLS = splice.B + splice.C
E = [(u, v) for u in CELLS for v in CELLS if adjacent(u, v)]
KZ, KA = 1.4e-4, 1e-4
BASE = splice.load(Path(__file__).parent / 'v36c')
FIRST_TICK = {4: 37, 5: 35, 6: 42, 11: 31, 13: 34, 19: 34}


def col(i):
    return sum(((i in row) << j) for j, row in enumerate(proxy.ROWS))


def target():
    return {q: col((CELLS.index(q)) % 7) for q in CELLS}


def forward(piv, ops, upto):
    x = {q: 0 for q in CELLS}
    for q, v in piv.items():
        x[int(q)] = v
    for layer in ops[:upto]:
        for u, v in layer:
            x[v] ^= x[u]
    return x


def backward(ops, frm):
    x = target()
    for layer in reversed(ops[frm:]):
        for u, v in layer:
            x[v] ^= x[u]
    return x


def score(state):
    sol = dict(T0=state['T0'], ops=state['ops'], pivots={str(q): v for q, v in state['pivots'].items()})
    try:
        spec = mkcand.spec_from(sol, state.get('policy', 'default'))
        u, d, nb = splice.build(BASE[0], BASE[1], spec)
    except AssertionError as e:
        return None, None
    s, _, _ = proxy.analyse(u, d, flags=sorted({e[2] for e in spec['extra'] if e[2] not in mkcand.CELLS}), starts=mkcand.starts_of(spec))
    if s['c1'] > 1e-12:
        return None, s
    return s['X2'] + KZ * s['RZ'] + KA * s['acc1'], s


def window_solutions(state, a, b, K, seed, avail):
    m = cp_model.CpModel()
    T = list(range(a, b))
    sel = {t: {e: m.NewBoolVar('') for e in E} for t in T}
    for t in T:
        for e in E:
            if t < avail[e[0]] or t < avail[e[1]]:
                m.Add(sel[t][e] == 0)
        for q in CELLS:
            m.AddAtMostOne([sel[t][e] for e in E if q in e])
    x = {t: {q: [m.NewBoolVar('') for _ in range(3)] for q in CELLS} for t in range(a, b + 1)}
    xb = backward(state['ops'], b)
    for q in CELLS:
        for k in range(3):
            m.Add(x[b][q][k] == ((xb[q] >> k) & 1))
    if a == 0:
        nz = []
        for q in CELLS:
            z = m.NewBoolVar(''); m.AddMaxEquality(z, x[0][q]); nz.append(z)
        m.Add(sum(nz) <= 3)
    else:
        xa = forward(state['pivots'], state['ops'], a)
        for q in CELLS:
            for k in range(3):
                m.Add(x[a][q][k] == ((xa[q] >> k) & 1))
    for t in T:
        for q in CELLS:
            ins = [e for e in E if e[1] == q]
            tin = m.NewBoolVar(''); m.AddMaxEquality(tin, [sel[t][e] for e in ins])
            for k in range(3):
                m.Add(x[t + 1][q][k] == x[t][q][k]).OnlyEnforceIf(tin.Not())
                for e in ins:
                    j = m.NewIntVar(0, 1, '')
                    m.Add(x[t + 1][q][k] + x[t][q][k] + x[t][e[0]][k] == 2 * j).OnlyEnforceIf(sel[t][e])
                    m.Add(j == 0).OnlyEnforceIf(sel[t][e].Not())
    rng = random.Random(seed)
    m.Minimize(sum(rng.randint(0, 5) * sel[t][e] for t in T for e in E) + 3 * sum(sel[t][e] for t in T for e in E))
    sols = []

    class CB(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            ops = [[list(e) for e in E if self.Value(sel[t][e])] for t in T]
            piv = None
            if a == 0:
                piv = {q: sum(self.Value(x[0][q][k]) << k for k in range(3)) for q in CELLS}
                piv = {q: v for q, v in piv.items() if v}
            sols.append((ops, piv))
            if len(sols) >= K:
                self.StopSearch()
    s = cp_model.CpSolver()
    s.parameters.cp_model_presolve = False
    s.parameters.enumerate_all_solutions = True
    s.parameters.num_search_workers = 1
    s.parameters.max_time_in_seconds = 20
    s.parameters.random_seed = seed
    # enumerate: drop the objective
    m.ClearObjective()
    s.Solve(m, CB())
    return sols


def run(start, prefix, seconds, seed, K=200):
    rng = random.Random(seed)
    state = json.loads(Path(start).read_text())
    state['pivots'] = {int(q): v for q, v in state['pivots'].items()}
    if isinstance(next(iter(state['pivots'].values())), list):
        state['pivots'] = {q: sum(b << k for k, b in enumerate(v)) for q, v in state['pivots'].items()}
    D = len(state['ops'])
    avail = {q: max(0, FIRST_TICK.get(q, 0) - state['T0']) for q in CELLS}
    J, s = score(state)
    print(json.dumps(dict(start=J, **(s or {}))), flush=True)
    best = (J, json.loads(json.dumps(state)), s)
    t0 = time.time()
    it = 0
    while time.time() - t0 < seconds:
        it += 1
        w = rng.choice([2, 2, 3, 3, 4])
        a = rng.randrange(0, D - w + 1)
        b = a + w
        sols = window_solutions(state, a, b, K, rng.randrange(1 << 30), avail)
        rng.shuffle(sols)
        cand = []
        for ops, piv in sols:
            st = dict(state)
            st['ops'] = state['ops'][:a] + ops + state['ops'][b:]
            if piv is not None:
                st['pivots'] = piv
            j, ss = score(st)
            if j is not None:
                cand.append((j, st, ss))
        if not cand:
            continue
        cand.sort(key=lambda c: c[0])
        j, st, ss = cand[0]
        if j < J - 1e-12 or (j < J + 2e-8 and rng.random() < 0.3):
            state, J = st, j
            if j < best[0] - 1e-12:
                best = (j, json.loads(json.dumps(st)), ss)
                out = dict(best[1]); out['pivots'] = {str(q): v for q, v in out['pivots'].items()}
                out['J'] = j; out['proxy'] = ss
                Path(prefix + '.json').write_text(json.dumps(out))
                print(json.dumps(dict(it=it, t=round(time.time() - t0), J=j, win=[a, b], nsol=len(sols),
                                      X2=ss['X2'], RZ=ss['RZ'], acc1=ss['acc1'], cx=sum(map(len, st['ops'])))), flush=True)
    print(json.dumps(dict(done=True, best=best[0], iters=it)), flush=True)


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else 200)


def normalize(state):
    """Pivot vectors re-expressed so that the forward run ends exactly at target() (fixed basis)."""
    piv = sorted(state['pivots'])
    unit = {q: 1 << k for k, q in enumerate(piv)}
    F = forward(unit, state['ops'], len(state['ops']))
    T = target()
    import itertools
    for vs in itertools.product(range(1, 8), repeat=len(piv)):
        ok = True
        for q in CELLS:
            acc = 0
            for k in range(len(piv)):
                if (F[q] >> k) & 1:
                    acc ^= vs[k]
            if acc != T[q]:
                ok = False
                break
        if ok:
            st = dict(state)
            st['pivots'] = {q: v for q, v in zip(piv, vs)}
            return st
    raise ValueError('state does not reach the target span')
