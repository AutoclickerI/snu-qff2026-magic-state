"""Dense independent channel/instrument identities, tested on a tomographic operator basis."""
import itertools,json
from fractions import Fraction as F
from pathlib import Path
import numpy as np

OUT=Path(__file__).resolve().parent
I=np.eye(2);X=np.array([[0,1],[1,0]]);Y=np.array([[0,-1j],[1j,0]]);Z=np.diag([1,-1]);P=[I,X,Y,Z]
CX=np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
SW=np.eye(4)[[0,2,1,3]]
p=F(1,1000);q=2*p/5;r=4*p/15
def conj(u,a):return u@a@u.conj().T
def d1(a,rate,wire=0):
    qs=[np.kron(pa,I) if wire==0 else np.kron(I,pa) for pa in P]
    return (1-float(rate))*a+sum(conj(pa,a) for pa in qs[1:])*float(rate)/3
def d2(a):return (1-float(p))*a+sum(conj(np.kron(a1,a2),a) for a1,a2 in itertools.product(P,P) if not (a1 is I and a2 is I))*float(p)/15
def traced(a):return np.einsum('ikjk->ij',a.reshape(2,2,2,2))
def dep(a,rate):return (1-float(rate))*a+float(rate)/3*sum(conj(pa,a) for pa in P[1:])
def flip(a,rate,axis):return (1-float(rate))*a+float(rate)*conj(P[axis],a)
def branch(a,basis,bit):
    v=np.eye(2)[:,bit] if basis=='Z' else np.array([1,(-1)**bit])/np.sqrt(2)
    k=np.kron(np.eye(2),v.reshape(1,2));return k@a@k.conj().T
def main():
    basis=[]
    for i,j in itertools.product(range(4),repeat=2):
        a=np.zeros((4,4),complex);a[i,j]=1;basis.append(a)
    errors={};count={}
    def test(name,actual,expected):
        e=float(np.max(np.abs(actual-expected)));errors[name]=max(errors.get(name,0),e);count[name]=count.get(name,0)+1
    q0=(2*p/5)/(1-8*p/15);w0=1-8*p/15;w1=8*p/15
    for a in basis:
        for U in (CX,SW@CX@SW):
            test('D2_through_own_CX',conj(U,d2(a)),d2(conj(U,a)))
            test('traced_D2',traced(d2(a)),dep(traced(a),4*p/5))
            # Data-only arbitrary depolarization commutes through CX after helper trace.
            test('output_D1_through_CX',traced(conj(U,d1(a,q))),dep(traced(conj(U,a)),q))
            axis=3 if np.array_equal(U,CX) else 1
            test('helper_D1_projection',traced(conj(U,d1(a,q,1))),flip(traced(conj(U,a)),2*q/3,axis))
        for bas,b in itertools.product(('X','Z'),(0,1)):
            rhs=float(w0)*dep(branch(a,bas,b),q0)+float(w1)*dep(branch(a,bas,1-b),F(3,4))
            test('measured_partner_branch',branch(d2(a),bas,b),rhs)
            # Residual instrument after extraction, including arbitrary input off-diagonal operators.
            residual=float(w0)*dep(branch(a,bas,b),(q0-q)/(1-4*q/3))+float(w1)*dep(branch(a,bas,1-b),F(3,4))
            test('measured_partner_common_D1',branch(d2(a),bas,b),dep(residual,q))
    pp=(p-2*q/3)/(1-4*q/3);br=(p-r)/(1-2*r)
    for bas in (Z,X):
        state=(I+(1-2*float(p))*bas)/2
        res=(I+(1-2*float(pp))*bas)/2
        test('basis_preparation_D1',state,dep(res,q))
        for axis in (1,3):
            if np.max(np.abs(P[axis]@bas-bas@P[axis]))<1e-12:
                test('commuting_helper_preparation',state,flip(state,r,axis))
            else:
                res=(I+(1-2*float(br))*bas)/2
                test('anticommuting_helper_preparation',state,flip(res,r,axis))
    residual=[(1-5*r+5*r*r)/(1-2*r)**2,r*r/(1-2*r)**2,r*r/(1-2*r)**2,r*(1-3*r)/(1-2*r)**2]
    independent=[(1-r)**2,r*(1-r),r*(1-r),r*r]
    assert min(residual)>=0 and sum(residual)==1
    assert [sum(independent[a]*residual[a^b] for a in range(4)) for b in range(4)]==[1-3*r,r,r,r]
    assert max(errors.values())<2e-15
    out=dict(tomographic_max_errors=errors,matrix_basis_checks=count,
             opposite_axis_exact_residual=[str(x) for x in residual],q0=str(q0),
             scope='Complete two-qubit operator basis, therefore includes arbitrary entangled spectator extensions by linearity; IEEE754 identity checks plus exact rational binary factor')
    (OUT/'experiments/instrument_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
