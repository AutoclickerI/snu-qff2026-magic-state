"""Re-synthesize the CX on a cell subset (edges inside it free over all layers), the rest frozen to a start
resource; robust hard for faults on the subset cells (and soft elsewhere if given); report proxy + save.
usage: localrob.py <start.json> <cells> <out.json> [seconds] [extra_free_cells]"""
import sys, json, time
from ortools.sat.python import cp_model
import synth_bc as S
import lns, mkcand
start = json.load(open(sys.argv[1]))
sub = set(int(q) for q in sys.argv[2].split(','))
secs = float(sys.argv[4]) if len(sys.argv) > 4 else 300
D = len(start['ops']); T0 = start['T0']
avail = {q: max(0, lns.FIRST_TICK.get(q, 0) - T0) for q in S.CELLS}
rc = sorted(int(q) for q in (sys.argv[5].split(",") if len(sys.argv) > 5 else sys.argv[2].split(",")))
m, sel, x, nz, E, ncx, zexp = S.build(D, avail, robust=True, robust_cells=rc, w_z=6, w_cx=12)
cur = {(t, tuple(e)) for t, layer in enumerate(start['ops']) for e in layer}
for t in range(D):
    for e in E:
        if e[0] in sub and e[1] in sub:
            m.AddHint(sel[t][e], int((t, e) in cur))
        else:
            m.Add(sel[t][e] == int((t, e) in cur))
sv = cp_model.CpSolver()
sv.parameters.cp_model_presolve = False
sv.parameters.num_search_workers = 4
sv.parameters.max_time_in_seconds = secs
st = sv.Solve(m)
print(sv.StatusName(st))
if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    ops = [[list(e) for e in E if sv.Value(sel[t][e])] for t in range(D)]
    piv = {str(q): sum(sv.Value(x[0][q][k]) << k for k in range(3)) for q in S.CELLS if sv.Value(nz[0][q])}
    out = dict(T0=T0, ops=ops, pivots=piv)
    json.dump(out, open(sys.argv[3], 'w'))
    stem, s, spec = mkcand.make(out, sys.argv[3].split('/')[-1].replace('.json', ''))
    print(json.dumps(s), sum(map(len, ops)))
