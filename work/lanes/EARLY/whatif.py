import sys, json
sys.path.insert(0, '.')
import layout as L
scen = {
 'base': {},
 'q14_32': {14: 32},
 'blue_34': {1: 34, 2: 34},
 'q14_32_blue_34': {14: 32, 1: 34, 2: 34},
 'all_anc_30': {c: min(v, 30) for c, v in L.REL.items() if 0 < v < 99},
}
for A_LEN in (5, 4):
    for name, upd in scen.items():
        saved = dict(L.REL)
        L.REL.update(upd)
        o = L.solve(A_LEN=A_LEN, BC_LEN=12, BC_LATE=6, NLATE=4, MAXH=3)
        L.REL.clear(); L.REL.update(saved)
        print(A_LEN, name, o.get('status'), o.get('R'), o.get('hops'), o.get('D'), flush=True)
