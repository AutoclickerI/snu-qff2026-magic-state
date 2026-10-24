"""Exact local effective-Pauli noise identity for the measured verification bus.

After folding helper MX into B MX, compare one direct B->C check to
B->h; h->C; MX(h), with B->data between the check legs.
Tuple bits are (X on data, B MX flip, C MZ flip). Phases are immaterial.
This only establishes noise equivalence; it does not imply a score gain.
"""
from fractions import Fraction as F
from collections import defaultdict
from itertools import product
import json
from pathlib import Path
p=F(1,1000)
paulis=[(0,0),(1,0),(0,1),(1,1)]
direct=defaultdict(F);first_bus=defaultdict(F);extra_gate=defaultdict(F)
for (xb,zb),(xc,zc) in product(paulis,repeat=2):
    w=1-p if not(xb or zb or xc or zc)else p/15
    direct[xb,zb,xc]+=w
    # Relabel second qubit h; its Z changes helper MX and hence B's readout.
    first_bus[xb,zb^zc,xc]+=w
    # For the second CX noise, the qubits are h,C.
    extra_gate[zb,xc]+=w
assert direct==first_bus

def convolve(a,b):
    c=defaultdict(F)
    for x,px in a.items():
        for y,py in b.items():c[tuple(i^j for i,j in zip(x,y))]+=px*py
    return c
prep={(0,0):1-p,(0,1):p}   # R(h) X error becomes a C readout flip
read={(0,0):1-p,(1,0):p}   # MX(h) error becomes a B readout flip
extra=convolve(convolve(extra_gate,prep),read)
out=dict(scope=__doc__,p=float(p),first_gate_matches_direct_exactly=direct==first_bus,
         extra_classical_BC_flip_distribution={str(k):dict(exact=str(v),probability=float(v))for k,v in sorted(extra.items())},
         extra_first_order_nonidentity_mass_per_pair='14p/5',
         extra_first_order_rejection_mass_seven_pairs='98p/5 = 0.0196 at p=0.001')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
