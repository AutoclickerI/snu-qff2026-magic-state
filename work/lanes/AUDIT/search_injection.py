import sys,random,json
sys.path.insert(0,'/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
from qiskit import QuantumCircuit,transpile
from qiskit.transpiler import CouplingMap
import tprep
from pathlib import Path
qc=QuantumCircuit(7)
qc.h(0);qc.t(0);qc.h(1);qc.cx(0,4);qc.cx(4,0);qc.cx(0,4);qc.cx(1,0);qc.h(2);qc.cx(1,5);qc.cx(5,1);qc.cx(1,5);qc.cx(2,1);qc.cx(4,5);qc.cx(5,2);qc.cx(2,4);qc.h(3);qc.cx(5,6);qc.cx(4,3);qc.cx(3,5);qc.cx(5,4);qc.cx(4,6);qc.cx(6,3);qc.cx(3,6);qc.cx(6,3)
cm=CouplingMap.from_grid(6,6); rng=random.Random(1);out=[]
for t in range(120):
 init=None
 try:r=transpile(qc,coupling_map=cm,basis_gates=['h','t','cx'],optimization_level=3,seed_transpiler=t)
 except Exception:continue
 n2=r.count_ops().get('cx',0)
 if n2>35:continue
 text=tprep.submission_text(r); D=list(r.layout.final_index_layout()[:7])
 rep=tprep.check(text,D,p=1e-3,shots=20000,seed=0)
 if rep.passed:
  out.append((rep.score,rep.acceptance,n2,t,D,init,text))
  print(f'{len(out):3} score {rep.score:.6f} acc {rep.acceptance:.4f} n2 {n2} t {t} D {D}',flush=True)
out.sort(key=lambda x:x[0]);
print('BEST',[(x[0],x[1],x[2],x[3],x[4]) for x in out[:10]])
if out:
 x=out[0];Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/injection_best.qasm').write_text(x[6]);Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/injection_best.meta').write_text(json.dumps({'score20k':x[0],'acceptance':x[1],'n2':x[2],'seed':x[3],'data':x[4],'initial':x[5]}))
