"""Exact computational-basis proof of batched dirty-bus CX synthesis.

All gates are permutations, so equality on all basis vectors proves equality
on arbitrary superpositions and states entangled with external references.
The middle qubit can be a retained data qubit or another live resource qubit.
"""
from itertools import product
from pathlib import Path
import json

def evolve(bits, gates):
 b=list(bits)
 for c,t in gates:b[t]^=b[c]
 return tuple(b)

out=[]
for k,l in [(1,2),(1,3),(2,2)]:
 n=k+l+1;h=k+l
 controls=list(range(k));targets=list(range(k,k+l))
 ref=[(a,b) for a in controls for b in targets]
 batched=[(a,h) for a in controls]+[(h,b) for b in targets]+[(a,h) for a in controls]+[(h,b) for b in targets]
 independent=sum(([(a,h),(h,b),(a,h),(h,b)] for a,b in ref),[])
 for bits in product(range(2),repeat=n):
  assert evolve(bits,batched)==evolve(bits,ref)
  assert evolve(bits,independent)==evolve(bits,ref)
  assert evolve(bits,batched)[h]==bits[h]
 out.append(dict(k=k,l=l,qubits=n,remote_CXs=k*l,independent_bridge_CXs=len(independent),batched_CXs=len(batched),saved_CXs=len(independent)-len(batched),basis_vectors_verified=2**n,gates=batched))
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
