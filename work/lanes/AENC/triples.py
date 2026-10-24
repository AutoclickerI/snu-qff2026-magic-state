"""Pauli-level 2nd/3rd-order loss of a deterministic boundary class: rest faults f (and f,g) with all detectors silent.
Logical cost from e bits: Z-type = bit6 ^ any(bits0-2) (cost 1), X-type = bit7 ^ any(bits3-5) (cost 1/2); s != 0 flagged."""
import sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bmodel
from bmodel import rep
ext = bmodel.Exterior('/home/jihoon/competitions/quantumn/work/lanes/MAIN/v36c')
groups = ext.rest_groups()
faults = []
for ch, fs in groups.items():
    md = ext.meta[ch]
    for f in fs:
        faults.append((f['d'], f['e'], f['s'], f['p'], ch, f['pauli'], md))
byd = defaultdict(list)
for i, x in enumerate(faults):
    byd[x[0]].append(i)

def cost(e, s):
    z = ((e >> 6) & 1) ^ (1 if e & 7 else 0)
    x = ((e >> 7) & 1) ^ (1 if (e >> 3) & 7 else 0)
    return z * 1.0 + x * 0.5 + (0.0 if not s else 0.0), bool(s)

def lab(i):
    d, e, s, p, ch, pa, md = faults[i]
    return f"{md['kind']} {md['op']} {md['qs']} t{md['t0']} {pa}"

for c in map(int, sys.argv[1:]):
    d0, s0, e0 = ext.sig_of(*rep(c))
    second = 0.; s2 = defaultdict(float); third = 0.; t3 = defaultdict(float); sflag = 0.
    for i in byd.get(d0, []):
        d, e, s, p, *_ = faults[i]
        cst, sf = cost(e ^ e0, s ^ s0)
        second += p * cst
        if cst: s2[lab(i)] += p * cst
    for i, (d, e, s, p, ch, pa, md) in enumerate(faults):
        want = d ^ d0
        for j in byd.get(want, []):
            if j <= i: continue
            if faults[j][4] == ch: continue
            d2, e2, s2_, p2, *_ = faults[j]
            cst, sf = cost(e ^ e2 ^ e0, s ^ s2_ ^ s0)
            if cst:
                third += p * p2 * cst
                t3[(lab(i), lab(j))] += p * p2 * cst
    print(f'class {c}: 2nd {second:.3e}  3rd {third:.3e}')
    for k, v in sorted(s2.items(), key=lambda x: -x[1])[:6]: print(f'   2: {v:.2e} {k}')
    agg = defaultdict(float)
    for (a, b), v in t3.items():
        agg[a.split(' t')[0] + ' | ' + b.split(' t')[0]] += v
    for k, v in sorted(agg.items(), key=lambda x: -x[1])[:12]: print(f'   3: {v:.2e} {k}')
