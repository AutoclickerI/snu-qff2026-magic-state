"""Build the Chamberland--Cross Fig. 5 error-detection preparation.
The state is prepared as the contest's |T_L>, mapped to the paper's |H_L>,
verified by one flagged logical-H measurement, then postselected on six
stabilizer syndromes (compact EC implementation), and mapped back.
"""
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import CHGate
from qiskit.transpiler import CouplingMap
import tprep, json, pathlib
N=36; nrec=8; data=list(range(7)); hm=7; flag=8; anc=list(range(9,15))
cm=CouplingMap.from_grid(6,6)
qc=QuantumCircuit(N,nrec)
# Problem's exact 7-qubit target injection/encoder.
qc.h(0); qc.t(0); qc.h(1)
for x in [(0,4),(4,0),(0,4),(1,0)]: qc.cx(*x)
qc.h(2)
for x in [(1,5),(5,1),(1,5),(2,1),(4,5),(5,2),(2,4)]: qc.cx(*x)
qc.h(3)
for x in [(5,6),(4,3),(3,5),(5,4),(4,6),(6,3),(3,6),(6,3)]: qc.cx(*x)
# Physical Sdg is logical S on this Steane convention; Sdg H maps A_L to paper H_L.
for q in data: qc.h(q)
for q in data: qc.sdg(q)
# Fig. 5a: H_m^{f1}, seven controlled-H gates and flag CNOTs around the string.
qc.reset(hm); qc.reset(flag); qc.h(hm); qc.cx(hm,flag)
for q in reversed(data): qc.append(CHGate(), [hm,q])
qc.cx(hm,flag); qc.h(hm); qc.measure(hm,0); qc.measure(flag,1)
# Compact EC: all six Steane stabilizers, with one fresh/reset ancilla each.
# This preserves the paper's postselection condition (all syndromes trivial),
# while avoiding a nonlocal custom operation.
stabs=[('X',[0,2,4,6]),('Z',[3,4,5,6]),('Z',[1,2,5,6]),
       ('Z',[0,2,4,6]),('X',[3,4,5,6]),('X',[1,2,5,6])]
for k,(typ,supp) in enumerate(stabs):
 a=anc[k]; qc.reset(a)
 if typ=='X': qc.h(a)
 for q in supp:
  if typ=='X': qc.cx(q,a)
  else: qc.cx(a,q)
 if typ=='X': qc.h(a)
 qc.measure(a,2+k)
# Return from H_L to target A_L: logical S H, physical S H.
for q in data: qc.s(q)
for q in data: qc.h(q)
# Map logical wires to a compact patch; all remaining logical wires have distinct cells.
used={7,8,9,13,14,15,16,10,11,12,17,18,19}
phys=[7,8,9,13,14,15,16,10,11,12,17,18,19]+[p for p in range(N) if p not in used]
tr=transpile(qc,basis_gates=['id','x','y','z','h','s','sdg','sx','sxdg','t','tdg','cx','reset','measure'],coupling_map=cm,initial_layout=phys,layout_method='sabre',routing_method='sabre',optimization_level=1,seed_transpiler=9)
layout=tr.layout.final_index_layout(); dp=[layout[i] for i in data]
print('ops',tr.count_ops(),'depth',tr.depth(),'dp',dp)
ps=[(0,[tr.clbits[i]]) for i in range(nrec)]
text=tprep.submission_text(tr,postselect=ps)
pathlib.Path('work/lanes/CC/cc_ec.qasm').write_text(text)
json.dump({'data_qubits':dp},open('work/lanes/CC/cc_ec.json','w'))
r=tprep.check(text,dp,p=1e-3,shots=100000,seed=0); print(r)
