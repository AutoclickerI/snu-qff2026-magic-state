"""Fewest moved roles (vs v36c/v36h end state) at fixed R, then fewest hops. usage: near.py R [MAXH]"""
import sys, json
sys.path.insert(0, '.')
import layout as L
L.CROSS = True
V = dict(A=[1, 14, 8, 9, 2, 16, 15], B=[6, 26, 13, 11, 4, 23, 27], C=[12, 25, 19, 17, 5, 29, 28])
R = int(sys.argv[1]); MAXH = int(sys.argv[2]) if len(sys.argv) > 2 else 3
WT = {i: 0.0 for i in range(7)}
o = L.solve(A_LEN=4, BC_LEN=12, BC_LATE=6, NLATE=4, MAXH=MAXH, fixR=R, spareW=0, spareWt=WT, near=V, prio='near')
keep = {k: o.get(k) for k in ('status', 'R', 'hops', 'paths', 'A', 'B', 'C', 'late', 'flag', 'arrival')}
if 'A' in o:
    keep['moved_roles'] = sum(1 for r in 'ABC' for i in range(7) if o[r][i] != V[r][i])
    keep['moved'] = [f"{r}{i}:{V[r][i]}->{o[r][i]}" for r in 'ABC' for i in range(7) if o[r][i] != V[r][i]]
print(R, json.dumps(keep), flush=True)
if 'D' in o:
    print(L.draw(o), flush=True)
