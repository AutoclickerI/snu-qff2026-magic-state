"""Exact verification of a partial moving Steane-check instrument.

CX(D,A); measure Z(A), keeping D, is exactly the same Kraus map as
CX(A,D); CX(D,A); measure Z(D), keeping A, after relabelling the output.
The ancilla may be entangled with other ancillas. No fresh-target assumption
or measurement-dependent physical correction is used.
"""
import json
from itertools import product
from pathlib import Path

def apply(bits,gates):
 b=list(bits)
 for c,t in gates:b[t]^=b[c]
 return b

def kraus(gates,read,keep,m):
 matrix=[[0]*4 for _ in range(2)]
 for d,a in product(range(2),repeat=2):
  bits=apply((d,a),gates)
  if bits[read]==m:matrix[bits[keep]][2*d+a]=1
 return matrix

old=[(0,1)]
new=[(1,0),(0,1)]
rows=[]
for m in [0,1]:
 k1=kraus(old,read=1,keep=0,m=m)
 k2=kraus(new,read=0,keep=1,m=m)
 assert k1==k2
 rows.append(k1)

# Verify full seven-pair unitary/readout map for every one of 128 masks and
# every computational basis input on the 14 pair legs. Equality for arbitrary
# superpositions, and external entanglement, follows because all phases are +1.
checked=0
for mask in range(128):
 for d in range(128):
  for a in range(128):
   outputs=records=0
   for i in range(7):
    b=apply(((d>>i)&1,(a>>i)&1),new if mask>>i&1 else old)
    read,keep=(0,1) if mask>>i&1 else (1,0)
    outputs|=b[keep]<<i;records|=b[read]<<i
   assert outputs==d and records==d^a
   checked+=1

result=dict(local_Kraus_matrices=rows,local_exact=True,all_partial_masks=128,
 full_basis_cases=checked,naive_check_then_swap_CX=4,fused_CX=2,
 added_CX_relative_to_stationary_check=1,
 noise_score_claim='None: the changed gate-noise propagation requires full-circuit pricing.')
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
