"""An already encoded, locally mixed flag can record an A phase fault.

This verifies ideal algebra only. Current v30f's two available A--resource
edges have scheduling conflicts; no full grid implementation is claimed.
"""
import json
from pathlib import Path
import numpy as np
def cx(c,t):
    U=np.zeros((16,16),complex)
    for x in range(16):U[x^(((x>>c)&1)<<t),x]=1
    return U
def pauli(x,z):
    P=np.zeros((16,16),complex)
    for i in range(16):P[i^x,i]=(-1)**((i&z).bit_count()%2)
    return P
# f=0 is one member of an existing encoded resource; b=1 another member.
# a=2 is watched A wire; u=3 is its local encoder control.
F=cx(0,2);U=cx(3,2);Za=pauli(0,1<<2);Zf=pauli(0,1<<0)
S=pauli((1<<0)|(1<<1),0)
assert np.array_equal(F@U@F,U)
assert np.array_equal(F@Za@U@F,Zf@Za@U)
assert np.array_equal(S@Zf,-Zf@S)
# Existing Bell parity has a maximally mixed single f: measuring f alone is
# random, but its already available parity with b deterministically sees Zf.
psi=np.zeros(16,complex);psi[0]=psi[3]=1/np.sqrt(2)
assert abs(np.vdot(psi,S@psi)-1)<1e-14
assert abs(np.vdot(psi,Zf@S@Zf@psi)+1)<1e-14
out=dict(scope=__doc__,ideal_unitary_max_error=float(np.max(np.abs(F@U@F-U))),
    fault_transport_max_error=float(np.max(np.abs(F@Za@U@F-Zf@Za@U))),
    flag_observable='Existing X_f X_b parity, not individual X_f',
    requirement='Propagate the flag operator through the concurrent B/C encoder and close its echo exactly; account for all noisy flag CXs.',
    available_L5_edges=[[13,14],[17,16]],
    distinction='Old external flags borrowed resource cells before preparation; this uses encoded resource syndrome information after/during preparation.',
    measured_physical_gain=False)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
