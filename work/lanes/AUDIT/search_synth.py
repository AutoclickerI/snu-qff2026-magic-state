import sys,random,itertools
sys.path.insert(0,'.')
from qiskit import QuantumCircuit,transpile
from qiskit.transpiler import CouplingMap
from qiskit.synthesis import synth_cnot_count_full_pmh
import numpy as np
# Desired output columns for inputs a,b,c,d in q0..q6 bit order
cols=[0b0010110,0b1010101,0b1100110,0b1111000] # check bit strings q0 right? bits q0 lsb; a 0,0,1,0,1,1,0 => 0b0110100 reversed? 0b0110100 numeric 52; use explicit below
cols=[sum(bit<<i for i,bit in enumerate(v)) for v in ([0,0,1,0,1,1,0],[1,0,1,0,1,0,1],[0,1,1,0,0,1,1],[0,0,0,1,1,1,1])]
print('cols',cols)
def rank(vs):
 x=list(vs);r=0
 for b in range(7):
  j=next((j for j in range(r,len(x)) if x[j]>>b&1),None)
  if j is None:continue
  x[r],x[j]=x[j],x[r]
  for k in range(len(x)):
   if k!=r and x[k]>>b&1:x[k]^=x[r]
  r+=1
 return r
rng=random.Random(0); best=[]
for t in range(5000):
 ext=[]
 while len(ext)<3:
  x=rng.randrange(1,128)
  if rank(cols+ext+[x])>len(cols)+len(ext):ext.append(x)
 # matrix rows outputs, cols inputs
 M=np.array([[(v>>i)&1 for v in cols+ext] for i in range(7)],dtype=bool)
 syn=synth_cnot_count_full_pmh(M)
 n=syn.count_ops().get('cx',0)
 best.append((n,ext,syn))
best.sort(key=lambda x:x[0]);print('best full',[(x[0],x[1]) for x in best[:20]])
cm=CouplingMap.from_grid(6,6)
for n,ext,syn in best[:100]:
 qc=QuantumCircuit(7);qc.h(0);qc.t(0);qc.h(1);qc.h(2);qc.h(3);qc.compose(syn,inplace=True)
 for seed in range(3):
  r=transpile(qc,coupling_map=cm,basis_gates=['h','t','cx'],optimization_level=3,seed_transpiler=seed)
  n2=r.count_ops().get('cx',0);D=list(r.layout.final_index_layout()[:7])
  if n2<=28:
   print('candidate',n,n2,ext,seed,D);open('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/synth_candidate.qasm','w').write(__import__('tprep').submission_text(r));open('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/synth_candidate.meta','w').write(str(D));raise SystemExit
print('none')
