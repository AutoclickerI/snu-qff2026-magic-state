"""Second-order partners of a boundary class: rest faults f with d(f) ^ d(class) == 0 (accepted at 2nd order)."""
import sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmodel
from bmodel import rep
ext = bmodel.Exterior('/home/jihoon/competitions/quantumn/work/lanes/MAIN/v36c')
groups = ext.rest_groups()
labels = ext.m.labels
for c in map(int, sys.argv[1:]):
    d0, s0, e0 = ext.sig_of(*rep(c))
    hits = defaultdict(float)
    tot = 0.
    for ch, fs in groups.items():
        for f in fs:
            if f['d'] == d0:
                md = ext.meta[ch]
                hits[(md['kind'], md['op'], md['qs'], md['t0'], f['pauli'], f['e'] ^ e0, f['s'] ^ s0)] += f['p']
                tot += f['p']
    print(f'class {c}: total accepted-partner prob {tot:.3e}')
    for k, v in sorted(hits.items(), key=lambda x: -x[1])[:14]:
        print(f'   {v:.2e} {k}')
