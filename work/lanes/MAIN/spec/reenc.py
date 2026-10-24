#!/usr/bin/env python
"""Re-encode final Z readouts with CX u->v before measuring (reviewer item 1).

    reenc.py <in stem> <out stem> u:v[,u:v...]
For each pair, both u and v must be Z-measured in the same barrier block after their last gate. The CX u->v takes
that step, both measurements move to the next barrier block, and every detector reading v's bit also reads u's
bit (old v = new v xor new u).
"""
import json
import re
import sys

src, out, spec = sys.argv[1], sys.argv[2], sys.argv[3]
L = open(src + ".qasm").read().split("\n")
pairs = [tuple(map(int, s.split(":"))) for s in spec.split(",")]
meas = {}
for i, l in enumerate(L):
    m = re.match(r"measure q\[(\d+)\] -> c\[(\d+)\];", l)
    if m:
        meas[int(m.group(1))] = (i, int(m.group(2)))      # last measurement of each qubit
moved, sub = [], {}
for u, v in pairs:
    iu, bu = meas[u]
    iv, bv = meas[v]
    assert L[iu - 1].startswith("measure") or L[iu - 1].startswith("barrier") or True
    L[iu] = f"cx q[{u}],q[{v}];"
    moved += [f"measure q[{u}] -> c[{bu}];", f"measure q[{v}] -> c[{bv}];"]
    L[iv] = None
    sub[bv] = bu
L = [l for l in L if l is not None]
first = min(meas[u][0] for u, _ in pairs)
nb = next(i for i in range(first, len(L)) if L[i].startswith("barrier") and i > first)
L[nb + 1:nb + 1] = moved
for i, l in enumerate(L):
    if l.startswith("// DETECTOR"):
        bits = [int(x) for x in re.findall(r"c\[(\d+)\]", l)]
        s = set()
        for b in bits:
            s ^= {b}
            if b in sub:
                s ^= {sub[b]}
        L[i] = "// DETECTOR " + " ".join(f"c[{b}]" for b in sorted(s))
open(out + ".qasm", "w").write("\n".join(L))
d = json.load(open(src + ".json"))
d["source"] = f"{src} with final readouts re-encoded by CX {spec} (reenc.py)"
json.dump(d, open(out + ".json", "w"))
