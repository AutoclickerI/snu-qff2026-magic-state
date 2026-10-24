"""Fewest-hop layouts at fixed R (calibrated A_LEN 4, BC 12/6/4, CROSS). usage: r43.py R"""
import sys, json
sys.path.insert(0, '.')
import layout as L
L.CROSS = True
R = int(sys.argv[1])
o = L.solve(A_LEN=4, BC_LEN=12, BC_LATE=6, NLATE=4, MAXH=3, fixR=R)
print(R, json.dumps({k: o.get(k) for k in ('status', 'R', 'hops', 'paths', 'A', 'B', 'C', 'late', 'flag', 'arrival')}), flush=True)
if 'D' in o:
    print(L.draw(o), flush=True)
