import sys
sys.path.insert(0,'.')
from qiskit import QuantumCircuit,transpile
from qiskit.transpiler import CouplingMap
import tprep
from pathlib import Path
# copy problem circuit
qc=QuantumCircuit(7)
qc.h(0);qc.t(0);qc.h(1);qc.cx(0,4);qc.cx(4,0);qc.cx(0,4);qc.cx(1,0);qc.h(2);qc.cx(1,5);qc.cx(5,1);qc.cx(1,5);qc.cx(2,1);qc.cx(4,5);qc.cx(5,2);qc.cx(2,4);qc.h(3);qc.cx(5,6);qc.cx(4,3);qc.cx(3,5);qc.cx(5,4);qc.cx(4,6);qc.cx(6,3);qc.cx(3,6);qc.cx(6,3)
cm=CouplingMap.from_grid(6,6)
for seed in range(10):
 r=transpile(qc,coupling_map=cm,basis_gates=['h','t','cx'],optimization_level=3,seed_transpiler=seed)
 d=r.layout.final_index_layout()[:7]
 print(seed,d,'2q',r.count_ops().get('cx',0),'ops',len(r.data))
 print(tprep.submission_text(r).splitlines()[:5])
