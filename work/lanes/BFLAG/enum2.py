"""Exhaustive local re-synthesis with the full FT model: free the CX on a cell subset over a layer window,
everything else frozen; hard first-order clean (F1); window CX count <= incumbent + extra; every completion
is scored by the proxy J.  usage: enum2.py <start.json> <cells|all> <a> <b> <extra> <maxsol> <out.json> [robust_soft]"""
import sys, json, time
from ortools.sat.python import cp_model
import synth_bc as S
import lns

def enum(state, sub, a, b, extra, maxsol, seconds=900, soft=None):
    D = len(state['ops']); T0 = state['T0']
    avail = {q: max(0, lns.FIRST_TICK.get(q, 0) - T0) for q in S.CELLS}
    m, sel, x, nz, E, ncx, zexp = S.build(D, avail, robust=False)
    m.ClearObjective()
    cur = {(t, tuple(e)) for t, layer in enumerate(state['ops']) for e in layer}
    free = []
    for t in range(D):
        for e in E:
            if a <= t < b and e[0] in sub and e[1] in sub:
                free.append(sel[t][e])
            else:
                m.Add(sel[t][e] == int((t, e) in cur))
    n0 = sum(1 for t in range(a, b) for e in E if (t, e) in cur and e[0] in sub and e[1] in sub)
    m.Add(sum(free) <= n0 + extra)
    best = [None]; cnt = [0, 0]
    class CB(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            ops = [[list(e) for e in E if self.Value(sel[t][e])] for t in range(D)]
            piv = {q: sum(self.Value(x[0][q][k]) << k for k in range(3)) for q in S.CELLS}
            st = dict(T0=T0, ops=ops, pivots={q: v for q, v in piv.items() if v})
            j, s = lns.score(st)
            cnt[0] += 1
            if j is not None:
                cnt[1] += 1
                if best[0] is None or j < best[0][0]:
                    best[0] = (j, st, s)
            if cnt[0] >= maxsol:
                self.StopSearch()
    sv = cp_model.CpSolver()
    sv.parameters.cp_model_presolve = False
    sv.parameters.enumerate_all_solutions = True
    sv.parameters.num_search_workers = 1
    sv.parameters.max_time_in_seconds = seconds
    status = sv.Solve(m, CB())
    return sv.StatusName(status), cnt, best[0], n0

if __name__ == '__main__':
    state = json.load(open(sys.argv[1]))
    state['pivots'] = {int(q): v for q, v in state['pivots'].items()}
    sub = set(S.CELLS) if sys.argv[2] == 'all' else set(int(q) for q in sys.argv[2].split(','))
    a, b, extra, maxsol = map(int, sys.argv[3:7])
    t = time.time()
    status, cnt, best, n0 = enum(state, sub, a, b, extra, maxsol)
    j0, s0 = lns.score(dict(state))
    print(json.dumps(dict(status=status, n=cnt[0], valid=cnt[1], n0=n0, start=j0, startX2=s0['X2'], best=best[0] if best else None,
                          bestproxy=best[2] if best else None, seconds=round(time.time() - t, 1))))
    if best:
        out = dict(best[1]); out['pivots'] = {str(q): v for q, v in out['pivots'].items()}; out['J'] = best[0]; out['proxy'] = best[2]
        json.dump(out, open(sys.argv[7], 'w'))
