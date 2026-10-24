"""Insert ops into a base stem: addops.py <base> <out> t:"line" ... (checks qubit conflicts per tick)."""
import sys, shutil, re
sys.path.insert(0, '.')
from qedit import load
base, out = sys.argv[1], sys.argv[2]
c = load(base)
for a in sys.argv[3:]:
    t, ln = a.split(':', 1)
    c.segs[int(t)].append(ln.split('|'))
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
