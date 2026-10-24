"""Exact small witness for measuring only safe parity-register combinations.

Three parity ancillas store u=x0+x1, v=x0+x2, w=x0+x1+x2.
After arbitrary diagonal phase gates, CX(u,v), CX(u,w) makes v=x1+x2,
w=x2. Erase u coherently with two CXs, and X-measure v,w. The only
byproducts are Z1Z2 and Z2, avoiding the dangerous Z0 syndrome direction.
"""
import json
from pathlib import Path
import numpy as np

L=[0b011,0b101,0b111]
angles=[np.pi/4,-np.pi/4,np.pi/4]
phase=np.array([np.exp(1j*sum(a*((r&x).bit_count()%2) for r,a in zip(L,angles))) for x in range(8)])
maxerr=0.
branch_probs=[]
rng=np.random.default_rng(20261024)
psi=rng.normal(size=8)+1j*rng.normal(size=8);psi/=np.linalg.norm(psi)
for m in range(4):
 K=np.zeros((8,8),complex)
 for x in range(8):
  u,v,w=[(r&x).bit_count()%2 for r in L]
  v^=u;w^=u
  u^=((x>>0)&1)^((x>>1)&1)
  assert u==0
  K[x,x]=phase[x]*(-1)**(((m&1)*v)^(((m>>1)&1)*w))/2
 correction=(0b110 if m&1 else 0)^(0b100 if m&2 else 0)
 assert correction&0b001==0
 corrected=np.diag([(-1)**((correction&x).bit_count()%2) for x in range(8)])@K
 maxerr=max(maxerr,float(np.max(np.abs(corrected-np.diag(phase)/2))))
 branch_probs.append(float(np.linalg.norm(K@psi)**2))
result=dict(parity_rows=L,new_safe_rows=[6,4],remaining_coherent_row=3,
 old_reverse_CX=sum(r.bit_count() for r in L),new_ancilla_basis_CX=2,
 remaining_uncompute_CX=2,measured_ancillas=2,saved_CX=3,
 corrected_Kraus_operator_max_error=maxerr,branch_probabilities=branch_probs,
 scope='Exact ideal instrument and CX count, not a noisy performance result or a current-v29 rewrite.',
 rank_caution='k-r safe register combinations include redundancy when rank(L)<k; quotient by row dependencies before claiming independent freedoms.')
assert maxerr<1e-14
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
