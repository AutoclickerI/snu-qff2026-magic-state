"""Exact noiseless certificates for two instrument-level synthesis freedoms.

These certify ideal identities only. They do not claim a finite-noise improvement.
1. Clean parity bus: replace coherent uncomputation by an X measurement.
2. Encoded Bell BC endpoint: allow a measured logical branch and use FRAME_X.
"""
import itertools,json
from pathlib import Path
import numpy as np

def bus_certificate(k,l):
    # Little-endian bits: k controls, l targets, last bit is the helper.
    n=k+l;d=1<<n;h=n
    branches=[]
    for m in range(2):
        K=np.zeros((d,d))
        U=np.zeros((d,d))
        for a in range(d):
            actual=a # helper input is zero
            for c,t in [(j,h)for j in range(k)]+[(h,j)for j in range(k,k+l)]:
                if (actual>>c)&1:actual^=1<<t
            K[actual&(d-1),a]=(-1)**(m*((actual>>h)&1))/np.sqrt(2)
            parity=sum((a>>j)&1 for j in range(k))%2
            b=a
            for c,t in itertools.product(range(k),range(k,k+l)):
                if (b>>c)&1:b^=1<<t
            U[b,a]=(-1)**(m*parity)/np.sqrt(2)
        branches.append(float(np.max(np.abs(K-U))))
    return dict(controls=k,targets=l,
                coherent_CX=2*k+l,measured_CX=k+l,
                branch_identity_max_error=branches,
                byproduct='Z on every control iff helper MX outcome is 1')

rows=[0b1010101,0b1100110,0b1111000]
S={0}
for r in rows:S|={x^r for x in tuple(S)}
assert len(S)==8
v0=np.zeros(128);v1=np.zeros(128)
for x in S:v0[x]=1/np.sqrt(8);v1[x^127]=1/np.sqrt(8)
bell=(np.outer(v0,v0)+np.outer(v1,v1))/np.sqrt(2)
branches=[]
for c in range(128):
    state=bell[:,c];prob=float(state@state)
    if prob<1e-14:continue
    b=c.bit_count()%2
    expected=v0 if b==0 else v1
    err=float(np.max(np.abs(state/np.sqrt(prob)-expected)))
    synd=[(c&r).bit_count()%2 for r in rows]
    assert synd==[0,0,0]
    branches.append(dict(C_result=c,C_parity=b,probability=prob,
                         conditional_B_state_error=err))
assert len(branches)==16
T=np.array([1,np.exp(1j*np.pi/4)])/np.sqrt(2)
X=np.array([[0,1],[1,0]])
frame_errors=[]
for b in (0,1):
    out=np.linalg.matrix_power(X,b)@np.linalg.matrix_power(X,b)@T
    frame_errors.append(float(np.max(np.abs(out-T))))
# A logical X fault on C changes the inferred branch but not B's actual branch.
# It passes the three C syndromes and gives an incorrect logical X frame.
C_logical_X_hazard=float(1-abs(np.vdot(T,X@T))**2)

out=dict(scope=__doc__,clean_bus=[bus_certificate(k,l)for k,l in [(1,1),(2,1),(2,2),(3,1)]],
         encoded_BC=dict(accepted_noiseless_probability=sum(x['probability']for x in branches),
                         branches=branches,FRAME_X_correction_errors=frame_errors,
                         uncorrelated_C_logical_X_fault_loss=C_logical_X_hazard,
                         conclusion='Joint synthesis must verify branch agreement; dropping a parity detector alone is unsafe.'))
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
