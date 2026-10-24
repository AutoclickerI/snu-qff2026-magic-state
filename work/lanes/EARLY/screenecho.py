"""Optimistic screen: X-type echo checks (helper |+>, CX helper->data at t1 and t2, MX helper at t2+1) on phantom helpers.
usage: screenecho.py <base> <out> helper:data:t1:t2 ...
Helper RX at t1-1; Z errors on data in (t1, t2) flip the helper's X readout."""
import sys, shutil, re
sys.path.insert(0, '.')
from qedit import load
base, out = sys.argv[1], sys.argv[2]
c = load(base)
b = c.max_creg() + 1
specs = [tuple(map(int, s.split(':'))) for s in sys.argv[3:]]
c.header = [h if not h.startswith('creg') else f'creg c[{b + len(specs)}];' for h in c.header]
for k, (h, d, t1, t2) in enumerate(specs):
    c.segs[t1 - 1].append([f'reset q[{h}];', f'h q[{h}];'])
    c.segs[t1].append([f'cx q[{h}],q[{d}];'])
    c.segs[t2].append([f'cx q[{h}],q[{d}];'])
    c.segs[t2 + 1].append([f'h q[{h}];', f'measure q[{h}] -> c[{b + k}];'])
    c.dets.append(f'// DETECTOR c[{b + k}]')
for t in range(len(c.segs)):
    seen = set()
    for g in c.segs[t]:
        qs = set()
        for ln in g:
            qs |= set(map(int, re.findall(r'q\[(\d+)\]', ln)))
        assert not (qs & seen), (t, g)
        seen |= qs
open(out + '.qasm', 'w').write(c.text())
shutil.copy(base + '.json', out + '.json')
