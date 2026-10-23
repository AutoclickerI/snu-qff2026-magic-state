import sys, random
sys.path.insert(0, '/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
from qiskit.synthesis import synth_cnot_count_full_pmh
import tprep

cols=[52,85,102,120]
def rank(vs):
 x=list(vs); r=0
 for b in range(7):
  j=next((j for j in range(r,len(x)) if x[j]>>b&1),None)
  if j is None: continue
  x[r],x[j]=x[j],x[r]
  for k in range(len(x)):
   if k!=r and x[k]>>b&1:x[k]^=x[r]
  r+=1
 return r
rng=random.Random(3); cm=CouplingMap.from_grid(6,6); low=[]
for _ in range(10000):
 ext=[]
 while len(ext)<3:
  z=rng.randrange(1,128)
  if rank(cols+ext+[z])>len(cols)+len(ext):ext.append(z)
 M=np.array([[(v>>i)&1 for v in cols+ext] for i in range(7)],bool)
 syn=synth_cnot_count_full_pmh(M)
 if syn.count_ops().get('cx',0)>18:continue
 qc=QuantumCircuit(7);qc.h(0);qc.t(0);qc.h(1);qc.h(2);qc.h(3);qc.compose(syn,inplace=True)
 for seed in (0,1,2):
  r=transpile(qc,coupling_map=cm,basis_gates=['h','t','cx'],optimization_level=3,seed_transpiler=seed)
  n2=r.count_ops().get('cx',0)
  if n2<=23:
   low.append((n2,ext,seed,list(r.layout.final_index_layout()[:7]),r));print('low',len(low),n2,ext,seed,low[-1][3],flush=True)
print('nlow',len(low))
out=[]
for j,(n2,ext,seed,D,r) in enumerate(low[:100]):
 text=tprep.submission_text(r);rep=tprep.check(text,D,p=1e-3,shots=20000,seed=0)
 if rep.passed:out.append((rep.score,n2,ext,seed,D,text));print('score',rep.score,n2,ext,seed,D,flush=True)
out.sort(key=lambda x:x[0]);print('BEST',[(x[0],x[1],x[2],x[3],x[4]) for x in out[:20]])
for i,row in enumerate(out[:5]):
 open(f'/home/jihoon/competitions/quantumn/work/lanes/AUDIT/low_{i}.qasm','w').write(row[5]);open(f'/home/jihoon/competitions/quantumn/work/lanes/AUDIT/low_{i}.meta','w').write(str(row[4]))
