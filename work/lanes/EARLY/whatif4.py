import sys, json
sys.path.insert(0, '.')
import layout as L
for A_LEN, BC_LATE, NLATE in [(5, 4, 4), (4, 4, 4), (5, 3, 3), (4, 3, 3), (4, 4, 7), (3, 4, 4)]:
    o = L.solve(A_LEN=A_LEN, BC_LEN=12, BC_LATE=BC_LATE, NLATE=NLATE, MAXH=3)
    print(A_LEN, BC_LATE, NLATE, o.get('status'), o.get('R'), o.get('hops'), o.get('D'), o.get('late'), o.get('arrival'), flush=True)
    if 'D' in o: print(L.draw(o))
