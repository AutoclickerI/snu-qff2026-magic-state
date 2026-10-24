import sys, json
sys.path.insert(0, '.')
import layout as L
baseR, baseD = dict(L.REL), dict(L.READY)
for A_LEN, BC_LATE, NLATE, anc30, early in [(4, 6, 7, False, True), (4, 6, 7, True, True), (5, 6, 7, True, True), (4, 5, 7, True, True)]:
    L.REL.clear(); L.REL.update(baseR); L.READY.clear(); L.READY.update(baseD)
    if anc30:
        L.REL.update({c: min(v, 30) for c, v in baseR.items() if 0 < v < 99 and c not in (1, 2)})
    if early:
        L.READY.update({1: 30, 3: 30, 5: 30})
    o = L.solve(A_LEN=A_LEN, BC_LEN=12, BC_LATE=BC_LATE, NLATE=NLATE, MAXH=3)
    print(A_LEN, BC_LATE, NLATE, anc30, early, o.get('status'), o.get('R'), o.get('hops'), o.get('D'), o.get('late'), o.get('arrival'), flush=True)
    if 'D' in o: print(L.draw(o))
