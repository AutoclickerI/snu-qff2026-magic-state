"""Remove ops (tick, first line) and detectors from a base stem. usage: rmgadget.py <base> <out> <spec.json>
spec: {"ops": [[t, "line"], ...], "dets": ["c[279]", ...], "replace": [[t, "old first line", ["new","lines"]], ...]}"""
import sys, json, shutil
sys.path.insert(0, '.')
from qedit import load
base, out, spec = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
c = load(base)
for t, ln in spec.get('ops', []):
    n0 = len(c.segs[t])
    c.segs[t] = [g for g in c.segs[t] if g[0] != ln and not (len(g) > 1 and g[1] == ln)]
    assert len(c.segs[t]) == n0 - 1, (t, ln)
for t, old, new in spec.get('replace', []):
    hit = [j for j, g in enumerate(c.segs[t]) if g[0] == old or (len(g) > 1 and g[1] == old)]
    assert len(hit) == 1, (t, old)
    c.segs[t][hit[0]] = new
drop = {f'// DETECTOR {d}' for d in spec.get('dets', [])}
n0 = len(c.dets)
c.dets = [d for d in c.dets if d.strip() not in drop]
assert len(c.dets) == n0 - len(drop), spec.get('dets')
open(out + '.qasm', 'w').write(c.text())
shutil.copy(base + '.json', out + '.json')
