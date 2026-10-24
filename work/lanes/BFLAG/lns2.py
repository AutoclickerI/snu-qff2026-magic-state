"""Full-model LNS: CP-SAT (soft robust + Z exposure + CX) over the whole resource with a random subset of
layer decisions frozen to the incumbent; every solution the solver reports is scored by the proxy J.
usage: lns2.py <start.json> <out_prefix> <seconds> <seed> [free_frac] [D T0]"""
import sys, json, random, time
from pathlib import Path
from ortools.sat.python import cp_model
import synth_bc as S
import lns

def run(start, prefix, seconds, seed, free=0.35, D=None, T0=None):
    rng = random.Random(seed)
    state = json.loads(Path(start).read_text())
    state['pivots'] = {int(q): (v if isinstance(v, int) else sum(b << k for k, b in enumerate(v))) for q, v in state['pivots'].items()}
    state = lns.normalize(state)
    if D is not None and D != len(state['ops']):
        # pad empty layers at the front (earlier start)
        pad = D - len(state['ops'])
        state['ops'] = [[] for _ in range(pad)] + state['ops']
        state['T0'] = T0
    D = len(state['ops'])
    T0 = state['T0']
    avail = {q: max(0, lns.FIRST_TICK.get(q, 0) - T0) for q in S.CELLS}
    J, s = lns.score(state)
    print(json.dumps(dict(start=J, D=D, T0=T0, **(s or {}))), flush=True)
    best = (J if J is not None else 1.0, state, s)
    t0 = time.time(); it = 0
    while time.time() - t0 < seconds:
        it += 1
        m, sel, x, nz, E, ncx, zexp = S.build(D, avail, soft=(rng.choice([30, 50, 80]), rng.choice([10, 20, 30])),
                                               w_z=rng.choice([3, 7, 12]), w_cx=rng.choice([1, 3, 6]))
        cur = {(t, tuple(e)) for t, layer in enumerate(best[1]['ops']) for e in layer}
        # freeze a random subset of decisions (layers or cells)
        mode = rng.choice(['layers', 'cells', 'random'])
        if mode == 'layers':
            w = rng.randint(3, 6); a = rng.randint(0, max(0, D - w)); freel = set(range(a, a + w))
            frz = lambda t, e: t not in freel
        elif mode == 'cells':
            k = rng.randint(4, 8); a = rng.randint(0, 14 - k); path = [4, 5, 11, 17, 23, 29, 28, 27, 26, 25, 19, 13, 12, 6]
            fc = set(path[a:a + k]); frz = lambda t, e: not (e[0] in fc and e[1] in fc)
        else:
            frz = lambda t, e: rng.random() > free
        for t in range(D):
            for e in E:
                if frz(t, e):
                    m.Add(sel[t][e] == int((t, e) in cur))
        # hint the incumbent
        for t in range(D):
            for e in E:
                m.AddHint(sel[t][e], int((t, e) in cur))
        sols = []
        class CB(cp_model.CpSolverSolutionCallback):
            def on_solution_callback(self):
                ops = [[list(e) for e in E if self.Value(sel[t][e])] for t in range(D)]
                piv = {q: sum(self.Value(x[0][q][k]) << k for k in range(3)) for q in S.CELLS}
                sols.append((ops, {q: v for q, v in piv.items() if v}))
        sv = cp_model.CpSolver()
        sv.parameters.cp_model_presolve = False
        sv.parameters.num_search_workers = 1
        sv.parameters.max_time_in_seconds = rng.choice([5, 10, 20])
        sv.parameters.random_seed = rng.randrange(1 << 30)
        sv.Solve(m, CB())
        for ops, piv in sols:
            st = dict(T0=T0, ops=ops, pivots=piv)
            j, ss = lns.score(st)
            if j is not None and j < best[0] - 1e-12:
                best = (j, st, ss)
                out = dict(st); out['pivots'] = {str(q): v for q, v in piv.items()}; out['J'] = j; out['proxy'] = ss
                Path(prefix + '.json').write_text(json.dumps(out))
                print(json.dumps(dict(it=it, t=round(time.time() - t0), mode=mode, J=j, X2=ss['X2'], RZ=ss['RZ'],
                                      acc1=ss['acc1'], cx=sum(map(len, ops)))), flush=True)
    print(json.dumps(dict(done=True, best=best[0], iters=it)), flush=True)

if __name__ == '__main__':
    a = sys.argv
    run(a[1], a[2], float(a[3]), int(a[4]), float(a[5]) if len(a) > 5 else 0.35,
        int(a[6]) if len(a) > 6 else None, int(a[7]) if len(a) > 7 else None)
