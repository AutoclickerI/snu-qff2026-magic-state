from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import CHGate
from qiskit.transpiler import CouplingMap
import tprep, json, pathlib
N=36; NC=2
cm=CouplingMap.from_grid(6,6)
qc=QuantumCircuit(N,NC)
data=list(range(7)); a=7; f=8
# direct target injection encoder from problem
qc.h(0); qc.t(0); qc.h(1)
for x in [(0,4),(4,0),(0,4),(1,0)]: qc.cx(*x)
qc.h(2)
for x in [(1,5),(5,1),(1,5),(2,1),(4,5),(5,2),(2,4)]: qc.cx(*x)
qc.h(3)
for x in [(5,6),(4,3),(3,5),(5,4),(4,6),(6,3),(3,6),(6,3)]: qc.cx(*x)
# U=S H takes A to paper H; then flagged H measurement
for q in data: qc.h(q)
for q in data: qc.sdg(q)
qc.h(a); qc.cx(a,f)
for q in reversed(data): qc.append(CHGate(),[a,q])
qc.cx(a,f)
qc.h(a); qc.measure(a,0); qc.measure(f,1)
# U^dag returns to A
for q in data: qc.s(q)
for q in data: qc.h(q)
# use initial mapping
phys=[7,8,9,13,14,15,16,10,11]+[p for p in range(N) if p not in {7,8,9,13,14,15,16,10,11}]
tr=transpile(qc,basis_gates=['id','x','y','z','h','s','sdg','sx','sxdg','t','tdg','cx','reset','measure'],coupling_map=cm,initial_layout=phys,layout_method='sabre',routing_method='sabre',optimization_level=1,seed_transpiler=9)
print('ops',tr.count_ops(),'depth',tr.depth())
layout=tr.layout.final_index_layout(); dp=[layout[i] for i in data]; print('dp',dp)
# Qiskit classical bits are preserved; postselect records indexes 0,1; tprep uses bits from qasm c[0],c[1]
text=tprep.submission_text(tr,postselect=[(0,[tr.clbits[0]]),(0,[tr.clbits[1]])])
pathlib.Path('work/lanes/CC/cc_hm.qasm').write_text(text)
json.dump({'data_qubits':dp},open('work/lanes/CC/cc_hm.json','w'))
r=tprep.check(text,dp,p=1e-3,shots=100000,seed=0); print(r)
