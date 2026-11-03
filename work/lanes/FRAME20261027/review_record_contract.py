"""Independent targeted checks of REBUILD's exact affine-record quotient.

Three small QASM circuits use the official exact simulator as the oracle.
One four-amplitude matrix model stresses a nonorthogonal X basis and i phases.
"""
import importlib.util
import json
import math
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from frame_tools import f, HERE, ROOT
from tprep.qasm import to_stim
from tprep.exact import run

spec=importlib.util.spec_from_file_location('record_contract',ROOT/'work/lanes/REBUILD20261027/record_contract.py')
rc=importlib.util.module_from_spec(spec);spec.loader.exec_module(rc)

def closure(rows):
    out={0:0}
    for row in rows:
        mask=sum(1<<b for b in row['bits']);ref=row['reference']
        for a,v in list(out.items()):
            assert a^mask not in out or out[a^mask]==v^ref
            out[a^mask]=v^ref
    return out

def compare(name,m,oracle):
    result=rc.complete(m,[])
    inferred=closure(result['missing'])
    assert inferred==oracle,(name,inferred,oracle)
    result.update(name=name,checked_parities=1<<len(m.record_ps),oracle_affine_relations=oracle,passed=True)
    return result

def circuit(name,body):
    text='OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[36];\ncreg c[2];\n'+body
    ops,dets=f.parse_current(text);f.DATA=list(range(7));m=f.make_model(ops,dets)
    native,errors=to_stim(text);assert not errors,errors
    state,inv,records,_,_=run(native,36)
    oracle={}
    for mask in range(1<<len(records)):
        P=state.stim.PauliString(state.n)
        for j,w in enumerate(records):
            if mask>>j&1:P[w]='Z'
        ev=state.expectation(P,inv)
        if abs(abs(ev)-1)<1e-10:oracle[mask]=int(ev<0)
    return compare(name,m,oracle)

def coordinate_case():
    # |phi> = exp(i*pi/4 X0) exp(i*pi/8 X0 X1)|00>.
    # A=-Y0 Z1 is deterministic -1; B=X0 X1 is random; C=A B.
    rots=[(3,0,1,math.pi/8,0),(1,0,1,math.pi/4,1)]
    records={0:(1,3,-1j),1:(3,0,1),2:(2,3,-1j)}
    m=SimpleNamespace(rots=rots,record_ps=records)
    I=np.eye(2,dtype=complex);X=np.array([[0,1],[1,0]],complex)
    Y=np.array([[0,-1j],[1j,0]],complex);Z=np.diag([1,-1]).astype(complex)
    X0=np.kron(I,X);XX=np.kron(X,X)
    phi=(math.cos(math.pi/4)*np.eye(4)+1j*math.sin(math.pi/4)*X0) @ ((math.cos(math.pi/8)*np.eye(4)+1j*math.sin(math.pi/8)*XX) @ np.array([1,0,0,0],complex))
    A=-np.kron(Z,Y);B=XX;C=A@B
    oracle={}
    for mask in range(8):
        P=np.eye(4,dtype=complex)
        for j,M in enumerate([A,B,C]):
            if mask>>j&1:P=P@M
        ev=np.vdot(phi,P@phi)
        if abs(abs(ev)-1)<1e-10:oracle[mask]=int(ev.real<0)
    return compare('nonorthogonal_basis_complex_phase',m,oracle)

if __name__=='__main__':
    result=[
        circuit('bell_record_parity','reset q[0];\nh q[0];\nreset q[1];\ncx q[0],q[1];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];\n'),
        circuit('magic_repeated_x_readout','reset q[0];\nh q[0];\nt q[0];\nh q[0];\nmeasure q[0] -> c[0];\nh q[0];\nbarrier q[0];\nh q[0];\nmeasure q[0] -> c[1];\nh q[0];\n'),
        circuit('negative_reference_from_four_t','reset q[0];\nh q[0];\nt q[0];\nt q[0];\nt q[0];\nt q[0];\nh q[0];\nmeasure q[0] -> c[0];\n'),
        coordinate_case(),
    ]
    (HERE/'record_contract_review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
