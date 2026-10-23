from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
import tprep, os, json
OUT='/home/jihoon/competitions/quantumn/work/codex';N=36;NC=32
edges=[]
for r in range(6):
 for c in range(6):
  q=6*r+c
  if c<5: edges += [(q,q+1),(q+1,q)]
  if r<5: edges += [(q,q+6),(q+6,q)]
cm=CouplingMap(edges)
data=list(range(7));cat1=list(range(7,14));cat2=list(range(14,21)); anc=33
master=QuantumCircuit(N,NC); current=list(range(N))
# initial positions: data 7-cell compact 2x4-ish; other virtuals place nearby to help
dest=[7,8,9,13,14,15,16]
for v,p in enumerate(dest): current[v]=p
# place cat1 row1 cols 1..5 + row2 etc, cat2 nearby
# all unspecified map bijection
used=set(current[:7]); avail=[p for p in range(N) if p not in used]
for v in range(7,N): current[v]=avail[v-7]

def route(stage, label):
 global master,current
 tr=transpile(stage,basis_gates=['id','x','y','z','h','s','sdg','sx','sxdg','t','tdg','cx','reset','measure'],coupling_map=cm,initial_layout=current,layout_method='sabre',routing_method='sabre',optimization_level=1,seed_transpiler=7)
 print(label,'cx',tr.count_ops().get('cx',0),'depth',tr.depth())
 master.compose(tr,inplace=True)
 current=tr.layout.final_index_layout()
 return tr
# stage 1 encode
s=QuantumCircuit(N,NC)
for q in range(4):s.h(q)
ops=[(0,4),(4,0),(0,4),(1,0),(1,5),(5,1),(1,5),(2,1),(4,5),(5,2),(2,4),(5,6),(4,3),(3,5),(5,4),(4,6),(6,3),(3,6),(6,3)]
for a,b in ops:s.cx(a,b)
route(s,'encode')
# data stabilizer checks, no intermediate reset movement
def checks():
 s=QuantumCircuit(N,NC); ci=0
 for kind in 'XZ':
  for support in tprep.grid.SUPPORTS:
   s.reset(anc)
   if kind=='X':
    for i in support:s.h(i)
   for i in support:s.cx(i,anc)
   s.measure(anc,ci);ci+=1
   if kind=='X':
    for i in support:s.h(i)
 return s
route(checks(),'checks')

def catstage(cat, ci, logical):
 s=QuantumCircuit(N,NC)
 # prep cat with only first H
 s.reset(cat[0]);s.h(cat[0])
 for q in cat[1:]:s.reset(q)
 for a,b in zip(cat[:-1],cat[1:]):s.cx(a,b)
 for i,(a,b) in enumerate(zip(cat[:-1],cat[1:])):
  v=21+i;s.reset(v);s.cx(a,v);s.cx(b,v);s.measure(v,ci+i)
 for q in data:s.t(q)
 for a,d in zip(cat,data):s.cx(a,d)
 for q in data:s.tdg(q)
 for j,a in enumerate(cat):s.h(a);s.measure(a,ci+6+j)
 return s
route(catstage(cat1,6,0),'cat1')
route(catstage(cat2,19,1),'cat2')
layout=current;data_phys=[layout[i] for i in data]
print('final data',data_phys,'total',master.count_ops(), 'layout',layout)
# map classical bits unchanged
# detectors: stabs c0..5, cat checks c6..11,c19..24, parity logical c12..18,c25..31
det=[[master.clbits[i]] for i in list(range(12))+list(range(19,25))]
det.append([master.clbits[i] for i in range(12,19)]+[master.clbits[i] for i in range(25,32)])
frame={'X':(0,[]),'Z':(0,[master.clbits[i] for i in range(12,19)])}
text=tprep.submission_text(master,detectors=det,frame=frame)
open(os.path.join(OUT,'seq.qasm'),'w').write(text)
if __name__=='__main__':
 r=tprep.check(text,data_phys,p=1e-3,shots=100000,seed=0);print(r)
