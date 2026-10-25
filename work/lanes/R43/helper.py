"""Layouts with spare helper cells next to the flag-gap data (CX D->helper at R, MX at R+1, RX at R-1), fewest moved
roles vs v36h, then same paths, then fewest hops. usage: helper.py R nhelper [MAXH]"""
import sys, json
sys.path.insert(0, '.')
import layout as L
L.CROSS = True
V = dict(A=[1, 14, 8, 9, 2, 16, 15], B=[6, 26, 13, 11, 4, 23, 27], C=[12, 25, 19, 17, 5, 29, 28],
         paths={0: [0], 1: [20], 2: [7], 3: [4, 10], 4: [3], 5: [15, 16, 22], 6: [8, 9, 15, 21]})
R = int(sys.argv[1]); nh = int(sys.argv[2]); MAXH = int(sys.argv[3]) if len(sys.argv) > 3 else 3
o = L.solve(A_LEN=4, BC_LEN=12, BC_LATE=6, NLATE=4, MAXH=MAXH, fixR=R, helper=nh, near=V)
keep = {k: o.get(k) for k in ('status', 'R', 'hops', 'paths', 'A', 'B', 'C', 'late', 'flag', 'flagdata', 'helpers', 'arrival')}
if 'A' in o:
    keep['moved_roles'] = sum(1 for r in 'ABC' for i in range(7) if o[r][i] != V[r][i])
    keep['moved'] = [f"{r}{i}:{V[r][i]}->{o[r][i]}" for r in 'ABC' for i in range(7) if o[r][i] != V[r][i]]
print(R, nh, json.dumps(keep), flush=True)
if 'D' in o:
    print(L.draw(o), flush=True)
