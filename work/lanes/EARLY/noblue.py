"""v36c with the blue XZ check removed (q1 reset at 37 as A0's init)."""
import sys, shutil
sys.path.insert(0, '.')
from qedit import load
c = load('../MAIN/v36c')
drop = {(28, 'reset q[1];'), (28, 'reset q[2];'), (29, 'cx q[2],q[1];'), (30, 'cx q[3],q[2];'), (30, 'cx q[7],q[1];'),
        (31, 'cx q[8],q[2];'), (31, 'cx q[0],q[1];'), (32, 'cx q[2],q[8];'), (32, 'cx q[1],q[0];'),
        (33, 'cx q[2],q[3];'), (33, 'cx q[1],q[7];'), (34, 'cx q[2],q[1];'), (35, 'h q[2];')}
for t in range(28, 36):
    c.segs[t] = [g for g in c.segs[t] if (t, g[0]) not in drop]
c.segs[37] = [['reset q[1];'] if g[0] == 'measure q[1] -> c[64];' else g for g in c.segs[37]]
c.dets = [d for d in c.dets if d.strip() not in ('// DETECTOR c[64]', '// DETECTOR c[67]')]
open('cand/noblue.qasm', 'w').write(c.text())
shutil.copy('../MAIN/v36c.json', 'cand/noblue.json')
