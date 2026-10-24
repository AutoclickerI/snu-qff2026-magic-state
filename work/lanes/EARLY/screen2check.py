"""Optimistic screen: a second blue-type XZ plaquette check during the data wait, on phantom (non-grid) ancillas.
usage: screen2check.py <out> <s> <a1> <a2> <first1> <second1> <first2> <second2> [tmoves q:t ...]
Data CX on a1-side pair at s+2 (first), s+3 (second), s+4 (second), s+5 (first); same for a2.
"""
import sys, shutil
sys.path.insert(0, '.')
from qedit import load
args = sys.argv[1:]
out, s, a1, a2, f1, s1, f2, s2 = args[0], *map(int, args[1:8])
moves = [tuple(map(int, m.split(':'))) for m in args[8:]]
import os
c = load(os.environ.get("BASE", "v36c"))
for q, t2 in moves:
    (t, j), = c.find(lambda g: g[0] == f"tdg q[{q}];")
    c.move(t, j, t2)
def put(t, line):
    for ln in ([line] if isinstance(line, str) else [line]):
        pass
    c.segs[t].append(line if isinstance(line, list) else [line])
b1, b2 = c.max_creg() + 1, c.max_creg() + 2
c.header = [h if not h.startswith('creg') else f'creg c[{b2 + 1}];' for h in c.header]
put(s, f'reset q[{a1}];'); put(s, [f'reset q[{a2}];', f'h q[{a2}];'])
put(s + 1, f'cx q[{a2}],q[{a1}];')
put(s + 2, f'cx q[{f1}],q[{a1}];'); put(s + 2, f'cx q[{f2}],q[{a2}];')
put(s + 3, f'cx q[{s1}],q[{a1}];'); put(s + 3, f'cx q[{s2}],q[{a2}];')
put(s + 4, f'cx q[{a1}],q[{s1}];'); put(s + 4, f'cx q[{a2}],q[{s2}];')
put(s + 5, f'cx q[{a1}],q[{f1}];'); put(s + 5, f'cx q[{a2}],q[{f2}];')
put(s + 6, f'cx q[{a2}],q[{a1}];')
put(s + 7, [f'h q[{a2}];', f'measure q[{a2}] -> c[{b1}];']); put(s + 7, f'measure q[{a1}] -> c[{b2}];')
# conflict check
for t in range(len(c.segs)):
    seen = {}
    import re
    for g in c.segs[t]:
        qs = set(map(int, re.findall(r'q\[(\d+)\]', g[0] if not g[0].startswith('h ') or len(g) == 1 else g[1])))
        for ln in g:
            qs |= set(map(int, re.findall(r'q\[(\d+)\]', ln)))
        for q in qs:
            assert q not in seen, (t, q, g, seen[q])
            seen[q] = g
c.dets += [f'// DETECTOR c[{b1}]', f'// DETECTOR c[{b2}]']
open(out + '.qasm', 'w').write(c.text())
shutil.copy(os.environ.get('BASE', '../MAIN/v36c') + '.json', out + '.json')
