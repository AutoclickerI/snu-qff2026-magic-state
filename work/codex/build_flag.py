from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
import tprep, os, json
OUT='/home/jihoon/competitions/quantumn/work/codex';N=36;NC=6
edges=[]
for r in range(6):
 for c in range(6):
  q=6*r+c
  if c<5:edges += [(q,q+1),(q+1,q)]
  if r<5:edges += [(q,q+6),(q+6,q)]
cm=CouplingMap(edges); data=list(range(7)); master=QuantumCircuit(N,NC)
# compact data mapping; map all remaining bijectively
current=list(range(N)); dest=[7,8,9,13,14,15,16]
for i,p in enumerate(dest): current[i]=p
used=set(dest); avail=[p for p in range(N) if p not in used]
for i in range(7,N):current[i]=avail[i-7]
def route(s,label):
 global current,master
 tr=transpile(s,basis_gates=['id','x','y','z','h','s','sdg','sx','sxdg','t','tdg','cx','reset','measure'],coupling_map=cm,initial_layout=current,layout_method='sabre',routing_method='sabre',optimization_level=1,seed_transpiler=9)
 print(label,'cx',tr.count_ops().get('cx',0),'depth',tr.depth())
 master.compose(tr,inplace=True);current=tr.layout.final_index_layout();return tr
# Encoder
s=QuantumCircuit(N,NC)
for q in range(4):s.h(q)
ops=[(0,4),(4,0),(0,4),(1,0),(1,5),(5,1),(1,5),(2,1),(4,5),(5,2),(2,4),(5,6),(4,3),(3,5),(5,4),(4,6),(6,3),(3,6),(6,3)]
for a,b in ops:s.cx(a,b)
route(s,'encode')
def flaground(a,f,cflag,c1,c2):
 s=QuantumCircuit(N,NC)
 s.reset(a);s.reset(f);s.h(f)
 s.cx(f,a)
 for q in data:s.t(q);s.h(q)
 for q in data:s.cx(q,a)
 for q in data:s.h(q);s.tdg(q)
 s.cx(f,a)
 s.h(f);s.measure(f,cflag)
 s.measure(a,c1);s.measure(a,c2)
 return s
route(flaground(34,35,0,1,2),'round1')
route(flaground(32,33,3,4,5),'round2')
layout=current;dp=[layout[i] for i in data]
# flags c0,c3; repeat readout comparisons c1^c2 and c4^c5; outcome comparison c1^c4 also deterministic if no errors
det=[[master.clbits[0]],[master.clbits[3]],[master.clbits[1],master.clbits[2]],[master.clbits[4],master.clbits[5]],[master.clbits[1],master.clbits[4]]]
frame={'X':(0,[]),'Z':(0,[master.clbits[1]])}
text=tprep.submission_text(master,detectors=det,frame=frame)
open(os.path.join(OUT,'flag.qasm'),'w').write(text)
print('dp',dp,'total',master.count_ops(),'layout',layout)
if __name__=='__main__':
 r=tprep.check(text,dp,p=1e-3,shots=100000,seed=0);print(r)
