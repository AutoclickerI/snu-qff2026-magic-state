import sys, json
sys.path.insert(0, '.')
import layout as L
base = dict(L.REL)
for A_LEN, BC_LEN, BC_LATE, NLATE, anc30 in [(4, 12, 6, 7, False), (4, 12, 6, 14, False), (4, 12, 6, 7, True), (4, 12, 4, 7, True), (3, 12, 6, 7, False)]:
    L.REL.clear(); L.REL.update(base)
    if anc30:
        L.REL.update({c: min(v, 30) for c, v in base.items() if 0 < v < 99})
    o = L.solve(A_LEN=A_LEN, BC_LEN=BC_LEN, BC_LATE=BC_LATE, NLATE=NLATE, MAXH=3)
    print(A_LEN, BC_LEN, BC_LATE, NLATE, anc30, o.get('status'), o.get('R'), o.get('hops'), o.get('D'), o.get('late'), flush=True)
    if 'D' in o: print(L.draw(o))
