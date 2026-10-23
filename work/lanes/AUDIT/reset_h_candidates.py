import sys, glob
sys.path.insert(0, '/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
import tprep
from pathlib import Path

for p in glob.glob('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/low_*.qasm'):
    c=Path(p).read_text(); seen=set(); out=[]
    for line in c.splitlines():
        if line.startswith('h q['):
            q=int(line.split('[')[1].split(']')[0])
            if q not in seen:
                out.append(f'reset q[{q}];'); seen.add(q)
        out.append(line)
    cc='\n'.join(out)+'\n'; mp=Path(p.replace('.qasm','.meta'))
    if not mp.exists(): continue
    D=eval(mp.read_text()); r=tprep.check(cc,D,p=1e-3,shots=200000,seed=0)
    print(p,r.score,r.acceptance,r.passed)
    Path(p.replace('.qasm','_rh.qasm')).write_text(cc)
