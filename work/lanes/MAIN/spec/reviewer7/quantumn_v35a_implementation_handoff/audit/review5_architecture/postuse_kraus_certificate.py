"""Exact finite certificate for the noiseless full post-use A/B instrument.
Binary phase-ignored Pauli stabilizers and dyadic Kraus matrices suffice.
"""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
ROWS=[sum(1<<i for i in row)for row in[(0,2,4,6),(1,2,5,6),(3,4,5,6)]]
S={0}
for row in ROWS:S|={s^row for s in list(S)}
C={x for x in range(128)if all((x&r).bit_count()%2==0 for r in ROWS)}
assert len(S)==8 and len(C)==16 and S<=C
# <+L|X^x|+L>: support intersection count divided by16.
KA=[sum((a^x)in C for a in C)//16 for x in range(128)]
assert all(v==int(x in C)for x,v in enumerate(KA))
# 8*K_B[x,y] = 1[x XOR y in S]. This is the exact X-stabilizer projector.
KB8=[[int((x^y)in S)for y in range(128)]for x in range(128)]
# Exact integer projector and commutation tests; trace of joint projector=2.
assert all(sum(KB8[x][z]*KB8[z][y]for z in range(128))==8*KB8[x][y]for x in range(128)for y in range(128))
assert all(KA[x]*KB8[x][y]==KB8[x][y]*KA[y]for x in range(128)for y in range(128))
assert sum(KA[x]*KB8[x][x]for x in range(128))==16
# Undetectable ancilla-preparation Paulis have only harmless propagated parts.
counts={}
for kind in ['Aplus','Bzero']:
 accepted=bad=0
 for x in range(128):
  for z in range(128):
   ok=(x in C and z in S)if kind=='Aplus'else(x in S and z in C)
   if ok:
    accepted+=1
    harmless=z in S if kind=='Aplus'else x in S
    bad+=not harmless
 counts[kind]=dict(paulis_checked=16384,undetectable_phase_ignored_paulis=accepted,harmful_propagated_parts=bad)
r=dict(scope=__doc__,S=sorted(S),C=sorted(C),kraus_A='diagonal 1[x in C] = P_Z',kraus_B='(1/8) sum_{s in S} X^s = P_X',joint_projector_rank=2,arbitrary_logical_input_unchanged=True,undetectable_preparation_fault_propagation=counts,limitation='Exact ideal instrument and prep-Pauli certificate. Full circuit has separate numerical single-fault and all-orders receipts; noisy decoder masking can still yield large second-order loss.')
(HERE/'postuse_kraus_certificate.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
