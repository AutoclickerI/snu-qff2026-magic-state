"""Which side binds R43 for v36c? Pin v36c's B,C (A, paths free) and v36c's A (B, C, paths free); CROSS on, A_LEN 4."""
import sys, json
sys.path.insert(0, '.')
import layout as L
L.CROSS = True
V = dict(A=[1, 14, 8, 9, 2, 16, 15], B=[6, 26, 13, 11, 4, 23, 27], C=[12, 25, 19, 17, 5, 29, 28])
for name, pin in [('pinBC', dict(B=V['B'], C=V['C'])), ('pinA', dict(A=V['A'])),
                  ('pinBC_flagfree', dict(B=V['B'], C=V['C']))]:
    L.PIN.clear(); L.PIN.update(pin)
    o = L.solve(A_LEN=4, BC_LEN=12, BC_LATE=6, NLATE=4, MAXH=3, flag=(name != 'pinBC_flagfree'))
    print(name, json.dumps({k: o.get(k) for k in ('status', 'R', 'hops', 'paths', 'A', 'late', 'flag', 'arrival')}), flush=True)
    if 'D' in o:
        print(L.draw(o), flush=True)
