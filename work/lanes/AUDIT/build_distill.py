import sys,random
sys.path.insert(0,'/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
from qiskit import QuantumCircuit,transpile
from qiskit.transpiler import CouplingMap
from pathlib import Path
import tprep
SUP=((2,3,4),(1,3,4),(1,2,4),(1,2,3),(0,3,4),(0,2,4),(0,2,3),(0,1,4),(0,1,3),(0,1,2),(0,1,2,3,4))
# 11 logical qubits: distillation rows 0..4, encoding output q4 + seeds/ancillas 5..10
qc=QuantumCircuit(11,4)
for i in range(4): qc.h(i);qc.t(i)
qc.h(4)
for S in SUP:
 p=S[-1]
 for i in S[:-1]:qc.cx(i,p)
 qc.t(p)
 for i in reversed(S[:-1]):qc.cx(i,p)
qc.s(4)
for i in range(4): qc.h(i);qc.measure(i,i)
e=[4,5,6,7,8,9,10]
qc.h(e[1]);qc.cx(e[0],e[4]);qc.cx(e[4],e[0]);qc.cx(e[0],e[4]);qc.cx(e[1],e[0]);qc.h(e[2]);qc.cx(e[1],e[5]);qc.cx(e[5],e[1]);qc.cx(e[1],e[5]);qc.cx(e[2],e[1]);qc.cx(e[4],e[5]);qc.cx(e[5],e[2]);qc.cx(e[2],e[4]);qc.h(e[3]);qc.cx(e[5],e[6]);qc.cx(e[4],e[3]);qc.cx(e[3],e[5]);qc.cx(e[5],e[4]);qc.cx(e[4],e[6]);qc.cx(e[6],e[3]);qc.cx(e[3],e[6]);qc.cx(e[6],e[3])
cm=CouplingMap.from_grid(6,6)
# search a few routing seeds/layouts; make best candidate by CNOT count and save
rng=random.Random(0); found=[]
for t in range(30):
 init=rng.sample(range(36),11)
 try:r=transpile(qc,coupling_map=cm,basis_gates=['h','t','s','cx'],optimization_level=3,seed_transpiler=t,initial_layout=init)
 except Exception as ex: continue
 D=[r.layout.final_index_layout()[i] for i in range(4,11)]
 n2=r.count_ops().get('cx',0)
 found.append((n2,t,init,D,r))
found.sort(key=lambda x:x[0]);
for n2,t,init,D,r in found[:10]:print('cand',n2,t,D,init)
# choose best
n2,t,init,D,r=found[0]
text=tprep.submission_text(r)
lines=text.splitlines(); qi=next(i for i,x in enumerate(lines) if x.startswith('creg'))
for i in range(4): lines.append(f'// DETECTOR c[{i}]')
text='\n'.join(lines)+'\n'
Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/distill_encode.qasm').write_text(text)
Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/distill_meta.txt').write_text(f'{D}\n{n2}\n{t}\n{init}\n')
print('chosen',D,n2,'lines',len(lines))
