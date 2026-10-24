"""Exhaustive local re-synthesis: free the CX inside a cell subset over a layer window (others frozen),
enumerate every completion that reaches the same final state, score each by the proxy J.
usage: enum_local.py <start.json> <cells comma> <a> <b> <maxsol> <out.json>"""
import sys, json, time
from ortools.sat.python import cp_model
import lns
from lns import E, CELLS

def enum(state, sub, a, b, maxsol, seconds=600):
    D = len(state['ops'])
    avail = {q: max(0, lns.FIRST_TICK.get(q, 0) - state['T0']) for q in CELLS}
    cur = {(t, tuple(e)) for t, layer in enumerate(state['ops']) for e in layer}
    m = cp_model.CpModel()
    T = list(range(a, b))
    sel = {t: {e: m.NewBoolVar('') for e in E} for t in T}
    for t in T:
        for e in E:
            inside = e[0] in sub and e[1] in sub
            if not inside:
                m.Add(sel[t][e] == int((t, e) in cur))
            elif t < avail[e[0]] or t < avail[e[1]]:
                m.Add(sel[t][e] == 0)
        for q in CELLS:
            m.AddAtMostOne([sel[t][e] for e in E if q in e])
    x = {t: {q: [m.NewBoolVar('') for _ in range(3)] for q in CELLS} for t in range(a, b + 1)}
    xb = lns.backward(state['ops'], b)
    xa = lns.forward(state['pivots'], state['ops'], a)
    for q in CELLS:
        for k in range(3):
            m.Add(x[b][q][k] == ((xb[q] >> k) & 1))
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
    res = []
    best = [None]
    class CB(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            ops = [list(l) for l in state['ops']]
            for t in T:
                ops[t] = [list(e) for e in E if self.Value(sel[t][e])]
            st = dict(T0=state['T0'], ops=ops, pivots=state['pivots'])
            j, s = lns.score(st)
            res.append(j)
            if j is not None and (best[0] is None or j < best[0][0]):
                best[0] = (j, st, s)
            if len(res) >= maxsol:
                self.StopSearch()
    sv = cp_model.CpSolver()
    sv.parameters.cp_model_presolve = False
    sv.parameters.enumerate_all_solutions = True
    sv.parameters.num_search_workers = 1
    sv.parameters.max_time_in_seconds = seconds
    st = sv.Solve(m, CB())
    return sv.StatusName(st), res, best[0]

if __name__ == '__main__':
    state = json.load(open(sys.argv[1]))
    state['pivots'] = {int(q): (v if isinstance(v, int) else sum(b << k for k, b in enumerate(v))) for q, v in state['pivots'].items()}
    state = lns.normalize(state)
    sub = set(int(q) for q in sys.argv[2].split(','))
    a, b, maxsol = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    t = time.time()
    status, res, best = enum(state, sub, a, b, maxsol)
    ok = [j for j in res if j is not None]
    j0, s0 = lns.score(dict(state))
    print(json.dumps(dict(status=status, n=len(res), valid=len(ok), start=j0, best=best[0] if best else None,
                          bestproxy=best[2] if best else None, seconds=round(time.time() - t, 1))))
    if best:
        out = dict(best[1]); out['pivots'] = {str(q): v for q, v in out['pivots'].items()}; out['J'] = best[0]; out['proxy'] = best[2]
        json.dump(out, open(sys.argv[6], 'w'))
