"""Layouts that free grid neighbours of late-idling data (for INTEG gadgets), at fixed R.
usage: freed.py R W [need data label | -] [near]  -- spare cell free from R-W on; weights = v36c residual late idle per data label (e-6).
Tie-break: most roles kept at v36c's cells, then fewest hops."""
import sys, json
sys.path.insert(0, '.')
import layout as L
L.CROSS = True
V = dict(A=[1, 14, 8, 9, 2, 16, 15], B=[6, 26, 13, 11, 4, 23, 27], C=[12, 25, 19, 17, 5, 29, 28])
WT = {0: 0.42, 1: 1.24, 2: 1.07, 3: 0.90, 4: 1.05, 5: 0.67, 6: 0.44}  # D0 q0 .. D6 q21
R, W = int(sys.argv[1]), int(sys.argv[2])
need = [int(sys.argv[3])] if len(sys.argv) > 3 and sys.argv[3] != '-' else []
prio = sys.argv[4] if len(sys.argv) > 4 else 'weight'
o = L.solve(A_LEN=4, BC_LEN=12, BC_LATE=6, NLATE=4, MAXH=3, fixR=R, spareW=W, spareWt=WT, near=V, need=need, prio=prio)
keep = {k: o.get(k) for k in ('status', 'R', 'hops', 'paths', 'A', 'B', 'C', 'late', 'flag', 'arrival', 'spare')}
if 'A' in o:
    keep['moved_roles'] = sum(1 for r in 'ABC' for i in range(7) if o[r][i] != V[r][i])
    keep['freed_weight_e6'] = round(sum(WT[i] for i in {sp['data'] for sp in o['spare']}), 2)
print(R, W, need, prio, json.dumps(keep), flush=True)
if 'D' in o:
    print(L.draw(o), flush=True)
