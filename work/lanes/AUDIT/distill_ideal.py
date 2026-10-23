import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
SUP=((2,3,4),(1,3,4),(1,2,4),(1,2,3),(0,3,4),(0,2,4),(0,2,3),(0,1,4),(0,1,3),(0,1,2),(0,1,2,3,4))
q=QuantumCircuit(5)
for i in range(4):q.h(i);q.t(i)
q.h(4)
for S in SUP:
 pivot=S[-1]
 for i in S[:-1]:q.cx(i,pivot)
 q.t(pivot)
 for i in reversed(S[:-1]):q.cx(i,pivot)
q.s(4)
for i in range(4):q.h(i)
sv=Statevector.from_instruction(q)
# project first four X outcomes 0
arr=sv.data.reshape([2]*5)
# qiskit little endian; index bits q0...
# inspect amplitudes output q4 after first bits 0 in X basis via explicit state vector and H before measure
qm=QuantumCircuit(5); # easier q with H included, measuring first 4 Z
qm.compose(q,inplace=True);# q currently H before output? append H on first4 already
# projection amplitude after H readout state: q has H and then state
sv2=Statevector.from_instruction(qm)
# output state conditioned bits q0..3=0, sum amplitudes
vec=np.array([sv2.data[(b<<4)] for b in [0,1]]) # wrong bits q0-3 zero means index bit4 only
print('norm',np.linalg.norm(vec),vec/np.linalg.norm(vec),'target',np.array([1,np.exp(1j*np.pi/4)])/np.sqrt(2))
# simulate measurement directly by projecting original final before readout and X basis overlaps
