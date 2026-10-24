"""Calibrate layout.py: v36c's own end state (paths, roles) pinned must give its real R44; then free search with
sequential cell reuse (CROSS) at the calibrated parameters. usage: calib.py [A_LEN] [maxR]"""
import sys, json
sys.path.insert(0, '.')
import layout as L
from ortools.sat.python import cp_model
V36C = dict(paths={0: [0], 1: [20], 2: [7], 3: [4, 10], 4: [3], 5: [15, 16, 22], 6: [8, 9, 15, 21]},
            A=[1, 14, 8, 9, 2, 16, 15], B=[6, 26, 13, 11, 4, 23, 27], C=[12, 25, 19, 17, 5, 29, 28])
L.CROSS = True
A_LEN = int(sys.argv[1]) if len(sys.argv) > 1 else 4
# v36c pinned: analytic R bound under the same proxy rules
occ = {i: L.occupancy(i, p) for i, p in V36C['paths'].items()}
arr = {i: L.hop_times(i, p)[0] for i, p in V36C['paths'].items()}
busy = {}
for i, p in V36C['paths'].items():
    busy.update(L.hop_times(i, p)[1])
flag = {3, 6}  # v36c flag data (D3 q10, D6 q21 couple at R-1)
lb = {}
for i in range(7):
    lb[f'D{i}'] = arr[i] + (1 if i in flag else 0)
for i, c in enumerate(V36C['A']):
    lb[f'A{i}@{c}'] = max(L.REL[c] if L.REL[c] < 99 else 0, busy.get(c, 0)) + A_LEN
bc = {}
for r in 'BC':
    for i, c in enumerate(V36C[r]):
        rel = busy.get(c, L.REL[c] if L.REL[c] < 99 else 0)
        bc[f'{r}{i}@{c}'] = (rel, c in busy)
# NLATE=4 late cells with BC_LATE=6: crossed cells must be late, then the largest releases
late = {k for k, (rel, crossed) in bc.items() if crossed}
rest = sorted((k for k in bc if k not in late), key=lambda k: -bc[k][0])
late |= set(rest[:max(0, 4 - len(late))])
for k, (rel, _) in bc.items():
    lb[k] = rel + (6 if k in late else 12)
print('v36c pinned R bound', max(lb.values()), sorted(lb.items(), key=lambda kv: -kv[1])[:6], flush=True)
maxR = int(sys.argv[2]) if len(sys.argv) > 2 else None
o = L.solve(A_LEN=A_LEN, BC_LEN=12, BC_LATE=6, NLATE=4, MAXH=3, maxR=maxR)
print(json.dumps({k: o.get(k) for k in ('status', 'R', 'hops', 'paths', 'A', 'B', 'C', 'late', 'flag', 'arrival')}), flush=True)
if 'D' in o:
    print(L.draw(o))
