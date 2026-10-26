"""Independent perfect-boundary Pauli enumeration for the interaction proposal regression."""
from pass4 import *
from signature4 import strength

def loss(errors):
 x=z=0
 for q,p in errors:
  if p in 'XY':x^=1<<q
  if p in 'YZ':z^=1<<q
 def decode(v):
  syn=0
  for q in range(7):
   if v>>q&1:syn^=q+1
  if syn:v^=1<<(syn-1)
  return v.bit_count()%2
 a,b=decode(x),decode(z)
 return 0.0 if (a,b)==(0,0)else 1.0 if (a,b)==(0,1)else .5

single=[loss([(q,p)])for q in [0,1]for p in 'XYZ'];pair={(a+b):loss([(0,a),(1,b)])for a,b in itertools.product('XYZ',repeat=2)}
assert single==[0.0]*6 and sum(pair.values())==5.0
# Physically disjoint output signatures must remain eligible for a coupled proposal.
link=strength(dict(detectors=[],rotation=0,output=1),dict(detectors=[],rotation=0,output=2));assert link>0
out=dict(scope='perfect Steane boundary diagnostic, not a complete circuit price',singleton_losses=single,pair_losses=pair,coefficient=sum(pair.values())/9,independent_decoder_coupling_detected=True)
dump(R/'decoder_interaction_regression.json',out);print(json.dumps(out))
