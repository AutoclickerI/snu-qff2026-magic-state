"""Optimistic screen: single-type weight-4 plaquette check on one phantom ancilla during the data wait.
usage: screen1check.py <out> <kind Z|X|XZ2> <s> <anc> d1 d2 d3 d4 [tmoves q:t ...]
Z: R anc at s, CX d->anc at s+1..s+4, M at s+5.  X: RX anc at s, CX anc->d at s+1..s+4, MX at s+5.
"""
import sys, shutil, os, re
sys.path.insert(0, '.')
from qedit import load
args = sys.argv[1:]
out, kind, s, anc = args[0], args[1], int(args[2]), int(args[3])
ds = list(map(int, args[4:8]))
moves = [tuple(map(int, m.split(':'))) for m in args[8:]]
base = os.environ.get('BASE', '../MAIN/v36c')
c = load(base)
for q, t2 in moves:
    (t, j), = c.find(lambda g: g[0] == f"tdg q[{q}];")
    c.move(t, j, t2)
b = c.max_creg() + 1
c.header = [h if not h.startswith('creg') else f'creg c[{b + 1}];' for h in c.header]
if kind == 'Z':
    c.segs[s].append([f'reset q[{anc}];'])
    for k, d in enumerate(ds):
        c.segs[s + 1 + k].append([f'cx q[{d}],q[{anc}];'])
    c.segs[s + 5].append([f'measure q[{anc}] -> c[{b}];'])
else:
    c.segs[s].append([f'reset q[{anc}];', f'h q[{anc}];'])
    for k, d in enumerate(ds):
        c.segs[s + 1 + k].append([f'cx q[{anc}],q[{d}];'])
    c.segs[s + 5].append([f'h q[{anc}];', f'measure q[{anc}] -> c[{b}];'])
for t in range(len(c.segs)):
    seen = set()
    for g in c.segs[t]:
        qs = set()
        for ln in g:
            qs |= set(map(int, re.findall(r'q\[(\d+)\]', ln)))
        assert not (qs & seen), (t, g)
        seen |= qs
c.dets.append(f'// DETECTOR c[{b}]')
open(out + '.qasm', 'w').write(c.text())
shutil.copy(base + '.json', out + '.json')
